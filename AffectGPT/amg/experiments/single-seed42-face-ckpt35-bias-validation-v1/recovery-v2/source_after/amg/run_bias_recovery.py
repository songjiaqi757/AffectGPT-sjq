"""Resume only missing bias-trial evaluations; reuse locked trained checkpoints."""
from __future__ import annotations
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import traceback
from .run_bias_validation import BiasExperiment,ARMS,compare_initializations
from .run_experiment import (DEFAULT_PYTHON,PROJECT,read_json,write_json,sha,now,
                            run_gpu_queue,exposure_signature)

class Recovery(BiasExperiment):
    def validate(self):
        p=self.protocol
        parent=Path(p["recovery"]["parent_directory"])
        original=read_json(parent/"READY.json")["locked_files"]
        patch=read_json(self.output/"PATCH.json")
        if original[patch["changed_file"]]!=patch["before_sha256"]:
            raise RuntimeError("Repair was not based on the locked original runner")
        if sha(self.output/"run_bias_validation.before.py")!=patch["before_sha256"]:
            raise RuntimeError("Original runner snapshot changed")
        before=(self.output/"run_bias_validation.before.py").read_text()
        expected=before.replace('            neighbors=trace.get("retrieved_ids",[])',
                                '            neighbors=trace.get("retrieved_ids") or []')
        if (PROJECT/"amg/run_bias_validation.py").read_text()!=expected:
            raise RuntimeError("Only the one null-list validation repair is permitted")
        for name,digest in original.items():
            allowed=patch["after_sha256"] if name==patch["changed_file"] else digest
            if sha(name)!=allowed:
                raise RuntimeError("Original locked artifact unexpectedly changed: "+name)
        result=super().validate()
        self.parent=parent
        prior=read_json(parent/"state.json")
        if prior["status"]!="failed" or prior["error"]!="TypeError: 'NoneType' object is not iterable":
            raise RuntimeError("Expected the documented post-training off validation failure")
        try:
            os.kill(prior["runner_pid"],0)
        except ProcessLookupError:
            pass
        else:
            raise RuntimeError("The original controller is still alive")
        for arm in ARMS:
            directory=parent/"training"/arm
            self.validate_training("retrieval",directory)
            checkpoint=directory/"checkpoint_001334.pth"
            declaration=p["recovery"]["trained_checkpoints"][arm]
            if str(checkpoint)!=declaration["path"] or sha(checkpoint)!=declaration["sha256"]:
                raise RuntimeError("Trained checkpoint identity changed")
            self.validate_inference(directory/"inference/retrieval/dev.jsonl",
                                    checkpoint,"retrieval","none")
        audit=compare_initializations(
            read_json(parent/"training/control/adapter_initialization.json"),
            read_json(parent/"training/zero_init/adapter_initialization.json"),self.shared)
        write_json(self.output/"matched-initialization.json",audit)
        self.init_compared=True
        a,b=[exposure_signature(parent/"training"/arm/"exposure.jsonl") for arm in ARMS]
        if a!=b or a[1]!=4002:
            raise RuntimeError("Actual training exposures are not identical and complete")
        write_json(self.output/"exposure-alignment.json",{
            "control":a,"zero_init":b,"identical":True,"examples":4002,"reused_training":True})
        self.validate_inference(parent/"training/zero_init/inference/off/dev.jsonl",
                                parent/"training/zero_init/checkpoint_001334.pth","off","none")
        required={"ref-normal","ref-off","ref-random","ref-off_trained",
                  "stage-a-zero-retrieval","stage-a-zero-random",
                  "stage-a-zero-retrieval-vs-ref-normal","stage-a-zero-random-vs-ref-random",
                  "stage-a-zero-retrieval-vs-stage-a-zero-random","stage-a-zero-retrieval-vs-ref-off",
                  "stage-b-control-retrieval","stage-b-zero_init-retrieval"}
        for key in required:
            path=parent/"reports"/(key+".json")
            report=read_json(path);meta=report["metadata"]
            if (report["metrics"]["N"]!=500 or report["metrics"]["failed_predictions"]!=0
                or meta["scorer_source_sha256"]!=sha(PROJECT/"amg/evaluate.py")
                or meta["predictions_sha256"]!=sha(meta["predictions"])
                or meta["inference_metadata_sha256"]!=sha(meta["inference_metadata"])
                or meta["base_checkpoint_sha256"]!=p["baseline_sha256"]
                or meta["manifest_sha256"]!=p["splits"]["dev"]["sha256"]):
                raise RuntimeError("Cached score/metadata/predictions changed: "+key)
            self.reports[key]=path
        self.state.update(resumed_from=str(parent),no_training=True,
                          original_failure=prior["error"],reused_reports=len(required),
                          original_state=str(parent/"state.json"))
        return {**result,"no_training":True,"reused_reports":len(required),
                "gpu_tasks":["control/off","control/random","zero_init/random"]}

    def worker(self,arm,gpu):
        checkpoint=self.parent/"training"/arm/"checkpoint_001334.pth"
        modes=("off","random") if arm=="control" else ("random",)
        for mode in modes:
            key="stage-b-"+arm+"-"+mode
            directory=self.output/"generation"/arm/mode
            directory.mkdir(parents=True)
            self.wait_gpu(gpu,key)
            args=self.infer_args(checkpoint,directory/"dev.jsonl")+[
                "--memory-mode",mode,"--value-last-bias-override","none"]
            rc=self.execute(args,self.output/"logs"/(key+"-infer.log"),
                            mode=key,stage="generating_dev",gpu=gpu,allowed=(0,1))
            audit=self.validate_inference(directory/"dev.jsonl",checkpoint,mode,"none")
            meta=read_json(directory/"dev.meta.json")
            expected="preserve" if arm=="control" else "zero"
            if meta["training_initialization"]["value_last_bias_init"]!=expected:
                raise RuntimeError("Wrong trained initialization in generation")
            write_json(directory/"inference-audit.json",audit)
            self.score(key,directory/"dev.jsonl",directory/"dev.meta.json")
            self.event(key,"complete",gpu=gpu,errors=audit["errors"],inference_returncode=rc)
        self.event("recovery-"+arm,"complete",gpu=gpu)

    def run(self):
        try:
            result=self.validate()
            for name in ("logs","reports","generation"):
                (self.output/name).mkdir(exist_ok=True)
            self.state["status"]="running"
            self.event("pipeline","validated_recovery",**result)
            zero_off=self.parent/"training/zero_init/inference/off"
            self.score("stage-b-zero_init-off",zero_off/"dev.jsonl",zero_off/"dev.meta.json")
            self.event("stage-b-zero_init-off","complete",reused=True,errors=0)
            # Save the completed primary result before GPU recovery without
            # using it to select, skip or change the remaining fixed comparisons.
            self.paired([("stage-b-zero_init-retrieval","stage-b-control-retrieval")])
            run_gpu_queue(ARMS,self.gpus,self.worker,self.stop_event,self.stop_children)
            pairs=[("stage-b-zero_init-retrieval","ref-off_trained"),
                   ("stage-b-control-retrieval","ref-normal")]
            pairs += [("stage-b-"+arm+"-retrieval","stage-b-"+arm+"-"+mode)
                      for arm in ARMS for mode in ("off","random")]
            self.event("pipeline","final_paired_scoring")
            self.paired(pairs)
            self.finish()
            return 0
        except BaseException as error:
            self.stop_children()
            self.state.update(status="interrupted" if self.interrupted_signal else "failed",
                              finished_at=now(),error=f"{type(error).__name__}: {error}")
            self.event("pipeline",self.state["status"],error=self.state["error"])
            (self.output/"FAILURE.txt").write_text(traceback.format_exc())
            traceback.print_exc()
            return 1

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol",required=True);parser.add_argument("--output-dir",required=True)
    parser.add_argument("--python",default=DEFAULT_PYTHON);parser.add_argument("--validate-only",action="store_true")
    args=parser.parse_args(argv)
    job=Recovery(args.protocol,args.output_dir,python=args.python)
    with (job.output/".run.lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.validate_only:
            print(json.dumps(job.validate()));return 0
        if (job.output/"state.json").exists():
            raise FileExistsError("Never overwrite an existing recovery state")
        for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,job.signal_handler)
        return job.run()
if __name__=="__main__":
    raise SystemExit(main())

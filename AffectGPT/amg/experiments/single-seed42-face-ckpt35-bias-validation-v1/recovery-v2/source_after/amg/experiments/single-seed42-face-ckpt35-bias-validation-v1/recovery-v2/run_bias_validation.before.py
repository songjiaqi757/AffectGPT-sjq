"""Bounded bias validation: old-checkpoint interventions, then one matched seed pair.

All inputs and source are server-side SHA256 locked. At most one child per GPU.
No model, CUDA context or media is loaded in this controller. A failed technical
check cancels only children launched here. Scientific negative results never
skip the predeclared matched training pair.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import json
import os
from pathlib import Path
import signal
import traceback
from .run_experiment import (Experiment, PROJECT, DEFAULT_PYTHON, absolute, now,
    sha, read_json, write_json, run_gpu_queue, first_five_validation, exposure_signature)

ARMS = ("control", "zero_init")
TARGET = "value_projection.2.bias"

def compare_initializations(control, zero, shared):
    """Require exact common start apart from the one declared trainable bias."""
    a,b = control["initial_adapter"],zero["initial_adapter"]
    changed = [key for key in a["parameter_sha256"]
               if a["parameter_sha256"][key] != b["parameter_sha256"].get(key)]
    if set(a["parameter_sha256"]) != set(b["parameter_sha256"]) or changed != [TARGET]:
        raise RuntimeError("Matched Adapter starts must differ only in the last value bias")
    if a["state_sha256"] != shared["state_sha256"]:
        raise RuntimeError("Control did not load the exact shared Adapter initialization")
    for record,policy in ((control,"preserve"),(zero,"zero")):
        if record["policy"] != policy:
            raise RuntimeError("Wrong initial bias policy")
        if record["shared"]["file_sha256"] != shared["file_sha256"]:
            raise RuntimeError("Arms did not read the same shared initialization file")
        if record["initial_lora_float32"] != shared["baseline_lora_float32"]:
            raise RuntimeError("An arm did not restore exact baseline LoRA")
        if not record["saved_before_optimizer_and_first_update"]:
            raise RuntimeError("Initialization was not audited before training")
    if zero["bias_override"]["target_after"]["nonzero"] != 0:
        raise RuntimeError("Zero-init bias was not zero before training")
    return {"schema":"amg-matched-initialization-comparison-v1", "verified_at":now(),
            "identical_except":[TARGET], "changed_parameters":changed,
            "same_baseline_lora":True, "same_shared_file":True,
            "bias_remains_trainable":True,
            "control_adapter_sha256":a["state_sha256"],
            "zero_adapter_sha256":b["state_sha256"],
            "lora_state_sha256":control["initial_lora_float32"]["state_sha256"]}

class BiasExperiment(Experiment):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.state["schema"]="amg-bias-validation-state-v1"
        self.reports={}
        self.init_compared=False

    def validate(self):
        p,t = self.protocol,self.protocol["training"]
        if p.get("schema")!="amg-bias-validation-protocol-v1" or p["seed"]!=42:
            raise ValueError("Expected the predeclared single seed bias protocol")
        if self.gpus!=(0,1) or self.cpu_workers!=2 or self.min_free_mib<32000:
            raise ValueError("Exactly GPUs 0/1, two CPU workers and >=32000 MiB free required")
        expected={"iterations":1334,"batch_size":1,"grad_accum":3,"nominal_examples":4002,
                  "lr":1e-5,"weight_decay":.05,"memory_dropout":.2,"num_tokens":4,
                  "hidden_dim":256,"train_peft":True,"workers":2,"cuda_memory_fraction":.35}
        if t!=expected:
            raise ValueError("Training budget/hyperparameters differ from the bounded protocol")
        if p["generation"]!={"task":"ovlabel","max_new_tokens":128,"do_sample":False,
                             "num_beams":1,"seed":42}:
            raise ValueError("Only the original locked greedy decoding is allowed")
        required={self.protocol_path,Path(__file__).resolve()}
        for key in ("config","baseline_checkpoint","memory_bank","evaluation_resource",
                    "shared_init","shared_init_metadata","old_retrieval_checkpoint",
                    "old_adapter_fingerprints","shared_init_generator"):
            required.add(absolute(p[key],key))
        required.add(Path(p["memory_bank"]+".json"))
        for ref in p["reference_predictions"].values():
            for key in ("predictions","metadata"):
                required.add(absolute(ref[key],key))
        for split in p["splits"].values():
            required.add(absolute(split["path"],"split"))
        required.update((PROJECT/"amg").glob("*.py"))
        required.update((PROJECT/"amg/tests").glob("test_*.py"))
        required.update(PROJECT/relative for relative in (
            "config.py","my_affectgpt/models/affectgpt.py","my_affectgpt/models/encoder.py",
            "my_affectgpt/datasets/datasets/base_dataset.py",
            "my_affectgpt/datasets/datasets/mercaptionplus_dataset.py"))
        locked=read_json(self.output/"READY.json")["locked_files"]
        missing=required-{Path(path) for path in locked}
        if missing: raise ValueError("READY lacks inputs/sources: "+repr(sorted(map(str,missing))))
        for name,digest in locked.items():
            absolute(name,"locked file")
            if sha(name)!=digest: raise RuntimeError("Locked artifact changed: "+name)
        for key,hkey in (("baseline_checkpoint","baseline_sha256"),("memory_bank","memory_bank_sha256"),
                         ("old_retrieval_checkpoint","old_retrieval_checkpoint_sha256")):
            if locked[p[key]]!=p[hkey]: raise RuntimeError("Protocol fingerprint differs: "+key)
        from .manifest import read_manifest
        ids,groups=set(),set()
        for split,count in (("fit",4000),("dev",500),("holdout",500)):
            item=p["splits"][split]; rows=read_manifest(item["path"])
            newids={row["name"] for row in rows};newgroups={row["group_id"] for row in rows}
            if len(rows)!=count or len(newids)!=count or ids&newids or groups&newgroups:
                raise RuntimeError("Split size/identity/group separation failed: "+split)
            if locked[item["path"]]!=item["sha256"]: raise RuntimeError("Manifest changed: "+split)
            ids.update(newids);groups.update(newgroups)
        self.bank_metadata=bank=read_json(p["memory_bank"]+".json")
        if (bank["schema"]!="amg-m0-bank-v1" or not bank["complete"] or bank["partial_for_testing"]
            or bank["records"]!=4000 or bank["total_manifest_records"]!=4000
            or bank["manifest_sha256"]!=p["splits"]["fit"]["sha256"]
            or bank["bank_sha256"]!=p["memory_bank_sha256"]
            or bank["version"]!=p["memory_bank_version"]
            or bank["config_sha256"]!=locked[p["config"]]):
            raise RuntimeError("Need the exact full fit-only frozen encoder bank")
        self.shared=read_json(p["shared_init_metadata"])
        if (self.shared["file_sha256"]!=locked[p["shared_init"]]
            or self.shared["baseline_sha256"]!=p["baseline_sha256"]
            or self.shared["config_sha256"]!=locked[p["config"]]
            or self.shared["seed"]!=42 or self.shared["tensor_count"]!=19
            or self.shared["baseline_lora_tensor_count"]!=392
            or self.shared["provenance"]["reproduces_old_training_initialization"] is not False):
            raise RuntimeError("Shared initialization provenance failed")
        self.fit_ids={row["name"] for row in read_manifest(p["splits"]["fit"]["path"])}
        self.dev_rows=[json.loads(line) for line in Path(p["splits"]["dev"]["path"]).read_text().splitlines()]
        self.old_adapter=read_json(p["old_adapter_fingerprints"])
        self.state.update(protocol_sha256=locked[str(self.protocol_path)],
            baseline_checkpoint=p["baseline_checkpoint"],baseline_sha256=p["baseline_sha256"],
            memory_bank_sha256=p["memory_bank_sha256"],memory_bank_version=p["memory_bank_version"],
            gpus=[0,1],max_concurrent_new_gpu_jobs=2,
            fresh_shared_init=True,reproduces_old_training_initialization=False)
        return {"validated":True,"locked_files":len(locked),"gpus":[0,1],
                "shared_init_sha256":self.shared["file_sha256"]}

    def parallel(self,items,fn):
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs=[pool.submit(fn,item) for item in items]
            try:
                for job in as_completed(jobs): job.result()
            except BaseException:
                self.stop_children()
                raise

    def score(self,key,prediction,metadata,*,paired=None):
        out=self.output/"reports"/(key+".json")
        args=[self.python,"-B","-m","amg.evaluate","--manifest",self.protocol["splits"]["dev"]["path"],
              "--split","dev","--task","ovlabel","--resource",self.protocol["evaluation_resource"],
              "--predictions",str(prediction),"--metadata",str(metadata),"--output",str(out)]
        if paired is not None:
            args+=["--paired-report",str(self.reports[paired]),"--bootstrap-seed","42",
                   "--bootstrap-resamples","1000"]
        self.execute(args,self.output/"logs"/(key+".log"),mode=key,stage="paired_scoring" if paired else "scoring")
        report=read_json(out);m=report["metadata"];p=self.protocol
        if (report["metrics"]["N"]!=500 or len(report["per_clip"])!=500
            or m["base_checkpoint_sha256"]!=p["baseline_sha256"]
            or m["manifest_sha256"]!=p["splits"]["dev"]["sha256"]):
            raise RuntimeError("Score lost full denominator or provenance: "+key)
        if paired and report["paired"]["N"]!=500: raise RuntimeError("Paired denominator failed")
        with self.lock: self.reports[key]=out
        return report

    def score_refs(self):
        def run(item):
            key,ref=item
            report=self.score("ref-"+key,ref["predictions"],ref["metadata"])
            m=report["metadata"]
            if (m["checkpoint_sha256"]!=ref["checkpoint_sha256"] or
                m["trained_mode"]!=ref["trained_mode"] or m["memory_mode"]!=ref["memory_mode"]):
                raise RuntimeError("Cached reference identity failed: "+key)
        self.parallel(list(self.protocol["reference_predictions"].items()),run)

    def validate_inference(self,path,checkpoint,mode,override,reference=None):
        meta=read_json(path.with_name("dev.meta.json"))
        rows=[json.loads(line) for line in path.read_text().splitlines()]
        expected=[row["name"] for row in self.dev_rows]
        if [row["name"] for row in rows]!=expected:
            raise RuntimeError("Inference must retain the 500 ordered original dev identities")
        p=self.protocol
        checks={"base_sha256":p["baseline_sha256"],"amg_sha256":sha(checkpoint),
                "manifest_sha256":p["splits"]["dev"]["sha256"],"memory_sha256":p["memory_bank_sha256"],
                "trained_mode":"retrieval","memory_mode":mode,"seed":42,
                "selected_clips":500,"manifest_records":500,"dry_run":False}
        if any(meta.get(key)!=value for key,value in checks.items()):
            raise RuntimeError("Inference provenance or denominator differs: "+str(path))
        intervention=meta["model_intervention"]
        if intervention["policy"]!=override or intervention["applied"]!=(override=="zero"):
            raise RuntimeError("Unrecorded or incorrect bias intervention")
        if override=="zero":
            if (intervention["changed_parameters"]!=[TARGET] or intervention["target_after"]["nonzero"]!=0
                or intervention["source_adapter_sha256"]!=self.old_adapter["original"]["state_sha256"]
                or intervention["runtime_adapter_sha256"]!=self.old_adapter["zero"]["state_sha256"]):
                raise RuntimeError("Stage A must alter precisely the old trained value bias")
        elif intervention["changed_parameters"]:
            raise RuntimeError("Stage B inference must preserve every learned parameter")
        if reference:
            prior=[json.loads(line) for line in Path(reference["predictions"]).read_text().splitlines()]
            oldmeta=read_json(reference["metadata"])
            for field in ("prompt_sha256","config_sha256","decoding","budget_source_sha256",
                          "max_length","memory_tokens_reserved","face_or_frame"):
                if meta.get(field)!=oldmeta.get(field):
                    raise RuntimeError("Intervention changed prompt/decoding: "+field)
            for row,old in zip(rows,prior):
                if row["name"]!=old["name"] or row.get("budget")!=old.get("budget"):
                    raise RuntimeError("Intervention changed clip or prompt token budget")
                if not row.get("error") and not old.get("error"):
                    if row.get("retrieval",{}).get("retrieved_ids")!=old.get("retrieval",{}).get("retrieved_ids"):
                        raise RuntimeError("Single-bias intervention changed neighbor identities")
        errors=0
        for row in rows:
            if row.get("error"):
                errors+=1
                continue
            trace=row.get("retrieval") or {}
            neighbors=trace.get("retrieved_ids",[])
            flat=[name for group in neighbors for name in group]
            if any(name not in self.fit_ids for name in flat):
                raise RuntimeError("Retrieval used a non-fit identity")
            if mode in ("retrieval","random") and (len(flat)!=5 or row["name"] in flat):
                raise RuntimeError("Expected five non-self fit memories")
            if mode=="off" and any(trace.get("memory_enabled",[])):
                raise RuntimeError("Off intervention actually enabled memory")
        if errors!=meta["errors"] or errors+meta["successes"]!=500:
            raise RuntimeError("Inference failure accounting mismatch")
        return {"rows":500,"errors":errors,"memory_mode":mode,
                "checkpoint_sha256":meta["amg_sha256"],"model_intervention":intervention}

    def intervention(self,mode,gpu):
        key="stage-a-zero-"+mode
        out=self.output/"interventions"/("zero-"+mode);out.mkdir(parents=True)
        checkpoint=self.protocol["old_retrieval_checkpoint"]
        args=self.infer_args(checkpoint,out/"dev.jsonl")+[
            "--memory-mode",mode,"--value-last-bias-override","zero"]
        self.wait_gpu(gpu,key)
        rc=self.execute(args,self.output/"logs"/(key+"-infer.log"),
                        mode=key,stage="generating_dev",gpu=gpu,allowed=(0,1))
        ref=self.protocol["reference_predictions"]["normal" if mode=="retrieval" else "random"]
        audit=self.validate_inference(out/"dev.jsonl",checkpoint,mode,"zero",reference=ref)
        write_json(out/"inference-audit.json",audit)
        self.score(key,out/"dev.jsonl",out/"dev.meta.json")
        self.event(key,"complete",gpu=gpu,inference_returncode=rc,errors=audit["errors"])

    def check_starts(self,required=False):
        with self.lock:
            if self.init_compared: return
            paths=[self.output/"training"/arm/"adapter_initialization.json" for arm in ARMS]
            if not all(path.is_file() for path in paths):
                if required: raise RuntimeError("Missing actual pre-training initialization audit")
                return
            record=compare_initializations(read_json(paths[0]),read_json(paths[1]),self.shared)
            write_json(self.output/"matched-initialization.json",record)
            self.init_compared=True
            self.event("matched-start","verified",**record)

    def train_arm(self,arm,gpu):
        out=self.output/"training"/arm
        policy="preserve" if arm=="control" else "zero"
        key="stage-b-"+arm
        early=False
        def monitor():
            nonlocal early
            self.check_starts()
            if not early and (out/"train.jsonl").is_file():
                record=first_five_validation(out/"train.jsonl")
                if record:
                    write_json(out/"first-five-validation.json",record);early=True
                    self.event(key,"training",gpu=gpu,first_five_finite=True,
                               first_five_optimizer_updates=record["optimizer_updates"])
        args=self.train_args("retrieval",out)+["--adapter-init-state",self.protocol["shared_init"],
                                               "--value-last-bias-init",policy]
        self.wait_gpu(gpu,key)
        self.execute(args,self.output/"logs"/(key+"-train.log"),mode=key,stage="training",gpu=gpu,monitor=monitor)
        if not early: raise RuntimeError("First five real training iterations were not validated")
        coverage=self.validate_training("retrieval",out)
        cfg=read_json(out/"config.json")
        if (cfg["value_last_bias_init"]!=policy
            or cfg["adapter_init_state_sha256"]!=self.shared["file_sha256"]
            or cfg["trainable_parameters"]!=42607361):
            raise RuntimeError("Matched arm policy/parameter count differs")
        self.event(key,"train_complete",gpu=gpu,optimizer_updates=coverage["optimizer_updates"],
                   covered=coverage["actual_covered_ids"],exposures=coverage["examples"])
        checkpoint=out/"checkpoint_001334.pth"
        for mode in ("retrieval","off","random"):
            run=out/"inference"/mode;run.mkdir(parents=True)
            name=key+"-"+mode
            self.wait_gpu(gpu,name)
            rc=self.execute(self.infer_args(checkpoint,run/"dev.jsonl")+[
                                "--memory-mode",mode,"--value-last-bias-override","none"],
                            self.output/"logs"/(name+"-infer.log"),
                            mode=name,stage="generating_dev",gpu=gpu,allowed=(0,1))
            audit=self.validate_inference(run/"dev.jsonl",checkpoint,mode,"none")
            meta=read_json(run/"dev.meta.json")
            if meta["training_initialization"]["value_last_bias_init"]!=policy:
                raise RuntimeError("Inference omitted the correct training initialization")
            write_json(run/"inference-audit.json",audit)
            self.score(name,run/"dev.jsonl",run/"dev.meta.json")
            self.event(name,"complete",gpu=gpu,inference_returncode=rc,errors=audit["errors"])
        self.event(key,"complete",gpu=gpu,completed_at=now())

    def paired(self,pairs):
        def one(pair):
            current,baseline=pair
            report=read_json(self.reports[current])
            meta=report["metadata"]
            self.score(current+"-vs-"+baseline,meta["predictions"],
                       meta["inference_metadata"],paired=baseline)
        self.parallel(pairs,one)

    def finish(self):
        reports={key:read_json(path) for key,path in self.reports.items()}
        metrics={key:report["metrics"] for key,report in reports.items() if "paired" not in report}
        paired={key:{"delta":report["paired"]["delta"],
                     "intervals":report["paired"]["bootstrap"]["intervals"],
                     "negative_gain_fraction":report["paired"]["negative_gain_fraction"]}
                for key,report in reports.items() if "paired" in report}
        primary=paired["stage-b-zero_init-retrieval-vs-stage-b-control-retrieval"]
        practical=float(self.protocol["decision_rules"]["min_practical_micro_f1_gain"])
        flags={"zero_init_vs_control_positive_95ci":primary["intervals"]["micro_f1"][0]>0,
               "zero_init_vs_control_gain_at_least_preset":primary["delta"]["micro_f1"]>=practical,
               "all_new_predictions_without_errors":all(
                   value["failed_predictions"]==0 for key,value in metrics.items() if not key.startswith("ref-"))}
        for mode in ("off","random"):
            key="stage-b-zero_init-retrieval-vs-stage-b-zero_init-"+mode
            flags["zero_init_retrieval_beats_"+mode+"_95ci"]=paired[key]["intervals"]["micro_f1"][0]>0
        summary={"schema":"amg-bias-validation-summary-v1","finished_at":now(),
                 "metrics":metrics,"paired":paired,"decision_flags":flags,
                 "preset_practical_gain":practical,
                 "recommendation":"candidate_for_next_locked_validation" if all(flags.values()) else
                                  "do_not_expand_graph_or_training_budget_on_this_evidence",
                 "limitations":self.protocol["limitations"],"automatic_expansion":False}
        summary["final_learned_bias"] = {
            arm:reports["stage-b-"+arm+"-retrieval"]["metadata"]["model_intervention"]["target_before"]
            for arm in ARMS}
        summary["label_set_agreement"] = {}
        for arm in ARMS:
            normal=reports["stage-b-"+arm+"-retrieval"]["per_clip"]
            for mode in ("random","off"):
                other=reports["stage-b-"+arm+"-"+mode]["per_clip"]
                summary["label_set_agreement"][arm+"-retrieval-vs-"+mode] = {
                    "same":sum(a["prediction_labels"]==b["prediction_labels"] for a,b in zip(normal,other)),
                    "total":500}
        write_json(self.output/"summary.json",summary)
        lines=["# Bias validation: single seed 42","",
               "Source development only; the shared baseline already saw all source clips.",
               "Stage A clears a learned bias at inference and is an out-of-distribution mechanism probe.",
               "Stage B compares fresh matched Adapter starts; it does not reproduce the old unsaved initialization.",
               "Zero initialization keeps the bias trainable. Final inference preserves learned biases.","",
               "| Run | Micro F1 | Sample macro F1 | Failed / 500 |","|---|---:|---:|---:|"]
        for key,value in metrics.items():
            lines.append(f"| {key} | {value['micro_f1']:.6f} | {value['sample_macro_f1']:.6f} | {value['failed_predictions']} |")
        lines+=["","| Comparison (current minus reference) | Micro F1 delta | Paired 95% CI |",
                "|---|---:|---|"]
        for key,value in paired.items():
            interval=value["intervals"]["micro_f1"]
            lines.append(f"| {key} | {value['delta']['micro_f1']:+.6f} | [{interval[0]:+.6f}, {interval[1]:+.6f}] |")
        lines+=["","Decision flags: "+json.dumps(flags),summary["recommendation"],
                "","These intervals measure sample uncertainty for this seed, not training-seed variability.",
                "No heldout or target evaluation, full-data training, graph model or multi-seed jobs are scheduled."]
        (self.output/"SUMMARY.md").write_text("\n".join(lines)+"\n")
        self.state.update(status="complete",completed_at=now(),summary=str(self.output/"summary.json"))
        self.event("pipeline","complete")

    def run(self):
        try:
            result=self.validate()
            for name in ("logs","reports","interventions","training"):
                (self.output/name).mkdir(exist_ok=True)
            self.state["status"]="running";self.event("pipeline","validated",**result)
            self.score_refs()
            self.event("pipeline","stage_a")
            run_gpu_queue(("retrieval","random"),self.gpus,self.intervention,self.stop_event,self.stop_children)
            self.paired([("stage-a-zero-retrieval","ref-normal"),
                         ("stage-a-zero-random","ref-random"),
                         ("stage-a-zero-retrieval","stage-a-zero-random"),
                         ("stage-a-zero-retrieval","ref-off")])
            self.event("pipeline","stage_b",
                       note="Matched training proceeds regardless of Stage A score; only technical errors stop it")
            run_gpu_queue(ARMS,self.gpus,self.train_arm,self.stop_event,self.stop_children)
            self.check_starts(required=True)
            a,b=[exposure_signature(self.output/"training"/arm/"exposure.jsonl") for arm in ARMS]
            alignment={"schema":"amg-bias-exposure-alignment-v1","control":a,"zero_init":b,
                       "identical":a==b,"examples":a[1]}
            write_json(self.output/"exposure-alignment.json",alignment)
            if a!=b or a[1]!=4002: raise RuntimeError("Actual task/clip/budget training exposure differs")
            pairs=[("stage-b-zero_init-retrieval","stage-b-control-retrieval"),
                   ("stage-b-zero_init-retrieval","ref-off_trained"),
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
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--protocol",required=True);p.add_argument("--output-dir",required=True)
    p.add_argument("--python",default=DEFAULT_PYTHON);p.add_argument("--validate-only",action="store_true")
    args=p.parse_args(argv)
    experiment=BiasExperiment(args.protocol,args.output_dir,python=args.python)
    with (experiment.output/".run.lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.validate_only:
            print(json.dumps(experiment.validate()));return 0
        if (experiment.output/"state.json").exists():
            raise FileExistsError("Existing state: do not relaunch or overwrite this trial")
        for sig in (signal.SIGINT,signal.SIGTERM): signal.signal(sig,experiment.signal_handler)
        return experiment.run()
if __name__=="__main__":
    raise SystemExit(main())

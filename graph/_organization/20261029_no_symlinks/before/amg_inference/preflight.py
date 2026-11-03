"""CPU preflight; never allocates CUDA memory or generates target predictions."""
import os,sys,io,copy,unittest,ast
from pathlib import Path
from types import SimpleNamespace
from amg_runtime.common import read,sha,canonical,atomic_json,require
from .common import ROOT,verify,now,gate
def main():
 run=Path(read(ROOT/"amg_inference/runs/current.json")["path"]);p=verify(run)
 from .tests import QueueTests
 buffer=io.StringIO();result=unittest.TextTestRunner(stream=buffer).run(unittest.defaultTestLoader.loadTestsFromTestCase(QueueTests))
 require(result.wasSuccessful(),buffer.getvalue())
 os.chdir(ROOT/"AffectGPT");sys.path.insert(0,str(ROOT/"AffectGPT"))
 from omegaconf import OmegaConf
 from amg_finetune_nogc.dataset import GraphContinueDataset
 from .model import make_prompt
 training=Path(p["training_run"]);cfg=OmegaConf.create(read(training/"original_config.json")["model"])
 reader=GraphContinueDataset(training,cfg);chat=SimpleNamespace(tokenizer=reader.tokenizer,replace_token_for_multimodal=reader.replace_token_for_multimodal)
 source=read(run/"source_probe.json");row=source["record"];cache=read(source["cache_path"])
 prompt,info=make_prompt(reader,chat,row,cache["evidence"],p)
 train_ids,_,training_prompt,_=reader.text_example(0,"ovlabel")
 require(row["sample_id"]==reader.annotation[0]["sample_id"] and prompt==training_prompt,"Inference source prompt differs from the training ovlabel prompt")
 cases=[dict(case="exact_training_ovlabel_prompt",passed=True,info=info)]
 for kind,record,ev in [
  ("literal_multimodal_markers",dict(row,subtitle="literal <MultiHere> <FaceHere> <AudioHere>"),cache["evidence"]),
  ("long_subtitle",dict(row,subtitle=" observation"*5000),cache["evidence"]),
  ("graph_abstention",row,dict(copy.deepcopy(cache["evidence"]),fallback=dict(required=True)))]:
  _,stats=make_prompt(reader,chat,record,ev,p)
  require(stats["prompt_tokens"]+1200<=2736,"Prompt/output bound failed")
  if kind=="graph_abstention":require(stats["graph_tokens"]==0,"Abstaining graph unexpectedly inserted")
  cases.append(dict(case=kind,passed=True,info=stats))
 for d,spec in p["datasets"].items():
  records=read(spec["path"])
  require(len(records)==spec["samples"] and all(not({"emo","val","label","ovlabel","description"}&set(x)) for x in records),"Target labels leaked into input manifests")
  require(len({x["sample_id"] for x in records})==len(records),"Duplicate target identity")
 report=dict(passed=True,queue_tests=result.testsRun,prompt_cases=cases,logical_jobs=225,datasets=len(p["datasets"]),dataset_samples=p["dataset_samples_total"],target_generation_performed=False,gpu_capacity_test="pending until each training queue completes",training_completion_gates_now={str(g):gate(p["training_run"],g) for g in [0,1]},plan_id=p["plan_id"],finished_at_beijing=now())
 atomic_json(run/"cpu_preflight.json",report);print("CPU_PREFLIGHT_PASSED",run)
if __name__=="__main__":main()

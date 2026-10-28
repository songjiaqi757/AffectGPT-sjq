"""CPU checks for nine-dataset scoring, full barrier, LPT order and exclusive claims."""
import argparse,os,sys,tempfile
from pathlib import Path
from .common import ROOT,verify,read,sha,canonical,atomic_json,require,now
from .priority_score import phase_plan,resources
from .full_score import truth,validate_reused,all_inference_complete,claim_score,score_counts
from .full_controller import refresh_dispatch
def scheduling_checks(phase):
 with tempfile.TemporaryDirectory(dir=phase) as directory:
  folder=Path(directory);(folder/"evaluation_jobs").mkdir()
  for jid,cost in [("small",10),("medium",20),("large",30)]:
   atomic_json(folder/"evaluation_jobs"/(jid+".json"),dict(job_id=jid,estimated_seconds=cost,state="pending",attempts=0))
  a=claim_score(folder);b=claim_score(folder)
  require(a[2]["job_id"]=="large" and b[2]["job_id"]=="medium","Scoring LPT or exclusive claim failed")
  c=claim_score(folder);require(c[2]["job_id"]=="small" and claim_score(folder) is None,"Duplicate score claim allowed")
  for claimed in [a,b,c]:claimed[1].close()
 with tempfile.TemporaryDirectory(dir=phase) as directory:
  folder=Path(directory);(folder/"jobs").mkdir();ids=[f"j{i:03d}" for i in range(225)]
  for jid in ids:atomic_json(folder/"jobs"/(jid+".json"),dict(state="complete"))
  ph=dict(job_ids=ids);require(all_inference_complete(folder,ph),"225 complete jobs rejected")
  atomic_json(folder/"jobs"/(ids[-1]+".json"),dict(state="running"))
  require(not all_inference_complete(folder,ph),"Scoring would start with one inference job unfinished")
  (folder/"jobs"/(ids[-1]+".json")).unlink()
  require(not all_inference_complete(folder,ph),"Missing inference job bypassed barrier")
 with tempfile.TemporaryDirectory(dir=phase) as directory:
  folder=Path(directory);(folder/"jobs").mkdir();(folder/"predictions"/"partial").mkdir(parents=True)
  for i in range(70):(folder/"predictions"/"partial"/f"{i}.json").write_text("{}")
  for jid,dataset in [("small","tiny"),("large","big"),("partial","partial")]:
   atomic_json(folder/"jobs"/(jid+".json"),dict(state="pending",dataset=dataset))
  atomic_json(folder/"job_dispatch.json",dict(phase_id="fixture"))
  ph=dict(job_ids=["small","large","partial"],phase_id="fixture")
  ip=dict(plan_id="fixture",datasets={"tiny":{"samples":10},"big":{"samples":100},"partial":{"samples":120}})
  info=refresh_dispatch(folder,ph,ip);policy=read(folder/"job_dispatch.json")
  require(policy["job_ids"]==["large","partial","small"] and info["remaining_samples"]==160,"Inference dispatch ignores committed partial predictions")
 return dict(score_exclusive_lpt=True,all_225_barrier=True,missing_job_blocks_scoring=True,inference_remaining_work_lpt=True)
def main():
 a=argparse.ArgumentParser();a.add_argument("--phase",required=True);args=a.parse_args();phase=Path(args.phase).resolve();ph=phase_plan(phase);ip=verify(ph["inference_run"]);resources(phase);validate_reused(phase,ph)
 require(len(ph["checkpoints"])==25 and len(ph["job_ids"])==225 and len(ph["datasets"])==9,"Full evaluation cardinality mismatch")
 checks=scheduling_checks(phase)
 os.chdir(ROOT/"AffectGPT");sys.path.insert(0,str(ROOT/"AffectGPT"));import evaluation
 coverage={d:len(truth(d,ip,evaluation)) for d in ph["datasets"]}
 require(sum(coverage.values())==12799,"Unexpected test coverage")
 c=score_counts(phase);require(c=={"complete":60,"pending":165} or c=={"pending":165,"complete":60},"Reuse queue cardinality mismatch")
 prior=read(Path(ph["reuse_priority_phase"])/"evaluation_lock.json")
 current=resources(phase)
 require(all(current["files_sha256"][path]==digest for path,digest in prior["files_sha256"].items()),"Prior score protocol differs")
 report=dict(passed=True,phase_id=ph["phase_id"],coverage=coverage,checkpoint_count=25,inference_tasks=225,total_predictions=319975,reused_scores=60,remaining_scores=165,evaluation_gpus=[0,1],evaluation_processes_per_gpu=1,tests=checks,no_gpu_judge_loaded=True,no_new_predictions_scored=True,finished_at_beijing=now())
 atomic_json(phase/"preflight.json",report);print("FULL_DUAL_EVALUATION_PREFLIGHT_PASSED",phase)
if __name__=="__main__":main()

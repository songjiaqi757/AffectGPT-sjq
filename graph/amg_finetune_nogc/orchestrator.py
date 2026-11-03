"""No-gradient-checkpointing restart: accepted cache gate and two GPU queues."""
from graph_paths import hash_matches as _graph_hash_matches
import argparse,os,subprocess,time,traceback
from graph_paths import Path
from amg_runtime.common import read,sha,atomic_json,require
from .common import ROOT,PYTHON,load_plan,now,verify_code
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);a=p.parse_args();run=Path(a.run);plan=load_plan(run);verify_code(run)
 status=dict(phase="no_gc_preflight",pid=os.getpid(),plan_id=plan["plan_id"],llm_gradient_checkpointing=False,started_at_beijing=now())
 def update(**kw):
  status.update(kw,updated_at_beijing=now());atomic_json(run/"status.json",status)
  pointer=dict(path=str(run),plan_id=plan["plan_id"],training_count=30755,audit_count=500,status=status["phase"],llm_gradient_checkpointing=False,final_target_evaluation_allowed=False)
  atomic_json(ROOT/"amg_finetune/runs/current.json",pointer);atomic_json(ROOT/"amg_finetune_nogc/runs/current.json",pointer)
 try:
  update()
  while True:
   checks=[run/"integration_tests.json",run/"gpu_smoke_report.json",run/"cache_reuse_verification.json"]
   for path in checks:
    if path.exists():require(read(path).get("passed",False),"No-GC preparation failed: "+path.name)
   if all(path.exists() for path in checks):break
   time.sleep(3)
  smoke=read(run/"gpu_smoke_report.json")
  require(smoke["llm_gradient_checkpointing"] is False,"GPU trial did not disable gradient checkpointing")
  require(smoke["maximum_context_stress"]["passed"] and smoke["maximum_context_stress"]["gradient_checkpointing_active"] is False,"Longest-input no-GC stress test failed")
  verify_code(run)
  source=Path(plan["cache"]["source_manifest"])
  require(_graph_hash_matches(source, plan['cache']['source_manifest_sha256'], sha(source)),"Accepted source cache manifest changed")
  jobs=[]
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",TOKENIZERS_PARALLELISM="false",OMP_NUM_THREADS="4",OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="4",PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
  for gpu in [0,1]:
   log=(run/f"queue_gpu_{gpu}.log").open("ab",buffering=0)
   child=subprocess.Popen([str(PYTHON),"-u","-m","amg_finetune_nogc.queue_worker","--run",str(run),"--gpu",str(gpu)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
   jobs.append(dict(gpu=gpu,pid=child.pid))
  atomic_json(run/"queue_jobs.json",jobs);update(phase="training",queues=jobs)
  while True:
   states=[read(run/f"gpu_{gpu}_queue_status.json") if (run/f"gpu_{gpu}_queue_status.json").exists() else dict(state="starting") for gpu in [0,1]]
   update(queue_status=states)
   require(not any(s["state"]=="failed" for s in states),"A no-GC queue failed; no automatic switch back to gradient checkpointing is permitted")
   if all(s["state"]=="complete" for s in states):break
   time.sleep(30)
  update(phase="complete",completed_experiments=5,finished_at_beijing=now())
 except Exception as exc:update(phase="failed",error=type(exc).__name__+": "+str(exc),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

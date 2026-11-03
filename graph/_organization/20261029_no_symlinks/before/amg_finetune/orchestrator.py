"""Server-side cache gate, full preflight and two independent GPU training queues."""
import argparse,os,subprocess,time,traceback
from pathlib import Path
from amg_runtime.common import read,sha,atomic_json,require
from .common import ROOT,PYTHON,load_plan,now,verify_code
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);a=p.parse_args();run=Path(a.run);plan=load_plan(run);verify_code(run)
 status=dict(phase="preparing_graph_evidence",pid=os.getpid(),plan_id=plan["plan_id"],started_at_beijing=now())
 def update(**kw):
  status.update(kw,updated_at_beijing=now());atomic_json(run/"status.json",status)
  atomic_json(ROOT/"amg_finetune/runs/current.json",dict(path=str(run),plan_id=plan["plan_id"],training_count=30755,audit_count=500,status=status["phase"],final_target_evaluation_allowed=False))
 try:
  update()
  while True:
   stages=[read(run/f"cache_worker_{w}_status.json") if (run/f"cache_worker_{w}_status.json").exists() else dict(state="starting",completed=0) for w in [0,1]]
   require(not any(s["state"]=="failed" for s in stages),"A cache worker failed; training remains gated")
   update(cache_completed=sum(s.get("completed",0) for s in stages),cache_total=30755)
   if all(s["state"]=="complete" for s in stages):break
   time.sleep(15)
  require(read(run/"integration_tests.json")["passed"],"Integration tests failed")
  require(read(run/"gpu_smoke_report.json")["passed"],"Real GPU forward/backward preflight failed")
  require(bool(read(run/"model_assets_manifest.json")["assets"]),"Pretrained model assets not fingerprinted")
  update(phase="full_cache_and_prompt_preflight")
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",TOKENIZERS_PARALLELISM="false",OMP_NUM_THREADS="2",OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="2")
  with (run/"preflight.log").open("ab",buffering=0) as f:
   result=subprocess.run([str(PYTHON),"-u","-m","amg_finetune.preflight","--run",str(run)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  require(result.returncode==0,"Full preflight failed; training remains gated")
  require(read(run/"cache_manifest.json")["complete"],"No accepted cache manifest")
  # Cache processes must release CUDA before the single-GPU training queues are created.
  cache_jobs=read(run/"cache_jobs.json")
  for job in cache_jobs:
   path=Path("/proc")/str(job["pid"])/"cmdline"
   while path.exists() and b"amg_finetune.cache_worker" in path.read_bytes():time.sleep(2)
  queues=[]
  for gpu in [0,1]:
   log=(run/f"queue_gpu_{gpu}.log").open("ab",buffering=0)
   child=subprocess.Popen([str(PYTHON),"-u","-m","amg_finetune.queue_worker","--run",str(run),"--gpu",str(gpu)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
   queues.append(dict(gpu=gpu,pid=child.pid))
  atomic_json(run/"queue_jobs.json",queues);update(phase="training",queues=queues)
  while True:
   states=[read(run/f"gpu_{g}_queue_status.json") if (run/f"gpu_{g}_queue_status.json").exists() else dict(state="starting") for g in [0,1]]
   update(queue_status=states)
   if any(s["state"]=="failed" for s in states):raise RuntimeError("A GPU training queue failed; consult queue/experiment logs")
   if all(s["state"]=="complete" for s in states):break
   time.sleep(30)
  update(phase="complete",finished_at_beijing=now(),completed_experiments=5)
  atomic_json(ROOT/"amg_finetune/runs/current.json",dict(path=str(run),plan_id=plan["plan_id"],training_count=30755,audit_count=500,status="complete",final_target_evaluation_allowed=False))
 except Exception as exc:update(phase="failed",error=type(exc).__name__+": "+str(exc),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

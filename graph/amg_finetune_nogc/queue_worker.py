"""One process queue per physical GPU; next checkpoint starts only after successful completion."""
import argparse,fcntl,os,subprocess,time,traceback
from graph_paths import Path
from amg_runtime.common import read,sha,atomic_json,require
from .common import ROOT,PYTHON,load_plan,now,verify_code
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);p.add_argument("--gpu",type=int,required=True);a=p.parse_args()
 run=Path(a.run);plan=load_plan(run);verify_code(run);jobs=[r for r in plan["checkpoints"] if r["gpu"]==a.gpu]
 lock=(ROOT/"amg_finetune_nogc"/f"gpu_{a.gpu}.lock").open("w");fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 status=dict(state="running",gpu=a.gpu,pid=os.getpid(),queue=[r["base_epoch"] for r in jobs],completed=[],started_at_beijing=now())
 def update(**kw):status.update(kw,updated_at_beijing=now());atomic_json(run/f"gpu_{a.gpu}_queue_status.json",status)
 try:
  update()
  for spec in jobs:
   epoch=spec["base_epoch"];log=(run/f"train_from_{epoch}.log").open("ab",buffering=0)
   env=dict(os.environ,PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True",CUDA_VISIBLE_DEVICES=str(a.gpu),PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",TOKENIZERS_PARALLELISM="false",OMP_NUM_THREADS="4",MKL_NUM_THREADS="4",OPENBLAS_NUM_THREADS="1")
   env.pop("RANK",None);env.pop("WORLD_SIZE",None);env.pop("LOCAL_RANK",None)
   child=subprocess.Popen([str(PYTHON),"-u","-m","amg_finetune_nogc.train_worker","--run",str(run),"--base-epoch",str(epoch)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
   update(current_base_epoch=epoch,child_pid=child.pid,log=str(run/f"train_from_{epoch}.log"))
   code=child.wait();log.close()
   require(code==0,"Training from "+str(epoch)+" failed with exit code "+str(code))
   require(read(run/f"experiment_{epoch}_status.json")["state"]=="complete","Child did not finish five epochs")
   status["completed"].append(epoch);update()
  update(state="complete",finished_at_beijing=now())
 except Exception as exc:update(state="failed",error=type(exc).__name__+": "+str(exc),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

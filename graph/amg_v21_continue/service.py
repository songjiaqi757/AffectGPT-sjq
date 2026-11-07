import argparse,os,subprocess,time,traceback
from pathlib import Path
from .common import *
def main():
 a=argparse.ArgumentParser();a.add_argument("--run",required=True);a.add_argument("--folds",required=True);x=a.parse_args();run=Path(x.run)
 children=[]
 for k in map(int,x.folds.split(",")):
  log=(run/"folds"/str(k)/"prepare.log").open("ab",buffering=0)
  child=subprocess.Popen([str(PYTHON),"-u","-B","-m","amg_v21_continue.prepare","--run",str(run),"--fold",str(k)],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,CUDA_VISIBLE_DEVICES="",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1"))
  atomic_json(run/"folds"/str(k)/"process.json",dict(pid=child.pid,node_port=os.environ.get("TASK_SSH_PORT"),started_at_beijing=now()))
  children.append((k,child,log))
 failed=[]
 for k,child,log in children:
  code=child.wait();log.close()
  if code:failed.append(dict(fold=k,exit_code=code))
 require(not failed,"OOF fold workers failed: "+repr(failed))
if __name__=="__main__":main()

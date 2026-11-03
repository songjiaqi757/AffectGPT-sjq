"""Detached server supervisor; a card is claimed only after its whole training queue."""
import argparse,os,subprocess,time,traceback
from graph_paths import Path
from amg_runtime.common import read,atomic_json,require
from .common import ROOT,PYTHON,verify,now,gate,locked,counts
def environment(gpu):
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu),PYTHONDONTWRITEBYTECODE="1",PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",TOKENIZERS_PARALLELISM="false",OMP_NUM_THREADS="4",MKL_NUM_THREADS="4",OPENBLAS_NUM_THREADS="1")
 for k in ["RANK","WORLD_SIZE","LOCAL_RANK"]:env.pop(k,None)
 return env
def launch(run,gpu,module,extra,tag):
 log=(run/(tag+".log")).open("ab",buffering=0)
 proc=subprocess.Popen([str(PYTHON),"-u","-m",module,"--run",str(run)]+extra,cwd=ROOT,env=environment(gpu),stdout=log,stderr=subprocess.STDOUT)
 log.close();return proc
def stop(processes):
 for proc in processes:
  if proc.poll() is None:proc.terminate()
 deadline=time.monotonic()+30
 for proc in processes:
  try:proc.wait(timeout=max(.1,deadline-time.monotonic()))
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
def card(run,gpu):
 p=verify(run);s=dict(state="waiting_for_training",gpu=gpu,pid=os.getpid(),started_at_beijing=now())
 def update(**kw):s.update(kw,updated_at_beijing=now());atomic_json(run/f"gpu_{gpu}_status.json",s)
 children=[];gpu_lock=None
 try:
  update()
  while not gate(p["training_run"],gpu):
   q=read(Path(p["training_run"])/f"gpu_{gpu}_queue_status.json")
   require(q["state"]!="failed","Training queue failed: "+str(gpu))
   update(training_queue=q);time.sleep(30)
  while gpu_lock is None:
   gpu_lock=locked(ROOT/"amg_finetune_nogc"/f"gpu_{gpu}.lock")
   if gpu_lock is None:update(state="waiting_for_training_lock_release");time.sleep(5)
  # The same exclusive GPU lock as the training queue prevents overlap.
  require(gate(p["training_run"],gpu),"Training completion gate changed")
  update(state="waiting_for_shared_cache")
  while True:
   status=run/"cache_status.json"
   if status.exists() and read(status)["state"]=="complete":break
   cache_lock=locked(run/"cache.lock")
   if cache_lock is None:time.sleep(20);continue
   try:
    if not (status.exists() and read(status)["state"]=="complete"):
     update(state="building_shared_graph_cache")
     proc=launch(run,gpu,"amg_inference.cache_worker",[],f"cache_gpu_{gpu}");children=[proc]
     require(proc.wait()==0,"Frozen target-input graph cache preparation failed")
     require(read(status)["state"]=="complete","Cache did not complete")
   finally:cache_lock.close()
   break
  # All three models must coexist and complete full-window source generation before targets.
  update(state="source_capacity_probe")
  go=run/f"gpu_{gpu}_probe_go.json"
  if go.exists():go.unlink()
  for slot in range(3):
   f=run/f"gpu_{gpu}_probe_{slot}_status.json"
   if f.exists():f.unlink()
  children=[launch(run,gpu,"amg_inference.worker",["--slot",str(slot),"--smoke"],f"gpu_{gpu}_probe_{slot}") for slot in range(3)]
  deadline=time.monotonic()+1800
  while True:
   require(time.monotonic()<deadline,"Three-process model loading timed out")
   require(all(proc.poll() is None for proc in children),"A source probe failed during model loading")
   ready=[run/f"gpu_{gpu}_probe_{slot}_status.json" for slot in range(3)]
   if all(f.exists() and read(f)["state"]=="ready" for f in ready):break
   time.sleep(5)
  atomic_json(go,dict(started_at_beijing=now(),pids=[c.pid for c in children]))
  deadline=time.monotonic()+1800
  while any(proc.poll() is None for proc in children):
   require(time.monotonic()<deadline,"Full-window generation capacity probe timeout")
   require(not any(proc.poll() not in [None,0] for proc in children),"Concurrent source generation failed")
   time.sleep(5)
  reports=[read(f) for f in ready]
  require(all(proc.returncode==0 for proc in children) and all(r.get("passed") for r in reports),"Concurrent source capacity probe did not pass")
  atomic_json(run/f"gpu_{gpu}_capacity.json",dict(passed=True,concurrent_models=3,full_prompt_limit=1536,generated_tokens_per_probe=1200,source_only=True,reports=reports,finished_at_beijing=now()))
  update(state="inference_running")
  children=[launch(run,gpu,"amg_inference.worker",["--slot",str(slot)],f"gpu_{gpu}_worker_{slot}") for slot in range(3)]
  restarts=[0,0,0]
  while True:
   summary=counts(run);update(jobs=summary,pids=[c.pid for c in children],worker_restarts=restarts)
   if summary.get("complete",0)+summary.get("failed",0)==p["logical_jobs"]:
    stop(children)
    require(summary.get("failed",0)==0,"Some inference jobs exhausted their retries")
    break
   for slot,proc in enumerate(children):
    if proc.poll() is not None:
     restarts[slot]+=1;require(restarts[slot]<=5,"Inference worker repeatedly failed; inspect its log")
     children[slot]=launch(run,gpu,"amg_inference.worker",["--slot",str(slot)],f"gpu_{gpu}_worker_{slot}")
   time.sleep(30)
  update(state="complete",finished_at_beijing=now())
 except BaseException as exc:
  stop(children);update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:
  if gpu_lock is not None:gpu_lock.close()
def main():
 a=argparse.ArgumentParser();a.add_argument("--run",required=True);a.add_argument("--gpu",type=int);args=a.parse_args();run=Path(args.run).resolve();p=verify(run)
 if args.gpu is not None:card(run,args.gpu);return
 preflight=read(run/"cpu_preflight.json");require(preflight["passed"] and preflight["plan_id"]==p["plan_id"],"CPU preflight has not passed")
 owner=locked(run/"controller.lock");require(owner is not None,"Inference controller already active")
 children=[];status=dict(state="waiting_for_training",pid=os.getpid(),pgid=os.getpgrp(),plan_id=p["plan_id"],logical_jobs=225,concurrency_per_gpu=3,started_at_beijing=now())
 def update(**kw):status.update(kw,updated_at_beijing=now());atomic_json(run/"controller_status.json",status)
 try:
  for gpu in [0,1]:
   children.append(launch(run,gpu,"amg_inference.controller",["--gpu",str(gpu)],f"gpu_{gpu}_controller"))
  while True:
   summary=counts(run);states={}
   for gpu in [0,1]:
    f=run/f"gpu_{gpu}_status.json"
    if f.exists():states[str(gpu)]=read(f)["state"]
   update(jobs=summary,cards=states,child_pids=[x.pid for x in children])
   if all(x.poll() is not None for x in children):
    require(all(x.returncode==0 for x in children) and summary.get("complete",0)==225,"Inference pipeline ended before all 225 jobs completed")
    break
   if any(x.poll() not in [None,0] for x in children):update(state="needs_attention")
   elif any(s in ["building_shared_graph_cache","source_capacity_probe","inference_running"] for s in states.values()):update(state="running")
   time.sleep(30)
  update(state="complete",finished_at_beijing=now())
 except BaseException as exc:stop(children);update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:owner.close()
if __name__=="__main__":main()

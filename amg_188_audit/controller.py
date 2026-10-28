
import argparse,signal,subprocess,time,traceback,collections
from .common import *
from .metrics import prepare,assemble
def gpu_used(g):return int(subprocess.check_output(["nvidia-smi","--id="+str(g),"--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip())
def stop(proc):
 if proc.poll() is None:
  try:os.killpg(proc.pid,signal.SIGTERM)
  except ProcessLookupError:pass
def free_gpus():
 deadline=time.monotonic()+180
 while any(gpu_used(g)>256 for g in [0,1]):
  require(time.monotonic()<deadline,"GPU memory not released");time.sleep(3)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);a=ap.parse_args();run=Path(a.run);p=plan(run);verify_code(run)
 owner=locked(run/"controller.lock");require(owner is not None,"Controller already running");handles=[];children=[];state=dict(pid=os.getpid(),plan_id=p["plan_id"],started_at_beijing=now())
 def update(**kw):state.update(kw,updated_at_beijing=now());atomic_json(run/"status.json",state)
 def halted(*unused):raise KeyboardInterrupt("Controller signal")
 signal.signal(signal.SIGTERM,halted);signal.signal(signal.SIGINT,halted)
 try:
  require(read(run/"cpu_preflight.json")["passed"],"CPU preflight failed")
  for g in [0,1]:
   h=locked(ROOT/"amg_finetune_nogc"/f"gpu_{g}.lock");require(h is not None,"GPU lock unavailable");handles.append(h);require(gpu_used(g)<256,"GPU not idle")
  if complete_count(run)<p["logical_jobs"]:
   for g in [0,1]:
    for kind in ["probe_go","probe_accepted"]:
     f=run/f"{kind}_gpu_{g}.json"
     if f.exists():f.unlink()
   procs={}
   for g in [0,1]:
    for slot in range(4):
     proc=launch_module(run,"infer_worker",["--gpu",str(g),"--slot",str(slot)],f"inference_gpu_{g}_slot_{slot}.log",g);procs[g,slot]=proc;children.append(proc)
   accepted=set();go=set();retries=collections.Counter();deadline=time.monotonic()+1800;run_deadline=time.monotonic()+p["max_inference_seconds"]
   while complete_count(run)<p["logical_jobs"]:
    for g in [0,1]:
     snapshots=[read(run/f"inference_gpu_{g}_slot_{s}.json") if (run/f"inference_gpu_{g}_slot_{s}.json").exists() else {} for s in range(4)]
     if g not in go and all(x.get("state")=="probe_loaded" for x in snapshots):
      atomic_json(run/f"probe_go_gpu_{g}.json",dict(time_beijing=now(),source_only=True));go.add(g)
     if g not in accepted and all(x.get("capacity_passed",False) for x in snapshots):
      atomic_json(run/f"probe_accepted_gpu_{g}.json",dict(passed=True,full_window_1536_plus_1200=True,source_only=True,reports=snapshots));accepted.add(g)
     for slot in range(4):
      proc=procs[g,slot]
      if proc.poll() is not None:
       require(proc.returncode==0 and complete_count(run)==p["logical_jobs"] or g in accepted,"Worker failed before capacity acceptance")
       if complete_count(run)<p["logical_jobs"]:
        retries[g,slot]+=1;require(retries[g,slot]<=2,"Inference repeatedly failed")
        procs[g,slot]=launch_module(run,"infer_worker",["--gpu",str(g),"--slot",str(slot)],f"inference_gpu_{g}_slot_{slot}.log",g);children.append(procs[g,slot])
    update(phase="inference" if len(accepted)==2 else "capacity_probe",capacity_accepted_gpus=sorted(accepted),inference_jobs_complete=complete_count(run),inference_jobs_total=p["logical_jobs"],inference_pids={str(g):[procs[g,s].pid for s in range(4)] for g in [0,1]})
    require(len(accepted)==2 or time.monotonic()<deadline,"Capacity timeout");require(time.monotonic()<run_deadline,"Inference budget exceeded");time.sleep(15)
   update(phase="waiting_for_inference_exit")
   for proc in procs.values():proc.wait(timeout=180);require(proc.returncode==0,"Inference exit failure")
  free_gpus();atomic_json(run/"evaluation_barrier.json",dict(passed=True,inference_jobs=p["logical_jobs"],all_inference_exited=True,time_beijing=now()))
  for stage in ["openset","sentiment"]:
   total=prepare(run,stage);update(phase="judge_"+stage,unique_inputs=total)
   procs=[launch_module(run,"judge_worker",["--gpu",str(g),"--stage",stage],f"judge_{stage}_gpu_{g}.log",g) for g in [0,1]];children.extend(procs)
   deadline=time.monotonic()+p["max_judge_stage_seconds"]
   while any(proc.poll() is None for proc in procs):
    for proc in procs:require(proc.poll() in [None,0],"Judge worker failed; see log")
    update(judge_inputs_complete=len(list((run/"judge_cache"/stage).glob("*.json"))),judge_inputs_total=total)
    require(time.monotonic()<deadline,"Judge stage budget exceeded");time.sleep(15)
   require(all(proc.returncode==0 for proc in procs),"Judge exit failure");free_gpus()
  update(phase="cpu_metrics");n=assemble(run)
  require(n==p["logical_jobs"],"Score count mismatch")
  update(phase="complete",scores_complete=n,result=str(run/"RESULTS.md"),finished_at_beijing=now(),next_stage="Dev admission required; no automatic graph changes or training.")
 except BaseException as exc:
  for proc in children:stop(proc)
  update(phase="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:
  for h in handles:h.close()
  owner.close()
if __name__=="__main__":main()

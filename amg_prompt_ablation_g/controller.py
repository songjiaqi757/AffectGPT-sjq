"""Two GPUs, four exclusive inference lanes per GPU, followed by one judge per GPU."""
import argparse,collections,csv,io,os,signal,subprocess,time,traceback
from .common import *
def stop(proc):
 if proc is not None and proc.poll() is None:
  try:os.killpg(proc.pid,signal.SIGTERM)
  except ProcessLookupError:pass
def gpu_used(gpu):
 return int(subprocess.check_output(["nvidia-smi","--id="+str(gpu),"--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip())
from .report import summarize
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);a=ap.parse_args();run=Path(a.run);p=plan(run);verify_code(run)
 owner=locked(run/"controller.lock");require(owner is not None,"Experiment already running")
 require(read(run/"cpu_preflight.json")["passed"],"CPU preflight must pass")
 handles=[];children=[];infer={};scorers=[];restarts=collections.Counter();go=set();accepted=set()
 state=dict(phase="starting",pid=os.getpid(),pgid=os.getpgrp(),plan_id=p["plan_id"],started_at_beijing=now())
 def update(**kw):state.update(kw,updated_at_beijing=now());atomic_json(run/"status.json",state)
 def on_signal(*args):raise KeyboardInterrupt("Controller stopped by signal")
 signal.signal(signal.SIGTERM,on_signal)
 try:
  for gpu in [0,1]:
   h=locked(ROOT/"amg_finetune_nogc"/f"gpu_{gpu}.lock");require(h is not None,f"GPU {gpu} lock is held by another run");handles.append(h)
   require(gpu_used(gpu)<256,f"GPU {gpu} is not free")
  if complete_count(run)<p["logical_jobs"]:
   for gpu in [0,1]:
    for name in ["probe_go","probe_accepted"]:
     marker=run/f"{name}_gpu_{gpu}.json"
     if marker.exists():marker.unlink()
    infer[gpu]=[launch(run,"amg_prompt_ablation_g.infer_worker",["--gpu",str(gpu),"--slot",str(slot)],f"inference_gpu_{gpu}_slot_{slot}.log",gpu) for slot in range(4)]
    children.extend(infer[gpu])
   update(phase="capacity_loading",inference_pids={str(g):[x.pid for x in xs] for g,xs in infer.items()})
   deadline=time.monotonic()+1800
   while True:
    for gpu in [0,1]:
     snapshots=[read(run/f"inference_gpu_{gpu}_slot_{slot}.json") if (run/f"inference_gpu_{gpu}_slot_{slot}.json").exists() else {} for slot in range(4)]
     if gpu not in go and all(s.get("state")=="probe_loaded" for s in snapshots):
      atomic_json(run/f"probe_go_gpu_{gpu}.json",dict(time_beijing=now(),concurrent_models=4));go.add(gpu)
     if gpu not in accepted and all(s.get("capacity_passed",False) for s in snapshots):
      atomic_json(run/f"probe_accepted_gpu_{gpu}.json",dict(passed=True,concurrent_models=4,source_only_full_window=True,reports=snapshots,time_beijing=now()));accepted.add(gpu)
     for slot,proc in enumerate(infer[gpu]):
      if proc.poll() not in [None,0] and complete_count(run)<p["logical_jobs"]:
       require(gpu in accepted,f"GPU {gpu} four-lane capacity/loading failed; see worker log")
       restarts[(gpu,slot)]+=1;require(restarts[(gpu,slot)]<=3,"Repeated inference failure")
       infer[gpu][slot]=launch(run,"amg_prompt_ablation_g.infer_worker",["--gpu",str(gpu),"--slot",str(slot)],f"inference_gpu_{gpu}_slot_{slot}.log",gpu);children.append(infer[gpu][slot])
    done=complete_count(run)
    update(phase="inference" if len(accepted)==2 else "capacity_probe",
       capacity_accepted_gpus=sorted(accepted),inference_jobs_complete=done,inference_jobs_total=p["logical_jobs"],
       inference_pids={str(g):[x.pid for x in xs] for g,xs in infer.items()})
    if done==p["logical_jobs"]:break
    require(len(accepted)==2 or time.monotonic()<deadline,"Capacity probe timed out")
    time.sleep(10)
   update(phase="waiting_for_inference_exit")
   for xs in infer.values():
    for proc in xs:proc.wait(timeout=180);require(proc.returncode==0,"Inference worker exit failure")
  deadline=time.monotonic()+180
  while any(gpu_used(g)>256 for g in [0,1]):
   require(time.monotonic()<deadline,"Inference memory was not released before judge stage");time.sleep(3)
  atomic_json(run/"evaluation_barrier.json",dict(passed=True,all_inference_jobs=p["logical_jobs"],inference_processes_exited=True,gpus_released=[0,1],time_beijing=now()))
  if len(list((run/"scores").glob("*.json")))<p["logical_jobs"]:
   scorers=[launch(run,"amg_prompt_ablation_g.score_worker",["--gpu",str(g)],f"evaluation_gpu_{g}.log",g) for g in [0,1]];children.extend(scorers)
   update(phase="dual_gpu_evaluation",evaluation_pids=[x.pid for x in scorers])
   while True:
    n=summarize(run,p);update(scores_complete=n,evaluation_pids=[x.pid for x in scorers])
    if n==p["logical_jobs"]:break
    for gpu,proc in enumerate(scorers):
     if proc.poll() is not None:
      restarts[("judge",gpu)]+=1;require(restarts[("judge",gpu)]<=3,"Repeated judge failure")
      require(gpu_used(gpu)<256,"Judge GPU has not been released")
      scorers[gpu]=launch(run,"amg_prompt_ablation_g.score_worker",["--gpu",str(gpu)],f"evaluation_gpu_{gpu}.log",gpu);children.append(scorers[gpu])
    time.sleep(15)
   for proc in scorers:proc.wait(timeout=180);require(proc.returncode==0,"Judge exit failure")
  summarize(run,p,final=True)
  update(phase="complete",weights=2,conditions=1,reference_conditions=6,datasets=3,predictions=p["sample_predictions_total"],scores=p["logical_jobs"],finished_at_beijing=now(),summary=str(run/"RESULTS.md"))
 except BaseException as exc:
  for proc in children:stop(proc)
  update(phase="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:
  for h in handles:h.close()
  owner.close()
if __name__=="__main__":main()

"""Supplement the existing three workers with one supervised lane per idle GPU."""
import argparse,os,subprocess,time,traceback,datetime
from graph_paths import Path
from amg_runtime.common import read,atomic_json,require
from .common import ROOT,PYTHON,verify,now,gate,locked,counts
from .controller import environment,launch,stop
def alive(pid):
 try:
  s=Path("/proc",str(pid),"stat").read_text().rsplit(")",1)[1].split()[0]
  return s!="Z"
 except (FileNotFoundError,ProcessLookupError):return False
def ready_snapshot(card,capacity,workers):
 return (card.get("state")=="inference_running" and len(card.get("pids",[]))==3
  and capacity.get("passed") and capacity.get("concurrent_models")==3
  and len(workers)==3 and all(w.get("state")=="running" and w.get("completed_samples",0)>0 for w in workers))
def base_ready(run,p,gpu):
 f=run/f"gpu_{gpu}_status.json";cap=run/f"gpu_{gpu}_capacity.json"
 if not f.exists() or not cap.exists() or not gate(p["training_run"],gpu):return False
 card=read(f);workers=[]
 for slot in range(3):
  f=run/f"gpu_{gpu}_worker_{slot}_status.json"
  if not f.exists():return False
  workers.append(read(f))
 return bool(ready_snapshot(card,read(cap),workers) and alive(card["pid"]) and all(alive(pid) for pid in card["pids"]))
def gpu_usage(gpu):
 result=subprocess.run(["nvidia-smi","--id="+str(gpu),"--query-gpu=memory.used,memory.free,utilization.gpu","--format=csv,noheader,nounits"],capture_output=True,text=True,check=True)
 used,free,util=[int(v.strip()) for v in result.stdout.strip().split(",")]
 return dict(used_mib=used,free_mib=free,utilization_percent=util,time_beijing=now())
def terminal(run,p):
 c=counts(run);return c.get("complete",0)+c.get("failed",0)==p["logical_jobs"]
def card(run,gpu):
 p=verify(run);owner=locked(run/f"gpu_{gpu}_fourth_lane.lock");require(owner is not None,"Fourth lane already supervised")
 child=None;s=dict(state="waiting_for_original_three",gpu=gpu,pid=os.getpid(),slot=3,effective_concurrency=4,started_at_beijing=now())
 def update(**kw):s.update(kw,updated_at_beijing=now());atomic_json(run/f"gpu_{gpu}_fourth_lane_status.json",s)
 try:
  update()
  while not base_ready(run,p,gpu):
   if terminal(run,p):update(state="complete",reason="All jobs already terminal");return
   update();time.sleep(15)
  original=read(run/f"gpu_{gpu}_status.json")
  probe_file=run/f"gpu_{gpu}_probe_3_status.json"
  if probe_file.exists():
   stamp=now()[:19].replace(":","").replace("-","")
   probe_file.replace(run/f"gpu_{gpu}_probe_3_previous_{stamp}.json")
  require((run/f"gpu_{gpu}_probe_go.json").exists(),"Original capacity barrier missing")
  update(state="fourth_source_capacity_probe",original_card_pid=original["pid"])
  child=launch(run,gpu,"amg_inference.worker",["--slot","3","--smoke"],f"gpu_{gpu}_probe_3")
  deadline=time.monotonic()+1800;peak=0;concurrent_samples=0
  while child.poll() is None:
   require(time.monotonic()<deadline,"Fourth-lane capacity test timed out")
   current=read(run/f"gpu_{gpu}_status.json")
   require(current["state"]=="inference_running" and current["pid"]==original["pid"] and all(alive(pid) for pid in original["pids"]),"Original three workers stopped during the capacity probe")
   usage=gpu_usage(gpu);peak=max(peak,usage["used_mib"])
   if probe_file.exists() and read(probe_file).get("state") in ["ready","validating_probe","complete"]:concurrent_samples+=1
   update(probe_pid=child.pid,gpu_usage=usage,peak_total_used_mib=peak)
   time.sleep(5)
  require(child.returncode==0,"Fourth source-only probe failed; inspect its log")
  report=read(probe_file)
  require(report.get("passed") and concurrent_samples>0,"Fourth source probe did not pass with three live workers")
  atomic_json(run/f"gpu_{gpu}_four_lane_capacity.json",dict(passed=True,concurrent_models=4,method="Existing three live target-inference models plus a fourth source-only full-window probe",source_probe=report,original_pids=original["pids"],concurrent_observations=concurrent_samples,peak_total_used_mib=peak,finished_at_beijing=now(),original_protocol_unchanged=True))
  update(state="starting_fourth_inference",capacity_passed=True)
  child=launch(run,gpu,"amg_inference.worker",["--slot","3"],f"gpu_{gpu}_worker_3")
  restarts=0;last_live=0
  while True:
   summary=counts(run)
   update(state="inference_running",worker_pid=child.pid,jobs=summary,gpu_usage=gpu_usage(gpu),worker_restarts=restarts)
   if terminal(run,p):
    stop([child]);require(summary.get("failed",0)==0,"Some tasks failed");break
   current=read(run/f"gpu_{gpu}_status.json")
   require(current["state"]=="inference_running" and alive(current["pid"]),"Original per-GPU supervisor stopped")
   if child.poll() is not None:
    restarts+=1;require(restarts<=5,"Fourth inference worker repeatedly failed")
    child=launch(run,gpu,"amg_inference.worker",["--slot","3"],f"gpu_{gpu}_worker_3")
   time.sleep(15)
  update(state="complete",finished_at_beijing=now())
 except BaseException as exc:
  if child is not None:stop([child])
  update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:owner.close()
def self_test():
 card=dict(state="inference_running",pids=[1,2,3]);capacity=dict(passed=True,concurrent_models=3);workers=[dict(state="running",completed_samples=1) for _ in range(3)]
 require(ready_snapshot(card,capacity,workers),"Ready three lanes rejected")
 require(not ready_snapshot(dict(card,state="waiting_for_training"),capacity,workers),"Training gate bypassed")
 require(not ready_snapshot(card,dict(capacity,passed=False),workers),"Capacity gate bypassed")
 require(not ready_snapshot(card,capacity,[dict(state="running",completed_samples=0)]+workers[1:]),"A cold worker counted as a resident model")
 print("Fourth-lane readiness checks passed")
def main():
 a=argparse.ArgumentParser();a.add_argument("--run");a.add_argument("--gpu",type=int);a.add_argument("--self-test",action="store_true");args=a.parse_args()
 if args.self_test:self_test();return
 run=Path(args.run).resolve()
 if args.gpu is not None:card(run,args.gpu);return
 p=verify(run);owner=locked(run/"fourth_lane_controller.lock");require(owner is not None,"Fourth-lane controller already active")
 children=[];s=dict(state="running",pid=os.getpid(),pgid=os.getpgrp(),concurrency_per_gpu=4,original_lanes=3,extra_lanes=1,plan_id=p["plan_id"],started_at_beijing=now())
 try:
  for gpu in [0,1]:children.append(launch(run,gpu,"amg_inference.fourth_lane",["--gpu",str(gpu)],f"gpu_{gpu}_fourth_lane_controller"))
  while any(c.poll() is None for c in children):
   cards={}
   for gpu in [0,1]:
    f=run/f"gpu_{gpu}_fourth_lane_status.json"
    if f.exists():cards[str(gpu)]=read(f)["state"]
   s.update(state="needs_attention" if any(c.poll() not in [None,0] for c in children) else "running",cards=cards,pids=[c.pid for c in children],jobs=counts(run),updated_at_beijing=now());atomic_json(run/"fourth_lane_controller_status.json",s)
   time.sleep(15)
  require(all(c.returncode==0 for c in children),"A fourth-lane supervisor failed")
  s.update(state="complete",finished_at_beijing=now());atomic_json(run/"fourth_lane_controller_status.json",s)
 except BaseException as exc:
  stop(children);s.update(state="failed",error=repr(exc),traceback=traceback.format_exc());atomic_json(run/"fourth_lane_controller_status.json",s);raise
 finally:owner.close()
if __name__=="__main__":main()

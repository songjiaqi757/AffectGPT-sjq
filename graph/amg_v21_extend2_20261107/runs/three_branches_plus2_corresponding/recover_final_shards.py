import sys,os,signal,time,subprocess,traceback
sys.path.insert(0,"/ai/sjq/AffectGPT-sjq/graph")
from amg_v21_extend2_20261107.common import *
from amg_v21_extend2_20261107.execute import all_inference
r=Path(read(G/"amg_v21_extend2_20261107/current_run.json")["path"])
owner=lock(r/"final_shard_recovery.lock");require(owner is not None,"Recovery already active")
def update(state,**kw):status(r,"final_shard_recovery",state=state,**kw)
def belongs(pid,mod):
 try:
  raw=Path(f"/proc/{pid}/cmdline").read_bytes()
  return mod.encode() in raw and str(r).encode() in raw
 except FileNotFoundError:return False
try:
 verify_code(r);require(len(list((r/"scores").glob("*.json")))==9,"Unexpected score count")
 n=read(r/"node_A800.json");a100=read(r/"node_A100.json")
 require(a100["phase"]=="inference","A100 unavailable")
 for slot in range(4):require(read(r/f"capacity_A100_{slot}.json")["passed"],"A100 capacity missing")
 require(all(read(f)["state"]=="complete" for f in (r/"training_jobs").glob("*.json")),"Training still active")
 remaining=[read(f) for f in (r/"shards").glob("*.json") if read(f)["state"]!="complete"]
 require(len(remaining)==3 and all(x["job_id"]=="from_40_epoch_42_MER2023" and x["node"]=="A800" for x in remaining),"Unexpected remaining work")
 update("releasing_A800_barrier",reason="Only three remaining shards; fourth A800 process has no task and cannot join four-model barrier",remaining_samples=sum(x["stop"]-x["start"] for x in remaining),old_controller=n["pid"],old_workers=n["worker_pids"])
 require(belongs(n["pid"],"amg_v21_extend2_20261107.rolling"),"Controller identity mismatch")
 for pid in n["worker_pids"].values():require(belongs(pid,"amg_v21_extend2_20261107.execute"),"Worker identity mismatch")
 os.kill(n["pid"],signal.SIGTERM)
 for pid in n["worker_pids"].values():
  try:os.killpg(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 deadline=time.monotonic()+60
 while any(belongs(pid,"amg_v21_extend2_20261107.execute") for pid in n["worker_pids"].values()):
  require(time.monotonic()<deadline,"A800 workers did not stop");time.sleep(1)
 reset=[]
 for item in remaining:
  f=r/"shards"/(item["id"]+".json");h=lock(f.with_suffix(".lock"))
  if h is None:continue
  try:
   x=read(f)
   if x["state"]=="running" and x.get("node")=="A800":
    x.update(state="pending",attempts=max(0,x["attempts"]-1),planned_handoff_to_ready_A100=True);write(f,x);reset.append(x["id"])
  finally:h.close()
 status(r,"node_A800",node="A800",phase="waiting_for_A100_remainder",completed_training=n["completed_training"],inference_workers_exited=True,remaining_inference_delegated_to_A100=True)
 update("A100_completing_remainder",released_shards=[x["id"] for x in remaining],reset_to_pending=reset,preserved_committed_predictions=True)
 deadline=time.monotonic()+1800
 while not all_inference(r):
  require(read(r/"node_A100.json").get("phase")!="failed","A100 controller failed")
  require(time.monotonic()<deadline,"A100 handoff timed out");time.sleep(5)
 update("restarting_A800_completion_controller")
 with (r/"logs/controller_A800.log").open("ab",buffering=0) as stream:
  child=subprocess.Popen([PYTHON,"-u","-B","-m","amg_v21_extend2_20261107.rolling","node","--run",str(r),"--node","A800"],cwd=G,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 write(r/"controller_A800_restarted_process.json",dict(pid=child.pid,at=now(),reason="All remaining inference transferred to capacity-validated A100; resume completion barrier"))
 update("handoff_complete",all_inference_complete=True,restarted_controller_pid=child.pid)
except BaseException as exc:
 update("failed",error=repr(exc),traceback=traceback.format_exc());raise
finally:owner.close()

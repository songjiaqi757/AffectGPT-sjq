"""Priority sixty inference barrier, single evaluator, then resume the original 225 queue."""
import argparse,os,signal,subprocess,time,traceback
from graph_paths import Path
from .common import ROOT,PYTHON,verify,read,sha,canonical,atomic_json,require,locked,counts,now
from .priority_score import phase_plan,inference_ready
from .fourth_lane import alive
from .controller import environment
def stop_inference_groups(run):
 stopped=[]
 for filename,module in [("fourth_lane_launch.json","amg_inference.fourth_lane"),("launch.json","amg_inference.controller")]:
  record=read(run/filename);pid=record["pid"]
  if not alive(pid):continue
  cmd=Path("/proc",str(pid),"cmdline").read_bytes().replace(b"\x00",b" ").decode()
  require(module in cmd and os.getpgid(pid)==pid,"Unexpected inference process group")
  os.killpg(pid,signal.SIGTERM);stopped.append(pid)
 deadline=time.monotonic()+60
 while any(alive(pid) for pid in stopped):
  require(time.monotonic()<deadline,"Inference supervisor did not stop");time.sleep(1)
 return stopped
def wait_gpu_free(gpu,timeout=300):
 deadline=time.monotonic()+timeout
 while True:
  result=subprocess.run(["nvidia-smi","--id="+str(gpu),"--query-gpu=memory.used","--format=csv,noheader,nounits"],capture_output=True,text=True,check=True)
  if int(result.stdout.strip())<1024:return
  require(time.monotonic()<deadline,"GPU still occupied after inference/evaluation exit");time.sleep(5)
def restore_jobs(run):
 reset=[]
 for f in (run/"jobs").glob("*.json"):
  handle=locked(f.with_suffix(".lock"))
  if handle is None:continue
  try:
   j=read(f)
   if j["state"]=="running" and not alive(j.get("pid",0)):
    j.update(state="pending",attempts=max(0,j.get("attempts",0)-1),intentional_preemptions=j.get("intentional_preemptions",0)+1,updated_at_beijing=now());atomic_json(f,j);reset.append(j["job_id"])
  finally:handle.close()
 return reset
def restart_inference(run,p):
 results=[]
 for module,logname,pointer in [("amg_inference.controller","controller.log","launch.json"),("amg_inference.fourth_lane","fourth_lane_controller.log","fourth_lane_launch.json")]:
  log=(run/logname).open("ab",buffering=0)
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",OPENBLAS_NUM_THREADS="1")
  proc=subprocess.Popen([str(PYTHON),"-u","-m",module,"--run",str(run)],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close()
  atomic_json(run/pointer,dict(pid=proc.pid,pgid=proc.pid,created_at_beijing=now(),plan_id=p["plan_id"],code_manifest_sha256=sha(run/"code_manifest.json"),reason="Resume after single-process priority evaluation"));results.append(proc.pid)
 return results
def main():
 a=argparse.ArgumentParser();a.add_argument("--phase",required=True);args=a.parse_args();phase=Path(args.phase).resolve();ph=phase_plan(phase);run=Path(ph["inference_run"]);p=verify(run)
 require(read(phase/"preflight.json")["passed"],"Priority/evaluation preflight has not passed")
 owner=locked(phase/"controller.lock");require(owner is not None,"Priority controller already active")
 status=dict(state="priority_inference",pid=os.getpid(),pgid=os.getpgrp(),phase_id=ph["phase_id"],inference_tasks=60,evaluation_processes=1,started_at_beijing=now());gpu_lock=None;child=None
 def update(**kw):status.update(kw,updated_at_beijing=now());atomic_json(phase/"status.json",status)
 try:
  update()
  while not inference_ready(run,ph):
   jobs=[read(run/"jobs"/(jid+".json")) for jid in ph["job_ids"]]
   require(not any(j["state"]=="failed" for j in jobs),"A priority inference task failed")
   update(counts={state:sum(j["state"]==state for j in jobs) for state in ["pending","running","complete","failed"]})
   restore_jobs(run);time.sleep(15)
  update(state="releasing_inference_gpu",counts={"complete":60})
  stopped=stop_inference_groups(run);wait_gpu_free(ph["evaluation_gpu"]);reset=restore_jobs(run)
  atomic_json(phase/"inference_to_scoring_transition.json",dict(stopped_inference_groups=stopped,reset_jobs=reset,training_untouched=True,time_beijing=now()))
  gpu_lock=locked(ROOT/"amg_finetune_nogc"/f"gpu_{ph['evaluation_gpu']}.lock");require(gpu_lock is not None,"Evaluation GPU lock is occupied")
  update(state="single_process_evaluation")
  log=(phase/"evaluation.log").open("ab",buffering=0)
  env=environment(ph["evaluation_gpu"]);env["VLLM_WORKER_MULTIPROC_METHOD"]="spawn"
  child=subprocess.Popen([str(PYTHON),"-u","-m","amg_inference.priority_score","--phase",str(phase)],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close()
  update(evaluator_pid=child.pid)
  while child.poll() is None:
   f=phase/"scoring_status.json"
   if f.exists():update(evaluation=read(f))
   time.sleep(15)
  require(child.returncode==0 and read(phase/"scoring_status.json")["state"]=="complete","Single-process evaluation failed; other inference remains paused")
  wait_gpu_free(ph["evaluation_gpu"]);gpu_lock.close();gpu_lock=None
  policy=read(run/"job_dispatch.json");require(policy["phase_id"]==ph["phase_id"],"Dispatch policy replaced during evaluation")
  policy.update(enabled=False,finished_at_beijing=now());atomic_json(run/"job_dispatch.json",policy);restore_jobs(run)
  resumed=restart_inference(run,p)
  update(state="complete",scores_completed=60,summary=str(phase/"per_checkpoint_summary.csv"),resumed_inference_controller_pids=resumed,finished_at_beijing=now())
 except BaseException as exc:
  update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:
  if gpu_lock is not None:gpu_lock.close()
  owner.close()
if __name__=="__main__":main()

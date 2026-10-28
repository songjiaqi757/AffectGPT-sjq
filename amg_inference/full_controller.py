"""Refresh live LPT dispatch, await all inference, then run exactly one scorer per GPU."""
import argparse,os,signal,subprocess,time,traceback
from pathlib import Path
from .common import ROOT,PYTHON,verify,read,sha,atomic_json,require,locked,now,counts
from .priority_score import phase_plan,resources
from .priority_controller import stop_inference_groups,wait_gpu_free
from .full_score import all_inference_complete,score_counts,summarize
from .controller import environment
def refresh_dispatch(run,ph,ip):
 rank=[];pending_costs=[]
 for jid in ph["job_ids"]:
  j=read(run/"jobs"/(jid+".json"))
  if j["state"]=="complete":remaining=0
  else:
   folder=run/"predictions"/jid
   n=sum(1 for f in os.scandir(folder) if f.is_file() and f.name.endswith(".json")) if folder.exists() else 0
   remaining=max(0,ip["datasets"][j["dataset"]]["samples"]-n)
  rank.append((remaining,jid))
  if j["state"]=="pending":pending_costs.append(remaining)
 rank.sort(key=lambda x:(-x[0],x[1]))
 policy=read(run/"job_dispatch.json")
 require(policy.get("phase_id")==ph["phase_id"],"Inference dispatch policy replaced")
 atomic_json(run/"job_dispatch.json",dict(enabled=True,plan_id=ip["plan_id"],phase_id=ph["phase_id"],strategy="largest_remaining_first",job_ids=[jid for _,jid in rank],updated_at_beijing=now(),all_225_jobs_allowed=True))
 return dict(pending_jobs=len(pending_costs),remaining_samples=sum(n for n,_ in rank),largest_remaining=rank[:12])
def launch_scorer(phase,gpu):
 log=(phase/f"gpu_{gpu}_evaluation.log").open("ab",buffering=0);env=environment(gpu);env["VLLM_WORKER_MULTIPROC_METHOD"]="spawn"
 child=subprocess.Popen([str(PYTHON),"-u","-m","amg_inference.full_score","--phase",str(phase),"--gpu",str(gpu)],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();return child
def main():
 a=argparse.ArgumentParser();a.add_argument("--phase",required=True);args=a.parse_args();phase=Path(args.phase).resolve();ph=phase_plan(phase);run=Path(ph["inference_run"]);ip=verify(run);resources(phase)
 require(read(phase/"preflight.json")["passed"],"Full evaluation preflight has not passed")
 owner=locked(phase/"controller.lock");require(owner is not None,"Full evaluation controller already active")
 s=dict(state="waiting_for_all_inference",pid=os.getpid(),pgid=os.getpgrp(),phase_id=ph["phase_id"],inference_tasks=225,evaluation_processes_per_gpu=1,reused_scores=60,started_at_beijing=now())
 children=[];gpu_locks=[]
 def update(**kw):s.update(kw,updated_at_beijing=now());atomic_json(phase/"status.json",s)
 try:
  update()
  while not all_inference_complete(run,ph):
   c=counts(run);require(c.get("failed",0)==0,"An inference job failed; scoring barrier remains closed")
   scheduling=refresh_dispatch(run,ph,ip);update(inference=c,scheduling=scheduling,evaluation=score_counts(phase));time.sleep(60)
  update(state="releasing_both_inference_gpus",inference={"complete":225})
  stopped=stop_inference_groups(run)
  for gpu in [0,1]:
   wait_gpu_free(gpu);handle=locked(ROOT/"amg_finetune_nogc"/f"gpu_{gpu}.lock")
   require(handle is not None,"GPU ownership lock is occupied");gpu_locks.append(handle)
  policy=read(run/"job_dispatch.json");policy.update(enabled=False,inference_finished_at_beijing=now());atomic_json(run/"job_dispatch.json",policy)
  atomic_json(phase/"evaluation_start_barrier.json",dict(passed=True,all_inference_complete=225,gpus_released=[0,1],stopped_inference_groups=stopped,time_beijing=now()))
  children=[launch_scorer(phase,gpu) for gpu in [0,1]];restarts=[0,0];update(state="dual_gpu_evaluation",evaluator_pids=[c.pid for c in children])
  while True:
   c=score_counts(phase);rows=summarize(phase,ph);update(evaluation=c,scores_written=len(rows),evaluator_pids=[p.pid for p in children],restarts=restarts)
   require(c.get("failed",0)==0,"A scoring job exhausted its retries")
   if c.get("complete",0)==225:
    break
   for gpu,proc in enumerate(children):
    if proc.poll() is not None:
     restarts[gpu]+=1;require(restarts[gpu]<=3,"Evaluator repeatedly failed")
     try:os.killpg(proc.pid,signal.SIGTERM)
     except ProcessLookupError:pass
     wait_gpu_free(gpu);children[gpu]=launch_scorer(phase,gpu)
   time.sleep(15)
  deadline=time.monotonic()+120
  for proc in children:
   proc.wait(timeout=max(1,deadline-time.monotonic()));require(proc.returncode==0,"Evaluator did not exit successfully")
  require(len(summarize(phase,ph))==225,"Final summary incomplete")
  update(state="complete",scores_completed=225,finished_at_beijing=now(),summary=str(phase/"per_checkpoint_summary.csv"))
 except BaseException as exc:
  for proc in children:
   if proc.poll() is None:
    try:os.killpg(proc.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:
  for handle in gpu_locks:handle.close()
  owner.close()
if __name__=="__main__":main()

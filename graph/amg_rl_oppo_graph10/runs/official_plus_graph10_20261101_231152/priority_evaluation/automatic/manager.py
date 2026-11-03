"""Sequential per-checkpoint evaluation policy for the existing server run."""
import sys,subprocess,time,traceback
from pathlib import Path
sys.path.insert(0,'/ai/sjq/AffectGPT-sjq/graph')
from amg_rl_oppo_graph10.common import *
RUN=Path(sys.argv[1]);AUTO=RUN/'priority_evaluation/automatic'
def main():
 owner=lock(AUTO/'manager.lock');require(owner is not None,'Automatic checkpoint evaluator already running')
 try:
  policy=read(AUTO/'policy.json');p=plan(RUN)
  for path,h in policy['source_sha256'].items():require(sha(path)==h,'Automatic evaluation source changed')
  for group in policy['batches']:
   targets=group['checkpoints'];folder=AUTO/'batches'/('_'.join(targets));folder.mkdir(parents=True,exist_ok=True)
   while True:
    jobs=[read(RUN/'jobs'/(cid+'_'+d+'.json')) for cid in targets for d in DATASETS]
    complete=sum(j['state']=='complete' for j in jobs)
    dump(AUTO/'status.json',dict(state='waiting_for_checkpoint_inference',checkpoints=targets,trigger_checkpoint=group['trigger_checkpoint'],datasets_complete=complete,datasets_total=len(jobs),pid=os.getpid(),time_beijing=now()))
    if complete==len(jobs):break
    time.sleep(15)
   dump(AUTO/'status.json',dict(state='evaluating_batch',checkpoints=targets,pid=os.getpid(),time_beijing=now()))
   with (folder/'batch.log').open('ab',buffering=0) as log:
    z=subprocess.Popen([PYTHON,'-u','-B',str(AUTO/'score_batch.py'),str(RUN),','.join(targets)],cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   require(z.wait()==0,'Batch evaluator process failed')
   require(all((RUN/'scores'/(cid+'_'+d+'.json')).exists() for cid in targets for d in DATASETS),'Batch scoring incomplete; see '+str(folder/'status.json'))
   batch=read(folder/'status.json');require(not batch['state'].startswith(('failed','resume_failed')),'Scoring or inference resume failed')
   dump(folder/'manager_verified.json',dict(passed=True,checkpoints=targets,plan_id=p['plan_id'],time_beijing=now()))
  dump(AUTO/'status.json',dict(state='complete',checkpoints=list(p['models']['rl']['checkpoints']),scores=108,pid=os.getpid(),time_beijing=now()))
 except BaseException as exc:
  dump(AUTO/'status.json',dict(state='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc(),pid=os.getpid(),time_beijing=now()));raise
 finally:owner.close()
if __name__=='__main__':main()

"""Pause only A100, score a completed checkpoint batch, and restore its workers."""
import sys,os,time,signal,subprocess,traceback,json
from pathlib import Path
sys.path.insert(0,'/ai/sjq/AffectGPT-sjq/graph')
from amg_rl_oppo_graph10.common import *
from amg_rl_oppo_graph10.execute import summarize
RUN=Path(sys.argv[1]);TARGETS=sys.argv[2].split(',');AUTO=RUN/'priority_evaluation'/'automatic';C=RUN/'multinode_control'
D=AUTO/'batches'/('_'.join(TARGETS));D.mkdir(parents=True,exist_ok=True)
def args(pid):
 try:return Path('/proc/'+str(pid)+'/cmdline').read_bytes().split(b'\0')
 except FileNotFoundError:return []
def alive(pid):
 if not args(pid):return False
 try:return Path('/proc/'+str(pid)+'/stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
def matches(pid,worker=False,slot=None):
 a=args(pid)
 try:
  ok=a[a.index(b'--run')+1]==str(RUN).encode()
  if worker:return ok and b'amg_rl_oppo_graph10.execute' in a and b'infer' in a and a[a.index(b'--role')+1]==b'rl' and a[a.index(b'--slot')+1]==str(slot).encode()
  return ok and str(C/'rl_multinode.py').encode() in a and a[a.index(b'--node')+1]==b'A100'
 except (ValueError,IndexError):return False
def memory():return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
def wait_free():
 deadline=time.monotonic()+180
 while memory()>512:require(time.monotonic()<deadline,'A100 memory not released');time.sleep(2)
def status(**kw):
 v=read(D/'status.json') if (D/'status.json').exists() else {}
 v.update(kw,checkpoints=TARGETS,pid=os.getpid(),time_beijing=now());dump(D/'status.json',v)
 dump(AUTO/'active_batch.json',dict(batch=str(D),**v))
def node_phase(phase):
 n=read(C/'A100.json');n.update(phase=phase,active_slots=[],workers=0,resume_workers=4,priority_checkpoints=TARGETS,time_beijing=now());dump(C/'A100.json',n)
def inference_complete():return all(read(f)['state']=='complete' for f in (RUN/'jobs').glob('rl*.json'))
def all_scored():return all((RUN/'scores'/(cid+'_'+d+'.json')).exists() for cid in read(RUN/'plan.json')['models']['rl']['checkpoints'] for d in DATASETS)
def reports(p):
 summaries=[]
 for cid in TARGETS:
  paths=[RUN/'scores'/(cid+'_'+d+'.json') for d in DATASETS]
  if not all(f.exists() for f in paths):continue
  rows=[read(f) for f in paths];require(all(r['checkpoint']==cid and r['plan_id']==p['plan_id'] for r in rows),'Wrong checkpoint score binding')
  mean=sum(r['main_score'] for r in rows)/9;epoch=p['models']['rl']['checkpoints'][cid]['epoch']
  lines=[f'# AffectGPT-RL checkpoint {epoch} + graph10','','All 12,799 samples; unchanged official scoring functions.','','|Dataset|Metric|Score (%)|','|---|---|---:|']
  lines+=['|'+r['dataset']+'|'+r['main_metric']+'|'+format(100*r['main_score'],'.2f')+'|' for r in rows]
  lines+=['|Mean||'+format(100*mean,'.2f')+'|','','No matched no-graph control has been evaluated.','']
  target=RUN/('CKPT%02d_RESULTS.md'%epoch);target.write_text('\n'.join(lines),encoding='utf-8')
  item=dict(checkpoint=cid,epoch=epoch,datasets=9,samples=12799,mean=mean,rows=rows,report=str(target),plan_id=p['plan_id'],completed_at_beijing=now())
  dump(AUTO/(cid+'_results.json'),item);summaries.append(item)
 if summaries:summarize(RUN,p)
 return summaries
def main():
 owner=lock(D/'batch.lock');require(owner is not None,'Batch already running')
 node_owner=None;score_owner=None;paused=False;scored=False;pids={}
 try:
  require(subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip()=='GPU-c011e801-690b-0cb9-63d8-184e68e2d39c','Wrong GPU')
  p=plan(RUN);policy=read(AUTO/'policy.json')
  for path,h in policy['source_sha256'].items():require(sha(path)==h,'Priority source changed')
  require(set(TARGETS)<=set(p['models']['rl']['checkpoints']),'Unknown checkpoint batch')
  while True:
   jobs=[read(RUN/'jobs'/(cid+'_'+d+'.json')) for cid in TARGETS for d in DATASETS]
   if all(j['state']=='complete' for j in jobs):break
   status(state='waiting_for_inference',datasets_complete=sum(j['state']=='complete' for j in jobs),datasets_total=len(jobs));time.sleep(15)
  if len(reports(p))==len(TARGETS):scored=True;status(state='complete_already_scored');return
  require(all(Path(j['official_npz']).exists() for j in jobs),'Official exports missing')
  status(state='pausing_A100_inference')
  n=read(C/'A100.json');controller=int(n['controller_pid']);pids={int(k):int(v) for k,v in n['pids'].items()}
  require(set(pids)==set(range(4,8)),'Unexpected A100 worker slots')
  active=any(alive(pid) and matches(pid,True,slot) for slot,pid in pids.items())
  if active:require(n['phase']=='inference' and matches(controller),'A100 coordinator unavailable')
  else:require(n['phase'] in ['waiting_for_incremental_scores','gpu_released','priority_evaluation_complete'],'Unexpected inactive A100 state')
  dump(D/'pause_snapshot.json',n)
  if alive(controller) and matches(controller):
   os.kill(controller,signal.SIGTERM);deadline=time.monotonic()+30
   while alive(controller):require(time.monotonic()<deadline,'Supervisor did not stop');time.sleep(.2)
  node_owner=lock(C/'A100.lock',True);paused=True;node_phase('priority_evaluation_releasing_gpu')
  for slot,pid in pids.items():
   if alive(pid) and matches(pid,True,slot):os.kill(pid,signal.SIGTERM)
  deadline=time.monotonic()+60
  while any(alive(pid) and matches(pid,True,slot) for slot,pid in pids.items()):
   require(time.monotonic()<deadline,'Workers did not stop');time.sleep(1)
  wait_free();node_phase('priority_evaluation');score_owner=lock(RUN/'score_rl.lock',True)
  for phase in ['ov','other']:
   for attempt in range(3):
    with (D/('score_'+phase+'.log')).open('ab',buffering=0) as log:
     z=subprocess.Popen([PYTHON,'-u','-B',str(AUTO/'score_checkpoints.py'),'--run',str(RUN),'--phase',phase,'--checkpoints',','.join(TARGETS)],cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    while z.poll() is None:
     ready=reports(p);status(state='scoring',scoring_phase=phase,scoring_pid=z.pid,attempt=attempt+1,reports_ready=[r['checkpoint'] for r in ready]);time.sleep(10)
    if z.returncode==0:break
    wait_free()
   require(z.returncode==0,'Official scoring failed: '+phase)
  ready=reports(p);require(len(ready)==len(TARGETS),'Missing checkpoint scores');scored=True
  status(state='scored',reports=[r['report'] for r in ready])
 except BaseException as exc:
  status(state='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc())
 finally:
  if score_owner is not None:score_owner.close()
  if paused:
   try:
    wait_free()
    if inference_complete():
     final=all_scored();node_phase('gpu_released' if final else 'waiting_for_incremental_scores')
     n=read(C/'A100.json');n.update(gpu_released=True,all_local_inference_workers_exited=True);dump(C/'A100.json',n)
     status(state='complete_all_inference_finished' if scored else 'failed_all_inference_finished')
    else:
     node_phase('priority_evaluation_complete')
     if node_owner is not None:node_owner.close();node_owner=None
     script=C/'rl_multinode.py';require(sha(script)==read(C/'topology.json')['source_sha256'],'Resume controller changed')
     with (C/'A100.log').open('ab',buffering=0) as log:
      z=subprocess.Popen([PYTHON,'-u','-B',str(script),'--run',str(RUN),'--node','A100'],cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
     status(state='complete_resuming_inference' if scored else 'failed_inference_resuming',resume_controller_pid=z.pid)
     deadline=time.monotonic()+900
     while time.monotonic()<deadline:
      n=read(C/'A100.json')
      if n.get('controller_pid')==z.pid and n.get('phase')=='failed':raise RuntimeError('A100 resume failed: '+str(n.get('error')))
      workers=[read(RUN/'workers'/('rl_'+str(slot)+'.json')) for slot in range(4,8)]
      if n.get('controller_pid')==z.pid and all(w.get('state')=='inference' and w.get('pid')!=pids[int(w['slot'])] for w in workers):
       status(state='complete_and_inference_resumed' if scored else 'failed_but_inference_resumed');break
      time.sleep(15)
   except BaseException as exc:
    status(state='resume_failed',scoring_completed=scored,error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc())
  if node_owner is not None:node_owner.close()
  owner.close()
if __name__=='__main__':main()

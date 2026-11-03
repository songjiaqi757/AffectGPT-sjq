"""Wait for checkpoint 10, score it on A100, resume the four A100 workers."""
import sys,os,time,signal,subprocess,traceback,datetime
from pathlib import Path
sys.path.insert(0,'/ai/sjq/AffectGPT-sjq/graph')
from amg_rl_oppo_graph10.common import *
from amg_rl_oppo_graph10.execute import finalize,summarize
RUN=Path(sys.argv[1]);D=RUN/'priority_evaluation'/'ckpt10';C=RUN/'multinode_control'
def args(pid):
 try:return Path('/proc/'+str(pid)+'/cmdline').read_bytes().split(b'\0')
 except FileNotFoundError:return []
def alive(pid):
 if not args(pid):return False
 try:return Path('/proc/'+str(pid)+'/stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
def matches(pid,worker=False,slot=None):
 a=args(pid)
 if not a:return False
 try:
  ok=a[a.index(b'--run')+1]==str(RUN).encode()
  if worker:ok=ok and b'amg_rl_oppo_graph10.execute' in a and b'infer' in a and a[a.index(b'--role')+1]==b'rl' and a[a.index(b'--slot')+1]==str(slot).encode()
  else:ok=ok and str(C/'rl_multinode.py').encode() in a and a[a.index(b'--node')+1]==b'A100'
  return ok
 except (ValueError,IndexError):return False
def memory():
 return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
def wait_free():
 deadline=time.monotonic()+180
 while memory()>512:
  require(time.monotonic()<deadline,'A100 GPU memory not released');time.sleep(2)
def status(**kw):
 value=read(D/'status.json') if (D/'status.json').exists() else {}
 value.update(kw,watcher_pid=os.getpid(),time_beijing=now());dump(D/'status.json',value)
def node_phase(phase):
 n=read(C/'A100.json');n.update(phase=phase,active_slots=[],workers=0,resume_workers=4,priority_checkpoint='rl_e010',time_beijing=now());dump(C/'A100.json',n)
def make_report(p):
 rows=[read(RUN/'scores'/('rl_e010_'+d+'.json')) for d in DATASETS]
 require(all(r['checkpoint']=='rl_e010' and r['plan_id']==p['plan_id'] for r in rows),'Score binding differs')
 mean=sum(r['main_score'] for r in rows)/9
 lines=['# AffectGPT-RL checkpoint 10 + graph10','', 'All 12,799 samples; official scoring functions, prior frozen Cue/Appraisal/10-emotion graph.','', '|Dataset|Metric|Score (%)|','|---|---|---:|']
 for r in rows:lines.append('|'+r['dataset']+'|'+r['main_metric']+'|'+format(100*r['main_score'],'.2f')+'|')
 lines+=['|Mean||'+format(100*mean,'.2f')+'|','', 'This is the graph-enhanced checkpoint-10 run. No matched no-graph control has been evaluated.','']
 (RUN/'CKPT10_RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
 dump(D/'results.json',dict(checkpoint='rl_e010',datasets=9,samples=12799,mean=mean,rows=rows,plan_id=p['plan_id'],completed_at_beijing=now()))
 summarize(RUN,p);return mean
def main():
 owner=lock(D/'watcher.lock');require(owner is not None,'Priority watcher already running')
 node_owner=None;score_owner=None;paused=False;scored=False;failure=None
 try:
  require(subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip()=='GPU-c011e801-690b-0cb9-63d8-184e68e2d39c','Priority scorer on wrong GPU')
  p=plan(RUN);request=read(D/'request.json')
  for path,h in request['source_sha256'].items():require(sha(path)==h,'Priority scoring source changed')
  status(state='waiting_for_ckpt10',checkpoint='rl_e010')
  while True:
   jobs=[read(RUN/'jobs'/('rl_e010_'+d+'.json')) for d in DATASETS]
   if all(j['state']=='complete' for j in jobs):break
   status(state='waiting_for_ckpt10',datasets_complete=sum(j['state']=='complete' for j in jobs))
   time.sleep(15)
  require(all(Path(j['official_npz']).exists() for j in jobs),'Official prediction export missing')
  status(state='pausing_A100_inference',inference_complete_at_beijing=now())
  n=read(C/'A100.json');controller=int(n['controller_pid']);pids={int(k):int(v) for k,v in n['pids'].items()}
  require(n['phase']=='inference' and matches(controller),'A100 coordinator is not in inference')
  require(set(pids)==set(range(4,8)),'Unexpected A100 slots')
  require(all(matches(pid,True,slot) for slot,pid in pids.items()),'A100 worker identity differs')
  dump(D/'pause_snapshot.json',n)
  os.kill(controller,signal.SIGTERM);deadline=time.monotonic()+30
  while alive(controller):
   require(time.monotonic()<deadline,'A100 supervisor did not exit');time.sleep(.2)
  node_owner=lock(C/'A100.lock',True);paused=True;node_phase('priority_evaluation_releasing_gpu')
  for slot,pid in pids.items():
   if alive(pid):
    require(matches(pid,True,slot),'Worker PID changed')
    os.kill(pid,signal.SIGTERM)
  deadline=time.monotonic()+60
  while any(alive(pid) for pid in pids.values()):
   require(time.monotonic()<deadline,'A100 workers did not exit');time.sleep(1)
  wait_free();node_phase('priority_evaluation');score_owner=lock(RUN/'score_rl.lock',True)
  status(state='scoring_ckpt10',a800_four_workers_continue=True)
  for phase in ['ov','other']:
   for attempt in range(3):
    with (D/('score_'+phase+'.log')).open('ab',buffering=0) as log:
     z=subprocess.Popen([PYTHON,'-u','-B',str(D/'score_checkpoint.py'),'--run',str(RUN),'--phase',phase],cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    while z.poll() is None:
     status(state='scoring_ckpt10',scoring_phase=phase,scoring_pid=z.pid,attempt=attempt+1);time.sleep(10)
    if z.returncode==0:break
    wait_free()
   require(z.returncode==0,'Official checkpoint-10 scorer failed: '+phase)
  mean=make_report(p);scored=True
  status(state='scored_resuming_A100',mean=mean,result=str(RUN/'CKPT10_RESULTS.md'))
 except BaseException as exc:
  failure=type(exc).__name__+': '+str(exc)
  status(state='failed',error=failure,traceback=traceback.format_exc())
 finally:
  if score_owner is not None:score_owner.close()
  if paused:
   try:
    wait_free();node_phase('priority_evaluation_complete' if scored else 'priority_evaluation_failed_resuming')
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
      status(state='complete_and_inference_resumed' if scored else 'failed_but_inference_resumed',resumed_workers=workers);break
     time.sleep(15)
   except BaseException as exc:
    status(state='resume_failed',error=type(exc).__name__+': '+str(exc),scoring_completed=scored,traceback=traceback.format_exc())
  if node_owner is not None:node_owner.close()
  owner.close()
if __name__=='__main__':main()

"""Bounded SSH queue endpoint; shares the existing flock/atomic prediction protocol."""
import sys,os,time,uuid,traceback,math
from pathlib import Path
sys.path.insert(0,'/ai/sjq/AffectGPT-sjq/graph')
from amg_rl_oppo_graph10.common import *
from amg_rl_oppo_graph10.execute import finalize
RUN=Path(__file__).resolve().parent.parent;C=RUN/'remote_qi'
def send(v):print(json.dumps(v,ensure_ascii=False,separators=(',',':')),flush=True)
def recv():
 line=sys.stdin.readline(4*1024*1024+1)
 if not line:return None
 require(len(line)<=4*1024*1024 and line.endswith('\n'),'Request too large or incomplete')
 return json.loads(line)
def main():
 require(os.environ.get('SSH_ORIGINAL_COMMAND')=='affectgpt-queue-v1','Only the fixed inference queue endpoint is authorized')
 p=plan(RUN);mp=p['models']['rl'];inv=read(RUN/'cache_inventory.json');cfg=read(C/'deployment.json')
 opening=recv()
 if opening and opening.get('op')=='supervisor_hello':
  require(opening['deployment_id']==cfg['deployment_id'] and opening['supervisor_sha256']==cfg['supervisor_sha256'],'Invalid Qi supervisor deployment')
  owner=lock(C/'supervisor_channel.lock');require(owner is not None,'Qi supervisor already connected')
  try:
   send(dict(type='supervisor_welcome',plan_id=p['plan_id']))
   while True:
    msg=recv()
    if msg is None:break
    require(msg.get('op')=='node_heartbeat','Only a node heartbeat is accepted on this channel')
    v=msg['status'];require(v['node']=='Qi' and v['deployment_id']==cfg['deployment_id'] and v['plan_id']==p['plan_id'],'Node identity changed')
    require(v['configured_workers']==7 and int(v['controller_pid'])==int(opening['pid']),'Node configuration changed')
    require(v['phase'] in ['inference','gpu_released','failed'],'Unsupported node phase')
    if v['phase']=='gpu_released':
     require(v.get('own_workers_exited') is True,'Qi workers still resident')
     require(all(read(RUN/'workers'/('rl_'+str(slot)+'.json'))['state']=='complete' for slot in range(8,15)),'Qi queue sessions incomplete')
    v.update(time_beijing=now(),broker_pid=os.getpid());dump(RUN/'multinode_control/Qi.json',v)
    send(dict(type='node_recorded'))
  finally:owner.close()
  return
 require(opening and opening.get('op')=='hello','Hello required')
 require(opening['deployment_id']==cfg['deployment_id'],'Wrong remote deployment')
 slot=int(opening['slot']);require(8<=slot<=14,'Invalid Qi slot')
 require(int(opening['gpu'])==(0 if slot<=10 else 1),'Wrong slot GPU')
 owner=lock(C/('slot_'+str(slot)+'.lock'));require(owner is not None,'Qi slot already connected')
 expected=mp['contract'];runtime=opening['runtime'];remote_pid=int(opening['pid'])
 require(runtime['dtype']=='bfloat16' and runtime['quantized'] is False,'Inference precision changed')
 require(opening['code_sha256']==cfg['worker_code_sha256'],'Qi worker code changed')
 require(runtime['bootstrap_sha256']==cfg['bootstrap_sha256'],'Qi relocation adapter changed')
 active=None;held=None;lease=None;done=0;rows_by_name={};rowcache={}
 fs=[f for f in (RUN/'shards').glob('rl*.json') if int(read(f)['checkpoint'][4:])>=40]
 specs={str(f):read(f) for f in fs}
 fs.sort(key=lambda f:(mp['checkpoints'][specs[str(f)]['checkpoint']]['epoch'],-mp['datasets'][specs[str(f)]['dataset']]['samples'],specs[str(f)]['start']))
 finished=set()
 def status(state,**kw):
  dump(RUN/'workers'/('rl_'+str(slot)+'.json'),dict(state=state,role='rl',node='Qi',slot=slot,pid=remote_pid,broker_pid=os.getpid(),gpu=int(opening['gpu']),gpu_uuid=runtime['gpu_uuid'],checkpoint=active['checkpoint'] if active else None,dataset=active['dataset'] if active else None,shard=active['id'] if active else None,completed_samples=done,plan_id=p['plan_id'],deployment_id=cfg['deployment_id'],time_beijing=now(),**kw))
 def release(reason=None):
  nonlocal active,held,lease,rows_by_name
  if held is not None:
   if active is not None:
    path=RUN/'shards'/(active['id']+'.json');s=read(path)
    if s.get('remote_lease')==lease and s['state']!='complete':
     s.update(state='pending',error=reason or 'Qi connection closed before shard finish');dump(path,s)
   held.close()
  active=None;held=None;lease=None;rows_by_name={}
 status('ready');send(dict(type='welcome',plan_id=p['plan_id'],deployment_id=cfg['deployment_id'],broker_pid=os.getpid()))
 try:
  while True:
   msg=recv()
   if msg is None:break
   op=msg.get('op')
   if op=='ping':send(dict(type='pong',plan_id=p['plan_id']));continue
   if op=='claim':
    require(active is None,'Previous shard not finished');task=None
    for f in fs:
     if str(f) in finished:continue
     s=read(f)
     if s['state']=='complete':finished.add(str(f));continue
     h=lock(f.with_suffix('.lock'))
     if h is None:continue
     s=read(f)
     if s['state']=='complete':h.close();finished.add(str(f));continue
     if s['attempts']>=3:h.close();raise RuntimeError('Repeated shard failure: '+s['id'])
     active=s;held=h;lease=uuid.uuid4().hex
     s.update(state='running',attempts=s['attempts']+1,pid=os.getpid(),slot=slot,node='Qi',remote_pid=remote_pid,remote_lease=lease);dump(f,s)
     d=s['dataset']
     if d not in rowcache:
      spec=mp['datasets'][d];require(sha(spec['path'])==spec['sha256'],'Input changed');rowcache[d]=read(spec['path'])
     allrows=rowcache[d][s['start']:s['stop']];rows_by_name={r['name']:r for r in allrows};todo=[]
     for row in allrows:
      dest=RUN/'predictions'/s['job_id']/(canonical(row['name'])+'.json')
      if dest.exists():require(read(dest)['plan_id']==p['plan_id'],'Wrong existing prediction')
      else:todo.append(row)
     task=dict(type='task',shard=s,lease=lease,rows=todo,checkpoint=mp['checkpoints'][s['checkpoint']],plan_id=p['plan_id'])
     status('inference');break
    if task is not None:send(task)
    else:
     jobs=[read(f) for f in (RUN/'jobs').glob('rl*.json')]
     complete=all(j['state']=='complete' for j in jobs)
     if not complete:
      for j in jobs:
       if j['state']!='complete':finalize(RUN,p,j['id'])
      complete=all(read(RUN/'jobs'/(j['id']+'.json'))['state']=='complete' for j in jobs)
     status('complete' if complete else 'idle');send(dict(type='complete' if complete else 'idle',retry_seconds=10))
    continue
   if op=='commit':
    require(active is not None and msg.get('lease')==lease,'Wrong commit lease')
    v=msg['record'];name=v['name'];require(name in rows_by_name,'Sample outside claimed shard');row=rows_by_name[name]
    require(v['sample_id']==row['sample_id'] and v['subtitle']==row['subtitle'],'Input identity changed')
    require(v['dataset']==active['dataset'] and v['checkpoint']==active['checkpoint'],'Checkpoint/dataset changed')
    require(v['plan_id']==p['plan_id'] and isinstance(v['response'],str),'Invalid output')
    require(v['graph_cache_id']==inv[row['sample_id']]['cache_id'],'Graph cache identity changed')
    require(v['prompt_info']['contract']==expected,'Official inference contract changed')
    require(isinstance(v['elapsed_seconds'],(float,int)) and math.isfinite(v['elapsed_seconds']) and v['elapsed_seconds']>=0,'Invalid elapsed time')
    dest=RUN/'predictions'/active['job_id']/(canonical(name)+'.json')
    if dest.exists():
     old=read(dest);require(old['plan_id']==p['plan_id'] and old['checkpoint']==active['checkpoint'],'Existing prediction mismatch')
     send(dict(type='committed',name=name,already_existed=True));continue
    v.update(role='rl',slot=slot,node='Qi',gpu=int(opening['gpu']),runtime=runtime,deployment_id=cfg['deployment_id'],received_at_beijing=now())
    dump(dest,v);done+=1;status('inference',last_sample=row['sample_id'],last_seconds=v['elapsed_seconds']);send(dict(type='committed',name=name,already_existed=False));continue
   if op=='finish':
    require(active is not None and msg.get('lease')==lease,'Wrong finish lease')
    for name in rows_by_name:
     v=read(RUN/'predictions'/active['job_id']/(canonical(name)+'.json'));require(v['plan_id']==p['plan_id'] and v['checkpoint']==active['checkpoint'],'Missing or incorrect shard prediction')
    active.update(state='complete',finished_at_beijing=now());dump(RUN/'shards'/(active['id']+'.json'),active)
    jid=active['job_id'];finished.add(str(RUN/'shards'/(active['id']+'.json')));release();finalize(RUN,p,jid);status('ready');send(dict(type='finished',job_id=jid));continue
   if op=='close':send(dict(type='bye'));break
   raise RuntimeError('Unsupported queue operation')
 finally:
  incomplete=active is not None;release('Qi session disconnected; committed samples preserved')
  if incomplete:status('disconnected')
  owner.close()
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  try:send(dict(type='error',error=type(exc).__name__+': '+str(exc)))
  except Exception:pass
  traceback.print_exc(file=sys.stderr);sys.exit(1)

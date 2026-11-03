"""Operational multi-node controller. Inference sources and plan_id stay unchanged."""
import argparse,os,sys,time,signal,subprocess,traceback
from pathlib import Path
sys.path.insert(0,'/ai/sjq/AffectGPT-sjq/graph')
from amg_rl_oppo_graph10.common import *
from amg_rl_oppo_graph10.execute import finalize,summarize
EXPECTED={'A800':'GPU-be2112e9-43e2-43e7-da85-ff9198a7c875','A100':'GPU-c011e801-690b-0cb9-63d8-184e68e2d39c'}
SLOTS={'A800':list(range(4)),'A100':list(range(4,8))}
def arguments(pid):
 try:return Path('/proc/'+str(pid)+'/cmdline').read_bytes().split(b'\0')
 except FileNotFoundError:return []
def alive(pid,run,slot=None,mode='infer'):
 a=arguments(pid)
 if not a:return False
 try:
  state=Path('/proc/'+str(pid)+'/stat').read_text().split()[2]
  if state=='Z':return False
  valid=b'amg_rl_oppo_graph10.execute' in a and mode.encode() in a and a[a.index(b'--role')+1]==b'rl' and a[a.index(b'--run')+1]==str(run).encode()
  if slot is not None:valid=valid and a[a.index(b'--slot')+1]==str(slot).encode()
  return valid
 except (FileNotFoundError,ValueError,IndexError):return False
def free_mib():
 return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
def main():
 a=argparse.ArgumentParser();a.add_argument('--run',required=True);a.add_argument('--node',choices=list(SLOTS),required=True);x=a.parse_args()
 run=Path(x.run);node=x.node;c=run/'multinode_control';p=plan(run)
 require(read(c/'cross_node_lock_test.json')['passed'],'Cross-node lock not verified')
 require(sha(__file__)==read(c/'topology.json')['source_sha256'],'Controller source changed')
 require(subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip()==EXPECTED[node],'Wrong physical GPU')
 owner=lock(c/(node+'.lock'));require(owner is not None,'Node controller already running')
 pipeline_owner=None;children={};pids={};retries={slot:0 for slot in SLOTS[node]}
 state=dict(node=node,controller_pid=os.getpid(),slots=SLOTS[node],gpu_uuid=EXPECTED[node],plan_id=p['plan_id'],controller_sha256=sha(__file__),started_at_beijing=now())
 def update(**kw):
  state.update(kw,pids={str(k):v for k,v in pids.items()},time_beijing=now())
  dump(c/(node+'.json'),state)
  if node=='A800' and pipeline_owner is not None:
   nodes={n:read(c/(n+'.json')) for n in SLOTS if (c/(n+'.json')).exists()}
   dump(run/'pipeline_rl.json',dict(role='rl',pid=os.getpid(),controller='multinode_v1',workers=8,phase=state.get('phase','inference'),pids={str(k):v for k,v in pids.items()},nodes=nodes,time_beijing=now()))
 def spawn(slot,mode='infer'):
  with (run/'logs'/('rl_'+mode+'_'+str(slot)+'.log')).open('ab',buffering=0) as log:
   z=subprocess.Popen([PYTHON,'-u','-B','-m','amg_rl_oppo_graph10.execute',mode,'--run',str(run),'--role','rl','--slot',str(slot)],cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  children[slot]=z;return z.pid
 try:
  if node=='A800':
   previous=read(run/'pipeline_rl.json')
   if previous.get('controller')!='multinode_v1':
    oldpid=int(previous['pid'])
    require(previous['phase']=='inference' and alive(oldpid,run,mode='pipeline'),'Legacy coordinator not in inference')
    require(len(previous['pids'])==4,'Expected four existing A800 workers')
    pids={int(k):int(v) for k,v in previous['pids'].items()}
    require(all(alive(pid,run,slot) for slot,pid in pids.items()),'Existing A800 worker not alive')
    dump(c/'previous_single_node_pipeline.json',previous)
    os.kill(oldpid,signal.SIGTERM)
    deadline=time.monotonic()+20
    while alive(oldpid,run,mode='pipeline'):
     require(time.monotonic()<deadline,'Legacy coordinator did not exit');time.sleep(.2)
   elif (c/'A800.json').exists():
    pids={int(k):int(v) for k,v in read(c/'A800.json')['pids'].items()}
   pipeline_owner=lock(run/'pipeline_rl.lock',True)
  elif (c/'A100.json').exists():
   prior=read(c/'A100.json')
   if prior.get('phase')=='gpu_released':
    require(all(read(f)['state']=='complete' for f in (run/'shards').glob('rl*.json')),'Released node with unfinished queue')
    return
   pids={int(k):int(v) for k,v in prior.get('pids',{}).items()}
  if node=='A100' and not any(alive(pid,run,slot) for slot,pid in pids.items()):
   require(free_mib()<512,'A100 is occupied')
  for slot in SLOTS[node]:
   if slot not in pids or not alive(pids[slot],run,slot):pids[slot]=spawn(slot)
  update(phase='inference',workers=4,adopted_existing_workers=(node=='A800'))
  active=set(SLOTS[node])
  while active:
   for slot in list(active):
    if slot in children:children[slot].poll()
    if alive(pids[slot],run,slot):continue
    f=run/'workers'/('rl_'+str(slot)+'.json');w=read(f) if f.exists() else {}
    if w.get('pid')==pids[slot] and w.get('state')=='complete':
     active.remove(slot);continue
    retries[slot]+=1;require(retries[slot]<=2,'Worker failed repeatedly: '+str(slot)+' '+str(w.get('error')))
    time.sleep(3);pids[slot]=spawn(slot)
   update(phase='inference',workers=4,active_slots=sorted(active),retries=retries)
   if active:time.sleep(10)
  update(phase='releasing_gpu',all_local_inference_workers_exited=True)
  deadline=time.monotonic()+180
  while free_mib()>512:
   require(time.monotonic()<deadline,'GPU memory not released');time.sleep(3)
  update(phase='gpu_released',all_local_inference_workers_exited=True,gpu_released=True)
  if node=='A100':return
  while True:
   other=read(c/'A100.json') if (c/'A100.json').exists() else {}
   require(other.get('phase')!='failed','A100 controller failed')
   if other.get('phase')=='gpu_released' and other.get('plan_id')==p['plan_id']:break
   update(phase='waiting_for_A100_release');time.sleep(10)
  for f in (run/'jobs').glob('rl*.json'):finalize(run,p,f.stem)
  jobs=[read(f) for f in (run/'jobs').glob('rl*.json')]
  require(len(jobs)==108 and all(j['state']=='complete' for j in jobs),'Global inference jobs incomplete')
  dump(c/'global_inference_barrier.json',dict(passed=True,inference_jobs=108,workers=8,nodes=list(SLOTS),both_gpus_released=True,all_eight_inference_workers_exited=True,plan_id=p['plan_id'],time_beijing=now()))
  update(phase='evaluation',global_inference_barrier_passed=True)
  for attempt in range(3):
   pid=spawn(0,'score');z=children[0]
   while z.poll() is None:summarize(run,p);time.sleep(15)
   summarize(run,p)
   if z.returncode==0:break
   time.sleep(5)
  require(z.returncode==0,'Official RL evaluation failed')
  update(phase='complete',results=str(run/'per_checkpoint_summary.csv'))
 except BaseException as exc:
  update(phase='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc())
  raise
 finally:
  if pipeline_owner is not None:pipeline_owner.close()
  owner.close()
if __name__=='__main__':main()

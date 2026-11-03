"""Four inference workers per physical GPU, dynamic whole-sample queue."""
import os,sys,time,copy,argparse,traceback,subprocess,signal
from pathlib import Path
ROOT=Path('/ai/sjq/AffectGPT-sjq');sys.path.insert(0,str(ROOT))
from amg_method_decision.pipeline import read,dump,canonical,sha,now,key,locked,environment,PYTHON
from amg_188_audit.policy import make_prompt
def verify(run):
 p=read(run/'inference_plan.json')
 if canonical({k:v for k,v in p.items() if k!='plan_id'})!=p['plan_id']:raise ValueError('Plan changed')
 for f,h in p['input_files'].items():
  if sha(f)!=h:raise ValueError('Input changed: '+f)
 return p
def worker(run,part,slot):
 node=['A800','A100'][slot//4];p=verify(run);dest=run/'workers'/f'gen_{part}_{slot}.json';state=dict(slot=slot,node=node,pid=os.getpid(),state='loading',completed_samples=0,generated=0,reused=0)
 def update(**kw):state.update(kw,time_beijing=now());dump(dest,state)
 try:
  update();import torch
  import amg_inference.model as original
  original.make_prompt=make_prompt;cfg=copy.deepcopy(p);cfg['variant']='A'
  with locked(run/f'model_loading_{node}.lock',blocking=True):model=original.Predictor(cfg)
  rr=read(run/'data'/f'{part}_records.json')
  for ck,spec in p['checkpoints'].items():
   with locked(run/f'model_loading_{node}.lock',blocking=True):model.load(spec)
   update(state='loaded_ready',checkpoint=ck)
   ready=run/'workers'/f'{part}_ready_{node}_{ck}_{slot}.json';dump(ready,dict(slot=slot,checkpoint=ck,loaded=True))
   while not all((run/'workers'/f'{part}_ready_{node}_{ck}_{s}.json').exists() for s in range(slot//4*4,slot//4*4+4)):
    if (run/'failure.json').exists():raise RuntimeError('Peer failure')
    time.sleep(2)
   if part=='development' and ck==next(iter(p['checkpoints'])):
    if node=='A100':
     update(state='full_window_capacity_probe')
     source=ROOT/'amg_188_path_noemotion/runs/path_noemotion_20261028_170538';oldstop=model.chat.stopping_criteria
     try:_,info=model.predict(read(source/'train_records.json')[0],read(source/'source_probe_bundle.json'),42+slot%4,stress=True)
     finally:model.chat.stopping_criteria=oldstop
     if not (1530<=info['stress_prompt_tokens']<=1536 and info['stress_generated_tokens']==1200):raise RuntimeError('Full-window capacity probe failed')
     dump(run/'workers'/f'capacity_A100_{slot}.json',dict(passed=True,slot=slot,info=info,gpu_uuid=p['physical_nodes'][1]['gpu_uuid'],peak_allocated_bytes=int(torch.cuda.max_memory_allocated()),plan_id=p['plan_id'],time_beijing=now()))
     while not all((run/'workers'/f'capacity_A100_{s}.json').exists() for s in range(4,8)):
      if (run/'failure.json').exists():raise RuntimeError('Peer capacity failure')
      time.sleep(2)
     dump(run/'capacity_accepted_A100.json',dict(passed=True,workers=4,gpu_uuid=p['physical_nodes'][1]['gpu_uuid'],plan_id=p['plan_id'],time_beijing=now()))
    while not (run/'capacity_accepted_A100.json').exists():
     if (run/'failure.json').exists():raise RuntimeError('Peer capacity failure')
     time.sleep(2)
   folder=run/'predictions'/part/ck
   while True:
    pending=False;worked=False
    for row in rr:
     out=folder/(key(row)+'.json')
     if out.exists():continue
     if ck!=next(iter(p['checkpoints'])):
      owner=read(run/'predictions'/part/next(iter(p['checkpoints']))/(key(row)+'.json'))['hardware_node']
      if owner!=node:continue
     pending=True;lock=locked(folder/(key(row)+'.lock'))
     if lock is None:continue
     try:
      if out.exists():continue
      worked=True;b=read(run/'prompt_cache'/(key(row)+'.json'))
      if b['bundle_id']!=canonical({k:v for k,v in b.items() if k!='bundle_id'}):raise ValueError('Prompt bundle changed')
      answers=[];cache={}
      for seed in p['seeds']:
       for arm in p['conditions']:
        update(state='inference',checkpoint=ck,sample_id=row['sample_id'],seed=seed,arm=arm)
        cfg['variant']=arm
        gkey=canonical(dict(plan_id=p['plan_id'],checkpoint=spec['sha256'],sample_id=row['sample_id'],text=b['texts'][arm],seed=seed,media_input=canonical({k:row[k] for k in ['audio_path','face_path','subtitle']})))
        f=run/'generation_cache'/(gkey+'.json')
        if (seed,b['texts'][arm]) in cache:
         value=copy.deepcopy(cache[seed,b['texts'][arm]]);value['reused_identical_prompt']=True;state['reused']+=1
        elif f.exists():
         value=read(f)
         if value['generation_key']!=gkey:raise ValueError('Stale cache')
         state['reused']+=1
        else:
         response,info=model.predict(row,b,seed)
         value=dict(response=response,prompt_info=info,generation_key=gkey,checkpoint_sha256=spec['sha256'],seed=seed,hardware_node=node,slot=slot,reused_identical_prompt=False)
         dump(f,value);state['generated']+=1
        cache[seed,b['texts'][arm]]=copy.deepcopy(value)
        value.update(condition=arm,seed=seed);answers.append(value)
      dump(out,dict(plan_id=p['plan_id'],sample_id=row['sample_id'],name=row['name'],family=row['family'],partition=part,checkpoint=ck,hardware_node=node,slot=slot,answers=answers,created_at_beijing=now()))
      state['completed_samples']+=1;update()
     finally:lock.close()
    if not pending or all((folder/(key(r)+'.json')).exists() for r in rr):break
    if (run/'failure.json').exists():raise RuntimeError('Peer failure')
    if not worked:time.sleep(3)
  update(state='complete')
 except BaseException as e:
  update(state='failed',error=repr(e),traceback=traceback.format_exc());dump(run/'failure.json',dict(phase='generation',node=node,slot=slot,partition=part,error=repr(e),traceback=traceback.format_exc(),time_beijing=now()));raise
def node(run,part,index):
 def stop(*unused):raise KeyboardInterrupt('Experiment controller interrupted')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 node=['A800','A100'][index];p=verify(run);procs=[];state=run/f'gen_node_{part}_{node}.json'
 try:
  snap=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.used','--format=csv,noheader,nounits'],text=True).strip().split(',')
  if snap[0].strip()!=p['physical_nodes'][index]['gpu_uuid']:raise ValueError('Wrong GPU')
  if int(snap[1].strip())>256:raise RuntimeError('GPU not released before generation')
  for ck in p['checkpoints']:
   for slot in range(index*4,index*4+4):(run/'workers'/f'{part}_ready_{node}_{ck}_{slot}.json').unlink(missing_ok=True)
  (run/'generation_cache').mkdir(exist_ok=True)
  for slot in range(index*4,index*4+4):
   f=(run/f'gen_{part}_{slot}.log').open('ab',buffering=0)
   z=subprocess.Popen([PYTHON,'-u','-B','-m','amg_method_decision.generate','worker','--run',str(run),'--part',part,'--slot',str(slot)],cwd=ROOT,env=environment(0),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);f.close();procs.append(z)
  deadline=time.monotonic()+172800
  while any(z.poll() is None for z in procs):
   if any(z.poll() not in [None,0] for z in procs) or (run/'failure.json').exists():raise RuntimeError('Generation worker failed')
   if time.monotonic()>deadline:raise TimeoutError('Generation budget exceeded')
   dump(state,dict(state='running',node=node,partition=part,pids=[z.pid for z in procs],time_beijing=now()));time.sleep(8)
  if any(z.returncode for z in procs):raise RuntimeError('Generation worker exit failure')
  dump(state,dict(state='complete',node=node,partition=part,time_beijing=now()))
 except BaseException as e:
  dump(state,dict(state='failed',node=node,error=repr(e),traceback=traceback.format_exc(),time_beijing=now()));dump(run/'failure.json',read(state))
  for z in procs:
   if z.poll() is None:
    try:os.killpg(z.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode');a.add_argument('--run',required=True);a.add_argument('--part',default='development');a.add_argument('--slot',type=int);a.add_argument('--index',type=int);x=a.parse_args()
 if x.mode=='worker':worker(Path(x.run),x.part,x.slot)
 elif x.mode=='node':node(Path(x.run),x.part,x.index)

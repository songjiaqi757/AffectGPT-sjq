"""A800-only four-worker inference, resumable exact exports, then automatic official scoring."""
import argparse,collections,csv,io,math,os,signal,subprocess,sys,time,traceback,zipfile
from .common import *

def verify(run):
 p=plan(run);code=read(Path(run)/'code_manifest.json')
 for f,h in code['files'].items():assert sha(f)==h,'Frozen runtime changed: '+f
 assert sha(Path(run)/'cache_inventory.json')==p['cache_inventory_sha256'];return p

def finalized(run,p,jid):
 h=lock(run/'jobs'/(jid+'.lock'))
 if h is None:return
 try:
  f=run/'jobs'/(jid+'.json');j=read(f)
  if j['state']=='complete':return
  if not all(read(run/'shards'/(s+'.json'))['state']=='complete' for s in j['shards']):return
  rows=read(p['datasets'][j['dataset']]['path']);folder=run/'predictions'/jid;names={};tmp=folder/'predictions.jsonl.tmp'
  with tmp.open('w') as stream:
   for row in rows:
    x=read(folder/(key(row['sample_id'])+'.json'));assert x['plan_id']==p['plan_id'] and x['checkpoint']['sha256']==p['checkpoints'][str(j['epoch'])]['sha256'];assert x['name']==row['name'];assert row['name'] not in names;names[row['name']]=x['response'];stream.write(json.dumps(x,ensure_ascii=False)+'\n')
  tmp.replace(folder/'predictions.jsonl')
  import numpy as np
  tmp=folder/'name2reason.npz.tmp'
  with tmp.open('wb') as stream:np.savez_compressed(stream,name2reason=names)
  tmp.replace(folder/'name2reason.npz');j.update(state='complete',finished_at=now(),official_npz=str(folder/'name2reason.npz'),prediction_path=str(folder/'predictions.jsonl'),prediction_sha256=sha(folder/'predictions.jsonl'));write(f,j)
 finally:h.close()

def infer(run,slot,node):
 p=verify(run);inv=read(run/'cache_inventory.json');statusfile=run/'workers'/f'{node}_{slot}.json';state=dict(node=node,slot=slot,pid=os.getpid(),completed_samples=0)
 def update(**kw):state.update(kw,updated_at=now());write(statusfile,state)
 try:
  from .model import Predictor
  import torch
  update(state='loading')
  with lock(run/(node+'_model_loading.lock'),True):model=Predictor(p);model.load(p['checkpoints']['30'])
  update(state='ready')
  files=[f for i,f in enumerate(sorted((run/'shards').glob('*.json'))) if i%2==p['nodes'].index(node)];rows_by_dataset={d:read(s['path']) for d,s in p['datasets'].items()}
  while True:
   def priority(f):
    s=read(f);return (0 if p['checkpoints'][str(s['epoch'])]['sha256']==model.loaded else 1,s['epoch'],-p['datasets'][s['dataset']]['samples'],s['start'])
   claimed=None
   for f in sorted(files,key=priority):
    meta=read(f)
    if meta['state']=='complete':continue
    if meta['state']=='failed':raise RuntimeError('A shard exhausted retries: '+f.name)
    h=lock(f.with_suffix('.lock'))
    if h is None:continue
    s=read(f)
    if s['state']=='complete':h.close();continue
    assert s['attempts']<3,'Shard retry budget exhausted';claimed=(f,h,s);break
   if claimed is None:
    if all(read(f)['state']=='complete' for f in files):break
    update(state='waiting_for_inflight_shards');time.sleep(2);continue
   f,h,s=claimed
   try:
    s.update(state='running',attempts=s['attempts']+1,pid=os.getpid(),slot=slot);write(f,s);spec=p['checkpoints'][str(s['epoch'])]
    if model.loaded!=spec['sha256']:
     update(state='switching_checkpoint',epoch=s['epoch'])
     with lock(run/(node+'_model_loading.lock'),True):model.load(spec)
    update(state='inference',epoch=s['epoch'],dataset=s['dataset'],shard=s['id']);folder=run/'predictions'/s['job_id'];folder.mkdir(parents=True,exist_ok=True)
    for row in rows_by_dataset[s['dataset']][s['start']:s['stop']]:
     dest=folder/(key(row['sample_id'])+'.json');binding=digest([p['plan_id'],spec['sha256'],p['datasets'][s['dataset']]['sha256'],inv[row['sample_id']]['cache_id']])
     if dest.exists():assert read(dest)['binding']==binding,'Stale prediction binding'
     else:
      entry=inv[row['sample_id']];assert sha(entry['path'])==entry['sha256'];b=read(entry['path']);assert b['cache_id']==entry['cache_id'] and b['row_sha256']==digest(row);seed=None;started=time.monotonic();response,info=model.predict(row,b,seed);assert isinstance(response,str)
      write(dest,dict(sample_id=row['sample_id'],name=row['name'],dataset=s['dataset'],epoch=s['epoch'],response=response,generation_empty=not response.strip(),checkpoint=spec,binding=binding,plan_id=p['plan_id'],cache_id=b['cache_id'],graph_release_id=p['graph_release_id'],prompt_release_id=p['prompt_release_id'],prompt_info=info,seed=seed,slot=slot,node=node,elapsed_seconds=time.monotonic()-started,created_at=now()));state['completed_samples']+=1;update(last_sample_id=row['sample_id'],last_seconds=time.monotonic()-started)
    s.update(state='complete',finished_at=now());write(f,s)
   except BaseException as exc:s.update(state='pending' if s['attempts']<3 else 'failed',error=repr(exc),traceback=traceback.format_exc());write(f,s);raise
   finally:h.close()
  update(state='complete')
 except BaseException as exc:update(state='failed',error=repr(exc),traceback=traceback.format_exc());raise

def summarize(run,p):
 rows=[read(f) for f in (run/'scores').glob('*.json')];fields=['epoch','dataset','samples','main_metric','main_score','HIT','WAF','ACC','F_s','P_s','R_s'];stream=io.StringIO();w=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for row in sorted(rows,key=lambda x:(x['epoch'],x['dataset'])):w.writerow(dict(row,**row['metrics']))
 tmp=run/'metrics_all.csv.tmp';tmp.write_text(stream.getvalue());tmp.replace(run/'metrics_all.csv');summary=[]
 for epoch in p['checkpoints']:
  matches=[x for x in rows if x['epoch']==int(epoch)];entry=dict(epoch=int(epoch),datasets_completed=len(matches))
  for x in matches:
   for k,v in x['metrics'].items():entry[x['dataset']+'_'+k]=v
  summary.append(entry)
 write(run/'per_checkpoint_summary.json',summary);stream=io.StringIO();w=csv.DictWriter(stream,fieldnames=['epoch','datasets_completed','MER2023_HIT','SIMS_WAF','SIMS_ACC','OVMERDPlus_F_s','OVMERDPlus_P_s','OVMERDPlus_R_s']);w.writeheader();w.writerows(summary);tmp=run/'per_checkpoint_summary.csv.tmp';tmp.write_text(stream.getvalue());tmp.replace(run/'per_checkpoint_summary.csv')
 if len(rows)==21:
  lines=['# Seven original checkpoints + Student OOF AMG graph + unified P4','', 'Official repository evaluation. Values below are percentages. No target-based prompt tuning or checkpoint mixing.','', '|Epoch|MER2023 HIT|SIMS WAF|SIMS ACC|OVMERDPlus F_s|P_s|R_s|','|---:|---:|---:|---:|---:|---:|---:|']
  for r in summary:lines.append('|'+str(r['epoch'])+'|'+'|'.join(f'{100*r[k]:.2f}' for k in ['MER2023_HIT','SIMS_WAF','SIMS_ACC','OVMERDPlus_F_s','OVMERDPlus_P_s','OVMERDPlus_R_s'])+'|')
  (run/'RESULTS.md').write_text('\n'.join(lines)+'\n')
 return len(rows)

def score(run):
 p=verify(run);assert read(run/'inference_barrier.json')['passed'];assert all(read(f)['state']=='complete' for f in (run/'jobs').glob('*.json'));os.chdir(PROJECT/'AffectGPT');sys.path.insert(0,str(PROJECT/'AffectGPT'));import evaluation
 from amg_inference.full_score import truth
 refs={d:truth(d,p,evaluation) for d in p['datasets']};judge=None
 for f in sorted((run/'jobs').glob('*.json')):
  j=read(f);dest=run/'scores'/f.name
  if dest.exists():assert read(dest)['plan_id']==p['plan_id'];continue
  raw=Path(j['official_npz']);assert raw.is_file();write(run/'evaluation_status.json',dict(state='scoring',job=j['id'],completed=len(list((run/'scores').glob('*.json'))),pid=os.getpid(),at=now()))
  for suffix in ['-openset.npz','-openset-sentiment.npz']:
   cached=raw.with_name(raw.stem+suffix)
   if cached.exists():
    try:
     with zipfile.ZipFile(cached) as z:good=z.testzip() is None
    except (OSError,zipfile.BadZipFile):good=False
    if not good:cached.unlink()
  if judge is None:judge=evaluation.func_read_batch_calling_model('Qwen25')
  d=j['dataset'];assert len(refs[d])==j['samples']
  if d=='MER2023':v,_=evaluation.calculate_discrete_zeroshot(str(raw),refs[d],*judge,True);metric='HIT';metrics=dict(HIT=float(v))
  elif d=='SIMS':v,acc=evaluation.calculate_dimension_zeroshot(str(raw),refs[d],*judge,True);metric='WAF';metrics=dict(WAF=float(v),ACC=float(acc))
  else:v,precision,recall=evaluation.calculate_ov_zeroshot(str(raw),refs[d],*judge,True);metric='F_s';metrics=dict(F_s=float(v),P_s=float(precision),R_s=float(recall))
  assert all(math.isfinite(x) for x in metrics.values());write(dest,dict(job_id=j['id'],epoch=j['epoch'],dataset=d,samples=j['samples'],main_metric=metric,main_score=float(v),metrics=metrics,checkpoint=p['checkpoints'][str(j['epoch'])],raw_sha256=sha(raw),plan_id=p['plan_id'],official_evaluation_source=str(PROJECT/'AffectGPT/evaluation.py'),completed_at=now()));j['score_state']='complete';write(f,j);summarize(run,p)
 assert summarize(run,p)==21;write(run/'evaluation_status.json',dict(state='complete',completed=21,at=now()))


def used_memory():
 return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())

def launch(run,mode,node=None,slot=None):
 args=[PYTHON,'-u','-B','-m','amg_oof_eval_20261105.execute',mode,'--run',str(run)]
 if node is not None:args+=['--node',node]
 if slot is not None:args+=['--slot',str(slot)]
 label='_'.join(str(x) for x in [mode,node,slot] if x is not None)
 with (run/'logs'/(label+'.log')).open('ab',buffering=0) as stream:
  return subprocess.Popen(args,cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)

def run_node(run,node):
 owner=lock(run/(node+'_node.lock'));assert owner is not None,'Node controller already running'
 p=verify(run);children={};state=dict(node=node,pid=os.getpid(),concurrency=4)
 def stopped(signum,frame):raise KeyboardInterrupt('Node stop requested')
 signal.signal(signal.SIGTERM,stopped);signal.signal(signal.SIGINT,stopped)
 def update(**kw):
  state.update(kw,at=now());write(run/'workers'/(node+'_controller.json'),state)
 try:
  assert used_memory()<512,'GPU is occupied'
  assert not (run/'STOP.json').exists(),'Run has stop signal'
  update(state='starting')
  for slot in range(4):children[slot]=launch(run,'infer',node,slot)
  retries=collections.Counter()
  while children:
   assert not (run/'STOP.json').exists(),'Coordinator stopped run'
   for slot,child in list(children.items()):
    code=child.poll()
    if code is None:continue
    if code==0:del children[slot];continue
    retries[slot]+=1;assert retries[slot]<=1,'Worker repeatedly failed: '+str(slot)
    children[slot]=launch(run,'infer',node,slot)
   update(state='running',pids={k:v.pid for k,v in children.items()},retries=dict(retries))
   if children:time.sleep(10)
  update(state='complete',pids={},retries=dict(retries))
 except BaseException as exc:
  update(state='failed',error=repr(exc),traceback=traceback.format_exc())
  for child in children.values():
   if child.poll() is None:
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:owner.close()

def pipeline(run):
 owner=lock(run/'pipeline.lock');assert owner is not None,'Pipeline already active'
 p=verify(run);children={};state=dict(pid=os.getpid(),run=str(run),plan_id=p['plan_id'],nodes=p['nodes'],concurrency=8,concurrency_per_gpu=4)
 def update(**kw):state.update(kw,at=now());write(run/'pipeline_status.json',state)
 def stop(signum,frame):raise KeyboardInterrupt('Stop requested')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  children['A800']=launch(run,'node','A800')
  update(phase='inference',predictions_completed=0,predictions_total=9800)
  deadline=time.monotonic()+1800
  while True:
   nodes={n:read(run/'workers'/(n+'_controller.json')) if (run/'workers'/(n+'_controller.json')).exists() else dict(state='pending_start') for n in p['nodes']}
   assert not any(v['state']=='failed' for v in nodes.values()),'Node failed: '+repr(nodes)
   for node,child in list(children.items()):
    if child.poll() is not None:assert child.returncode==0,'Local node controller failed'
   done=sum(read(f)['state']=='complete' for f in (run/'shards').glob('*.json'))
   groups=sum(read(f)['state']=='complete' for f in (run/'jobs').glob('*.json'))
   completed=sum(len(list(folder.glob('*.json'))) for folder in (run/'predictions').iterdir() if folder.is_dir())
   update(phase='inference',predictions_completed=completed,inference_groups_complete=groups,completed_shards=done,node_states={k:v['state'] for k,v in nodes.items()})
   if all(v['state']=='complete' for v in nodes.values()):break
   if any(v['state']=='pending_start' for v in nodes.values()):assert time.monotonic()<deadline,'Second node did not start'
   time.sleep(15)
  for f in (run/'jobs').glob('*.json'):finalized(run,p,f.stem)
  assert len(list((run/'jobs').glob('*.json')))==21 and all(read(f)['state']=='complete' for f in (run/'jobs').glob('*.json'))
  assert completed==9800
  write(run/'inference_barrier.json',dict(passed=True,groups=21,predictions=9800,all_eight_workers_exited=True,at=now()))
  update(phase='waiting_for_GPU_release_before_evaluation')
  deadline=time.monotonic()+180
  while used_memory()>512:assert time.monotonic()<deadline,'GPU not released';time.sleep(3)
  child=launch(run,'score');children={'score':child};update(phase='automatic_official_evaluation',evaluator_pid=child.pid)
  while child.poll() is None:
   update(phase='automatic_official_evaluation',scored_groups=len(list((run/'scores').glob('*.json'))));time.sleep(15)
  assert child.returncode==0,'Official evaluation failed; see logs/score.log'
  assert len(list((run/'scores').glob('*.json')))==21
  update(phase='complete',predictions_completed=9800,scored_groups=21,results=str(run/'RESULTS.md'))
 except BaseException as exc:
  update(phase='failed',error=repr(exc),traceback=traceback.format_exc());write(run/'STOP.json',dict(error=repr(exc),at=now()))
  for child in children.values():
   if child.poll() is None:
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:owner.close()

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['infer','node','pipeline','score']);a.add_argument('--run',required=True);a.add_argument('--node',choices=['A800','A100']);a.add_argument('--slot',type=int)
 x=a.parse_args();r=Path(x.run)
 {'infer':lambda:infer(r,x.slot,x.node),'node':lambda:run_node(r,x.node),'pipeline':lambda:pipeline(r),'score':lambda:score(r)}[x.mode]()

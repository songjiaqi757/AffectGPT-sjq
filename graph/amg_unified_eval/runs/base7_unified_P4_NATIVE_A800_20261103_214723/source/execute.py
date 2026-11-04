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

def infer(run,slot):
 p=verify(run);inv=read(run/'cache_inventory.json');statusfile=run/'workers'/f'A800_{slot}.json';state=dict(node='A800',slot=slot,pid=os.getpid(),completed_samples=0)
 def update(**kw):state.update(kw,updated_at=now());write(statusfile,state)
 try:
  from .model import Predictor
  import torch
  update(state='loading')
  with lock(run/'model_loading.lock',True):model=Predictor(p);model.load(p['checkpoints']['30'])
  update(state='probe_ready')
  while not (run/'capacity_go.json').exists():time.sleep(2)
  source=read(run/'source_probe.json');response,info=model.predict(source['row'],source,None,stress=True);assert 794<=info['stress_prompt_tokens']<=800 and info['stress_generated_tokens']==1200,'Full context capacity test failed';write(run/'workers'/f'capacity_{slot}.json',dict(passed=True,slot=slot,pid=os.getpid(),info=info,plan_id=p['plan_id'],at=now()));update(state='probe_passed')
  while not (run/'capacity_accepted.json').exists():time.sleep(2)
  files=list((run/'shards').glob('*.json'));rows_by_dataset={d:read(s['path']) for d,s in p['datasets'].items()}
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
     with lock(run/'model_loading.lock',True):model.load(spec)
    smokefile=run/'workers'/f'checkpoint_smoke_{s["epoch"]}.json'
    with lock(smokefile.with_suffix('.lock'),True):
     if not smokefile.exists():
      answer,si=model.predict(source['row'],source,None);assert isinstance(answer,str) and answer.strip(),'Source checkpoint smoke empty';write(smokefile,dict(passed=True,checkpoint=spec,response=answer,prompt_info=si,at=now()))
    update(state='inference',epoch=s['epoch'],dataset=s['dataset'],shard=s['id']);folder=run/'predictions'/s['job_id'];folder.mkdir(parents=True,exist_ok=True)
    for row in rows_by_dataset[s['dataset']][s['start']:s['stop']]:
     dest=folder/(key(row['sample_id'])+'.json');binding=digest([p['plan_id'],spec['sha256'],p['datasets'][s['dataset']]['sha256'],inv[row['sample_id']]['cache_id']])
     if dest.exists():assert read(dest)['binding']==binding,'Stale prediction binding'
     else:
      entry=inv[row['sample_id']];assert sha(entry['path'])==entry['sha256'];b=read(entry['path']);assert b['cache_id']==entry['cache_id'] and b['row_sha256']==digest(row);seed=None;started=time.monotonic();response,info=model.predict(row,b,seed);assert isinstance(response,str)
      write(dest,dict(sample_id=row['sample_id'],name=row['name'],dataset=s['dataset'],epoch=s['epoch'],response=response,generation_empty=not response.strip(),checkpoint=spec,binding=binding,plan_id=p['plan_id'],cache_id=b['cache_id'],graph_release_id=p['graph_release_id'],prompt_release_id=p['prompt_release_id'],prompt_info=info,seed=seed,slot=slot,elapsed_seconds=time.monotonic()-started,created_at=now()));state['completed_samples']+=1;update(last_sample_id=row['sample_id'],last_seconds=time.monotonic()-started)
    s.update(state='complete',finished_at=now());write(f,s);finalized(run,p,s['job_id'])
   except BaseException as exc:s.update(state='pending' if s['attempts']<3 else 'failed',error=repr(exc),traceback=traceback.format_exc());write(f,s);raise
   finally:h.close()
  for f in (run/'jobs').glob('*.json'):finalized(run,p,f.stem)
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
  lines=['# Seven original checkpoints + AMG v2.1 unified P4','', 'Official repository evaluation. Values below are percentages. No target-based prompt tuning or checkpoint mixing.','', '|Epoch|MER2023 HIT|SIMS WAF|SIMS ACC|OVMERDPlus F_s|P_s|R_s|','|---:|---:|---:|---:|---:|---:|---:|']
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

def used_memory():return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
def pipeline(run):
 owner=lock(run/'pipeline.lock');assert owner is not None,'Pipeline already active';p=verify(run);children={};state=dict(pid=os.getpid(),run=str(run),plan_id=p['plan_id'],node='A800',concurrency=4)
 def update(**kw):state.update(kw,at=now());write(run/'pipeline_status.json',state)
 def launch(mode,slot=None):
  args=[PYTHON,'-u','-B','-m','amg_unified_eval.execute',mode,'--run',str(run)]
  if slot is not None:args+=['--slot',str(slot)]
  log=run/'logs'/(mode+('_'+str(slot) if slot is not None else '')+'.log')
  with log.open('ab',buffering=0) as stream:return subprocess.Popen(args,cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 def stop(signum,frame):raise KeyboardInterrupt('Pipeline stop requested')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  uuid=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip();assert uuid==p['gpu_uuid'],'This run is A800 only';assert used_memory()<512,'A800 GPU is occupied'
  for f in [run/'capacity_go.json',run/'capacity_accepted.json']:f.unlink(missing_ok=True)
  for slot in range(4):
   for f in [run/'workers'/f'A800_{slot}.json',run/'workers'/f'capacity_{slot}.json']:f.unlink(missing_ok=True)
   children[slot]=launch('infer',slot)
  update(phase='loading_four_models',pids={k:v.pid for k,v in children.items()});deadline=time.monotonic()+2400
  while True:
   assert all(v.poll() is None for v in children.values()),'Worker failed during loading; see worker logs'
   ss=[read(run/'workers'/f'A800_{s}.json') if (run/'workers'/f'A800_{s}.json').exists() else {} for s in range(4)]
   update(phase='loading_four_models',worker_states=[s.get('state') for s in ss])
   if all(s.get('state')=='probe_ready' for s in ss):break
   assert time.monotonic()<deadline,'Four-model loading timeout';time.sleep(5)
  write(run/'capacity_go.json',dict(workers=4,at=now()));update(phase='four_way_full_context_capacity_probe')
  while not all((run/'workers'/f'capacity_{s}.json').exists() for s in range(4)):
   assert all(v.poll() is None for v in children.values()),'Four-way capacity worker failed';assert time.monotonic()<deadline,'Capacity probe timeout';time.sleep(5)
  reports=[read(run/'workers'/f'capacity_{s}.json') for s in range(4)];assert all(x['passed'] for x in reports);write(run/'capacity_accepted.json',dict(passed=True,workers=4,context=2000,input_tokens=800,generated_tokens=1200,reports=reports,at=now()));update(phase='inference',capacity_passed=True)
  retries=collections.Counter()
  while children:
   for slot,child in list(children.items()):
    code=child.poll()
    if code is None:continue
    if code==0:del children[slot];continue
    retries[slot]+=1;assert retries[slot]<=2,'Repeated worker failure; see '+str(slot)
    # Capacity has already passed; restarted workers reuse the explicit accepted barrier.
    children[slot]=launch('infer',slot)
   completed=sum(len(list(folder.glob('*.json'))) for folder in (run/'predictions').iterdir() if folder.is_dir());jobs_done=sum(read(f)['state']=='complete' for f in (run/'jobs').glob('*.json'));update(phase='inference',predictions_completed=completed,predictions_total=9800,inference_groups_complete=jobs_done,pids={k:v.pid for k,v in children.items()},retries=dict(retries));time.sleep(10)
  for f in (run/'jobs').glob('*.json'):finalized(run,p,f.stem)
  assert len(list((run/'jobs').glob('*.json')))==21 and all(read(f)['state']=='complete' for f in (run/'jobs').glob('*.json'));write(run/'inference_barrier.json',dict(passed=True,groups=21,predictions=9800,all_four_workers_exited=True,at=now()));update(phase='waiting_for_GPU_release_before_evaluation')
  deadline=time.monotonic()+180
  while used_memory()>512:assert time.monotonic()<deadline,'GPU not released';time.sleep(3)
  for attempt in range(3):
   child=launch('score');children={'score':child};update(phase='automatic_official_evaluation',evaluator_pid=child.pid)
   while child.poll() is None:summarize(run,p);time.sleep(15)
   children={};summarize(run,p)
   if child.returncode==0:break
   assert attempt<2,'Official evaluation repeatedly failed'
   try:os.killpg(child.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   deadline=time.monotonic()+180
   while used_memory()>512:assert time.monotonic()<deadline,'Evaluator GPU workers did not exit';time.sleep(3)
   time.sleep(5)
  assert len(list((run/'scores').glob('*.json')))==21;update(phase='complete',predictions_completed=9800,scored_groups=21,results=str(run/'RESULTS.md'))
 except BaseException as exc:
  update(phase='failed',error=repr(exc),traceback=traceback.format_exc())
  for child in children.values():
   if child.poll() is None:
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:owner.close()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['infer','score','pipeline']);a.add_argument('--run',required=True);a.add_argument('--slot',type=int);x=a.parse_args();r=Path(x.run)
 {'infer':lambda:infer(r,x.slot),'score':lambda:score(r),'pipeline':lambda:pipeline(r)}[x.mode]()

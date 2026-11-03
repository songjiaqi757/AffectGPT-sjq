"""Global longest-dataset-first inference and post-inference automatic evaluation."""
from .run import *
import io,math,zipfile
from graph_paths import resolve_path
DISCRETE={'MER2023','MER2024','MELD','IEMOCAPFour'}
DIMENSION={'CMUMOSI','CMUMOSEI','SIMS','SIMSv2'}

def verify_cache(run,p,row,inventory):
 f=Path(p['graph_cache_directory'])/(key(row['sample_id'])+'.json')
 require(sha(f)==inventory[row['sample_id']]['sha256'],'Graph cache changed')
 b=read(f)
 require(b['cache_id']==inventory[row['sample_id']]['cache_id'] and b['plan_id']==p['graph_cache_plan_id'] and b['sample_id']==row['sample_id'],'Graph cache binding mismatch')
 require(b['evidence']['graph_release_id']==p['graph_release_id'] and b['evidence']['query_config_id']==p['query_config_id'],'Graph ontology/config mismatch')
 return b

def verified(run):
 p=plan(run);e=read(run/'execution_plan.json')
 require(e['execution_id']==canonical({k:v for k,v in e.items() if k!='execution_id'}),'Execution plan changed')
 require(e['inference_plan_id']==p['plan_id'],'Execution/inference mismatch')
 for f,h in e['protected_files'].items():require(sha(f)==h,'Execution resource changed: '+f)
 return p,e
def ordered(run,p):
 files=list((run/'shards').glob('*.json'));meta={f:read(f) for f in files}
 return sorted(files,key=lambda f:(-p['datasets'][meta[f]['dataset']]['samples'],-meta[f]['samples'],meta[f]['epoch'],meta[f]['start']))
def choose(files):
 for f in files:
  s=read(f)
  if s['state']=='complete':continue
  require(s['state']!='failed','Failed shard '+f.name)
  h=lock(f.with_suffix('.lock'))
  if h is None:continue
  s=read(f)
  if s['state']=='complete':h.close();continue
  require(s['attempts']<3,'Shard retry budget exhausted')
  return f,h,s
 return None
def infer(run,name,slot):
 p,e=verified(run);status_path=run/'workers'/f'{name}_{slot}.json';state=dict(node=name,slot=slot,pid=os.getpid(),completed_samples=0,started_at_beijing=now())
 def update(**kw):state.update(kw,updated_at_beijing=now());dump(status_path,state)
 try:
  update(state='loading')
  import torch
  from .original_model import Predictor
  with lock(run/f'loading_{name}.lock',True):model=Predictor(p);model.load(p['checkpoints']['30'])
  update(state='probe_ready')
  deadline=time.monotonic()+2400
  while not (run/f'probe_go_v2_{name}.json').exists():require(time.monotonic()<deadline,'Probe timeout');time.sleep(2)
  reference=read(e['capacity_reference'])
  require(reference['inference_plan_id']==p['plan_id'] and reference['gpu_uuids'][name]==p['nodes'][name]['gpu_uuid'],'Capacity reference mismatch')
  saved=reference['reports'][name][str(slot)]
  require(saved['passed'],'Prior conservative capacity probe failed')
  dump(run/'workers'/f'capacity_v2_{name}_{slot}.json',dict(passed=True,info=saved['info'],capacity_reused=True,execution_id=e['execution_id']))
  update(state='probe_passed')
  while not (run/f'probe_accepted_v2_{name}.json').exists():time.sleep(2)
  inventory=read(run/'cache_inventory.json');files=ordered(run,p);checked=set()
  while True:
   claim=choose(files)
   if claim is None:
    if all(read(f)['state']=='complete' for f in files):break
    update(state='waiting_for_inflight_shards');time.sleep(3);continue
   f,h,s=claim
   try:
    s.update(state='running',attempts=s['attempts']+1,node=name,slot=slot,pid=os.getpid());dump(f,s)
    spec=p['checkpoints'][str(s['epoch'])]
    if model.loaded!=spec['sha256']:
     update(state='switching_checkpoint',epoch=s['epoch'])
     with lock(run/f'loading_{name}.lock',True):model.load(spec)
    update(state='inference',epoch=s['epoch'],job_id=s['job_id'],shard=f.name,scheduling='global largest dataset first')
    folder=run/'predictions'/s['job_id'];folder.mkdir(exist_ok=True);binding=canonical([p['plan_id'],spec['sha256'],p['datasets'][s['dataset']]['sha256']])
    for row in read(p['datasets'][s['dataset']]['path'])[s['start']:s['stop']]:
     dest=folder/(key(row['sample_id'])+'.json');b=verify_cache(run,p,row,inventory)
     if dest.exists():
      x=read(dest);require(x['binding']==binding and x['cache_id']==b['cache_id'],'Stale partial prediction')
     else:
      seed=None;started=time.monotonic()
      response,info=model.predict(row,b['evidence'],seed);require(isinstance(response,str),'Target response is not text')
      dump(dest,dict(sample_id=row['sample_id'],name=row['name'],dataset=s['dataset'],epoch=s['epoch'],response=response,generation_empty=(not response.strip()),checkpoint=spec,plan_id=p['plan_id'],binding=binding,cache_id=b['cache_id'],graph_release_id=p['graph_release_id'],query_config_id=p['query_config_id'],policy='D=compact+gate+Graph-OOF inference',seed=seed,prompt_info=info,node=name,slot=slot,elapsed_seconds=time.monotonic()-started,created_at_beijing=now()))
     require(dest!=status_path,'Status path collides with prediction')
     state['completed_samples']+=1;update(last_sample_id=row['sample_id'])
     committed=read(dest);require(committed.get('binding')==binding and isinstance(committed.get('response'),str),'Prediction was overwritten')
    s.update(state='complete',finished_at_beijing=now());dump(f,s);finalize(run,p,s['job_id'])
   except BaseException as exc:s.update(state='pending' if s['attempts']<3 else 'failed',error=repr(exc));dump(f,s);raise
   finally:h.close()
  for f in (run/'jobs').glob('*.json'):finalize(run,p,f.stem)
  update(state='complete',finished_at_beijing=now())
 except BaseException as exc:update(state='failed',error=repr(exc),traceback=traceback.format_exc());raise
def score_claim(run):
 files=list((run/'evaluation_jobs').glob('*.json'));files.sort(key=lambda f:(-read(f)['samples'],f.name))
 for f in files:
  if read(f)['state']=='complete':continue
  h=lock(f.with_suffix('.lock'))
  if h is None:continue
  j=read(f)
  if j['state']=='complete':h.close();continue
  if (run/'scores'/f.name).exists():
   result=read(run/'scores'/f.name);require(result['job_id']==j['job_id'],'Wrong committed score');j['state']='complete';dump(f,j);h.close();continue
  require(j['attempts']<3,'Score retry limit');j.update(state='running',attempts=j['attempts']+1,pid=os.getpid());dump(f,j);return f,h,j
 return None
def score(run,name):
 p,e=verified(run);require(read(run/'evaluation_barrier.json')['passed'],'Global inference barrier closed')
 state=dict(node=name,pid=os.getpid(),completed=0,started_at_beijing=now())
 def update(**kw):state.update(kw,time_beijing=now());dump(run/f'evaluation_{name}.json',state)
 try:
  update(state='loading')
  os.chdir(resolve_path(ROOT/'AffectGPT'));sys.path.insert(0,str(ROOT/'AffectGPT'));import evaluation
  from amg_inference.full_score import truth
  refs={d:truth(d,p,evaluation) for d in p['datasets']};judge=None
  while True:
   claim=score_claim(run)
   if claim is None:
    if all(read(f)['state']=='complete' for f in (run/'evaluation_jobs').glob('*.json')):break
    update(state='waiting');time.sleep(5);continue
   f,h,j=claim
   try:
    job=read(run/'jobs'/f.name);require(job['state']=='complete','Incomplete inference')
    raw=Path(job['official_npz'])
    for suffix in ['-openset.npz','-openset-sentiment.npz']:
     cache=raw.with_name(raw.stem+suffix)
     if cache.exists():
      try:
       with zipfile.ZipFile(cache) as z:valid=z.testzip() is None
      except (OSError,zipfile.BadZipFile):valid=False
      if not valid:cache.unlink()
    if judge is None:judge=evaluation.func_read_batch_calling_model('Qwen25')
    llm,t,params=judge;d=j['dataset'];update(state='scoring',job_id=j['job_id'])
    if d in DISCRETE:
     value,_=evaluation.calculate_discrete_zeroshot(str(raw),refs[d],llm,t,params,True);metrics={'HIT':float(value)};metric='HIT'
    elif d in DIMENSION:
     value,acc=evaluation.calculate_dimension_zeroshot(str(raw),refs[d],llm,t,params,True);metrics={'WAF':float(value),'ACC':float(acc)};metric='WAF'
    else:
     value,precision,recall=evaluation.calculate_ov_zeroshot(str(raw),refs[d],llm,t,params,True);metrics={'F_s':float(value),'P_s':float(precision),'R_s':float(recall)};metric='F_s'
    require(all(math.isfinite(v) for v in metrics.values()),'Nonfinite score')
    dump(run/'scores'/f.name,dict(job_id=j['job_id'],epoch=j['epoch'],dataset=d,samples=len(refs[d]),main_metric=metric,main_score=float(value),metrics=metrics,checkpoint=p['checkpoints'][str(j['epoch'])],plan_id=p['plan_id'],execution_id=e['execution_id'],raw_sha256=sha(raw),node=name,completed_at_beijing=now()))
    j.update(state='complete');dump(f,j);state['completed']+=1;update()
   except BaseException as exc:j.update(state='pending' if j['attempts']<3 else 'failed',error=repr(exc));dump(f,j);raise
   finally:h.close()
  update(state='complete')
 except BaseException as exc:update(state='failed',error=repr(exc),traceback=traceback.format_exc());raise
def summarize(run,p):
 h=lock(run/'summary.lock')
 if h is None:return
 try:
  rows=[read(f) for f in (run/'scores').glob('*.json')]
  columns=['epoch','dataset','samples','main_metric','main_score','HIT','WAF','ACC','F_s','P_s','R_s']
  out=io.StringIO();w=csv.DictWriter(out,fieldnames=columns,extrasaction='ignore');w.writeheader()
  for r in sorted(rows,key=lambda r:(r['epoch'],r['dataset'])):w.writerow(dict(r,**r['metrics']))
  tmp=run/'metrics_all.csv.tmp';tmp.write_text(out.getvalue());tmp.replace(run/'metrics_all.csv')
  summary=[]
  for epoch in p['checkpoints']:
   selected=[r for r in rows if r['epoch']==int(epoch)];r=dict(epoch=int(epoch),datasets_completed=len(selected),nine_dataset_mean=sum(v['main_score'] for v in selected)/9 if len(selected)==9 else None)
   for v in selected:
    for k,value in v['metrics'].items():r[v['dataset']+'_'+k]=value
   summary.append(r)
  dump(run/'per_checkpoint_summary.json',summary);fields=['epoch','datasets_completed','nine_dataset_mean']
  for d in p['datasets']:fields += [d+'_'+k for k in (['HIT'] if d in DISCRETE else ['WAF','ACC'] if d in DIMENSION else ['F_s','P_s','R_s'])]
  out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields);w.writeheader();w.writerows(summary)
  tmp=run/'per_checkpoint_summary.csv.tmp';tmp.write_text(out.getvalue());tmp.replace(run/'per_checkpoint_summary.csv')
  if len(rows)==63:
   ds=list(p['datasets']);lines=['# Seven original checkpoints + graph10, D inference','', 'Original repository metrics; percentages. Arithmetic mean of nine dataset main scores is descriptive.','', '|Epoch|'+'|'.join(ds)+'|Nine-dataset mean|','|---:|'+'---:|'*(len(ds)+1)]
   for r in summary:
    vals=[r[d+('_HIT' if d in DISCRETE else '_WAF' if d in DIMENSION else '_F_s')] for d in ds]+[r['nine_dataset_mean']]
    lines.append('|'+str(r['epoch'])+'|'+'|'.join(f'{100*v:.2f}' for v in vals)+'|')
   (run/'RESULTS.md').write_text('\n'.join(lines)+'\n')
 finally:h.close()
def gpu_free():
 return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())<512
def pipeline(run,name):
 owner=lock(run/f'pipeline_{name}.lock');require(owner is not None,'Pipeline already running')
 p,e=verified(run);procs={};state=dict(node=name,pid=os.getpid(),execution_id=e['execution_id'])
 def update(**kw):state.update(kw,time_beijing=now());dump(run/f'pipeline_{name}.json',state)
 def start(mode,slot=None):
  args=[PYTHON,'-u','-B','-m','amg_base7_graph10.execution_original',mode,'--run',str(run),'--node',name]
  if slot is not None:args+=['--slot',str(slot)]
  with (run/(f'v2_{mode}_{name}'+('' if slot is None else '_'+str(slot))+'.log')).open('ab',buffering=0) as f:
   return subprocess.Popen(args,cwd=ROOT,env=dict(env(),VLLM_WORKER_MULTIPROC_METHOD='spawn'),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 def stop(*_):raise KeyboardInterrupt('Pipeline stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  uuid=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip();require(uuid==p['nodes'][name]['gpu_uuid'],'Wrong GPU');require(gpu_free(),'GPU busy')
  for f in [run/f'probe_go_v2_{name}.json',run/f'probe_accepted_v2_{name}.json',run/f'gpu_released_{name}.json']:f.unlink(missing_ok=True)
  for slot in range(3):
   (run/'workers'/f'{name}_{slot}.json').unlink(missing_ok=True);(run/'workers'/f'capacity_v2_{name}_{slot}.json').unlink(missing_ok=True);procs[slot]=start('infer',slot)
  deadline=time.monotonic()+2400
  while True:
   require(all(z.poll() is None for z in procs.values()),'Worker failed during model loading')
   ss=[read(run/'workers'/f'{name}_{s}.json') if (run/'workers'/f'{name}_{s}.json').exists() else {} for s in range(3)];update(phase='loading_and_capacity',workers=ss)
   if all(s.get('state')=='probe_ready' for s in ss):dump(run/f'probe_go_v2_{name}.json',dict(workers=3,time_beijing=now()));break
   require(time.monotonic()<deadline,'Loading deadline');time.sleep(5)
  while not all((run/'workers'/f'capacity_v2_{name}_{s}.json').exists() for s in range(3)):
   require(all(z.poll() is None for z in procs.values()),'Capacity worker failed');require(time.monotonic()<deadline,'Capacity deadline');time.sleep(5)
  dump(run/f'probe_accepted_v2_{name}.json',dict(passed=True,workers=3,gpu_uuid=uuid,execution_id=e['execution_id'],time_beijing=now()))
  retries=Counter()
  while procs:
   update(phase='inference',pids={s:z.pid for s,z in procs.items()})
   for slot,z in list(procs.items()):
    if z.poll() is None:continue
    if z.returncode==0:del procs[slot];continue
    retries[slot]+=1;require(retries[slot]<=2,'Repeated inference failure');time.sleep(3);procs[slot]=start('infer',slot)
   time.sleep(5)
  require(all(read(f)['state']=='complete' for f in (run/'jobs').glob('*.json')),'Incomplete export')
  update(phase='waiting_for_gpu_release');deadline=time.monotonic()+180
  while not gpu_free():require(time.monotonic()<deadline,'GPU not released');time.sleep(3)
  dump(run/f'gpu_released_{name}.json',dict(passed=True,all_local_inference_processes_exited=True,gpu_uuid=uuid,execution_id=e['execution_id'],time_beijing=now()))
  update(phase='waiting_for_both_gpus')
  while not all((run/f'gpu_released_{n}.json').exists() and read(run/f'gpu_released_{n}.json')['execution_id']==e['execution_id'] for n in ['A800','A100']):
   other=run/f'pipeline_{"A100" if name=="A800" else "A800"}.json'
   if other.exists():require(read(other).get('phase')!='failed','Other node failed')
   time.sleep(5)
  with lock(run/'evaluation_barrier.lock',True):
   dump(run/'evaluation_barrier.json',dict(passed=True,inference_jobs=63,predictions=89593,both_nodes_released=True,all_six_inference_processes_exited=True,execution_id=e['execution_id'],time_beijing=now()))
  update(phase='evaluation');attempt=0
  while True:
   z=start('score');procs={'score':z}
   while z.poll() is None:summarize(run,p);time.sleep(10)
   procs={};summarize(run,p)
   if z.returncode==0:break
   attempt+=1;require(attempt<=2,'Repeated evaluator failure')
   try:os.killpg(z.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   deadline=time.monotonic()+180
   while not gpu_free():require(time.monotonic()<deadline,'Judge GPU memory held');time.sleep(3)
  require(len(list((run/'scores').glob('*.json')))==63,'Missing scores');update(phase='complete',scores=63,results=str(run/'RESULTS.md'))
 except BaseException as exc:
  update(phase='failed',error=repr(exc),traceback=traceback.format_exc())
  for z in procs.values():
   if z.poll() is None:
    try:os.killpg(z.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:owner.close()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['infer','score','pipeline']);a.add_argument('--run',required=True);a.add_argument('--node',required=True);a.add_argument('--slot',type=int);x=a.parse_args()
 {'infer':lambda:infer(Path(x.run),x.node,x.slot),'score':lambda:score(Path(x.run),x.node),'pipeline':lambda:pipeline(Path(x.run),x.node)}[x.mode]()

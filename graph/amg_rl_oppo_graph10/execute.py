import argparse,subprocess,time,traceback,signal,csv,io,math,copy
from collections import Counter
from .common import *
def status(run,role,slot,**kw):
 path=Path(run)/'workers'/(role+'_'+str(slot)+'.json')
 value=read(path) if path.exists() else {}
 value.update(kw,role=role,slot=slot,pid=os.getpid(),time_beijing=now());dump(path,value)
def inventory(run,p):
 require(sha(Path(run)/'cache_inventory.json')==p['cache_inventory_sha256'],'Cache inventory changed')
 return read(Path(run)/'cache_inventory.json')
def finalize(run,p,jid):
 run=Path(run);h=lock(run/'jobs'/(jid+'.lock'))
 if h is None:return
 try:
  j=read(run/'jobs'/(jid+'.json'))
  if j['state']=='complete':return
  if not all(read(run/'shards'/(sid+'.json'))['state']=='complete' for sid in j['shards']):return
  model=p['models'][j['role']];rows=read(model['datasets'][j['dataset']]['path']);records=[]
  for row in rows:
   value=read(run/'predictions'/jid/(canonical(row['name'])+'.json'))
   require(value['plan_id']==p['plan_id'] and value['checkpoint']==j['checkpoint'],'Wrong prediction binding')
   records.append(value)
  outdir=run/'official'/j['role']/('results-'+j['dataset'].lower())/'graph10';outdir.mkdir(parents=True,exist_ok=True)
  spec=model['checkpoints'][j['checkpoint']]
  if j['role']=='rl':
   import numpy as np
   dest=outdir/(Path(spec['path']).stem+'.npz');temp=dest.with_suffix('.tmp')
   with temp.open('wb') as f:np.savez_compressed(f,name2reason={x['name']:x['response'] for x in records})
   temp.replace(dest);j['official_npz']=str(dest)
  else:
   sys.path.insert(0,str(OPPO))
   from affect_r1.merbench.result_writer import MerBenchResultWriter
   tmp=outdir/(j['checkpoint']+'.jsonl')
   stage=run/'official'/'oppo_export_staging'
   writer=MerBenchResultWriter(str(stage),j['dataset'],'graph10',j['checkpoint'],extra_metadata=dict(model_path=spec['path'],revision=spec['revision'],graph_release_id=p['graph_release_id'],plan_id=p['plan_id']))
   try:
    # Rebuild one complete file; never append duplicate retries.
    writer._fh.close();writer._fh=open(writer.jsonl_path,'w',encoding='utf-8')
    for x in records:
     writer.log_sample(x['name'],x['response'],subtitle=x['subtitle'],metadata=x['prompt_info'])
   finally:writer.close()
   Path(writer.jsonl_path).replace(tmp);j['official_jsonl']=str(tmp)
  j.update(state='complete',finished_at_beijing=now());dump(run/'jobs'/(jid+'.json'),j)
 finally:h.close()
def infer(run,role,slot):
 run=Path(run);p=plan(run);modelp=p['models'][role];inv=inventory(run,p)
 status(run,role,slot,state='loading',completed_samples=0)
 try:
  if role=='rl':
   from .native_rl import Predictor
  else:
   from .native_oppo import Predictor
  # Separate processes retain each model's native module namespace.
  with lock(run/('loading_'+role+'.lock'),True):
   predictor=Predictor();predictor.load(next(iter(modelp['checkpoints'].values())))
  status(run,role,slot,state='ready')
  allfiles=[f for f in (run/'shards').glob(role+'*.json')]
  def order(f):
   s=read(f);epoch=modelp['checkpoints'][s['checkpoint']]['epoch'] or 0
   return (epoch,-modelp['datasets'][s['dataset']]['samples'],s['start'])
  allfiles.sort(key=order);done=0
  for f in allfiles:
   if read(f)['state']=='complete':continue
   h=lock(f.with_suffix('.lock'))
   if h is None:continue
   try:
    s=read(f)
    if s['state']=='complete':continue
    require(s['attempts']<3,'Shard failed repeatedly '+s['id'])
    s.update(state='running',attempts=s['attempts']+1,pid=os.getpid(),slot=slot);dump(f,s)
    predictor.load(modelp['checkpoints'][s['checkpoint']])
    status(run,role,slot,state='inference',checkpoint=s['checkpoint'],dataset=s['dataset'],shard=s['id'],completed_samples=done)
    folder=run/'predictions'/s['job_id'];folder.mkdir(parents=True,exist_ok=True)
    for row in read(modelp['datasets'][s['dataset']]['path'])[s['start']:s['stop']]:
     dest=folder/(canonical(row['name'])+'.json')
     if dest.exists():
      old=read(dest);require(old['plan_id']==p['plan_id'],'Stale saved prediction');continue
     b=graph_evidence(p,inv,row['dataset'],row['name']);started=time.monotonic()
     response,info=predictor.predict(p,row,b['evidence'])
     require(isinstance(response,str),'Response is not text')
     dump(dest,dict(name=row['name'],sample_id=row['sample_id'],dataset=row['dataset'],subtitle=row['subtitle'],role=role,checkpoint=s['checkpoint'],response=response,generation_empty=not response.strip(),prompt_info=info,graph_cache_id=b['cache_id'],plan_id=p['plan_id'],slot=slot,elapsed_seconds=time.monotonic()-started,time_beijing=now()))
     done+=1;status(run,role,slot,state='inference',completed_samples=done,last_sample=row['sample_id'],last_seconds=time.monotonic()-started)
    s.update(state='complete',finished_at_beijing=now());dump(f,s);finalize(run,p,s['job_id'])
   except BaseException as exc:
    s.update(state='pending' if s.get('attempts',0)<3 else 'failed',error=type(exc).__name__+': '+str(exc));dump(f,s);raise
   finally:h.close()
  # Other workers may own skipped shards.
  status(run,role,slot,state='complete',completed_samples=done)
 except BaseException as exc:
  status(run,role,slot,state='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc());raise
def summarize(run,p):
 run=Path(run);h=lock(run/'summary.lock')
 if h is None:return
 try:
  rows=[read(f) for f in (run/'scores').glob('*.json')]
  fields=['role','checkpoint','dataset','samples','main_metric','main_score','metrics']
  s=io.StringIO();w=csv.DictWriter(s,fieldnames=fields,extrasaction='ignore');w.writeheader()
  for x in sorted(rows,key=lambda x:(x['role'],x['checkpoint'],x['dataset'])):w.writerow(x)
  temp=run/'metrics_all.csv.tmp';temp.write_text(s.getvalue());temp.replace(run/'metrics_all.csv')
  summary=[]
  for role,model in p['models'].items():
   for cid in model['checkpoints']:
    subset=[r for r in rows if r['checkpoint']==cid]
    x=dict(role=role,checkpoint=cid,datasets_completed=len(subset),nine_dataset_mean=sum(r['main_score'] for r in subset)/9 if len(subset)==9 else None)
    x.update({r['dataset']:r['main_score'] for r in subset});summary.append(x)
  dump(run/'per_checkpoint_summary.json',summary)
  fields=['role','checkpoint','datasets_completed']+DATASETS+['nine_dataset_mean']
  s=io.StringIO();w=csv.DictWriter(s,fieldnames=fields);w.writeheader();w.writerows(summary)
  temp=run/'per_checkpoint_summary.csv.tmp';temp.write_text(s.getvalue());temp.replace(run/'per_checkpoint_summary.csv')
  if len(rows)==117:
   lines=['# Official inference + Cue/Appraisal/10-emotion graph','','Percentages; each row uses the same checkpoint across all nine datasets.','', '|Model/checkpoint|'+'|'.join(DATASETS)+'|Mean|','|---|'+'---:|'*10]
   for x in summary:lines.append('|'+x['checkpoint']+'|'+'|'.join('%.2f'%(100*x[d]) for d in DATASETS)+'|%.2f|'%(100*x['nine_dataset_mean']))
   (run/'RESULTS.md').write_text('\n'.join(lines)+'\n')
 finally:h.close()
def pipeline(run,role,workers):
 run=Path(run);p=plan(run);owner=lock(run/('pipeline_'+role+'.lock'));require(owner is not None,'Pipeline already running')
 statefile=run/('pipeline_'+role+'.json');procs={};retries=Counter()
 def update(**kw):dump(statefile,dict(role=role,pid=os.getpid(),time_beijing=now(),**kw))
 def start(mode,slot=0):
  logfile=run/'logs'/(role+'_'+mode+'_'+str(slot)+'.log')
  with logfile.open('ab',buffering=0) as log:
   return subprocess.Popen([PYTHON,'-u','-B','-m','amg_rl_oppo_graph10.execute',mode,'--run',str(run),'--role',role,'--slot',str(slot)],cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  update(phase='inference',workers=workers)
  for slot in range(workers):procs[slot]=start('infer',slot)
  while procs:
   for slot,z in list(procs.items()):
    if z.poll() is None:continue
    if z.returncode==0:del procs[slot]
    else:
     retries[slot]+=1;require(retries[slot]<=2,'Repeated inference worker failure: '+str(slot));time.sleep(3);procs[slot]=start('infer',slot)
   update(phase='inference',workers=workers,pids={s:z.pid for s,z in procs.items()});time.sleep(10)
  for f in (run/'jobs').glob(role+'*.json'):finalize(run,p,f.stem)
  require(all(read(f)['state']=='complete' for f in (run/'jobs').glob(role+'*.json')),'Incomplete inference jobs')
  update(phase='evaluation',workers_exited=True)
  for attempt in range(3):
   z=start('score');procs={'score':z}
   while z.poll() is None:summarize(run,p);time.sleep(15)
   procs={};summarize(run,p)
   if z.returncode==0:break
  require(z.returncode==0,'Repeated evaluation failure')
  update(phase='complete',results=str(run/'per_checkpoint_summary.csv'))
 except BaseException as exc:
  update(phase='failed',error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc())
  for z in procs.values():
   if z.poll() is None:
    try:os.killpg(z.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:owner.close()
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['infer','score','pipeline','summarize']);a.add_argument('--run',required=True);a.add_argument('--role',choices=['rl','oppo'],default='rl');a.add_argument('--slot',type=int,default=0);a.add_argument('--workers',type=int,default=1);x=a.parse_args()
 if x.mode=='infer':infer(x.run,x.role,x.slot)
 elif x.mode=='pipeline':pipeline(x.run,x.role,x.workers)
 elif x.mode=='score':
  from .scoring import score
  score(x.run,x.role)
 else:summarize(x.run,plan(x.run))
if __name__=='__main__':main()

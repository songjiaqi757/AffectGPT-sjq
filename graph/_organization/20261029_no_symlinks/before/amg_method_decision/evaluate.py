"""Shared-content judge cache and official metrics for new, separated records."""
import os,sys,time,copy,collections,json,math,runpy,argparse
from pathlib import Path
ROOT=Path('/ai/sjq/AffectGPT-sjq');sys.path.insert(0,str(ROOT))
from amg_method_decision.pipeline import read,dump,canonical,sha,now,key
from amg_method_decision.generate import verify
from amg_188_audit.metrics import npwrite
SOURCE=ROOT/'amg_188_path_noemotion/runs/path_noemotion_20261028_170538'
def jkey(p,stage,text):return canonical(dict(protocol=p['judge_protocol_id'],stage=stage,input=text))
def eroot(run,part):
 e=run/'evaluation'/part;e.mkdir(parents=True,exist_ok=True);return e
def materialize(run,part):
 p=verify(run);e=eroot(run,part);rr=read(run/'data'/f'{part}_records.json');jobs=[];result={ck:{r['name']:read(run/'predictions'/part/ck/(key(r)+'.json')) for r in rr} for ck in p['checkpoints']}
 for ck in p['checkpoints']:
  for r in rr:
   x=result[ck][r['name']]
   if x['plan_id']!=p['plan_id'] or len(x['answers'])!=len(p['seeds'])*len(p['conditions']):raise ValueError('Incomplete inference')
 for ck in p['checkpoints']:
  for seed in p['seeds']:
   for arm in p['conditions']:
    for fam in ['MER_track1','MER_OV']:
     names=[r['name'] for r in rr if r['family']==fam];job=f'{ck}__{seed}__{arm}__{fam}';folder=e/'predictions'/job;folder.mkdir(parents=True,exist_ok=True);raw=folder/'name2reason.npz';answers={}
     for n in names:
      a=[a for a in result[ck][n]['answers'] if a['seed']==seed and a['condition']==arm]
      if len(a)!=1:raise ValueError('Answer identity mismatch')
      answers[n]=a[0]['response']
     npwrite(raw,name2reason=answers);jobs.append(dict(job_id=job,checkpoint=ck,seed=seed,condition=arm,family=fam,raw=str(raw),answers=answers))
 dump(e/'jobs.json',jobs);dump(e/'evaluation_barrier.json',dict(passed=True,all_generators_finished=True,time_beijing=now()));return jobs
def prepare_judge(run,part,stage):
 p=verify(run);e=eroot(run,part);items={}
 for j in read(e/'jobs.json'):
  if stage=='sentiment' and j['family']!='MER_track1':continue
  for text in j['answers'].values():
   if stage=='sentiment':text=read(run/'judge_cache/openset'/(jkey(p,'openset',text)+'.json'))['output']
   k=jkey(p,stage,text);items[k]=dict(key=k,text=text,seed=(20261028+int(k[:8],16))%2**32)
 reused=0
 for x in items.values():
  f=run/'judge_cache'/stage/(x['key']+'.json');src=SOURCE/'judge_cache'/stage/f.name
  if not f.exists() and src.exists():
   y=read(src)
   if any(y[k]!=x[k] for k in ['key','text','seed']) or y['judge_protocol_id']!=p['judge_protocol_id']:raise ValueError('Judge cache mismatch')
   f.symlink_to(src);reused+=1
 dump(e/f'judge_inputs_{stage}.json',[items[k] for k in sorted(items)]);dump(e/f'judge_preparation_{stage}.json',dict(total=len(items),reused_parent_exact_content=reused,time_beijing=now()))
 return len(items)
def judge(run,part,index,stage):
 p=verify(run);e=eroot(run,part);dest=e/f'judge_{stage}_{index}.json';state=dict(index=index,stage=stage,pid=os.getpid(),state='loading')
 def update(**kw):state.update(kw,time_beijing=now());dump(dest,state)
 try:
  for f,h in read(run/'evaluation_resources.json')['files'].items():
   if sha(f)!=h:raise ValueError('Evaluation resource changed')
  rows=[x for x in read(e/f'judge_inputs_{stage}.json') if int(x['key'][:8],16)%2==index];pending=[x for x in rows if not (run/'judge_cache'/stage/(x['key']+'.json')).exists()];update(total=len(rows),pending=len(pending),completed=0)
  if pending:
   os.chdir(ROOT/'AffectGPT');sys.path.insert(0,str(ROOT/'AffectGPT'));import evaluation
   llm,t,params=evaluation.func_read_batch_calling_model('Qwen25');fn=evaluation.reason_to_openset_qwen if stage=='openset' else evaluation.openset_to_sentiment_qwen
   for start in range(0,len(pending),8):
    batch=pending[start:start+8];settings=[]
    for x in batch:
     s=copy.deepcopy(params);s.seed=x['seed'];settings.append(s)
    values=fn(llm=llm,tokenizer=t,sampling_params=settings,batch_reasons=[x['text'] for x in batch])
    if len(values)!=len(batch):raise ValueError('Judge cardinality mismatch')
    for x,y in zip(batch,values):
     if not isinstance(y,str):raise ValueError('Judge output not string')
     dump(run/'judge_cache'/stage/(x['key']+'.json'),dict(**x,output=y,judge_protocol_id=p['judge_protocol_id']))
    update(state='scoring',completed=start+len(batch))
  update(state='complete',completed=len(rows))
 except BaseException as ex:update(state='failed',error=repr(ex));raise
def metrics(run,part):
 import numpy as np
 p=verify(run);e=eroot(run,part);labels=read(run/'data'/f'{part}_labels.json');rr=read(run/'data'/f'{part}_records.json')
 cat={r['name']:labels[r['name']]['MER_track1']['discrete'] for r in rr if r['family']=='MER_track1'}
 val={n:float(labels[n]['MER_track1']['valence']) for n in cat if str(labels[n]['MER_track1'].get('valence','')).strip()}
 ov={r['name']:labels[r['name']]['MER_OV']['openset'] for r in rr if r['family']=='MER_OV'}
 os.chdir(ROOT/'AffectGPT');sys.path.insert(0,str(ROOT/'AffectGPT'));import evaluation
 scores=[]
 for j in read(e/'jobs.json'):
  raw=Path(j['raw']);answers=j['answers'];names=list(answers);op={n:read(run/'judge_cache/openset'/(jkey(p,'openset',answers[n])+'.json'))['output'] for n in names}
  npwrite(raw.with_name(raw.stem+'-openset.npz'),filenames=names,fileitems=[op[n] for n in names])
  if j['family']=='MER_track1':
   sent={n:read(run/'judge_cache/sentiment'/(jkey(p,'sentiment',op[n])+'.json'))['output'] for n in names};npwrite(raw.with_name(raw.stem+'-openset-sentiment.npz'),filenames=names,fileitems=[sent[n] for n in names])
   h,m=evaluation.calculate_discrete_zeroshot(str(raw),cat,None,None,None,False);w,a=evaluation.calculate_dimension_zeroshot(str(raw),val,None,None,None,False)
   values={'MER_track1_discrete':dict(HIT=float(h),M=float(m)), 'MER_track1_polarity':dict(WAF=float(w),ACC=float(a))}
  else:
   f,pr,re=evaluation.calculate_ov_zeroshot(str(raw),ov,None,None,None,False);values={'MER_OV':dict(F_s=float(f),P_s=float(pr),R_s=float(re))}
  for task,ms in values.items():
   x={k:v for k,v in j.items() if k!='answers'};x.update(task=task,metrics=ms,samples=len(val) if task.endswith('polarity') else len(names),mean_extracted_labels=float(np.mean([len(evaluation.string_to_list(op[n])) for n in names])))
   if not all(math.isfinite(v) for v in ms.values()):raise ValueError('Nonfinite metric')
   scores.append(x)
 dump(e/'metrics.json',scores);dump(e/'references.json',dict(MER2023=cat,SIMS=val,OVMERDPlus=ov));return scores
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode');a.add_argument('--run',required=True);a.add_argument('--part',default='development');a.add_argument('--index',type=int);a.add_argument('--stage');x=a.parse_args();r=Path(x.run)
 if x.mode=='materialize':materialize(r,x.part)
 elif x.mode=='prepare':prepare_judge(r,x.part,x.stage)
 elif x.mode=='judge':judge(r,x.part,x.index,x.stage)
 elif x.mode=='metrics':metrics(r,x.part)

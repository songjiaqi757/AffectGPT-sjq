import os,json,pathlib,runpy,warnings,collections,re,hashlib,datetime
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
ROOT=pathlib.Path('/ai/sjq/AffectGPT-sjq')
RUN=ROOT/'amg_188_audit/runs/winner188_20261028_114057'
OUT=RUN/'analysis'; OUT.mkdir(exist_ok=True)
with warnings.catch_warnings():
 warnings.simplefilter('ignore',RuntimeWarning)
 h=runpy.run_path(str(ROOT/'analysis_reports/sample_audit_75_43_20261028/common.py'))
p=json.loads((RUN/'plan.json').read_text())
scores=json.loads((RUN/'metrics_all.json').read_text())
L={(x['dataset'],x['condition']):x for x in scores}
conds=p['conditions']; ds=list(p['datasets'])
oldcases=[]
for fn in ['selected_cases.json','expanded_cases.json']:
 v=json.loads((ROOT/'analysis_reports/sample_audit_75_43_20261028'/fn).read_text())
 if isinstance(v,list):oldcases+=v
prior={(v['dataset'],v['name']):v for v in oldcases if 'dataset' in v and 'name' in v}
AR={}; RAW={}; PREDS={}; ROWS={}
for d in ds:
 ROWS[d]={x['name']:x for x in json.loads(pathlib.Path(p['datasets'][d]['path']).read_text())}
 for c in conds:
  AR[d,c]=h['arrays'](L[d,c]['raw_path'],d)
  RAW[d,c]=h['npdict'](L[d,c]['raw_path'])
  q=pathlib.Path(L[d,c]['raw_path']).with_name('predictions.jsonl')
  PREDS[d,c]={x['name']:x for x in map(json.loads,q.read_text().splitlines())}
 print('loaded',d,flush=True)
def safe(data):
 if isinstance(data,float) and not np.isfinite(data):return None
 if isinstance(data,dict):return {k:safe(v) for k,v in data.items()}
 if isinstance(data,list):return [safe(v) for v in data]
 return data
def jsonwrite(name,data):
 (OUT/name).write_text(json.dumps(safe(data),ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def cluster(d,n):
 if d in ['CMUMOSI','CMUMOSEI','MELD','IEMOCAPFour','SIMS','SIMSv2']:return n.rsplit('_',1)[0]
 return n
def sufficient(a,d,names,gidx,G):
 if 'y' in a:
  y=a['y'];z=a['z']
  rows=np.stack([y&z,~y&~z,~y&z,y&~z],axis=1).astype(float)
 else:
  keys=['prec','rec'] if d=='OVMERDPlus' else ['hit']
  chunks=[]
  for key in keys:
   x=a[key];chunks.extend([np.nan_to_num(x),np.isfinite(x).astype(float)])
  rows=np.concatenate(chunks,axis=1)
 sums=np.zeros((G,rows.shape[1]));np.add.at(sums,gidx,rows);return sums
def value(stats,d):
 if d in ['CMUMOSI','CMUMOSEI','SIMS','SIMSv2']:
  tp,tn,fp,fn=np.moveaxis(stats,-1,0);n=tp+tn+fp+fn
  return (np.divide(2*tp,2*tp+fp+fn,out=np.zeros_like(tp),where=2*tp+fp+fn>0)*(tp+fn)+np.divide(2*tn,2*tn+fp+fn,out=np.zeros_like(tn),where=2*tn+fp+fn>0)*(tn+fp))/n
 z=np.divide(stats[...,:5],stats[...,5:10],out=np.zeros_like(stats[...,:5]),where=stats[...,5:10]>0)
 if d!='OVMERDPlus':return z.mean(axis=-1)
 t=np.divide(stats[...,10:15],stats[...,15:20],out=np.zeros_like(stats[...,10:15]),where=stats[...,15:20]>0)
 return np.divide(2*z*t,z+t,out=np.zeros_like(z),where=z+t>0).mean(axis=-1)
pairs=[('A','P'),('B','A'),('C','B'),('D','B'),('E','C'),('P','E'),('C','P'),('E','D')]
summary={'means':{c:100*float(np.mean([L[d,c]['main_score'] for d in ds])) for c in conds},
 'contrasts':[],'integrity':{},'case_selection_note':'Mechanism diagnostic from already viewed tests; selection balanced by dataset/contrast/direction, not blinded validation.'}
allrecords=[]; cases=[]; classstats=[]; old_summary=[]
for d in ds:
 a=AR[d,'A'];names=a['names']
 used=[n for i,n in enumerate(names) if 'valid' not in a or a['valid'][i]]
 groups=sorted({cluster(d,n) for n in used});gi={g:i for i,g in enumerate(groups)};gidx=np.array([gi[cluster(d,n)] for n in used]);G=len(groups)
 rng=np.random.default_rng(20261028+int(hashlib.sha256(d.encode()).hexdigest()[:6],16))
 w=rng.multinomial(G,np.full(G,1/G),size=2000)
 boot={}
 for c in conds:
  stats=sufficient(AR[d,c],d,used,gidx,G)
  observed=float(value(stats.sum(axis=0),d));assert abs(observed-L[d,c]['main_score'])<1e-9,(d,c,observed,L[d,c]['main_score'])
  boot[c]=value(w@stats,d)
 recs=[]
 for i,n in enumerate(names):
  row=ROWS[d][n];sid=row['sample_id'];pr=PREDS[d,'P'][n]
  z={'dataset':d,'name':n,'reference':h['refs'][d][n],'subtitle':row['subtitle'],'chinese':row.get('text',{}).get('chinese',''),'gate_level':pr['prompt_info']['evidence_level'],'gate_reasons':pr['prompt_info']['gate_reasons'],'paths':pr['prompt_info']['displayed_paths'],'responses':{},'opens':{},'quality':{},'prompt_ids':{},'evidence':{}}
  pc=json.loads((RUN/'prompt_cache'/(h['hashlib'].sha256(json.dumps(sid,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()+'.json')).read_text()) if False else None
  for c in conds:
   ar=AR[d,c];z['responses'][c]=RAW[d,c][n];z['opens'][c]=ar['opens'][n];z['prompt_ids'][c]=PREDS[d,c][n]['prompt_info']['prompt_id']
   if 'all_y' in ar:
    z.setdefault('sentiment',{})[c]=int(ar['all_z'][i]);z['quality'][c]=None if ar['all_y'][i]==0 else float((ar['all_y'][i]>0)==(ar['all_z'][i]>0))
   else:
    with warnings.catch_warnings():
     warnings.simplefilter('ignore',RuntimeWarning)
     z['quality'][c]=float(np.nanmean(ar['hit'][i])) if d!='OVMERDPlus' else float(np.nanmean(ar['prec'][i]+ar['rec'][i])/2)
  z['quality']=safe(z['quality'])
  if (d,n) in prior:
   z['prior_group']=prior[d,n].get('group');z['historical_response']=prior[d,n].get('winner_response')
  recs.append(z)
 allrecords.extend(recs)
 for c,b in pairs:
  active=[r for r in recs if r['prompt_ids'][c]!=r['prompt_ids'][b]]
  valid=[r for r in recs if r['quality'][c] is not None and r['quality'][b] is not None]
  up=[r for r in valid if r['quality'][c]-r['quality'][b]>1e-12]
  down=[r for r in valid if r['quality'][c]-r['quality'][b]<-1e-12]
  same=[r for r in recs if r['prompt_ids'][c]==r['prompt_ids'][b]]
  violations=[r['name'] for r in same if r['responses'][c]!=r['responses'][b] or r['opens'][c]!=r['opens'][b]]
  assert not violations,(d,c,b,violations[:5])
  ci=np.percentile(100*(boot[c]-boot[b]),[2.5,97.5]).tolist()
  out={'dataset':d,'condition':c,'reference':b,'delta_pp':100*(L[d,c]['main_score']-L[d,b]['main_score']),'bootstrap95_pp':ci,'resampling':'source-video/dialogue cluster' if d not in ['MER2023','MER2024','OVMERDPlus'] else 'sample iid; source groups unavailable','clusters':G,'evaluated_samples':len(used),'prompt_changed_samples':len(active),'improved':len(up),'worsened':len(down),'unchanged':len(valid)-len(up)-len(down),'identical_prompt_violations':len(violations)}
  summary['contrasts'].append(out)
  if (c,b) in [('C','B'),('E','C'),('P','E'),('A','P'),('C','P')]:
   for direction,items in [('improved',up),('worsened',down)]:
    # Fixed id ordering, up to 2 examples per cell; larger reading pool in all_samples.
    items=sorted(items,key=lambda r:r['name'])
    for v in items[:2]:cases.append(dict(v,contrast=c+'-'+b,direction=direction,delta_quality=v['quality'][c]-v['quality'][b]))
 if 'y' not in a and d!='OVMERDPlus':
  for label in sorted(set(h['refs'][d].values())):
   ids=[i for i,n in enumerate(names) if h['refs'][d][n]==label]
   with warnings.catch_warnings():
    warnings.simplefilter('ignore',RuntimeWarning)
    classstats.append({'dataset':d,'class':label,'n':len(ids),'HIT':{c:100*float(np.nanmean(AR[d,c]['hit'][ids])) for c in conds},'M':{c:100*float(np.nanmean(AR[d,c]['m'][ids])) for c in conds}})
 for group in sorted({r.get('prior_group') for r in recs if r.get('prior_group')}):
  sub=[r for r in recs if r.get('prior_group')==group]
  old_summary.append({'dataset':d,'prior_group':group,'n':len(sub),'mean_quality':{c:float(np.mean([r['quality'][c] for r in sub if r['quality'][c] is not None])) for c in conds}})
 print('analyzed',d,'clusters',G,flush=True)
# Add exact evidence text for the case reading pool using sample_id index.
needed={(x['dataset'],x['name']) for x in cases}
pcindex={}
for f in (RUN/'prompt_cache').glob('*.json'):
 v=json.loads(f.read_text());d,n=v['sample_id'].split('::',1)
 if (d,n) in needed:pcindex[d,n]=v
for x in cases:
 x['evidence']=pcindex[x['dataset'],x['name']]['texts']
summary['integrity']={'jobs':len(scores),'job_states':dict(collections.Counter(json.loads(f.read_text())['state'] for f in (RUN/'jobs').glob('*.json'))),'barrier':json.loads((RUN/'evaluation_barrier.json').read_text()),'final_verification':json.loads((RUN/'final_verification.json').read_text()),'main_metric_recomputed_all54':True,'identical_prompt_violations':0,'status_counters_note':'status.json retains stale progress counters (53/54 inference and partial judge counts); all job manifests, final outputs and recomputed metrics establish completion.'}
summary['mean_contrasts']={}
for c,b in pairs:
 v=[r for r in summary['contrasts'] if r['condition']==c and r['reference']==b]
 summary['mean_contrasts'][c+'-'+b]={'delta_pp':float(np.mean([x['delta_pp'] for x in v])),'positive_datasets':sum(x['delta_pp']>0 for x in v),'negative_datasets':sum(x['delta_pp']<0 for x in v),'improved':sum(x['improved'] for x in v),'worsened':sum(x['worsened'] for x in v),'prompt_changed':sum(x['prompt_changed_samples'] for x in v)}
jsonwrite('summary.json',summary);jsonwrite('class_effects.json',classstats);jsonwrite('prior_case_effects.json',old_summary);jsonwrite('case_reading_pool.json',cases)
with (OUT/'all_samples.jsonl').open('w') as f:
 for x in allrecords:f.write(json.dumps(safe(x),ensure_ascii=False,allow_nan=False)+'\n')
lines=['# 第一轮结果复核与案例池','','A 无证据；B Cue；C Cue+Appraisal；D Cue+Emotion；E Cue+Appraisal+Emotion无路径；P原完整提示。','',
'全部54项指标已独立重算匹配。区间使用2000次配对重采样；可从名称识别来源时按视频/对话聚类，其余样本iid。区间只反映本次固定生成和裁判输出的样本不确定性，不覆盖多种子、训练或裁判变化。','',
'|条件|九集均值%|','|---|---:|']
lines += ['|'+c+'|'+format(summary['means'][c],'.4f')+'|' for c in conds]
lines += ['','|集|对照|差值pp|95%区间|改善/变差|实际改变提示|','|---|---|---:|---|---|---:|']
for x in summary['contrasts']:
 lines.append('|'+x['dataset']+'|'+x['condition']+'-'+x['reference']+'|'+format(x['delta_pp'],'.3f')+'|'+', '.join(format(a,'.3f') for a in x['bootstrap95_pp'])+'|'+str(x['improved'])+'/'+str(x['worsened'])+'|'+str(x['prompt_changed_samples'])+'|')
(OUT/'STATISTICS.md').write_text('\n'.join(lines)+'\n')
print('DONE',str(OUT), 'cases',len(cases),flush=True)


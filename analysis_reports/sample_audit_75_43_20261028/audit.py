
from pathlib import Path
import os,json,collections,hashlib,warnings
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OPENBLAS_NUM_THREADS']='1'
warnings.filterwarnings('ignore',category=RuntimeWarning)
exec(compile((Path(__file__).parent/'common.py').read_text(),'common.py','exec'))
OUT=Path(__file__).parent
result={};selected=[]
def py(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,set):return sorted(x)
 raise TypeError(type(x).__name__)
def quality(a,d):
 if 'y' in a:
  q=np.full(len(a['names']),np.nan);q[a['valid']]=(a['y']==a['z']);return q
 if d!='OVMERDPlus':return np.nanmean(a['hit'],axis=1)
 f=np.divide(2*a['prec']*a['rec'],a['prec']+a['rec'],out=np.zeros_like(a['prec']),where=(a['prec']+a['rec'])>0);f[~np.isfinite(a['prec'])]=np.nan;return np.nanmean(f,axis=1)
for d in D:
 ss=sorted([s for s in scores if s['dataset']==d],key=lambda s:(s['base_epoch'],s['epoch']))
 win=max(ss,key=lambda s:s['main_score']);cur=arrays(win['raw_path'],d);names=cur['names'];N=len(names);cq=quality(cur,d)
 old=read(ROOT/f'AffectGPT/output/evaluation_20261016_2140/metrics/face/epoch_{win["base_epoch"]}_{d}.json')
 base=arrays(old['raw_path'],d);bq=quality(base,d);data={x['name']:x for x in read(p['datasets'][d]['path'])}
 rawcur=npdict(win['raw_path']);rawbase=npdict(old['raw_path'])
 pred={x['name']:x for x in (json.loads(l) for l in open(read(R/'jobs'/(win['job_id']+'.json'))['prediction_path']))}
 qs=[];binary_votes=[]
 for s in ss:
  a=arrays(s['raw_path'],d);qs.append(quality(a,d))
  if 'y' in a:binary_votes.append(a['all_z']>0)
 Q=np.array(qs)
 valid=np.isfinite(cq);fail=valid&(cq<1e-12);perfect=valid&(cq>1-1e-12)
 groups={'both_fail':fail&(bq<1e-12),'both_perfect':perfect&(bq>1-1e-12),'corrected':valid&(cq>bq+1e-12),'harmed':valid&(cq<bq-1e-12)}
 st=dict(winner=win['job_id'],metric=100*win['main_score'],n=N,scored=int(valid.sum()),winner_zero=int(fail.sum()),winner_perfect=int(perfect.sum()),winner_partial=int((valid&~fail&~perfect).sum()),
         groups={k:int(v.sum()) for k,v in groups.items()},persistent_zero_all50=int((valid&np.all(Q<1e-12,axis=0)).sum()),perfect_all50=int((valid&np.all(Q>1-1e-12,axis=0)).sum()),winner_zero_rescued_other=int((fail&np.any(Q>0,axis=0)).sum()),mean_quality_over50=np.nanmean(Q,axis=0).tolist())
 if 'y' in cur:
  y=cur['all_y'];z=cur['all_z'];st['strength']={}
  for lo,hi in [(0,.5),(.5,1),(1,4)]:
   mask=valid&(abs(y)>lo)&(abs(y)<=hi);st['strength'][str((lo,hi))]=dict(n=int(mask.sum()),errors=int((mask&fail).sum()),error_rate=float(fail[mask].mean()))
  st['errors_by_judge']=dict(collections.Counter(npdict(Path(win['raw_path']).with_name('name2reason-openset-sentiment.npz'),None)[n] for i,n in enumerate(names) if fail[i]))
  V=np.array(binary_votes);majority=(V.sum(axis=0)>25)
  st['majority50_WAF']=100*float(waf(y[valid]>0,majority[valid]));st['winner_errors_majority_correct']=int((fail&(majority==(y>0))).sum())
  st['pos_errors']=int((fail&(y>0)).sum());st['neg_errors']=int((fail&(y<0)).sum())
 else:
  if d!='OVMERDPlus':
   st['class_failures']={c:dict(n=sum(refs[d][n]==c for n in names),scored=int((valid&np.array([refs[d][n]==c for n in names])).sum()),zero=int((fail&np.array([refs[d][n]==c for n in names])).sum()),hit=100*float(np.nanmean(cur['hit'][[refs[d][n]==c for n in names]]))) for c in sorted(set(refs[d].values()))}
   st['miss_predicted_wheel0']=dict(collections.Counter(z for i,n in enumerate(names) if fail[i] for z in mapped(cur['opens'][n],0)).most_common(20))
 st['gate']={}
 for level in [0,1,2,3]:
  mask=np.array([pred[n]['prompt_info']['evidence_level']==level for n in names])&valid
  st['gate'][level]=dict(n=int(mask.sum()),zero=int((mask&fail).sum()),mean_quality=float(np.nanmean(cq[mask])) if mask.any() else None)
 result[d]=st
 # Two examples per stratum, diversify truth and output. Fixed hash order avoids editorial selection.
 for group,mask in groups.items():
  candidates=np.where(mask)[0].tolist();candidates.sort(key=lambda i:hashlib.sha256((d+group+names[i]).encode()).hexdigest())
  chosen=[];seen=set()
  for i in candidates:
   category=str(refs[d][names[i]]) if 'y' not in cur else str(refs[d][names[i]]>0)
   if category not in seen:chosen.append(i);seen.add(category)
   if len(chosen)>=2:break
  for i in candidates:
   if len(chosen)>=2:break
   if i not in chosen:chosen.append(i)
  for i in chosen:
   n=names[i];selected.append(dict(dataset=d,name=n,group=group,reference=refs[d][n],winner_job=win['job_id'],base_epoch=win['base_epoch'],base_quality=float(bq[i]),winner_quality=float(cq[i]),mean_quality50=float(np.nanmean(Q[:,i])),zero_count50=int((Q[:,i]<1e-12).sum()),perfect_count50=int((Q[:,i]>1-1e-12).sum()),subtitle=data[n]['subtitle'],chinese=data[n]['text'].get('chinese',''),base_response=rawbase[n],winner_response=rawcur[n],base_opens=base['opens'][n],winner_opens=cur['opens'][n],prompt_info=pred[n]['prompt_info'],media={k:data[n][k] for k in ['video_path','audio_path','face_path']}))
 # Per-sample table with all50 quality, references and winner/base answers, no predictions changed.
 with (OUT/(d+'_all_samples.jsonl')).open('w') as f:
  for i,n in enumerate(names):
   f.write(json.dumps(dict(name=n,reference=refs[d][n],winner_quality=cq[i],base_quality=bq[i],quality50=Q[:,i],winner_response=rawcur[n],base_response=rawbase[n]),ensure_ascii=False,default=py,allow_nan=True)+'\n')
 (OUT/'statistics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=py))
 (OUT/'selected_cases.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2,default=py))
 print(d,json.dumps({k:v for k,v in st.items() if k!='mean_quality_over50'},ensure_ascii=False,default=py),flush=True)
 cache.clear()
print('SELECTED',len(selected),'GPU_IMPORTS',any(k in sys.modules for k in ['torch','vllm']),flush=True)

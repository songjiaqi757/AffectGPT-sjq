from graph_paths import resolve_path as _graph_resolve_path
from graph_paths import Path as _GraphPath
import os,sys,json,pathlib,ast,runpy,glob,re,csv,collections,statistics,zipfile,pickle,types,contextlib,io,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,pandas as pd
ROOT=_GraphPath('/ai/sjq/AffectGPT-sjq/graph'); A=ROOT/'AffectGPT';R=ROOT/'amg_d_multistart10/runs/d_multistart10_20261025_160152'
os.chdir(_graph_resolve_path(A));config=types.SimpleNamespace(**runpy.run_path(str(A/'config.py')))
ns=dict(np=np,pd=pd,re=re,os=os,glob=glob,config=config)
for f in ['toolkit/utils/functions.py','toolkit/utils/read_files.py','my_affectgpt/evaluation/wheel.py']:
 tree=ast.parse((A/f).read_text())
 exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and (f.endswith('wheel.py') or x.name in ['string_to_list','func_read_key_from_csv'])],type_ignores=[]),f,'exec'),ns)
with contextlib.redirect_stdout(io.StringIO()):
 fm=ns['read_format2raws']();rm=ns['read_candidate_synonym_merge']()
wheels=[ns['func_get_wheel_cluster']('wheel'+str(i),'level1') for i in range(1,6)]
split=ns['string_to_list'];mapcache={}
def mapped(s,w):
 key=(str(s),w)
 if key not in mapcache:
  mapcache[key]=set(ns['func_map_label_to_synonym']([x.strip().lower() for x in split(s)],fm,rm,wheels[w],'case3_wheel'+str(w+1)+'_level1'))
 return mapcache[key]
def read(p):return json.loads(_GraphPath(p).read_text())
p=read(R/'plan.json');D=list(p['datasets']);scores=[read(f) for f in (R/'scores').glob('*.json')]
def npdict(path,key='name2reason'):
 x=np.load(_graph_resolve_path(path), allow_pickle=True)
 return x[key].item() if key in x else dict(zip(x['filenames'].tolist(),x['fileitems'].tolist()))
def corpus(path,key):return np.load(_graph_resolve_path(path), allow_pickle=True)[key].item()
def truth(d):
 names=[x['name'] for x in read(p['datasets'][d]['path'])]
 path=(A/config.PATH_TO_LABEL[d]).resolve()
 if d=='OVMERDPlus':
  with path.open() as f:tab={x['name']:x['openset'] for x in csv.DictReader(f)}
  return {n:', '.join(split(tab[n]) or ['neutral']) for n in names}
 key='test1_corpus' if d in ['MER2023','MER2024'] else 'whole_corpus' if d=='IEMOCAPFour' else 'test_corpus'
 c=corpus(path,key)
 if d in ['CMUMOSI','CMUMOSEI','SIMS','SIMSv2']:return {n:float(c[n]['val']) for n in names}
 enums={'MELD':['anger','joy','sadness','neutral','disgust','fear','surprise'],'IEMOCAPFour':['happy','sad','neutral','anger']}
 return {n:c[n]['emo'] if isinstance(c[n]['emo'],str) else enums[d][int(c[n]['emo'])] for n in names}
refs={d:truth(d) for d in D};cache={}
def arrays(raw,d):
 k=(str(raw),d)
 if k in cache:return cache[k]
 raw=_GraphPath(raw);gt=refs[d];names=list(gt)
 opens=npdict(raw.with_name(raw.stem+'-openset.npz'),None)
 if d in ['CMUMOSI','CMUMOSEI','SIMS','SIMSv2']:
  sent=npdict(raw.with_name(raw.stem+'-openset-sentiment.npz'),None)
  y=np.array([gt[n] for n in names]);z=np.array([1 if sent[n]=='positive' else -1 if sent[n]=='negative' else 0 for n in names]);valid=y!=0
  result=dict(names=names,y=y[valid]>0,z=z[valid]>0,all_y=y,all_z=z,valid=valid,sent=dict(collections.Counter(sent.values())),opens=opens)
 else:
  hit=np.full((len(names),5),np.nan);m=hit.copy();prec=hit.copy();rec=hit.copy();sizes=np.zeros_like(hit)
  for w in range(5):
   candidates=set().union(*(mapped(v,w) for v in set(gt.values()))) if d!='OVMERDPlus' else set()
   for i,n in enumerate(names):
    g=mapped(gt[n],w);z=mapped(opens[n],w);sizes[i,w]=len(z)
    if not g:continue
    h=len(g&z);hit[i,w]=h;m[i,w]=h/len(z&candidates) if z&candidates else 0
    prec[i,w]=h/len(z) if z else 0;rec[i,w]=h/len(g)
  result=dict(names=names,hit=hit,m=m,prec=prec,rec=rec,sizes=sizes,opens=opens)
 cache[k]=result;return result
def waf(y,z):
 tp=np.sum(y&z,axis=-1);tn=np.sum(~y&~z,axis=-1);fp=np.sum(~y&z,axis=-1);fn=np.sum(y&~z,axis=-1)
 return (np.divide(2*tp,2*tp+fp+fn,out=np.zeros_like(tp,dtype=float),where=(2*tp+fp+fn)>0)*(tp+fn)+np.divide(2*tn,2*tn+fp+fn,out=np.zeros_like(tp,dtype=float),where=(2*tn+fp+fn)>0)*(tn+fp))/(tp+tn+fp+fn)
def metric(a,d,ix=None,key=None):
 if 'y' in a:
  y=a['y'] if ix is None else a['y'][ix];z=a['z'] if ix is None else a['z'][ix]
  return waf(y,z)
 if key is None:key='F_s' if d=='OVMERDPlus' else 'hit'
 if key=='F_s':
  pre=np.nanmean(a['prec'] if ix is None else a['prec'][ix],axis=-2);rec=np.nanmean(a['rec'] if ix is None else a['rec'][ix],axis=-2)
  return np.mean(np.divide(2*pre*rec,pre+rec,out=np.zeros_like(pre),where=pre+rec>0),axis=-1)
 return np.nanmean(np.nanmean(a[key] if ix is None else a[key][ix],axis=-2),axis=-1)
def compare(a,b,d):
 va=metric(a,d);vb=metric(b,d);N=len(a['y']) if 'y' in a else len(a['names'])
 rng=np.random.default_rng(20261027);boots=[]
 for _ in range(20):
  ix=rng.integers(0,N,size=(100,N));boots.extend((metric(b,d,ix)-metric(a,d,ix)).tolist())
 out=dict(original=100*float(va),current=100*float(vb),difference=100*float(vb-va),paired_bootstrap95=(100*np.percentile(boots,[2.5,97.5])).tolist(),bootstrap_samples=N)
 if 'y' in a:
  old=a['y']==a['z'];new=b['y']==b['z'];gt=a['y'];pr=b['z']
  out.update(corrected=int(np.sum(~old&new)),harmed=int(np.sum(old&~new)),predicted_sentiment=b['sent'],confusion=dict(TP=int(np.sum(gt&pr)),TN=int(np.sum(~gt&~pr)),FP=int(np.sum(~gt&pr)),FN=int(np.sum(gt&~pr))),original_sentiment=a['sent'],positive_recall=float(np.mean(pr[gt])),negative_recall=float(np.mean(~pr[~gt])))
 else:
  dif=np.nanmean(b['hit']-a['hit'],axis=1) if d!='OVMERDPlus' else np.nanmean(b['prec']+b['rec']-a['prec']-a['rec'],axis=1)
  out.update(improved_samples=int(np.sum(dif>1e-12)),worsened_samples=int(np.sum(dif< -1e-12)),old_pred_labels=float(a['sizes'].mean()),new_pred_labels=float(b['sizes'].mean()))
  if d!='OVMERDPlus':
   out.update(old_M=100*float(metric(a,d,key='m')),new_M=100*float(metric(b,d,key='m')),per_class={c:dict(n=sum(refs[d][n]==c for n in a['names']),old_hit=100*float(np.nanmean(a['hit'][[refs[d][n]==c for n in a['names']]])),new_hit=100*float(np.nanmean(b['hit'][[refs[d][n]==c for n in a['names']]]))) for c in set(refs[d].values())})
  else:out.update(old_P=100*float(np.nanmean(a['prec'],axis=0).mean()),new_P=100*float(np.nanmean(b['prec'],axis=0).mean()),old_R=100*float(np.nanmean(a['rec'],axis=0).mean()),new_R=100*float(np.nanmean(b['rec'],axis=0).mean()))
 return out

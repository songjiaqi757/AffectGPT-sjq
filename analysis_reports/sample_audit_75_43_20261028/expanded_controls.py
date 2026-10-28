
from pathlib import Path
import os,json,warnings,collections
os.environ['CUDA_VISIBLE_DEVICES']='';warnings.filterwarnings('ignore',category=RuntimeWarning)
OUT=Path(__file__).resolve().parent
exec(compile((OUT/'common.py').read_text(),'common.py','exec'))
xs=read(OUT/'expanded_cases.json')
long=[read(f) for f in (ROOT/'amg_inference/runs/graph_225_20261022_174537/evaluation_all_20261023_175630/scores').glob('*.json')]
def qual(a,d):
 if 'y' in a:
  q=np.full(len(a['names']),np.nan);q[a['valid']]=(a['y']==a['z']);return q
 if d!='OVMERDPlus':return np.nanmean(a['hit'],axis=1)
 f=np.divide(2*a['prec']*a['rec'],a['prec']+a['rec'],out=np.zeros_like(a['prec']),where=(a['prec']+a['rec'])>0);f[~np.isfinite(a['prec'])]=np.nan;return np.nanmean(f,axis=1)
neutral={};sources={}
for d in D:
 orig=[read(f) for f in (ROOT/'AffectGPT/output/evaluation_20261016_2140/metrics/face').glob('*_'+d+'.json')]
 controls=[('original_dataset_best',max(orig,key=lambda z:z['main_score'])),('long_graph_dataset_best',max([z for z in long if z['dataset']==d],key=lambda z:z['main_score']))]
 for tag,z in controls:
  a=arrays(z['raw_path'],d);q=qual(a,d);ix={n:i for i,n in enumerate(a['names'])};raw=npdict(z['raw_path']);sources[d+'::'+tag]=z
  for x in [x for x in xs if x['dataset']==d]:
   i=ix[x['name']];x.setdefault('historical_controls',{})[tag]=dict(epoch=z.get('epoch'),base_epoch=z.get('base_epoch'),main_score=z['main_score'],quality=float(q[i]) if np.isfinite(q[i]) else None,response=raw[x['name']],opens=a['opens'][x['name']])
 if d in ['MER2023','MER2024','MELD','IEMOCAPFour']:
  win=max([z for z in scores if z['dataset']==d],key=lambda z:z['main_score']);a=arrays(win['raw_path'],d);ns0=[n for n in a['names'] if refs[d][n]=='neutral'];raw=npdict(win['raw_path'])
  neutral[d]=dict(n=len(ns0),raw_contains_neutral=sum('neutral' in raw[n].lower() for n in ns0),opens_empty=sum(not split(a['opens'][n]) for n in ns0),opens_any_wheel=sum(any(mapped(a['opens'][n],w) for w in range(5)) for n in ns0),note='Diagnostic outputs for neutral GT, not official HIT errors; calm may map into happy in some wheels.')
 cache.clear()
(OUT/'expanded_cases.json').write_text(json.dumps(xs,ensure_ascii=False,indent=2))
(OUT/'expanded_historical_sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
(OUT/'expanded_neutral_audit.json').write_text(json.dumps(neutral,ensure_ascii=False,indent=2))
for x in xs:
 if x['group']=='persistent_error':
  print(x['dataset'],x['name'],'GT',x['reference'],'ORIGINAL_BEST',x['historical_controls']['original_dataset_best'],'LONG_BEST',x['historical_controls']['long_graph_dataset_best'],flush=True)
print('NEUTRAL',json.dumps(neutral,ensure_ascii=False),flush=True)

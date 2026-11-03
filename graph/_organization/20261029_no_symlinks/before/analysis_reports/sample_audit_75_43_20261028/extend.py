
from pathlib import Path
import os,json,collections,re,warnings,hashlib
os.environ['CUDA_VISIBLE_DEVICES']='';warnings.filterwarnings('ignore',category=RuntimeWarning)
exec(compile((Path(__file__).parent/'common.py').read_text(),'common.py','exec'))
OUT=Path(__file__).parent
cases=read(OUT/'selected_cases.json');stats=read(OUT/'statistics.json');cross={}
def quality(a,d):
 if 'y' in a:
  q=np.full(len(a['names']),np.nan);q[a['valid']]=(a['y']==a['z']);return q
 if d!='OVMERDPlus':return np.nanmean(a['hit'],axis=1)
 f=np.divide(2*a['prec']*a['rec'],a['prec']+a['rec'],out=np.zeros_like(a['prec']),where=(a['prec']+a['rec'])>0);f[~np.isfinite(a['prec'])]=np.nan;return np.nanmean(f,axis=1)
abls=[]
for rr in [ROOT/'amg_prompt_ablation/runs/prompt_ablation_20261027_215553',ROOT/'amg_prompt_ablation_g/runs/g_soft_appraisal_20261028_002141']:
 for sfile in (rr/'scores').glob('*.json'):
  s=read(sfile);s['run']=str(rr);abls.append(s)
for d in D:
 ss=[s for s in scores if s['dataset']==d];win=max(ss,key=lambda s:s['main_score'])
 a=arrays(win['raw_path'],d);names=a['names'];raw=npdict(win['raw_path']);opens=a['opens']
 data={v['name']:v for v in read(p['datasets'][d]['path'])}
 rows=[json.loads(l) for l in open(OUT/(d+'_all_samples.jsonl'))]
 persistent=collections.Counter(str(x['reference']) for x in rows if all(v<1e-12 for v in x['quality50']))
 if d in ['CMUMOSI','CMUMOSEI','SIMS','SIMSv2']:
  persistent=collections.Counter('positive' if x['reference']>0 else 'negative' for x in rows if x['reference']!=0 and all(v<1e-12 for v in x['quality50']))
 stats[d]['persistent_by_class']=dict(persistent)
 # literal GT family found in raw output but omitted from extracted set: diagnostic only.
 patterns={'happy':r'\b(?:happy|happiness|joy|joyful)\b','joy':r'\b(?:happy|happiness|joy|joyful)\b','angry':r'\b(?:anger|angry)\b','anger':r'\b(?:anger|angry)\b','sad':r'\b(?:sad|sadness)\b','sadness':r'\b(?:sad|sadness)\b','surprise':r'\b(?:surprise|surprised|surprising)\b','fear':r'\b(?:fear|afraid|scared)\b','disgust':r'\b(?:disgust|disgusted)\b','worried':r'\b(?:worried|worry|anxious|anxiety)\b'}
 lost=[]
 for n in names:
  gt=refs[d][n];pat=patterns.get(str(gt))
  if pat and re.search(pat,raw[n],re.I) and not re.search(pat,str(opens[n]),re.I):lost.append(dict(name=n,gt=gt,raw=raw[n],opens=opens[n]))
 stats[d]['literal_gt_family_omission']=lost
 # English short context observational slice.
 if d not in ['MER2024','SIMS','SIMSv2']:
  q=quality(a,d)
  stats[d]['subtitle_length']={}
  for label,lo,hi in [('0-3',0,3),('4-10',4,10),('11+',11,100000)]:
   ix=[i for i,n in enumerate(names) if lo<=len(data[n]['subtitle'].split())<=hi and np.isfinite(q[i])]
   stats[d]['subtitle_length'][label]=dict(n=len(ix),zero=sum(q[i]<1e-12 for i in ix),mean_quality=float(np.mean(q[ix])) if ix else None)
 for s in [z for z in abls if z['dataset']==d]:
  b=arrays(s['raw_path'],d);bq=quality(b,d);br=npdict(s['raw_path']);idx={n:i for i,n in enumerate(b['names'])}
  for x in [x for x in cases if x['dataset']==d]:
   n=x['name'];x.setdefault('other_experiments',{})[s['variant']]=dict(quality=float(bq[idx[n]]),response=br[n],opens=b['opens'][n])
 if d in ['MER2023','SIMS','OVMERDPlus']:
  q=quality(a,d);sub={}
  for s in [z for z in abls if z['dataset']==d]:
   bq=quality(arrays(s['raw_path'],d),d);mask=np.isfinite(q)&np.isfinite(bq)
   sub[s['variant']]=dict(winner_zero_with_other_nonzero=int(((q<1e-12)&(bq>1e-12)&mask).sum()),winner_perfect_other_zero=int(((q>1-1e-12)&(bq<1e-12)&mask).sum()))
  cross[d]=sub
 cache.clear()
(OUT/'statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2,default=lambda v:v.item()))
(OUT/'selected_cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
(OUT/'cross_experiment_statistics.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2))
for d in D:print(d,json.dumps({k:stats[d].get(k) for k in ['persistent_by_class','subtitle_length','literal_gt_family_omission']},ensure_ascii=False,default=lambda v:v.item()),flush=True)
print('CROSS',json.dumps(cross,ensure_ascii=False),flush=True)

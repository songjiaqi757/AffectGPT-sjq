from graph_paths import resolve_path as _graph_resolve_path

from graph_paths import Path
import os,json,hashlib,collections,warnings
os.environ['CUDA_VISIBLE_DEVICES']='';warnings.filterwarnings('ignore',category=RuntimeWarning)
OUT=Path(__file__).resolve().parent
exec(compile((OUT/'common.py').read_text(),'common.py','exec'))
old=read(OUT/'selected_cases.json');exclude={(x['dataset'],x['name']) for x in old}
new=[];selection_counts={}
abl=[]
for rr in [ROOT/'amg_prompt_ablation/runs/prompt_ablation_20261027_215553',ROOT/'amg_prompt_ablation_g/runs/g_soft_appraisal_20261028_002141']:
 abl.extend(read(f) for f in (rr/'scores').glob('*.json'))
def qual(a,d):
 if 'y' in a:
  q=np.full(len(a['names']),np.nan);q[a['valid']]=(a['y']==a['z']);return q
 if d!='OVMERDPlus':return np.nanmean(a['hit'],axis=1)
 f=np.divide(2*a['prec']*a['rec'],a['prec']+a['rec'],out=np.zeros_like(a['prec']),where=(a['prec']+a['rec'])>0);f[~np.isfinite(a['prec'])]=np.nan;return np.nanmean(f,axis=1)
if '--resume' in sys.argv:
 new=read(OUT/'expanded_cases.json');selection_counts=dict(collections.Counter(x['dataset']+'::'+x['group'] for x in new));exclude.update((x['dataset'],x['name']) for x in new)
done_datasets={x['dataset'] for x in new}
for d in D:
 if d in done_datasets:continue
 rows=[json.loads(l) for l in open(_graph_resolve_path(OUT / (d + '_all_samples.jsonl')))]
 win=max([z for z in scores if z['dataset']==d],key=lambda z:z['main_score']);base_epoch=win['base_epoch']
 items={v['name']:v for v in read(p['datasets'][d]['path'])}
 preds={v['name']:v for v in (json.loads(l) for l in open(_graph_resolve_path(read(R / 'jobs' / (win['job_id'] + '.json'))['prediction_path'])))}
 valid=[v for v in rows if np.isfinite(v['winner_quality']) and (d,v['name']) not in exclude]
 tests={
  'persistent_error':lambda v:all(z<1e-12 for z in v['quality50']),
  'stable_correct':lambda v:all(z>1-1e-12 for z in v['quality50']),
  'winner_miss_others_often_correct':lambda v:v['winner_quality']<1e-12 and np.nanmean(v['quality50'])>=.5,
  'winner_correct_others_often_wrong':lambda v:v['winner_quality']>1-1e-12 and np.nanmean(v['quality50'])<=.5,
  'improved_vs_start':lambda v:v['winner_quality']>v['base_quality']+1e-12,
  'harmed_vs_start':lambda v:v['winner_quality']<v['base_quality']-1e-12}
 chosen=[]
 for group,fn in tests.items():
  pool=[v for v in valid if fn(v) and (d,v['name']) not in exclude]
  pool.sort(key=lambda v:hashlib.sha256(('expanded-v2'+d+group+v['name']).encode()).hexdigest())
  selected=[];seen=set()
  for v in pool:
   gt=v['reference'];cat=str(gt) if isinstance(gt,str) else ('pos' if gt>0 else 'neg')+('weak' if abs(gt)<=.5 else 'strong')
   if cat in seen:continue
   selected.append(v);seen.add(cat)
   if len(selected)==3:break
  for v in pool:
   if len(selected)==3:break
   if v not in selected:selected.append(v)
  selection_counts[d+'::'+group]=len(selected)
  for v in selected:
   n=v['name'];exclude.add((d,n));row=items[n];pred=preds[n];Q=v['quality50']
   sid=d+'::'+n;h=hashlib.sha256(json.dumps(sid,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
   cp=ROOT/'amg_inference/runs/graph_225_20261022_174537/cache'/(h+'.json');e=read(cp)['evidence']
   x=dict(dataset=d,name=n,group=group,reference=v['reference'],winner_job=win['job_id'],base_epoch=base_epoch,base_quality=v['base_quality'],winner_quality=v['winner_quality'],mean_quality50=float(np.nanmean(Q)),zero_count50=sum(z<1e-12 for z in Q),perfect_count50=sum(z>1-1e-12 for z in Q),subtitle=row['subtitle'],chinese=row['text'].get('chinese',''),base_response=v['base_response'],winner_response=v['winner_response'],prompt_info=pred['prompt_info'],media={k:row[k] for k in ['video_path','audio_path','face_path']},cues=[z['cue_id'] for z in e['query_cues']],emotions=[z['canonical_name'] for z in e['emotion_candidates']],appraisals={z['dimension_id']:[{'state':a['state_id'],'relative_support':a['relative_support']} for a in z['display_candidates']] for z in e['appraisal_dimensions']})
   chosen.append(x)
 # Additional neutral controls: official HIT leaves them unscored.
 if d in ['MER2023','MER2024','MELD','IEMOCAPFour']:
  pool=[v for v in rows if str(v['reference'])=='neutral' and (d,v['name']) not in exclude]
  pool.sort(key=lambda v:hashlib.sha256(('neutral-v2'+d+v['name']).encode()).hexdigest())
  for v in pool[:2]:
   n=v['name'];row=items[n];chosen.append(dict(dataset=d,name=n,group='neutral_unscored_control',reference='neutral',winner_job=win['job_id'],base_epoch=base_epoch,base_quality=None,winner_quality=None,mean_quality50=None,zero_count50=None,perfect_count50=None,subtitle=row['subtitle'],chinese=row['text'].get('chinese',''),base_response=v['base_response'],winner_response=v['winner_response'],prompt_info=preds[n]['prompt_info'],media={k:row[k] for k in ['video_path','audio_path','face_path']}))
  selection_counts[d+'::neutral_unscored_control']=min(2,len(pool))
 cur=arrays(win['raw_path'],d)
 oldscore=read(ROOT/f'AffectGPT/output/evaluation_20261016_2140/metrics/face/epoch_{base_epoch}_{d}.json')
 base=arrays(oldscore['raw_path'],d)
 for x in chosen:
  n=x['name'];x['winner_opens']=cur['opens'][n];x['base_opens']=base['opens'][n]
  x['mapping']={str(w+1):dict(reference=sorted(mapped(str(refs[d][n]),w)),winner=sorted(mapped(cur['opens'][n],w))) for w in range(5)} if d=='OVMERDPlus' else {}
  if 'y' in cur:
   x['winner_sentiment']=npdict(Path(win['raw_path']).with_name('name2reason-openset-sentiment.npz'),None)[n]
   x['base_sentiment']=npdict(Path(oldscore['raw_path']).with_name(Path(oldscore['raw_path']).stem+'-openset-sentiment.npz'),None)[n]
 for z in [z for z in abl if z['dataset']==d]:
  a=arrays(z['raw_path'],d);q=qual(a,d);ix={n:i for i,n in enumerate(a['names'])};raw=npdict(z['raw_path'])
  for x in chosen:
   n=x['name'];x.setdefault('other_experiments',{})[z['variant']]=dict(quality=float(q[ix[n]]) if np.isfinite(q[ix[n]]) else None,response=raw[n],opens=a['opens'][n])
 new.extend(chosen);cache.clear()
 (OUT/'expanded_cases.json').write_text(json.dumps(new,ensure_ascii=False,indent=2))
 print('DATASET',d,len(chosen),flush=True)
(OUT/'expanded_selection.json').write_text(json.dumps(dict(counts=selection_counts,new_cases=len(new),old_cases=len(old),overlap=len({(x['dataset'],x['name']) for x in old}&{(x['dataset'],x['name']) for x in new}),selection='Fixed SHA256 within six targeted strata, diversify truth/sign-strength, exclude prior72; add2 neutral controls per discrete dataset. Exploratory, no prevalence inference.'),ensure_ascii=False,indent=2))
print('DONE',len(new),flush=True)

import pathlib,json,collections
import numpy as np
ROOT=pathlib.Path('/ai/sjq/AffectGPT-sjq');R=ROOT/'amg_d_multistart10/runs/d_multistart10_20261025_160152'
def read(p):return json.loads(pathlib.Path(p).read_text())
scores=[read(f) for f in (R/'scores').glob('*.json')];out={}
for d in ['CMUMOSI','CMUMOSEI','SIMS','SIMSv2']:
 groups=collections.defaultdict(collections.Counter);examples=collections.defaultdict(dict);n=0
 for r in scores:
  if r['dataset']!=d:continue
  raw=pathlib.Path(r['raw_path'])
  answers=np.load(raw,allow_pickle=True)['name2reason'].item()
  z=np.load(raw.with_name(raw.stem+'-openset-sentiment.npz'),allow_pickle=True);sent=dict(zip(z['filenames'].tolist(),z['fileitems'].tolist()))
  for name,answer in answers.items():
   value=sent[name];groups[answer][value]+=1;n+=1
   examples[answer].setdefault(value,dict(name=name,job_id=r['job_id']))
 repeated={s:c for s,c in groups.items() if sum(c.values())>1}
 inconsistent={s:c for s,c in repeated.items() if len(c)>1}
 flip={s:c for s,c in inconsistent.items() if c.get('positive',0)>0 and sum(v for k,v in c.items() if k!='positive')>0}
 result=dict(total_predictions=n,unique_exact_responses=len(groups),repeated_response_types=len(repeated),inconsistent_sentiment_types=len(inconsistent),binary_flip_types=len(flip),occurrences_in_binary_flip_groups=sum(sum(c.values()) for c in flip.values()),minority_binary_occurrences=sum(min(c.get('positive',0),sum(v for k,v in c.items() if k!='positive')) for c in flip.values()),examples=[dict(response=s,sentiment_counts=dict(c),provenance=examples[s]) for s,c in sorted(flip.items(),key=lambda x:-sum(x[1].values()))[:8]])
 out[d]=result;print(d,json.dumps(result,ensure_ascii=False),flush=True)
out['interpretation']='Identical full model responses with conflicting judge sentiments prove evaluator inconsistency conditional on text. Counts are sensitivity diagnostics,not true error rates or an estimate of score bias. Across jobs,different other batch requests and stochastic judge sampling may change extraction; no judge rerun performed.'
(ROOT/'analysis_reports/reanalysis_20261027_judge_consistency.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))


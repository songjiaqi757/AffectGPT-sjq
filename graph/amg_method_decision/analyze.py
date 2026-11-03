"""Paired, sample-cluster statistics and a development-frozen method decision."""
import sys,os,runpy,collections,math,json
from graph_paths import Path
ROOT=Path('/ai/sjq/AffectGPT-sjq/graph');sys.path.insert(0,str(ROOT))
from amg_method_decision.pipeline import read,dump,canonical,now,key
from amg_method_decision.generate import verify
def analyze(run,part):
 import numpy as np
 p=verify(run);e=run/'evaluation'/part;scores=read(e/'metrics.json')
 helper=runpy.run_path(str(ROOT/'analysis_reports/sample_audit_75_43_20261028/common.py'));ar=helper['arrays'];metric=helper['metric'];refs=read(e/'references.json');ar.__globals__['refs']=refs;ar.__globals__['cache']={}
 roles={'MER_track1_discrete':('MER2023','HIT'),'MER_track1_polarity':('SIMS','WAF'),'MER_OV':('OVMERDPlus','F_s')}
 arrays={};points={};rawrows={}
 for x in scores:
  role,field=roles[x['task']];a=ar(x['raw'],role);point=float(metric(a,role))
  if abs(point-x['metrics'][field])>1e-9:raise ValueError('Official/sample metric mismatch: '+str((x['job_id'],x['task'],point,x['metrics'][field])))
  arrays[x['checkpoint'],x['condition'],x['seed'],x['task']]=a
  rawrows[x['checkpoint'],x['condition'],x['seed'],x['task']]=x
 for ck in p['checkpoints']:
  for arm in p['conditions']:
   for task in roles:points[ck,arm,task]=float(np.mean([rawrows[ck,arm,s,task]['metrics'][roles[task][1]] for s in p['seeds']]))
 comparisons={}
 def pair(ck,arm,ref,refck=None):
  refck=refck or ck;id='::'.join([ck,arm,refck,ref])
  if id in comparisons:return comparisons[id]
  result=dict(checkpoint=ck,condition=arm,reference_checkpoint=refck,reference=ref,tasks={});boots={}
  for task,(role,field) in roles.items():
   aa=[arrays[ck,arm,s,task] for s in p['seeds']];bb=[arrays[refck,ref,s,task] for s in p['seeds']]
   n=len(aa[0]['y']) if role=='SIMS' else len(aa[0]['names']);rng=np.random.default_rng(int(canonical([part,task,'paired-bootstrap-v1'])[:8],16));boot=[];seed_delta=[float(metric(a,role)-metric(b,role)) for a,b in zip(aa,bb)]
   for _ in range(20):
    ix=rng.integers(0,n,size=(100,n));diff=np.mean([metric(a,role,ix)-metric(b,role,ix) for a,b in zip(aa,bb)],axis=0);boot.extend(diff.tolist())
   boot=np.array(boot);boots[task]=boot
   item=dict(unique_samples=n,delta_pp=100*float(np.mean(seed_delta)),paired_bootstrap95_pp=(100*np.percentile(boot,[2.5,97.5])).tolist(),per_seed_delta_pp=(100*np.array(seed_delta)).tolist())
   if role=='SIMS':
    item.update(corrected_across_three_seeds=int(sum(np.sum((a['y']!=b['z'])&(a['y']==a['z'])) for a,b in zip(aa,bb))),harmed_across_three_seeds=int(sum(np.sum((a['y']==b['z'])&(a['y']!=a['z'])) for a,b in zip(aa,bb))),positive_recall=float(np.mean([np.mean(a['z'][a['y']]) for a in aa])),negative_recall=float(np.mean([np.mean(~a['z'][~a['y']]) for a in aa])))
   elif role=='MER2023':
    item['per_class']={}
    for c in sorted(set(refs[role].values())):
     mask=np.array([refs[role][name]==c for name in aa[0]['names']],dtype=bool)
     def class_mean(a):
      v=a['hit'][mask];finite=v[np.isfinite(v)]
      return 100*float(finite.mean()) if finite.size else None
     values=[class_mean(a) for a in aa];oldvalues=[class_mean(a) for a in bb]
     covered=np.isfinite(aa[0]['hit'][mask])
     item['per_class'][c]=dict(n=int(mask.sum()),current_HIT=float(np.mean(values)) if all(v is not None for v in values) else None,reference_HIT=float(np.mean(oldvalues)) if all(v is not None for v in oldvalues) else None,scorable_samples=int(np.any(covered,axis=1).sum()),scorable_samples_by_wheel=covered.sum(axis=0).tolist(),status='defined' if covered.any() else 'not_defined_by_original_wheel_metric')

   result['tasks'][task]=item
  comb=(boots['MER_track1_discrete']+boots['MER_OV'])/2
  result['primary_equal_weight_HIT_OV']=dict(delta_pp=(result['tasks']['MER_track1_discrete']['delta_pp']+result['tasks']['MER_OV']['delta_pp'])/2,paired_bootstrap95_pp=(100*np.percentile(comb,[2.5,97.5])).tolist(),per_seed_delta_pp=((np.array(result['tasks']['MER_track1_discrete']['per_seed_delta_pp'])+np.array(result['tasks']['MER_OV']['per_seed_delta_pp']))/2).tolist())
  comparisons[id]=result;return result
 for ck in p['checkpoints']:
  for a,b in [('B','A'),('C','A'),('C','B'),('C','S'),('P','A'),('P','B'),('P','C')]:pair(ck,a,b)
 def positive(x):return x['primary_equal_weight_HIT_OV']['paired_bootstrap95_pp'][0]>0 and sum(v>0 for v in x['primary_equal_weight_HIT_OV']['per_seed_delta_pp'])>=2
 def guard(x):return x['tasks']['MER_track1_polarity']['delta_pp']>=-1.0
 if part=='development':
  candidates=[]
  for ck in p['checkpoints']:
   for arm in ['A','B','C','P']:
    ok=arm=='A'
    if arm in ['B','P']:ok=positive(pair(ck,arm,'A')) and guard(pair(ck,arm,'A'))
    if arm=='C':
     ok=positive(pair(ck,'C','A')) and positive(pair(ck,'C','B')) and positive(pair(ck,'C','S')) and guard(pair(ck,'C','A'))
     ok=ok and all(pair(other,'C','B')['primary_equal_weight_HIT_OV']['delta_pp']>0 and pair(other,'C','S')['primary_equal_weight_HIT_OV']['delta_pp']>0 for other in p['checkpoints'])
    candidates.append(dict(checkpoint=ck,condition=arm,eligible=bool(ok),primary_mean=(points[ck,arm,'MER_track1_discrete']+points[ck,arm,'MER_OV'])/2))
  eligible=[x for x in candidates if x['eligible']];best=max(eligible,key=lambda x:(x['primary_mean'],x['condition']=='A',x['checkpoint']=='original_epoch40'))
  if best['checkpoint']!='original_epoch40':
   cross=pair(best['checkpoint'],best['condition'],'A','original_epoch40')
   if not positive(cross) or not guard(cross):best=max((x for x in eligible if x['checkpoint']=='original_epoch40'),key=lambda x:(x['primary_mean'],x['condition']=='A'))
  frozen=dict(schema='frozen_method_before_confirmation_v1',checkpoint=best['checkpoint'],condition=best['condition'],development_candidates=candidates,rule='Equal-weight mean of discrete HIT and OV F over 3 fixed seeds; paired 95% lower bound positive, >=2/3 seed improvements, polarity WAF guard -1pp; C must also beat B and S, with positive point deltas in both fixed weights. Graph checkpoint additionally must beat original40 A. Confirmation cannot reselect a second candidate.',source_independence_certified=False,confirmation_not_scored=True,plan_id=p['plan_id'],time_beijing=now())
  frozen['selection_id']=canonical(frozen)
  if (run/'frozen_selection.json').exists():
   previous=read(run/'frozen_selection.json')
   fields=[k for k in frozen if k not in ['time_beijing','selection_id']]
   if canonical({k:frozen[k] for k in fields})!=canonical({k:previous[k] for k in fields}):raise ValueError('Existing pre-confirmation selection would change; refusing overwrite')
   frozen=previous
  else:dump(run/'frozen_selection.json',frozen)
 else:
  frozen=read(run/'frozen_selection.json');ck=frozen['checkpoint'];arm=frozen['condition']
  if frozen['selection_id']!=canonical({k:v for k,v in frozen.items() if k!='selection_id'}):raise ValueError('Frozen selection changed')
  checks=[]
  if arm!='A':checks.append(pair(ck,arm,'A'))
  if arm=='C':checks.extend([pair(ck,'C','B'),pair(ck,'C','S')])
  if ck!='original_epoch40':checks.append(pair(ck,arm,'A','original_epoch40'))
  accepted=all(positive(x) and guard(x) for x in checks)
  decision=dict(frozen_candidate={'checkpoint':ck,'condition':arm},confirmation_passed=bool(accepted),adopt_provisionally={'checkpoint':ck,'condition':arm} if accepted else {'checkpoint':'original_epoch40','condition':'A'},Appraisal_validated=bool(accepted and arm=='C'),training_ready=False,training_reason='Original-source/speaker isolation remains unverified; current results support provisional inference-method choice only. No new graph/semantic supervision was independently validated.',scope='New sample/media-disjoint MER-only material, not source/speaker-independent validation or a new nine-benchmark claim.',time_beijing=now())
  dump(run/'method_decision.json',decision)
 secondary=[]
 sem={x['sample_id'].removeprefix('NEW::'):x['semantic_state_set_changed'] for x in read(run/'audit/shuffle_intervention_audit.json')['rows'] if x['partition']==part}
 for ck in p['checkpoints']:
  for changed in [True,False]:
   for task,(role,field) in roles.items():
    samples=[];deltas=[]
    for seed in p['seeds']:
     aa=arrays[ck,'C',seed,task];bb=arrays[ck,'S',seed,task]
     names=[n for n,v in zip(aa['names'],aa['valid']) if v] if role=='SIMS' else aa['names']
     ix=np.array([i for i,n in enumerate(names) if sem.get(n)==changed],dtype=int)
     if len(ix)==0:continue
     def sliced(a):
      if role=='SIMS':return dict(y=a['y'][ix],z=a['z'][ix])
      return {k:a[k][ix] for k in ['hit','m','prec','rec','sizes']}
     deltas.append(100*float(metric(sliced(aa),role)-metric(sliced(bb),role)));samples.append(len(ix))
    secondary.append(dict(checkpoint=ck,task=task,semantic_state_set_changed=changed,unique_samples=samples[0] if samples else 0,C_minus_S_pp_mean=float(np.mean(deltas)) if deltas else None,per_seed_delta_pp=deltas,role='Secondary intervention coverage diagnostic; sample selection uses evidence only, not outcomes'))
 dump(e/'semantic_change_strata.json',secondary)
 summary=[]
 for ck in p['checkpoints']:
  for arm in p['conditions']:
   x=dict(checkpoint=ck,condition=arm,tasks={})
   for task in roles:
    ss=[rawrows[ck,arm,s,task] for s in p['seeds']];fields=ss[0]['metrics'];x['tasks'][task]={f:100*float(np.mean([v['metrics'][f] for v in ss])) for f in fields}
   summary.append(x)
 dump(e/'three_seed_summary.json',summary);dump(e/'paired_analysis.json',list(comparisons.values()))
 lines=[f'# {part}: fixed-weight, three-seed method comparison','', 'All percentages are means across three fixed generation seeds. Primary selection score: equally weighted categorical HIT and OV F. Polarity WAF is a separate harm guard. Bootstrap resamples samples identically across seeds; it does not certify source independence or represent training-seed uncertainty.','', '|Checkpoint|Arm|HIT|M|Polarity WAF|ACC|OV F|OV P|OV R|','|---|---|---:|---:|---:|---:|---:|---:|---:|']
 for x in summary:
  a=x['tasks'];vals=[a['MER_track1_discrete'][k] for k in ['HIT','M']]+[a['MER_track1_polarity'][k] for k in ['WAF','ACC']]+[a['MER_OV'][k] for k in ['F_s','P_s','R_s']]
  lines.append('|'+x['checkpoint']+'|'+x['condition']+'|'+'|'.join(f'{v:.3f}' for v in vals)+'|')
 lines+=['','Per-class effects, corrected/harmed counts and paired intervals: paired_analysis.json.','Source/video/speaker mapping remains unavailable. Near-video search covered selected media only; near-duplicate training videos and undocumented pretraining exposure remain unverified.','']
 if part=='development':lines+=['Frozen candidate: '+frozen['checkpoint']+' / '+frozen['condition']+'. Confirmation outcomes must not alter this selection.']
 else:lines += ['Decision: '+json.dumps(decision,ensure_ascii=False)]
 (e/'RESULTS.md').write_text('\n'.join(lines)+'\n')
 dump(e/'metrics_verified.json',dict(passed=True,official_metric_records=len(scores),all_sample_array_metrics_match_official=True,unique_rows=len(read(run/'data'/f'{part}_records.json')),source_independence_certified=False,time_beijing=now()))
 return summary
if __name__=='__main__':analyze(Path(sys.argv[1]),sys.argv[2])

"""Train only calibration/admission policies. Formal Cue Students and G1 stay frozen."""
import concurrent.futures,collections,os,time
import numpy as np
from scipy.special import expit,logit
from amg_graph_v2.v21.common import *
from amg_graph_v2.v21.calibration import *

def legacy_threshold(y,p):
 order=np.argsort(-p,kind='stable');pp=p[order];yy=y[order];ends=np.r_[np.flatnonzero(np.diff(pp)!=0),len(pp)-1];n=ends+1;tp=np.cumsum(yy)[ends];pr=tp/n;lower=(pr+1.96**2/(2*n)-1.96*np.sqrt(pr*(1-pr)/n+1.96**2/(4*n*n)))/(1+1.96**2/n);v=np.flatnonzero((pr>=.65)&(n>=10)&(lower>=.5));return float(pp[ends[v[-1]]]) if len(v) else None

def identification_metrics(y,selected,groups):
 tp=int(y[selected].sum());n=int(selected.sum());pos=int(y.sum());return dict(valid=len(y),positive=pos,TP=tp,FP=n-tp,FN=pos-tp,predictions=n,prediction_groups=len(set(groups[selected])),precision=tp/n if n else None,recall=tp/pos if pos else None,f1=2*tp/max(1,n+pos))

def run_cue(j,data,c,ids):
 output=ROOT/'work/cues'/f'{j:02d}.json';npz=output.with_suffix('.npz');output.parent.mkdir(parents=True,exist_ok=True)
 if output.exists() and npz.exists():return read(output)
 valid=data['label_mask'][:,j]&data['available'][:,j]&np.isfinite(data['scores'][:,j]);ii=np.flatnonzero(valid);q=data['scores'][ii,j].astype(float);y=data['targets'][ii,j].astype(int);groups=data['groups'][ii];N=len(data['scores']);seed=c['seed']+j*1000003;event('cue_start',index=j,cue_id=ids[j],valid=len(ii),positive=int(y.sum()))
 model,p=crossfit_platt(q,y,groups,ii,c,seed);report=dict(cue_index=j,cue_id=ids[j],calibration=model,valid_indices=ii.tolist(),label_provenance=c['label_provenance']);oof=np.full(N,np.nan);full=np.full(N,np.nan);ct=np.array([]);et=np.array([])
 if p is not None:
  oof[ii]=p;full[ii]=mapped(q,model,c);policy,ct,et=admission_policy(y,p,groups,c,seed+17);report['policy']=policy
 else:report['policy']=dict(candidate=dict(status='deferred',threshold=None,reason=model['reason']),evidence=dict(status='deferred',threshold=None,reason=model['reason']),evidence_without_stability=dict(status='deferred',threshold=None),legacy_threshold=None,stability=dict(status='not_applicable_calibrator_deferred'))
 outer=None;nestedp=np.full(N,np.nan);selections={k:np.zeros(N,bool) for k in ['T0_refit_workflow','T1','T2','T3','T4']};traces=[]
 if outer is not None:
  for k,(train,held) in enumerate(outer):
   trainindices=ii[train];heldindices=ii[held];inner,innerp=crossfit_platt(q[train],y[train],groups[train],trainindices,c,seed+10000+k*31)
   trace=dict(outer_fold=k,training_indices=trainindices.tolist(),heldout_indices=heldindices.tolist(),inner_calibration=inner)
   # T0 refits the old same-sample Platt+threshold workflow inside the outer training split.
   legacy=fit_platt(q[train],y[train],c)
   if legacy['slope']>0 and legacy['converged']:
    lm=dict(method='platt',**legacy);trainp=mapped(q[train],lm,c);tt=legacy_threshold(y[train],trainp)
    if tt is not None:selections['T0_refit_workflow'][heldindices]=mapped(q[held],lm,c)>=tt
   if innerp is not None:
    pol,_,_=admission_policy(y[train],innerp,groups[train],c,seed+30000+k*71);heldp=mapped(q[held],inner,c);nestedp[heldindices]=heldp
    for name,t in [('T1',pol['legacy_threshold']),('T2',pol['candidate']['threshold']),('T3',pol['evidence_without_stability']['threshold']),('T4',pol['evidence']['threshold'])]:
     if t is not None:selections[name][heldindices]=heldp>=t
    trace['policy']=pol
   traces.append(trace);event('cue_nested_fold',cue_id=ids[j],fold=k,calibration_method=inner['method'])
 report['nested_group_cv']=dict(outer_fold_count=len(outer) if outer else 0,traces=traces,metrics={name:identification_metrics(y,sel[ii],groups) for name,sel in selections.items()},selected_calibration_metrics=evaluate_calibration(y[np.isfinite(nestedp[ii])],nestedp[ii][np.isfinite(nestedp[ii])],c['ece_bins']) if np.isfinite(nestedp[ii]).any() else None,scope='Outer groups held out from calibrator fitting, calibrator selection, threshold search and threshold stability; historically exposed source pseudo-labels, not external independent audit')
 save(npz,oof=oof,final_fit_scores=full,nested_scores=nestedp,bootstrap_candidate_thresholds=ct,bootstrap_evidence_thresholds=et,**{name:sel for name,sel in selections.items()});write(output,report);event('cue_complete',cue_id=ids[j],calibrator=model['method'],candidate=report['policy']['candidate']['status'],evidence=report['policy']['evidence']['status']);return report

def main():
 c=read(ROOT/'config.json');prepared=read(ROOT/'data/prepared.json');assert prepared['baseline_G1_sha256']==sha(BASELINE/'learned_relations/G1.npz');assert prepared['baseline_student_binding_sha256']==sha(BASELINE/'runtime/student_binding.json');data=dict(np.load(ROOT/'data/development.npz'));ids=read(BASELINE/'ontology/index.json')['cue_ids'];start=time.time();reports=[None]*42
 with concurrent.futures.ThreadPoolExecutor(max_workers=c['workers']) as pool:
  futures={pool.submit(run_cue,j,data,c,ids):j for j in range(42)}
  for future in concurrent.futures.as_completed(futures):
   j=futures[future];reports[j]=future.result();event('cue_progress',completed=sum(r is not None for r in reports),total=42,elapsed_seconds=round(time.time()-start,1))
 work=ROOT/'work';work.mkdir(exist_ok=True);policies=[]
 for r in reports:
  ca={k:v for k,v in r['calibration'].items() if k not in ('trace','raw_metrics','platt_oof_metrics')};policies.append(dict(cue_id=r['cue_id'],cue_index=r['cue_index'],calibration=ca,candidate=r['policy']['candidate'],evidence=r['policy']['evidence'],evidence_without_stability=r['policy']['evidence_without_stability'],legacy_threshold=r['policy'].get('legacy_threshold'),stability=r['policy']['stability']))
 write(work/'cue_admission_policy.json',dict(schema_version='amg_v21_cue_admission',cue_ids=ids,cues=policies,label_provenance=c['label_provenance'],candidate_enters_prompt=False,preserve_g1_input_distribution=True,human_precision_guarantee=False))
 write(work/'cue_calibration_final.json',dict(cues=[dict(cue_id=p['cue_id'],**p['calibration']) for p in policies],fit_scope='Full source calibration development; performance assessed by nested group CV, no independent manual audit yet'))
 write(work/'cue_calibration_oof.json',dict(cues=[dict(cue_id=r['cue_id'],valid_indices=r['valid_indices'],folds=r['calibration'].get('trace',[]),method=r['calibration']['method']) for r in reports],scores='cue_scores_and_oof.npz',student_oof=False,calibration_oof=True,Student_training_overlap=0))
 write(work/'cue_calibration_metrics.json',dict(cues=[dict(cue_id=r['cue_id'],raw=r['calibration'].get('raw_metrics'),platt_oof=r['calibration'].get('platt_oof_metrics'),method=r['calibration']['method'],oof_vs_final_score_shift=r['calibration'].get('oof_vs_final_score_shift')) for r in reports]))
 write(work/'nested_group_cv_report.json',dict(cues=[dict(cue_id=r['cue_id'],**r['nested_group_cv']) for r in reports],label_provenance=c['label_provenance'],independent_audit=False,selection_repeated_in_each_outer_training_split=True))
 arrays=[np.load(work/'cues'/f'{j:02d}.npz') for j in range(42)];save(work/'cue_scores_and_oof.npz',oof=np.stack([a['oof'] for a in arrays],1),final_fit=np.stack([a['final_fit_scores'] for a in arrays],1),nested=np.stack([a['nested_scores'] for a in arrays],1),sample_ids=data['sample_ids'],groups=data['groups'])
 write(work/'cue_candidate_thresholds.json',dict(cues=[dict(cue_id=p['cue_id'],**p['candidate']) for p in policies]));write(work/'cue_evidence_thresholds.json',dict(cues=[dict(cue_id=p['cue_id'],**p['evidence']) for p in policies]));write(work/'cue_threshold_stability.json',dict(cues=[dict(cue_id=p['cue_id'],**p['stability']) for p in policies],replicates=c['threshold_stability_replicates'],inner_precision_ci_replicates=c['stability_inner_ci_replicates'],failed_replicates_retained=True));write(work/'cue_group_bootstrap.json',dict(replicates=c['bootstrap_replicates'],unit='Known source groups including conservative long-transcript proxies',method='Multinomial group resampling; inner resampling compresses groups with identical (TP,prediction) counts, which is distribution-exact',precision_intervals='Per-Cue marginal; not a simultaneous 42-Cue guarantee',stability_method='Each resample searches all tied-score-aware candidate thresholds and recomputes its Group Bootstrap precision LCB; fixed-threshold CI and selection stability are distinct',conditional_on='Fixed OOF calibration scores; nested group CV separately measures calibration and policy selection uncertainty'))
 # Paired internal regression on data never used for v2.1 fitting or policy choices.
 evaluation=dict(np.load(ROOT/'data/internal_evaluation.npz'));baseline=read(BASELINE/'calibration/cue_policy.json');comparisons={name:[] for name in ['T0_frozen','T1','T2','T3','T4']}
 for j,p in enumerate(policies):
  v=evaluation['label_mask'][:,j]&evaluation['available'][:,j];yy=evaluation['targets'][v,j].astype(int);q=evaluation['scores'][v,j];gg=evaluation['groups'][v];t0score=expit(logit(np.clip(q,c['raw_score_clip'],1-c['raw_score_clip']))*baseline['calibration_slope'][j]+baseline['calibration_intercept'][j]);take=t0score>=baseline['thresholds'][j] if baseline['calibration_status'][j].startswith('platt_') else np.zeros(len(q),bool);comparisons['T0_frozen'].append(dict(cue_id=p['cue_id'],**identification_metrics(yy,take,gg)))
  for name,threshold in [('T1',p['legacy_threshold']),('T2',p['candidate']['threshold']),('T3',p['evidence_without_stability']['threshold']),('T4',p['evidence']['threshold'])]:
   if p['calibration']['method']!='deferred' and threshold is not None:score=mapped(q,p['calibration'],c);sel=score>=threshold
   else:sel=np.zeros(len(q),bool)
   comparisons[name].append(dict(cue_id=p['cue_id'],**identification_metrics(yy,sel,gg)))
 def summary(items):
  tp=sum(a['TP'] for a in items);fp=sum(a['FP'] for a in items);fn=sum(a['FN'] for a in items);return dict(micro_precision=tp/(tp+fp) if tp+fp else None,micro_recall=tp/(tp+fn) if tp+fn else None,macro_precision_over_emitting_cues=float(np.mean([a['precision'] for a in items if a['precision'] is not None])) if any(a['precision'] is not None for a in items) else None,emitting_cues=sum(a['predictions']>0 for a in items),predictions=tp+fp,TP=tp,FP=fp,FN=fn)
 write(work/'cue_precision_recall_report.json',dict(internal_regression={k:dict(summary=summary(v),per_cue=v) for k,v in comparisons.items()},nested_cv={name:dict(summary=summary([r['nested_group_cv']['metrics'][name] for r in reports]),per_cue=[dict(cue_id=r['cue_id'],**r['nested_group_cv']['metrics'][name]) for r in reports]) for name in ['T0_refit_workflow','T1','T2','T3','T4']},label_provenance=c['label_provenance'],thresholds_frozen_before_internal_evaluation=True))
 write(work/'cue_reliability_report.json',dict(bins=c['ece_bins'],bin_strategy='Fixed equal-width [0,1] bins, counts reported',cues=[dict(cue_id=r['cue_id'],raw=r['calibration'].get('raw_metrics',{}).get('reliability_bins'),OOF=r['calibration'].get('platt_oof_metrics',{}).get('reliability_bins')) for r in reports]))
 counts=dict(calibration=dict(collections.Counter(p['calibration']['method'] for p in policies)),candidate_admitted=sum(p['candidate']['threshold'] is not None for p in policies),evidence_admitted=sum(p['evidence']['threshold'] is not None for p in policies),evidence_deferred=sum(p['evidence']['threshold'] is None for p in policies));write(work/'fit_complete.json',dict(complete=True,**counts,student_retrained=False,G1_refitted=False,elapsed_seconds=time.time()-start,config_sha256=sha(ROOT/'config.json')));event('v21_fit_complete',**counts)
if __name__=='__main__':main()

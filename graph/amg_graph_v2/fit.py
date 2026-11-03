"""Build graph relations from fixed original Student scores; Student is never trained."""
import argparse,collections,csv,json,os,time
import numpy as np
from scipy.special import expit,softmax,logit
from .common import *
from .models import *
from .calibration import *

def main():
 config=read(ROOT/'config.json');info=read(ROOT/'data/prepared.json');assert info['student_retrained'] is False and info['cue_prediction_oof'] is False
 z=np.load(ROOT/'data/labels.npz');qz=np.load(ROOT/'data/cue_scores.npz');q=qz['scores'].astype(np.float64);av=qz['available'];q=np.where(av,q,0.)
 cy=z['cue_y'];cm=z['cue_mask'];ay=z['app_y'];am=z['app_mask'];ey=z['emotion_y'];em=z['emotion_mask'];tr=z['train'];tune=z['tune'];ev=z['evaluation'];fold=z['fold'];groups=z['groups'];ids=z['sample_ids'];dims=[np.flatnonzero(np.array(info['state_dim'])==d) for d in range(6)]
 out=ROOT/'work';out.mkdir(exist_ok=True)
 state_y=np.zeros((len(q),16),bool)
 for d,cols in enumerate(dims):
  for local,global_index in enumerate(cols):state_y[:,global_index]=am[:,d]&(ay[:,d]==local)
 state_mask=am[:,np.array(info['state_dim'])]
 pc,s_ca=npmi(cy[tr].astype(bool),cm[tr],state_y[tr],state_mask[tr]);pe,s_ce=npmi(cy[tr].astype(bool),cm[tr],ey[tr].astype(bool),em[tr]);pa,s_ae=npmi(state_y[tr],state_mask[tr],ey[tr].astype(bool),em[tr])
 save(out/'npmi_baseline.npz',CA=pc,CE=pe,AE=pa)
 params={};model_reports={};preds={};fold_params=[];cross_app=None
 for method in ['G1','G2','G3']:
  path=out/(method+'.npz');event('fit_method',method=method)
  if path.exists():
   data=np.load(path);cw,cb,ew,eb,aw,ab,cp=[data[k] for k in ['CA','CA_bias','CE','CE_bias','AE','AE_bias','cross_fitted_appraisal']];reports=read(out/(method+'_fit.json'))
  else:
   cw,cb,cr=app_fit(q[tr],ay[tr],am[tr],dims,method=method,prior=pc*.25,c=config['relation_C']);cp=np.zeros((int(tr.sum()),16));trainfold=fold[tr];qq=q[tr];yyy=ay[tr];mmm=am[tr];foldca=[]
   for k in range(5):
    f=trainfold==k;w,b,r=app_fit(qq[~f],yyy[~f],mmm[~f],dims,method=method,prior=pc*.25,c=config['relation_C']);cp[f]=app_predict(qq[f],w,b,dims);foldca.append((w,b));event('CA_crossfit',method=method,fold=k,train=int((~f).sum()),predict=int(f.sum()))
   ew,eb,er=binary_fit(q[tr],ey[tr],em[tr],method=method,prior=pe*.25,c=config['relation_C'],jobs=config['relation_jobs']);aw,ab,ar=binary_fit(cp,ey[tr],em[tr],method=method,prior=pa*.25,c=config['relation_C'],jobs=config['relation_jobs'])
   reports=dict(CA=cr,CE=er,AE=ar,crossfit='Appraisal predictions are group cross-fitted; Cue scores are reused in-sample Student predictions, not OOF')
   save(path,CA=cw,CA_bias=cb,CE=ew,CE_bias=eb,AE=aw,AE_bias=ab,cross_fitted_appraisal=cp)
   write(out/(method+'_fit.json'),reports)
   if method=='G1':
    for k,(w,b) in enumerate(foldca):save(out/f'CA_fold{k}.npz',W=w,b=b)
  params[method]=dict(CA=cw,CA_bias=cb,CE=ew,CE_bias=eb,AE=aw,AE_bias=ab);model_reports[method]=reports
  pp=app_predict(q,cw,cb,dims);preds[method]=dict(appraisal=pp,CE=q@ew+eb,AE=pp@aw+ab)
  if method=='G1':cross_app=cp
 # Statistical NPMI is a separately calibrated baseline with identical frozen Cue inputs.
 cb=np.zeros(16)
 for d,cols in enumerate(dims):
  c=state_y[tr][:,cols].sum(0)+.5;cb[cols]=np.log(c/c.sum())
 prevalence=(ey[tr]*em[tr]).sum(0)/np.maximum(1,em[tr].sum(0));prior_logit=logit(np.clip(prevalence,1e-5,1-1e-5))
 pp=app_predict(q,pc,cb,dims);preds['G0_NPMI']=dict(appraisal=pp,CE=q@pe+prior_logit,AE=pp@pa+prior_logit)
 # Freeze score calibration, per-Cue policies and branch selection on the tuning half only.
 csl,cbi,cst=binary_calibrate(logit(np.clip(q[tune],1e-6,1-1e-6)),cy[tune],cm[tune]&av[tune],config)
 cq=apply_binary(logit(np.clip(q,1e-6,1-1e-6)),csl,cbi);ct,ctr=thresholds(cy[tune],cq[tune],cm[tune]&av[tune],config,config['cue_precision_target'])
 for j,s in enumerate(cst):
  if not s.startswith('platt_'):ct[j]=1.1;ctr[j]['status']='deferred_uncalibrated';ctr[j]['threshold']=1.1
 write(out/'cue_policy.json',dict(cue_ids=info['cue_ids'],thresholds=ct.tolist(),calibration_slope=csl.tolist(),calibration_intercept=cbi.tolist(),calibration_status=cst,per_cue=ctr,raw_scores_unchanged=True,student_binding=str(ROOT/'data/student_binding.json'),calibration_version='platt_internal_development_v1',threshold_objective='Maximum recall subject to precision >= .65, >=10 predictions, Wilson lower precision >= .5'))
 report={};cal={};p=preds['G1'];mainp=params['G1'];temps,ag=app_calibrate(q[tune]@mainp['CA']+mainp['CA_bias'],ay[tune],am[tune],dims,config);cal['appraisal_temperature']=temps.tolist();cal['appraisal_gates']=ag
 # AE consumes cross-fitted predicted Appraisal at training and final CA predicted Appraisal at inference; never Teacher one-hot inputs.
 # Keep AE input probabilities raw (temperature is a display/gating calibration), matching training.
 for name,pred in preds.items():
  branches={};bc={}
  for branch in ['CE','AE']:
   sl,bi,st=binary_calibrate(pred[branch][tune],ey[tune],em[tune],config);prob=apply_binary(pred[branch],sl,bi);tt,rr=thresholds(ey[tune],prob[tune],em[tune],config,config['emotion_precision_target']);bc[branch]=dict(slope=sl.tolist(),intercept=bi.tolist(),status=st,thresholds=tt.tolist(),threshold_audit=rr);branches[branch]=prob
  best=None;grid=[]
  for alpha in config['fusion_alpha_grid']:
   logits=pred['CE']+alpha*(pred['AE']-prior_logit);sl,bi,st=binary_calibrate(logits[tune],ey[tune],em[tune],config);prob=apply_binary(logits,sl,bi);score=binary_metrics(ey[tune],prob[tune],em[tune])['brier'];grid.append(dict(alpha=alpha,tune_brier=score))
   if best is None or score<best[0]-1e-12:best=(score,alpha,prob,sl,bi,st)
  _,alpha,fused,sl,bi,st=best;tt,rr=thresholds(ey[tune],fused[tune],em[tune],config,config['emotion_precision_target']);bc['fusion']=dict(alpha=alpha,bias=(-alpha*prior_logit).tolist(),slope=sl.tolist(),intercept=bi.tolist(),status=st,thresholds=tt.tolist(),threshold_audit=rr,selection_grid=grid)
  inc=paired_bootstrap(ey[ev],branches['CE'][ev],fused[ev],em[ev],groups[ev],config['validation_bootstrap_replicates']);increment=bool(alpha>0 and inc['lower']>0)
  base=np.repeat(prevalence[None],len(q),axis=0);ce_quality=paired_bootstrap(ey[ev],base[ev],branches['CE'][ev],em[ev],groups[ev],config['validation_bootstrap_replicates']);ce_enabled=ce_quality['lower']>0
  report[name]=dict(tune={b:binary_metrics(ey[tune],prob[tune],em[tune],bc[b]['thresholds']) for b,prob in branches.items()},internal_evaluation={b:binary_metrics(ey[ev],prob[ev],em[ev],bc[b]['thresholds']) for b,prob in branches.items()},appraisal_internal_evaluation=appraisal_metrics(ay[ev],pred['appraisal'][ev],am[ev],dims),fusion_internal_evaluation=binary_metrics(ey[ev],fused[ev],em[ev],tt),fusion_vs_CE_group_bootstrap=inc,CE_vs_prior_group_bootstrap=ce_quality,path_branch_enabled=increment,CE_branch_enabled=ce_enabled)
  if name=='G1':
   cal.update(branches=bc,path_branch_enabled=increment,CE_branch_enabled=bool(ce_enabled));mainprobs=branches;mainfused=fused
 write(out/'calibration.json',cal);write(out/'method_comparison.json',report)
 save(out/'predictions.npz',q=q,cue_calibrated=cq,appraisal=preds['G1']['appraisal'],CE_logits=preds['G1']['CE'],AE_logits=preds['G1']['AE'],CE=mainprobs['CE'],AE=mainprobs['AE'],fused=mainfused)
 # Relation fold fits share the same group split; Student is fixed and no OOF claim is made.
 for k in range(5):
  path=out/f'relation_fold{k}.npz'
  if path.exists():d=np.load(path);fold_params.append({t:d[t] for t in ['CA','CE','AE']});continue
  use=fold[tr]!=k;cw=np.load(out/f'CA_fold{k}.npz');ew,eb,er=binary_fit(q[tr][use],ey[tr][use],em[tr][use],c=config['relation_C'],jobs=config['relation_jobs']);aw,ab,ar=binary_fit(cross_app[use],ey[tr][use],em[tr][use],c=config['relation_C'],jobs=config['relation_jobs'])
  save(path,CA=cw['W'],CA_bias=cw['b'],CE=ew,CE_bias=eb,AE=aw,AE_bias=ab)
  trainids=ids[tr][use].tolist();validids=ids[tr][~use].tolist();assert not(set(trainids)&set(validids));assert not(set(groups[tr][use])&set(groups[tr][~use]));write(out/f'relation_fold{k}.json',dict(fold=k,train_ids=trainids,heldout_ids=validids,train_ids_sha256=digest(trainids),heldout_ids_sha256=digest(validids),cue_student_fixed=True,cue_scores_oof=False,CA_training_samples=len(trainids),checkpoint_sha256=sha(path)))
  fold_params.append(dict(CA=cw['W'],CE=ew,AE=aw));event('relation_fold',fold=k)
 # Refit all three relations for each known-source-group bootstrap sample.
 unique,inv=np.unique(groups[tr],return_inverse=True);singleton=len(unique)==int(tr.sum());boots=[];bootdir=out/'bootstrap';bootdir.mkdir(exist_ok=True)
 for k in range(config['coefficient_bootstrap_replicates']):
  path=bootdir/f'{k:03d}.npz'
  if path.exists():d=np.load(path);boots.append({t:d[t] for t in ['CA','CE','AE']});continue
  rng=np.random.default_rng(config['seed']+1000+k);counts=rng.multinomial(len(unique),np.repeat(1/len(unique),len(unique)));weights=counts[inv]
  cw,cb,cr=app_fit(q[tr],ay[tr],am[tr],dims,weights=weights,c=config['relation_C']);ew,eb,er=binary_fit(q[tr],ey[tr],em[tr],weights=weights,c=config['relation_C'],jobs=config['relation_jobs']);aw,ab,ar=binary_fit(cross_app,ey[tr],em[tr],weights=weights,c=config['relation_C'],jobs=config['relation_jobs']);save(path,CA=cw,CE=ew,AE=aw)
  boots.append(dict(CA=cw,CE=ew,AE=aw));event('group_bootstrap',done=k+1,total=config['coefficient_bootstrap_replicates'])
 write(out/'bootstrap_report.json',dict(unit='known_source_groups',replicates=len(boots),group_count=len(unique),training_rows=int(tr.sum()),maximum_known_group_size=int(np.bincount(inv).max()),row_bootstrap_equivalent=singleton,row_bootstrap_report='With verified singleton known groups, row bootstrap and known-group bootstrap are exactly the same resampling procedure.' if singleton else 'Known group bootstrap used; row bootstrap not used for admission.',limitation=info['group_limitations'],refitted_relations=['CA','CE','AE'],AE_crossfit_probability_inputs='Fixed cross-fitted Appraisal predictions in bootstrap; conditional relation-parameter uncertainty, not full pipeline retraining uncertainty'))
 # Audit every matrix entry, including rejections.
 ids_by=dict(CA=(info['cue_ids'],info['states']),CE=(info['cue_ids'],info['emotion_ids']),AE=(info['states'],info['emotion_ids']));support=dict(CA=s_ca,CE=s_ce,AE=s_ae);audit=[];admitted={t:[] for t in ids_by};qa=q[tune];pp=preds['G1']['appraisal'][tune]
 for typ in ['CA','CE','AE']:
  ww=mainp[typ];bw=np.stack([a[typ] for a in boots]);lower=np.quantile(bw,.025,axis=0);upper=np.quantile(bw,.975,axis=0);fw=np.stack([a[typ] for a in fold_params]);sign=(np.sign(fw)==np.sign(ww)).mean(0)
  for s in range(ww.shape[0]):
   for t in range(ww.shape[1]):
    weight=float(ww[s,t]);count=int(support[typ][s,t]);xpositive=(cy[tr,s].astype(bool)&cm[tr,s]) if typ!='AE' else state_y[tr,s];targetpositive=state_y[tr,t] if typ=='CA' else ey[tr,t].astype(bool);sg=len(set(groups[tr][xpositive&targetpositive]))
    if typ=='CA':
     d=int(info['state_dim'][t]);cols=dims[d];v=am[tune,d];a=ay[tune,d];base=app_predict(qa,mainp['CA'],mainp['CA_bias'],dims,temps)[:,cols];zz=(qa@mainp['CA']+mainp['CA_bias'])[:,cols];zz[:,list(cols).index(t)]-=qa[:,s]*weight;abl=softmax(zz/temps[d],axis=1);truth=np.eye(len(cols))[np.maximum(a,0)];delta=float((np.square(abl-truth).sum(1)[v]-np.square(base-truth).sum(1)[v]).mean()) if v.any() else 0.
    else:
     v=em[tune,t];x=(qa[:,s] if typ=='CE' else pp[:,s]);logits=preds['G1'][typ][tune,t];spec=cal['branches'][typ];sl=spec['slope'][t];bi=spec['intercept'][t];base=expit(logits*sl+bi);abl=expit((logits-x*weight)*sl+bi);delta=float((np.square(abl-ey[tune,t])[v]-np.square(base-ey[tune,t])[v]).mean()) if v.any() else 0.
    reasons=[]
    if count<config['minimum_edge_support_samples']:reasons.append('insufficient_joint_sample_support')
    if sg<config['minimum_edge_support_groups']:reasons.append('insufficient_known_source_groups')
    if abs(weight)<config['minimum_absolute_weight']:reasons.append('small_coefficient')
    if sign[s,t]<config['minimum_fold_sign_consistency']:reasons.append('fold_sign_unstable')
    if lower[s,t]<=0<=upper[s,t]:reasons.append('bootstrap_interval_crosses_zero')
    if delta<=config['minimum_edge_deletion_brier_improvement']:reasons.append('no_positive_deletion_increment')
    if typ=='AE' and not cal['path_branch_enabled']:reasons.append('Appraisal_branch_failed_increment_gate')
    if typ=='CE' and not cal['CE_branch_enabled']:reasons.append('CE_branch_failed_quality_gate')
    source,target=ids_by[typ][0][s],ids_by[typ][1][t];record=dict(edge_id=f'{typ}_{s:02d}_{t:03d}',source_id=source,target_id=target,source_index=s,target_index=t,relation_type=typ,weight=weight,sign='positive' if weight>0 else 'negative' if weight<0 else 'zero',support_sample_count=count,support_group_count=sg,fold_sign_consistency=float(sign[s,t]),bootstrap_lower=float(lower[s,t]),bootstrap_upper=float(upper[s,t]),dev_contribution=delta,admission_status='admitted' if not reasons else 'rejected',rejection_reason=';'.join(reasons),training_release_id=info['cue_release_id'],model_release_id='amg_v2_reused_student_G1',interpretation='conditional_predictive_association')
    audit.append(record)
    if not reasons:admitted[typ].append(record)
  event('edges_audited',relation=typ,total=ww.size,admitted=len(admitted[typ]))
 with (out/'edge_audit.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
 write(out/'admitted_edges.json',admitted)
 # Candidate paths require stable admitted endpoints and held-out branch improvement.
 paths=[];ca_by=collections.defaultdict(list);ae_by=collections.defaultdict(list)
 for e in admitted['CA']:ca_by[e['target_index']].append(e)
 for e in admitted['AE']:ae_by[e['source_index']].append(e)
 for a in sorted(set(ca_by)&set(ae_by)):
  for ca in ca_by[a]:
   for ae in ae_by[a]:
    c,e=ca['source_index'],ae['target_index'];use=cy[tr,c].astype(bool)&cm[tr,c]&state_y[tr,a]&ey[tr,e].astype(bool)&em[tr,e];count=int(use.sum());gc=len(set(groups[tr][use]));reasons=[]
    if count<config['minimum_path_joint_support'] or gc<config['minimum_path_joint_support']:reasons.append('insufficient_triple_joint_support')
    # Actual single-path ablation: delete this CA logit term, recompute its softmax state,
    # then delete only its downstream AE contribution to this target Emotion.
    ap=preds['G1']['appraisal'][ev];d=info['state_dim'][a];cols=dims[d];zz=(q[ev]@mainp['CA']+mainp['CA_bias'])[:,cols];zz[:,list(cols).index(a)]-=q[ev,c]*ca['weight'];alt=softmax(zz,axis=1)[:,list(cols).index(a)];fc=cal['branches']['fusion'];delta_logit=fc['alpha']*ae['weight']*(ap[:,a]-alt);zfull=preds['G1']['CE'][ev,e]+fc['alpha']*preds['G1']['AE'][ev,e]+fc['bias'][e];ablate=expit((zfull-delta_logit)*fc['slope'][e]+fc['intercept'][e]);metric=paired_bootstrap(ey[ev,e,None],mainfused[ev,e,None],ablate[:,None],em[ev,e,None],groups[ev],config['validation_bootstrap_replicates']);improvement=-metric['delta'];lower=-metric['upper'];upper=-metric['lower']
    if lower<=0:reasons.append('single_path_deletion_increment_not_stable')
    paths.append(dict(path_id=f'PATH_{c:02d}_{a:02d}_{e:03d}',cue_id=info['cue_ids'][c],appraisal_state_id=info['states'][a],emotion_id=info['emotion_ids'][e],CA_edge_id=ca['edge_id'],AE_edge_id=ae['edge_id'],joint_support_samples=count,joint_support_groups=gc,coefficient_product=ca['weight']*ae['weight'],sign='positive' if ca['weight']*ae['weight']>0 else 'negative',independent_internal_path_deletion_brier_increment=improvement,increment_lower=lower,increment_upper=upper,admission_status='admitted' if not reasons else 'rejected',rejection_reason=';'.join(reasons)))
 write(out/'paths.json',paths)
 write(out/'fit_complete.json',dict(complete=True,student_retrained=False,cue_oof=False,relation_crossfit_verified=True,edge_candidate_count=len(audit),edge_admitted_counts={k:len(v) for k,v in admitted.items()},path_candidate_count=len(paths),path_admitted_count=sum(a['admission_status']=='admitted' for a in paths),method_metrics_file=str(out/'method_comparison.json'),config_sha256=sha(ROOT/'config.json')))
 event('fit_complete',edges={k:len(v) for k,v in admitted.items()},paths=len(paths))
if __name__=='__main__':main()

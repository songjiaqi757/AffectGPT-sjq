"""Group cross-fitting, nested strategy evaluation and exact group-resampling admission."""
import collections
import numpy as np
from scipy.special import expit,logit
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import average_precision_score,roc_auc_score

def evaluate_calibration(y,p,bins=10):
 p=np.clip(np.asarray(p,float),1e-7,1-1e-7);y=np.asarray(y,float);counts=[];ece=0.
 for k in range(bins):
  v=(p>=k/bins)&(p<((k+1)/bins) if k<bins-1 else p<=1);n=int(v.sum());acc=float(y[v].mean()) if n else None;conf=float(p[v].mean()) if n else None
  if n:ece+=n/max(1,len(y))*abs(acc-conf)
  counts.append(dict(lower=k/bins,upper=(k+1)/bins,count=n,observed_frequency=acc,mean_score=conf))
 return dict(samples=len(y),positive=int(y.sum()),brier=float(np.mean((p-y)**2)) if len(y) else None,log_loss=float(np.mean(-y*np.log(p)-(1-y)*np.log(1-p))) if len(y) else None,ece=float(ece),pr_auc=float(average_precision_score(y,p)) if len(np.unique(y))==2 else None,roc_auc=float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,reliability_bins=counts)

def support(y,groups,c):
 return len(y) and y.sum()>=c['minimum_positive'] and (len(y)-y.sum())>=c['minimum_negative'] and len(set(groups[y==1]))>=c['minimum_positive_groups'] and len(set(groups[y==0]))>=c['minimum_negative_groups']

def make_group_folds(y,groups,c,seed,outer=False):
 if not support(y,groups,c):return None
 for splits in [c['outer_folds'] if outer else c['inner_folds'],c['fallback_folds']]:
  if len(set(groups))<splits:continue
  cv=StratifiedGroupKFold(n_splits=splits,shuffle=True,random_state=seed);folds=list(cv.split(np.zeros((len(y),1)),y,groups))
  if all(support(y[a],groups[a],c) and len(np.unique(y[b]))==2 for a,b in folds):
   assert all(not(set(groups[a])&set(groups[b])) for a,b in folds);return folds
 return None

def fit_platt(q,y,c):
 z=logit(np.clip(q,c['raw_score_clip'],1-c['raw_score_clip']));clf=LogisticRegression(C=c['platt_C'],solver='lbfgs',max_iter=500,tol=1e-9).fit(z[:,None],y.astype(int))
 return dict(slope=float(clf.coef_[0,0]),intercept=float(clf.intercept_[0]),converged=bool(clf.n_iter_[0]<500))

def mapped(q,model,c):
 if model['method']=='identity':return np.asarray(q,float)
 return expit(logit(np.clip(q,c['raw_score_clip'],1-c['raw_score_clip']))*model['slope']+model['intercept'])

def crossfit_platt(q,y,groups,indices,c,seed):
 folds=make_group_folds(y,groups,c,seed);trace=[]
 if folds is None:return dict(method='deferred',reason='insufficient_class_or_group_support_for_crossfit',trace=trace),None
 pp=np.empty(len(q));slopes=[]
 for k,(a,b) in enumerate(folds):
  model=fit_platt(q[a],y[a],c);slopes.append(model['slope']);pp[b]=mapped(q[b],dict(method='platt',**model),c);trace.append(dict(fold=k,training_indices=indices[a].tolist(),heldout_indices=indices[b].tolist(),positive=int(y[a].sum()),negative=int(len(a)-y[a].sum()),**model))
 raw=evaluate_calibration(y,q,c['ece_bins']);oof=evaluate_calibration(y,pp,c['ece_bins']);cv=float(np.std(slopes)/max(abs(np.mean(slopes)),1e-8));stable=all(s>0 for s in slopes) and cv<=c['platt_slope_cv_max'] and all(t['converged'] for t in trace)
 if stable and oof['brier']<=raw['brier']-c['platt_minimum_brier_gain'] and oof['log_loss']<=raw['log_loss']+c['platt_max_logloss_degradation']:
  final=fit_platt(q,y,c)
  if final['slope']>0 and final['converged']:model=dict(method='platt',status='source_pseudolabel_oof_calibrated',**final);chosen=pp
  else:model=dict(method='deferred',reason='nonpositive_or_unconverged_final_Platt');chosen=None
 elif raw['ece']<=c['identity_max_ece'] and raw['brier']<=oof['brier']+c['identity_max_brier_vs_platt'] and raw['log_loss']<=oof['log_loss']+c['identity_max_logloss_vs_platt']:
  model=dict(method='identity',slope=1.,intercept=0.,status='source_pseudolabel_identity_accepted_by_frozen_rule');chosen=np.asarray(q,float)
 else:model=dict(method='deferred',reason='OOF_calibration_quality_or_direction_failed');chosen=None
 model.update(raw_metrics=raw,platt_oof_metrics=oof,fold_slope_cv=cv,trace=trace,fold_count=len(folds),positive=int(y.sum()),negative=int(len(y)-y.sum()),positive_groups=len(set(groups[y==1])),negative_groups=len(set(groups[y==0])))
 if chosen is not None:
  finalp=mapped(q,model,c);model['oof_vs_final_score_shift']=dict(mean_absolute_difference=float(np.abs(chosen-finalp).mean()),q95_absolute_difference=float(np.quantile(np.abs(chosen-finalp),.95)),mean_oof=float(chosen.mean()),mean_final=float(finalp.mean()))
 return model,chosen

class GroupThresholdSearch:
 def __init__(self,y,p,groups,c,seed):
  self.c=c;self.seed=seed;self.y=np.asarray(y,int);self.p=np.asarray(p,float);self.groups=np.asarray(groups);self.unique,self.inv=np.unique(groups,return_inverse=True);self.G=len(self.unique);self.N=len(y);self.order=np.argsort(-self.p,kind='stable');self.yy=self.y[self.order];self.pp=self.p[self.order];self.gi=self.inv[self.order];self.ends=np.r_[np.flatnonzero(np.diff(self.pp)!=0),self.N-1];self.thresholds=self.pp[self.ends];self.first=np.full(self.G,self.N);np.minimum.at(self.first,self.gi,np.arange(self.N));self.first_event=np.zeros(self.N,int);self.first_event[self.first]=1;self.cache={};self.singleton=self.G==self.N
  rng=np.random.default_rng(seed);self.weights=rng.multinomial(self.G,np.repeat(1/self.G,self.G),size=c['bootstrap_replicates']);rw=self.weights[:,self.gi];self.boot_n=np.cumsum(rw,axis=1)[:,self.ends];self.boot_tp=np.cumsum(rw*self.yy,axis=1)[:,self.ends];bp=np.divide(self.boot_tp,self.boot_n,out=np.zeros_like(self.boot_tp,float),where=self.boot_n>0);self.lcb=np.quantile(bp,c['precision_lcb_quantile'],axis=0);self.ucb=np.quantile(bp,1-c['precision_lcb_quantile'],axis=0);self.fixed_zero_prediction_replicates=(self.boot_n==0).sum(0);self.n=np.arange(1,self.N+1)[self.ends];self.tp=np.cumsum(self.yy)[self.ends];self.prec=self.tp/self.n;self.recall=self.tp/max(1,self.y.sum());self.ng=np.cumsum(self.first_event)[self.ends]
 def original(self,constraints,min_threshold=None):
  v=(self.prec>=constraints['minimum_precision'])&(self.lcb>=constraints['minimum_group_precision_lcb'])&(self.n>=constraints['minimum_predictions'])&(self.ng>=constraints['minimum_prediction_groups'])
  if min_threshold is not None:v&=self.thresholds>=min_threshold
  possible=np.flatnonzero(v)
  if not len(possible):return dict(status='deferred',threshold=None,reason='no_threshold_satisfies_all_frozen_constraints')
  k=int(possible[-1]);return self.point(k)
 def point(self,k):
  return dict(status='admitted',threshold=float(self.thresholds[k]),precision=float(self.prec[k]),recall=float(self.recall[k]),predictions=int(self.n[k]),prediction_groups=int(self.ng[k]),group_precision_lcb=float(self.lcb[k]),group_precision_ucb=float(self.ucb[k]),fixed_threshold_zero_prediction_bootstrap_replicates=int(self.fixed_zero_prediction_replicates[k]),curve_index=k)
 def legacy(self,pmin=.65,nmin=10,lmin=.5):
  n=self.n;pr=self.prec;lower=(pr+1.96**2/(2*n)-1.96*np.sqrt(pr*(1-pr)/n+1.96**2/(4*n*n)))/(1+1.96**2/n);possible=np.flatnonzero((pr>=pmin)&(n>=nmin)&(lower>=lmin))
  return float(self.thresholds[possible[-1]]) if len(possible) else None
 def _inner_lcb(self,k,w,tp,n,rng):
  if self.singleton:
   probs=np.array([tp,n-tp,self.G-n],float)/self.G;counts=rng.multinomial(self.G,np.maximum(probs,0)/np.maximum(probs.sum(),1e-15),size=self.c['stability_inner_ci_replicates']);den=counts[:,0]+counts[:,1];pr=np.divide(counts[:,0],den,out=np.zeros(len(den)),where=den>0)
  else:
   if k not in self.cache:
    e=int(self.ends[k])+1;ng=np.bincount(self.gi[:e],minlength=self.G);tpg=np.bincount(self.gi[:e],weights=self.yy[:e],minlength=self.G).astype(int);types,inv=np.unique(np.c_[tpg,ng],axis=0,return_inverse=True);self.cache[k]=(types,inv)
   types,inv=self.cache[k];probs=np.bincount(inv,weights=w,minlength=len(types))/self.G;draws=rng.multinomial(self.G,probs/probs.sum(),size=self.c['stability_inner_ci_replicates']);num=draws@types[:,0];den=draws@types[:,1];pr=np.divide(num,den,out=np.zeros(len(den)),where=den>0)
  return float(np.quantile(pr,self.c['precision_lcb_quantile']))
 def bootstrap_threshold_stability(self):
  B=self.c['threshold_stability_replicates'];rng=np.random.default_rng(self.seed+710000);weights=self.weights if B==len(self.weights) else rng.multinomial(self.G,np.repeat(1/self.G,self.G),size=B);ct=np.full(B,np.nan);et=np.full(B,np.nan);failure={'candidate':collections.Counter(),'evidence':collections.Counter()}
  for b,w in enumerate(weights):
   rw=w[self.gi];n=np.cumsum(rw)[self.ends];tp=np.cumsum(rw*self.yy)[self.ends];pr=np.divide(tp,n,out=np.zeros(len(n),float),where=n>0);events=np.zeros(self.N,int);events[self.first]=(w>0);ng=np.cumsum(events)[self.ends]
   minimum=None
   for name,constraints,result,offset in [('candidate',self.c['candidate'],ct,0),('evidence',self.c['evidence'],et,100000000)]:
    valid=(pr>=constraints['minimum_precision'])&(n>=constraints['minimum_predictions'])&(ng>=constraints['minimum_prediction_groups'])
    if minimum is not None:valid&=self.thresholds>=minimum
    possible=np.flatnonzero(valid)[::-1];found=False
    for k in possible:
     rr=np.random.default_rng(self.seed+offset+int(b)*2003+int(k)*17)
     if self._inner_lcb(int(k),w,int(tp[k]),int(n[k]),rr)>=constraints['minimum_group_precision_lcb']:
      result[b]=self.thresholds[k];found=True
      if name=='candidate':minimum=float(result[b])
      break
    if not found:failure[name]['no_threshold_satisfies_resampled_precision_support_group_LCB']+=1
  def summarize(values,name):
   success=np.isfinite(values);vv=values[success];return dict(replicates=B,successful_replicates=int(success.sum()),failed_replicates=int((~success).sum()),activation_rate=float(success.mean()),threshold_median=float(np.median(vv)) if len(vv) else None,threshold_q25=float(np.quantile(vv,.25)) if len(vv) else None,threshold_q75=float(np.quantile(vv,.75)) if len(vv) else None,threshold_lower=float(np.quantile(vv,.025)) if len(vv) else None,threshold_upper=float(np.quantile(vv,.975)) if len(vv) else None,quantile_scope='Conditional on feasible threshold; failures retained in activation denominator',failure_reasons=dict(failure[name]),CI_replicates_per_resampled_threshold=self.c['stability_inner_ci_replicates'])
  return dict(candidate=summarize(ct,'candidate'),evidence=summarize(et,'evidence')),ct,et

def admission_policy(y,p,groups,c,seed,stability=True):
 search=GroupThresholdSearch(y,p,groups,c,seed);candidate=search.original(c['candidate']);evidence=search.original(c['evidence'],candidate['threshold']);unfiltered=dict(evidence);stats,ct,et=search.bootstrap_threshold_stability() if stability else ({},np.array([]),np.array([]))
 if stability and evidence['threshold'] is not None and stats['evidence']['activation_rate']<c['evidence']['minimum_bootstrap_activation_rate']:evidence=dict(status='deferred',threshold=None,reason='bootstrap_threshold_activation_rate_below_minimum',unfiltered_threshold=unfiltered['threshold'])
 return dict(candidate=candidate,evidence=evidence,evidence_without_stability=unfiltered,stability=stats,legacy_threshold=search.legacy(),group_count=search.G,singleton_groups=search.singleton,bootstrap_precision_scope='Per-Cue marginal interval; not simultaneous 42-Cue coverage'),ct,et

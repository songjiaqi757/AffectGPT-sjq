import numpy as np
from scipy.special import expit,logit,softmax
from scipy.optimize import minimize_scalar
from sklearn.linear_model import LogisticRegression
from .models import binary_metrics

def binary_calibrate(z,y,mask,config):
 a=np.ones(y.shape[1]);b=np.zeros(y.shape[1]);status=[]
 for j in range(y.shape[1]):
  v=mask[:,j];yy=y[v,j]
  if yy.sum()>=config['minimum_calibration_positive'] and (len(yy)-yy.sum())>=config['minimum_calibration_negative']:
   clf=LogisticRegression(C=1.,solver='lbfgs',max_iter=300,tol=1e-8).fit(z[v,j,None],yy.astype(int))
   if clf.coef_[0,0]>0:a[j]=clf.coef_[0,0];b[j]=clf.intercept_[0];status.append('platt_internal_development_fitted')
   else:status.append('deferred_nonpositive_calibration_slope')
  else:status.append('uncalibrated_insufficient_supervision')
 return a,b,status

def apply_binary(z,a,b):return expit(z*a+b)

def thresholds(y,p,mask,config,target):
 t=np.repeat(1.1,y.shape[1]);reports=[]
 for j in range(y.shape[1]):
  v=mask[:,j];yy=y[v,j];pp=p[v,j];best=None
  for cutoff in np.unique(np.r_[np.linspace(.1,.95,86),np.quantile(pp,np.linspace(0,1,101)) if len(pp) else []]):
   take=pp>=cutoff;n=int(take.sum());tp=int(yy[take].sum());precision=tp/max(1,n)
   lower=(precision+1.96**2/(2*max(n,1))-1.96*np.sqrt(precision*(1-precision)/max(n,1)+1.96**2/(4*max(n,1)**2)))/(1+1.96**2/max(n,1))
   if n>=config['minimum_threshold_predictions'] and precision>=target and lower>=.5:
    recall=tp/max(1,int(yy.sum()));cand=(recall,precision,float(cutoff),n,lower)
    if best is None or cand[:2]>best[:2]:best=cand
  if best is not None:t[j]=best[2]
  reports.append(dict(threshold=float(t[j]),status='active' if best is not None else 'deferred',dev_positive=int(yy.sum()),dev_valid=len(yy),precision=best[1] if best else None,recall=best[0] if best else None,predictions=best[3] if best else 0,precision_wilson_lower=best[4] if best else None))
 return t,reports

def app_calibrate(z,y,mask,dimensions,config):
 temps=[];gates=[]
 for d,cols in enumerate(dimensions):
  v=mask[:,d];zz=z[v][:,cols];yy=y[v,d]
  if len(yy)>=100:
   def obj(t):return float(-np.log(np.clip(softmax(zz/t,axis=1)[np.arange(len(yy)),yy],1e-8,1)).mean())
   r=minimize_scalar(obj,bounds=(.25,4.),method='bounded');temp=float(r.x)
  else:temp=1.
  temps.append(temp);q=softmax(zz/temp,axis=1);order=np.sort(q,axis=1);top=q.argmax(1);margin=order[:,-1]-order[:,-2];entropy=-(q*np.log(np.clip(q,1e-8,1))).sum(1)/np.log(len(cols));threshold=1.1;stats=None
  for tt in np.arange(.5,.951,.05):
   take=(q.max(1)>=tt)&(margin>=config['appraisal_margin'])&(entropy<=config['appraisal_max_normalized_entropy']);n=int(take.sum());accuracy=float((top[take]==yy[take]).mean()) if n else 0
   if n>=20 and accuracy>=config['appraisal_minimum_precision']:threshold=float(tt);stats=dict(dev_predictions=n,dev_accuracy=accuracy);break
  gates.append(dict(threshold=threshold,margin=config['appraisal_margin'],max_normalized_entropy=config['appraisal_max_normalized_entropy'],status='active' if threshold<=1 else 'unresolved_only',calibration='temperature_internal_development',**(stats or {})))
 return np.array(temps),gates

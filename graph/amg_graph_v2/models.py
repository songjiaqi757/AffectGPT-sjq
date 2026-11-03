"""Small signed relation matrices; Cue Student is never fitted here."""
import warnings
import numpy as np
from scipy.special import expit,softmax
from scipy.optimize import minimize
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score,f1_score,log_loss
from joblib import Parallel,delayed

def app_predict(x,w,b,dimensions,temperature=None):
 z=x@w+b;p=np.zeros_like(z)
 for d,cols in enumerate(dimensions):p[:,cols]=softmax(z[:,cols]/(temperature[d] if temperature is not None else 1.),axis=1)
 return p

def binary_fit(x,y,mask,weights=None,method='G1',prior=None,c=.2,jobs=4):
 x=np.ascontiguousarray(x,dtype=np.float64);sw=np.ones(len(x)) if weights is None else weights
 def one(j):
  valid=mask[:,j]&(sw>0);xx=x[valid];yy=y[valid,j];ww=sw[valid];positive=float((yy*ww).sum());negative=float(((1-yy)*ww).sum());b=float(np.log((positive+.5)/(negative+.5)));w=np.zeros(x.shape[1])
  if min(positive,negative)<1:return w,b,dict(positive=positive,negative=negative,fit=False,converged=True)
  clf=LogisticRegression(C=c,solver='liblinear',penalty='l1' if method=='G3' else 'l2',intercept_scaling=10.,max_iter=500,tol=1e-6,random_state=20261103)
  clf.fit(xx,yy.astype(int),sample_weight=ww)
  if clf.n_iter_[0]>=500:
   clf.set_params(max_iter=5000);clf.fit(xx,yy.astype(int),sample_weight=ww)
  w=clf.coef_[0];b=clf.intercept_[0];converged=bool(clf.n_iter_[0]<clf.max_iter)
  if method=='G2':
   target=prior[:,j] if prior is not None else np.zeros_like(w);lam=1/(c*ww.sum())
   def objective(v):
    z=xx@v[:-1]+v[-1];err=expit(z)-yy
    loss=np.dot(ww,np.logaddexp(0,z)-yy*z)/ww.sum()+.5*lam*np.square(v[:-1]-target).sum()
    grad=np.r_[(xx.T@(ww*err))/ww.sum()+lam*(v[:-1]-target),(ww*err).sum()/ww.sum()]
    return loss,grad
   r=minimize(objective,np.r_[w,b],jac=True,method='L-BFGS-B',options=dict(maxiter=300,ftol=1e-10,gtol=1e-6));w,b=r.x[:-1],r.x[-1];converged=bool(r.success)
  return w,float(b),dict(positive=positive,negative=negative,fit=True,converged=converged)
 res=Parallel(n_jobs=jobs,prefer='threads')(delayed(one)(j) for j in range(y.shape[1]));return np.stack([a[0] for a in res],1),np.array([a[1] for a in res]),[a[2] for a in res]

def app_fit(x,y,mask,dimensions,weights=None,method='G1',prior=None,c=.2):
 sw=np.ones(len(x)) if weights is None else weights
 w=np.zeros((x.shape[1],sum(map(len,dimensions))));b=np.zeros(w.shape[1]);report=[]
 for d,cols in enumerate(dimensions):
  v=mask[:,d]&(sw>0);xx=np.asarray(x[v],np.float64);yy=y[v,d];ww=sw[v];k=len(cols);counts=np.bincount(yy,weights=ww,minlength=k);bb=np.log((counts+.5)/(counts.sum()+k*.5));bb-=bb.mean();wc=np.zeros((x.shape[1],k))
  dc=c*min(1.,int(v.sum())/12000.)
  if len(np.unique(yy))>=2:
   clf=LogisticRegression(C=dc,solver='saga' if method=='G3' else 'lbfgs',penalty='l1' if method=='G3' else 'l2',max_iter=1000,tol=1e-6,random_state=20261103)
   clf.fit(xx,yy,sample_weight=ww)
   if len(clf.classes_)==2:
    a,z=clf.classes_;wc[:,a]=-.5*clf.coef_[0];wc[:,z]=.5*clf.coef_[0];bb[a]=-.5*clf.intercept_[0];bb[z]=.5*clf.intercept_[0]
   else:
    wc[:,clf.classes_]=clf.coef_.T;bb[clf.classes_]=clf.intercept_
   for missing in set(range(k))-set(clf.classes_):bb[missing]=-20.
   if method=='G2':
    target=prior[:,cols] if prior is not None else wc*0;target=target-target.mean(1,keepdims=True);lam=1/(dc*ww.sum())
    def objective(vv):
     coef=vv[:-k].reshape(x.shape[1],k);bi=vv[-k:];z=xx@coef+bi;pp=softmax(z,axis=1);nll=np.logaddexp.reduce(z,axis=1)-z[np.arange(len(yy)),yy];err=pp;err[np.arange(len(yy)),yy]-=1;err*=ww[:,None]/ww.sum()
     return np.dot(ww,nll)/ww.sum()+.5*lam*np.square(coef-target).sum(),np.r_[(xx.T@err+lam*(coef-target)).ravel(),err.sum(0)]
    r=minimize(objective,np.r_[wc.ravel(),bb],jac=True,method='L-BFGS-B',options=dict(maxiter=300,ftol=1e-10,gtol=1e-6));wc=r.x[:-k].reshape(x.shape[1],k);bb=r.x[-k:]
   converged=bool(clf.n_iter_.max()<1000)
  else:converged=True
  wc-=wc.mean(1,keepdims=True);bb-=bb.mean();w[:,cols]=wc;b[cols]=bb
  report.append(dict(valid=int(v.sum()),class_counts=counts.tolist(),C=dc,converged=converged))
 return w,b,report

def npmi(x,xmask,y,ymask):
 out=np.zeros((x.shape[1],y.shape[1]));support=np.zeros_like(out,int)
 for j in range(y.shape[1]):
  mm=xmask&ymask[:,j,None];joint=(x&y[:,j,None]&mm).sum(0);total=mm.sum(0);px=((x&mm).sum(0)+1)/(total+2);py=((y[:,j,None]&mm).sum(0)+1)/(total+2);p11=(joint+.5)/(total+2)
  out[:,j]=np.clip(np.log(p11/(px*py))/-np.log(p11),-1,1);support[:,j]=joint
 return out,support

def binary_metrics(y,p,mask,threshold=.5):
 p=np.clip(p,1e-7,1-1e-7);aps=[];f=[];prec=[];rec=[];per=[]
 for j in range(y.shape[1]):
  v=mask[:,j];a=y[v,j];q=p[v,j];pred=q>=np.asarray(threshold).reshape(-1)[j] if np.ndim(threshold)>0 else q>=threshold
  tp=float((pred&(a==1)).sum());pr=tp/max(1,int(pred.sum()));re=tp/max(1,int(a.sum()));ff=2*pr*re/max(1e-12,pr+re)
  ap=float(average_precision_score(a,q)) if len(a) and a.max()>0 and a.min()<1 else None
  if ap is not None:aps.append(ap)
  if a.sum()>0:f.append(ff);prec.append(pr);rec.append(re)
  per.append(dict(positive=int(a.sum()),valid=int(v.sum()),ap=ap,f1=ff,precision=pr,recall=re))
 valid=mask;den=max(1,int(valid.sum()));pred=p>=threshold;tp=float((pred&(y==1)&valid).sum());fp=float((pred&(y==0)&valid).sum());fn=float((~pred&(y==1)&valid).sum())
 return dict(macro_ap=float(np.mean(aps)) if aps else None,macro_f1=float(np.mean(f)) if f else None,macro_precision=float(np.mean(prec)) if prec else None,macro_recall=float(np.mean(rec)) if rec else None,micro_f1=2*tp/max(1,2*tp+fp+fn),brier=float((np.square(p-y)*valid).sum()/den),masked_log_loss=float(((-y*np.log(p)-(1-y)*np.log(1-p))*valid).sum()/den),per_class=per)

def appraisal_metrics(y,p,mask,dimensions):
 out=[]
 for d,cols in enumerate(dimensions):
  v=mask[:,d];a=y[v,d];q=np.clip(p[v][:,cols],1e-8,1);pred=q.argmax(1)
  out.append(dict(valid=int(v.sum()),macro_f1=float(f1_score(a,pred,labels=list(range(len(cols))),average='macro',zero_division=0)) if len(a) else None,accuracy=float((pred==a).mean()) if len(a) else None,masked_log_loss=float(-np.log(q[np.arange(len(a)),a]).mean()) if len(a) else None,brier=float(np.square(q-np.eye(len(cols))[a]).sum(1).mean()) if len(a) else None))
 return out

def paired_bootstrap(y,p0,p1,mask,groups,replicates=1000,seed=20261103):
 a=(np.square(p0-y)*mask).sum(1);b=(np.square(p1-y)*mask).sum(1);den=mask.sum(1);unique,inv=np.unique(groups,return_inverse=True);delta=np.bincount(inv,weights=a-b);d=np.bincount(inv,weights=den);rng=np.random.default_rng(seed);dist=[]
 for k in range(replicates):
  counts=rng.multinomial(len(unique),np.repeat(1/len(unique),len(unique)));dist.append(float(counts@delta/max(1,counts@d)))
 return dict(metric='masked_Brier_improvement_positive_is_better',delta=float((a-b).sum()/max(1,den.sum())),lower=float(np.quantile(dist,.025)),upper=float(np.quantile(dist,.975)),replicates=replicates,unit='known_source_group')

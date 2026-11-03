"""CPU-only replay of the archived official metrics and paired bootstrap intervals."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS","1")
os.environ.setdefault("OMP_NUM_THREADS","1")
os.environ.setdefault("MKL_NUM_THREADS","1")
import argparse,json,hashlib
from pathlib import Path
import numpy as np
def read(p):return json.loads(Path(p).read_text())
def score(dataset,ft,counts):
 counts=np.atleast_2d(counts)
 if dataset=="SIMS":
  cm=((counts*ft["valid"][None,:])@ft["conf"]).reshape((-1,2,2))
  support=cm.sum(2);pred=cm.sum(1);tp=np.diagonal(cm,axis1=1,axis2=2);total=support.sum(1)
  f=np.divide(2*tp,support+pred,out=np.zeros_like(tp),where=(support+pred)>0)
  return np.stack([(f*support).sum(1)/total,tp.sum(1)/total],1)
 denominator=counts@ft["valid"].astype(float)
 def mean(x):return (counts@np.nan_to_num(x))/np.maximum(denominator,1e-15)
 if dataset=="MER2023":return np.stack([mean(ft["hit"]).mean(1),mean(ft["m"]).mean(1)],1)
 p=mean(ft["p"]);r=mean(ft["r"])
 f=np.divide(2*p*r,p+r,out=np.zeros_like(p),where=(p+r)>0)
 return np.stack([f.mean(1),p.mean(1),r.mean(1)],1)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def main(directory,verify_inputs=False):
 summary=read(directory/"analysis_results.json");plan=read(directory.parent/"plan.json")
 if verify_inputs:
  for p,digest in read(directory/"input_sha256.json").items():
   assert sha(p)==digest,p
 with np.load(directory/"metric_arrays.npz",allow_pickle=False) as z:arrays={k:z[k] for k in z.files}
 features={}
 for key,value in arrays.items():
  fields=key.split("__")
  if len(fields)==4:
   w,c,d,field=fields;features.setdefault((w,c,d),{})[field]=value
 metricnames={"MER2023":["HIT","M"],"SIMS":["WAF","ACC"],"OVMERDPlus":["F_s","P_s","R_s"]}
 official={(r["weight"],r["ablation"],r["dataset"]):r["metrics"] for r in summary["official_metrics"]}
 rng=np.random.default_rng(20261027)
 counts={d:rng.multinomial(len(arrays[d+"__names"]),np.full(len(arrays[d+"__names"]),1/len(arrays[d+"__names"])),size=5000).astype(float) for d in plan["datasets"]}
 boot={}
 point={}
 maxerror=0.
 for key,ft in features.items():
  d=key[2];n=len(arrays[d+"__names"])
  point[key]=score(d,ft,np.ones(n))[0];boot[key]=score(d,ft,counts[d])
  expected=np.asarray([official[key][m] for m in metricnames[d]])
  maxerror=max(maxerror,float(abs(point[key]-expected).max()))
  assert np.max(abs(point[key]-expected))<1e-12,key
 cierror=0.
 for r in summary["pairs"]:
  w,d=r["weight"],r["dataset"];a,b=r["pair"].split("-")
  ka,kb=(w,a,d),(w,b,d)
  difference=(point[ka]-point[kb])*100
  interval=np.quantile((boot[ka]-boot[kb])*100,[.025,.975],axis=0)
  for j,m in enumerate(metricnames[d]):
   assert abs(difference[j]-r["delta"][m])<1e-10
   cierror=max(cierror,float(abs(interval[:,j]-np.asarray(r["ci95"][m])).max()))
   assert np.max(abs(interval[:,j]-np.asarray(r["ci95"][m])))<1e-8
 print(json.dumps(dict(passed=True,official_jobs=len(features),paired_comparisons=len(summary["pairs"]),
   score_max_error=maxerror,ci_max_error=cierror,bootstrap_replicates=5000,
   inputs_verified=verify_inputs),ensure_ascii=False))
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--directory",type=Path,default=Path(__file__).resolve().parent)
 ap.add_argument("--verify-inputs",action="store_true")
 a=ap.parse_args();main(a.directory,a.verify_inputs)

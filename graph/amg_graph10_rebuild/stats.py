import numpy as np
from scipy.stats import hypergeom
def npmi(cells,degenerate_nan=True):
 t=np.asarray(cells,dtype=np.float64);a,b,c,d=np.moveaxis(t,-1,0);n=a+b+c+d
 joint=(a+.5)/(n+2);pu=(a+b+1)/(n+2);pv=(a+c+1)/(n+2)
 result=np.log(joint/(pu*pv))/-np.log(joint)
 if degenerate_nan:result=np.where((n>0)&(a+b>0)&(a+c>0)&(c+d>0)&(b+d>0),result,np.nan)
 return result
def table(x,y,eligible,groups=None):
 x=np.asarray(x,bool);y=np.asarray(y,bool);m=np.asarray(eligible,bool)
 if groups is None:w=m.astype(float)
 else:
  _,inv=np.unique(np.asarray(groups)[m],return_inverse=True)
  sizes=np.bincount(inv);w=np.zeros(len(x),float);w[m]=1/sizes[inv]
 return np.array([w[x&y].sum(),w[x&~y].sum(),w[~x&y].sum(),w[~x&~y].sum()])
def exact_positive_p(cells):
 a,b,c,d=np.moveaxis(np.asarray(cells,dtype=np.int64),-1,0)
 return hypergeom.sf(a-1,a+b+c+d,a+b,a+c)
def bh(p):
 p=np.asarray(p,float);order=np.argsort(p,kind="stable");ranked=p[order]*len(p)/np.arange(1,len(p)+1)
 adjusted=np.minimum.accumulate(ranked[::-1])[::-1].clip(0,1)
 result=np.empty_like(p);result[order]=adjusted;return result
def moments_to_cells(z):
 n,u,v,j=np.moveaxis(z,-1,0)
 return np.stack([j,u-j,v-j,n-u-v+j],axis=-1)
def edge_bootstrap(P,M,sources,targets,W,chunk=128,progress=None):
 b=len(W);k=len(sources);points=np.empty((k,4),np.float64);boot=np.empty((b,k),np.float32);eligible_hashes=[]
 import hashlib
 for lo in range(0,k,chunk):
  hi=min(lo+chunk,k);X=P[:,sources[lo:hi]];Y=P[:,targets[lo:hi]]
  mask=M[:,sources[lo:hi]]&M[:,targets[lo:hi]]
  F=np.empty((len(P),(hi-lo)*4),np.float32)
  F[:,0::4]=mask;F[:,1::4]=X&mask;F[:,2::4]=Y&mask;F[:,3::4]=X&Y&mask
  points[lo:hi]=moments_to_cells(F.sum(0,dtype=np.float64).reshape(-1,4))
  z=(W@F).reshape(b,hi-lo,4);cells=moments_to_cells(z)
  assert cells.min()>=0
  boot[:,lo:hi]=npmi(cells)
  eligible_hashes.extend(hashlib.sha256(mask[:,i].tobytes()).hexdigest() for i in range(hi-lo))
  if progress:progress(hi,k)
 return points,boot,eligible_hashes

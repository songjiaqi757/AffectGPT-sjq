"""Label-free pretrained encoders with original CueModel pooling. CPU sharded extraction."""
import argparse,os,time
import numpy as np
import torch
from torch import nn
from .common import *
class Mean(nn.Module):
 def forward(self,x,mask):
  w=mask.unsqueeze(-1).to(x.dtype);return (x*w).sum(1)/w.sum(1)

def run(m,shard,shards,threads):
 torch.set_num_threads(threads);torch.set_num_interop_threads(1)
 from cue_student.models import CueModel
 from cue_student.data import make_collator
 cfg=read(GRAPH/f'cue_student/configs/{m}.json');cfg.update(encoder_train='frozen',frame_batch_size=8,decode_threads=1)
 n={'text':15,'audio':17,'visual':10}[m];dim={'text':1538,'audio':1024,'visual':768}[m]
 rows=read(ROOT/'data/input_rows.json');ii=np.arange(len(rows))[shard::shards]
 out=ROOT/f'features/{m}_{shard:02d}.npz';status=out.with_suffix('.json');out.parent.mkdir(exist_ok=True)
 if out.exists():
  z=np.load(out);assert np.array_equal(z['indices'],ii);event('features_exist',modality=m,shard=shard);return
 model=CueModel(cfg).eval().requires_grad_(False);model.head=nn.Identity() if m=='text' else Mean();coll=make_collator(cfg)
 x=np.zeros((len(ii),dim),np.float32);available=np.zeros(len(ii),bool);errors=[];start=time.time();batchsize=16 if m=='text' else 1
 checkpoint=out.with_name(out.stem+'.partial.npz');done=0
 if checkpoint.exists():
  z=np.load(checkpoint);x[:]=z['features'];available[:]=z['available'];done=int(z['done'])
  errors=read(status).get('errors',[]) if status.exists() else []
 for st in range(done,len(ii),batchsize):
  inds=ii[st:st+batchsize];items=[]
  for i in inds:
   r=rows[int(i)]
   # Only raw sample fields enter collators. No supervision or Teacher notes.
   a={k:r[k] for k in ('sample_id','text','audio_path','video_path') if k in r}
   a.update(targets=np.zeros(n,np.float32),label_mask=np.zeros(n,bool));items.append(a)
  try:
   with torch.inference_mode():f=model(coll(items)).float().numpy()
   assert f.shape==(len(inds),dim) and np.isfinite(f).all()
   x[st:st+len(inds)]=f;available[st:st+len(inds)]=True
  except Exception as exc:
   errors.append(dict(indices=inds.tolist(),sample_ids=[r['sample_id'] for r in items],error=repr(exc)))
   if m=='text' and len(inds)>1:
    for j,a in enumerate(items):
     try:
      with torch.inference_mode():f=model(coll([a])).float().numpy()[0]
      if np.isfinite(f).all():x[st+j]=f;available[st+j]=True
     except Exception as e:errors.append(dict(sample_id=a['sample_id'],error=repr(e)))
  end=min(st+batchsize,len(ii))
  if end%100<batchsize or end==len(ii):
   write(status,dict(modality=m,shard=shard,shards=shards,pid=os.getpid(),done=end,total=len(ii),elapsed_seconds=time.time()-start,available=int(available[:end].sum()),errors=errors,config=cfg,source_rows_sha256=sha(ROOT/'data/input_rows.json')))
   event('extract',modality=m,shard=shard,done=end,total=len(ii),elapsed=round(time.time()-start,1),errors=len(errors))
  if end%500<batchsize:
   save(checkpoint,indices=ii,features=x,available=available,done=np.array(end))
 save(out,indices=ii,features=x,available=available)
 meta=read(status);meta.update(complete=True,sha256=sha(out),feature_semantics='Unsupervised pretrained encoder features; zero Teacher/model-supervised labels entered encoder',input_fingerprint=digest([dict(sample_id=rows[int(i)]['sample_id'],text=rows[int(i)].get('text'),media_assets=rows[int(i)].get('media_assets')) for i in ii]));write(status,meta)
 if checkpoint.exists():checkpoint.unlink()
 event('feature_complete',modality=m,shard=shard,total=len(ii),seconds=time.time()-start)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--modality',choices=['text','audio','visual'],required=True);a.add_argument('--shard',type=int,required=True);a.add_argument('--shards',type=int,required=True);a.add_argument('--threads',type=int,default=4);v=a.parse_args();run(v.modality,v.shard,v.shards,v.threads)

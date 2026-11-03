"""Export only model tensors from a static Torch ZIP description; never unpickle."""
import argparse,datetime,json,math,sys,zipfile
from pathlib import Path
from zoneinfo import ZoneInfo
import torch
from safetensors import safe_open
from safetensors.torch import save_file
from .common import ROOT,read,sha,atomic_json,require,p0_context,canonical
from .checkpoint_metadata import read_checkpoint_metadata,Opaque
def tensor_digest(t):
 import hashlib
 return hashlib.sha256(t.contiguous().numpy().tobytes()).hexdigest()
def export_one(spec,destination):
 source=Path(spec["path"]);before=source.stat()
 require(sha(source)==spec["sha256"],"Source checkpoint SHA256 mismatch")
 meta=read_checkpoint_metadata(source)
 require(meta["signature"]==spec["signature"] and meta["config"]==spec["config"],"Source metadata mismatch")
 require(meta["assets"]==spec["encoder_assets"],"Encoder binding mismatch")
 tensors={};descriptions={}
 with zipfile.ZipFile(source) as z:
  prefix=next(n[:-len("data.pkl")] for n in z.namelist() if n.endswith("/data.pkl"))
  byteorder=prefix+"byteorder"
  require(byteorder not in z.namelist() or z.read(byteorder)==b"little","Unsupported checkpoint byteorder")
  for name,ref in meta["model"].items():
   require(isinstance(ref,Opaque) and ref.kind=="torch._utils _rebuild_tensor_v2","Unsupported tensor reconstruction")
   storage,offset,shape,stride,*rest=ref.args
   require(isinstance(storage,Opaque) and storage.kind=="persistent_storage","Unsupported storage")
   tag,dtype,key,location,count=storage.args
   require(tag=="storage" and isinstance(dtype,Opaque) and dtype.kind=="global" and dtype.args=="torch FloatStorage","Only float32 model weights supported")
   require(location=="cpu" and isinstance(key,str) and key.isdigit(),"Unexpected tensor storage location/key")
   require(type(offset) is int and offset>=0 and all(type(x) is int and x>0 for x in shape) and len(shape)==len(stride) and all(type(x) is int and x>=0 for x in stride),"Invalid tensor geometry")
   require(offset+sum((size-1)*step for size,step in zip(shape,stride))<count,"Tensor storage overrun")
   raw=z.read(prefix+"data/"+key)
   require(len(raw)==count*4,"Storage size mismatch")
   tensor=torch.frombuffer(bytearray(raw),dtype=torch.float32).as_strided(shape,stride,storage_offset=offset).clone().contiguous()
   require(bool(torch.isfinite(tensor).all()),"Non-finite checkpoint tensor")
   tensors[name]=tensor
   descriptions[name]=dict(shape=list(shape),dtype="float32",sha256=tensor_digest(tensor))
 destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
 tmp=destination.with_suffix(".tmp")
 save_file(tensors,str(tmp),metadata={"format":"pt","source_checkpoint_sha256":spec["sha256"],"conversion":"static_zip_model_tensors_only_v1"})
 tmp.replace(destination)
 with safe_open(str(destination),framework="pt",device="cpu") as f:
  require(set(f.keys())==set(tensors),"Export tensor set changed")
  for name in f.keys():require(tensor_digest(f.get_tensor(name))==descriptions[name]["sha256"],"Export changed tensor: "+name)
 require((source.stat().st_size,source.stat().st_mtime_ns)==(before.st_size,before.st_mtime_ns),"Checkpoint changed during export")
 return dict(path=str(destination),sha256=sha(destination),source_checkpoint=str(source),source_sha256=spec["sha256"],signature=meta["signature"],config=meta["config"],cue_ids=meta["cue_ids"],encoder_assets=meta["assets"],train_positive=meta["train_positive"],train_negative=meta["train_negative"],tensor_count=len(tensors),tensor_descriptions=descriptions,conversion="static_zip_to_safetensors_lossless_v1",pickle_callables_executed=False)
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",required=True);args=p.parse_args()
 output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
 pointer,lock,inputs=p0_context();exports={}
 for m,spec in inputs["checkpoints"].items():
  print("Exporting "+m,flush=True)
  record=export_one(spec,output/"weights"/(m+".safetensors"))
  atomic_json(output/("export_"+m+".json"),record);exports[m]=record
  print("Verified lossless export "+m,flush=True)
 assets={}
 for spec in inputs["checkpoints"].values():
  for filename,expected in spec["encoder_assets"]["sha256"].items():
   path=str(Path(spec["encoder_assets"]["directory"])/filename)
   if path not in assets:assets[path]=sha(path)
   require(assets[path]==expected,"Encoder asset drift: "+path)
 atomic_json(output/"inputs_p0.json",inputs)
 atomic_json(output/"weight_exports.json",dict(exports=exports,p0_lock_id=lock["lock_id"],encoder_asset_sha256=assets,completed_at_beijing=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()))
 print("WEIGHT EXPORT COMPLETE",flush=True)
if __name__=="__main__":main()

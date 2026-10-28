"""Fingerprint local pretrained assets used by every continuation experiment."""
from pathlib import Path
from amg_runtime.common import read,sha,atomic_json
from .common import ROOT,now
def main():
 run=Path(read(ROOT/"amg_finetune/runs/current.json")["path"]);assets={}
 for name in ["Qwen2.5-7B-Instruct","clip-vit-large-patch14","chinese-hubert-large"]:
  base=ROOT/"AffectGPT/models"/name
  for p in sorted(base.rglob("*")):
   if p.is_file() and p.suffix in [".json",".safetensors",".bin",".txt",".model"]:
    st=p.stat();assets[str(p)]=dict(sha256=sha(p),bytes=st.st_size,mtime_ns=st.st_mtime_ns)
  print("HASHED",name,flush=True)
 atomic_json(run/"model_assets_manifest.json",dict(created_at_beijing=now(),assets=assets))
if __name__=="__main__":main()

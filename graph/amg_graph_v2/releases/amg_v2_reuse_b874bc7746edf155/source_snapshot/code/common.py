import hashlib,json,os,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
GRAPH=ROOT.parent

def read(p): return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False));t.replace(p)
def event(stage,**v):print(json.dumps(dict(time=time.strftime('%Y-%m-%d %H:%M:%S'),stage=stage,**v),ensure_ascii=False),flush=True)
def save(p,**v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_name(p.stem+'.tmp.npz');np.savez_compressed(t,**v);t.replace(p)

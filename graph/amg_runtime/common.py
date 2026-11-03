"""Versioned server-only AMG runtime utilities."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import hashlib,json,math,os,tempfile
from graph_paths import Path
ROOT=Path("/ai/sjq/AffectGPT-sjq/graph")
MODALITIES=("text","audio","visual")
OFFSETS={"text":(0,15),"audio":(15,32),"visual":(32,42)}
def read(path):return json.loads(Path(path).read_text())
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for block in iter(lambda:f.read(8*1024*1024),b""):h.update(block)
 return h.hexdigest()
def atomic_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=path.name+".",suffix=".tmp")
 try:
  with os.fdopen(fd,"w") as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write("\n")
  os.replace(tmp,path)
 finally:
  if os.path.exists(_graph_resolve_path(tmp)):os.unlink(_graph_resolve_path(tmp))
def require(test,message):
 if not test:raise ValueError(message)
def finite_number(value):
 return type(value) in (int,float) and math.isfinite(value)
def release_path(path=None):
 if path is None:path=read(ROOT/"amg_runtime/releases/current.json")["path"]
 return Path(path).resolve()
def p0_context():
 pointer=read(ROOT/"amg_graph/preflight/current.json");lock=read(pointer["version_lock"])
 require(canonical({k:v for k,v in lock.items() if k!="lock_id"})==lock["lock_id"],"P0 lock identity mismatch")
 require(lock["lock_id"]==pointer["lock_id"],"P0 pointer drift")
 inputs=read(pointer["query_engine_inputs"])
 require(_graph_hash_matches(pointer['query_engine_inputs'], lock['query_engine_inputs_sha256'], sha(pointer['query_engine_inputs'])),"P0 inputs changed")
 require(read(inputs["cue_release"]["pointer"])["release_id"]==lock["cue_release_id"],"Current Cue release drift")
 require(read(inputs["graph"]["pointer"])["release_id"]==lock["graph_release_id"],"Current graph release drift")
 return pointer,lock,inputs

import os,json,fcntl,datetime,hashlib,uuid,errno,time
from graph_paths import Path
from amg_runtime.common import read as _read_json,sha as _sha_file,canonical,atomic_json,require
from amg_unified_eval.common import env,now
G=Path("/ai/sjq/AffectGPT-sjq/graph")
ROOT=G
PROJECT=G.parent
PYTHON="/ai/sjq/miniconda3/envs/vllm/bin/python"
def fs_retry(action,label):
 for attempt in range(12):
  try:return action()
  except OSError as exc:
   if exc.errno not in {errno.ESTALE,errno.EIO,errno.ETIMEDOUT,errno.EINTR,errno.EAGAIN} or attempt==11:raise
   print(json.dumps(dict(event="transient_shared_filesystem_retry",path=str(label),attempt=attempt+1,errno=exc.errno),ensure_ascii=False),flush=True)
   time.sleep(min(.25*2**attempt,3))
def read(path):return fs_retry(lambda:_read_json(path),path)
def sha(path):return fs_retry(lambda:_sha_file(path),path)
def lock(path,blocking=False):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);f=fs_retry(lambda:path.open("a+"),path)
 try:fcntl.flock(f,fcntl.LOCK_EX|(0 if blocking else fcntl.LOCK_NB));return f
 except BlockingIOError:f.close();return None
def load_plan(run):
 p=read(Path(run)/"plan.json");require(p["plan_id"]==canonical({k:v for k,v in p.items() if k!="plan_id"}),"Plan changed");return p
def verify_code(run):
 for f,h in read(Path(run)/"code_manifest.json")["files"].items():require(sha(f)==h,"Code changed: "+f)
def write(p,x):return fs_retry(lambda:atomic_json(Path(p),x),p)
def checkpoint(run,base,epoch):
 f=Path(run)/f"from_{base}"/"checkpoints.json"
 if not f.exists():return None
 return next((x for x in read(f) if x["epoch"]==epoch),None)
def status(run,name,**kw):write(Path(run)/(name+".json"),dict(at=now(),pid=os.getpid(),**kw))

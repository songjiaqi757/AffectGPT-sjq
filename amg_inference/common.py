"""Server-only prediction jobs, dependency gates and immutable provenance."""
import os,json,fcntl,contextlib
from pathlib import Path
from amg_runtime.common import read,sha,canonical,atomic_json,require
from amg_finetune_nogc.common import ROOT,PYTHON,now
DATASETS={"MER2023":411,"MER2024":1169,"MELD":2610,"IEMOCAPFour":1241,"CMUMOSI":686,"CMUMOSEI":4659,"SIMS":457,"SIMSv2":1034,"OVMERDPlus":532}
def plan(run):
 p=read(Path(run)/"plan.json")
 require(p["plan_id"]==canonical({k:v for k,v in p.items() if k!="plan_id"}),"Inference plan changed")
 return p
def verify(run):
 p=plan(run)
 for filename,digest in read(Path(run)/"code_manifest.json")["files_sha256"].items():
  require(sha(ROOT/filename)==digest,"Code drift: "+filename)
 for d,s in p["datasets"].items():require(sha(s["path"])==s["sha256"],"Dataset input drift: "+d)
 require(sha(Path(p["training_run"])/"plan.json")==p["training_plan_sha256"],"Training plan drift")
 tp=read(Path(p["training_run"])/"plan.json")
 for filename,name in [("original_config.json","original_config_sha256"),("query_engine_config.json","query_config_sha256")]:
  require(sha(Path(p["training_run"])/filename)==tp["inputs"][name],"Frozen config drift: "+filename)
 for filename,binding in read(Path(p["training_run"])/"model_assets_manifest.json")["assets"].items():
  st=Path(filename).stat();require((st.st_size,st.st_mtime_ns)==(binding["bytes"],binding["mtime_ns"]),"Pretrained model asset drift")
 require(sha(Path(run)/"source_probe.json")==read(Path(run)/"code_manifest.json")["source_probe_sha256"],"Source capacity probe changed")
 return p
def locked(path,blocking=False):
 f=Path(path).open("a+")
 try:fcntl.flock(f,fcntl.LOCK_EX|(0 if blocking else fcntl.LOCK_NB));return f
 except BlockingIOError:f.close();return None
def key(sample_id):return canonical(sample_id)
def cache_path(run,row):return Path(run)/"cache"/(key(row["sample_id"])+".json")
def cue_input(row):return {k:row[k] for k in ["sample_id","text","audio_path","video_path"]}
def evidence(run,row,p):
 x=read(cache_path(run,row))
 require(x["plan_id"]==p["plan_id"] and x["input_id"]==canonical(cue_input(row)),"Cache input mismatch")
 require(x["cache_id"]==canonical({k:v for k,v in x.items() if k!="cache_id"}),"Cache identity mismatch")
 require(x["evidence"]["query_config_id"]==p["query_config_id"],"Query config drift")
 return x
def gate(training_run,gpu):
 f=Path(training_run)/f"gpu_{gpu}_queue_status.json"
 if not f.exists():return False
 s=read(f)
 expected=[30,40,50] if gpu==0 else [35,45]
 return s["state"]=="complete" and s["completed"]==expected
def checkpoint(p,job):
 f=Path(p["training_run"])/f"from_{job['base_epoch']}"/"checkpoints.json"
 if not f.exists():return None
 doc=read(f);items=doc if isinstance(doc,list) else doc.get("checkpoints",[])
 matches=[x for x in items if x["epoch"]==job["epoch"]]
 require(len(matches)<=1,"Duplicate saved epoch")
 if not matches:return None
 x=matches[0]
 require(Path(x["path"]).is_file(),"Published checkpoint absent")
 return x
def job_files(run):return sorted((Path(run)/"jobs").glob("*.json"))
def counts(run):
 out={}
 for f in job_files(run):
  s=read(f)["state"];out[s]=out.get(s,0)+1
 return out
def dispatch_files(run,p):
 files=job_files(run);policy_path=Path(run)/"job_dispatch.json"
 if not policy_path.exists():return files
 policy=read(policy_path)
 if not policy.get("enabled"):return files
 require(policy["plan_id"]==p["plan_id"],"Dispatch policy belongs to another plan")
 ids=policy["job_ids"];require(len(ids)==len(set(ids)) and set(ids)<=set(f.stem for f in files),"Invalid priority job selection")
 rank={jid:i for i,jid in enumerate(ids)}
 return sorted((f for f in files if f.stem in rank),key=lambda f:rank[f.stem])
def acquire_job(run,p):
 for f in dispatch_files(run,p):
  h=locked(f.with_suffix(".lock"))
  if h is None:continue
  j=read(f)
  if j["state"] in ["complete","failed"] or not checkpoint(p,j):h.close();continue
  if j.get("attempts",0)>=3:
   j.update(state="failed",error="Three failed worker attempts");atomic_json(f,j);h.close();continue
  j.update(state="running",attempts=j.get("attempts",0)+1,pid=os.getpid(),gpu=os.environ.get("CUDA_VISIBLE_DEVICES"),updated_at_beijing=now())
  atomic_json(f,j);return f,h,j
 return None

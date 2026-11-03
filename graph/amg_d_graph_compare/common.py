from graph_paths import hash_matches as _graph_hash_matches
import os,sys,json,time,fcntl,datetime,subprocess,hashlib
from graph_paths import Path
from zoneinfo import ZoneInfo
from amg_runtime.common import read,sha,canonical,atomic_json,require
ROOT=Path("/ai/sjq/AffectGPT-sjq/graph")
PYTHON=Path("/ai/sjq/miniconda3/envs/vllm/bin/python")
SOURCE=ROOT/"amg_finetune/runs/graph_continue_no_gc_20261022_164836"
OLD_INFER=ROOT/"amg_inference/runs/graph_225_20261022_174537"
def now():return datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
def plan(run):
 p=read(Path(run)/"plan.json");require(p["plan_id"]==canonical({k:v for k,v in p.items() if k!="plan_id"}),"Plan identity changed");return p
def verify_code(run):
 p=Path(run)/"code_manifest.json"
 for name,digest in read(p)["files"].items():require(_graph_hash_matches(ROOT / name, digest, sha(ROOT / name)),"Code drift: "+name)
def environment(gpu=None):
 e=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",TOKENIZERS_PARALLELISM="false",OMP_NUM_THREADS="4",MKL_NUM_THREADS="4",OPENBLAS_NUM_THREADS="1",PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True",VLLM_WORKER_MULTIPROC_METHOD="spawn")
 if gpu is not None:e["CUDA_VISIBLE_DEVICES"]=str(gpu)
 for k in ["RANK","WORLD_SIZE","LOCAL_RANK"]:e.pop(k,None)
 return e
def locked(path,blocking=False):
 f=Path(path).open("a+")
 try:fcntl.flock(f,fcntl.LOCK_EX|(0 if blocking else fcntl.LOCK_NB));return f
 except BlockingIOError:f.close();return None
def launch(run,module,args,log,gpu=None):
 with (Path(run)/log).open("ab",buffering=0) as f:
  return subprocess.Popen([str(PYTHON),"-u","-B","-m",module,"--run",str(run)]+args,cwd=ROOT,env=environment(gpu),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
def sid_key(sid):return canonical(sid)
def source_cache(p,sid):return Path(p["source_cache"])/(sid+".json")
def target_cache(p,sid):return Path(p["target_cache"])/(sid_key(sid)+".json")
def evidence_for(run,variant,row,training=False,expected_cache_id=None):
 p=plan(run)
 if "active_variant" not in p:p=plan(Path(run)/(variant+"_plan"))
 if training:
  x=read(Path(p["oof_cache"])/(row["sample_id"]+".json"))
  require(x["sample_id"]==row["sample_id"] and x["cache_id"]==canonical({k:v for k,v in x.items() if k!="cache_id"}),"Invalid OOF cache")
  require(x["input_record_id"]==canonical({k:row[k] for k in ["sample_id","text","audio_path","video_path"]}),"OOF input drift")
  require(expected_cache_id is None or x["cache_id"]==expected_cache_id,"OOF cache changed since full verification")
  expected=p["oof_folds"][str(x["fold"])]
  require(x["fold_graph_id"]==expected["graph_id"] and x["evidence"]["query_config_id"]==expected["query_config_id"],"OOF fold/query mismatch")
  return x["evidence"]
 x=read(target_cache(p,row["sample_id"]));require(x["sample_id"]==row["sample_id"],"Target cache sample mismatch")
 require(x["cache_id"]==canonical({k:v for k,v in x.items() if k!="cache_id"}) and x["evidence"]["query_config_id"]==p["query_config_id"] and x["evidence"]["graph_release_id"]==p["graph_release_id"],"Target graph cache drift")
 return x["evidence"]
def jobs(run):return [read(p) for p in sorted((Path(run)/"jobs").glob("*.json"))]
def complete_count(run):return sum(j["state"]=="complete" for j in jobs(run))
def checkpoint(run,variant,epoch):
 f=Path(run)/variant/"checkpoints.json"
 if not f.exists():return None
 return next((x for x in read(f) if x["epoch"]==epoch),None)

load_plan=plan

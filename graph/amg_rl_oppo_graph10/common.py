import os,sys,json,hashlib,datetime,fcntl,tempfile
from pathlib import Path
from zoneinfo import ZoneInfo
GRAPH=Path('/ai/sjq/AffectGPT-sjq/graph')
BASE=GRAPH.parent/'AffectGPT'
RL=Path('/ai/sjq/AffectGPT-RL')
OPPO=Path('/ai/sjq/OPPO')
PYTHON='/ai/sjq/miniconda3/envs/vllm_affect_oppo/bin/python'
DATASETS=['CMUMOSI','CMUMOSEI','SIMS','SIMSv2','MER2023','MER2024','MELD','IEMOCAPFour','OVMERDPlus']
DISCRETE={'MER2023','MER2024','MELD','IEMOCAPFour'}
DIMENSION={'CMUMOSI','CMUMOSEI','SIMS','SIMSv2'}
def now():return datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix=p.name+'.',suffix='.tmp',dir=p.parent)
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def lock(p,blocking=False):
 f=open(p,'a+')
 try:fcntl.flock(f,fcntl.LOCK_EX|(0 if blocking else fcntl.LOCK_NB));return f
 except BlockingIOError:f.close();return None
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def plan(run):
 p=read(Path(run)/'plan.json')
 require(p['plan_id']==canonical({k:v for k,v in p.items() if k!='plan_id'}),'Plan changed')
 for path,h in p['protected_sources'].items():require(sha(path)==h,'Source changed: '+path)
 return p
def graph_evidence(p,inventory,d,name):
 sid=d+'::'+name;spec=inventory[sid]
 f=Path(p['graph_cache_directory'])/(canonical(sid)+'.json')
 require(sha(f)==spec['sha256'],'Graph evidence changed '+sid)
 b=read(f)
 require(b['sample_id']==sid and b['cache_id']==spec['cache_id'],'Cache identity mismatch')
 require(b['evidence']['graph_release_id']==p['graph_release_id'] and b['evidence']['query_config_id']==p['query_config_id'],'Wrong graph version')
 return b
def format_graph(p,evidence,tokenizer):
 from amg_bcd.policy import format_evidence
 return format_evidence(evidence,tokenizer,512,variant='D')
def env():
 return dict(os.environ,PYTHONUTF8='1',PYTHONPATH=str(GRAPH),PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',VLLM_WORKER_MULTIPROC_METHOD='spawn',MERBENCH_LLM_PATH='/ai/sjq/OPPO/models/Qwen2.5-7B-Instruct')

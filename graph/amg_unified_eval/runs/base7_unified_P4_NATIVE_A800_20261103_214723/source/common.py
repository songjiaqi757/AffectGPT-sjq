import os,json,hashlib,fcntl,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from amg_graph_v2.common import read,write,sha,digest
PROJECT=Path('/ai/sjq/AffectGPT-sjq');GRAPH=PROJECT/'graph';ROOT=GRAPH/'amg_unified_eval';PYTHON='/ai/sjq/miniconda3/envs/vllm/bin/python'
def now():return datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def key(s):return digest(s)
def lock(path,blocking=False):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);f=path.open('a+')
 try:fcntl.flock(f,fcntl.LOCK_EX|(0 if blocking else fcntl.LOCK_NB));return f
 except BlockingIOError:f.close();return None
def env():return dict(os.environ,PYTHONPATH=str(GRAPH),CUDA_VISIBLE_DEVICES='0',PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True',VLLM_WORKER_MULTIPROC_METHOD='spawn')
def plan(run):
 p=read(Path(run)/'plan.json');assert p['plan_id']==digest({k:v for k,v in p.items() if k!='plan_id'}),'Plan changed';return p

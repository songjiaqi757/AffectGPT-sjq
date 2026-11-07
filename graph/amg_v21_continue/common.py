import datetime,json,hashlib
from pathlib import Path
from zoneinfo import ZoneInfo
from amg_runtime.common import read,sha,canonical,atomic_json,require
ROOT=Path("/ai/sjq/AffectGPT-sjq/graph")
PROJECT=ROOT.parent
PYTHON=Path("/ai/sjq/miniconda3/envs/vllm/bin/python")
def now():return datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
def load_plan(run):
 p=read(Path(run)/"plan.json");require(p["plan_id"]==canonical({k:v for k,v in p.items() if k!="plan_id"}),"Plan identity changed");return p
def verify_code(run):
 for f,h in read(Path(run)/"code_manifest.json")["files"].items():require(sha(f)==h,"Code changed: "+f)

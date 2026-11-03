from pathlib import Path
import datetime,json,os,hashlib
from zoneinfo import ZoneInfo
from amg_runtime.common import read,sha,canonical,atomic_json,require
ROOT=Path("/ai/sjq/AffectGPT-sjq")
PYTHON=Path("/ai/sjq/miniconda3/envs/vllm/bin/python")
def now():return datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
def load_plan(run):
 run=Path(run);p=read(run/"plan.json")
 require(p["plan_id"]==canonical({k:v for k,v in p.items() if k!="plan_id"}),"Plan identity mismatch")
 return p
def compact_query(result):
 keys=["schema_version","sample_id","runtime_release_id","graph_release_id","cue_release_id","query_input_id","query_config_id","query_result_id","policy_profile","policy_status","score_semantics","query_cues","appraisal_dimensions","emotion_candidates","explanation_paths","coverage","fallback"]
 return {k:result[k] for k in keys}
def bound_query(result,engine):
 names={k:dict(name=v.get("canonical_name",v.get("name",k)),node_type=v["node_type"]) for k,v in engine.nodes.items()}
 q=compact_query(result);q["node_names"]={k:names[k] for k in names if k in {c["cue_id"] for c in q["query_cues"]}|{e["emotion_id"] for e in q["emotion_candidates"]}|{s["state_id"] for d in q["appraisal_dimensions"] for s in d["state_supports"]}}
 return q
def verify_code(run):
 lock=read(Path(run)/"code_manifest.json")
 for relative,digest in lock["files_sha256"].items():require(sha(ROOT/relative)==digest,"Source drift: "+relative)
 return lock

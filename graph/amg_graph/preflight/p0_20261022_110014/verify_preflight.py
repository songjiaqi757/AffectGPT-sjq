"""Recheck a completed P0 artifact package and locked fingerprints without running models."""
import argparse,datetime,hashlib,json
from pathlib import Path
from zoneinfo import ZoneInfo
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest()
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
def verify(folder,full=False):
 folder=Path(folder).resolve();art=read(folder/"artifact_manifest.json")
 for name,expected in art["sha256"].items():
  assert sha(folder/name)==expected,"P0 artifact changed: "+name
 lock=read(folder/"version_lock.json")
 assert canonical({k:v for k,v in lock.items() if k!="lock_id"})==lock["lock_id"]
 report=read(folder/"preflight_audit.json");cfg=read(folder/"query_engine_inputs.json")
 assert report["p0_complete"] and all(c["passed"] for c in report["checks"])
 assert report["check_count"]==len(report["checks"])
 assert report["lock_id"]==lock["lock_id"]==art["lock_id"]
 assert sha(folder/"query_engine_inputs.json")==lock["query_engine_inputs_sha256"]
 assert sha(folder/"source_code_fingerprints.json")==lock["source_code_fingerprints_sha256"]
 assert sha(folder/"environment.json")==lock["environment_sha256"]
 assert sha(folder/"document_revision_v2_9.json")==lock["document_revision_sha256"]
 for label in ["input","output"]:
  assert sha(folder/("student_"+label+"_schema.json"))==cfg[label+"_schema_sha256"]
 assert lock["selected_runs"]==report["selected_runs"]==dict(text="text",audio="audio_full",visual="visual_full")
 assert cfg["gates"]["allow_engineering_development"] and not cfg["gates"]["allow_final_target_evaluation"]
 assert cfg["scores"]["active_deferred"]["active_mask"] is None
 assert cfg["scores"]["active_deferred"]["deferred_mask"] is None
 assert cfg["graph"]["frozen_build_constraints"]==dict(edge_min_source_groups=20,path_min_joint_source_groups=5)
 assert all(v is None for k,v in cfg["query_parameters"].items() if k!="status")
 assert cfg["cue_id_order"]==sum([read(Path(cfg["cue_release"]["path"])/"ontology.json")["cue_ids"][m] for m in ["text","audio","visual"]],[])
 inventory=read(folder/"checkpoint_inventory.json")
 assert len(inventory)==9
 for m,c in cfg["checkpoints"].items():
  assert c["sha256"]==lock["selected_checkpoint_sha256"][m]
  assert c["sha256"]==inventory[c["run"]]["sha256"]
  assert c["path"]==inventory[c["run"]]["checkpoint"]
 assert read(Path(cfg["cue_release"]["pointer"]))["release_id"]==lock["cue_release_id"]
 assert read(Path(cfg["graph"]["pointer"]))["release_id"]==lock["graph_release_id"]
 external=0
 if full:
  for p,expected in lock["input_fingerprints"].items():
   assert sha(p)==expected,"Locked input changed: "+p
   external+=1
 return dict(passed=True,checked_P0_artifacts=len(art["sha256"]),locked_input_files_rehashed=external,lock_id=lock["lock_id"],checked_at_beijing=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat())
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--directory",required=True);p.add_argument("--full",action="store_true");args=p.parse_args()
 print(json.dumps(verify(args.directory,args.full),ensure_ascii=False))

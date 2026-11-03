"""Verify every reused OOF record and grouped split without changing old artifacts."""
from pathlib import Path
from .common import *
def verify_oof(run,p):
 source=Path(p["oof_reference_run"]);records=read(run/"train_records.json");by_id={r["sample_id"]:r for r in records};manifest=read(source/"oof_manifest.json")
 require(manifest["complete"] and manifest["samples"]==len(records)==30755,"Incomplete OOF cache")
 require(sha(source/"oof_manifest.json")==p["oof_manifest_sha256"] and sha(source/"fold_assignment.json")==p["oof_assignment_sha256"],"OOF provenance changed")
 assignment=read(source/"fold_assignment.json")["assignments"];require(set(assignment)==set(by_id),"OOF membership mismatch")
 require({f.stem for f in Path(p["oof_cache"]).glob("*.json")}==set(by_id),"Missing or extra OOF cache")
 parent={sid:sid for sid in by_id}
 def group(s):
  while parent[s]!=s:parent[s]=parent[parent[s]];s=parent[s]
  return s
 def union(a,b):
  a,b=group(a),group(b)
  if a!=b:parent[max(a,b)]=min(a,b)
 seen={}
 for r in records:
  keys=[("group",r["group_id"])]+[(m,a["sha256"]) for m,a in r.get("media_assets",{}).items()]
  for key in keys:
   if key in seen:union(r["sample_id"],seen[key])
   else:seen[key]=r["sample_id"]
 require(all(assignment[s]==int(canonical([42,group(s)])[:12],16)%5 for s in by_id),"Grouped fold assignment changed")
 original_config=read(p["query_config_path"]);resources=[source/"oof_manifest.json",source/"fold_assignment.json"]
 for fold in range(5):
  folder=source/"folds"/str(fold);fm=read(folder/"manifest.json");cfg=read(folder/"query_config.json");expected=p["oof_folds"][str(fold)]
  fit=set(fm["fit_sample_ids"]);held=set(fm["held_sample_ids"])
  require(held=={s for s in by_id if assignment[s]==fold} and fit<=set(by_id),"Fold membership drift")
  require(not({group(s) for s in fit}&{group(s) for s in held}),"Held group or exact duplicate used to fit graph")
  require(all(by_id[s]["previous_role"]=="pseudo_train" for s in fit),"Fold graph includes non-training source role")
  require(fm["graph_release_id"]==expected["graph_id"] and sha(folder/"manifest.json")==expected["manifest_sha256"],"Fold manifest drift")
  require(canonical(cfg)==expected["query_config_id"],"Fold query identity drift")
  restored=dict(cfg);restored["graph_release_id"]=original_config["graph_release_id"];require(restored==original_config,"OOF query hyperparameters retuned")
  resources.extend([folder/n for n in ["manifest.json","query_config.json","graph.json","paths.json","inputs.json"]])
 inventory={}
 for i,row in enumerate(records):
  sid=row["sample_id"];x=read(Path(p["oof_cache"])/(sid+".json"));fold=assignment[sid];expected=p["oof_folds"][str(fold)]
  require(x["cache_id"]==canonical({k:v for k,v in x.items() if k!="cache_id"}),"Corrupt OOF record")
  require(x["sample_id"]==sid and x["fold"]==fold,"Wrong held fold cache")
  require(x["input_record_id"]==canonical({k:row[k] for k in ["sample_id","text","audio_path","video_path"]}),"OOF input changed")
  require(x["fold_graph_id"]==expected["graph_id"] and x["evidence"]["graph_release_id"]==expected["graph_id"] and x["evidence"]["query_config_id"]==expected["query_config_id"],"Wrong fold graph or query")
  original=read(source_cache(p,sid));require(x["source_cache_id"]==original["cache_id"],"Frozen Cue provenance changed")
  require(x["evidence"]["cue_release_id"]==p["cue_release_id"] and x["evidence"]["runtime_release_id"]==p["runtime_release_id"],"Cue/runtime drift")
  inventory[sid]=x["cache_id"]
  if (i+1)%5000==0:print("OOF_VERIFIED",i+1,flush=True)
 atomic_json(run/"oof_cache_inventory.json",inventory)
 report=dict(passed=True,samples=len(inventory),folds=5,group_and_exact_media_exclusion=True,all_record_hashes_and_inputs_valid=True,source_cue_cache_bound=True,query_parameters_unchanged=True,source_only=True,graph_only=True,cue_models_retrained=False,reference_run=str(source),reference_plan_id=p["oof_reference_plan_id"],inventory_sha256=sha(run/"oof_cache_inventory.json"),files_sha256={str(f):sha(f) for f in resources},completed_at_beijing=now())
 atomic_json(run/"oof_reuse_verification.json",report);return report

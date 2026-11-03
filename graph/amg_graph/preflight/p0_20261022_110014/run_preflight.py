"""P0 audit. Run only on Qiii; writes only inside its own preflight directory."""
import collections, contextlib, csv, datetime, hashlib, importlib.metadata, io, json, math, os, platform, re, subprocess, sys, traceback
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path("/ai/sjq/AffectGPT-sjq")
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(OUT))
from checkpoint_metadata import read_checkpoint_metadata,tensor_shape
def read(p):return json.loads(Path(p).read_text())
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
def write(name,v):
 p=OUT/name;p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
 return p
fingerprints={}
def sha(p):
 p=Path(p);before=p.stat();h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(8*1024*1024),b""):h.update(block)
 after=p.stat()
 assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),str(p)+" changed during hash"
 digest=h.hexdigest();fingerprints[str(p)]=digest
 return digest
checks=[]
def check(name,condition,details=None):
 if not bool(condition):raise AssertionError(name+": "+str(details))
 checks.append(dict(name=name,passed=True,details=details))
def event(s):print(datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),s,flush=True)
def package_versions():
 return {d.metadata["Name"]:d.version for d in importlib.metadata.distributions() if d.metadata.get("Name")}
def schema(name,fields,status):
 return dict(schema_id=name,format="JSON",fields=fields,status=status)
def main():
 event("P0 starting")
 started=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
 cue_pointer=ROOT/"cue_student/artifacts/current_release.json"
 graph_pointer=ROOT/"amg_graph/runs/current.json"
 cp=read(cue_pointer);gp=read(graph_pointer)
 release_path=Path(cp["path"]);graph_root=ROOT/"amg_graph/runs"/gp["run_id"]
 expected_release="2019ab786e4e065699a3f980291b1d300a17ee1ec9a18213672f620fd2823ac7"
 expected_graph="75d45e203722ce060829e0db17ce7348f24ef44c024f1e99ff310f050194a420"
 check("current_cue_release",cp["release_id"]==expected_release)
 check("current_graph_release",gp["release_id"]==expected_graph and gp["run_id"]=="amg_edges_v2_restore_diagnostic_20261022")
 sha(cue_pointer);sha(graph_pointer)
 protocol=read(graph_root/"manifest/protocol.json")
 check("graph_protocol_identity",canonical({k:v for k,v in protocol.items() if k!="release_id"})==gp["release_id"])
 check("graph_source_release",protocol["source_release_id"]==cp["release_id"] and Path(protocol["source_paths"]["release"])==release_path)
 protected={}
 for folder in [release_path,graph_root,ROOT/"emotion_nodes/runs/affectgpt_original_v1"]:
  for p in folder.rglob("*"):
   if p.is_file():protected[str(p)]=sha(p)
 event("Release and frozen graph file fingerprints captured")
 from cue_student.data import Release
 release=Release(release_path);rows=release.rows
 roles=collections.Counter(r["role"] for r in rows)
 expected_roles=dict(pseudo_train=27679,pseudo_validation=3076,gold_audit=300,diagnostic_reserved=200)
 check("role_counts",dict(roles)==expected_roles==cp["role_counts"]==release.manifest["split"]["role_counts"],dict(roles))
 check("unique_sample_ids",len({r["sample_id"] for r in rows})==31255)
 check("release_identity",release.manifest["release_id"]==expected_release)
 role_sets={role:{r["sample_id"] for r in rows if r["role"]==role} for role in roles}
 group_sets={role:{r["group_id"] for r in rows if r["role"]==role} for role in roles}
 media_sets={m:{role:{r["media_assets"][m]["sha256"] for r in rows if r["role"]==role} for role in roles} for m in ["audio","visual"]}
 for i,role in enumerate(roles):
  for other in list(roles)[i+1:]:
   check("sample_role_disjoint:"+role+":"+other,not(role_sets[role]&role_sets[other]))
   check("manifest_group_disjoint:"+role+":"+other,not(group_sets[role]&group_sets[other]))
   for m in media_sets:check("registered_exact_media_disjoint:"+m+":"+role+":"+other,not(media_sets[m][role]&media_sets[m][other]))
 role_ledger={}
 for role in roles:
  ids=sorted(role_sets[role]);groups=sorted(group_sets[role])
  role_ledger[role]=dict(samples=len(ids),groups=len(groups),sample_ids_canonical_sha256=canonical(ids),group_ids_canonical_sha256=canonical(groups))
 write("role_reconciliation.json",dict(release_id=expected_release,total=len(rows),roles=role_ledger,source_group_independence="manifest and registered exact hashes only; original/near-duplicate audit pending"))
 with (OUT/"role_reconciliation.csv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["role","samples","groups","sample_ids_canonical_sha256","group_ids_canonical_sha256"]);w.writeheader()
  for role,data in role_ledger.items():w.writerow(dict(role=role,**data))
 graph_roles=read(graph_root/"manifest/sample_roles.json")
 role_by_id={r["sample_id"]:r for r in rows}
 check("graph_member_roles_exact",graph_roles==[{k:r[k] for k in ["sample_id","group_id","role"]} for r in rows if r["role"] in ["pseudo_train","pseudo_validation"]])
 check("graph_contains_no_gold_or_reserved",not({r["sample_id"] for r in graph_roles}&(role_sets["gold_audit"]|role_sets["diagnostic_reserved"])))
 for name,expected in release.manifest["source_artifacts"].items():
  p=ROOT/"cue_annotation/runs/mercaptionplus"/name
  check("cue_source_artifact:"+name,sha(p)==expected)
 media_checked=0;real_roots=set()
 for r in rows:
  for m in ["audio","visual"]:
   asset=r["media_assets"][m];p=Path(asset["path"]);s=p.stat()
   check_ok=s.st_size==asset["bytes"] and s.st_mtime_ns==asset["mtime_ns"]
   if not check_ok:raise AssertionError("Media stat drift: "+str(p))
   media_checked+=1
   if media_checked<=2:real_roots.add(str(p.resolve().parent))
 check("all_media_paths_and_recorded_stat_identities",media_checked==62510,dict(paths=media_checked,content_rehashed=False,resolved_media_roots=sorted(real_roots)))
 cue_ids=sum([release.ontology["cue_ids"][m] for m in ["text","audio","visual"]],[])
 check("42_cue_order",list(map(lambda m:len(release.ontology["cue_ids"][m]),["text","audio","visual"]))==[15,17,10] and len(set(cue_ids))==42)
 event("Roles, registered exact-hash separation and 62,510 media stat identities verified")
 from amg_graph import verify
 check("verifier_uses_current_graph",verify.RUN==graph_root)
 captured={}
 def audit_only_write(path,value):
  check("verifier_write_redirected",Path(path)==graph_root/"manifest/verification.json")
  captured.update(value);write("graph_independent_verification.json",value)
 verify.write=audit_only_write
 log=io.StringIO()
 with contextlib.redirect_stdout(log):verify.main()
 (OUT/"graph_verification.log").write_text(log.getvalue())
 check("independent_graph_verification",captured.get("passed") is True)
 event("Recomputed all 11,576 candidate tables, FDR, bootstrap intervals and 3,209 path supports")
 graph=read(graph_root/"graph/graph.json")
 node_map={n["id"]:n for n in graph["nodes"]}
 counts=collections.Counter(n["node_type"] for n in graph["nodes"])
 check("node_counts",dict(counts)==dict(CueType=42,AppraisalDimension=6,AppraisalState=16,EmotionConcept=188))
 check("node_order",cue_ids==[n["id"] for n in graph["nodes"] if n["node_type"]=="CueType"])
 allowed={"CUE_TO_APPRAISAL_STATE":("CueType","AppraisalState"),"CUE_TO_EMOTION":("CueType","EmotionConcept"),"APPRAISAL_STATE_TO_EMOTION":("AppraisalState","EmotionConcept")}
 # Actual relation strings are required to match the frozen graph and its exported tables.
 relation_types={}
 for e in graph["statistical_edges"]:
  types=(node_map[e["source_node_id"]]["node_type"],node_map[e["target_node_id"]]["node_type"])
  if types not in allowed.values():raise AssertionError("Illegal statistical edge direction")
  old=relation_types.setdefault(e["relation_type"],types)
  if old!=types:raise AssertionError("Mixed relation endpoints")
  if not (math.isfinite(e["edge_weight"]) and 0<e["edge_weight"]<=1 and e["support_count_groups"]>=20 and e["source_split_version"]==expected_release):raise AssertionError("Invalid statistical edge")
 check("edge_directions_weights_support_and_release",len(relation_types)==3 and len(graph["statistical_edges"])==1048)
 app_ontology=read(graph_root/"ontology/appraisal_ontology_v2.3.json")
 expected_hierarchy={(d,s) for d,states in app_ontology["dimensions"].items() for s in states}
 check("fixed_hierarchy_exact",{(e["source_node_id"],e["target_node_id"]) for e in graph["ontology_edges"]}==expected_hierarchy and all(e["relation_type"]=="HAS_STATE" and e["edge_weight"]==1 for e in graph["ontology_edges"]))
 with (graph_root/"graph/paths_cue_appraisal_emotion.csv").open() as f:paths=list(csv.DictReader(f))
 with (graph_root/"graph/candidate_path_audit.csv").open() as f:candidates=list(csv.DictReader(f))
 selected_paths=[r for r in candidates if r["admitted"]=="True"]
 check("admitted_paths_exact",paths==selected_paths and len(paths)==2595 and all(int(r["joint_support_groups"])>=5 and int(r["joint_support_rule"])==5 for r in paths))
 edge_lookup={(e["source_node_id"],e["target_node_id"]):e for e in graph["statistical_edges"]}
 for p in paths:
  left=edge_lookup[(p["source_node_id"],p["appraisal_state_id"])];right=edge_lookup[(p["appraisal_state_id"],p["target_node_id"])]
  for field,key,edge in [("cue_appraisal_weight","edge_weight",left),("appraisal_emotion_weight","edge_weight",right),("cue_appraisal_support_groups","support_count_groups",left),("appraisal_emotion_support_groups","support_count_groups",right)]:
   if not math.isclose(float(p[field]),edge[key],rel_tol=1e-12,abs_tol=1e-15):raise AssertionError("Path/edge fields disagree")
 check("all_path_edge_weights_and_group_support_fields",True,len(paths))
 report_path=ROOT/"cue_student/reports/cue_training_report_20261021.json"
 training_report=read(report_path);sha(report_path)
 inventory={};assets_seen={};source_code={}
 for name,row in training_report["runs"].items():
  out=Path(row["output"]);ckpt_path=Path(row["best_checkpoint"])
  event("Checking checkpoint "+name)
  metadata=read_checkpoint_metadata(ckpt_path)
  manifest=read(out/"training_manifest.json");cfg=read(out/"config.resolved.json")
  check("checkpoint_training_report_status:"+name,row["state"]=="completed" and row["exit_code"]==0)
  for k in ["signature","code_hash","release_id","fixed_holdout_id","cue_ids","train_positive","train_negative","scope"]:
   check("checkpoint_manifest:"+name+":"+k,metadata[k]==manifest[k])
  check("checkpoint_release:"+name,metadata["release_id"]==expected_release and metadata["fixed_holdout_id"]==release.fixed_holdout_id)
  check("checkpoint_config:"+name,metadata["config"]==cfg==row["config"])
  modality=cfg["modality"];ids=release.ontology["cue_ids"][modality];sl=release.offsets[modality]
  check("checkpoint_cue_order:"+name,metadata["cue_ids"]==ids)
  train_indices=[i for i,r in enumerate(rows) if r["role"]=="pseudo_train" and release.mask[i,sl].any()]
  import numpy as np
  mask=release.mask[train_indices,sl];targets=release.targets[train_indices,sl]
  pos=((targets==1)&mask).sum(0).tolist();neg=((targets==0)&mask).sum(0).tolist()
  check("training_support_recomputed:"+name,pos==metadata["train_positive"] and neg==metadata["train_negative"] and manifest["train_samples"]==len(train_indices) and manifest["validation_samples"]==3076)
  expected_sig=canonical(dict(config=cfg,release_id=expected_release,assets=metadata["assets"],cue_ids=ids,code_hash=metadata["code_hash"],fixed_holdout_id=release.fixed_holdout_id))
  check("checkpoint_signature:"+name,metadata["signature"]==expected_sig==row["signature"])
  job_root=ROOT/"cue_student/jobs"/row["job"]
  archive=job_root/"source/cue_student"
  archive_hash={p.name:sha(p) for p in sorted(archive.glob("*.py"))}
  check("archived_training_code_hash:"+name,canonical(archive_hash)==metadata["code_hash"])
  live_hash={p.name:sha(p) for p in sorted((ROOT/"cue_student").glob("*.py"))}
  changes={k:dict(archived=archive_hash.get(k),current=live_hash.get(k)) for k in set(archive_hash)|set(live_hash) if archive_hash.get(k)!=live_hash.get(k)}
  check("all_original_cue_modules_unchanged:"+name,all(live_hash.get(k)==v for k,v in archive_hash.items()),list(changes))
  source_code[name]=dict(training_archive=str(archive),training_module_sha256=archive_hash,current_module_sha256=live_hash,additional_current_files=changes)
  check("encoder_manifest_binding:"+name,metadata["assets"]==manifest["model_assets"]==row["encoder_assets"])
  for filename,expected in metadata["assets"]["sha256"].items():
   p=Path(metadata["assets"]["directory"])/filename
   if str(p) not in assets_seen:assets_seen[str(p)]=sha(p)
   check("encoder_asset:"+name+":"+filename,assets_seen[str(p)]==expected)
  shapes={k:tensor_shape(v) for k,v in metadata["model"].items()}
  output_bias=[k for k,v in shapes.items() if k.startswith("head.") and k.endswith("bias") and v==[len(ids)]]
  check("output_head_dimension:"+name,len(output_bias)==1,output_bias)
  metrics=metadata["validation"]
  check("best_embedded_metrics:"+name,metrics==row["best_metrics"] and metadata["progress"]["global_step"]==row["best_step"])
  check("best_selection_metric:"+name,metrics["macro_ap"]==metadata["progress"]["best_score"] and metrics["masked_bce"]==metadata["progress"]["best_loss"])
  last_metrics=read(out/"validation.last.json")
  with np.load(out/"validation.last.npz",allow_pickle=False) as z:
   check("last_validation_ids:"+name,set(z["sample_ids"].tolist())==role_sets["pseudo_validation"])
  old_identity=training_report["checkpoint_identity"].get(str(ckpt_path),{})
  stat=ckpt_path.stat()
  check("checkpoint_historical_stat_identity:"+name,old_identity==dict(bytes=stat.st_size,mtime_ns=stat.st_mtime_ns))
  digest=sha(ckpt_path)
  for p in [out/"config.resolved.json",out/"training_manifest.json",out/"validation.last.json",out/"validation.last.npz",out/"events.jsonl",Path(row["config_path"]),job_root/"status.json"]:sha(p)
  validations=[]
  for line in (out/"events.jsonl").read_text().splitlines():
   item=json.loads(line)
   if item.get("event")=="validation":validations.append(item)
  check("best_epoch_selection_recomputed:"+name,bool(validations) and math.isclose(max(e["macro_ap"] for e in validations),metrics["macro_ap"],rel_tol=1e-12),len(validations))
  # The original training report already records the complete AP-selected best metrics.
  inventory[name]=dict(modality=modality,checkpoint=str(ckpt_path),sha256=digest,bytes=stat.st_size,mtime_ns=stat.st_mtime_ns,signature=metadata["signature"],code_hash=metadata["code_hash"],config=cfg,config_sha256=fingerprints[str(out/"config.resolved.json")],cue_ids=ids,output_dimensions=len(ids),head_tensor_shapes={k:v for k,v in shapes.items() if k.startswith("head.")},train_samples=len(train_indices),excluded_no_supervision=27679-len(train_indices),train_positive=pos,train_negative=neg,best_epoch=metadata["progress"]["epoch"],best_step=metadata["progress"]["global_step"],best_metrics=dict(macro_ap=metrics["macro_ap"],masked_bce=metrics["masked_bce"],macro_f1=metrics["macro_f1"],reference=metrics["reference"]),last_prediction_cache=dict(path=str(out/"validation.last.npz"),sha256=fingerprints[str(out/"validation.last.npz")],embedded_checkpoint_identity=False,metrics_equal_to_best=last_metrics==metrics,usable_as_best_predictions=False,reason="Cache stores no checkpoint hash; regenerate and bind to the locked checkpoint in P2/P4"),encoder_assets=metadata["assets"],temporal_architecture=metadata["temporal_architecture"],scope=metadata["scope"])
 write("checkpoint_inventory.json",inventory)
 selected=training_report["selected_by_validation_macro_ap"]
 for modality in ["text","audio","visual"]:
  options=[k for k,v in inventory.items() if v["modality"]==modality]
  best=sorted(options,key=lambda k:(-inventory[k]["best_metrics"]["macro_ap"],inventory[k]["best_metrics"]["masked_bce"],k))[0]
  check("existing_model_selection_reproduced:"+modality,selected[modality]==best)
 check("existing_selected_trio",selected==dict(text="text",audio="audio_full",visual="visual_full"))
 for p in [ROOT/"cue_student/jobs/latest_all_experiments.json",ROOT/"Cue 提取与训练执行方案.md",ROOT/"图构建.md"]:sha(p)
 event("All nine checkpoints and encoder assets verified; existing three-model selection reproduced")
 old_revision=read(graph_root/"manifest/document_revision.json")
 current_doc_hash=sha(ROOT/"图构建.md")
 frozen_hash=sha(Path(protocol["source_paths"]["source_plan"]))
 doc_text=(ROOT/"图构建.md").read_text()
 check("current_plan_has_v29_and_P0",bool(re.search(r"13[.]3.*P0",doc_text)) and "v2.9" in doc_text)
 check("frozen_source_plan_hash",frozen_hash==protocol["input_fingerprints"]["图构建.md"])
 document_revision=dict(current_document=str(ROOT/"图构建.md"),current_version="v2.9",current_sha256=current_doc_hash,previous_revision_record=str(graph_root/"manifest/document_revision.json"),previous_record_declared_version=old_revision["current_document_version"],previous_record_declared_sha256=old_revision["current_sha256"],previous_record_matches_live=current_doc_hash==old_revision["current_sha256"],frozen_build_plan=str(protocol["source_paths"]["source_plan"]),frozen_build_plan_sha256=frozen_hash,frozen_plan_unchanged=True,disposition="New P0 provenance only; retain the old v2.8 revision as historical; v2.9 adds execution plans and is not a graph build input")
 write("document_revision_v2_9.json",document_revision)
 versions=package_versions()
 expected_environment=read(ROOT/"cue_student/environment.verified.json")
 differences={k:dict(expected=v,current=importlib.metadata.version(k)) for k,v in expected_environment["packages"].items() if importlib.metadata.version(k)!=v}
 check("recorded_runtime_package_versions",not differences,differences)
 try:gpu=subprocess.check_output(["nvidia-smi","--query-gpu=name,uuid,driver_version","--format=csv,noheader"],text=True).strip()
 except (OSError,subprocess.CalledProcessError):gpu=None
 environment=dict(executable=sys.executable,python=sys.version,platform=platform.platform(),packages=versions,gpu_inventory=gpu,model_execution="none; CPU static ZIP/opcode metadata inspection only",network_model_calls=0,seeds=dict(graph=protocol["config"]["seed"],cue_checkpoints={k:v["config"]["seed"] for k,v in inventory.items()}),audit_randomness="none")
 write("environment.json",environment)
 git_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 git_status=subprocess.check_output(["git","status","--short"],cwd=ROOT,text=True)
 (OUT/"git_status.txt").write_text(git_status)
 source_files={}
 for folder in ["amg_graph","cue_student","appraisal_annotation","emotion_nodes"]:
  for p in sorted((ROOT/folder).glob("*.py")):source_files[str(p.relative_to(ROOT))]=sha(p)
 for p in [Path(__file__),OUT/"checkpoint_metadata.py"]:source_files[str(p.relative_to(ROOT))]=sha(p)
 write("source_code_fingerprints.json",dict(git_head=git_head,git_status_file=str(OUT/"git_status.txt"),current_sources=source_files,cue_training_archives=source_code,limitation="Core implementation directories are untracked; commit alone is insufficient, use individual SHA256 locks."))
 input_schema=schema("cue_predict_single_modality_input_existing_v1",dict(sample_id="string",text=dict(chinese="string or missing",english="string or missing"),audio_path="absolute server path or missing",video_path="absolute server path or missing"),"existing predictor input; per-modality required fields follow config; raw Teacher masks are never input")
 output_schema=schema("cue_predict_single_modality_output_existing_v1",dict(sample_id="string",modality="text|audio|visual",cue_ids="ordered 15|17|10 strings",scores="same-length sigmoid scores or null if unavailable",input_valid="boolean",thresholds="all 0.5",threshold_status="uncalibrated_0.5",selected_positive="score >= 0.5 cue IDs; not active/deferred policy",input_observation="per-modality input diagnostics when valid",error="string when invalid"),"documents existing code; unified 42D active/deferred schema remains P2")
 write("student_input_schema.json",input_schema);write("student_output_schema.json",output_schema)
 query_config=dict(schema_version="amg_query_inputs_p0_v1",status="locked_inputs_for_P2_P3_engineering_only",project_root=str(ROOT),cue_release=dict(pointer=str(cue_pointer),path=str(release_path),release_id=expected_release),graph=dict(pointer=str(graph_pointer),run_id=gp["run_id"],release_id=expected_graph,path=str(graph_root),graph_file=str(graph_root/"graph/graph.json"),path_file=str(graph_root/"graph/paths_cue_appraisal_emotion.csv"),frozen_build_constraints=dict(edge_min_source_groups=20,path_min_joint_source_groups=5),weight_semantics="95% bootstrap NPMI lower bound; statistical association, not probability"),cue_id_order=cue_ids,modality_offsets=dict(text=[0,15],audio=[15,32],visual=[32,42]),checkpoints={m:dict(run=selected[m],path=inventory[selected[m]]["checkpoint"],sha256=inventory[selected[m]]["sha256"],signature=inventory[selected[m]]["signature"],config=inventory[selected[m]]["config"],encoder_assets=inventory[selected[m]]["encoder_assets"]) for m in selected},scores=dict(transform="independent sigmoid",calibration=dict(status="uncalibrated",artifact=None),engineering_thresholds=[0.5]*42,threshold_status="uncalibrated_0.5",active_deferred=dict(status="not_frozen",artifact=None,active_mask=None,deferred_mask=None),modality_mask_source="actual runtime availability; never Teacher label_mask"),query_parameters=dict(status="pending_P4_preregistration_and_source_validation",query_min_support_groups=None,query_path_min_joint_support_groups=None,appraisal_dimension_evidence_thresholds=None,coverage_threshold=None,emotion_top_k=None,path_top_k=None,direct_two_hop_lambda=None),gates=dict(allow_engineering_development=True,allow_final_target_evaluation=False,reasons=["P1 source/near-duplicate and human audit pending","P2 unified interface and active/deferred freeze pending","P3 Query Engine pending","P4 query parameter selection pending","P5-P7 integration/experiments/final freeze pending"]),input_schema_sha256=sha(OUT/"student_input_schema.json"),output_schema_sha256=sha(OUT/"student_output_schema.json"),version_lock=str(OUT/"version_lock.json"))
 write("query_engine_inputs.json",query_config)
 check("pointers_unchanged_during_audit",sha(cue_pointer)==fingerprints[str(cue_pointer)] and read(cue_pointer)==cp and read(graph_pointer)==gp)
 event("Checking that all original release, graph and Emotion files are unchanged")
 unchanged={p:sha(p)==digest for p,digest in protected.items()}
 check("all_protected_files_unchanged",all(unchanged.values()),dict(files=len(unchanged)))
 lock=dict(schema_version="amg_p0_version_lock_v1",created_at_beijing=started,git_head=git_head,cue_release_id=expected_release,graph_release_id=expected_graph,role_counts=expected_roles,selected_runs=selected,selected_checkpoint_sha256={m:inventory[selected[m]]["sha256"] for m in selected},input_fingerprints=fingerprints,query_engine_inputs_sha256=sha(OUT/"query_engine_inputs.json"),source_code_fingerprints_sha256=sha(OUT/"source_code_fingerprints.json"),environment_sha256=sha(OUT/"environment.json"),document_revision_sha256=sha(OUT/"document_revision_v2_9.json"),status="P0_passed_with_explicit_downstream_gates")
 lock["lock_id"]=canonical(lock);write("version_lock.json",lock)
 warnings=[
  dict(code="historical_document_revision_is_v28",stage="P0 recorded",detail="Live v2.9 hash is separately locked; frozen build plan and old revision record are unchanged."),
  dict(code="cue_code_aggregate_has_added_migration_file",stage="P0 recorded",detail="All original training source modules match archived code; added cancel_diagnostic.py changes the aggregate current module hash. Exact live and archive hashes are recorded."),
  dict(code="uncalibrated_thresholds_and_no_active_deferred_freeze",stage="P2",detail="Current fixed 0.5 is an uncalibrated engineering threshold. No human calibration or deployment active/deferred artifact is claimed."),
  dict(code="validation_last_cache_not_bound_to_best",stage="P2/P4",detail="Do not reuse validation.last.npz as best predictions; regenerate from the locked trio and store checkpoint hashes."),
  dict(code="human_and_original_source_audits_pending",stage="P1",detail="Registered group/exact hash isolation is verified; original provenance and near duplicates remain unaudited."),
  dict(code="untracked_implementation",stage="P0 recorded",detail="Git commit is recorded; exact source hashes are required because core directories are currently untracked.")
 ]
 result=dict(schema_version="amg_preflight_audit_v1",p0_complete=True,status="passed_with_explicit_downstream_gates",started_at_beijing=started,finished_at_beijing=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),audit_directory=str(OUT),lock_id=lock["lock_id"],checks=checks,check_count=len(checks),role_counts=expected_roles,graph_counts=dict(nodes=252,statistical_edges=1048,fixed_edges=16,admitted_paths=2595),selected_runs=selected,protected_original_files_unchanged=len(unchanged),warnings=warnings,ready_for_engineering_P2_P3=True,ready_for_final_target_evaluation=False,scope=dict(trained_models=0,teacher_calls=0,graph_rebuilds=0,gpu_inference_runs=0,target_labels_used=False,local_project_files_saved=False),limitations=dict(media_verification="62,510 paths re-statted; existing source content SHA256 used for exact-duplicate grouping; media content not rehashed in P0",checkpoint_verification="Full-file SHA256, static metadata/signature/config/head shapes; no pickle callable executed and no forward inference in P0"))
 write("preflight_audit.json",result)
 lines=["# P0 运行前核验报告","","状态：P0 完成；可进入 P2/P3 工程开发，最终目标集评测仍受后续阶段门槛限制。","",f"完成时间（北京时间）：{result['finished_at_beijing']}",f"自动检查：{len(checks)} 项通过。",f"版本锁 ID：{lock['lock_id']}","","## 数据与图","",f"- 数据 release：{expected_release}",f"- 图 release：{expected_graph}","- 角色：训练 27,679；验证 3,076；人工审计 300；独立保留 200。","- 252 节点、1,048 统计边、16 层级边、2,595 合格路径。","- 独立复算 11,576 张列联表、完整候选族 FDR、bootstrap 区间和 3,209 条候选路径联合支持。","- 样本 ID、manifest 来源组及已登记媒体 SHA256 在各角色之间无交叉；原视频来源及近重复独立性仍属于 P1。",f"- {media_checked} 个媒体文件重新核验存在性、字节数与 mtime；本次不重新计算所有媒体内容哈希。",f"- {len(unchanged)} 个原数据/图/Emotion 文件前后指纹一致。","","## 已有模型选择的核验与锁定","","| 模态 | 已选实验 | Teacher 验证 macro AP | 有监督训练样本 |","|---|---|---:|---:|"]
 for m in ["text","audio","visual"]:
  x=inventory[selected[m]];lines.append(f"| {m} | {selected[m]} | {x['best_metrics']['macro_ap']:.10f} | {x['train_samples']} |")
 lines+=["","核验九组 best.pt 的完整文件 SHA256、静态元数据、签名、数据/holdout 身份、Cue 顺序、模型头维度、配置、支持计数、归档训练代码和编码器资产。选择复现已有训练报告的源域验证 macro AP 规则；无新训练和目标集数据使用。","","## 已明确记录的差异与后续门槛",""]
 lines += ["- "+w["code"]+"："+w["detail"] for w in warnings]
 lines += ["","## 入口与复现","","- preflight_audit.json：逐项检查结果与范围。","- version_lock.json：数据、图、模型、源码、环境、schema 指纹。","- query_engine_inputs.json：后续模块统一输入配置；P4 参数为空，active/deferred 未冻结。","- role_reconciliation.json / .csv：四种角色数量与成员/组 ID 摘要。","- checkpoint_inventory.json：九组权重及现有三路选择证据。","- document_revision_v2_9.json：本次文档修订来源记录，保留旧 v2.8 历史。","- run_preflight.py / checkpoint_metadata.py：服务器上的审计程序。","","本次不调用旧验证器的文档修订检查，因为它针对旧 v2.8；统计核验结果重定向到本目录，未覆盖冻结图的历史 verification.json。",""]
 (OUT/"README.md").write_text("\n".join(lines))
 artifact_manifest={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!="artifact_manifest.json" and p.name!="run.log"}
 write("artifact_manifest.json",dict(sha256=artifact_manifest,lock_id=lock["lock_id"]))
 # Publish only an explicit P0 entry point; current data and graph pointers are untouched.
 pointer=OUT.parent/"current.json"
 tmp=pointer.with_suffix(".tmp")
 tmp.write_text(json.dumps(dict(path=str(OUT),audit=str(OUT/"preflight_audit.json"),version_lock=str(OUT/"version_lock.json"),query_engine_inputs=str(OUT/"query_engine_inputs.json"),lock_id=lock["lock_id"],status=result["status"]),ensure_ascii=False,indent=2)+"\n")
 tmp.replace(pointer)
 event("P0 COMPLETE "+json.dumps(dict(audit=str(OUT),checks=len(checks),lock_id=lock["lock_id"],selected=selected),ensure_ascii=False))
if __name__=="__main__":
 try:main()
 except Exception as exc:
  write("failure.json",dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc()))
  traceback.print_exc();sys.exit(1)

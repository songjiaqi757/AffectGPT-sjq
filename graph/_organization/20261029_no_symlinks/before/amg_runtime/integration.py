"""Real GPU smoke checks on source validation inputs only; no labels or parameter selection."""
import argparse,copy,json,shutil,subprocess,tempfile,traceback
from pathlib import Path
import jsonschema
from .common import ROOT,read,sha,atomic_json,require,canonical
from .student import StudentRunner,CueAssembler
from .engine import GraphQueryEngine
from .versioning import load_release
def run(directory,device):
 import torch
 directory=Path(directory).resolve();out=directory/"validation";out.mkdir(exist_ok=True)
 manifest=load_release(directory);inputs=read(directory/"inputs_p0.json")
 schemas={p.name:read(p) for p in (directory/"schemas").glob("*.json")}
 members=read(Path(inputs["cue_release"]["path"])/"members.json")
 candidates=[r for r in members if r["role"]=="pseudo_validation" and all((r.get("text",{}).get(lang) or "").strip() for lang in ["chinese","english"])]
 candidates.sort(key=lambda r:(r.get("audio_duration",0)+r.get("visual_duration",0),r["sample_id"]))
 originals=[{k:r[k] for k in ["sample_id","text","audio_path","video_path"]} for r in candidates[:2]]
 require(len(originals)==2,"Need two source validation examples")
 checks=[]
 def check(name,condition,details=None):
  require(condition,name+": "+str(details));checks.append(dict(name=name,passed=True,details=details));print("PASS "+name,flush=True)
 runner=StudentRunner(directory,device=device);engine=GraphQueryEngine.from_release(directory)
 check("models_are_initially_lazy",not runner.models)
 if device.startswith("cuda"):
  torch.empty(0,device=device);torch.cuda.reset_peak_memory_stats(torch.device(device))
 batch=runner.predict_records(originals)
 check("all_three_modalities_available",all(all(row["modality_present"].values()) for row in batch))
 check("fixed_42D_outputs",all(len(row["scores"])==42 and all(v is not None for v in row["scores"]) for row in batch))
 check("exact_checkpoint_bindings",all(all(row["model_versions"][m]["checkpoint_sha256"]==inputs["checkpoints"][m]["sha256"] for m in inputs["checkpoints"]) for row in batch))
 repeat=runner.predict_records([originals[0]])[0]
 check("single_vs_batch_predictions_equal",batch[0]==repeat)
 again=runner.predict_records([originals[0]])[0]
 check("repeated_inference_bitwise_equal",repeat==again)
 cases=list(batch)
 source=originals[0]
 for language in ["chinese","english"]:
  record=dict(sample_id=source["sample_id"]+"_"+language+"_only",text={language:source["text"][language]})
  row=runner.predict_records([record])[0];cases.append(row)
  expected=[1.,0.] if language=="chinese" else [0.,1.]
  check(language+"_only_missing_language_mask",row["diagnostics"]["text"]["input_observation"]["language_present"]==expected)
  check(language+"_only_other_modalities_null",row["scores"][15:]==[None]*27)
 missing=dict(sample_id="P2_missing_all",text=dict(chinese="",english=None),audio_path=str(out/"not_present.wav"),video_path=str(out/"not_present.mp4"))
 row=runner.predict_records([missing])[0];cases.append(row)
 check("missing_all_scores_null",row["scores"]==[None]*42 and row["fallback"]["required"])
 check("missing_text_reason_explicit",row["diagnostics"]["text"]["error_code"]=="both_text_languages_unavailable")
 check("missing_media_reason_explicit",all(row["diagnostics"][m]["error_code"]=="media_unavailable" for m in ["audio","visual"]))
 for missing_modality,path_key in [("audio","audio_path"),("visual","video_path"),("text","text")]:
  rec=copy.deepcopy(source);rec["sample_id"]=source["sample_id"]+"_missing_"+missing_modality;rec.pop(path_key)
  prediction=runner.predict_records([rec])[0];cases.append(prediction)
  check("single_missing_"+missing_modality,not prediction["modality_present"][missing_modality] and sum(prediction["modality_present"].values())==2)
 # Invalid decodable content must be an explicit unavailable input, never a negative vector.
 for ext in ["wav","mp4"]:(out/("corrupt."+ext)).write_bytes(b"invalid test media")
 corrupt=dict(sample_id="P2_corrupt_av",audio_path=str(out/"corrupt.wav"),video_path=str(out/"corrupt.mp4"))
 row=runner.predict_records([corrupt])[0];cases.append(row)
 check("corrupt_media_falls_back",row["scores"]==[None]*42 and row["fallback"]["required"])
 # Real source text with enough tokens to exercise overlapping chunk coverage.
 long=dict(sample_id="P2_long_source_text",text={k:v*200 for k,v in source["text"].items()})
 row=runner.predict_records([long])[0];cases.append(row)
 check("long_text_all_chunks_used",len(row["diagnostics"]["text"]["input_observation"]["token_spans"])>2)
 runner.assembler=CueAssembler(inputs,read(directory/"cue_policy.json"),profile="deployment")
 dep=runner.predict_records([dict(sample_id="P2_deployment_gate",text=source["text"])])[0];cases.append(dep)
 check("deployment_policy_returns_empty",not any(dep["selected_mask"]) and dep["fallback"]["reason"]=="deployment_policy_pending_human_audit")
 runner.assembler=CueAssembler(inputs,read(directory/"cue_policy.json"),profile="engineering")
 excluded=runner.predict_records([dict(sample_id="P2_request_none",text=source["text"])],requested_mask=[False]*42)[0];cases.append(excluded)
 check("requested_mask_exclusion",not any(excluded["selected_mask"]) and "not_requested" in excluded["cue_states"])
 check("empty_batch_is_empty",runner.predict_records([])==[])
 for row in cases:jsonschema.validate(row,schemas["cue_query_42.schema.json"])
 check("all_real_cue_outputs_match_schema",True,len(cases))
 queries=[engine.query(row) for row in cases]
 for row in queries:jsonschema.validate(row,schemas["graph_query.schema.json"])
 check("all_real_graph_outputs_match_schema",True,len(queries))
 check("real_query_is_deterministic",engine.query(batch[0])==engine.query(batch[0]))
 check("real_graph_returns_some_supported_candidates",any(q["emotion_candidates"] for q in queries[:2]))
 frozen=read(Path(inputs["graph"]["path"])/"manifest/protocol.json")
 for name in ["graph/graph.json","graph/paths_cue_appraisal_emotion.csv"]:check("frozen_graph_unchanged:"+name,sha(Path(inputs["graph"]["path"])/name)==frozen["artifacts"][name])
 called=[]
 fallback=engine.query_or_fallback(next(row for row in cases if row["sample_id"]=="P2_missing_all"),lambda:called.append("baseline") or dict(status="original_affectgpt_callback_test"))
 check("fallback_adapter_invoked",called==["baseline"] and fallback["baseline_output"]["status"]=="original_affectgpt_callback_test")
 with tempfile.TemporaryDirectory(prefix="drift_",dir=out) as temp:
  temp=Path(temp)
  for relative in manifest["files"]:
   path=temp/relative;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(directory/relative,path)
  shutil.copyfile(directory/"release_manifest.json",temp/"release_manifest.json")
  policy=read(temp/"cue_policy.json");policy["thresholds"][0]=.6;atomic_json(temp/"cue_policy.json",policy)
  try:load_release(temp)
  except ValueError as error:check("policy_drift_rejected","fingerprint" in str(error))
  else:raise AssertionError("Policy drift accepted")
 for row in [dict(sample_id="forbidden",emotion="happy"),dict(sample_id="forbidden2",label_mask=[1]*42)]:
  try:runner.predict_records([row])
  except ValueError:pass
  else:raise AssertionError("Label-bearing input accepted")
 check("label_bearing_inference_inputs_rejected",True)
 atomic_json(out/"cue_smoke_predictions.json",cases);atomic_json(out/"query_smoke_results.json",queries);atomic_json(out/"fallback_example.json",fallback)
 with (out/"query_audit.jsonl").open("w") as f:
  for row in queries:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n")
 metrics=dict(peak_allocated_bytes=torch.cuda.max_memory_allocated(torch.device(device)),peak_reserved_bytes=torch.cuda.max_memory_reserved(torch.device(device))) if device.startswith("cuda") else {}
 result=dict(passed=True,checks=checks,check_count=len(checks),runtime_release_id=manifest["release_id"],source_validation_sample_ids=[r["sample_id"] for r in originals],derived_boundary_cases=True,cue_prediction_cases=len(cases),query_cases=len(queries),gpu_device=device,gpu_memory=metrics,teacher_calls=0,training_steps=0,graph_updates=0,target_datasets_used=False,full_validation_parameter_selection_performed=False,baseline_model_run=False,note="AffectGPT callback routing tested; actual AffectGPT model integration belongs to P5. This is a source-domain engineering smoke check, not an accuracy evaluation.")
 atomic_json(out/"integration_report.json",result)
 print(json.dumps(dict(passed=True,checks=len(checks),cases=len(cases),runtime_release_id=manifest["release_id"]),ensure_ascii=False))
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument("--release",required=True);p.add_argument("--device",default="cuda:0");args=p.parse_args()
 try:run(args.release,args.device)
 except Exception as exc:
  atomic_json(Path(args.release)/"validation/integration_failure.json",dict(type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc()));raise
if __name__=="__main__":main()

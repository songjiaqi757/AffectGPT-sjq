"""Post-selection integrity and public CLI verification; never tunes parameters."""
import csv,json,math,os,subprocess,sys
from pathlib import Path
ROOT=Path("/ai/sjq/AffectGPT-sjq");sys.path.insert(0,str(ROOT))
from amg_runtime.common import read,sha,canonical,require,atomic_json
from amg_validation.finalize import selection_key
def verify(run):
 run=Path(run).resolve();reg=read(run/"preregistration.json");selection=read(run/"selection_manifest.json")
 require(selection["selection_release_id"]==canonical({k:v for k,v in selection.items() if k!="selection_release_id"}),"Selection manifest identity mismatch")
 require(reg["preregistration_id"]==canonical({k:v for k,v in reg.items() if k!="preregistration_id"}),"Preregistration changed")
 delivery=read(run/"delivery_manifest.json")
 for relative,digest in delivery["files_sha256"].items():require(sha(run/relative)==digest,"Delivery drift: "+relative)
 config=read(run/"query_engine_config.json")
 require(sha(run/"query_engine_config.json")==selection["config_sha256"] and canonical(config)==selection["config_id"],"Final config mismatch")
 for name,relative in [("preregistration_sha256","preregistration.json"),("predictions_sha256","cue_predictions.jsonl"),("references_sha256","references.json"),("evaluation_code_sha256","evaluation_code_manifest.json")]:
  require(sha(run/relative)==selection["inputs"][name],"Input fingerprint mismatch: "+relative)
 codes=read(run/"evaluation_code_manifest.json")["source_code_sha256"]
 for name,digest in codes.items():require(sha(ROOT/name)==digest,"Evaluation source changed")
 grid=read(run/"stage_B_grid_results.json")
 winner=sorted(grid["results"],key=selection_key)[0]
 require(winner["candidate_id"]==grid["selected"]["candidate_id"]==selection["selection"]["selected_stage_B_candidate"],"Selection tie-break not reproduced")
 with (run/"per_sample_metrics.csv").open() as f:rows=list(csv.DictReader(f))
 ids=[r["sample_id"] for r in rows];require(ids==reg["validation_sample_ids"] and len(ids)==3076,"Metric rows not exactly validation members")
 valid=[r for r in rows if r["emotion_reference_valid"]=="True"]
 require(len(valid)==selection["emotion_valid_samples"]==3001,"Emotion mask denominator mismatch")
 f1=math.fsum(float(r["emotion_f1"]) for r in valid)/len(valid)
 require(abs(f1-selection["metrics"]["emotion_sample_macro_f1"])<1e-14,"Per-sample F1 does not reproduce report")
 selected_indexes={0,1538,3075};cue_subset=[];expected=[];query_ids=[]
 with (run/"cue_predictions.jsonl").open() as f:
  for i,line in enumerate(f):
   if i in selected_indexes:cue_subset.append(json.loads(line))
 with (run/"per_sample_query_results.jsonl").open() as f:
  for i,line in enumerate(f):
   row=json.loads(line);query_ids.append(row["sample_id"])
   require(row["query_result_id"]==canonical({k:v for k,v in row.items() if k!="query_result_id"}),"Query result checksum mismatch")
   require(row["query_config_id"]==selection["config_id"],"A query used a different configuration")
   if i in selected_indexes:expected.append(row)
 require(query_ids==reg["validation_sample_ids"],"Query log membership differs")
 atomic_json(run/"cli_verification_inputs.json",cue_subset)
 command=[sys.executable,"-m","amg_runtime.cli","query","--release",reg["runtime_path"],"--query-config",str(run/"query_engine_config.json"),"--input",str(run/"cli_verification_inputs.json"),"--output",str(run/"cli_verification_outputs.json")]
 result=subprocess.run(command,cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"),capture_output=True,text=True)
 (run/"cli_verification.log").write_text(result.stdout+result.stderr);require(result.returncode==0,"Public CLI failed")
 require(read(run/"cli_verification_outputs.json")==expected,"Public CLI differs from selected outputs")
 pointer=read(ROOT/"amg_validation/runs/current.json")
 require(pointer["selection_release_id"]==selection["selection_release_id"] and pointer["query_config_id"]==selection["config_id"],"Published entry mismatch")
 report=dict(passed=True,validation_members=3076,emotion_valid_reference=3001,all_query_checksums_verified=True,all_queries_use_frozen_selected_config=True,all_delivery_hashes_verified=True,selection_rule_reproduced=True,per_sample_emotion_F1_reproduced=True,public_CLI_cases_matched=len(expected),source_code_fingerprints_verified=True,selection_release_id=selection["selection_release_id"],config_id=selection["config_id"],target_data_used=False)
 atomic_json(run/"verification_report.json",report)
 for relative in ["verification_report.json","verify_p4.py","cli_verification_inputs.json","cli_verification_outputs.json"]:delivery["files_sha256"][relative]=sha(run/relative)
 atomic_json(run/"delivery_manifest.json",delivery);print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":verify(sys.argv[1])

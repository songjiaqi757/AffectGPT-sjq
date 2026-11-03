"""Validate complete prediction membership and choose pre-registered per-dimension gates."""
import argparse,json
from graph_paths import Path
from amg_runtime.common import read,sha,canonical,atomic_json,require
from .evaluation import predictions,engine_for,appraisal_features,feature_prediction,state_metrics,appraisal_metrics
def prepare(run):
 run=Path(run);reg=read(run/"preregistration.json")
 for w in range(2):require(read(run/("worker_"+str(w)+"_status.json"))["state"]=="complete","Prediction workers incomplete")
 require({p.stem for p in (run/"predictions").glob("*.json")}==set(reg["validation_sample_ids"]),"Prediction cache membership differs")
 qs=predictions(run);refs=read(run/"references.json")
 require([q["sample_id"] for q in qs]==[r["sample_id"] for r in refs]==reg["validation_sample_ids"],"Reference/prediction alignment mismatch")
 base=engine_for(run,{})
 assignment={r["sample_id"]:r for w in range(2) for r in read(run/"inputs"/("worker_"+str(w)+".json"))}
 for q in qs:
  base._validate_cues(q)
  require(read(run/"predictions"/(q["sample_id"]+".json"))["record_sha256"]==canonical(assignment[q["sample_id"]]),"Raw input provenance mismatch")
 with (run/"cue_predictions.jsonl").open("w") as f:
  for q in qs:f.write(json.dumps(q,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n")
 atomic_json(run/"prediction_manifest.json",dict(samples=len(qs),sample_ids_digest=canonical([q["sample_id"] for q in qs]),sha256=sha(run/"cue_predictions.jsonl"),runtime_release_id=reg["runtime_release_id"],preregistration_id=reg["preregistration_id"],invalid_modality_counts={m:sum(not q["modality_present"][m] for q in qs) for m in ["text","audio","visual"]},no_query_samples=sum(not any(q["selected_mask"]) for q in qs),roles=["pseudo_validation"],gold_reserved_target_used=False))
 features=[appraisal_features(base,q) for q in qs];atomic_json(run/"appraisal_features.json",features)
 rows=[];profiles=[]
 for index,coverage in enumerate(reg["candidate_grid"]["minimum_coverage"]):
  chosen={}
  for d,states in base.dimensions.items():
   options=[]
   for delta in reg["candidate_grid"]["dimension_min_evidence"]:
    thresholds={dim:(delta if dim==d else 0.) for dim in base.dimensions}
    pred=[feature_prediction(f,base.dimensions,thresholds,coverage)[d] for f in features]
    metrics=state_metrics([r["appraisal"][d] for r in refs],pred,states)
    option=dict(profile_index=index,minimum_coverage=coverage,dimension_id=d,delta=delta,metrics=metrics)
    options.append(option)
   winner=sorted(options,key=lambda o:(-round(o["metrics"]["macro_f1"] or 0.,12),-round(o["metrics"]["coverage"] or 0.,12),-o["delta"]))[0]
   chosen[d]=winner["delta"]
   for o in options:o["selected"]=o["delta"]==winner["delta"];rows.append(o)
  pred=[feature_prediction(f,base.dimensions,chosen,coverage) for f in features]
  profiles.append(dict(profile_index=index,minimum_coverage=coverage,dimension_min_evidence=chosen,appraisal_metrics=appraisal_metrics(refs,pred,base.dimensions)))
 atomic_json(run/"stage_A_results.json",dict(preregistration_id=reg["preregistration_id"],results=rows))
 atomic_json(run/"stage_A_profiles.json",profiles)
 require(min(e["support_count_groups"] for e in base.graph["statistical_edges"])>=20,"Edge filter aliases are not equivalent")
 require(min(int(p["joint_support_groups"]) for p in base.paths.values())>=5,"Path filter aliases are not equivalent")
 atomic_json(run/"support_alias_proof.json",dict(query_support_values=reg["candidate_grid"]["query_min_support_groups"],query_joint_values=reg["candidate_grid"]["query_path_min_joint_support_groups"],all_12_combinations_identical_on_frozen_admitted_graph=True,reason="All frozen statistical edges have >=20 source groups and all frozen paths have >=5 joint source groups. Query filters never restore rejected candidates.",selected_values_must_be_explained_as_tie_break=True,graph_release_id=reg["graph_release_id"]))
 atomic_json(run/"status.json",dict(phase="stage_A_complete",samples=len(qs),profiles=len(profiles),preregistration_id=reg["preregistration_id"]))
 print(json.dumps(dict(stage="A",samples=len(qs),threshold_profiles=profiles),ensure_ascii=False))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);args=p.parse_args();prepare(args.run)

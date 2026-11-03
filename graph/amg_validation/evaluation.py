"""Source-only metrics and exact reuse of frozen-engine query supports."""
import copy,json,math
from graph_paths import Path
import numpy as np
from amg_runtime.common import read,canonical,atomic_json,require
from amg_runtime.engine import GraphQueryEngine

def predictions(run,allow_partial=False):
 run=Path(run);reg=read(run/"preregistration.json");rows=[]
 for sid in reg["validation_sample_ids"]:
  path=run/"predictions"/(sid+".json")
  if not path.exists():
   if allow_partial:continue
   raise ValueError("Missing prediction: "+sid)
  row=read(path);q=row["prediction"]
  require(row["preregistration_id"]==reg["preregistration_id"] and q["sample_id"]==sid and q["runtime_release_id"]==reg["runtime_release_id"],"Prediction identity mismatch")
  require(q["query_input_id"]==canonical({k:v for k,v in q.items() if k!="query_input_id"}),"Prediction checksum mismatch")
  rows.append(q)
 return rows

def engine_for(run,parameters):
 reg=read(Path(run)/"preregistration.json");runtime=Path(reg["runtime_path"])
 config=read(runtime/"query_config.engineering.json");config["purpose"]="source_validation_candidate"
 config["notes"]="P4 preregistration "+reg["preregistration_id"]+"; source validation only; graph build rules unchanged."
 config["query_parameters"].update(parameters)
 engine=GraphQueryEngine.from_release(runtime)
 engine.config=config;engine._validate_config()
 return engine

def state_metrics(truth,pred,states):
 valid=[i for i,v in enumerate(truth) if v is not None];details={}
 for state in states:
  tp=sum(truth[i]==state and pred[i]==state for i in valid)
  fp=sum(truth[i]!=state and pred[i]==state for i in valid)
  fn=sum(truth[i]==state and pred[i]!=state for i in valid)
  positive=tp+fn
  details[state]=dict(tp=tp,fp=fp,fn=fn,positive_reference=positive,precision=(tp/(tp+fp) if tp+fp else 0.) if positive else None,recall=tp/positive if positive else None,f1=2*tp/(2*tp+fp+fn) if positive else None,evaluable=positive>0)
 eligible=[r for r in details.values() if r["evaluable"]]
 return dict(macro_precision=math.fsum(r["precision"] for r in eligible)/len(eligible) if eligible else None,macro_recall=math.fsum(r["recall"] for r in eligible)/len(eligible) if eligible else None,macro_f1=math.fsum(r["f1"] for r in eligible)/len(eligible) if eligible else None,valid_reference=len(valid),predicted_on_valid=sum(pred[i] is not None for i in valid),coverage=sum(pred[i] is not None for i in valid)/len(valid) if valid else None,abstention=1-sum(pred[i] is not None for i in valid)/len(valid) if valid else None,unscorable_predictions=sum(t is None and p is not None for t,p in zip(truth,pred)),states=details)

def appraisal_metrics(refs,preds,dimensions):
 details={d:state_metrics([r["appraisal"][d] for r in refs],[r.get(d) for r in preds],states) for d,states in dimensions.items()}
 states=[s for d in details.values() for s in d["states"].values() if s["evaluable"]]
 valid=sum(d["valid_reference"] for d in details.values());covered=sum(d["predicted_on_valid"] for d in details.values())
 return dict(macro_state_precision=math.fsum(s["precision"] for s in states)/len(states) if states else 0.,macro_state_recall=math.fsum(s["recall"] for s in states)/len(states) if states else 0.,macro_state_f1=math.fsum(s["f1"] for s in states)/len(states) if states else 0.,valid_reference_dimensions=valid,covered_reference_dimensions=covered,valid_dimension_coverage=covered/valid if valid else 0.,abstention=1-covered/valid if valid else 1.,per_dimension=details)

def appraisal_features(engine,cue):
 q={c:w for c,w in zip(engine.ids,cue["query_weights"]) if w>0};z=math.fsum(q.values())
 ca={k:e for k,e in engine.ca.items() if k[0] in q}
 a={s:math.fsum(q[c]*e["edge_weight"] for (c,t),e in ca.items() if t==s)/z if z else 0. for s in engine.state_dim}
 sc={s:math.fsum(q[c] for c,t in ca if t==s)/z if z else 0. for s in engine.state_dim}
 mass={d:math.fsum(a[s] for s in states) for d,states in engine.dimensions.items()}
 cov={d:math.fsum(q[c] for c in q if any((c,s) in ca for s in states))/z if z else 0. for d,states in engine.dimensions.items()}
 return dict(sample_id=cue["sample_id"],state_support=a,state_coverage=sc,dimension_evidence=mass,dimension_coverage=cov)

def feature_prediction(feature,dimensions,thresholds,coverage):
 out={}
 for d,states in dimensions.items():
  gate=feature["dimension_evidence"][d]>0 and feature["dimension_evidence"][d]>=thresholds[d] and feature["dimension_coverage"][d]>=coverage
  candidates=[s for s in states if gate and feature["state_support"][s]>0 and feature["state_coverage"][s]>=coverage]
  candidates.sort(key=lambda s:(-feature["state_support"][s],s));out[d]=candidates[0] if candidates else None
 return out

def result_appraisal(result,dimensions):
 by_dim={d["dimension_id"]:d for d in result["appraisal_dimensions"]}
 return {d:by_dim[d]["display_candidates"][0]["state_id"] if d in by_dim and by_dim[d]["display_candidates"] else None for d in dimensions}

def rerank(base,lam,k,path_k):
 candidates=[]
 for row in base.get("candidate_audit",[]):
  r=dict(row)
  r["association_score"]=lam*r["direct_score"]+(1-lam)*r["two_hop_score"] if r["direct_available"] and r["two_hop_available"] else r["direct_score"] if r["direct_available"] else r["two_hop_score"]
  candidates.append(r)
 candidates.sort(key=lambda r:(-r["association_score"],r["emotion_id"]))
 selected=candidates[:k];ids={r["emotion_id"] for r in selected}
 all_paths=[p for p in base.get("path_audit",[]) if p["emotion_id"] in ids]
 return dict(sample_id=base["sample_id"],query_cues=base["query_cues"],appraisal_dimensions=base["appraisal_dimensions"],emotion_candidates=selected,explanation_paths=all_paths[:path_k],available_candidate_count=len(candidates),available_selected_path_count=len(all_paths),query_coverage=base["coverage"]["query"])

def preview(result):
 # A fixed evidence serialization, not the final P5 AffectGPT prompt or tokenizer.
 value=dict(schema="graph_evidence_preview_v1",score_semantics="Statistical association support; not probabilities, causes or final labels.",cue_evidence=result["query_cues"],appraisal=[dict(dimension_id=d["dimension_id"],status=d["status"],evidence_mass=d["evidence_mass"],query_coverage=d["query_coverage"],candidates=[{k:s[k] for k in ["state_id","association_support","relative_support","query_coverage"]} for s in d["display_candidates"]]) for d in result["appraisal_dimensions"]],emotion_candidates=result["emotion_candidates"],paths=result["explanation_paths"])
 text=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
 return text

def emotion_case(reference,result):
 predicted={r["emotion_id"] for r in result["emotion_candidates"]};gt=set(reference["emotion_ids"]);n=len(predicted);tp=len(predicted & gt)
 if reference["emotion_valid"]:
  p=tp/n if n else 0.;r=tp/len(gt);f=2*tp/(n+len(gt))
 else:p=r=f=float("nan")
 covered=len({p["emotion_id"] for p in result["explanation_paths"]}&predicted)/n if n else 0.
 text=preview(result)
 return [p,r,f,float(bool(n)),float(n),float(result["available_candidate_count"]),float(len(result["explanation_paths"])),float(result["available_selected_path_count"]),covered,float(len(text)),float(len(text.encode("utf-8"))),result["query_coverage"]]

FIELDS=["emotion_precision","emotion_recall","emotion_f1","nonempty_query","emotion_candidates","available_emotion_candidates","displayed_paths","available_paths_for_selected_emotions","explained_candidate_fraction","context_characters","context_utf8_bytes","graph_query_coverage"]

def case_summary(array,refs):
 mask=np.array([r["emotion_valid"] for r in refs],bool)
 require(mask.any(),"No evaluable Emotion references")
 mean=lambda col:float(np.mean(array[:,FIELDS.index(col)]))
 return dict(emotion_sample_macro_precision=float(np.mean(array[mask,0])),emotion_sample_macro_recall=float(np.mean(array[mask,1])),emotion_sample_macro_f1=float(np.mean(array[mask,2])),emotion_valid_reference=int(mask.sum()),emotion_valid_query_coverage=float(np.mean(array[mask,3])),overall_query_coverage=mean("nonempty_query"),emotion_candidate_count_mean=mean("emotion_candidates"),available_emotion_candidate_count_mean=mean("available_emotion_candidates"),path_count_mean=mean("displayed_paths"),available_path_count_mean=mean("available_paths_for_selected_emotions"),explained_candidate_fraction_mean=mean("explained_candidate_fraction"),context_characters_mean=mean("context_characters"),context_utf8_bytes_mean=mean("context_utf8_bytes"),graph_query_weight_coverage_mean=mean("graph_query_coverage"))

"""Evaluate all lambda/K variants by exact reuse of invariant native query supports."""
import argparse,json,time,traceback
from pathlib import Path
import numpy as np
from amg_runtime.common import read,sha,canonical,atomic_json,require
from .evaluation import predictions,engine_for,feature_prediction,result_appraisal,rerank,preview,emotion_case,case_summary,appraisal_metrics,FIELDS
def run_profile(run,index):
 run=Path(run);reg=read(run/"preregistration.json");profile=read(run/"stage_A_profiles.json")[index]
 qs=predictions(run);refs=read(run/"references.json");features=read(run/"appraisal_features.json")
 base_params=dict(query_min_support_groups=20,query_path_min_joint_support_groups=5,dimension_min_evidence=profile["dimension_min_evidence"],minimum_coverage=profile["minimum_coverage"],emotion_top_k=188,path_top_k=1000,direct_two_hop_lambda=.5,branch="full")
 engine=engine_for(run,base_params)
 variants=[(lam,k) for lam in reg["candidate_grid"]["direct_two_hop_lambda"] for k in reg["candidate_grid"]["emotion_top_k"]]
 result_array=np.full((len(variants),len(qs),len(FIELDS)),np.nan,dtype=np.float64)
 verify_indexes={0,997,2049,3075};proofs=0;native_checks={}
 app_predictions=[];start=time.time()
 def status(state,done,error=None):
  atomic_json(run/("profile_"+str(index)+"_status.json"),dict(state=state,completed=done,total=len(qs),profile_index=index,elapsed_seconds=time.time()-start,error=error))
 try:
  status("running",0)
  for i,(cue,ref,feature) in enumerate(zip(qs,refs,features)):
   base=engine.query(cue);app=result_appraisal(base,engine.dimensions);app_predictions.append(app)
   require(app==feature_prediction(feature,engine.dimensions,profile["dimension_min_evidence"],profile["minimum_coverage"]),"Stage A/native appraisal mismatch")
   for v,(lam,k) in enumerate(variants):
    derived=rerank(base,lam,k,20);result_array[v,i]=emotion_case(ref,derived)
    if i in verify_indexes:
     if v not in native_checks:
      params=dict(base_params,direct_two_hop_lambda=lam,emotion_top_k=k,path_top_k=20)
      native_checks[v]=engine_for(run,params)
     native=native_checks[v].query(cue)
     require(derived["emotion_candidates"]==native["emotion_candidates"] and derived["explanation_paths"]==native["explanation_paths"],"Cached/native ranking or paths mismatch")
     require(preview(derived)==preview(native),"Cached/native evidence preview mismatch");proofs+=1
   if (i+1)%100==0 or i+1==len(qs):status("running",i+1);print(json.dumps(dict(profile=index,completed=i+1,total=len(qs))),flush=True)
  app=appraisal_metrics(refs,app_predictions,engine.dimensions)
  require(app==profile["appraisal_metrics"],"Stage A appraisal aggregate mismatch")
  summaries=[]
  for v,(lam,k) in enumerate(variants):
   metrics=case_summary(result_array[v],refs);metrics.update(appraisal_macro_state_f1=app["macro_state_f1"],appraisal_macro_state_precision=app["macro_state_precision"],appraisal_macro_state_recall=app["macro_state_recall"],appraisal_valid_dimension_coverage=app["valid_dimension_coverage"],objective=.5*(app["macro_state_f1"]+metrics["emotion_sample_macro_f1"]))
   summaries.append(dict(profile_index=index,minimum_coverage=profile["minimum_coverage"],dimension_min_evidence=profile["dimension_min_evidence"],direct_two_hop_lambda=lam,emotion_top_k=k,metrics=metrics))
  atomic_json(run/("profile_"+str(index)+"_results.json"),dict(summaries=summaries,appraisal_metrics=app,preregistration_id=reg["preregistration_id"],runtime_release_id=reg["runtime_release_id"],native_derived_equality_checks=proofs,all_3076_appraisal_predictions_match_native=True))
  np.savez_compressed(run/("profile_"+str(index)+"_per_sample.npz"),values=result_array,sample_ids=np.asarray(reg["validation_sample_ids"]),fields=np.asarray(FIELDS),lambdas=np.asarray([l for l,k in variants]),emotion_k=np.asarray([k for l,k in variants]))
  status("complete",len(qs))
 except Exception as exc:
  status("failed",len(app_predictions),type(exc).__name__+": "+str(exc))
  atomic_json(run/("profile_"+str(index)+"_failure.json"),dict(error=str(exc),traceback=traceback.format_exc()));raise
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);p.add_argument("--index",type=int,required=True);args=p.parse_args();run_profile(args.run,args.index)

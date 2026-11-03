"""Source-domain statistical edges; no model/API calls and no target datasets."""
from graph_paths import resolve_path as _graph_resolve_path
import collections,csv,hashlib,json,os,shutil,time,warnings
from graph_paths import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from .data import BASE,PROJECT,read,write,load,sha
from .stats import npmi,exact_positive_p,bh,edge_bootstrap
RUN=BASE/"runs"/os.environ.get("AMG_RUN_ID","wheel5_level1_alias10_full_20261025")
RELATIONS=["CUE_TO_APPRAISAL_STATE","CUE_TO_EMOTION","APPRAISAL_STATE_TO_EMOTION"]
def status(phase,**kw):write(RUN/"status.json",dict(phase=phase,updated_unix=time.time(),pid=os.getpid(),**kw))
def make_edges():
 edges=[]
 for rel,srcs,tgts in [(RELATIONS[0],range(42),range(42,58)),(RELATIONS[1],range(42),range(58,68)),(RELATIONS[2],range(42,58),range(58,68))]:
  edges.extend((rel,s,t) for s in srcs for t in tgts)
 return edges
def rank_stability(boot,rows):
 out=np.full_like(boot,np.nan)
 for rel in RELATIONS:
  for src in sorted(set(r["source_index"] for r in rows if r["relation_type"]==rel)):
   indices=[i for i,r in enumerate(rows) if r["relation_type"]==rel and r["source_index"]==src and r["estimable"]]
   if not indices:continue
   values=boot[:,indices];valid=np.isfinite(values)
   ranks=rankdata(-np.where(valid,values,-np.inf),axis=1,method="average")
   ranks[~valid]=np.nan;out[:,indices]=ranks
 return out
def weights_for(frame,support):
 mask=frame.estimable & (frame.support_count_groups>=support)&(frame.npmi_ci95_low>0)&(frame.fdr_q<.05)&(frame.bootstrap_valid_replicates>=950)
 w=[np.zeros((42,16)),np.zeros((42,10)),np.zeros((16,10))]
 for row in frame[mask].to_dict("records"):
  rel=RELATIONS.index(row["relation_type"]);s=row["source_index"];t=row["target_index"]
  if rel==0:w[0][s,t-42]=row["npmi_ci95_low"]
  elif rel==1:w[1][s,t-58]=row["npmi_ci95_low"]
  else:w[2][s-42,t-58]=row["npmi_ci95_low"]
 return mask,w
def normalize_rows(x):
 den=x.sum(1,keepdims=True);return np.divide(x,den,out=np.zeros_like(x),where=den>0)
def graph_retrieval(data,w,J,joint_threshold):
 val=data["val"];P=data["P"][val];M=data["M"][val];query=P[:,:42].astype(float)
 ca,ce,ae=w;a_scores=query@ca
 recalls=[];cover=[]
 for a in range(16):
  dim=data["dim_of_state"][a];lo=np.flatnonzero(data["dim_of_state"]==dim)
  scores=a_scores[:,lo];available=scores.sum(1)>0
  prediction=np.argmax(scores,axis=1)
  truth=P[:,42+a]&M[:,42+a]
  if truth.any():recalls.append(float((available& (prediction==list(lo).index(a)))[truth].mean()))
 for dim in range(6):
  truth=data["Am"][val,dim];lo=np.flatnonzero(data["dim_of_state"]==dim)
  if truth.any():cover.append(float((a_scores[:,lo].sum(1)>0)[truth].mean()))
 direct=normalize_rows(query@ce)
 gate=(J>=joint_threshold)&(J>0)
 tensor=ca[:,:,None]*ae[None,:,:]*gate
 via=normalize_rows(query@tensor.sum(1))
 score=.5*direct+.5*via
 truth=data["E"][val];eligible=data["Em"][val]
 rank=np.argsort(-score,axis=1,kind="stable")[:,:5]
 pred=np.zeros_like(truth)
 np.put_along_axis(pred,rank,np.take_along_axis(score,rank,axis=1)>0,axis=1)
 count=truth.sum(1);valid=eligible&(count>0)
 recall=np.divide((pred&truth).sum(1),count,out=np.zeros(len(count),float),where=count>0)
 app=float(np.mean(recalls));emo=float(recall[valid].mean())
 return dict(objective=.5*(app+emo),appraisal_macro_state_recall_at1=app,emotion_sample_macro_recall_at5=emo,
  appraisal_valid_dimension_query_coverage=float(np.mean(cover)),emotion_query_coverage=float((score.sum(1)>0)[valid].mean()),
  appraisal_evaluable_states=len(recalls),emotion_evaluable_samples=int(valid.sum()))
def main():
 assert not RUN.exists(),"Frozen graph run already exists"
 RUN.mkdir(parents=True)
 config=read(BASE/"config.json");config["minimum_valid_bootstrap_replicates"]=950
 write(RUN/"config.json",config)
 (RUN/"manifest").mkdir(exist_ok=True)
 source_plan=RUN/"manifest/source_graph_plan.md"
 shutil.copy2(_graph_resolve_path(Path(os.environ.get('AMG_SOURCE_PLAN', str(BASE / 'source_graph_plan.md')))), _graph_resolve_path(source_plan))
 status("aligning_inputs");data=load(plan_path=source_plan);train=data["train"];P=data["P"][train];M=data["M"][train];n=len(P)
 assert n==data["release"].manifest["split"]["role_counts"]["pseudo_train"]
 write(RUN/"manifest/sample_roles.json",[{k:r[k] for k in ["sample_id","group_id","role"]} for r in data["rows"]])
 write(RUN/"manifest/input_fingerprints.json",data["source_hashes"])
 (RUN/"ontology").mkdir()
 shutil.copy2(_graph_resolve_path(Path(data['release'].path) / 'ontology.json'), _graph_resolve_path(RUN / 'ontology/cue_ontology_v1.2.json'))
 shutil.copy2(_graph_resolve_path(data['app_root'] / 'ontology.json'), _graph_resolve_path(RUN / 'ontology/appraisal_ontology_v2.3.json'))
 shutil.copy2(_graph_resolve_path(data['emotion_run'] / 'nodes.json'), _graph_resolve_path(RUN / 'ontology/emotion_concepts_frozen.json'))
 shutil.copy2(_graph_resolve_path(data['emotion_run'] / 'wheel_mappings.json'), _graph_resolve_path(RUN / 'ontology/emotion_wheel_mappings.json'))
 edges=make_edges();sources=np.array([x[1] for x in edges]);targets=np.array([x[2] for x in edges])
 assert len(edges)==1252
 rng=np.random.default_rng(config["seed"])
 status("bootstrap",completed_candidates=0,total_candidates=len(edges))
 W=rng.multinomial(n,np.full(n,1/n),size=config["bootstrap_replicates"]).astype(np.float32)
 assert np.all(W.sum(1)==n)
 def progress(done,total):
  status("bootstrap",completed_candidates=done,total_candidates=total)
  if done%1024==0 or done==total:print(json.dumps({"phase":"bootstrap","done":done,"total":total}),flush=True)
 cells,boot,eligible_hashes=edge_bootstrap(P,M,sources,targets,W,progress=progress)
 point=npmi(cells);N=cells.sum(1);valid_counts=np.isfinite(boot).sum(0)
 with warnings.catch_warnings():
  warnings.simplefilter("ignore",RuntimeWarning)
  ci=np.nanquantile(boot,[.025,.975],axis=0)
 rows=[]
 for i,(rel,s,t) in enumerate(edges):
  estimable=bool(N[i]>=20 and np.isfinite(point[i]))
  rows.append(dict(edge_id="EDGE_"+hashlib.sha256((rel+data["node_ids"][s]+data["node_ids"][t]).encode()).hexdigest()[:20],
   source_node_id=data["node_ids"][s],target_node_id=data["node_ids"][t],relation_type=rel,source_index=s,target_index=t,
   source_name=data["node_ids"][s] if s<58 else data["emotion_names"][s-58],
   target_name=data["node_ids"][t] if t<58 else data["emotion_names"][t-58],
   n11=float(cells[i,0]),n10=float(cells[i,1]),n01=float(cells[i,2]),n00=float(cells[i,3]),
   eligible_samples=int(N[i]),eligible_groups=int(N[i]),eligible_set_hash=eligible_hashes[i],
   support_count_groups=int(cells[i,0]),source_positive_groups=int(cells[i,0]+cells[i,1]),
   target_positive_groups=int(cells[i,0]+cells[i,2]),estimable=estimable,npmi_point_estimate=float(point[i]),
   npmi_ci95_low=float(ci[0,i]),npmi_ci95_high=float(ci[1,i]),bootstrap_valid_replicates=int(valid_counts[i]),
   bootstrap_positive_frequency=float((boot[:,i]>0).mean()),permutation_p=float(exact_positive_p(cells[i])) if estimable else np.nan,
   source_split_version=data["release"].manifest["release_id"],edge_rule_version="npmi_cluster_bootstrap_v1",
   cue_ontology_version="cue_ontology_v1.2",appraisal_schema_version="appraisal_ontology_v2.3",appraisal_prompt_version="appraisal_teacher_v2.4",
   emotion_ontology_version=read(data["emotion_run"]/"protocol.json")["release_id"]))
 status("fdr_and_rank_stability")
 frame=pd.DataFrame(rows);frame["fdr_q"]=np.nan
 for rel in RELATIONS:
  idx=frame.index[(frame.relation_type==rel)&frame.estimable]
  frame.loc[idx,"fdr_q"]=bh(frame.loc[idx,"permutation_p"].to_numpy())
 ranks=rank_stability(boot,rows)
 with warnings.catch_warnings():
  warnings.simplefilter("ignore",RuntimeWarning)
  frame["bootstrap_rank_mean"]=np.nanmean(ranks,axis=0);frame["bootstrap_rank_sd"]=np.nanstd(ranks,axis=0)
 frame["bootstrap_top5_positive_frequency"]=((ranks<=5)&(boot>0)).mean(0)
 np.savez_compressed(_graph_resolve_path(RUN / 'bootstrap_npmi.npz'), npmi=boot, edge_ids=frame.edge_id.to_numpy(dtype=str))
 del boot,ranks
 status("joint_support_and_validation")
 J=np.zeros((42,16,10),np.int32)
 E=P[:,58:].astype(np.float32)
 for a in range(16):
  take=P[:,42+a]&M[:,58]
  J[:,a,:]=(P[take,:42].astype(np.float32).T@E[take]).astype(np.int32)
 np.savez_compressed(_graph_resolve_path(RUN / 'train_joint_support.npz'), support=J)
 validations=[]
 for support in config["support_grid"]:
  mask,w=weights_for(frame,support)
  pd.DataFrame(frame[mask]).to_csv(RUN/f"edges_support_{support}.csv",index=False)
  for joint in config["joint_support_grid"]:
   metrics=graph_retrieval(data,w,J,joint)
   validations.append(dict(min_support=support,joint_support_threshold=joint,edges=int(mask.sum()),**metrics))
 selection=sorted(validations,key=lambda r:(-round(r["objective"],12),-r["min_support"],-r["joint_support_threshold"]))[0]
 write(RUN/"validation/grid_results.json",dict(query_source=config["selection_queries"],objective=config["selection_objective"],results=validations,selected=selection))
 support=selection["min_support"];joint_threshold=max(1,selection["joint_support_threshold"])
 admitted,w=weights_for(frame,support)
 frame["admitted"]=admitted;frame["edge_weight"]=np.where(admitted,frame.npmi_ci95_low,0.)
 frame["min_support_rule"]=support
 reasons=[]
 for row in frame.to_dict("records"):
  bad=[]
  if not row["estimable"]:bad.append("not_estimable")
  if row["bootstrap_valid_replicates"]<950:bad.append("insufficient_valid_bootstrap_replicates")
  if not row["npmi_ci95_low"]>0:bad.append("nonpositive_ci_lower_bound")
  if not row["fdr_q"]<.05:bad.append("fdr_not_significant")
  if row["support_count_groups"]<support:bad.append("insufficient_positive_source_groups")
  reasons.append(";".join(bad))
 frame["exclusion_reason"]=reasons
 assert (frame.admitted==(frame.exclusion_reason=="")).all()
 (RUN/"graph").mkdir()
 frame.to_parquet(RUN/"graph/candidate_edge_audit.parquet",index=False)
 frame.to_csv(RUN/"graph/candidate_edge_audit.csv",index=False)
 edge_files=["edges_cue_appraisal.csv","edges_cue_emotion.csv","edges_appraisal_emotion.csv"]
 for rel,filename in zip(RELATIONS,edge_files):frame[admitted&(frame.relation_type==rel)].to_csv(RUN/"graph"/filename,index=False)
 # Stable node IDs and fixed ontology relations.
 cue_nodes=[dict(id=c,node_type="CueType",canonical_name=c,modality=("text" if i<15 else "audio" if i<32 else "visual"),
  teacher_positive_groups=int(P[:,i].sum()),teacher_negative_groups=int((M[:,i]&~P[:,i]).sum()),
  deployment_active_status="not_selected_by_edge_builder") for i,c in enumerate(data["cue_ids"])]
 app_dims=[dict(id=d,node_type="AppraisalDimension",canonical_name=d) for d in data["dims"]]
 app_states=[dict(id=s,node_type="AppraisalState",canonical_name=s,dimension_id=data["dims"][data["dim_of_state"][i]],
  valid_positive_train_groups=int(P[:,42+i].sum())) for i,s in enumerate(data["states"])]
 emotion_nodes=[dict(id=e,node_type="EmotionConcept",canonical_name=name,train_support_groups=int(P[:,58+i].sum())) for i,(e,name) in enumerate(zip(data["emotion_ids"],data["emotion_names"]))]
 all_nodes=cue_nodes+app_dims+app_states+emotion_nodes
 for name,items in [("nodes_cue",cue_nodes),("nodes_appraisal_dimension",app_dims),("nodes_appraisal_state",app_states),("nodes_emotion",emotion_nodes)]:
  pd.DataFrame(items).to_csv(RUN/"graph"/(name+".csv"),index=False)
 fixed=[dict(source_node_id=node["dimension_id"],target_node_id=node["id"],relation_type="HAS_STATE",edge_weight=1.) for node in app_states]
 pd.DataFrame(fixed).to_csv(RUN/"graph/edges_has_state.csv",index=False)
 # Candidate paths must have both admitted edges; count joint support on the same train sample.
 paths=[];path_indices=[]
 for c,a in zip(*np.nonzero(w[0])):
  for e in np.flatnonzero(w[2][a]):
   j=int(J[c,a,e]);keep=j>=joint_threshold
   paths.append(dict(source_node_id=data["cue_ids"][c],appraisal_state_id=data["states"][a],target_node_id=data["emotion_ids"][e],
    joint_support_groups=j,cue_appraisal_weight=float(w[0][c,a]),appraisal_emotion_weight=float(w[2][a,e]),
    cue_appraisal_support_groups=int(frame.loc[(frame.source_index==c)&(frame.target_index==42+a),"support_count_groups"].iloc[0]),
    appraisal_emotion_support_groups=int(frame.loc[(frame.source_index==42+a)&(frame.target_index==58+e),"support_count_groups"].iloc[0]),
    admitted=keep,exclusion_reason="" if keep else "insufficient_same_sample_joint_source_support",joint_support_rule=joint_threshold))
   path_indices.append((c,a,e))
 status("path_bootstrap",candidate_paths=len(paths))
 Wpresent=(W>0).astype(np.float32)
 for lo in range(0,len(paths),128):
  triple=np.stack([P[:,c]&P[:,42+a]&P[:,58+e]&M[:,58] for c,a,e in path_indices[lo:lo+128]],axis=1).astype(np.float32)
  resampled=Wpresent@triple
  for j,path in enumerate(paths[lo:lo+128]):
   z=resampled[:,j];path.update(bootstrap_joint_positive_frequency=float((z>0).mean()),
    bootstrap_joint_support_ci95_low=float(np.quantile(z,.025)),bootstrap_joint_support_ci95_high=float(np.quantile(z,.975)),
    bootstrap_joint_threshold_retention_frequency=float((z>=joint_threshold).mean()))
 path_frame=pd.DataFrame(paths)
 path_frame.to_csv(RUN/"graph/candidate_path_audit.csv",index=False)
 if paths:path_frame[path_frame.admitted].to_csv(RUN/"graph/paths_cue_appraisal_emotion.csv",index=False)
 else:pd.DataFrame(columns=["source_node_id","appraisal_state_id","target_node_id","joint_support_groups","admitted"]).to_csv(RUN/"graph/paths_cue_appraisal_emotion.csv",index=False)
 write(RUN/"graph/graph.json",dict(nodes=all_nodes,ontology_edges=fixed,statistical_edges=frame[admitted].drop(columns=["source_index","target_index"]).to_dict("records"),
  path_file="paths_cue_appraisal_emotion.csv",interpretation="Source annotation association; not causal/psychological truth"))
 report=dict(phase="complete",release_status="engineering_graph_pending_human_and_original_source_audit",train_samples=n,validation_samples=int(data["val"].sum()),gold_samples_used=0,
  node_counts=dict(cue=42,appraisal_dimension=6,appraisal_state=16,emotion=10,total=74),
  candidate_edges=len(frame),estimable_edges=int(frame.estimable.sum()),admitted_edges=int(admitted.sum()),
  by_relation={rel:dict(candidates=int((frame.relation_type==rel).sum()),estimable=int(((frame.relation_type==rel)&frame.estimable).sum()),
   admitted=int(((frame.relation_type==rel)&admitted).sum())) for rel in RELATIONS},
  fixed_has_state_edges=16,bootstrap_replicates=1000,bootstrap_draws_hash=hashlib.sha256(W.tobytes()).hexdigest(),
  selected_min_support=support,selected_joint_support=joint_threshold,validation_selection=selection,
  validation_query_source=config["selection_queries"],candidate_paths=len(paths),admitted_paths=sum(p["admitted"] for p in paths),
  appraisal_dimension_train_valid_counts={d:int(data["Am"][train,i].sum()) for i,d in enumerate(data["dims"])},
  emotion_train_eligible_samples=int(data["Em"][train].sum()),emotion_validation_eligible_samples=int(data["Em"][data["val"]].sum()),
  group_limitations=data["release"].manifest["group_limitations"],human_audit_completed=False,model_calls=0)
 write(RUN/"manifest/graph_build_report.json",report)
 protocol=dict(source_paths=data["source_paths"],config=config,input_fingerprints=data["source_hashes"],source_release_id=data["release"].manifest["release_id"],
  emotion_release_id=read(data["emotion_run"]/"protocol.json")["release_id"],statistical_fit_role="pseudo_train",selection_role="pseudo_validation; preregistered source-domain 3x4 grid",
  gold_role_used=False,selected_min_support=support,selected_joint_support=joint_threshold,
  source_code_sha256={str(p.relative_to(PROJECT)):sha(p) for p in sorted(BASE.glob("*.py"))},
  artifacts={str(p.relative_to(RUN)):sha(p) for p in sorted((RUN/"graph").glob("*"))})
 protocol["release_id"]=hashlib.sha256(json.dumps(protocol,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
 write(RUN/"manifest/protocol.json",protocol)
 write(BASE/"runs/current.json",dict(run_id=RUN.name,release_id=protocol["release_id"],admitted_edges=int(admitted.sum()),release_status=report["release_status"]))
 status("complete",candidate_edges=len(frame),admitted_edges=int(admitted.sum()),admitted_paths=report["admitted_paths"],release_id=protocol["release_id"])
 print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()

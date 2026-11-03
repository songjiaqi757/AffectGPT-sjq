"""CPU-only graph OOF construction. Frozen statistics/rules; no Teacher or GPU calls."""
import argparse,copy,collections,csv,json,math,os,time,warnings
from graph_paths import Path
import numpy as np
from amg_runtime.common import read,sha,canonical,atomic_json,require
from amg_graph.data import load
from amg_graph.build import make_edges,RELATIONS
from amg_graph.stats import npmi,bh,exact_positive_p,edge_bootstrap
from amg_runtime.engine import GraphQueryEngine
from amg_finetune_nogc.common import bound_query
from .common import plan,now,source_cache
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);args=ap.parse_args();run=Path(args.run);p=plan(run)
 state=dict(phase="loading_source_annotations",pid=os.getpid(),gpu_model_calls=0,started_at_beijing=now())
 def update(**kw):state.update(kw,updated_at_beijing=now());atomic_json(run/"oof_status.json",state)
 try:
  update();data=load();records=read(run/"train_records.json");rows={r["sample_id"]:r for r in records}
  require(set(rows)==set(data["ids"]) and len(rows)==30755,"Source alignment mismatch")
  parent={s:s for s in rows}
  def root(s):
   while parent[s]!=s:parent[s]=parent[parent[s]];s=parent[s]
   return s
  def union(a,b):
   a,b=root(a),root(b)
   if a!=b:parent[max(a,b)]=min(a,b)
  seen={}
  for r in records:
   keys=[("group",r["group_id"])]
   keys += [(m,a["sha256"]) for m,a in r.get("media_assets",{}).items()]
   for k in keys:
    if k in seen:union(r["sample_id"],seen[k])
    else:seen[k]=r["sample_id"]
  assignment={s:int(canonical([42,root(s)])[:12],16)%5 for s in rows}
  atomic_json(run/"fold_assignment.json",dict(assignments=assignment,groups=len(set(root(s) for s in rows)),unit="source group union exact audio/video hashes",seed=42,targets_used=False))
  original_inputs=read(Path(p["runtime_path"])/"inputs_p0.json");policy=read(Path(p["runtime_path"])/"cue_policy.json");config=read(p["query_config_path"])
  original_graph=read(original_inputs["graph"]["graph_file"])
  edges=make_edges();sources=np.array([s for rel,s,t in edges]);targets=np.array([t for rel,s,t in edges])
  summaries=[]
  for fold in range(5):
   out=run/"folds"/str(fold);out.mkdir(exist_ok=True)
   held=[s for s in rows if assignment[s]==fold]
   take=np.array([bool(t) and assignment[s]!=fold for s,t in zip(data["ids"],data["train"])])
   fit=[s for s,t in zip(data["ids"],take) if t]
   require(not({root(s) for s in held}&{root(s) for s in fit}),"Held group or exact duplicate leaked into graph fit")
   require(len(set(root(s) for s in fit))==len(fit),"Clustered fit requires a group-aware bootstrap implementation")
   update(phase="building_fold",fold=fold,fit_samples=len(fit),held_samples=len(held))
   P=data["P"][take];M=data["M"][take];n=len(P)
   rng=np.random.default_rng(42+fold);W=rng.multinomial(n,np.full(n,1/n),size=1000).astype(np.float32)
   def progress(done,total):update(phase="fold_bootstrap",fold=fold,completed_candidates=done,total_candidates=total)
   cells,boot,hashes=edge_bootstrap(P,M,sources,targets,W,progress=progress)
   point=npmi(cells);N=cells.sum(1);valid=np.isfinite(boot).sum(0)
   with warnings.catch_warnings():
    warnings.simplefilter("ignore",RuntimeWarning);low=np.nanquantile(boot,.025,axis=0)
   estimable=(N>=20)&np.isfinite(point);q=np.full(len(edges),np.nan)
   for rel in RELATIONS:
    ix=np.array([i for i,e in enumerate(edges) if e[0]==rel and estimable[i]],int)
    q[ix]=bh(exact_positive_p(cells[ix]))
   admit=estimable&(valid>=950)&(low>0)&(q<.05)&(cells[:,0]>=20)
   statistics=[]
   for i,(rel,s,t) in enumerate(edges):
    if not admit[i]:continue
    statistics.append(dict(edge_id="BCD_FOLD_EDGE_"+canonical([fold,rel,data["node_ids"][s],data["node_ids"][t]])[:20],
     source_node_id=data["node_ids"][s],target_node_id=data["node_ids"][t],relation_type=rel,edge_weight=float(low[i]),support_count_groups=int(cells[i,0]),
     source_split_version=original_inputs["cue_release"]["release_id"],npmi_point_estimate=float(point[i]),fdr_q=float(q[i])))
   active=set(data["emotion_ids"][i] for i in np.flatnonzero(P[:,58:].sum(0)>0))
   nodes=[copy.deepcopy(z) for z in original_graph["nodes"] if z["node_type"]!="EmotionConcept" or z["id"] in active]
   for z in nodes:
    if z["node_type"]=="EmotionConcept":z["train_support_groups"]=int(P[:,58+data["emotion_ids"].index(z["id"])].sum())
   graph=dict(nodes=nodes,ontology_edges=copy.deepcopy(original_graph["ontology_edges"]),statistical_edges=statistics)
   graph_id=canonical(dict(fold=fold,fit=fit,graph=graph,bootstrap=1000,support=20,joint=5))
   ca={(e["source_node_id"],e["target_node_id"]):e for e in statistics if e["relation_type"]==RELATIONS[0]}
   ae={(e["source_node_id"],e["target_node_id"]):e for e in statistics if e["relation_type"]==RELATIONS[2]}
   paths=[]
   for (cid,aid),left in ca.items():
    c=data["cue_ids"].index(cid);a=data["states"].index(aid)
    for (aa,eid),right in ae.items():
     if aa!=aid:continue
     e=data["emotion_ids"].index(eid);joint=int((P[:,c]&P[:,42+a]&P[:,58+e]&M[:,58]).sum())
     if joint<5:continue
     paths.append(dict(source_node_id=cid,appraisal_state_id=aid,target_node_id=eid,joint_support_groups=joint,cue_appraisal_weight=left["edge_weight"],appraisal_emotion_weight=right["edge_weight"],
      cue_appraisal_support_groups=left["support_count_groups"],appraisal_emotion_support_groups=right["support_count_groups"],admitted=True,joint_support_rule=5))
   atomic_json(out/"graph.json",graph);atomic_json(out/"paths.json",paths)
   inputs=copy.deepcopy(original_inputs);inputs["graph"]["release_id"]=graph_id
   cfg=copy.deepcopy(config);cfg["graph_release_id"]=graph_id
   engine=GraphQueryEngine(graph,paths,inputs,policy,cfg,p["runtime_release_id"])
   atomic_json(out/"inputs.json",inputs);atomic_json(out/"query_config.json",cfg)
   atomic_json(out/"manifest.json",dict(fold=fold,fit_sample_ids=fit,held_sample_ids=held,graph_release_id=graph_id,edges=len(statistics),paths=len(paths),active_emotions=len(active),no_held_source_groups=True,query_parameters_retuned=False))
   del W,boot
   for i,sid in enumerate(held):
    raw=read(source_cache(p,sid));cue=copy.deepcopy(raw["cue"]);cue["graph_release_id"]=graph_id;cue["query_input_id"]=canonical({k:v for k,v in cue.items() if k!="query_input_id"})
    result=engine.query(cue);evidence=bound_query(result,engine)
    item=dict(sample_id=sid,fold=fold,source_cache_id=raw["cache_id"],input_record_id=canonical({k:rows[sid][k] for k in ["sample_id","text","audio_path","video_path"]}),evidence=evidence,fold_graph_id=graph_id)
    item["cache_id"]=canonical(item);atomic_json(run/"oof_cache"/(sid+".json"),item)
    if (i+1)%100==0:update(phase="fold_evidence",fold=fold,completed=i+1,total=len(held))
   summaries.append(dict(fold=fold,fit=len(fit),held=len(held),edges=len(statistics),paths=len(paths),graph_id=graph_id))
   update(phase="fold_complete",fold=fold,summaries=summaries)
  atomic_json(run/"oof_manifest.json",dict(complete=True,samples=len(rows),folds=summaries,fold_assignment_sha256=sha(run/"fold_assignment.json"),graph_only=True,cue_models_retrained=False,all_data_and_work_on_server=True))
  update(phase="complete",samples=len(rows),finished_at_beijing=now())
 except BaseException as e:
  import traceback
  update(phase="failed",error=repr(e),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

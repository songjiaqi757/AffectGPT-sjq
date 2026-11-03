"""Independent full table/role/FDR/edge/path checks; all data stay on server."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import hashlib,json,math,warnings,os
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact,false_discovery_control
from .data import BASE,PROJECT,read,write,load,sha
from .build import RELATIONS,make_edges
RUN=BASE/"runs"/os.environ.get("AMG_RUN_ID",read(BASE/"runs/current.json")["run_id"] if (BASE/"runs/current.json").exists() else "amg_edges_v2_restore_diagnostic_20261022")
def main():
 protocol=read(RUN/"manifest/protocol.json")
 identity={k:v for k,v in protocol.items() if k!="release_id"}
 assert hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()==protocol["release_id"]
 for relative,expected in protocol["artifacts"].items():assert _graph_hash_matches(RUN / relative, expected, sha(RUN / relative)),relative
 for relative,expected in protocol["source_code_sha256"].items():
  live=PROJECT/relative;archived=RUN/"manifest/source_code_snapshot"/relative
  assert _graph_hash_matches(live, expected, sha(live)) or (archived.exists() and _graph_hash_matches(archived, expected, sha(archived))),relative
 paths=protocol.get("source_paths")
 if paths is None:
  keys=protocol["input_fingerprints"]
  release=PROJECT/next(k for k in keys if k.startswith("cue_student/artifacts/") and k.endswith("/manifest.json"))
  emotion=PROJECT/next(k for k in keys if k.startswith("emotion_nodes/runs/") and k.endswith("/protocol.json"))
  annotation=PROJECT/next(k for k in keys if k.startswith("appraisal_annotation/") and k.endswith("/final_verification.json"))
  plan=RUN/"manifest/source_graph_plan_v2_6.md"
  paths=dict(release=str(release.parent),emotion_run=str(emotion.parent),source_plan=str(plan),annotation_verification=str(annotation))
 data=load(release_path=paths["release"],emotion_run=paths["emotion_run"],plan_path=paths["source_plan"],annotation_verification=paths["annotation_verification"]);assert data["source_hashes"]==protocol["input_fingerprints"]
 P=data["P"][data["train"]];M=data["M"][data["train"]]
 frame=pd.read_parquet(RUN/"graph/candidate_edge_audit.parquet")
 assert len(frame)==11576 and frame.edge_id.is_unique
 assert list(zip(frame.relation_type,frame.source_index,frame.target_index))==make_edges()
 for row in frame.itertuples():
  s=row.source_index;t=row.target_index;m=M[:,s]&M[:,t];x=P[:,s];y=P[:,t]
  table=np.array([(m&x&y).sum(),(m&x&~y).sum(),(m&~x&y).sum(),(m&~x&~y).sum()])
  np.testing.assert_array_equal(table,[row.n11,row.n10,row.n01,row.n00])
  assert m.sum()==row.eligible_samples==row.eligible_groups
  assert hashlib.sha256(m.tobytes()).hexdigest()==row.eligible_set_hash
 for relation in RELATIONS:
  idx=frame.index[(frame.relation_type==relation)&frame.estimable]
  expected=false_discovery_control(frame.loc[idx,"permutation_p"].to_numpy(),method="bh")
  np.testing.assert_allclose(frame.loc[idx,"fdr_q"],expected,rtol=1e-12,atol=1e-15)
 checked=0
 for row in frame[frame.estimable].iloc[::79].itertuples():
  p=fisher_exact([[int(row.n11),int(row.n10)],[int(row.n01),int(row.n00)]],alternative="greater").pvalue
  np.testing.assert_allclose(row.permutation_p,p,rtol=1e-10,atol=1e-300);checked+=1
 with np.load(_graph_resolve_path(RUN / 'bootstrap_npmi.npz'), allow_pickle=False) as z:
  assert z["npmi"].shape==(1000,11576)
  np.testing.assert_array_equal(z["edge_ids"],frame.edge_id.to_numpy(dtype=str))
  with warnings.catch_warnings():
   warnings.simplefilter("ignore",RuntimeWarning)
   bounds=np.nanquantile(z["npmi"],[.025,.975],axis=0)
  np.testing.assert_allclose(frame.npmi_ci95_low,bounds[0],equal_nan=True)
  np.testing.assert_allclose(frame.npmi_ci95_high,bounds[1],equal_nan=True)
 report=read(RUN/"manifest/graph_build_report.json");support=report["selected_min_support"]
 expected=frame.estimable&(frame.support_count_groups>=support)&(frame.npmi_ci95_low>0)&(frame.fdr_q<.05)&(frame.bootstrap_valid_replicates>=950)
 np.testing.assert_array_equal(frame.admitted,expected)
 admitted=frame[frame.admitted]
 assert (admitted.edge_weight>0).all() and (admitted.edge_weight<=1).all()
 np.testing.assert_array_equal(admitted.edge_weight,admitted.npmi_ci95_low)
 names=["edges_cue_appraisal.csv","edges_cue_emotion.csv","edges_appraisal_emotion.csv"]
 for relation,name in zip(RELATIONS,names):
  f=pd.read_csv(_graph_resolve_path(RUN / 'graph' / name));assert set(f.edge_id)==set(admitted[admitted.relation_type==relation].edge_id)
 graph=read(RUN/"graph/graph.json");node_ids={n["id"] for n in graph["nodes"]}
 assert len(node_ids)==252 and len(graph["ontology_edges"])==16 and len(graph["statistical_edges"])==len(admitted)
 for edge in graph["ontology_edges"]+graph["statistical_edges"]:
  assert edge["source_node_id"] in node_ids and edge["target_node_id"] in node_ids
 edge_lookup={(r.source_node_id,r.target_node_id):r for r in admitted.itertuples()}
 path_file=RUN/"graph/candidate_path_audit.csv";path_count=0;kept=0
 if path_file.stat().st_size>2:
  paths=pd.read_csv(_graph_resolve_path(path_file))
  with np.load(_graph_resolve_path(RUN / 'train_joint_support.npz'), allow_pickle=False) as z:J=z["support"]
  for row in paths.itertuples():
   c=data["cue_ids"].index(row.source_node_id);a=data["states"].index(row.appraisal_state_id);e=data["emotion_ids"].index(row.target_node_id)
   observed=int((P[:,c]&P[:,42+a]&P[:,58+e]&M[:,58]).sum())
   assert row.joint_support_groups==observed==J[c,a,e]
   left=edge_lookup[(row.source_node_id,row.appraisal_state_id)];right=edge_lookup[(row.appraisal_state_id,row.target_node_id)]
   assert observed<=min(left.support_count_groups,right.support_count_groups)
   assert bool(row.admitted)==(observed>=report["selected_joint_support"])
   assert observed>0 or not row.admitted
   assert 0<=row.bootstrap_joint_positive_frequency<=1
   assert 0<=row.bootstrap_joint_threshold_retention_frequency<=1
   path_count+=1;kept+=int(row.admitted)
 grid=read(RUN/"validation/grid_results.json");selection=sorted(grid["results"],key=lambda r:(-round(r["objective"],12),-r["min_support"],-r["joint_support_threshold"]))[0]
 assert selection==grid["selected"] and selection["min_support"]==support
 assert report["gold_samples_used"]==0 and report["train_samples"]==int(data["train"].sum()) and report["validation_samples"]==int(data["val"].sum())
 out=dict(passed=True,verified_candidate_tables=len(frame),verified_statistical_edges=len(admitted),verified_fixed_edges=16,
  verified_path_joint_counts=path_count,verified_admitted_paths=kept,independent_fisher_comparisons=checked,
  complete_family_fdr_verified=True,bootstrap_intervals_verified=True,source_fingerprints_verified=True,
  train_only_counts_verified=True,gold_and_target_data_used=False,selected_min_support=support,
  selected_joint_support=report["selected_joint_support"],release_id=protocol["release_id"])
 write(RUN/"manifest/verification.json",out);print(json.dumps(out,ensure_ascii=False))
if __name__=="__main__":main()

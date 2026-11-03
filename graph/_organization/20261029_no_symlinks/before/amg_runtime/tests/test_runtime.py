"""Independent hand-calculated graph cases and protocol boundary checks."""
import copy,json,math,unittest
from pathlib import Path
from amg_runtime.common import ROOT,read,canonical
from amg_runtime.student import CueAssembler,validate_records
from amg_runtime.engine import GraphQueryEngine
from amg_runtime.build_release import create_policy,create_query_config,create_schemas

INPUTS=read(read(ROOT/"amg_graph/preflight/current.json")["query_engine_inputs"])
POLICY=create_policy(INPUTS)
IDS=INPUTS["cue_id_order"]

def payload(scores=None,profile="engineering",present=("text","audio","visual"),requested=None,policy=None):
 scores=[0.0]*42 if scores is None else scores
 mods={}
 for m,(a,b) in {"text":(0,15),"audio":(15,32),"visual":(32,42)}.items():
  mods[m]=dict(sample_id="test",cue_ids=IDS[a:b],input_valid=m in present,scores=list(scores[a:b]) if m in present else None)
 out=CueAssembler(INPUTS,policy or POLICY,profile).assemble("test",mods,requested)
 out["runtime_release_id"]="test";out["query_input_id"]=canonical({k:v for k,v in out.items() if k!="query_input_id"})
 return out

def fixture(**changes):
 nodes=[dict(id=c,node_type="CueType",canonical_name=c) for c in IDS]
 nodes += [dict(id=d,node_type="AppraisalDimension") for d in ["D0","D1"]]
 nodes += [dict(id=s,node_type="AppraisalState") for s in ["A0","A1","A2"]]
 nodes += [dict(id=e,node_type="EmotionConcept",canonical_name=e) for e in ["E0","E1","E2"]]
 edges=[];lookup={}
 def edge(c,t,w,n):
  row=dict(edge_id="edge_"+str(len(edges)),source_node_id=c,target_node_id=t,edge_weight=w,support_count_groups=n,source_split_version=INPUTS["cue_release"]["release_id"])
  edges.append(row);lookup[(c,t)]=row
 c0,c1,c2=IDS[:3]
 for row in [(c0,"A0",.8,40),(c1,"A0",.4,25),(c1,"A1",.2,21),(c2,"A2",.6,60),("A0","E0",.5,40),("A1","E0",.2,21),("A2","E0",.9,60),("A0","E1",.4,40),(c0,"E0",.6,40),(c1,"E1",.3,25)]:edge(*row)
 hierarchy=[dict(source_node_id=d,target_node_id=s,relation_type="HAS_STATE",edge_weight=1.) for d,s in [("D0","A0"),("D0","A1"),("D1","A2")]]
 paths=[]
 for c,a,e,j in [(c0,"A0","E0",10),(c1,"A0","E0",5),(c1,"A1","E0",5),(c2,"A2","E0",20),(c0,"A0","E1",7)]:
  left=lookup[(c,a)];right=lookup[(a,e)]
  paths.append(dict(source_node_id=c,appraisal_state_id=a,target_node_id=e,joint_support_groups=j,joint_support_rule=5,admitted=True,cue_appraisal_weight=left["edge_weight"],appraisal_emotion_weight=right["edge_weight"],cue_appraisal_support_groups=left["support_count_groups"],appraisal_emotion_support_groups=right["support_count_groups"]))
 graph=dict(nodes=nodes,ontology_edges=hierarchy,statistical_edges=edges)
 config=create_query_config(INPUTS,["D0","D1"]);config["query_parameters"].update(changes)
 return graph,paths,config

def engine(**changes):
 g,p,c=fixture(**changes);return GraphQueryEngine(g,p,INPUTS,POLICY,c,"test")
def cue3():
 values=[0.0]*42;values[:3]=[.8,.6,.9];return payload(values)
def find(out,e):return next(row for row in out["emotion_candidates"] if row["emotion_id"]==e)

class CueContractTests(unittest.TestCase):
 def test_exact_threshold_included_continuous_weight(self):
  s=[0.0]*42;s[:3]=[.5,.499999,1.]
  out=payload(s)
  self.assertEqual(out["query_weights"][:3],[.5,0.,1.]);self.assertEqual(out["cue_states"][:3],["selected","below_threshold","selected"])
 def test_missing_modalities_are_null(self):
  out=payload([.8]*42,present=("audio",))
  self.assertEqual(out["scores"][:15],[None]*15);self.assertEqual(out["scores"][32:],[None]*10)
  self.assertFalse(out["modality_present"]["text"]);self.assertTrue(out["modality_present"]["audio"])
 def test_all_deferred_deployment_returns_empty(self):
  out=payload([.9]*42,profile="deployment")
  self.assertFalse(any(out["selected_mask"]));self.assertTrue(all(out["deferred_mask"]))
  self.assertEqual(out["fallback"]["reason"],"deployment_policy_pending_human_audit")
 def test_request_mask_distinct_from_below_threshold(self):
  out=payload([.9]*42,requested=[False]*42)
  self.assertTrue(all(s=="not_requested" for s in out["cue_states"]));self.assertFalse(any(out["selected_mask"]))
 def test_unavailable_is_not_negative(self):
  out=payload([.0]*42,present=())
  self.assertEqual(out["scores"],[None]*42);self.assertEqual(out["cue_states"],["modality_unavailable"]*42)
 def test_low_score_kept_and_not_marked_deferred(self):
  out=payload([.01]*42)
  self.assertEqual(out["scores"],[.01]*42);self.assertFalse(any(out["deferred_mask"]));self.assertTrue(out["fallback"]["required"])
 def test_nan_infinity_and_out_of_range_rejected(self):
  for value in [float("nan"),float("inf"),-.01,1.01,True]:
   values=[0.0]*42;values[0]=value
   with self.subTest(value=str(value)),self.assertRaises(ValueError):payload(values)
 def test_unknown_input_fields_and_labels_rejected(self):
  for key in ["emotion","target","label","label_mask","teacher","description","features"]:
   with self.subTest(key=key),self.assertRaises(ValueError):validate_records([dict(sample_id="x",**{key:[]})])
 def test_corrupt_pyav_media_returns_unavailable(self):
  import tempfile,av
  from amg_runtime.student import StudentRunner
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/"releases"/"corrupt.mp4";path.parent.mkdir();path.write_bytes(b"invalid test media")
   runner=StudentRunner.__new__(StudentRunner);runner.inputs=INPUTS;runner.device="cpu";runner.exports={"visual":{"sha256":"test"}};runner._load=lambda m:None
   def decode(items):
    with av.open(items[0]["video_path"]) as container:return None
   runner.collators={"visual":decode}
   out,digest=runner._predict_modality(dict(sample_id="corrupt",video_path=str(path)),"visual")
   self.assertFalse(out["input_valid"]);self.assertIsNone(out["scores"]);self.assertEqual(out["error_code"],"input_or_inference_error");self.assertIn("InvalidDataError",out["error"]);self.assertIsNotNone(digest)
 def test_weight_integrity_failure_is_not_converted_to_missing_input(self):
  import tempfile
  from amg_runtime.student import StudentRunner
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/"exists.mp4";path.write_bytes(b"input")
   runner=StudentRunner.__new__(StudentRunner);runner.inputs=INPUTS;runner.exports={"visual":{"sha256":"test"}}
   def fail(m):raise ValueError("Inference weight fingerprint mismatch")
   runner._load=fail
   with self.assertRaisesRegex(ValueError,"fingerprint mismatch"):runner._predict_modality(dict(sample_id="bad_weights",video_path=str(path)),"visual")
 def test_bilingual_missing_languages_allowed(self):
  validate_records([dict(sample_id="cn",text=dict(chinese="你好")),dict(sample_id="en",text=dict(english="Hello")),dict(sample_id="missing",text={})])
 def test_duplicate_ids_bad_text_relative_media_rejected(self):
  for rows in [[dict(sample_id="x"),dict(sample_id="x")],[dict(sample_id="x",text=dict(chinese=3))],[dict(sample_id="x",audio_path="relative.wav")]]:
   with self.assertRaises(ValueError):validate_records(rows)
 def test_empty_batch(self):self.assertEqual(validate_records([]),[])
 def test_mask_and_modality_alignment_rejected(self):
  assembler=CueAssembler(INPUTS,POLICY)
  with self.assertRaises(ValueError):assembler.assemble("x",dict(text=dict(sample_id="other",input_valid=False,scores=None)))
  with self.assertRaises(ValueError):assembler.assemble("x",{},[True])
 def test_input_schema_rejects_hidden_target_labels(self):
  import jsonschema
  schema=create_schemas(INPUTS)["current_sample.schema.json"]
  jsonschema.validate(dict(sample_id="x",text=dict(chinese="文本",english=None)),schema)
  with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(dict(sample_id="x",emotion=["happy"]),schema)
 def test_score_schema_checks_fixed_dimension(self):
  import jsonschema
  schema=create_schemas(INPUTS)["cue_query_42.schema.json"];out=payload([.8]*42)
  jsonschema.validate(out,schema);out["scores"].pop()
  with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(out,schema)

class GraphFormulaTests(unittest.TestCase):
 def test_hand_calculated_full_fusion_and_dimension_weighting(self):
  out=engine().query(cue3());e=find(out,"E0")
  self.assertAlmostEqual(e["direct_score"],.48/2.3,places=12)
  self.assertAlmostEqual(e["two_hop_score"],(.464+.54*.9)/1.54,places=12)
  self.assertAlmostEqual(e["association_score"],.5*(.48/2.3+(.464+.54*.9)/1.54),places=12)
 def test_joint_ratio_missing_triple_not_inferred_from_two_edges(self):
  out=engine().query(cue3());e=find(out,"E1")
  self.assertAlmostEqual(e["two_hop_score"],.256,places=12)
  paths=[p for p in out["path_audit"] if p["emotion_id"]=="E1" and p["path_type"]=="two_hop"]
  self.assertEqual(len(paths),1);self.assertAlmostEqual(paths[0]["joint_support_ratio"],.64/.88,places=12)
 def test_joint_threshold_changes_score_and_does_not_penalize_direct_fallback(self):
  out=engine(query_path_min_joint_support_groups=10).query(cue3())
  self.assertAlmostEqual(find(out,"E0")["two_hop_score"],(.32+.54*.9)/1.54,places=12)
  e=find(out,"E1");self.assertFalse(e["two_hop_available"]);self.assertAlmostEqual(e["association_score"],.18/2.3,places=12)
  self.assertTrue(any(not p["gates"]["joint_support"] for p in out["rejected_paths"]))
 def test_query_support_filter_preserves_all_cue_denominator(self):
  out=engine(query_min_support_groups=50).query(cue3());e=find(out,"E0")
  self.assertFalse(e["direct_available"]);self.assertAlmostEqual(e["association_score"],.9)
  d=next(d for d in out["appraisal_dimensions"] if d["dimension_id"]=="D1")
  self.assertAlmostEqual(d["evidence_mass"],.54/2.3)
 def test_zero_query_filter_never_resurrects_nonadmitted_paths(self):
  a=engine(query_min_support_groups=0,query_path_min_joint_support_groups=0).query(cue3())
  b=engine().query(cue3())
  self.assertEqual(a["emotion_candidates"],b["emotion_candidates"])
  self.assertFalse(any(p.get("cue_id")==IDS[1] and p.get("emotion_id")=="E1" and p["path_type"]=="two_hop" for p in a["path_audit"]))
 def test_coverage_gate_abstains(self):
  out=engine(minimum_coverage=.9).query(cue3())
  self.assertTrue(out["fallback"]["required"]);self.assertFalse(out["emotion_candidates"])
  self.assertTrue(all(d["status"]=="abstain" for d in out["appraisal_dimensions"]))
 def test_dimension_evidence_gate_abstains_independently(self):
  out=engine(dimension_min_evidence={"D0":10.,"D1":0.}).query(cue3())
  self.assertAlmostEqual(find(out,"E0")["two_hop_score"],.9)
  self.assertEqual(out["appraisal_dimensions"][0]["status"],"abstain")
 def test_coverage_filters_low_coverage_state_without_renormalizing(self):
  out=engine(minimum_coverage=.5).query(cue3())
  e=find(out,"E0");self.assertFalse(e["direct_available"]);self.assertAlmostEqual(e["two_hop_score"],.44)
 def test_direct_and_appraisal_branches(self):
  direct=find(engine(branch="direct").query(cue3()),"E0")
  app=find(engine(branch="appraisal").query(cue3()),"E0")
  self.assertAlmostEqual(direct["association_score"],.48/2.3);self.assertFalse(direct["two_hop_available"])
  self.assertAlmostEqual(app["association_score"],(.464+.54*.9)/1.54);self.assertFalse(app["direct_available"])
 def test_lambda_endpoints(self):
  for lam,key in [(0.,"two_hop_score"),(1.,"direct_score")]:
   e=find(engine(direct_two_hop_lambda=lam).query(cue3()),"E0");self.assertEqual(e["association_score"],e[key])
 def test_traceable_path_formula_and_supports(self):
  out=engine().query(cue3())
  path=next(p for p in out["path_audit"] if p["path_type"]=="two_hop" and p["cue_id"]==IDS[0] and p["emotion_id"]=="E0")
  self.assertAlmostEqual(path["association_path_score"],.8/2.3*.8*.5)
  self.assertEqual(path["edge_support_count_groups"],[40,40]);self.assertEqual(path["joint_support_groups"],10)
 def test_topk_limits_and_paths_reference_retained_candidates(self):
  out=engine(emotion_top_k=1,path_top_k=1).query(cue3())
  self.assertEqual(len(out["emotion_candidates"]),1);self.assertEqual(len(out["explanation_paths"]),1)
  self.assertEqual(out["explanation_paths"][0]["emotion_id"],out["emotion_candidates"][0]["emotion_id"])
 def test_deterministic_repeated_query(self):
  e=engine();self.assertEqual(e.query(cue3()),e.query(cue3()))
 def test_tie_breaks_by_node_id(self):
  g,p,c=fixture(branch="direct")
  edge=next(e for e in g["statistical_edges"] if e["source_node_id"]==IDS[0] and e["target_node_id"]=="E0");edge["edge_weight"]=.3
  s=[0.]*42;s[:3]=[.6,.6,.9]
  out=GraphQueryEngine(g,p,INPUTS,POLICY,c,"test").query(payload(s))
  self.assertEqual([e["emotion_id"] for e in out["emotion_candidates"]],["E0","E1"])
 def test_empty_cue_and_isolated_cue_fallbacks(self):
  out=engine().query(payload())
  self.assertEqual(out["fallback"]["reason"],"no_query_cues")
  s=[0.]*42;s[4]=.8;out=engine().query(payload(s))
  self.assertEqual(out["fallback"]["reason"],"no_graph_candidates")
 def test_baseline_callback_triggered_exactly_once(self):
  called=[];e=engine()
  result=e.query_or_fallback(payload(),lambda:called.append(1) or "baseline")
  self.assertEqual(called,[1]);self.assertEqual(result["baseline_output"],"baseline")
  e.query_or_fallback(cue3(),lambda:called.append(2));self.assertEqual(called,[1])
 def test_malformed_query_is_audited_and_falls_back(self):
  called=[];result=engine().query_or_fallback({"sample_id":"bad"},lambda:called.append(1) or "baseline")
  self.assertEqual(result["fallback"]["reason"],"graph_query_failed");self.assertEqual(called,[1])
 def test_runtime_checkpoint_order_checksum_mismatches_fail(self):
  for mutate in [lambda c:c.update(runtime_release_id="wrong"),lambda c:c["cue_id_order"].reverse(),lambda c:c["model_versions"]["text"].update(checkpoint_sha256="bad"),lambda c:c["query_weights"].__setitem__(0,1.)]:
   cue=cue3();mutate(cue);cue["query_input_id"]=canonical({k:v for k,v in cue.items() if k!="query_input_id"})
   with self.assertRaises(ValueError):engine().query(cue)
 def test_target_label_in_query_payload_is_rejected(self):
  cue=cue3();cue["emotion"]="happy";cue["query_input_id"]=canonical({k:v for k,v in cue.items() if k!="query_input_id"})
  with self.assertRaises(ValueError):engine().query(cue)
 def test_unknown_build_rule_cannot_be_overridden(self):
  g,p,c=fixture();c["frozen_build_constraints"]["edge_min_source_groups"]=5
  with self.assertRaises(ValueError):GraphQueryEngine(g,p,INPUTS,POLICY,c,"test")
 def test_nonadmitted_or_low_joint_path_rejected_at_load(self):
  for key,value in [("admitted",False),("joint_support_groups",4)]:
   g,p,c=fixture();p[0][key]=value
   with self.assertRaises(ValueError):GraphQueryEngine(g,p,INPUTS,POLICY,c,"test")
 def test_negative_weight_or_wrong_direction_rejected(self):
  g,p,c=fixture();g["statistical_edges"][0]["edge_weight"]=-.1
  with self.assertRaises(ValueError):GraphQueryEngine(g,p,INPUTS,POLICY,c,"test")
  g,p,c=fixture();g["statistical_edges"][0]["source_node_id"]="E0"
  with self.assertRaises(ValueError):GraphQueryEngine(g,p,INPUTS,POLICY,c,"test")
 def test_graph_config_schema_validation(self):
  import jsonschema
  g,p,c=fixture();schema=create_schemas(INPUTS)["query_config.schema.json"]
  jsonschema.validate(c,schema);c["query_parameters"]["direct_two_hop_lambda"]=2
  with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(c,schema)
 def test_graph_result_schema_validation(self):
  import jsonschema
  jsonschema.validate(engine().query(cue3()),create_schemas(INPUTS)["graph_query.schema.json"])
if __name__=="__main__":unittest.main()

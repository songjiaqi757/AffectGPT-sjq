"""Deterministic frozen-graph association query; equations from 图构建.md section 6."""
import copy,csv,math
from graph_paths import Path
from .common import MODALITIES,OFFSETS,canonical,finite_number,read,require,release_path
from .student import CueAssembler
class GraphQueryEngine:
 def __init__(self,graph,paths,inputs,policy,config,runtime_release_id,inference_weights_sha256=None):
  self.graph=copy.deepcopy(graph);self.inputs=copy.deepcopy(inputs);self.policy=copy.deepcopy(policy);self.config=copy.deepcopy(config);self.runtime_id=runtime_release_id
  self.expected_inference_weights=inference_weights_sha256
  self.ids=inputs["cue_id_order"];self.nodes={n["id"]:n for n in graph["nodes"]}
  require(len(self.nodes)==len(graph["nodes"]),"Duplicate graph node ID")
  require(self.ids==[n["id"] for n in graph["nodes"] if n["node_type"]=="CueType"],"Graph Cue order mismatch")
  self.dimensions={}
  for edge in graph["ontology_edges"]:
   require(edge["relation_type"]=="HAS_STATE" and self.nodes[edge["source_node_id"]]["node_type"]=="AppraisalDimension" and self.nodes[edge["target_node_id"]]["node_type"]=="AppraisalState","Invalid hierarchy")
   self.dimensions.setdefault(edge["source_node_id"],[]).append(edge["target_node_id"])
  self.state_dim={s:d for d,states in self.dimensions.items() for s in states}
  require(len(self.state_dim)==sum(map(len,self.dimensions.values())),"State has multiple dimensions")
  self.ca={};self.ce={};self.ae={};self.edge_ids=set()
  expected_pairs={("CueType","AppraisalState"):self.ca,("CueType","EmotionConcept"):self.ce,("AppraisalState","EmotionConcept"):self.ae}
  for edge in graph["statistical_edges"]:
   source=edge["source_node_id"];target=edge["target_node_id"]
   require(source in self.nodes and target in self.nodes,"Unknown graph endpoint")
   pair=(self.nodes[source]["node_type"],self.nodes[target]["node_type"])
   require(pair in expected_pairs,"Invalid edge direction")
   require(edge["edge_id"] not in self.edge_ids,"Duplicate statistical edge ID");self.edge_ids.add(edge["edge_id"])
   require(finite_number(edge["edge_weight"]) and 0<edge["edge_weight"]<=1 and type(edge["support_count_groups"]) is int and edge["support_count_groups"]>=20,"Invalid frozen statistical edge")
   require(edge["source_split_version"]==inputs["cue_release"]["release_id"],"Edge release mismatch")
   bucket=expected_pairs[pair];require((source,target) not in bucket,"Duplicate graph edge");bucket[(source,target)]=edge
  self.paths={}
  for row in paths:
   row=copy.deepcopy(row);key=(row["source_node_id"],row["appraisal_state_id"],row["target_node_id"])
   require(key not in self.paths,"Duplicate frozen path")
   require((key[0],key[1]) in self.ca and (key[1],key[2]) in self.ae,"Frozen path edge missing")
   require(row["admitted"] in (True,"True") and int(row["joint_support_groups"])>=5 and int(row["joint_support_rule"])==5,"Only frozen admitted paths with >=5 joint source groups are permitted")
   for field,edge in [("cue_appraisal_weight",self.ca[key[:2]]),("appraisal_emotion_weight",self.ae[key[1:]])]:
    require(math.isclose(float(row[field]),edge["edge_weight"],rel_tol=1e-12,abs_tol=1e-15),"Path edge weight mismatch")
   for field,edge in [("cue_appraisal_support_groups",self.ca[key[:2]]),("appraisal_emotion_support_groups",self.ae[key[1:]])]:
    require(int(row[field])==edge["support_count_groups"],"Path edge source support mismatch")
   self.paths[key]=row
  self._validate_config()
 @classmethod
 def from_release(cls,directory=None,config_path=None):
  from .versioning import load_release
  directory=release_path(directory);manifest=load_release(directory)
  inputs=read(directory/"inputs_p0.json")
  config=read(config_path or directory/"query_config.engineering.json")
  with Path(inputs["graph"]["path_file"]).open() as f:paths=list(csv.DictReader(f))
  return cls(read(inputs["graph"]["graph_file"]),paths,inputs,read(directory/"cue_policy.json"),config,manifest["release_id"],{m:spec["sha256"] for m,spec in read(directory/"weight_exports.json")["exports"].items()})
 def _validate_config(self):
  cfg=self.config
  require(cfg["schema_version"]=="amg_query_config_v1" and cfg["graph_release_id"]==self.inputs["graph"]["release_id"],"Query config graph/version mismatch")
  require(cfg["purpose"] in ("engineering_contract_tests","source_validation_candidate","source_validation_frozen"),"Query configuration purpose is required")
  require(cfg["frozen_build_constraints"]=={"edge_min_source_groups":20,"path_min_joint_source_groups":5},"Query config cannot alter graph build rules")
  p=cfg["query_parameters"]
  require(set(p)=={"query_min_support_groups","query_path_min_joint_support_groups","dimension_min_evidence","minimum_coverage","emotion_top_k","path_top_k","direct_two_hop_lambda","branch"},"Unknown/missing query parameter")
  for k in ["query_min_support_groups","query_path_min_joint_support_groups"]:
   require(type(p[k]) is int and p[k]>=0,"Invalid support filter")
  require(set(p["dimension_min_evidence"])==set(self.dimensions),"Dimension threshold keys mismatch")
  require(all(finite_number(v) and v>=0 for v in p["dimension_min_evidence"].values()),"Invalid dimension evidence threshold")
  for k in ["minimum_coverage","direct_two_hop_lambda"]:require(finite_number(p[k]) and 0<=p[k]<=1,"Invalid "+k)
  for k in ["emotion_top_k","path_top_k"]:require(type(p[k]) is int and 1<=p[k]<=1000,"Invalid Top-K")
  require(p["branch"] in ("full","direct","appraisal"),"Invalid query branch")
  self.params=p;self.config_id=canonical(cfg)
 def _validate_cues(self,cue):
  from .build_release import create_schemas
  require(isinstance(cue,dict) and set(cue)==set(create_schemas(self.inputs)["cue_query_42.schema.json"]["properties"]),"Unknown or missing Cue query fields; labels/Teacher fields are forbidden")
  require(cue.get("schema_version")=="cue_query_42_v1" and cue.get("cue_id_order")==self.ids,"Cue query schema/order mismatch")
  require(cue.get("runtime_release_id")==self.runtime_id,"Runtime release mismatch")
  require(cue.get("cue_release_id")==self.inputs["cue_release"]["release_id"] and cue.get("graph_release_id")==self.inputs["graph"]["release_id"],"Input release mismatch")
  require(cue.get("query_input_id")==canonical({k:v for k,v in cue.items() if k!="query_input_id"}),"Cue query checksum mismatch")
  require(set(cue["model_versions"])==set(MODALITIES),"Model version keys mismatch")
  for m in MODALITIES:
   require(cue["model_versions"][m]["checkpoint_sha256"]==self.inputs["checkpoints"][m]["sha256"] and cue["model_versions"][m]["signature"]==self.inputs["checkpoints"][m]["signature"],"Checkpoint binding mismatch")
   if self.expected_inference_weights is not None:require(cue["model_versions"][m].get("inference_weights_sha256")==self.expected_inference_weights[m],"Inference weight binding mismatch")
  require(len(cue.get("scores",[]))==42 and len(cue.get("availability_mask",[]))==42,"Score/mask dimension mismatch")
  rows={}
  for m in MODALITIES:
   a,b=OFFSETS[m];mask=cue["availability_mask"][a:b]
   require(all(type(v) is bool for v in mask) and len(set(mask))==1,"Availability is a runtime modality mask")
   rows[m]=dict(sample_id=cue["sample_id"],input_valid=mask[0],scores=cue["scores"][a:b] if mask[0] else None,cue_ids=self.ids[a:b])
   if not mask[0]:require(all(s is None for s in cue["scores"][a:b]),"Unavailable Cue scores must be null")
  expected=CueAssembler(self.inputs,self.policy,cue["policy_profile"]).assemble(cue["sample_id"],rows,cue["requested_mask"])
  for field in ["active_mask","deferred_mask","query_allowed_mask","selected_mask","query_weights","thresholds","threshold_status","policy_id","policy_status","calibration","modality_present","cue_states"]:
   require(cue.get(field)==expected[field],"Cue policy/selection mismatch: "+field)
 def query(self,cue):
  self._validate_cues(cue)
  p=self.params;coverage_min=p["minimum_coverage"];min_support=p["query_min_support_groups"];kappa=p["query_path_min_joint_support_groups"]
  q={c:w for c,w in zip(self.ids,cue["query_weights"]) if w>0};z=math.fsum(q.values())
  output=dict(schema_version="amg_query_result_v1",sample_id=cue["sample_id"],runtime_release_id=self.runtime_id,graph_release_id=self.inputs["graph"]["release_id"],cue_release_id=self.inputs["cue_release"]["release_id"],query_input_id=cue["query_input_id"],query_config_id=self.config_id,query_config=copy.deepcopy(self.config),policy_profile=cue["policy_profile"],policy_status=cue["policy_status"],score_semantics="statistical association support; not calibrated probability, causal evidence or a final label",query_cues=[dict(cue_id=c,score=cue["scores"][self.ids.index(c)],weight=q[c]) for c in self.ids if c in q],query_weight_sum=z,appraisal_dimensions=[],emotion_candidates=[],explanation_paths=[],rejected_paths=[],coverage=dict(query=0.0),fallback=dict(required=True,reason=None,target="original_affectgpt"),input_snapshot=copy.deepcopy(cue))
  if not q or z<=0:
   output["fallback"]["reason"]=cue["fallback"]["reason"] or "no_query_cues"
   return self._finish(output)
  available=lambda edge:edge["support_count_groups"]>=min_support
  ca={key:e for key,e in self.ca.items() if key[0] in q and available(e)}
  ce={key:e for key,e in self.ce.items() if key[0] in q and available(e)}
  ae={key:e for key,e in self.ae.items() if available(e)}
  state_support={s:math.fsum(q[c]*e["edge_weight"] for (c,a),e in ca.items() if a==s)/z for s in self.state_dim}
  state_coverage={s:math.fsum(q[c] for c,a in ca if a==s)/z for s in self.state_dim}
  evidence={d:math.fsum(state_support[s] for s in states) for d,states in self.dimensions.items()}
  dim_coverage={d:math.fsum(q[c] for c in q if any((c,s) in ca for s in states))/z for d,states in self.dimensions.items()}
  dim_pass={d:evidence[d]>0 and evidence[d]>=p["dimension_min_evidence"][d] and dim_coverage[d]>=coverage_min for d in self.dimensions}
  state_pass={s:dim_pass[self.state_dim[s]] and state_support[s]>0 and state_coverage[s]>=coverage_min for s in self.state_dim}
  for d,states in self.dimensions.items():
   ranked=sorted(states,key=lambda s:(-state_support[s],s))
   details=[]
   for s in ranked:
    related=[dict(edge_id=e["edge_id"],cue_id=c,weight=e["edge_weight"],support_count_groups=e["support_count_groups"]) for (c,a),e in sorted(ca.items()) if a==s]
    details.append(dict(state_id=s,association_support=state_support[s],relative_support=state_support[s]/evidence[d] if evidence[d]>0 else None,query_coverage=state_coverage[s],eligible_for_paths=state_pass[s],supporting_edges=related,status="supported" if state_pass[s] else "no_graph_support" if state_support[s]==0 else "insufficient_evidence_or_coverage"))
   output["appraisal_dimensions"].append(dict(dimension_id=d,evidence_mass=evidence[d],query_coverage=dim_coverage[d],evidence_threshold=p["dimension_min_evidence"][d],status="supported" if dim_pass[d] else "abstain",state_supports=details,display_candidates=[s for s in details if s["eligible_for_paths"]][:2]))
  emotions=[n["id"] for n in self.graph["nodes"] if n["node_type"]=="EmotionConcept"]
  raw_paths={};ratios={}
  for (c,a,e),record in sorted(self.paths.items()):
   if c not in q:continue
   left=ca.get((c,a));right=ae.get((a,e))
   gates=dict(cue_appraisal_edge=left is not None,appraisal_emotion_edge=right is not None,appraisal_evidence=bool(state_pass[a]),joint_support=kappa==0 or int(record["joint_support_groups"])>=kappa)
   if not all(gates.values()):
    output["rejected_paths"].append(dict(cue_id=c,appraisal_state_id=a,emotion_id=e,joint_support_groups=int(record["joint_support_groups"]),gates=gates,reason="query_gate_failed"))
    continue
   raw_paths.setdefault((a,e),[]).append((c,record))
  for (a,e),records in raw_paths.items():
   denominator=state_support[a]*z
   ratios[(a,e)]=math.fsum(q[c]*ca[(c,a)]["edge_weight"] for c,r in records)/denominator if denominator>0 else 0.0
  all_candidates=[];all_explanations=[];raw_supported_count=0
  for e in emotions:
   direct_edges=[(c,edge) for (c,target),edge in sorted(ce.items()) if target==e]
   direct_score=math.fsum(q[c]*edge["edge_weight"] for c,edge in direct_edges)/z if direct_edges else None
   direct_cov=math.fsum(q[c] for c,edge in direct_edges)/z
   supporting_dimensions={}
   for d,states in self.dimensions.items():
    terms=[state_support[a]/evidence[d]*ae[(a,e)]["edge_weight"]*ratios[(a,e)] for a in states if (a,e) in ratios and dim_pass[d] and evidence[d]>0]
    if terms:supporting_dimensions[d]=math.fsum(terms)
   two_score=math.fsum(evidence[d]*score for d,score in supporting_dimensions.items())/math.fsum(evidence[d] for d in supporting_dimensions) if supporting_dimensions else None
   two_cues={c for (a,target),records in raw_paths.items() if target==e for c,r in records}
   two_cov=math.fsum(q[c] for c in sorted(two_cues))/z
   direct_available=direct_score is not None and direct_cov>=coverage_min and p["branch"]!="appraisal"
   two_available=two_score is not None and two_cov>=coverage_min and p["branch"]!="direct"
   if direct_score is not None or two_score is not None:raw_supported_count+=1
   if not direct_available and not two_available:continue
   score=(p["direct_two_hop_lambda"]*direct_score+(1-p["direct_two_hop_lambda"])*two_score) if direct_available and two_available else direct_score if direct_available else two_score
   merged_cues=({c for c,edge in direct_edges} if direct_available else set())|(two_cues if two_available else set())
   merged_cov=math.fsum(q[c] for c in sorted(merged_cues))/z
   candidate=dict(emotion_id=e,canonical_name=self.nodes[e].get("canonical_name",e),association_score=score,direct_score=direct_score,two_hop_score=two_score,direct_available=direct_available,two_hop_available=two_available,direct_query_coverage=direct_cov,two_hop_query_coverage=two_cov,query_coverage=merged_cov,dimension_scores=supporting_dimensions,dimension_evidence={d:evidence[d] for d in supporting_dimensions},dimension_weight_normalizer=math.fsum(evidence[d] for d in supporting_dimensions))
   all_candidates.append(candidate)
   if direct_available:
    for c,edge in direct_edges:
     all_explanations.append(dict(path_type="direct",path_id="DIRECT_"+edge["edge_id"],cue_id=c,emotion_id=e,association_path_score=q[c]/z*edge["edge_weight"],edge_ids=[edge["edge_id"]],edge_weights=[edge["edge_weight"]],edge_support_count_groups=[edge["support_count_groups"]],joint_support_groups=None,joint_support_ratio=None,query_coverage=direct_cov,gates=dict(admitted=True,query_support=True,coverage=True)))
   if two_available:
    for (a,target),records in sorted(raw_paths.items()):
     if target!=e:continue
     for c,record in records:
      left=ca[(c,a)];right=ae[(a,e)]
      all_explanations.append(dict(path_type="two_hop",path_id="PATH_"+canonical([c,a,e])[:24],cue_id=c,appraisal_state_id=a,appraisal_dimension_id=self.state_dim[a],emotion_id=e,association_path_score=q[c]/z*left["edge_weight"]*right["edge_weight"],edge_ids=[left["edge_id"],right["edge_id"]],edge_weights=[left["edge_weight"],right["edge_weight"]],edge_support_count_groups=[left["support_count_groups"],right["support_count_groups"]],joint_support_groups=int(record["joint_support_groups"]),joint_support_ratio=ratios[(a,e)],ca_state_query_coverage=state_coverage[a],query_coverage=two_cov,gates=dict(admitted=True,query_support=True,appraisal_evidence=True,joint_support=True,coverage=True)))
  all_candidates.sort(key=lambda e:(-e["association_score"],e["emotion_id"]))
  chosen=all_candidates[:p["emotion_top_k"]];selected_emotions={e["emotion_id"] for e in chosen}
  all_explanations.sort(key=lambda r:(-r["association_path_score"],r["path_id"]))
  output["emotion_candidates"]=chosen
  output["explanation_paths"]=[r for r in all_explanations if r["emotion_id"] in selected_emotions][:p["path_top_k"]]
  output["candidate_audit"]=all_candidates
  output["path_audit"]=all_explanations
  covered={path["cue_id"] for path in all_explanations}
  output["coverage"]=dict(query=math.fsum(q[c] for c in sorted(covered))/z,selected_cue_count=len(q),supported_emotion_count=len(all_candidates),raw_supported_emotion_count=raw_supported_count,retained_path_count=len(all_explanations))
  output["fallback"]=dict(required=not bool(chosen),reason=None if chosen else "insufficient_evidence_or_coverage" if raw_supported_count else "no_graph_candidates",target="original_affectgpt")
  return self._finish(output)
 def _finish(self,output):
  output["query_result_id"]=canonical(output)
  return output
 def query_or_fallback(self,cue,baseline_callback):
  require(callable(baseline_callback),"A baseline callback is required")
  try:result=self.query(cue)
  except (ValueError,KeyError,TypeError) as exc:
   result=dict(schema_version="amg_query_failure_v1",sample_id=cue.get("sample_id"),runtime_release_id=self.runtime_id,error=type(exc).__name__+": "+str(exc),fallback=dict(required=True,reason="graph_query_failed",target="original_affectgpt"))
  if result["fallback"]["required"]:result["baseline_output"]=baseline_callback()
  return result

"""Independent dense-array oracle on the actual graph, using synthetic Cue scores only."""
import argparse,csv,json
from graph_paths import Path
import numpy as np
from .common import read,atomic_json,require,canonical
from .engine import GraphQueryEngine
from .student import CueAssembler
def run(directory):
 directory=Path(directory);inputs=read(directory/"inputs_p0.json");policy=read(directory/"cue_policy.json")
 engine=GraphQueryEngine.from_release(directory);ids=inputs["cue_id_order"]
 graph=read(inputs["graph"]["graph_file"]);states=[n["id"] for n in graph["nodes"] if n["node_type"]=="AppraisalState"];emotions=[n["id"] for n in graph["nodes"] if n["node_type"]=="EmotionConcept"]
 dims={e["target_node_id"]:e["source_node_id"] for e in graph["ontology_edges"]}
 wca=np.zeros((42,len(states)));wce=np.zeros((42,len(emotions)));wae=np.zeros((len(states),len(emotions)))
 for edge in graph["statistical_edges"]:
  s,t,w=edge["source_node_id"],edge["target_node_id"],edge["edge_weight"]
  if s in ids and t in states:wca[ids.index(s),states.index(t)]=w
  elif s in ids and t in emotions:wce[ids.index(s),emotions.index(t)]=w
  elif s in states and t in emotions:wae[states.index(s),emotions.index(t)]=w
 joint=np.zeros((42,len(states),len(emotions)),bool)
 with Path(inputs["graph"]["path_file"]).open() as f:
  for p in csv.DictReader(f):joint[ids.index(p["source_node_id"]),states.index(p["appraisal_state_id"]),emotions.index(p["target_node_id"])]=True
 rng=np.random.default_rng(20261022);patterns=[np.zeros(42),np.ones(42)]
 patterns += [np.eye(42)[i]*.8 for i in range(42)]
 patterns += [rng.random(42) for _ in range(8)]
 comparisons=0;max_error=0.
 for number,scores in enumerate(patterns):
  rows={m:dict(sample_id="oracle_"+str(number),cue_ids=ids[a:b],scores=scores[a:b].tolist(),input_valid=True,inference_weights_sha256=read(directory/"weight_exports.json")["exports"][m]["sha256"]) for m,(a,b) in {"text":(0,15),"audio":(15,32),"visual":(32,42)}.items()}
  cue=CueAssembler(inputs,policy).assemble("oracle_"+str(number),rows);cue["runtime_release_id"]=engine.runtime_id;cue["query_input_id"]=canonical({k:v for k,v in cue.items() if k!="query_input_id"})
  result=engine.query(cue);q=np.where(scores>=.5,scores,0.);z=q.sum()
  if z==0:require(result["fallback"]["required"],"Empty oracle query must fall back");continue
  an=q@wca;a=an/z
  rn=np.einsum("c,ca,cae->ae",q,wca,joint,optimize=True)
  ratios=np.divide(rn,an[:,None],out=np.zeros_like(rn),where=an[:,None]>0)
  effective=wae*ratios
  pd=[];gd=[];support=[]
  for d in dict.fromkeys(dims.values()):
   index=[i for i,s in enumerate(states) if dims[s]==d];g=a[index].sum()
   relative=a[index]/g if g>0 else np.zeros(len(index))
   pd.append(relative@effective[index]);gd.append(g);support.append((effective[index]>0).any(axis=0) & (g>0))
  pd=np.asarray(pd);gd=np.asarray(gd);support=np.asarray(support)
  denom=(gd[:,None]*support).sum(axis=0)
  two=np.divide((gd[:,None]*pd*support).sum(axis=0),denom,out=np.zeros(len(emotions)),where=denom>0)
  direct=q@wce/z;has_direct=((wce>0)&(q[:,None]>0)).any(axis=0);has_two=denom>0
  expected={}
  for j,e in enumerate(emotions):
   if has_direct[j] or has_two[j]:
    expected[e]=.5*(direct[j]+two[j]) if has_direct[j] and has_two[j] else direct[j] if has_direct[j] else two[j]
  actual={e["emotion_id"]:e["association_score"] for e in result["candidate_audit"]}
  require(set(actual)==set(expected),"Oracle candidate set mismatch")
  for e,score in expected.items():
   delta=abs(actual[e]-score);max_error=max(max_error,delta)
   require(delta<1e-12,"Oracle association score mismatch");comparisons+=1
  expected_top=sorted(expected,key=lambda e:(-expected[e],e))[:5]
  require([e["emotion_id"] for e in result["emotion_candidates"]]==expected_top,"Oracle ranking mismatch")
 report=dict(passed=True,synthetic_queries=len(patterns),candidate_scores_compared=comparisons,max_absolute_error=max_error,seed=20261022,graph_release_id=inputs["graph"]["release_id"],runtime_release_id=engine.runtime_id,source_or_target_labels_used=False,method="Independent dense matrices and NumPy einsum; synthetic scores, no evaluation performance claims")
 atomic_json(directory/"validation/dense_oracle_report.json",report);print(json.dumps(report))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--release",required=True);args=p.parse_args();run(args.release)

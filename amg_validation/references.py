"""Freeze references from exactly the pre-registered pseudo_validation members."""
import argparse,hashlib,json
from pathlib import Path
from amg_runtime.common import ROOT,read,sha,canonical,atomic_json,require
def build(run):
 run=Path(run);reg=read(run/"preregistration.json");runtime=Path(reg["runtime_path"]);inputs=read(runtime/"inputs_p0.json")
 members=read(Path(inputs["cue_release"]["path"])/"members.json");val={r["sample_id"]:r for r in members if r["role"]=="pseudo_validation"}
 require(sorted(val)==reg["validation_sample_ids"],"Validation membership drift")
 graph=read(inputs["graph"]["graph_file"]);emotions={n["id"] for n in graph["nodes"] if n["node_type"]=="EmotionConcept"}
 ontology=read(Path(inputs["graph"]["path"])/"ontology/appraisal_ontology_v2.3.json")["dimensions"]
 app=ROOT/"appraisal_annotation/runs/mercaptionplus_v2_4";records={};digest=hashlib.sha256()
 for sid in reg["validation_sample_ids"]:
  path=app/"annotations"/(sid+".json");raw=path.read_bytes();row=json.loads(raw)
  require(row["sample_id"]==sid and row["data_role"]=="pseudo_validation","Appraisal role mismatch")
  require(row["versions"]["prompt_version"]=="appraisal_teacher_v2.4","Appraisal prompt drift")
  digest.update(sid.encode());digest.update(hashlib.sha256(raw).digest())
  labels={}
  for item in row["annotation"]["dimensions"]:
   d=item["dimension_id"];require(d in ontology and type(item["valid"]) is bool,"Malformed appraisal reference")
   require((item["valid"] and item["state"] in ontology[d]) or (not item["valid"] and item["state"] is None),"Invalid appraisal state/mask")
   labels[d]=item["state"] if item["valid"] else None
  require(set(labels)==set(ontology),"Incomplete appraisal dimensions")
  records[sid]=dict(sample_id=sid,source_group_id=val[sid]["group_id"],appraisal=labels)
 emotion_path=ROOT/"emotion_nodes/runs/affectgpt_original_v1/labels.jsonl";seen=set()
 with emotion_path.open() as f:
  for line in f:
   row=json.loads(line);sid=row["sample_id"]
   if sid not in val:continue
   require(sid not in seen and row["data_role"]=="pseudo_validation","Emotion role/identity mismatch");seen.add(sid)
   mask=bool(row["emotion_set_mask"]);ids=row["emotion_node_ids"]
   require(all(e in emotions for e in ids),"Emotion OOV must not expand frozen graph")
   if mask:require(bool(ids) and not row["oov_canonical_labels"],"Invalid usable Emotion reference")
   records[sid].update(emotion_ids=ids if mask else [],emotion_valid=mask,oov_canonical_labels=row["oov_canonical_labels"])
 require(seen==set(val),"Missing Emotion validation references")
 ordered=[records[sid] for sid in reg["validation_sample_ids"]]
 atomic_json(run/"references.json",ordered)
 report=dict(samples=len(ordered),sample_ids_digest=canonical([r["sample_id"] for r in ordered]),reference_sha256=sha(run/"references.json"),emotion_valid=sum(r["emotion_valid"] for r in ordered),appraisal_valid_by_dimension={d:sum(r["appraisal"][d] is not None for r in ordered) for d in ontology},appraisal_validation_ordered_digest=digest.hexdigest(),emotion_source_sha256=sha(emotion_path),roles_used=["pseudo_validation"],gold_or_reserved_used=False,target_data_used=False,graph_nodes_unchanged=True,preregistration_id=reg["preregistration_id"])
 atomic_json(run/"reference_manifest.json",report);print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);args=p.parse_args();build(args.run)

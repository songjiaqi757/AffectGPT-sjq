"""Recover literal JSON null spelling errors without changing any annotation decision."""
from pathlib import Path
import collections,copy,fcntl,hashlib,json,os,time
import annotate_full as full
pilot=full.pilot
ROOT=full.ROOT
RULE="json_null_string_to_null_v1"
def main():
 with (ROOT/"runner.lock").open("a") as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  queue=full.JointQueue(ROOT)
  with queue.lock:
   jobs=[dict(row) for row in queue.db.execute("SELECT sid,attempts,state FROM tasks WHERE state='failed'")]
  assert len(jobs)==8 and all(j["attempts"]==6 for j in jobs)
  protocol=full.load(ROOT/"protocol.json")
  samples=full.load(ROOT/"samples.json")
  source={s["sample_id"]:s for s in samples}
  pending=[]
  for job in jobs:
   sid=job["sid"];n=job["attempts"];path=ROOT/"teacher_raw"/f"{sid}.attempt{n}.json"
   raw_bytes=path.read_bytes();raw=full.load(path);body=raw["response"]
   original=json.loads(body["choices"][0]["message"]["content"]);fixed=copy.deepcopy(original)
   changes=[]
   for i,d in enumerate(fixed["dimensions"]):
    if d.get("state")=="null":
     assert d["valid"] is False
     assert d["evidence"]=="" and d["evidence_modalities"]==[] and d["unknown_reason"] in pilot.REASONS
     d["state"]=None;changes.append(f"/dimensions/{i}/state")
   assert len(changes)>=1
   annotation=pilot.validate(json.dumps(fixed,ensure_ascii=False))
   rollback=copy.deepcopy(annotation)
   for field_path in changes:
    rollback["dimensions"][int(field_path.split("/")[2])]["state"]="null"
   assert rollback==original,"Normalization unexpectedly changed another field"
   meta=raw["input_metadata"];sample=source[sid]
   record=dict(status="ok",sample_id=sid,source_group_id=sample["source_group_id"],source_video_id=sample["source_video_id"],
    data_role=sample["data_role"],annotation=annotation,meta=meta,
    versions=dict(prompt_version=pilot.PROMPT_VERSION,prompt_sha256=protocol["prompt_sha256"],
     annotation_schema_version=pilot.SCHEMA_VERSION,ontology_version=pilot.ONTOLOGY_VERSION,format_normalization=RULE),
    api=dict(model_requested=full.media.MODEL,model_returned=body.get("model"),response_id=body.get("id"),
     usage=body.get("usage",{}),attempt=n,retry_count=n-1,seconds=raw["seconds"],json_parse_status="valid_after_literal_null_normalization"),
    postprocessing=dict(rule=RULE,changed_paths=changes,source_raw_response=str(path),
     source_raw_sha256=hashlib.sha256(raw_bytes).hexdigest(),validity_decisions_unchanged=True,model_calls=0))
   assert not (ROOT/"annotations"/f"{sid}.json").exists()
   pending.append((sid,record,path,hashlib.sha256(raw_bytes).hexdigest()))
  archive=ROOT/"failed_before_format_normalization";archive.mkdir(exist_ok=True)
  for sid,record,path,before_hash in pending:
   full.dump(ROOT/"annotations"/f"{sid}.json",record)
   queue.success(sid,record["annotation"])
   failed=ROOT/"failed"/f"{sid}.json"
   if failed.exists():os.replace(failed,archive/failed.name)
   assert hashlib.sha256(path.read_bytes()).hexdigest()==before_hash
  audit=dict(rule=RULE,recovered_samples=len(pending),model_calls=0,validity_decisions_unchanged=True,other_annotation_fields_unchanged=True,
   raw_responses_unchanged=True,updated_unix=time.time(),samples=[{"sample_id":sid,"source_raw_sha256":h} for sid,_,_,h in pending])
  full.dump(ROOT/"format_normalization_audit.json",audit)
  for name in ["status.json","summary.json"]:
   status=full.load(ROOT/name);status.update(queue.snapshot())
   assert status["successful_samples"]==31255 and status["counts"]["failed"]==status["counts"]["pending"]==status["counts"]["running"]==0
   status.update(phase="complete",complete=True,test_complete=True,tested_samples=31255,updated_unix=time.time(),
    halt_reason="",format_normalization=dict(rule=RULE,recovered_samples=8,model_calls=0))
   full.dump(ROOT/name,status)
  old_snapshot=ROOT/"labels.annotation_snapshot.csv"
  if old_snapshot.exists():os.replace(old_snapshot,ROOT/"labels.before_format_normalization.csv")
  full.export(ROOT,samples,queue)
  review=full.load(ROOT/"final_failed_review.json")
  review.update(resolved_by=RULE,remaining_unresolved=0)
  full.dump(ROOT/"final_failed_review.json",review)
  print(json.dumps({"recovered_samples":len(pending),"successful_samples":31255,"failed":0,"model_calls":0,"raw_responses_unchanged":True}))
if __name__=="__main__":main()

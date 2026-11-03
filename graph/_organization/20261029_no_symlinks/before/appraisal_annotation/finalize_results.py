"""Validate finished Appraisal records and publish CSV with current data roles."""
import collections,csv,fcntl,hashlib,json,os
from pathlib import Path
import annotate
BASE=Path(__file__).resolve().parent
ROOT=BASE/"runs/mercaptionplus_v2_4"
def main():
 with (ROOT/"runner.lock").open("a") as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  status=json.loads((ROOT/"status.json").read_text())
  assert status["phase"] in ("complete","complete_with_failures"),"Annotation is not finished"
  pointer=json.loads((BASE.parent/"cue_student/artifacts/current_release.json").read_text())
  members=json.loads((Path(pointer["path"])/"members.json").read_text())
  roles={m["sample_id"]:m["role"] for m in members}
  snapshots={s["sample_id"]:s["data_role"] for s in json.loads((ROOT/"samples.json").read_text())}
  assert set(roles)==set(snapshots) and len(roles)==31255
  expected=status["successful_samples"];counts=collections.Counter();byrole=collections.defaultdict(collections.Counter)
  for p in (ROOT/"annotations").glob("*.json"):
   rec=json.loads(p.read_text());sid=rec["sample_id"]
   assert sid==p.stem and sid in roles
   result=annotate.validate(json.dumps(rec["annotation"],ensure_ascii=False))
   assert rec["versions"]["prompt_version"]=="appraisal_teacher_v2.4"
   assert rec["versions"]["annotation_schema_version"]=="appraisal_annotation_schema_v2.4"
   counts["successful_samples"]+=1
   for d in result["dimensions"]:
    key="valid_dimensions" if d["valid"] else "invalid_dimensions"
    counts[key]+=1;byrole[roles[sid]][key]+=1
   byrole[roles[sid]]["successful_samples"]+=1
  assert counts["successful_samples"]==expected
  assert counts["valid_dimensions"]==status["valid_dimension_count"]
  assert counts["invalid_dimensions"]==status["invalid_dimension_count"]
  export=json.loads((ROOT/"export_status.json").read_text())
  assert export["successful_samples"]==expected and export["rows"]==31255*6
  source=ROOT/"labels.annotation_snapshot.csv"
  if not source.exists():os.replace(ROOT/"labels.csv",source)
  temp=ROOT/"labels.current_split.tmp"
  row_count=0
  with source.open(encoding="utf-8-sig",newline="") as f,temp.open("w",encoding="utf-8-sig",newline="") as out:
   reader=csv.DictReader(f);fields=list(reader.fieldnames)
   if "annotation_snapshot_role" not in fields:fields.append("annotation_snapshot_role")
   writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
   for row in reader:
    sid=row["sample_id"];row["annotation_snapshot_role"]=snapshots[sid];row["data_role"]=roles[sid]
    writer.writerow(row);row_count+=1
  assert row_count==187530
  os.replace(temp,ROOT/"labels.csv")
  report=dict(passed=True,phase=status["phase"],counts=dict(counts),queue_counts=status["counts"],
   dimensions_checked=counts["valid_dimensions"]+counts["invalid_dimensions"],
   roles=dict(collections.Counter(roles.values())),by_role={k:dict(v) for k,v in byrole.items()},
   csv_rows=row_count,current_data_release_id=pointer["release_id"],original_annotation_snapshot_roles_preserved=True,
   exported_csv_sha256=hashlib.sha256((ROOT/"labels.csv").read_bytes()).hexdigest())
  (ROOT/"current_split_verification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
  print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()

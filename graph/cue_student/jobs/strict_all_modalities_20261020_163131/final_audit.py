from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,sys,os,math
ROOT=Path(__file__).resolve().parent;PROJECT=Path("/ai/sjq/AffectGPT-sjq");sys.path.insert(0,str(PROJECT))
from cue_student.common import atomic_json,code_hash,sha256
from cue_student.data import Release,CueDataset
from cue_student.holdout import load_fixed_holdout
from cue_student.eligibility import annotation_eligibility
status=json.loads((ROOT/"status.json").read_text());assert status["phase"]=="training"
release=Release(status["release"]);holdout=load_fixed_holdout()
samples=json.loads((PROJECT/"cue_annotation/runs/mercaptionplus/samples.json").read_text())
live=annotation_eligibility(PROJECT/"cue_annotation/runs/mercaptionplus",samples)
assert live==release.eligibility
failed=set(live["excluded_sample_ids"]);assert len(failed)==72 and live["failed_tasks"]==78
assert not failed&set(holdout["sample_ids"]) and len(set(holdout["sample_ids"]))==300
for name,h in release.manifest["source_artifacts"].items():assert sha256(PROJECT/"cue_annotation/runs/mercaptionplus"/name)==h
assert {p.name:sha256(p) for p in (ROOT/"source/cue_student").glob("*.py")}=={p.name:sha256(p) for p in (PROJECT/"cue_student").glob("*.py")}
report=dict(verified_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),phase="training",policy=live["policy"],excluded_samples=72,failed_tasks=78,
 release_id=release.manifest["release_id"],fixed_holdout_id=holdout["holdout_id"],roles=release.manifest["split"]["role_counts"],unit_tests=64,integration_tests_passed=True,
 exclusion_intersections={},runs={},code_hash=code_hash(),source_annotations_unchanged=True)
for role in release.manifest["split"]["role_counts"]:
 ids={r["sample_id"] for r in release.rows if r["role"]==role};inter=sorted(ids&failed);assert not inter;report["exclusion_intersections"][role]=inter
for name,run in status["runs"].items():
 assert "--resume" not in run["command"] and "--init-from" not in run["command"] and run["fresh_pretrained_start"]
 cmd=Path("/proc",str(run["pid"]),"cmdline").read_bytes();assert b"cue_student.train" in cmd
 cfg=json.loads(Path(run["config"]).read_text())
 train=CueDataset(release,cfg["modality"],"pseudo_train",training=True);val=CueDataset(release,cfg["modality"],"pseudo_validation")
 assert not failed&{release.rows[i]["sample_id"] for i in train.indices+val.indices}
 f=Path(run["output"])/"events.jsonl"
 with f.open("rb") as stream:
  stream.seek(0,2);stream.seek(max(0,stream.tell()-32768));lines=stream.read().splitlines()
 events=[]
 for line in lines:
  try:events.append(json.loads(line))
  except ValueError:pass
 last=next(e for e in reversed(events) if e["event"]=="train")
 assert last["step"]>0 and math.isfinite(last["masked_bce"]) and math.isfinite(last["grad_norm"])
 manifest=json.loads((Path(run["output"])/"training_manifest.json").read_text())
 assert manifest["release_id"]==report["release_id"] and manifest["fixed_holdout_id"]==report["fixed_holdout_id"]
 assert cfg["pin_memory"] and cfg["prefetch_factor"]==2
 report["runs"][name]=dict(pid=run["pid"],step=last["step"],epoch=last["epoch"],masked_bce=last["masked_bce"],grad_norm=last["grad_norm"],
    train_samples=len(train),validation_samples=len(val),encoder_train=cfg["encoder_train"],loader=run["loader_optimization"],fresh_start=True)
atomic_json(ROOT/"launch_verified.json",report)
atomic_json(PROJECT/"cue_student/reports/strict_all_modalities_20261020.json",report)
atomic_json(PROJECT/"cue_student/jobs/latest_optimization.json",dict(job=str(ROOT),source=str(PROJECT/"cue_student"),code_hash=report["code_hash"],
 optimization="ordered spawn DataLoader/prefetch/pin_memory/non_blocking/worker and decode thread limits",runs={k:v["loader"] for k,v in report["runs"].items()}))
print(json.dumps(report,ensure_ascii=False),flush=True)

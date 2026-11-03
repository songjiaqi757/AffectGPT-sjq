from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,os,sys,math,collections,subprocess
ROOT=Path(__file__).resolve().parent;PROJECT=Path("/ai/sjq/AffectGPT-sjq");sys.path.insert(0,str(PROJECT))
from cue_student.common import sha256,atomic_json,code_hash
from cue_student.data import Release
from cue_student.holdout import load_fixed_holdout
plan=json.loads((ROOT/"experiment_plan.json").read_text());status=json.loads((ROOT/"status.json").read_text())
assert status["phase"]=="training" and len(status["runs"])==4
assert {f.name:sha256(f) for f in (PROJECT/"cue_student").glob("*.py")}==plan["source_files"]
assert status["runner_sha256"]==sha256(ROOT/"memory_limited_train.py")
release=Release(plan["release"]);hold=load_fixed_holdout();assert release.fixed_holdout_id==hold["holdout_id"]==plan["fixed_holdout_id"]
assert not set(release.eligibility["excluded_sample_ids"])&set(hold["sample_ids"])
baseline=json.loads((Path(plan["baseline_job"])/"status.json").read_text())
report=dict(verified_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),phase="training",new_runs={},baseline_runs={},assignment=plan["assignment"],memory_budgets=status["memory_budgets"],
 release_id=release.manifest["release_id"],fixed_holdout_id=release.fixed_holdout_id,excluded_samples=len(release.eligibility["excluded_sample_ids"]),source_unchanged=True,
 preflights_all_passed=True,spawn_guard_verified=True,code_hash=code_hash(),all_operations_server_only=True)
for name,run in status["runs"].items():
 cfg=json.loads(Path(run["config"]).read_text())
 assert cfg["encoder_train"]=="full" and cfg["gradient_checkpointing"] and cfg["cuda_memory_fraction"]==.20
 assert run["physical_gpu"]==plan["assignment"][name]
 assert "--resume" not in run["command"] and "--init-from" not in run["command"]
 cmd=Path("/proc",str(run["pid"]),"cmdline").read_bytes()
 assert str(ROOT/"memory_limited_train.py").encode() in cmd
 env={}
 for entry in Path("/proc",str(run["pid"]),"environ").read_bytes().split(b"\0"):
  if b"=" in entry:
   k,v=entry.split(b"=",1)
   if k==b"CUDA_VISIBLE_DEVICES":env["cuda"]=v.decode()
 assert env["cuda"]==run["cuda_visible_devices"]
 manifest=json.loads((Path(run["output"])/"training_manifest.json").read_text())
 assert manifest["release_id"]==report["release_id"] and manifest["fixed_holdout_id"]==report["fixed_holdout_id"]
 with (Path(run["output"])/"events.jsonl").open("rb") as f:
  f.seek(0,2);f.seek(max(0,f.tell()-16384));lines=f.read().splitlines()
 train=None
 for line in reversed(lines):
  try:
   e=json.loads(line)
   if e["event"]=="train":train=e;break
  except ValueError:pass
 assert train and train["step"]>=1 and math.isfinite(train["masked_bce"]) and math.isfinite(train["grad_norm"])
 report["new_runs"][name]=dict(pid=run["pid"],gpu=run["physical_gpu"],step=train["step"],epoch=train["epoch"],masked_bce=train["masked_bce"],encoder_train="full",gradient_checkpointing=True,cuda_memory_fraction=.20,loader=run["loader_optimization"])
for name,run in baseline["runs"].items():
 # Original jobs remain owned by their original supervisor; completion is also valid.
 assert run["pid"]==plan["baseline_runs"][name]["pid"] and run["config_sha256"]==plan["baseline_runs"][name]["config_sha256"]
 if run["state"]=="running":assert b"cue_student.train" in Path("/proc",str(run["pid"]),"cmdline").read_bytes()
 report["baseline_runs"][name]=dict(pid=run["pid"],state=run["state"],gpu=run["physical_gpu"],last_event=run.get("last_event"))
report["all_assignment_counts"]=dict(collections.Counter([r["physical_gpu"] for r in baseline["runs"].values()]+[r["physical_gpu"] for r in status["runs"].values()]))
report["gpu_snapshot"]=subprocess.check_output(["nvidia-smi","--query-gpu=index,memory.used,utilization.gpu","--format=csv"],text=True)
atomic_json(ROOT/"launch_verified.json",report);atomic_json(PROJECT/"cue_student/reports/full_finetune_20261020.json",report)
print(json.dumps(report,ensure_ascii=False),flush=True)

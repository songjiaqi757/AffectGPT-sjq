"""Five fresh optimized runs on the strict all-modality-success release."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import sys,os,json,time,subprocess,traceback,fcntl
ROOT=Path(__file__).resolve().parent;PROJECT=Path("/ai/sjq/AffectGPT-sjq")
sys.path.insert(0,str(PROJECT))
from cue_student.common import atomic_json,code_hash,sha256,load_config
from cue_student.data import Release,CueDataset
from cue_student.holdout import load_fixed_holdout
from cue_student.temporal import temporal_spec
def now():return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
def tail_event(path):
 p=Path(path)/"events.jsonl"
 if not p.exists():return None
 with p.open("rb") as f:
  f.seek(0,2);f.seek(max(0,f.tell()-16384));lines=f.read().splitlines()
 for line in reversed(lines):
  try:return json.loads(line)
  except (ValueError,UnicodeDecodeError):pass
def summarize(status):
 import torch
 selected={}
 for name,run in status["runs"].items():
  checkpoint=torch.load(Path(run["output"])/"best.pt",map_location="cpu",weights_only=False)
  assert checkpoint["release_id"]==status["release_id"] and checkpoint["fixed_holdout_id"]==status["fixed_holdout_id"]
  selected[name]=dict(checkpoint=str(Path(run["output"])/"best.pt"),validation=checkpoint["validation"],progress=checkpoint["progress"])
 def comparison(a,b):
  av,bv=selected[a]["validation"],selected[b]["validation"]
  return dict(baseline=a,candidate=b,macro_ap_delta=bv["macro_ap"]-av["macro_ap"],masked_bce_delta=bv["masked_bce"]-av["masked_bce"])
 atomic_json(ROOT/"comparison.json",dict(scope="Same pseudo-validation set; best selected by macro AP; not human gold.",release_id=status["release_id"],
  fixed_holdout_id=status["fixed_holdout_id"],runs=selected,audio=comparison("audio","audio_temporal"),video=comparison("visual","visual_temporal")))
def main():
 with (ROOT/"supervisor.lock").open("w") as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if not json.loads((ROOT/"stop_status.json").read_text())["complete"]:raise RuntimeError("Old runs not stopped")
  if not (ROOT/"unit_tests.log").read_text().rstrip().endswith("OK"):raise RuntimeError("Unit tests not passed")
  integration=json.loads((ROOT/"integration_report.json").read_text())
  if not integration["passed"] or integration["code_hash"]!=code_hash():raise RuntimeError("Missing/stale integration tests")
  audit=json.loads((ROOT/"data_audit.json").read_text());release=Release(audit["release"]);hold=load_fixed_holdout()
  assert release.fixed_holdout_id==hold["holdout_id"]==audit["fixed_holdout_id"]
  assert len(hold["sample_ids"])==300
  frozen=code_hash();status=dict(job=str(ROOT),supervisor_pid=os.getpid(),phase="launching",started_at=now(),runs={},release=audit["release"],
    release_id=release.manifest["release_id"],fixed_holdout_id=hold["holdout_id"],code_hash=frozen,exclusion_policy=release.eligibility["policy"],
    excluded_samples=72,failed_tasks=78,role_counts=release.manifest["split"]["role_counts"],fresh_pretrained_start=True,
    caveat="Engineering pseudo-label comparison. Human gold not yet available; near-duplicate/source provenance remains unverified.")
  atomic_json(ROOT/"status.json",status)
  gpu_lines=subprocess.check_output(["nvidia-smi","--query-gpu=index,uuid,memory.free","--format=csv,noheader,nounits"],text=True).splitlines()
  gpus={}
  for line in gpu_lines:
   index,uuid,free=[s.strip() for s in line.split(",")];gpus[int(index)]=dict(uuid=uuid,free_mib=int(free))
  if any(gpus[i]["free_mib"]<24000 for i in (0,1)):raise RuntimeError("Insufficient free memory")
  processes={};logs={};assign=dict(text=0,audio=0,audio_temporal=0,visual=1,visual_temporal=1)
  for name in ("text","audio","visual","visual_temporal","audio_temporal"):
   cfgpath=ROOT/"configs"/(name+".json");cfg=load_config(cfgpath)
   expected_workers=0 if name=="text" else 4 if name.startswith("visual") else 2
   assert cfg["num_workers"]==expected_workers and cfg["pin_memory"] is True and cfg["prefetch_factor"]==2
   if name.startswith("visual"):assert cfg["decode_threads"]==1
   ds=CueDataset(release,cfg["modality"],"pseudo_train",training=True);val=CueDataset(release,cfg["modality"],"pseudo_validation")
   output=PROJECT/"cue_student/output"/ROOT.name/name
   if (output/"last.pt").exists():raise RuntimeError("Fresh output contains checkpoint")
   env=dict(os.environ,PYTHONPATH=str(PROJECT),PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",
    TOKENIZERS_PARALLELISM="false",OMP_NUM_THREADS="8",MKL_NUM_THREADS="8",OPENBLAS_NUM_THREADS="8",
    CUDA_VISIBLE_DEVICES=gpus[assign[name]]["uuid"],CUDA_DEVICE_ORDER="PCI_BUS_ID")
   cmd=[sys.executable,"-u","-m","cue_student.train","--config",str(cfgpath),"--release",audit["release"],"--output",str(output),"--device","cuda:0","--cpu-threads","8","--allow-unverified-groups"]
   logfile=ROOT/(name+".log");log=logfile.open("ab",buffering=0);logs[name]=log
   proc=subprocess.Popen(cmd,cwd=PROJECT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);processes[name]=proc
   status["runs"][name]=dict(pid=proc.pid,state="running",config=str(cfgpath),config_sha256=sha256(cfgpath),output=str(output),log=str(logfile),
    command=cmd,physical_gpu=assign[name],cuda_visible_devices=env["CUDA_VISIBLE_DEVICES"],started_at=now(),
    train_samples=len(ds),validation_samples=len(val),temporal_architecture=temporal_spec(cfg),fresh_pretrained_start=True,
    loader_optimization={k:cfg.get(k) for k in ("num_workers","pin_memory","prefetch_factor","persistent_workers","decode_threads")})
   atomic_json(ROOT/"status.json",status)
   time.sleep(2)
  status["phase"]="training";atomic_json(ROOT/"status.json",status)
  atomic_json(PROJECT/"cue_student/jobs/latest_full.json",dict(job=str(ROOT),supervisor_pid=os.getpid(),supervisor_script=str(ROOT/"launch.py"),runs=list(status["runs"])))
  atomic_json(PROJECT/"cue_student/jobs/latest_audio_temporal.json",dict(job=str(ROOT),run="audio_temporal",supervisor_pid=os.getpid(),pid=processes["audio_temporal"].pid,status=str(ROOT/"status.json")))
  while True:
   for name,proc in processes.items():
    run=status["runs"][name];ret=proc.poll();run["last_event"]=tail_event(run["output"])
    if ret is not None and "returncode" not in run:run.update(returncode=ret,state="completed" if ret==0 else "failed",finished_at=now());logs[name].close()
   active=any(proc.poll() is None for proc in processes.values())
   status["phase"]="training" if active else "completed" if all(r.get("returncode")==0 for r in status["runs"].values()) else "finished_with_errors"
   status["updated_at"]=now();atomic_json(ROOT/"status.json",status)
   if not active:break
   time.sleep(20)
  if status["phase"]=="completed":summarize(status)
try:main()
except BaseException:
 path=ROOT/"status.json";status=json.loads(path.read_text()) if path.exists() else {}
 status.update(phase="failed",error=traceback.format_exc(),updated_at=now());atomic_json(path,status);raise

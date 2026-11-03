"""User-requested 3+1 placement, bounded memory, sequential startup ramp."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import sys,os,json,time,subprocess,fcntl,traceback,hashlib
ROOT=Path(__file__).resolve().parent;PROJECT=Path("/ai/sjq/AffectGPT-sjq")
sys.path.insert(0,str(PROJECT))
from cue_student.common import atomic_json,code_hash,load_config,sha256
from cue_student.data import Release,CueDataset
def now():return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
def tail_event(output):
 p=Path(output)/"events.jsonl"
 if not p.exists():return None
 with p.open("rb") as f:
  f.seek(0,2);f.seek(max(0,f.tell()-16384));lines=f.read().splitlines()
 for line in reversed(lines):
  try:return json.loads(line)
  except (ValueError,UnicodeDecodeError):pass
def gpus():
 lines=subprocess.check_output(["nvidia-smi","--query-gpu=index,uuid,memory.total,memory.used","--format=csv,noheader,nounits"],text=True).splitlines()
 result={}
 for line in lines:
  index,uuid,total,used=[s.strip() for s in line.split(",")]
  result[int(index)]=dict(uuid=uuid,total_mib=int(total),used_mib=int(used))
 return result
def compare_finished(status,baseline):
 import torch
 summary=dict(scope="Best checkpoints on same pseudo-validation set; not human gold.",release_id=status["release_id"],fixed_holdout_id=status["fixed_holdout_id"],runs={})
 for name,run in status["runs"].items():
  base_name=name.removesuffix("_full");base_run=baseline["runs"][base_name]
  if base_run.get("state")!="completed":continue
  a=torch.load(Path(base_run["output"])/"best.pt",map_location="cpu",weights_only=False)
  b=torch.load(Path(run["output"])/"best.pt",map_location="cpu",weights_only=False)
  assert a["release_id"]==b["release_id"]==status["release_id"]
  assert a["fixed_holdout_id"]==b["fixed_holdout_id"]==status["fixed_holdout_id"] and a["cue_ids"]==b["cue_ids"]
  summary["runs"][name]=dict(baseline=base_name,baseline_validation=a["validation"],full_validation=b["validation"],
   macro_ap_delta=b["validation"]["macro_ap"]-a["validation"]["macro_ap"],masked_bce_delta=b["validation"]["masked_bce"]-a["validation"]["masked_bce"])
 atomic_json(ROOT/"comparison.json",summary)
def main():
 with (ROOT/"supervisor.lock").open("w") as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  plan=json.loads((ROOT/"experiment_plan.json").read_text())
  assert plan["source_files"]=={f.name:sha256(f) for f in (PROJECT/"cue_student").glob("*.py")}
  frozen=code_hash();release=Release(plan["release"])
  assert release.manifest["release_id"]==plan["release_id"] and release.fixed_holdout_id==plan["fixed_holdout_id"]
  profiles={}
  for name in plan["assignment"]:
   r=json.loads((ROOT/(name+".preflight.json")).read_text())
   assert r["passed"] and r["code_hash"]==frozen and r["memory_fraction_cap"]==0.20 and r["release_id"]==plan["release_id"]
   assert r["trainable_encoder_parameters"]==r["encoder_parameters"]
   profiles[name]=r
  cards=gpus();budgets={}
  for gpu in (0,1):
   count=sum(i==gpu for i in plan["assignment"].values())
   max_new=count*cards[gpu]["total_mib"]*.20
   required=cards[gpu]["used_mib"]+max_new+8192
   if required>cards[gpu]["total_mib"]:raise RuntimeError("Insufficient conservative collective budget on GPU "+str(gpu))
   budgets[gpu]=dict(existing_used_mib=cards[gpu]["used_mib"],new_processes=count,max_new_allocator_mib=max_new,reserve_mib=8192,total_mib=cards[gpu]["total_mib"])
  status=dict(job=str(ROOT),supervisor_pid=os.getpid(),phase="launching",started_at=now(),runs={},release=plan["release"],release_id=plan["release_id"],
    fixed_holdout_id=plan["fixed_holdout_id"],baseline_job=plan["baseline_job"],code_hash=frozen,memory_budgets=budgets,assignment=plan["assignment"],
    runner_sha256=sha256(ROOT/"memory_limited_train.py"),source_unchanged=True,
    startup="Start one new process at a time and wait for its first optimizer update before starting the next; each new process has a 20% allocator cap.")
  atomic_json(ROOT/"status.json",status)
  envbase=dict(os.environ,PYTHONPATH=str(PROJECT),PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",
   TOKENIZERS_PARALLELISM="false",OMP_NUM_THREADS="8",MKL_NUM_THREADS="8",OPENBLAS_NUM_THREADS="8",CUDA_DEVICE_ORDER="PCI_BUS_ID")
  processes={};logs={}
  # Place the single GPU1 candidate first, then ramp the three GPU0 candidates.
  for name in ("visual_temporal_full","audio_full","audio_temporal_full","visual_full"):
   assert code_hash()==frozen
   cfgpath=ROOT/"configs"/(name+".json");cfg=load_config(cfgpath);assert cfg["encoder_train"]=="full" and cfg["gradient_checkpointing"] and cfg["cuda_memory_fraction"]==0.20
   base_cfg=load_config(Path(plan["baseline_job"])/"configs"/(name.removesuffix("_full")+".json"))
   assert all(cfg[k]==v for k,v in base_cfg.items() if k!="encoder_train")
   out=PROJECT/"cue_student/output"/ROOT.name/name
   if (out/"last.pt").exists():raise RuntimeError("New experiment must start fresh")
   gpu=plan["assignment"][name];env=dict(envbase,CUDA_VISIBLE_DEVICES=cards[gpu]["uuid"])
   cmd=[sys.executable,"-u",str(ROOT/"memory_limited_train.py"),"--config",str(cfgpath),"--release",plan["release"],"--output",str(out),"--device","cuda:0","--cpu-threads","8","--allow-unverified-groups"]
   logpath=ROOT/(name+".log");log=logpath.open("ab",buffering=0);logs[name]=log
   proc=subprocess.Popen(cmd,cwd=PROJECT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);processes[name]=proc
   status["runs"][name]=dict(pid=proc.pid,state="starting",started_at=now(),physical_gpu=gpu,cuda_visible_devices=cards[gpu]["uuid"],
    config=str(cfgpath),output=str(out),log=str(logpath),command=cmd,fresh_pretrained_start=True,encoder_train="full",gradient_checkpointing=True,
    cuda_memory_fraction=.20,memory_allocator_cap_mib=cards[gpu]["total_mib"]*.20,train_samples=len(CueDataset(release,cfg["modality"],"pseudo_train",training=True)),
    validation_samples=len(CueDataset(release,cfg["modality"],"pseudo_validation")),loader_optimization={k:cfg.get(k) for k in ("num_workers","pin_memory","prefetch_factor","persistent_workers","decode_threads")})
   atomic_json(ROOT/"status.json",status);deadline=time.monotonic()+900
   while True:
    ret=proc.poll();event=tail_event(out);status["runs"][name]["last_event"]=event;status["updated_at"]=now();atomic_json(ROOT/"status.json",status)
    if ret is not None:raise RuntimeError("New trainer failed during bounded startup: "+name+" exit "+str(ret))
    if event is not None and event.get("event") in ("train","checkpoint"):
     status["runs"][name]["state"]="running";print("STARTED",name,proc.pid,"GPU",gpu,flush=True);break
    if time.monotonic()>deadline:raise RuntimeError("First-update startup timeout: "+name)
    time.sleep(10)
  status["phase"]="training";atomic_json(ROOT/"status.json",status)
  atomic_json(PROJECT/"cue_student/jobs/latest_full_finetune.json",dict(job=str(ROOT),supervisor_pid=os.getpid(),status=str(ROOT/"status.json"),runs=list(status["runs"])))
  atomic_json(PROJECT/"cue_student/jobs/latest_all_experiments.json",dict(baseline_job=plan["baseline_job"],full_finetune_job=str(ROOT),total_runs=9,assignment=plan["assignment"]))
  while True:
   for name,proc in processes.items():
    run=status["runs"][name];ret=proc.poll();run["last_event"]=tail_event(run["output"])
    if ret is not None and "returncode" not in run:run.update(returncode=ret,state="completed" if ret==0 else "failed",finished_at=now());logs[name].close()
   active=any(p.poll() is None for p in processes.values());status["phase"]="training" if active else "completed" if all(r.get("returncode")==0 for r in status["runs"].values()) else "finished_with_errors"
   status["updated_at"]=now();atomic_json(ROOT/"status.json",status)
   if not active:break
   time.sleep(20)
  if status["phase"]=="completed":
   baseline=json.loads((Path(plan["baseline_job"])/"status.json").read_text());compare_finished(status,baseline)
try:main()
except BaseException:
 path=ROOT/"status.json";s=json.loads(path.read_text()) if path.exists() else {}
 s.update(phase="failed",error=traceback.format_exc(),updated_at=now());atomic_json(path,s);raise

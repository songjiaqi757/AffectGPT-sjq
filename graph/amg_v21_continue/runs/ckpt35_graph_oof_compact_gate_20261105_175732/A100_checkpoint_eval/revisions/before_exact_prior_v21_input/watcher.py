import argparse,collections,csv,io,json,math,os,signal,subprocess,time,traceback
from .common import *
def verify_shared(run):
 p=plan(run)
 for filename,h in read(run/"code_manifest.json")["files"].items():assert sha(filename)==h,"Frozen evaluation dependency changed: "+filename
 assert sha(run/"cache_inventory.json")==p["cache_inventory_sha256"]
 assert sha(p["gate_source"])==p["gate_source_sha256"]
 return p
def committed_checkpoints(p):
 root=Path(p["training_source_run"])/"from_35";f=root/"checkpoints.json"
 if not f.exists():return {}
 records=read(f);result={}
 for spec in records:
  epoch=spec["epoch"];path=Path(spec["path"])
  assert epoch in p["expected_epochs"] and epoch not in result
  assert path.parent==root and path.suffix==".pth" and path.is_file()
  result[epoch]=spec
 return result
def prepare_epoch(run,p,spec):
 epoch=spec["epoch"];out=run/"epochs"/f"epoch_{epoch:03d}"
 if (out/"plan.json").exists():
  ep=plan(out);assert ep["checkpoints"][str(epoch)]["sha256"]==spec["sha256"];return out
 assert sha(spec["path"])==spec["sha256"],"Training checkpoint is not fully committed"
 out.mkdir(exist_ok=True)
 for name in ["jobs","shards","workers","logs","predictions","scores"]:(out/name).mkdir(exist_ok=True)
 ep=dict(p);ep.pop("plan_id");ep.update(run=str(out),training_run=str(out),checkpoints={str(epoch):dict(path=spec["path"],sha256=spec["sha256"],epoch=epoch)},logical_jobs=3,total_predictions=1400,parent_plan_id=p["plan_id"],expected_epochs=[epoch],created_at=now())
 # All checkpoint runs share immutable prepared input files by exact absolute paths.
 for name in ["original_config.json","cache_inventory.json","source_probe.json","tokenizer_binding.json","code_manifest.json"]:write(out/name,read(run/name))
 ep["plan_id"]=digest(ep);write(out/"plan.json",ep)
 for dataset,ds in ep["datasets"].items():
  jid=f"epoch_{epoch:03d}_{dataset}";shards=[]
  for start in range(0,ds["samples"],16):
   sid=jid+f"_{start:05d}";shards.append(sid);write(out/"shards"/(sid+".json"),dict(id=sid,job_id=jid,epoch=epoch,dataset=dataset,start=start,stop=min(start+16,ds["samples"]),state="pending",attempts=0))
  write(out/"jobs"/(jid+".json"),dict(id=jid,epoch=epoch,dataset=dataset,samples=ds["samples"],shards=shards,state="pending",score_state="pending"))
 return out
def summarize(run,p):
 rows=[]
 for epoch in p["expected_epochs"]:
  folder=run/"epochs"/f"epoch_{epoch:03d}"/"scores"
  if folder.exists():
   for f in sorted(folder.glob("*.json")):rows.append(read(f))
 fields=["epoch","dataset","samples","main_metric","main_score","HIT","WAF","ACC","F_s","P_s","R_s"]
 buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=fields,extrasaction="ignore");writer.writeheader()
 for row in sorted(rows,key=lambda r:(r["epoch"],r["dataset"])):writer.writerow(dict(row,**row["metrics"]))
 temp=run/"metrics_all.csv.tmp";temp.write_text(buf.getvalue());temp.replace(run/"metrics_all.csv")
 write(run/"scores_all.json",rows)
 lines=["# Continuation checkpoint36–40 · v2.1 P4 gate · A100","","Official metrics, percentages. Blank cells are pending.","","|Checkpoint|MER2023 HIT|SIMS WAF|SIMS ACC|OV-MERD+ F_s|P_s|R_s|","|---:|---:|---:|---:|---:|---:|---:|"]
 for epoch in p["expected_epochs"]:
  vals={}
  for row in rows:
   if row["epoch"]==epoch:vals.update({row["dataset"]+"_"+k:v for k,v in row["metrics"].items()})
  keys=["MER2023_HIT","SIMS_WAF","SIMS_ACC","OVMERDPlus_F_s","OVMERDPlus_P_s","OVMERDPlus_R_s"]
  lines.append("|"+str(epoch)+"|"+"|".join(f"{100*vals[k]:.2f}" if k in vals else "" for k in keys)+"|")
 temp=run/"RESULTS.md.tmp";temp.write_text("\n".join(lines)+"\n");temp.replace(run/"RESULTS.md")
 return rows
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);ap.add_argument("--check",action="store_true");a=ap.parse_args();run=Path(a.run);p=verify_shared(run)
 assert subprocess.check_output(["nvidia-smi","--query-gpu=uuid","--format=csv,noheader"],text=True).strip()==p["gpu_uuid"]
 if a.check:print(json.dumps(dict(passed=True,node="A100",expected_epochs=p["expected_epochs"],datasets={d:s["samples"] for d,s in p["datasets"].items()},committed_epochs=sorted(committed_checkpoints(p)),generation=p["generation"],same_training_gate=True,total_predictions=7000),ensure_ascii=False));return
 owner=lock(run/"watcher.lock");assert owner is not None,"An A100 evaluation watcher is already running"
 state=dict(pid=os.getpid(),node="A100",plan_id=p["plan_id"],expected_epochs=p["expected_epochs"],completed_epochs=[],failed_epochs=[],started_at=now());child=None
 def update(**kw):state.update(kw,updated_at=now());write(run/"watcher_status.json",state)
 def stop(signum,frame):raise KeyboardInterrupt("Watcher termination requested")
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  while True:
   committed=committed_checkpoints(p);completed=[];failed=[];pending=[]
   for epoch in p["expected_epochs"]:
    dest=run/"epochs"/f"epoch_{epoch:03d}";status=read(dest/"pipeline_status.json") if (dest/"pipeline_status.json").exists() else {}
    if status.get("phase")=="complete":completed.append(epoch)
    elif (dest/"final_failure.json").exists():failed.append(epoch)
    elif epoch in committed:pending.append(epoch)
   rows=summarize(run,p)
   if len(completed)+len(failed)==5:
    update(state="complete" if not failed else "complete_with_failures",completed_epochs=completed,failed_epochs=failed,scored_groups=len(rows));break
   if not pending:
    training=read(Path(p["training_source_run"])/"from_35/status.json")
    if training["state"]=="failed":update(state="training_failed",training_error=training.get("error"),completed_epochs=completed,failed_epochs=failed);break
    if training["state"]=="complete" and len(committed)!=5:raise AssertionError("Training completed without all five committed checkpoints")
    update(state="waiting_for_checkpoint",completed_epochs=completed,failed_epochs=failed,committed_epochs=sorted(committed),next_epoch=next(e for e in p["expected_epochs"] if e not in completed+failed),training_epoch=training.get("current_epoch"),training_step=training.get("epoch_step"),scored_groups=len(rows));time.sleep(20);continue
   epoch=pending[0];dest=prepare_epoch(run,p,committed[epoch]);verify_shared(run)
   used=int(subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip())
   if used>=512:update(state="waiting_for_A100_GPU",next_epoch=epoch,gpu_memory_used_MiB=used);time.sleep(20);continue
   with (run/"logs"/f"epoch_{epoch:03d}_pipeline.log").open("ab",buffering=0) as log:
    child=subprocess.Popen([PYTHON,"-u","-B","-m","amg_v21_checkpoint_eval.execute","pipeline","--run",str(dest)],cwd=GRAPH,env=env(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    update(state="evaluating_checkpoint",active_epoch=epoch,pipeline_pid=child.pid,completed_epochs=completed,failed_epochs=failed)
    while child.poll() is None:summarize(run,p);time.sleep(15)
   if child.returncode:
    write(dest/"final_failure.json",dict(epoch=epoch,exit_code=child.returncode,status=read(dest/"pipeline_status.json") if (dest/"pipeline_status.json").exists() else {},at=now()))
   else:assert read(dest/"pipeline_status.json")["phase"]=="complete"
   child=None
 except BaseException as exc:
  update(state="failed",error=repr(exc),traceback=traceback.format_exc())
  if child is not None and child.poll() is None:
   try:os.killpg(child.pid,signal.SIGTERM)
   except ProcessLookupError:pass
  raise
 finally:owner.close()
if __name__=="__main__":main()

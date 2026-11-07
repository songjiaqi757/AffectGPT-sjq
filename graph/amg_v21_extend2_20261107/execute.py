import argparse,collections,csv,io,json,math,os,signal,subprocess,sys,time,traceback
from .common import *
MODULE="amg_v21_extend2_20261107"
class PlannedInferencePause(Exception):pass
def pause_requested(run,node):return node=="A100" and (run/"pause_inference_A100.json").exists()
def spawn(run,mode,node,slot=None):
 args=[PYTHON,"-u","-B","-m",MODULE+".execute",mode,"--run",str(run),"--node",node]
 if slot is not None:args+=["--slot",str(slot)]
 with (run/"logs"/(mode+"_"+node+("_"+str(slot) if slot is not None else "")+".log")).open("ab",buffering=0) as out:
  return subprocess.Popen(args,cwd=G,env=env(),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
def training_claim(run,p,node):
 for spec in p["checkpoints"]:
  f=run/"training_jobs"/(str(spec["base_epoch"])+".json");h=lock(f.with_suffix(".lock"))
  if h is None:continue
  j=read(f)
  if j["state"]=="complete":h.close();continue
  if j["state"]!="pending":h.close();raise RuntimeError("Training interrupted or failed; see "+str(f))
  j.update(state="running",node=node,started_at=now());write(f,j);return spec,f,h,j
 return None
def all_inference(run):return all(read(f)["state"]=="complete" for f in (run/"jobs").glob("*.json"))
def finalize(run,p,jid):
 f=run/"jobs"/(jid+".json");h=lock(f.with_suffix(".lock"))
 if h is None:return
 try:
  j=read(f)
  if j["state"]=="complete" or not all(read(run/"shards"/(s+".json"))["state"]=="complete" for s in j["shards"]):return
  cp=checkpoint(run,j["base_epoch"],j["epoch"]);require(cp is not None,"Missing checkpoint")
  rows=read(p["datasets"][j["dataset"]]["path"]);values={};folder=run/"predictions"/jid;target=folder/"predictions.jsonl"
  with target.with_suffix(".tmp").open("w") as out:
   for row in rows:
    x=read(folder/(canonical(row["sample_id"])+".json"))
    require(x["checkpoint"]["sha256"]==cp["sha256"] and x["plan_id"]==p["plan_id"],"Wrong prediction provenance")
    require(x["name"]==row["name"] and x["name"] not in values,"Duplicate or wrong sample")
    values[x["name"]]=x["response"];out.write(json.dumps(x,ensure_ascii=False)+"\n")
  target.with_suffix(".tmp").replace(target)
  import numpy as np
  raw=folder/"name2reason.npz"
  with raw.with_suffix(".tmp").open("wb") as out:np.savez_compressed(out,name2reason=values)
  raw.with_suffix(".tmp").replace(raw)
  j.update(state="complete",finished_at=now(),checkpoint=cp,official_npz=str(raw),prediction_path=str(target),prediction_sha256=sha(target));write(f,j)
 finally:h.close()
def infer(run,node,slot):
 p=load_plan(run);verify_code(run);sf=f"worker_{node}_{slot}";model=None;cache={};rows={};total=0
 def update(**kw):status(run,sf,node=node,slot=slot,completed_samples=total,**kw)
 try:
  while not (run/"eval_cache_manifest.json").exists():
   require(not (run/"preparation_failed.json").exists(),"Evaluation prompt preparation failed")
   update(state="waiting_for_eval_cache");time.sleep(10)
  if pause_requested(run,node):update(state="paused_for_checkpoint_evaluation");return
  from amg_unified_eval.model import Predictor
  model=Predictor(p)
  while True:
   if pause_requested(run,node):update(state="paused_for_checkpoint_evaluation");return
   ready=[]
   for jobfile in sorted((run/"jobs").glob("*.json")):
    j=read(jobfile)
    if j["state"]=="complete":continue
    cp=checkpoint(run,j["base_epoch"],j["epoch"])
    if cp:
     for sid in j["shards"]:ready.append((0 if model.loaded==cp["sha256"] else 1,j["base_epoch"],j["epoch"],sid,cp))
   claimed=None
   for _,base,epoch,sid,cp in sorted(ready):
    f=run/"shards"/(sid+".json");s=read(f)
    if s["state"]=="complete":continue
    require(s["state"]!="failed","Inference shard exhausted retries: "+sid)
    h=lock(f.with_suffix(".lock"))
    if h is None:continue
    s=read(f)
    if s["state"]=="complete":h.close();continue
    require(s["attempts"]<3,"Shard retry budget exhausted")
    claimed=f,h,s,cp;break
   if claimed is None:
    if all_inference(run):break
    require(not any(read(f)["state"]=="failed" for f in (run/"training_jobs").glob("*.json")),"A training job failed; see training_jobs")
    update(state="waiting_for_checkpoints_or_inflight_shards");time.sleep(10);continue
   f,h,s,cp=claimed
   try:
    s.update(state="running",attempts=s["attempts"]+1,node=node,slot=slot,pid=os.getpid());write(f,s)
    if model.loaded!=cp["sha256"]:
     update(state="loading_checkpoint",base_epoch=s["base_epoch"],epoch=s["epoch"])
     with lock(run/("model_loading_"+node+".lock"),True):model.load(cp)
    capacity=run/f"capacity_{node}_{slot}.json"
    if not capacity.exists():
     status(run,f"probe_ready_{node}_{slot}",state="ready",node=node,slot=slot)
     deadline=time.monotonic()+2400
     while not all((run/f"probe_ready_{node}_{i}.json").exists() for i in range(4)):
      require(time.monotonic()<deadline,"Four-model loading barrier timeout");time.sleep(3)
     source=read(run/"source_probe.json");answer,info=model.predict(source["row"],source,stress=True)
     require(794<=info["stress_prompt_tokens"]<=800 and info["stress_generated_tokens"]==1200,"Capacity probe failed")
     write(capacity,dict(passed=True,node=node,slot=slot,info=info,at=now()))
    deadline=time.monotonic()+2400
    while not all((run/f"capacity_{node}_{i}.json").exists() for i in range(4)):
     require(time.monotonic()<deadline,"Four-way capacity barrier timeout");time.sleep(3)
    d=s["dataset"]
    if d not in rows:
     rows[d]=read(p["datasets"][d]["path"]);entry=next(e for e in read(run/"eval_cache_manifest.json")["parts"] if e["name"]==d)
     require(sha(entry["path"])==entry["sha256"],"Eval cache changed")
     with Path(entry["path"]).open() as stream:cache[d]={x["sample_id"]:x for x in map(json.loads,stream)}
    update(state="inference",base_epoch=s["base_epoch"],epoch=s["epoch"],dataset=d,shard=s["id"])
    folder=run/"predictions"/s["job_id"];folder.mkdir(exist_ok=True)
    for row in rows[d][s["start"]:s["stop"]]:
     if pause_requested(run,node):raise PlannedInferencePause()
     dest=folder/(canonical(row["sample_id"])+".json");b=cache[d][row["sample_id"]]
     binding=canonical([p["plan_id"],cp["sha256"],p["datasets"][d]["sha256"],b["cache_id"]])
     if dest.exists():require(read(dest)["binding"]==binding,"Stale prediction");continue
     require(b["row_sha256"]==canonical(row),"Wrong cached prompt")
     started=time.monotonic();answer,info=model.predict(row,b)
     write(dest,dict(sample_id=row["sample_id"],name=row["name"],dataset=d,base_epoch=s["base_epoch"],epoch=s["epoch"],response=answer,generation_empty=not answer.strip(),checkpoint=cp,binding=binding,plan_id=p["plan_id"],cache_id=b["cache_id"],prompt_info=info,node=node,slot=slot,elapsed_seconds=time.monotonic()-started))
     total+=1
     if total%8==0:update(state="inference",base_epoch=s["base_epoch"],epoch=s["epoch"],dataset=d,last_sample_id=row["sample_id"])
    s.update(state="complete",finished_at=now());write(f,s);finalize(run,p,s["job_id"])
   except PlannedInferencePause:
    s.update(state="pending",attempts=max(0,s["attempts"]-1),planned_yield_for_A100_evaluation=True);write(f,s)
    update(state="paused_for_checkpoint_evaluation");return
   except BaseException as exc:
    s.update(state="pending" if s["attempts"]<3 else "failed",error=repr(exc),traceback=traceback.format_exc());write(f,s);raise
   finally:h.close()
  update(state="complete")
 except BaseException as exc:update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
def summarize(run,p):
 with lock(run/"summary.lock",True):
  scores=[read(f) for f in (run/"scores").glob("*.json")]
  fields=["base_epoch","epoch","dataset","samples","main_metric","main_score","HIT","WAF","ACC","F_s","P_s","R_s"]
  stream=io.StringIO();w=csv.DictWriter(stream,fields,extrasaction="ignore");w.writeheader()
  for x in sorted(scores,key=lambda x:(x["base_epoch"],x["epoch"],x["dataset"])):w.writerow(dict(x,**x["metrics"]))
  f=run/"metrics_all.csv";f.with_suffix(".tmp").write_text(stream.getvalue());f.with_suffix(".tmp").replace(f)
  result=[]
  for spec in p["checkpoints"]:
   for epoch in spec["epochs"]:
    subset=[x for x in scores if x["base_epoch"]==spec["base_epoch"] and x["epoch"]==epoch]
    r=dict(base_epoch=spec["base_epoch"],epoch=epoch,datasets_completed=len(subset))
    for x in subset:
     for k,v in x["metrics"].items():r[x["dataset"]+"_"+k]=v
    result.append(r)
  write(run/"per_checkpoint_summary.json",result)
  cols=["base_epoch","epoch","datasets_completed"]+sorted({k for r in result for k in r if "_" in k and k not in ["base_epoch","datasets_completed"]})
  stream=io.StringIO();w=csv.DictWriter(stream,cols);w.writeheader();w.writerows(result)
  f=run/"per_checkpoint_summary.csv";f.with_suffix(".tmp").write_text(stream.getvalue());f.with_suffix(".tmp").replace(f)
  lines=["# Three trained branches each extended two epochs; corresponding datasets only","","Native v2.1 full graph + P4; all nine official test memberships.","",f"Completed official evaluation groups: {len(scores)} / 10.","","|Base|Epoch|Datasets|"+ "|".join(p["datasets"])+"|","|---:|---:|---:|"+"---:|"*len(p["datasets"])]
  for r in result:
   cells=[]
   for d in p["datasets"]:
    k=next((d+"_"+m for m in ["HIT","WAF","F_s"] if d+"_"+m in r),None);cells.append(f"{100*r[k]:.2f}" if k else "")
   lines.append("|"+str(r["base_epoch"])+"|"+str(r["epoch"])+"|"+str(r["datasets_completed"])+"|"+"|".join(cells)+"|")
  (run/"RESULTS.md").write_text("\n".join(lines)+"\n")
 from .comparison import report
 report(run,p)
 return len(scores)
def score(run,node):
 p=load_plan(run);verify_code(run);require(all_inference(run),"All inference must finish before scoring")
 for n in ["A800","A100"]:require(read(run/f"node_{n}.json")["inference_workers_exited"],"Inference still uses GPU")
 os.chdir(PROJECT/"AffectGPT");sys.path.insert(0,str(PROJECT/"AffectGPT"));import evaluation
 from amg_inference.full_score import truth,DISCRETE,DIMENSION
 judge=None;refs={}
 for f in sorted((run/"jobs").glob("*.json")):
  dest=run/"scores"/f.name
  if dest.exists():continue
  h=lock((run/"scores"/f.name).with_suffix(".lock"))
  if h is None:continue
  try:
   if dest.exists():continue
   j=read(f);d=j["dataset"];raw=Path(j["official_npz"])
   status(run,"scoring_"+node,state="loading_judge" if judge is None else "scoring",job=j["id"])
   if judge is None:judge=evaluation.func_read_batch_calling_model("Qwen25")
   if d not in refs:refs[d]=truth(d,p,evaluation)
   gt=refs[d];require(len(gt)==j["samples"],"Ground truth membership mismatch")
   import zipfile
   for suffix in ["-openset.npz","-openset-sentiment.npz"]:
    cachefile=raw.with_name(raw.stem+suffix)
    if cachefile.exists():
     try:
      with zipfile.ZipFile(cachefile) as z:valid=z.testzip() is None
     except (OSError,zipfile.BadZipFile):valid=False
     if not valid:cachefile.unlink()
   if d in DISCRETE:v,_=evaluation.calculate_discrete_zeroshot(str(raw),gt,*judge,True);metrics=dict(HIT=float(v));metric="HIT"
   elif d in DIMENSION:v,acc=evaluation.calculate_dimension_zeroshot(str(raw),gt,*judge,True);metrics=dict(WAF=float(v),ACC=float(acc));metric="WAF"
   else:v,pr,re=evaluation.calculate_ov_zeroshot(str(raw),gt,*judge,True);metrics=dict(F_s=float(v),P_s=float(pr),R_s=float(re));metric="F_s"
   require(all(math.isfinite(x) for x in metrics.values()),"Nonfinite score")
   write(dest,dict(base_epoch=j["base_epoch"],epoch=j["epoch"],dataset=d,samples=len(gt),main_metric=metric,main_score=float(v),metrics=metrics,checkpoint=j["checkpoint"],plan_id=p["plan_id"],raw_sha256=sha(raw),official_evaluation_source=str(PROJECT/"AffectGPT/evaluation.py"),completed_at=now(),node=node))
   summarize(run,p)
  finally:h.close()
 while summarize(run,p)<10:status(run,"scoring_"+node,state="waiting_for_other_evaluator");time.sleep(15)
 status(run,"scoring_"+node,state="complete",groups=10)
def node_main(run,node):
 p=load_plan(run);verify_code(run);owner=lock(run/("node_"+node+".lock"));require(owner is not None,"Node controller already running");children=[]
 sf="node_"+node;completed=[]
 def update(**kw):status(run,sf,node=node,completed_training=completed,inference_workers_exited=False,**kw)
 try:
  update(phase="waiting_for_training_cache")
  while not (run/"cpu_preflight.json").exists():
   if (run/"preparation_failed.json").exists():raise RuntimeError("Preparation failed")
   time.sleep(10)
  while True:
   claim=training_claim(run,p,node)
   if claim is None:break
   spec,f,h,j=claim
   try:
    args=[PYTHON,"-u","-B","-m",MODULE+".train_worker","--run",str(run),"--base-epoch",str(spec["base_epoch"])]
    with (run/"logs"/f"train_from_{spec['base_epoch']}_{node}.log").open("ab",buffering=0) as stream:
     child=subprocess.Popen(args,cwd=G,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    children=[child];update(phase="training",base_epoch=spec["base_epoch"],training_pid=child.pid)
    rc=child.wait();children=[];require(rc==0,"Training failed: "+str(spec["base_epoch"]))
    require(read(run/f"experiment_{spec['base_epoch']}_status.json")["state"]=="complete","Training completion missing")
    j.update(state="complete",finished_at=now());write(f,j);completed.append(spec["base_epoch"])
   except BaseException as exc:j.update(state="failed",error=repr(exc));write(f,j);raise
   finally:h.close()
  update(phase="starting_four_inference_workers")
  children=[spawn(run,"infer",node,s) for s in range(4)];retries=collections.Counter();active={s:c for s,c in enumerate(children)}
  while active:
   for slot,child in list(active.items()):
    rc=child.poll()
    if rc is None:continue
    if rc==0:del active[slot]
    else:
     retries[slot]+=1;require(retries[slot]<=2,"Inference worker repeatedly failed")
     active[slot]=spawn(run,"infer",node,slot);children.append(active[slot])
   update(phase="inference",worker_pids={s:c.pid for s,c in active.items()},retries=dict(retries));time.sleep(15)
  for f in (run/"jobs").glob("*.json"):finalize(run,p,f.stem)
  require(all_inference(run),"Incomplete inference")
  status(run,sf,node=node,phase="waiting_for_global_inference_barrier",completed_training=completed,inference_workers_exited=True)
  while not all((run/f"node_{n}.json").exists() and read(run/f"node_{n}.json").get("inference_workers_exited") for n in ["A800","A100"]):time.sleep(15)
  with lock(run/"inference_barrier.lock",True):
   if not (run/"inference_barrier.json").exists():write(run/"inference_barrier.json",dict(passed=True,groups=10,predictions=p["sample_predictions_total"],all_eight_workers_exited=True,at=now()))
  for attempt in range(3):
   child=spawn(run,"score",node);children=[child];rc=child.wait();children=[]
   if rc==0:break
   require(attempt<2,"Evaluation repeatedly failed");time.sleep(15)
  require(summarize(run,p)==10,"Incomplete official scoring")
  status(run,sf,node=node,phase="complete",completed_training=completed,inference_workers_exited=True,results=str(run/"RESULTS.md"))
 except BaseException as exc:
  status(run,sf,node=node,phase="failed",completed_training=completed,inference_workers_exited=False,error=repr(exc),traceback=traceback.format_exc())
  for child in children:
   if child.poll() is None:
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:owner.close()
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("mode",choices=["node","infer","score"]);a.add_argument("--run",required=True);a.add_argument("--node",required=True);a.add_argument("--slot",type=int);v=a.parse_args()
 {"node":lambda:node_main(Path(v.run),v.node),"infer":lambda:infer(Path(v.run),v.node,v.slot),"score":lambda:score(Path(v.run),v.node)}[v.mode]()

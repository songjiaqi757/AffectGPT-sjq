"""Train three branches and evaluate assigned datasets on A100 as each artifact finishes."""
import argparse,collections,csv,json,math,os,signal,subprocess,sys,time,traceback,zipfile
from .common import *
from .execute import all_inference,finalize,summarize,spawn,training_claim
def pause_path(run):return run/"pause_inference_A100.json"
def used_memory():
 return int(subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip())
def wait_gpu(run,node,reason):
 deadline=time.monotonic()+240
 while used_memory()>512:
  require(time.monotonic()<deadline,"GPU not released before "+reason)
  time.sleep(3)
def selected_groups(jobs,datasets,scores):
 groups=collections.defaultdict(dict)
 for j in jobs:
  k=(j["base_epoch"],j["epoch"])
  require(j["dataset"] not in groups[k],"Duplicate dataset job for checkpoint")
  groups[k][j["dataset"]]=j
 ready=[]
 for (base,epoch),items in sorted(groups.items()):
  expected=datasets[str(base)]
  if set(items)!=set(expected) or not all(j["state"]=="complete" for j in items.values()):continue
  if all(j["id"] in scores for j in items.values()):continue
  hashes={j["checkpoint"]["sha256"] for j in items.values()}
  require(len(hashes)==1,"Assigned datasets do not reference one checkpoint")
  ready.append((base,epoch))
 return ready
def ready_groups(run,p):
 jobs=[read(f) for f in (run/"jobs").glob("*.json")]
 scores={f.stem for f in (run/"scores").glob("*.json")}
 return selected_groups(jobs,p["datasets_by_base"],scores)
def score_group(run,base,epoch):
 p=load_plan(run);verify_code(run);require((base,epoch) in selected_groups([read(f) for f in (run/"jobs").glob("*.json")],p["datasets_by_base"],set()),"Assigned dataset readiness not satisfied")
 require(pause_path(run).exists(),"A100 inference was not paused")
 require(used_memory()<512,"A100 GPU is occupied before evaluation")
 owner=lock(run/"A100_evaluator.lock");require(owner is not None,"Another evaluator owns A100")
 os.chdir(PROJECT/"AffectGPT");sys.path.insert(0,str(PROJECT/"AffectGPT"));import evaluation
 from amg_inference.full_score import truth,DISCRETE,DIMENSION
 jobs=[]
 for d in p["datasets_by_base"][str(base)]:
  f=run/"jobs"/f"from_{base:02d}_epoch_{epoch:02d}_{d}.json";j=read(f)
  require(j["state"]=="complete","Dataset inference incomplete")
  require(j["checkpoint"]["sha256"]==checkpoint(run,base,epoch)["sha256"],"Checkpoint provenance mismatch")
  jobs.append(j)
 judge=None;count=0
 try:
  for j in jobs:
   dest=run/"scores"/(j["id"]+".json");h=lock(dest.with_suffix(".lock"),True)
   try:
    if dest.exists():
     x=read(dest);require(x["plan_id"]==p["plan_id"] and x["checkpoint"]["sha256"]==j["checkpoint"]["sha256"],"Stale score");count+=1;continue
    d=j["dataset"];raw=Path(j["official_npz"])
    require(raw.is_file() and sha(j["prediction_path"])==j["prediction_sha256"],"Committed inference output changed")
    status(run,"scoring_A100",state="loading_judge" if judge is None else "scoring",base_epoch=base,epoch=epoch,dataset=d,datasets_complete=count,datasets_total=len(jobs))
    if judge is None:
     from vllm import SamplingParams
     llm,tok,native=evaluation.func_read_batch_calling_model("Qwen25")
     params=SamplingParams(**p["judge"])
     require(params.temperature==0 and params.top_p==1 and params.repetition_penalty==1.05 and params.max_tokens==512,"Judge configuration mismatch")
     judge=(llm,tok,params)
     write(run/f"judge_runtime_from_{base}_epoch_{epoch}.json",dict(parameters=repr(params),sampling_type=str(params.sampling_type),node="A100",at=now()))
    gt=truth(d,p,evaluation);require(len(gt)==j["samples"],"Official test membership mismatch")
    for suffix in ["-openset.npz","-openset-sentiment.npz"]:
     f=raw.with_name(raw.stem+suffix)
     if f.exists():
      try:
       with zipfile.ZipFile(f) as z:valid=z.testzip() is None
      except (OSError,zipfile.BadZipFile):valid=False
      if not valid:f.unlink()
    if d in DISCRETE:v,_=evaluation.calculate_discrete_zeroshot(str(raw),gt,*judge,True);metrics=dict(HIT=float(v));metric="HIT"
    elif d in DIMENSION:v,acc=evaluation.calculate_dimension_zeroshot(str(raw),gt,*judge,True);metrics=dict(WAF=float(v),ACC=float(acc));metric="WAF"
    else:v,pr,re=evaluation.calculate_ov_zeroshot(str(raw),gt,*judge,True);metrics=dict(F_s=float(v),P_s=float(pr),R_s=float(re));metric="F_s"
    require(all(math.isfinite(v) for v in metrics.values()),"Nonfinite official score")
    write(dest,dict(base_epoch=base,epoch=epoch,dataset=d,samples=len(gt),main_metric=metric,main_score=float(v),metrics=metrics,checkpoint=j["checkpoint"],plan_id=p["plan_id"],raw_sha256=sha(raw),official_evaluation_source=str(PROJECT/"AffectGPT/evaluation.py"),completed_at=now(),node="A100",dispatch="checkpoint_complete_nine_datasets"))
    count+=1;summarize(run,p)
   finally:h.close()
  require(count==len(jobs),"Incomplete assigned checkpoint evaluation")
  out=run/"checkpoint_results"/f"from_{base:02d}_epoch_{epoch:02d}";out.mkdir(parents=True,exist_ok=True)
  values=[read(run/"scores"/(j["id"]+".json")) for j in jobs];write(out/"metrics.json",dict(base_epoch=base,epoch=epoch,checkpoint=jobs[0]["checkpoint"],datasets=values,complete=True,completed_at=now(),node="A100"))
  import io
  stream=io.StringIO();cols=["dataset","samples","main_metric","main_score","HIT","WAF","ACC","F_s","P_s","R_s"];w=csv.DictWriter(stream,cols,extrasaction="ignore");w.writeheader()
  for x in values:w.writerow(dict(x,**x["metrics"]))
  (out/"metrics.csv").write_text(stream.getvalue())
  lines=[f"# Base {base}, continuation epoch {epoch}","","Official evaluation on A100; all assigned datasets complete.","","|Dataset|Metric|Score (%)|","|---|---|---:|"]
  for x in values:lines.append(f"|{x['dataset']}|{x['main_metric']}|{100*x['main_score']:.2f}|")
  (out/"RESULTS.md").write_text("\n".join(lines)+"\n")
  summarize(run,p);status(run,"scoring_A100",state="checkpoint_complete",base_epoch=base,epoch=epoch,datasets_complete=len(jobs),results=str(out/"RESULTS.md"))
 finally:owner.close()
def adopt_training(run,p,node):
 completed=[]
 while True:
  claim=training_claim(run,p,node)
  if claim is None:break
  spec,f,h,j=claim
  try:
   args=[PYTHON,"-u","-B","-m","amg_v21_extend2_20261107.train_worker","--run",str(run),"--base-epoch",str(spec["base_epoch"])]
   with (run/"logs"/f"train_from_{spec['base_epoch']}_{node}.log").open("ab",buffering=0) as stream:
    child=subprocess.Popen(args,cwd=G,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
   status(run,"node_"+node,node=node,phase="training",base_epoch=spec["base_epoch"],training_pid=child.pid,completed_training=completed,inference_workers_exited=False)
   rc=child.wait();require(rc==0,"Training failed: "+str(spec["base_epoch"]))
   st=read(run/f"experiment_{spec['base_epoch']}_status.json")
   require(st["state"]=="complete" and st["completed_steps"]==10000 and st["completed_epochs"]==2,"Incomplete two-epoch continuation")
   require(len(read(Path(spec["output"])/"checkpoints.json"))==2,"Missing saved epoch")
   j.update(state="complete",finished_at=now());write(f,j);completed.append(spec["base_epoch"])
  except BaseException as exc:j.update(state="failed",error=repr(exc));write(f,j);raise
  finally:h.close()
 return completed
def children_stop(run,node,active,planned=True):
 if node=="A100":write(pause_path(run),dict(pause=True,reason="Nine-dataset checkpoint ready for official A100 evaluation",at=now()))
 deadline=time.monotonic()+600
 while active:
  for slot,child in list(active.items()):
   if child.poll() is not None:del active[slot]
  require(time.monotonic()<deadline,"Inference did not yield to evaluation")
  if active:time.sleep(2)
 wait_gpu(run,node,"evaluation")
def score_launch(run,base,epoch):
 args=[PYTHON,"-u","-B","-m","amg_v21_extend2_20261107.rolling","score-group","--run",str(run),"--base-epoch",str(base),"--epoch",str(epoch)]
 with (run/"logs"/f"score_from_{base}_epoch_{epoch}_A100.log").open("ab",buffering=0) as stream:
  return subprocess.Popen(args,cwd=G,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
def node_main(run,node):
 p=load_plan(run);verify_code(run);owner=lock(run/("node_"+node+".lock"));require(owner is not None,"Node controller already active")
 gpu=subprocess.check_output(["nvidia-smi","--query-gpu=name","--format=csv,noheader"],text=True);require(node in gpu,"Wrong physical GPU for node")
 active={};child_score=None;retries=collections.Counter();completed=[]
 def update(phase,**kw):status(run,"node_"+node,node=node,phase=phase,completed_training=completed,inference_workers_exited=not bool(active),evaluation_dispatch="checkpoint_nine_datasets_A100_only",**kw)
 def start_workers():
  if node=="A100":pause_path(run).unlink(missing_ok=True)
  wait_gpu(run,node,"four-way inference")
  for slot in range(4):active[slot]=spawn(run,"infer",node,slot)
 def collect():
  for slot,child in list(active.items()):
   rc=child.poll()
   if rc is None:continue
   del active[slot]
   if rc!=0:
    retries[slot]+=1;require(retries[slot]<=2,"Inference worker exhausted retries")
    active[slot]=spawn(run,"infer",node,slot)
 try:
  completed=adopt_training(run,p,node);wait_gpu(run,node,"inference after training")
  while True:
   collect()
   ready=ready_groups(run,p) if node=="A100" else []
   if ready:
    base,epoch=ready[0]
    update("pausing_A100_inference_for_checkpoint_evaluation",base_epoch=base,epoch=epoch,worker_pids={s:c.pid for s,c in active.items()})
    children_stop(run,node,active)
    for attempt in range(3):
     update("evaluating_checkpoint",base_epoch=base,epoch=epoch)
     child_score=score_launch(run,base,epoch);rc=child_score.wait()
     try:os.killpg(child_score.pid,signal.SIGTERM)
     except ProcessLookupError:pass
     child_score=None;wait_gpu(run,node,"inference after evaluation")
     if rc==0:break
     require(attempt<2,"Checkpoint official evaluation repeatedly failed")
    continue
   done=all_inference(run)
   if done:
    while active:collect();time.sleep(2)
    for f in (run/"jobs").glob("*.json"):finalize(run,p,f.stem)
    if node=="A100" and len(list((run/"scores").glob("*.json")))<10:continue
    if summarize(run,p)==10:break
    update("waiting_for_A100_checkpoint_evaluations",inference_groups_complete=10)
    other=read(run/"node_A100.json");require(other.get("phase")!="failed","A100 evaluation controller failed")
    time.sleep(10);continue
   if not active:start_workers()
   update("inference",worker_pids={s:c.pid for s,c in active.items()},retries=dict(retries))
   time.sleep(5)
  update("complete",results=str(run/"RESULTS.md"),scored_groups=10)
 except BaseException as exc:
  update("failed",error=repr(exc),traceback=traceback.format_exc())
  for child in list(active.values())+([child_score] if child_score else []):
   if child.poll() is None:
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:owner.close()
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("mode",choices=["node","score-group"]);a.add_argument("--run",required=True);a.add_argument("--node",choices=["A800","A100"]);a.add_argument("--base-epoch",type=int);a.add_argument("--epoch",type=int);v=a.parse_args()
 if v.mode=="node":node_main(Path(v.run),v.node)
 else:score_group(Path(v.run),v.base_epoch,v.epoch)

"""Re-evaluate frozen AffectGPT predictions using only greedy Qwen judge changes."""
import argparse,collections,csv,io,json,math,os,signal,subprocess,sys,time,traceback,zipfile
from amg_v21_batch_20261106.common import *
K=G/"amg_v21_rejudge_20261107"
def verify(run):
 p=load_plan(run)
 for f,h in read(run/"code_manifest.json")["files"].items():require(sha(f)==h,"Evaluation source changed: "+f)
 require(sha(Path(p["source_run"])/"plan.json")==p["source_plan_sha256"],"Source plan changed")
 require(read(run/"preflight.json")["passed"],"Preflight has not passed")
 for f,b in read(run/"model_assets_manifest.json")["assets"].items():
  st=Path(f).stat();require(st.st_size==b["bytes"] and st.st_mtime_ns==b["mtime_ns"],"Model asset changed")
 return p
def atomic_text(f,value):
 f=Path(f);tmp=f.with_name(f.name+".tmp")
 fs_retry(lambda:tmp.write_text(value),tmp);fs_retry(lambda:tmp.replace(f),f)
def csv_text(rows,fields):
 s=io.StringIO();w=csv.DictWriter(s,fields,extrasaction="ignore");w.writeheader();w.writerows(rows);return s.getvalue()
def summarize(run,p):
 with lock(run/"summary.lock",True):
  scores=[read(f) for f in (run/"scores").glob("*.json")]
  specs={j["id"]:j for j in p["jobs"]};scored={x["job_id"]:x for x in scores}
  fields=["base_epoch","epoch","dataset","samples","main_metric","main_score","HIT","WAF","ACC","F_s","P_s","R_s","node"]
  rows=[dict(x,**x["metrics"]) for x in sorted(scores,key=lambda x:(x["base_epoch"],x["epoch"],x["dataset"]))]
  atomic_text(run/"metrics_all.csv",csv_text(rows,fields))
  paired=[]
  for x in rows:
   old=specs[x["job_id"]];paired.append(dict(x,baseline_main_score=old["baseline_main_score"],new_main_score=x["main_score"],delta_pp=100*(x["main_score"]-old["baseline_main_score"])))
  atomic_text(run/"paired_comparison_all.csv",csv_text(paired,["base_epoch","epoch","dataset","samples","main_metric","baseline_main_score","new_main_score","delta_pp","node"]))
  best=[];fixed=[]
  for d,baseline in p["baseline_winners"].items():
   matches=[x for x in scores if x["dataset"]==d];old=specs[baseline["job_id"]]
   entry=dict(dataset=d,main_metric=old["baseline_main_metric"],baseline_best_score=baseline["main_score"],baseline_base_epoch=baseline["base_epoch"],baseline_epoch=baseline["epoch"],evaluated=len(matches),expected=25)
   if matches:
    winner=max(matches,key=lambda x:x["main_score"]);entry.update(new_best_score=winner["main_score"],new_base_epoch=winner["base_epoch"],new_epoch=winner["epoch"],new_metrics=winner["metrics"],delta_pp=100*(winner["main_score"]-baseline["main_score"]))
   best.append(entry)
   if baseline["job_id"] in scored:
    x=scored[baseline["job_id"]];fixed.append(dict(dataset=d,main_metric=x["main_metric"],base_epoch=x["base_epoch"],epoch=x["epoch"],baseline_score=baseline["main_score"],new_score=x["main_score"],delta_pp=100*(x["main_score"]-baseline["main_score"])))
  complete=len(scores)==225
  fixed_mean=math.fsum(x["new_score"] for x in fixed)/9 if len(fixed)==9 else None
  best_mean=math.fsum(x["new_best_score"] for x in best)/9 if complete else None
  summary=dict(complete=complete,scored_jobs=len(scores),expected_jobs=225,baseline_best_mean=p["baseline_best_mean"],greedy_fixed_original_winners_mean=fixed_mean,greedy_reselected_best_mean=best_mean,original_winners_evaluated=len(fixed),dataset_best=best,judge=p["judge"],at=now())
  write(run/"summary.json",summary)
  atomic_text(run/"best_by_dataset.csv",csv_text(best,["dataset","main_metric","baseline_best_score","baseline_base_epoch","baseline_epoch","new_best_score","new_base_epoch","new_epoch","delta_pp","evaluated","expected"]))
  atomic_text(run/"fixed_original_winners_comparison.csv",csv_text(fixed,["dataset","main_metric","base_epoch","epoch","baseline_score","new_score","delta_pp"]))
  groups=collections.defaultdict(list)
  for x in scores:groups[(x["base_epoch"],x["epoch"])].append(x)
  checkpoints=[]
  for (base,epoch),xs in sorted(groups.items()):
   row=dict(base_epoch=base,epoch=epoch,datasets_complete=len(xs),mean_main_score=math.fsum(x["main_score"] for x in xs)/9 if len(xs)==9 else None)
   for x in xs:row[x["dataset"]]=x["main_score"]
   checkpoints.append(row)
  atomic_text(run/"per_checkpoint_summary.csv",csv_text(checkpoints,["base_epoch","epoch","datasets_complete","mean_main_score"]+list(p["datasets"])))
  lines=["# Re-evaluation with greedy Qwen25 judge","","Frozen original AffectGPT predictions. Only judge temperature 0.7 -> 0 and top_p 0.8 -> 1 changed. Official metrics, prompts, repetition_penalty 1.05, max_tokens 512, labels and test memberships preserved.","",f"Scored dataset jobs: {len(scores)}/225.",f"Original dataset-wise best mean: {100*p['baseline_best_mean']:.6f}%.",""]
  if fixed_mean is not None:lines.append(f"New mean at the FIXED original nine winning checkpoints: {100*fixed_mean:.6f}% (delta {100*(fixed_mean-p['baseline_best_mean']):+.6f} percentage points).")
  if best_mean is not None:lines.append(f"New dataset-wise reselected best mean after all 225 scores: {100*best_mean:.6f}% (delta {100*(best_mean-p['baseline_best_mean']):+.6f} percentage points).")
  lines+=["","|Dataset|Metric|Original best (%)|New best (%)|New base -> epoch|Compared checkpoints|","|---|---|---:|---:|---|---:|"]
  for x in best:
   value=f"{100*x['new_best_score']:.2f}" if "new_best_score" in x else ""
   cp=f"{x['new_base_epoch']} -> {x['new_epoch']}" if "new_best_score" in x else ""
   lines.append(f"|{x['dataset']}|{x['main_metric']}|{100*x['baseline_best_score']:.2f}|{value}|{cp}|{x['evaluated']}/25|")
  if not complete:lines+=["","New best values are provisional until all 25 checkpoints for every dataset have been evaluated."]
  atomic_text(run/"RESULTS.md","\n".join(lines)+"\n")
 return len(scores)
def claim(run,p):
 spec={j["id"]:j for j in p["jobs"]}
 ordered=sorted((run/"jobs").glob("*.json"),key=lambda f:(read(f)["priority"],read(f)["base_epoch"],read(f)["epoch"],-spec[f.stem]["samples"],f.stem))
 for f in ordered:
  h=lock(f.with_suffix(".lock"))
  if h is None:continue
  j=read(f)
  if j["state"]=="complete":h.close();continue
  dest=run/"scores"/f.name
  if dest.exists():
   x=read(dest);require(x["plan_id"]==p["plan_id"] and x["job_id"]==j["id"],"Stale committed score")
   j.update(state="complete",recovered_committed_score=True);write(f,j);h.close();continue
  if j["state"]=="failed" or j["attempts"]>=3:
   h.close();raise RuntimeError("Job exhausted retries: "+j["id"])
  j.update(state="running",attempts=j["attempts"]+1,pid=os.getpid(),started_at=now());write(f,j)
  return f,h,j,spec[j["id"]]
 return None
def worker(run,node):
 p=verify(run);owner=lock(run/f"judge_worker_{node}.lock");require(owner is not None,"Judge worker already active")
 state=dict(node=node,pid=os.getpid(),completed_this_worker=0,plan_id=p["plan_id"],judge=p["judge"])
 def update(**kw):state.update(kw,at=now());write(run/"workers"/(node+".json"),state)
 try:
  require(used_memory()<512,"GPU occupied before loading judge")
  os.chdir(PROJECT/"AffectGPT");sys.path.insert(0,str(PROJECT/"AffectGPT"));import evaluation
  from vllm import SamplingParams
  from amg_inference.full_score import truth,DISCRETE,DIMENSION
  update(state="loading_judge")
  llm,tokenizer,old=evaluation.func_read_batch_calling_model("Qwen25")
  params=SamplingParams(temperature=0,top_p=1,repetition_penalty=old.repetition_penalty,max_tokens=old.max_tokens)
  fields=getattr(old,"__struct_fields__",None) or tuple(vars(old))
  changed={k:dict(old=repr(getattr(old,k)),new=repr(getattr(params,k))) for k in fields if getattr(old,k)!=getattr(params,k)}
  require(set(changed)=={"temperature","top_p"},"Unexpected judge parameter changed")
  require(old.temperature==.7 and old.top_p==.8 and params.repetition_penalty==1.05 and params.max_tokens==512,"Judge baseline configuration mismatch")
  write(run/f"judge_runtime_{node}.json",dict(passed=True,node=node,pid=os.getpid(),changed=changed,old_parameters=repr(old),new_parameters=repr(params),sampling_type=str(params.sampling_type),all_other_sampling_fields_equal=True,model_loader="Unchanged evaluation.func_read_batch_calling_model Qwen25",at=now()))
  refs={};judge=(llm,tokenizer,params);update(state="ready")
  while True:
   selected=claim(run,p)
   if selected is None:
    states=collections.Counter(read(f)["state"] for f in (run/"jobs").glob("*.json"))
    if states.get("complete",0)==225:break
    require(not states.get("failed"),"A scoring job failed")
    update(state="waiting_for_other_worker",job_counts=dict(states));time.sleep(5);continue
   f,h,j,spec=selected
   try:
    d=spec["dataset"];raw=Path(spec["raw_path"]);require(sha(raw)==spec["raw_sha256"] and sha(spec["source_prediction_archive"])==spec["raw_sha256"],"Prediction archive changed")
    require(sha(spec["baseline_score_path"])==spec["baseline_score_sha256"],"Original score changed")
    binding=canonical([p["plan_id"],j["id"],spec["raw_sha256"],spec["checkpoint"]["sha256"]]);update(state="scoring",job_id=j["id"],dataset=d,base_epoch=spec["base_epoch"],epoch=spec["epoch"])
    for suffix in ["-openset.npz","-openset-sentiment.npz"]:
     cache=raw.with_name(raw.stem+suffix)
     if cache.exists():
      try:
       with zipfile.ZipFile(cache) as z:valid=z.testzip() is None
      except (OSError,zipfile.BadZipFile):valid=False
      if not valid:cache.unlink()
    if d not in refs:refs[d]=truth(d,p,evaluation)
    gt=refs[d];require(len(gt)==spec["samples"],"Ground truth membership mismatch");started=time.monotonic()
    if d in DISCRETE:v,_=evaluation.calculate_discrete_zeroshot(str(raw),gt,*judge,True);metric="HIT";metrics=dict(HIT=float(v))
    elif d in DIMENSION:v,acc=evaluation.calculate_dimension_zeroshot(str(raw),gt,*judge,True);metric="WAF";metrics=dict(WAF=float(v),ACC=float(acc))
    else:v,pr,re=evaluation.calculate_ov_zeroshot(str(raw),gt,*judge,True);metric="F_s";metrics=dict(F_s=float(v),P_s=float(pr),R_s=float(re))
    require(metric==spec["baseline_main_metric"] and all(math.isfinite(v) for v in metrics.values()),"Metric contract changed")
    result=dict(job_id=j["id"],base_epoch=spec["base_epoch"],epoch=spec["epoch"],dataset=d,samples=spec["samples"],checkpoint=spec["checkpoint"],main_metric=metric,main_score=float(v),metrics=metrics,baseline_main_score=spec["baseline_main_score"],baseline_metrics=spec["baseline_metrics"],delta_pp=100*(float(v)-spec["baseline_main_score"]),raw_path=str(raw),raw_sha256=spec["raw_sha256"],binding=binding,plan_id=p["plan_id"],judge=p["judge"],node=node,elapsed_seconds=time.monotonic()-started,completed_at=now())
    write(run/"scores"/f.name,result);j.update(state="complete",node=node,score_path=str(run/"scores"/f.name),finished_at=now());write(f,j)
    state["completed_this_worker"]+=1;summarize(run,p);update(state="ready",last_job=j["id"],last_score=float(v),last_delta_pp=result["delta_pp"])
   except BaseException as exc:
    j.update(state="pending" if j["attempts"]<3 else "failed",error=repr(exc),traceback=traceback.format_exc());write(f,j);raise
   finally:h.close()
  require(summarize(run,p)==225,"Incomplete final scoring");update(state="complete",completed_total=225,results=str(run/"RESULTS.md"))
 except BaseException as exc:update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:owner.close()
def used_memory():
 return int(subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip())
def supervise(run,node):
 p=verify(run);owner=lock(run/f"supervisor_{node}.lock");require(owner is not None,"Supervisor already active")
 gpu=subprocess.check_output(["nvidia-smi","--query-gpu=name","--format=csv,noheader"],text=True).strip();require(node in gpu,"Unexpected physical GPU")
 child=None
 def update(**kw):status(run,"supervisor_"+node,node=node,gpu=gpu,**kw)
 def release():
  deadline=time.monotonic()+240
  while used_memory()>512:require(time.monotonic()<deadline,"Judge GPU memory did not release");time.sleep(3)
 try:
  require(used_memory()<512,"GPU occupied before starting re-evaluation")
  for attempt in range(4):
   require(not any(read(f)["state"]=="failed" for f in (run/"jobs").glob("*.json")),"Shared job retry budget exhausted")
   with (run/"logs"/f"worker_{node}_attempt_{attempt}.log").open("ab",buffering=0) as stream:
    child=subprocess.Popen([PYTHON,"-u","-B","-m","amg_v21_rejudge_20261107.execute","worker","--run",str(run),"--node",node],cwd=G,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
   update(state="running",attempt=attempt,judge_pid=child.pid)
   rc=child.wait()
   try:os.killpg(child.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   child=None;release()
   if rc==0:
    require(len(list((run/"scores").glob("*.json")))==225,"Worker exited before all scores were committed")
    update(state="complete",scored_jobs=225,results=str(run/"RESULTS.md"));return
   require(attempt<3,"Judge worker repeatedly failed");update(state="retrying",previous_returncode=rc);time.sleep(5)
 except BaseException as exc:
  update(state="failed",error=repr(exc),traceback=traceback.format_exc())
  if child and child.poll() is None:
   try:os.killpg(child.pid,signal.SIGTERM)
   except ProcessLookupError:pass
  raise
 finally:owner.close()
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("mode",choices=["worker","supervise","summarize"]);a.add_argument("--run",required=True);a.add_argument("--node",choices=["A800","A100"]);v=a.parse_args();r=Path(v.run)
 if v.mode=="worker":worker(r,v.node)
 elif v.mode=="supervise":supervise(r,v.node)
 else:summarize(r,verify(r))

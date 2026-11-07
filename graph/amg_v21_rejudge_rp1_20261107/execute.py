"""Re-evaluate frozen AffectGPT predictions using only greedy Qwen judge changes."""
import argparse,collections,csv,io,json,math,os,signal,subprocess,sys,time,traceback,zipfile
from amg_v21_batch_20261106.common import *
K=G/"amg_v21_rejudge_rp1_20261107"
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
  scores=[read(f) for f in (run/"scores").glob("*.json")];specs={j["id"]:j for j in p["jobs"]}
  rows=[]
  for x in sorted(scores,key=lambda x:list(p["datasets"]).index(x["dataset"])):
   old=specs[x["job_id"]]
   rows.append(dict(x,**x["metrics"],native_reference_score=old["native_reference_score"],previous_score=old["baseline_main_score"],current_score=x["main_score"],delta_vs_previous_pp=100*(x["main_score"]-old["baseline_main_score"]),delta_vs_native_pp=100*(x["main_score"]-old["native_reference_score"])))
  fields=["dataset","base_epoch","epoch","main_metric","native_reference_score","previous_score","current_score","delta_vs_previous_pp","delta_vs_native_pp","HIT","WAF","ACC","F_s","P_s","R_s","node"]
  atomic_text(run/"metrics_all.csv",csv_text(rows,fields));atomic_text(run/"paired_comparison.csv",csv_text(rows,fields))
  complete=len(rows)==p["expected_jobs"]
  mean=math.fsum(x["main_score"] for x in rows)/9 if complete else None
  summary=dict(complete=complete,scored_jobs=len(rows),expected_jobs=p["expected_jobs"],selected_pairs=p["expected_jobs"],distinct_checkpoints=p["expected_artifacts"],judge=p["judge"],previous_judge=p["baseline_judge"],native_reference_mean=p["native_reference_mean"],previous_T0_P1_RP105_mean=p["baseline_best_mean"],current_fixed_pairs_mean=mean,delta_vs_previous_pp=100*(mean-p["baseline_best_mean"]) if complete else None,delta_vs_native_pp=100*(mean-p["native_reference_mean"]) if complete else None,results=rows,checkpoint_choices_frozen=True,at=now())
  write(run/"summary.json",summary)
  lines=["# Fixed best checkpoint evaluation: repetition penalty 1.0","","Exactly nine previously chosen dataset/checkpoint pairs. Raw predictions, physical GPU assignment, prompts, metrics and labels preserved. The only change from the previous greedy evaluation is repetition_penalty 1.05 -> 1.0.","",f"Scored pairs: {len(rows)}/{p['expected_jobs']}.",f"Original stochastic judge reference: {100*p['native_reference_mean']:.6f}%.",f"Previous T0/P1 with RP1.05: {100*p['baseline_best_mean']:.6f}%.",""]
  if complete:lines.append(f"Current T0/P1 with RP1.0: {100*mean:.6f}% (delta {100*(mean-p['baseline_best_mean']):+.6f} percentage points vs RP1.05).")
  lines+=["","|Dataset|Metric|Base -> epoch|Previous RP1.05 (%)|New RP1.0 (%)|Delta (pp)|","|---|---|---|---:|---:|---:|"]
  for x in rows:lines.append(f"|{x['dataset']}|{x['main_metric']}|{x['base_epoch']} -> {x['epoch']}|{100*x['previous_score']:.2f}|{100*x['current_score']:.2f}|{x['delta_vs_previous_pp']:+.4f}|")
  if not complete:lines+=["","Nine-dataset mean is withheld until all nine pairs finish."]
  atomic_text(run/"RESULTS.md","\n".join(lines)+"\n")
 return len(scores)

def claim(run,p,node):
 spec={j["id"]:j for j in p["jobs"]}
 ordered=sorted((run/"jobs").glob("*.json"),key=lambda f:(read(f)["priority"],read(f)["base_epoch"],read(f)["epoch"],-spec[f.stem]["samples"],f.stem))
 for f in ordered:
  if spec[f.stem]["preferred_node"]!=node:continue
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
  llm,tokenizer,native=evaluation.func_read_batch_calling_model("Qwen25")
  old=SamplingParams(temperature=p["baseline_judge"]["temperature"],top_p=p["baseline_judge"]["top_p"],repetition_penalty=p["baseline_judge"]["repetition_penalty"],max_tokens=p["baseline_judge"]["max_tokens"])
  params=SamplingParams(temperature=p["judge"]["temperature"],top_p=p["judge"]["top_p"],repetition_penalty=p["judge"]["repetition_penalty"],max_tokens=p["judge"]["max_tokens"])
  fields=getattr(old,"__struct_fields__",None) or tuple(vars(old))
  changed={k:dict(old=repr(getattr(old,k)),new=repr(getattr(params,k))) for k in fields if getattr(old,k)!=getattr(params,k)}
  require(set(changed)=={"repetition_penalty"},"Unexpected judge parameter changed")
  require(native.temperature==.7 and native.top_p==.8 and old.temperature==0 and old.top_p==1 and old.repetition_penalty==1.05 and params.repetition_penalty==1.0 and params.max_tokens==512,"Judge baseline configuration mismatch")
  write(run/f"judge_runtime_{node}.json",dict(passed=True,node=node,pid=os.getpid(),changed=changed,old_parameters=repr(old),new_parameters=repr(params),sampling_type=str(params.sampling_type),all_other_sampling_fields_equal=True,model_loader="Unchanged evaluation.func_read_batch_calling_model Qwen25",at=now()))
  refs={};judge=(llm,tokenizer,params);update(state="ready")
  while True:
   selected=claim(run,p,node)
   if selected is None:
    states=collections.Counter(read(f)["state"] for f in (run/"jobs").glob("*.json"))
    if states.get("complete",0)==p["expected_jobs"]:break
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
  require(summarize(run,p)==p["expected_jobs"],"Incomplete final scoring");update(state="complete",completed_total=p["expected_jobs"],results=str(run/"RESULTS.md"))
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
    child=subprocess.Popen([PYTHON,"-u","-B","-m","amg_v21_rejudge_rp1_20261107.execute","worker","--run",str(run),"--node",node],cwd=G,env=env(),stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
   update(state="running",attempt=attempt,judge_pid=child.pid)
   rc=child.wait()
   try:os.killpg(child.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   child=None;release()
   if rc==0:
    require(len(list((run/"scores").glob("*.json")))==p["expected_jobs"],"Worker exited before all scores were committed")
    update(state="complete",scored_jobs=p["expected_jobs"],results=str(run/"RESULTS.md"));return
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

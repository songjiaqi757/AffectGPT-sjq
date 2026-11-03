"""Server-only resumable dual-GPU source polarity pseudo annotation."""
import argparse,collections,csv,io,json,os,signal,subprocess,sys,time,traceback
from pathlib import Path
from amg_inference.common import ROOT,PYTHON,read,sha,canonical,atomic_json,require,locked,now
LABELS={"negative":0,"neutral":1,"positive":2}
SIGNS={"negative":-1,"neutral":0,"positive":1}
def normalize(raw):
 s=raw.strip().lower()
 if s in LABELS:return s
 s=s.strip(" \t\r\n\"'"+chr(96)).rstrip(".。").strip()
 return s if s in LABELS else None
def plan(run):
 p=read(run/"plan.json");require(p["plan_id"]==canonical({k:v for k,v in p.items() if k!="plan_id"}),"Plan changed")
 for path,digest in p["files_sha256"].items():require(sha(path)==digest,"Input/code changed: "+path)
 for path,st in p["model_assets"].items():
  cur=Path(path).stat();require(cur.st_size==st["bytes"] and cur.st_mtime_ns==st["mtime_ns"],"Judge asset changed")
 return p
def counts(run):return dict(collections.Counter(read(f)["state"] for f in (run/"jobs").glob("*.json")))
def result_ok(run,item,p):
 f=run/"unique_results"/(item["query_id"]+".json")
 if not f.exists():return False
 x=read(f);require(x["plan_id"]==p["plan_id"] and x["query_id"]==item["query_id"] and x["source_ovlabel"]==item["ovlabel"] and (x["polarity"] in LABELS or (x["polarity"]=="abstain" and x["polarity_id"]==-100)),"Corrupt label");return True
def claim(run,p):
 for f in sorted((run/"jobs").glob("*.json")):
  handle=locked(f.with_suffix(".lock"))
  if handle is None:continue
  j=read(f)
  if j["state"] in ["complete","failed"]:handle.close();continue
  if all(result_ok(run,x,p) for x in j["items"]):
   j.update(state="complete",recovered=True);atomic_json(f,j);handle.close();continue
  if j.get("attempts",0)>=3:
   j.update(state="failed",error="Three batch attempts exhausted");atomic_json(f,j);handle.close();continue
  j.update(state="running",attempts=j.get("attempts",0)+1,pid=os.getpid(),gpu=os.environ.get("CUDA_VISIBLE_DEVICES"),started_at_beijing=now());atomic_json(f,j);return f,handle,j
 return None
def worker(run,gpu):
 p=plan(run);owner=locked(ROOT/"amg_finetune_nogc"/f"gpu_{gpu}.lock");require(owner is not None,"GPU already owned")
 own=locked(run/f"gpu_{gpu}.lock");require(own is not None,"Worker already active")
 s=dict(state="loading_model",gpu=gpu,pid=os.getpid(),started_at_beijing=now(),completed_unique_this_worker=0)
 def update(**kw):s.update(kw,updated_at_beijing=now());atomic_json(run/f"gpu_{gpu}_status.json",s)
 try:
  update();os.chdir(ROOT/"AffectGPT");sys.path.insert(0,str(ROOT/"AffectGPT"));import evaluation
  llm,tokenizer,params=evaluation.func_read_batch_calling_model("Qwen25")
  update(state="ready",sampling=dict(temperature=params.temperature,top_p=params.top_p,repetition_penalty=params.repetition_penalty,max_tokens=params.max_tokens))
  deadline=time.monotonic()+1200
  while not (run/"both_gpus_ready.json").exists():require(time.monotonic()<deadline,"Ready barrier timed out");time.sleep(1)
  while True:
   job=claim(run,p)
   if job is None:
    c=counts(run)
    if c.get("complete",0)+c.get("failed",0)==p["batches"]:require(not c.get("failed",0),"Jobs failed");break
    update(state="waiting_for_peer",jobs=c);time.sleep(2);continue
   f,handle,j=job
   try:
    todo=[x for x in j["items"] if not result_ok(run,x,p)];update(state="annotating",job_id=j["job_id"],batch_unique=len(todo))
    last_invalid={}
    for retry in range(3):
     if not todo:break
     seed=42+int(j["job_id"].split("_")[-1])*10+(j["attempts"]-1)*3+retry
     call_params=params.clone();call_params.seed=seed
     responses=evaluation.openset_to_sentiment_qwen(llm=llm,tokenizer=tokenizer,sampling_params=call_params,batch_reasons=[x["ovlabel"] for x in todo])
     require(len(responses)==len(todo),"Response count mismatch");pending=[]
     for item,raw in zip(todo,responses):
      label=normalize(raw)
      if label is None:
       with (run/f"gpu_{gpu}_invalid_outputs.jsonl").open("a") as stream:stream.write(json.dumps(dict(query_id=item["query_id"],raw_response=raw,seed=seed,time_beijing=now()),ensure_ascii=False)+"\n")
       last_invalid[item["query_id"]]=dict(raw_response=raw,seed=seed);pending.append(item);continue
      x=dict(plan_id=p["plan_id"],query_id=item["query_id"],source_ovlabel=item["ovlabel"],polarity=label,polarity_id=LABELS[label],polarity_sign=SIGNS[label],raw_response=raw,teacher="Qwen2.5-7B-Instruct",gpu=gpu,seed=seed,pseudo_label=True,human_verified=False,completed_at_beijing=now())
      atomic_json(run/"unique_results"/(item["query_id"]+".json"),x);s["completed_unique_this_worker"]+=1
     todo=pending
    for item in todo:
     last=last_invalid[item["query_id"]]
     x=dict(plan_id=p["plan_id"],query_id=item["query_id"],source_ovlabel=item["ovlabel"],polarity="abstain",polarity_id=-100,polarity_sign=None,raw_response=last["raw_response"],teacher="Qwen2.5-7B-Instruct",gpu=gpu,seed=last["seed"],pseudo_label=True,human_verified=False,valid_for_polarity_loss=False,abstention_reason="No valid three-class output after three attempts",completed_at_beijing=now())
     atomic_json(run/"unique_results"/(item["query_id"]+".json"),x);s["completed_unique_this_worker"]+=1
    j.update(state="complete",finished_at_beijing=now());update(jobs=counts(run))
   except BaseException as exc:j.update(state="pending" if j["attempts"]<3 else "failed",error=repr(exc),traceback=traceback.format_exc());raise
   finally:atomic_json(f,j);handle.close()
  update(state="complete",finished_at_beijing=now())
 except BaseException as exc:update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:own.close();owner.close()
def aggregate(run,p):
 source=read(p["source_records"]);members=read(run/"source_members.json");require(len(source)==len(members)==p["training_samples"],"Membership drift")
 labels=[];used=set()
 for original,row in zip(source,members):
  require(row["sample_id"]==original["sample_id"] and row["ovlabel"]==original["ovlabel"],"Source changed")
  require(result_ok(run,dict(query_id=row["query_id"],ovlabel=row["ovlabel"]),p),"Missing label")
  x=read(run/"unique_results"/(row["query_id"]+".json"));used.add(row["query_id"])
  labels.append(dict(sample_id=row["sample_id"],group_id=row["group_id"],source_ovlabel=row["ovlabel"],polarity=x["polarity"],polarity_id=x["polarity_id"],polarity_sign=x["polarity_sign"],valid_for_polarity_loss=x["polarity"] in LABELS,query_id=row["query_id"],pseudo_label=True,human_verified=False,raw_response=x["raw_response"],teacher=x["teacher"],plan_id=p["plan_id"]))
 require(len({x["sample_id"] for x in labels})==p["training_samples"] and len(used)==p["unique_queries"],"Coverage mismatch")
 atomic_json(run/"polarity_labels.json",labels)
 out=io.StringIO();w=csv.DictWriter(out,fieldnames=["sample_id","group_id","polarity","polarity_id","polarity_sign","valid_for_polarity_loss","source_ovlabel","query_id","pseudo_label","human_verified"]);w.writeheader()
 for x in labels:w.writerow({k:x[k] for k in w.fieldnames})
 tmp=run/"polarity_labels.csv.tmp";tmp.write_text(out.getvalue());tmp.replace(run/"polarity_labels.csv")
 tmp=run/"polarity_labels.jsonl.tmp"
 with tmp.open("w") as f:
  for x in labels:f.write(json.dumps(x,ensure_ascii=False)+"\n")
 tmp.replace(run/"polarity_labels.jsonl")
 report=dict(passed=True,plan_id=p["plan_id"],samples=len(labels),unique_queries=len(used),sample_class_counts=dict(collections.Counter(x["polarity"] for x in labels)),unique_class_counts=dict(collections.Counter(read(f)["polarity"] for f in (run/"unique_results").glob("*.json"))),id_mapping=LABELS,sign_mapping=SIGNS,source_only=True,audit_500_excluded=True,valid_labels_have_allowed_classes=True,valid_for_polarity_loss=sum(x["valid_for_polarity_loss"] for x in labels),abstained_samples=sum(not x["valid_for_polarity_loss"] for x in labels),human_verified=False,training_started=False,files_sha256={n:sha(run/n) for n in ["polarity_labels.json","polarity_labels.jsonl","polarity_labels.csv"]},finished_at_beijing=now())
 atomic_json(run/"summary.json",report);atomic_json(run/"needs_review.json",[x for x in labels if not x["valid_for_polarity_loss"]]);return report
def controller(run):
 p=plan(run);owner=locked(run/"controller.lock");require(owner is not None,"Controller already active")
 children=[];s=dict(state="starting_dual_gpu",pid=os.getpid(),started_at_beijing=now(),plan_id=p["plan_id"])
 def update(**kw):s.update(kw,updated_at_beijing=now());atomic_json(run/"status.json",s)
 def launch(gpu):
  log=(run/f"gpu_{gpu}.log").open("ab",buffering=0)
  env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu),PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="4",VLLM_WORKER_MULTIPROC_METHOD="spawn")
  for key in ["RANK","WORLD_SIZE","LOCAL_RANK"]:env.pop(key,None)
  child=subprocess.Popen([str(PYTHON),"-u","-m","amg_polarity.pipeline","--run",str(run),"--gpu",str(gpu)],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();return child
 try:
  update();children=[launch(gpu) for gpu in [0,1]];update(worker_pids=[x.pid for x in children],state="loading_dual_gpu_models");deadline=time.monotonic()+1200
  while True:
   require(all(x.poll() is None for x in children),"Worker failed during loading");fs=[run/f"gpu_{gpu}_status.json" for gpu in [0,1]]
   if all(f.exists() and read(f)["state"]=="ready" for f in fs):break
   require(time.monotonic()<deadline,"Loading timed out");time.sleep(2)
  atomic_json(run/"both_gpus_ready.json",dict(passed=True,worker_pids=[x.pid for x in children],time_beijing=now()));update(state="annotating")
  while any(x.poll() is None for x in children):
   require(all(x.poll() in [None,0] for x in children),"Worker failed; labels retained");update(jobs=counts(run),unique_completed=sum(1 for f in (run/"unique_results").glob("*.json")));time.sleep(5)
  require(all(x.returncode==0 for x in children),"Worker exit failure");require(counts(run)=={"complete":p["batches"]},"Incomplete batches")
  report=aggregate(run,p);update(state="complete",summary=report,finished_at_beijing=now())
 except BaseException as exc:
  for child in children:
   if child.poll() is None:
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:owner.close()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);ap.add_argument("--gpu",type=int);a=ap.parse_args();run=Path(a.run).resolve()
 if a.gpu is None:controller(run)
 else:worker(run,a.gpu)
if __name__=="__main__":main()

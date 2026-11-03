"""One persistent evaluator per GPU with exclusive shared scoring jobs."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,csv,io,json,math,os,sys,time,zipfile
from graph_paths import Path
from .common import ROOT,verify,locked,now,sha,canonical,read,atomic_json,require,DATASETS
from .priority_score import phase_plan,resources,corpus,prepare_raw,truth as priority_truth
DISCRETE={"MER2023","MER2024","MELD","IEMOCAPFour"}
DIMENSION={"CMUMOSI","CMUMOSEI","SIMS","SIMSv2"}
def all_inference_complete(run,ph):
 if len(ph["job_ids"])!=225:return False
 for jid in ph["job_ids"]:
  f=Path(run)/"jobs"/(jid+".json")
  if not f.exists() or read(f).get("state")!="complete":return False
 return True
def truth(dataset,ip,evaluation):
 if dataset in ["MER2023","SIMS","OVMERDPlus"]:return priority_truth(dataset,ip,evaluation)
 import config
 path=(ROOT/"AffectGPT"/config.PATH_TO_LABEL[dataset]).resolve()
 names=[r["name"] for r in read(ip["datasets"][dataset]["path"])]
 member="test1_corpus" if dataset=="MER2024" else "whole_corpus" if dataset=="IEMOCAPFour" else "test_corpus"
 source=corpus(path,member)
 if dataset in DIMENSION:
  answer={n:float(source[n]["val"]) for n in names}
  require(all(math.isfinite(v) for v in answer.values()),"Non-finite test label")
 elif dataset=="MER2024":
  answer={n:source[n]["emo"] for n in names};require(all(isinstance(v,str) for v in answer.values()),"Unexpected MER2024 label type")
 else:
  cls=evaluation.MELD_Dataset if dataset=="MELD" else evaluation.IEMOCAPFour_Dataset
  instance=cls.__new__(cls);_,idx2emo=evaluation.get_emo2idx_idx2emo(instance)
  answer={n:source[n]["emo"] if isinstance(source[n]["emo"],str) else idx2emo[int(source[n]["emo"])] for n in names}
 require(set(answer)==set(names) and len(answer)==ip["datasets"][dataset]["samples"],"Test membership mismatch: "+dataset)
 return answer
def score_counts(phase):
 result={}
 for f in (Path(phase)/"evaluation_jobs").glob("*.json"):
  state=read(f)["state"];result[state]=result.get(state,0)+1
 return result
def claim_score(phase):
 files=list((Path(phase)/"evaluation_jobs").glob("*.json"))
 files.sort(key=lambda f:(-read(f)["estimated_seconds"],f.name))
 for f in files:
  handle=locked(f.with_suffix(".lock"))
  if handle is None:continue
  j=read(f)
  if j["state"] in ["complete","failed"]:handle.close();continue
  cached=Path(phase)/"scores"/(j["job_id"]+".json")
  if cached.exists():
   result=read(cached);require(result["job_id"]==j["job_id"] and all(math.isfinite(v) for v in result["metrics"].values()),"Invalid committed score")
   j.update(state="complete",score_path=str(cached),recovered_committed_score=True);atomic_json(f,j);handle.close();continue
  if j.get("attempts",0)>=3:
   j.update(state="failed",error="Three scoring attempts exhausted");atomic_json(f,j);handle.close();continue
  j.update(state="running",attempts=j.get("attempts",0)+1,pid=os.getpid(),gpu=os.environ.get("CUDA_VISIBLE_DEVICES"),updated_at_beijing=now());atomic_json(f,j)
  return f,handle,j
 return None
def validate_reused(phase,ph):
 for jid,binding in read(Path(phase)/"reuse_manifest.json")["scores"].items():
  require(jid in ph["job_ids"],"Unexpected reused result")
  require(_graph_hash_matches(binding['score_path'], binding['score_sha256'], sha(binding['score_path'])),"Prior score changed")
  require(_graph_hash_matches(binding['raw_path'], binding['raw_sha256'], sha(binding['raw_path'])),"Prior scored predictions changed")
  score=read(binding["score_path"])
  require(score["inference_plan_id"]==ph["inference_plan_id"] and score["job_id"]==jid,"Prior score belongs to another inference")
def summarize(phase,ph):
 rows=[]
 for jid in ph["job_ids"]:
  f=Path(phase)/"scores"/(jid+".json")
  if f.exists():rows.append(read(f))
 columns=["base_epoch","epoch","dataset","samples","main_metric","main_score","HIT","WAF","ACC","F_s","P_s","R_s","completed_at_beijing"]
 buffer=io.StringIO();writer=csv.DictWriter(buffer,fieldnames=columns);writer.writeheader()
 for row in sorted(rows,key=lambda x:(x["base_epoch"],x["epoch"],x["dataset"])):
  fields={k:row.get(k,"") for k in columns};fields.update(row["metrics"]);writer.writerow(fields)
 path=Path(phase)/"metrics_all.csv";temp=path.with_suffix(".csv.tmp");temp.write_text(buffer.getvalue());temp.replace(path)
 per_checkpoint=[]
 for spec in ph["checkpoints"]:
  subset=[r for r in rows if (r["base_epoch"],r["epoch"])==(spec["base_epoch"],spec["epoch"])]
  record=dict(base_epoch=spec["base_epoch"],epoch=spec["epoch"],datasets_completed=len(subset),dataset_wise_mean=sum(x["main_score"] for x in subset)/9 if len(subset)==9 else None,checkpoint_sha256=spec["sha256"])
  for row in subset:
   for key,value in row["metrics"].items():record[row["dataset"]+"_"+key]=value
  per_checkpoint.append(record)
 atomic_json(Path(phase)/"per_checkpoint_summary.json",per_checkpoint)
 fields=["base_epoch","epoch","datasets_completed","dataset_wise_mean"]
 for d in ph["datasets"]:
  fields += [d+"_"+metric for metric in (["HIT"] if d in DISCRETE else ["WAF","ACC"] if d in DIMENSION else ["F_s","P_s","R_s"])]
 buffer=io.StringIO();writer=csv.DictWriter(buffer,fieldnames=fields,extrasaction="ignore");writer.writeheader();writer.writerows(per_checkpoint)
 path=Path(phase)/"per_checkpoint_summary.csv";temp=path.with_suffix(".csv.tmp");temp.write_text(buffer.getvalue());temp.replace(path)
 if len(rows)==225:
  best=[]
  for d in ph["datasets"]:
   candidates=[x for x in rows if x["dataset"]==d];winner=max(candidates,key=lambda x:x["main_score"]);best.append(winner)
  atomic_json(Path(phase)/"best_original_reporting.json",best)
 return rows
def main():
 a=argparse.ArgumentParser();a.add_argument("--phase",required=True);a.add_argument("--gpu",required=True,type=int);args=a.parse_args()
 phase=Path(args.phase).resolve();ph=phase_plan(phase);run=Path(ph["inference_run"]);ip=verify(run);lock=resources(phase);validate_reused(phase,ph)
 require(all_inference_complete(run,ph),"All 225 inference jobs must finish before evaluation")
 owner=locked(phase/f"gpu_{args.gpu}_evaluator.lock");require(owner is not None,"An evaluator already owns this GPU slot")
 s=dict(state="loading",pid=os.getpid(),gpu=args.gpu,evaluation_processes_on_gpu=1,judge_instances=1,completed_this_worker=0,started_at_beijing=now())
 def update(**kw):s.update(kw,updated_at_beijing=now());atomic_json(phase/f"gpu_{args.gpu}_evaluation_status.json",s)
 try:
  update();os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"));import evaluation
  datasets={};judge=None
  while True:
   claim=claim_score(phase)
   if claim is None:
    counts=score_counts(phase);update(state="waiting_for_other_evaluator",counts=counts)
    if counts.get("complete",0)+counts.get("failed",0)==225:
     require(counts.get("failed",0)==0,"Some scoring jobs failed");break
    time.sleep(10);continue
   f,handle,j=claim
   try:
    inference=read(run/"jobs"/(j["job_id"]+".json"));d=inference["dataset"]
    update(state="loading_judge" if judge is None else "scoring",job_id=j["job_id"])
    if judge is None:judge=evaluation.func_read_batch_calling_model("Qwen25")
    if d not in datasets:datasets[d]=truth(d,ip,evaluation)
    raw=prepare_raw(phase,ip,ph,inference)
    # Repository caches are generated by us; remove only truncated caches on recovery.
    for suffix in ["-openset.npz","-openset-sentiment.npz"]:
     cache=raw.with_name(raw.stem+suffix)
     if cache.exists():
      try:
       with zipfile.ZipFile(cache) as z:valid=z.testzip() is None
      except (OSError,zipfile.BadZipFile):valid=False
      if not valid:cache.unlink()
    llm,tokenizer,params=judge;gt=datasets[d];update(state="scoring")
    if d in DISCRETE:
     primary,_=evaluation.calculate_discrete_zeroshot(str(raw),gt,llm,tokenizer,params,True);metrics={"HIT":float(primary)};metric="HIT"
    elif d in DIMENSION:
     primary,accuracy=evaluation.calculate_dimension_zeroshot(str(raw),gt,llm,tokenizer,params,True);metrics={"WAF":float(primary),"ACC":float(accuracy)};metric="WAF"
    else:
     primary,precision,recall=evaluation.calculate_ov_zeroshot(str(raw),gt,llm,tokenizer,params,True);metrics={"F_s":float(primary),"P_s":float(precision),"R_s":float(recall)};metric="F_s"
    require(all(math.isfinite(v) for v in metrics.values()),"Non-finite metric")
    result=dict(job_id=j["job_id"],base_epoch=inference["base_epoch"],epoch=inference["epoch"],dataset=d,samples=len(gt),main_metric=metric,main_score=float(primary),metrics=metrics,checkpoint=inference["checkpoint"],raw_path=str(raw),raw_sha256=sha(raw),phase_id=ph["phase_id"],inference_plan_id=ip["plan_id"],evaluation_lock_id=lock["lock_id"],evaluation_gpu=args.gpu,completed_at_beijing=now(),protocol=ph["evaluation_protocol"])
    atomic_json(phase/"scores"/(j["job_id"]+".json"),result)
    j.update(state="complete",score_path=str(phase/"scores"/(j["job_id"]+".json")),finished_at_beijing=now());s["completed_this_worker"]+=1;update()
   except BaseException as exc:
    import traceback
    j.update(state="pending" if j["attempts"]<3 else "failed",error=repr(exc),traceback=traceback.format_exc(),updated_at_beijing=now());raise
   finally:atomic_json(f,j);handle.close()
  update(state="complete",finished_at_beijing=now())
 except BaseException as exc:
  import traceback
  update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:owner.close()
if __name__=="__main__":main()

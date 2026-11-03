"""One evaluator, one local Qwen judge, all sixty fixed results scored sequentially."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,csv,io,json,math,os,sys,zipfile
from graph_paths import Path
import numpy as np
from .common import ROOT,verify,locked,now,canonical,sha,read,atomic_json,require
from .prepare import NumpyOnly
def phase_plan(phase):
 p=read(Path(phase)/"plan.json")
 require(p["phase_id"]==canonical({k:v for k,v in p.items() if k!="phase_id"}),"Priority phase identity changed")
 return p
def resources(phase):
 lock=read(Path(phase)/"evaluation_lock.json")
 require(lock["lock_id"]==canonical({k:v for k,v in lock.items() if k!="lock_id"}),"Evaluation lock changed")
 for filename,digest in lock["files_sha256"].items():require(_graph_hash_matches(filename, digest, sha(filename)),"Evaluation resource changed: "+filename)
 return lock
def corpus(path,member):
 with zipfile.ZipFile(path) as z:
  with z.open(member+".npy") as f:
   version=np.lib.format.read_magic(f);shape,_,dtype=np.lib.format._read_array_header(f,version)
   require(shape==() and dtype.hasobject,"Unexpected label corpus format")
   value=NumpyOnly(f).load().item();require(isinstance(value,dict),"Label corpus must be a dictionary");return value
def truth(d,ip,evaluation):
 import config
 path=(ROOT/"AffectGPT"/config.PATH_TO_LABEL[d]).resolve()
 names=[r["name"] for r in read(ip["datasets"][d]["path"])]
 if d=="MER2023":
  source=corpus(path,"test1_corpus");answer={n:source[n]["emo"] for n in names}
  require(all(isinstance(v,str) for v in answer.values()),"Unexpected MER2023 categorical labels")
 elif d=="SIMS":
  source=corpus(path,"test_corpus");answer={n:float(source[n]["val"]) for n in names}
  require(all(math.isfinite(v) for v in answer.values()),"Non-finite SIMS label")
 elif d=="OVMERDPlus":
  with path.open(newline="") as f:source={r["name"]:r["openset"] for r in csv.DictReader(f)}
  answer={}
  for n in names:
   labels=evaluation.string_to_list(source[n])
   answer[n]=", ".join(labels or ["neutral"])
 else:raise ValueError("Unsupported priority dataset")
 require(set(answer)==set(names) and len(answer)==ip["datasets"][d]["samples"],"Ground truth coverage mismatch")
 return answer
def inference_ready(run,ph):
 selected=[read(Path(run)/"jobs"/(jid+".json")) for jid in ph["job_ids"]]
 return len(selected)==60 and all(j["state"]=="complete" for j in selected)
def prepare_raw(phase,ip,ph,j):
 require(j["state"]=="complete","Inference not complete")
 spec=next(s for s in ph["checkpoints"] if s["base_epoch"]==j["base_epoch"] and s["epoch"]==j["epoch"])
 require(j["checkpoint"]["sha256"]==spec["sha256"],"Scoring wrong checkpoint")
 names=[r["name"] for r in read(ip["datasets"][j["dataset"]]["path"])]
 expected=canonical(dict(plan_id=ip["plan_id"],checkpoint=spec["sha256"],input_sha=ip["datasets"][j["dataset"]]["sha256"]))
 values={}
 with Path(j["prediction_path"]).open() as stream:
  for line in stream:
   row=json.loads(line);require(row["binding"]==expected and row["dataset"]==j["dataset"],"Prediction provenance mismatch")
   require(row["name"] not in values and isinstance(row["response"],str),"Invalid or duplicate prediction");values[row["name"]]=row["response"]
 require(set(values)==set(names) and len(values)==j["samples"],"Incomplete prediction coverage")
 output=Path(phase)/"score_inputs"/j["job_id"]/"name2reason.npz";output.parent.mkdir(parents=True,exist_ok=True)
 if not output.exists():
  temp=output.with_suffix(".npz.tmp")
  with temp.open("wb") as f:np.savez_compressed(_graph_resolve_path(f), name2reason={n: values[n] for n in names})
  temp.replace(output)
 return output
def summarize(phase,ph):
 rows=[]
 for jid in ph["job_ids"]:
  f=Path(phase)/"scores"/(jid+".json")
  if f.exists():rows.append(read(f))
 columns=["base_epoch","epoch","dataset","samples","main_metric","main_score","HIT","WAF","ACC","F_s","P_s","R_s","completed_at_beijing"]
 out=io.StringIO();writer=csv.DictWriter(out,fieldnames=columns);writer.writeheader()
 for row in rows:
  flat={k:row.get(k,"") for k in columns};flat.update(row["metrics"]);writer.writerow(flat)
 target=Path(phase)/"metrics_all.csv";temp=target.with_suffix(".csv.tmp");temp.write_text(out.getvalue());temp.replace(target)
 summaries=[]
 for spec in ph["checkpoints"]:
  subset=[r for r in rows if r["base_epoch"]==spec["base_epoch"] and r["epoch"]==spec["epoch"]]
  record=dict(base_epoch=spec["base_epoch"],epoch=spec["epoch"],datasets_completed=len(subset),checkpoint_sha256=spec["sha256"])
  for row in subset:
   for key,value in row["metrics"].items():record[row["dataset"]+"_"+key]=value
  summaries.append(record)
 atomic_json(Path(phase)/"per_checkpoint_summary.json",summaries)
 matrix=io.StringIO();fields=["base_epoch","epoch","datasets_completed","MER2023_HIT","SIMS_WAF","SIMS_ACC","OVMERDPlus_F_s","OVMERDPlus_P_s","OVMERDPlus_R_s"]
 writer=csv.DictWriter(matrix,fieldnames=fields,extrasaction="ignore");writer.writeheader();writer.writerows(summaries)
 target=Path(phase)/"per_checkpoint_summary.csv";temp=target.with_suffix(".csv.tmp");temp.write_text(matrix.getvalue());temp.replace(target)
 return rows
def main():
 a=argparse.ArgumentParser();a.add_argument("--phase",required=True);args=a.parse_args();phase=Path(args.phase).resolve();ph=phase_plan(phase);run=Path(ph["inference_run"]);ip=verify(run);lock=resources(phase)
 owner=locked(phase/"single_evaluator.lock");require(owner is not None,"A scoring process already exists")
 status=dict(state="loading",pid=os.getpid(),physical_gpu=os.environ.get("CUDA_VISIBLE_DEVICES"),evaluation_processes=1,judge_instances=1,total=60,completed=0,phase_id=ph["phase_id"],started_at_beijing=now())
 def update(**kw):status.update(kw,updated_at_beijing=now());atomic_json(phase/"scoring_status.json",status)
 try:
  require(inference_ready(run,ph),"All sixty inference jobs must finish before any scoring")
  update();os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"))
  import evaluation
  datasets={d:truth(d,ip,evaluation) for d in ph["datasets"]}
  judge=None;done=0
  for jid in ph["job_ids"]:
   dest=phase/"scores"/(jid+".json")
   if dest.exists():
    result=read(dest);require(result["phase_id"]==ph["phase_id"] and result["evaluation_lock_id"]==lock["lock_id"],"Stale score");done+=1;continue
   if judge is None:
    # Exact repository loader, model, sampling parameters and vLLM defaults.
    judge=evaluation.func_read_batch_calling_model("Qwen25")
   llm,tokenizer,params=judge;j=read(run/"jobs"/(jid+".json"));raw=prepare_raw(phase,ip,ph,j);gt=datasets[j["dataset"]]
   update(state="scoring",job_id=jid,completed=done)
   if j["dataset"]=="MER2023":
    main_score,_=evaluation.calculate_discrete_zeroshot(str(raw),gt,llm,tokenizer,params,True);metrics={"HIT":float(main_score)};metric="HIT"
   elif j["dataset"]=="SIMS":
    main_score,accuracy=evaluation.calculate_dimension_zeroshot(str(raw),gt,llm,tokenizer,params,True);metrics={"WAF":float(main_score),"ACC":float(accuracy)};metric="WAF"
   else:
    main_score,precision,recall=evaluation.calculate_ov_zeroshot(str(raw),gt,llm,tokenizer,params,True);metrics={"F_s":float(main_score),"P_s":float(precision),"R_s":float(recall)};metric="F_s"
   require(all(math.isfinite(v) for v in metrics.values()),"Non-finite score")
   result=dict(job_id=jid,base_epoch=j["base_epoch"],epoch=j["epoch"],dataset=j["dataset"],samples=len(gt),main_metric=metric,main_score=float(main_score),metrics=metrics,checkpoint=j["checkpoint"],raw_path=str(raw),raw_sha256=sha(raw),phase_id=ph["phase_id"],inference_plan_id=ip["plan_id"],evaluation_lock_id=lock["lock_id"],completed_at_beijing=now(),protocol=ph["evaluation_protocol"])
   atomic_json(dest,result);done+=1;summarize(phase,ph);update(completed=done)
  require(len(summarize(phase,ph))==60,"Incomplete scoring summary");update(state="complete",completed=60,finished_at_beijing=now())
 except BaseException as exc:
  import traceback
  update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:owner.close()
if __name__=="__main__":main()

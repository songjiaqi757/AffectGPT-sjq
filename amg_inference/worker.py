"""Persistent single-GPU inference worker with exclusive resumable dataset jobs."""
import argparse,os,time,traceback,json
from pathlib import Path
from amg_runtime.common import read,canonical,atomic_json,require
from .common import verify,now,checkpoint,acquire_job,counts,evidence,key
def seed_for(p,spec,sid):
 return (p["seed"]+int(canonical([spec["sha256"],sid])[:8],16))%2**32
def main():
 a=argparse.ArgumentParser();a.add_argument("--run",required=True);a.add_argument("--slot",required=True,type=int);a.add_argument("--smoke",action="store_true");args=a.parse_args()
 run=Path(args.run);p=verify(run);gpu=os.environ["CUDA_VISIBLE_DEVICES"]
 report=run/f"gpu_{gpu}_{'probe' if args.smoke else 'worker'}_{args.slot}_status.json"
 s=dict(state="loading",pid=os.getpid(),gpu=gpu,slot=args.slot,started_at_beijing=now())
 def update(**kw):s.update(kw,updated_at_beijing=now());atomic_json(report,s)
 try:
  if args.smoke:
   from .model import Predictor
   model=Predictor(p);tp=read(Path(p["training_run"])/"plan.json");spec=tp["checkpoints"][0]
   model.load(dict(spec,epoch=spec["base_epoch"]))
   update(state="ready")
   deadline=time.monotonic()+1200
   while not (run/f"gpu_{gpu}_probe_go.json").exists():
    require(time.monotonic()<deadline,"Three-model capacity barrier timeout");time.sleep(2)
   source=read(run/"source_probe.json");cache=read(source["cache_path"])
   output,info=model.predict(source["record"],cache["evidence"],42+args.slot,stress=True)
   import torch
   update(state="validating_probe",prompt_info=info,peak_bytes=torch.cuda.max_memory_allocated(),reserved_bytes=torch.cuda.max_memory_reserved())
   require(1530<=info["stress_prompt_tokens"]<=1536 and info["stress_generated_tokens"]==1200,"Source capacity probe did not fill the full input/output window")
   update(state="complete",passed=True,peak_bytes=torch.cuda.max_memory_allocated(),reserved_bytes=torch.cuda.max_memory_reserved(),prompt_info=info)
   return
  require(read(run/f"gpu_{gpu}_capacity.json")["passed"],"Three concurrent source probes have not passed")
  model=None
  while True:
   claimed=acquire_job(run,p)
   if claimed is None:
    summary=counts(run);update(state="waiting_for_checkpoint",jobs=summary)
    if summary.get("complete",0)+summary.get("failed",0)==p["logical_jobs"]:break
    # A failed training queue cannot publish its remaining checkpoint dependencies.
    failures=[read(Path(p["training_run"])/f"gpu_{g}_queue_status.json")["state"]=="failed" for g in [0,1]]
    require(not any(failures),"Training failed; uncreated checkpoint jobs remain blocked")
    time.sleep(30);continue
   f,handle,j=claimed
   try:
    update(state="running",job_id=j["job_id"],completed_samples=0)
    spec=checkpoint(p,j)
    if model is None:
     from .model import Predictor
     model=Predictor(p)
    model.load(spec,j)
    rows=read(p["datasets"][j["dataset"]]["path"])
    out=run/"predictions"/j["job_id"];out.mkdir(parents=True,exist_ok=True)
    binding=canonical(dict(plan_id=p["plan_id"],checkpoint=spec["sha256"],input_sha=p["datasets"][j["dataset"]]["sha256"]))
    for i,row in enumerate(rows):
     dest=out/(key(row["sample_id"])+".json");cache=evidence(run,row,p)
     if dest.exists():
      previous=read(dest)
      require(previous["binding"]==binding and previous["sample_id"]==row["sample_id"] and previous["cache_id"]==cache["cache_id"],"Stale prediction found")
     else:
      seed=seed_for(p,spec,row["sample_id"]);response,info=model.predict(row,cache["evidence"],seed)
      atomic_json(dest,dict(sample_id=row["sample_id"],name=row["name"],dataset=j["dataset"],response=response,binding=binding,checkpoint=spec,plan_id=p["plan_id"],cache_id=cache["cache_id"],query_config_id=p["query_config_id"],seed=seed,prompt_info=info,created_at_beijing=now()))
     if i%10==0 or i+1==len(rows):update(completed_samples=i+1,total_samples=len(rows))
    # Official name2reason format plus safe JSONL; label evaluation is a separate operation.
    name2reason={}
    temp=out/"predictions.jsonl.tmp"
    with temp.open("w") as stream:
     for row in rows:
      value=read(out/(key(row["sample_id"])+".json"));stream.write(json.dumps(value,ensure_ascii=False)+"\n");name2reason[row["name"]]=value["response"]
    temp.replace(out/"predictions.jsonl")
    import numpy as np
    with (out/"name2reason.npz.tmp").open("wb") as stream:np.savez_compressed(stream,name2reason=name2reason)
    (out/"name2reason.npz.tmp").replace(out/"name2reason.npz")
    j.update(state="complete",samples=len(rows),checkpoint=spec,finished_at_beijing=now(),prediction_path=str(out/"predictions.jsonl"),official_npz=str(out/"name2reason.npz"))
   except BaseException as exc:
    j.update(state="pending" if j["attempts"]<3 else "failed",error=repr(exc),traceback=traceback.format_exc(),updated_at_beijing=now())
    atomic_json(f,j)
    # Restart after any error to discard possibly damaged CUDA context. Completed samples persist.
    raise
   finally:atomic_json(f,j);handle.close()
  update(state="complete")
 except BaseException as exc:update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

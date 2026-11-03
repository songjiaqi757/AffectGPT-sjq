from graph_paths import resolve_path as _graph_resolve_path
import argparse,copy,json,os,time,traceback
from graph_paths import Path
from .common import *
from .policy import make_prompt
def load_bound(model,config,run,p,variant,spec):
 config['variant']=variant
 config['training_plan_id']=spec.get('training_plan_id') or read(Path(run)/(variant+'_plan')/'plan.json')['plan_id']
 model.load(spec,dict(base_epoch=spec.get('continuation_base_epoch',p['variant_bases'][variant])))
def all_done(run):return complete_count(run)==plan(run)["logical_jobs"]
def choose(run,p):
 # Select ready jobs before inspecting their shards; the live queue has >10000 shards.
 candidates=[j for j in jobs(run) if j['state']!='complete']
 candidates.sort(key=lambda j:(-j['samples'],j['job_id']))
 for j in candidates:
  if checkpoint(run,j['variant'],j['epoch']) is None:continue
  for name in j['shards']:
   f=run/'shards'/name;s=read(f)
   if s['state']=='complete':continue
   handle=locked(f.with_suffix('.lock'))
   if handle is None:continue
   s=read(f)
   if s['state']=='complete':handle.close();continue
   require(s.get('attempts',0)<3,'Inference shard exhausted retries: '+f.name)
   s.update(state='running',attempts=s.get('attempts',0)+1,pid=os.getpid());atomic_json(f,s);return f,handle,s
 return None
def finalize(run,p,jid):
 h=locked(run/"jobs"/(jid+".lock"))
 if h is None:return
 try:
  j=read(run/"jobs"/(jid+".json"));shards=[read(run/"shards"/n) for n in j["shards"]]
  if not all(s["state"]=="complete" for s in shards):return
  rows=read(p["datasets"][j["dataset"]]["path"]);out=run/"predictions"/jid
  spec=checkpoint(run,j["variant"],j["epoch"]);values={}
  temp=out/"predictions.jsonl.tmp"
  with temp.open("w") as f:
   for row in rows:
    x=read(out/(sid_key(row["sample_id"])+".json"));require(x["checkpoint"]["sha256"]==spec["sha256"] and x["plan_id"]==p["plan_id"],"Prediction provenance changed")
    require(row["name"] not in values,"Duplicate name");values[row["name"]]=x["response"];f.write(json.dumps(x,ensure_ascii=False)+"\n")
  temp.replace(out/"predictions.jsonl")
  import numpy as np
  with (out/"name2reason.npz.tmp").open("wb") as f:np.savez_compressed(_graph_resolve_path(f), name2reason=values)
  (out/"name2reason.npz.tmp").replace(out/"name2reason.npz")
  j.update(state="complete",checkpoint=spec,prediction_path=str(out/"predictions.jsonl"),official_npz=str(out/"name2reason.npz"),finished_at_beijing=now());atomic_json(run/"jobs"/(jid+".json"),j)
 finally:h.close()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);ap.add_argument("--gpu",required=True,type=int);ap.add_argument("--slot",required=True,type=int);a=ap.parse_args();run=Path(a.run);p=plan(run);verify_code(run)
 dest=run/f"inference_gpu_{a.gpu}_slot_{a.slot}.json";s=dict(state="loading",pid=os.getpid(),gpu=a.gpu,slot=a.slot,started_at_beijing=now())
 def update(**kw):s.update(kw,updated_at_beijing=now());atomic_json(dest,s)
 try:
  import torch
  import amg_inference.model as original
  original.make_prompt=make_prompt
  config=copy.deepcopy(p);config["variant"]=p["variants"][0];config["training_plan_id"]=read(run/(p["variants"][0]+"_plan")/"plan.json")["plan_id"]
  model=original.Predictor(config);spec=None
  while spec is None:
   for v in p["variants"]:
    for epoch in p["variant_epochs"][v]:
     candidate=checkpoint(run,v,epoch)
     if candidate is not None:spec=candidate;config["variant"]=v;config["training_plan_id"]=read(run/(v+"_plan")/"plan.json")["plan_id"];break
    if spec is not None:break
   if spec is None:time.sleep(3)
  load_bound(model,config,run,p,config["variant"],spec);update(state="probe_loaded")
  while not (run/f"probe_go_gpu_{a.gpu}.json").exists():time.sleep(2)
  row=read(run/"train_records.json")[0];evidence=read(source_cache(p,row["sample_id"]))["evidence"]
  saved_stopping_criteria=model.chat.stopping_criteria
  try:response,info=model.predict(row,evidence,42+a.slot,stress=True)
  finally:model.chat.stopping_criteria=saved_stopping_criteria
  require(1530<=info["stress_prompt_tokens"]<=1536 and info["stress_generated_tokens"]==1200,"Four-lane full-window capacity probe failed")
  update(state="probe_passed",capacity_passed=True,probe_info=info,peak_memory_bytes=int(torch.cuda.max_memory_allocated()))
  while not (run/f"probe_accepted_gpu_{a.gpu}.json").exists():time.sleep(2)
  completed=0
  while not all_done(run):
   claim=choose(run,p)
   if claim is None:update(state="waiting_for_available_checkpoint",completed_samples=completed);time.sleep(4);continue
   f,handle,shard=claim
   try:
    variant=shard["variant"];config["variant"]=variant;config["training_plan_id"]=read(run/(variant+"_plan")/"plan.json")["plan_id"]
    spec=checkpoint(run,variant,shard["epoch"]);load_bound(model,config,run,p,config["variant"],spec)
    allrows=read(p["datasets"][shard["dataset"]]["path"]);rows=allrows[shard["start"]:shard["stop"]]
    out=run/"predictions"/shard["job_id"];out.mkdir(exist_ok=True)
    binding=canonical(dict(plan_id=p["plan_id"],variant=variant,checkpoint=spec["sha256"],input_sha=p["datasets"][shard["dataset"]]["sha256"]))
    update(state="inference",job_id=shard["job_id"],shard=f.name,completed_samples=completed)
    for row in rows:
     path=out/(sid_key(row["sample_id"])+".json")
     if path.exists():
      previous=read(path);require(previous["binding"]==binding,"Stale partial prediction")
     else:
      evidence=evidence_for(run,variant,row)
      # Same per-sample random stream across variants/epochs for a paired comparison.
      seed=(42+int(canonical(row["sample_id"])[:8],16))%2**32
      response,info=model.predict(row,evidence,seed)
      atomic_json(path,dict(sample_id=row["sample_id"],name=row["name"],dataset=shard["dataset"],variant=variant,epoch=shard["epoch"],response=response,checkpoint=spec,plan_id=p["plan_id"],binding=binding,seed=seed,prompt_info=info,created_at_beijing=now()))
     completed+=1
     if completed%10==0:update(completed_samples=completed)
    shard.update(state="complete",finished_at_beijing=now());atomic_json(f,shard);finalize(run,p,shard["job_id"])
   except BaseException as exc:
    shard.update(state="pending" if shard["attempts"]<3 else "failed",error=repr(exc));atomic_json(f,shard);raise
   finally:handle.close()
  update(state="complete",completed_samples=completed,finished_at_beijing=now())
 except BaseException as exc:update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

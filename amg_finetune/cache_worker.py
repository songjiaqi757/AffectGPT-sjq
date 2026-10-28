"""Batched frozen Cue inference; source inputs only, then frozen native graph query."""
import argparse,contextlib,json,os,time,traceback
from pathlib import Path
import numpy as np
import torch
from amg_runtime.common import read,sha,canonical,atomic_json,require,OFFSETS,MODALITIES
from amg_runtime.student import StudentRunner
from amg_runtime.engine import GraphQueryEngine
from .common import ROOT,load_plan,now,bound_query

class CacheCollator:
 def __init__(self,configs):self.configs=configs;self.collators={}
 def __call__(self,records):
  from cue_student.data import make_collator
  from cue_student.observations import describe
  payload=dict(records=records,modalities={},fingerprints=[])
  for row in records:
   dig=dict(text=dict(text_sha256=canonical({lang:row.get("text",{}).get(lang) or "" for lang in ["chinese","english"]})))
   for m,key in [("audio","audio_path"),("visual","video_path")]:
    p=Path(row[key]);st=p.stat();dig[m]=dict(path=str(p.resolve()),sha256=sha(p),bytes=st.st_size,mtime_ns=st.st_mtime_ns)
   payload["fingerprints"].append(dig)
  for m in MODALITIES:
   cfg=self.configs[m];a,b=OFFSETS[m]
   if m not in self.collators:self.collators[m]=make_collator(cfg)
   items=[dict(r,targets=np.zeros(b-a,np.float32),label_mask=np.zeros(b-a,bool)) for r in records]
   try:
    batch=self.collators[m](items)
    obs=[describe(batch,i,m,cfg) for i in range(len(records))]
    payload["modalities"][m]=dict(batch=batch,observations=obs)
   except Exception as exc:payload["modalities"][m]=dict(error=type(exc).__name__+": "+str(exc))
  return payload

def initialize_worker(index):
 torch.set_num_threads(1)
 os.environ["TOKENIZERS_PARALLELISM"]="false"
def make_batches(records,size=4):
 # Length buckets reduce audio padding without changing membership or Cue preprocessing.
 ordered=sorted(range(len(records)),key=lambda i:Path(records[i]["audio_path"]).stat().st_size)
 return [ordered[i:i+size] for i in range(0,len(ordered),size)]
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);p.add_argument("--worker",type=int,required=True);args=p.parse_args()
 run=Path(args.run);plan=load_plan(run);w=args.worker;started=time.time();done=0;invalid={m:0 for m in MODALITIES}
 status=dict(state="running",worker=w,device="cuda:0",physical_gpu=os.environ.get("CUDA_VISIBLE_DEVICES"),started_at_beijing=now(),plan_id=plan["plan_id"])
 def update():
  atomic_json(run/f"cache_worker_{w}_status.json",dict(status,completed=done,total=len(records),invalid_modality_counts=invalid,elapsed_seconds=time.time()-started))
 try:
  records=read(run/f"cache_inputs_{w}.json");update()
  require(set(r["sample_id"] for r in records)<=set(r["sample_id"] for r in read(run/"train_inputs.json")),"Out-of-split cache input")
  runner=StudentRunner(plan["runtime_path"],device="cuda:0",profile=plan["cue_profile"])
  engine=GraphQueryEngine.from_release(plan["runtime_path"],config_path=plan["query_config_path"])
  require(engine.config_id==plan["query_config_id"],"Query configuration drift")
  for m in MODALITIES:runner._load(m)
  cfgs={m:runner.inputs["checkpoints"][m]["config"] for m in MODALITIES}
  output=run/"cache";output.mkdir(exist_ok=True)
  pending=[r for r in records if not (output/(r["sample_id"]+".json")).exists()]
  done=len(records)-len(pending);update()
  # Worker children only preprocess/hash raw media; they never run a GPU model or read labels.
  loader=torch.utils.data.DataLoader(pending,batch_sampler=make_batches(pending,1),num_workers=plan["cache"]["loader_workers"],collate_fn=CacheCollator(cfgs),worker_init_fn=initialize_worker,multiprocessing_context="spawn",persistent_workers=True,prefetch_factor=2)
  proof=[]
  for payload in loader:
   rows=payload["records"];per_row=[{} for _ in rows]
   for m in MODALITIES:
    part=payload["modalities"][m];a,b=OFFSETS[m];scores=None
    if "batch" in part:
     from cue_student.common import move_batch
     batch=move_batch(part["batch"],torch.device("cuda:0"));cfg=cfgs[m]
     autocast=torch.autocast("cuda",dtype=torch.bfloat16) if cfg.get("precision")=="bf16" else contextlib.nullcontext()
     try:
      with torch.inference_mode(),autocast:logits=runner.models[m](batch)
      require(bool(torch.isfinite(logits).all()),"Non-finite batched Cue logits")
      scores=logits.float().sigmoid().cpu().tolist();del logits
     except torch.cuda.OutOfMemoryError:
      scores=None
     finally:
      del batch
    if scores is None:
     torch.cuda.empty_cache()
     for i,row in enumerate(rows):
      per_row[i][m],digest=runner._predict_modality(row,m)
      if digest is not None:payload["fingerprints"][i][m]=digest
    else:
     for i,row in enumerate(rows):
      per_row[i][m]=dict(sample_id=row["sample_id"],cue_ids=runner.inputs["cue_id_order"][a:b],scores=scores[i],input_valid=True,input_observation=part["observations"][i],inference_weights_sha256=runner.exports[m]["sha256"])
   for i,row in enumerate(rows):
    cue=runner.assembler.assemble(row["sample_id"],per_row[i],input_fingerprints=payload["fingerprints"][i])
    cue["runtime_release_id"]=runner.manifest["release_id"];cue["query_input_id"]=canonical({k:v for k,v in cue.items() if k!="query_input_id"})
    engine._validate_cues(cue)
    # Fixed first batch: compare reused batched forward with the native single-record API.
    if len(proof)<4:
     native=runner.predict_records([row])[0]
     diffs=[abs(x-y) for x,y in zip(cue["scores"],native["scores"]) if x is not None and y is not None]
     require(cue["availability_mask"]==native["availability_mask"],"Batched availability mismatch")
     require(max(diffs,default=0)==0,"Prefetched single-record/native Cue discrepancy")
     proof.append(dict(sample_id=row["sample_id"],maximum_absolute_score_difference=max(diffs,default=0),selected_mask_identical=cue["selected_mask"]==native["selected_mask"]))
     atomic_json(run/f"cache_worker_{w}_batch_proof.json",dict(cases=proof,tolerance=0,semantics="Native single-record forward with CPU preprocessing prefetch; all fixed proof scores must match bit-for-bit"))
    result=engine.query(cue);evidence=bound_query(result,engine)
    item=dict(schema_version="amg_training_cache_v1",sample_id=row["sample_id"],plan_id=plan["plan_id"],record_sha256=canonical(row),cue=cue,evidence=evidence,created_at_beijing=now())
    item["cache_id"]=canonical(item)
    atomic_json(output/(row["sample_id"]+".json"),item)
    for m in MODALITIES:invalid[m]+=int(not cue["modality_present"][m])
    done+=1
   if done%20<4 or done==len(records):
    update();print(json.dumps(dict(worker=w,completed=done,total=len(records),elapsed_seconds=time.time()-started)),flush=True)
  status.update(state="complete",finished_at_beijing=now());update()
 except Exception as exc:
  status.update(state="failed",error=type(exc).__name__+": "+str(exc),traceback=traceback.format_exc())
  if "records" not in locals():records=[]
  update();raise
if __name__=="__main__":main()

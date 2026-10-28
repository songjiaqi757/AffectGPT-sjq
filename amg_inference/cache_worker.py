"""One shared native single-record Cue/graph cache for the nine target input sets."""
import argparse,time,traceback
from pathlib import Path
import torch
from amg_runtime.common import read,canonical,atomic_json,require
from amg_runtime.student import StudentRunner
from amg_runtime.engine import GraphQueryEngine
from amg_finetune_nogc.common import bound_query,now
from .common import verify,cache_path,cue_input,evidence
def main():
 a=argparse.ArgumentParser();a.add_argument("--run",required=True);args=a.parse_args();run=Path(args.run);p=verify(run)
 s=dict(state="running",completed=0,total=p["dataset_samples_total"],started_at_beijing=now())
 def update():atomic_json(run/"cache_status.json",dict(s,updated_at_beijing=now()))
 try:
  torch.set_num_threads(4)
  runner=StudentRunner(p["runtime_path"],device="cuda:0",profile=p["cue_profile"])
  engine=GraphQueryEngine.from_release(p["runtime_path"],config_path=p["query_config_path"])
  require(engine.config_id==p["query_config_id"],"Frozen query configuration changed")
  for d,spec in p["datasets"].items():
   s["dataset"]=d;update()
   for row in read(spec["path"]):
    out=cache_path(run,row)
    if out.exists():evidence(run,row,p)
    else:
     inp=cue_input(row);cue=runner.predict_records([inp])[0]
     result=engine.query(cue);bound=bound_query(result,engine)
     item=dict(schema_version="amg_prediction_cache_v1",sample_id=row["sample_id"],plan_id=p["plan_id"],input_id=canonical(inp),cue=cue,evidence=bound,created_at_beijing=now())
     item["cache_id"]=canonical(item);atomic_json(out,item)
    s["completed"]+=1
    if s["completed"]%20==0:update()
  s.update(state="complete",finished_at_beijing=now());update()
 except BaseException as exc:
  s.update(state="failed",error=repr(exc),traceback=traceback.format_exc());update();raise
if __name__=="__main__":main()

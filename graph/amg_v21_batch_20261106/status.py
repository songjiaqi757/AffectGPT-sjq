import json,collections
from .common import *
if __name__=="__main__":
 run=Path(read(G/"amg_v21_batch_20261106/current_run.json")["path"]);p=load_plan(run);out=dict(run=str(run),plan_id=p["plan_id"],datasets=p["datasets"].keys(),predictions_total=p["sample_predictions_total"])
 out["datasets"]=list(out["datasets"])
 for name in ["preparation","preparation_failed","node_A800","node_A100"]:
  if (run/(name+".json")).exists():out[name]=read(run/(name+".json"))
 out["training_jobs"]=[read(f) for f in sorted((run/"training_jobs").glob("*.json"))]
 out["training"]=[read(f) for f in sorted(run.glob("experiment_*_status.json"))]
 out["inference_jobs"]=dict(collections.Counter(read(f)["state"] for f in (run/"jobs").glob("*.json")))
 out["scores_complete"]=len(list((run/"scores").glob("*.json")))
 print(json.dumps(out,ensure_ascii=False,indent=2))

"""Fresh best-checkpoint Cue predictions for pre-registered source validation members only."""
from graph_paths import hash_matches as _graph_hash_matches
import argparse,datetime,json,os,time,traceback
from graph_paths import Path
from zoneinfo import ZoneInfo
from amg_runtime.common import read,canonical,atomic_json,require,sha
from amg_runtime.student import StudentRunner
from amg_runtime.versioning import load_release
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);p.add_argument("--worker",type=int,required=True);args=p.parse_args()
 run=Path(args.run).resolve();reg=read(run/"preregistration.json")
 require(canonical({k:v for k,v in reg.items() if k!="preregistration_id"})==reg["preregistration_id"],"Preregistration identity mismatch")
 manifest=load_release(reg["runtime_path"]);require(manifest["release_id"]==reg["runtime_release_id"],"Runtime drift")
 assignment=read(run/"inputs"/("worker_"+str(args.worker)+".json"))
 require(_graph_hash_matches(run / 'inputs' / ('worker_' + str(args.worker) + '.json'), reg['worker_input_sha256'][str(args.worker)], sha(run / 'inputs' / ('worker_' + str(args.worker) + '.json'))),"Input assignment drift")
 require(set(row["sample_id"] for row in assignment)<=set(reg["validation_sample_ids"]),"Non-validation input")
 out=run/"predictions";out.mkdir(exist_ok=True)
 device="cuda:"+str(args.worker);started=time.time();done=0;invalid={m:0 for m in ["text","audio","visual"]}
 status=dict(state="running",worker=args.worker,device=device,total=len(assignment),runtime_release_id=manifest["release_id"],preregistration_id=reg["preregistration_id"],started_at_beijing=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat())
 def save():
  elapsed=time.time()-started
  atomic_json(run/("worker_"+str(args.worker)+"_status.json"),dict(status,completed=done,invalid_modality_counts=invalid,elapsed_seconds=elapsed,remaining=len(assignment)-done,mean_seconds_per_completed=elapsed/max(done,1)))
 try:
  save();runner=StudentRunner(reg["runtime_path"],device=device,profile="engineering")
  for row in assignment:
   path=out/(row["sample_id"]+".json");row_hash=canonical(row)
   if path.exists():
    cached=read(path);require(cached["record_sha256"]==row_hash and cached["prediction"]["runtime_release_id"]==manifest["release_id"],"Existing prediction provenance mismatch")
    prediction=cached["prediction"]
   else:
    before=time.time();prediction=runner.predict_records([row])[0]
    atomic_json(path,dict(record_sha256=row_hash,preregistration_id=reg["preregistration_id"],prediction=prediction,worker_device=device,inference_seconds=time.time()-before))
   require(prediction["sample_id"]==row["sample_id"],"Sample alignment error")
   require(prediction["query_input_id"]==canonical({k:v for k,v in prediction.items() if k!="query_input_id"}),"Prediction checksum error")
   for m,present in prediction["modality_present"].items():invalid[m]+=int(not present)
   done+=1
   if done%10==0 or done==len(assignment):save();print(json.dumps(dict(worker=args.worker,completed=done,total=len(assignment))),flush=True)
  status["state"]="complete";status["finished_at_beijing"]=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat();save()
 except Exception as exc:
  status.update(state="failed",error=type(exc).__name__+": "+str(exc),traceback=traceback.format_exc());save();raise
if __name__=="__main__":main()

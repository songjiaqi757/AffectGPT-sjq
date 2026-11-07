import argparse,os,subprocess,time,traceback,collections,json
from pathlib import Path
from .common import *
def main():
 a=argparse.ArgumentParser();a.add_argument("--run",required=True);x=a.parse_args();run=Path(x.run);p=load_plan(run);status=run/"pipeline_status.json"
 def update(state,**kw):atomic_json(status,dict(state=state,pid=os.getpid(),time_beijing=now(),**kw))
 try:
  update("waiting_for_5_graph_oof_folds")
  while True:
   done=[];stages={}
   for k in range(5):
    f=run/"folds"/str(k)/"status.json"
    if f.exists():
     s=read(f);stages[k]=s["state"];require(s["state"]!="failed","Fold "+str(k)+" failed: "+str(s.get("error")))
     if s["state"]=="complete":done.append(k)
   if len(done)==5:break
   update("waiting_for_5_graph_oof_folds",completed_folds=done,fold_stages=stages);time.sleep(15)
  update("final_preflight")
  require(read(run/"native_P4_prompt_equivalence.json")["passed"],"Previous three-dataset Prompt equivalence not verified")
  verify_code(run)
  records=read(run/"train_records.json");audit=read(run/"human_audit_500.json");ids={r["sample_id"] for r in records};assert len(ids)==30755 and not ids&{r["sample_id"] for r in audit} and len(audit)==500
  checked=set();manifests=[]
  for k in range(5):
   fold=run/"folds"/str(k);m=read(fold/"evidence_manifest.json");assert m["complete"] and m["sha256"]==sha(fold/"evidence.jsonl");held=set(read(fold/"membership.json")["held_ids"])
   actual=set()
   with (fold/"evidence.jsonl").open() as f:
    for line in f:
     item=json.loads(line);assert item["fold"]==k and item["sample_id"] not in actual;actual.add(item["sample_id"])
   assert actual==held and not checked&actual;checked|=actual;manifests.append(m)
  assert checked==ids
  spec=p["checkpoints"][0];assert sha(spec["path"])==spec["sha256"]
  assets=read(run/"model_assets_manifest.json")
  for name,binding in assets["assets"].items():
   st=Path(name).stat();assert st.st_size==binding["bytes"] and st.st_mtime_ns==binding["mtime_ns"],name
  assert sha(run/"train_records.json")==p["inputs"]["train_records_sha256"]
  assert sha(run/"human_audit_500.json")==p["inputs"]["audit_records_sha256"]
  atomic_json(run/"cache_manifest.json",dict(complete=True,samples=30755,plan_id=p["plan_id"],folds=manifests,graph_version="v2.1",format="P4",graph_only=True,cue_student_oof=False))
  atomic_json(run/"cpu_preflight.json",dict(passed=True,train_samples=30755,audit_samples_excluded=500,held_group_overlap=0,folds=5,prompt_checks=sum(m["cpu_prompt_checks"] for m in manifests),maximum_sequence_tokens=max(m["maximum_sequence_tokens"] for m in manifests),maximum_prompt_tokens=max(m["maximum_prompt_tokens"] for m in manifests),original_subtitle_preserved=True,P4_max_graph_tokens=p["training"]["graph_token_budget"],answer_only_loss_mask=True,gpu_update_test="Counted within requested training",time_beijing=now()))
  used=int(subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip());require(used<1000,"GPU is occupied before launch")
  update("starting_training",epochs=[36,37,38,39,40],maximum_sequence_tokens=max(m["maximum_sequence_tokens"] for m in manifests))
  env=dict(os.environ,CUDA_VISIBLE_DEVICES="0",OMP_NUM_THREADS="4",MKL_NUM_THREADS="4",OPENBLAS_NUM_THREADS="1",PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True")
  with (run/"train.log").open("ab",buffering=0) as log:
   process=subprocess.Popen([str(PYTHON),"-u","-B","-m","amg_v21_continue.train_worker","--run",str(run),"--base-epoch","35"],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
   atomic_json(run/"training_process.json",dict(pid=process.pid,node="Qiii",ssh_port=34989,started_at_beijing=now()))
   update("training",training_pid=process.pid,epochs=[36,37,38,39,40]);code=process.wait()
  require(code==0,"Training exited with status "+str(code))
  final=read(run/"from_35/status.json");checkpoints=read(run/"from_35/checkpoints.json")
  assert final["state"]=="complete" and final["completed_steps"]==25000 and [c["epoch"] for c in checkpoints]==[36,37,38,39,40]
  for c in checkpoints:assert sha(c["path"])==c["sha256"]
  update("complete",checkpoints=checkpoints,completed_steps=25000)
 except BaseException as exc:update("failed",error=repr(exc),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

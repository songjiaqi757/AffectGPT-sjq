import argparse,collections,csv,io,json,os,signal,subprocess,time,traceback
from pathlib import Path
from .common import *
def stop(proc):
 if proc is not None and proc.poll() is None:
  try:os.killpg(proc.pid,signal.SIGTERM)
  except ProcessLookupError:pass
def summarize(run,p):
 rows=[read(f) for f in (run/"scores").glob("*.json")]
 fields=["variant","base_epoch","epoch","dataset","samples","main_metric","main_score","HIT","WAF","ACC","F_s","P_s","R_s"]
 out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields,extrasaction="ignore");w.writeheader()
 for r in sorted(rows,key=lambda r:(r["variant"],r["epoch"],r["dataset"])):w.writerow(dict(r,**r["metrics"]))
 temp=run/"metrics_all.csv.tmp";temp.write_text(out.getvalue());temp.replace(run/"metrics_all.csv")
 summary=[]
 for variant in p["variants"]:
  for epoch in p["variant_epochs"][variant]:
   selected=[r for r in rows if r["variant"]==variant and r["epoch"]==epoch]
   r=dict(variant=variant,base_epoch=p["variant_bases"][variant],epoch=epoch,datasets_completed=len(selected),three_dataset_mean=sum(x["main_score"] for x in selected)/3 if len(selected)==3 else None)
   for x in selected:
    for k,v in x["metrics"].items():r[x["dataset"]+"_"+k]=v
   summary.append(r)
 atomic_json(run/"per_checkpoint_summary.json",summary)
 fields=["variant","base_epoch","epoch","datasets_completed","three_dataset_mean","MER2023_HIT","SIMS_WAF","SIMS_ACC","OVMERDPlus_F_s","OVMERDPlus_P_s","OVMERDPlus_R_s"]
 out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields);w.writeheader();w.writerows(summary)
 temp=run/"per_checkpoint_summary.csv.tmp";temp.write_text(out.getvalue());temp.replace(run/"per_checkpoint_summary.csv")
 if len(rows)==p["logical_jobs"]:
  lines=["# D continuation: old graph versus new graph","All 10 checkpoints x three datasets completed. Scores are exploratory; no nine-dataset mean is implied.","","|Variant|Epoch|MER2023 HIT|SIMS WAF|OVMERDPlus F_s|Three-set mean|","|---|---:|---:|---:|---:|---:|"]
  for r in summary:lines.append("|"+r["variant"]+"|"+str(r["epoch"])+"|"+"|".join(f"{100*r[k]:.2f}" for k in ["MER2023_HIT","SIMS_WAF","OVMERDPlus_F_s","three_dataset_mean"])+"|")
  (run/"RESULTS.md").write_text("\n".join(lines)+"\n")
 return len(rows)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);a=ap.parse_args();run=Path(a.run);p=plan(run);verify_code(run)
 owner=locked(run/"controller.lock");require(owner is not None,"Pipeline already running")
 require(read(run/"cpu_preflight.json")["passed"],"CPU preflight not passed")
 gpu_locks=[];training={};infer={0:[],1:[]};scorers=[];allchildren=[]
 queues={int(k):list(v) for k,v in p["gpu_training_queues"].items()};completed={0:[],1:[]};probe_go=set();probe_accepted=set();restarts=collections.Counter()
 state=dict(phase="starting",pid=os.getpid(),pgid=os.getpgrp(),plan_id=p["plan_id"],started_at_beijing=now())
 def update(**kw):
  state.update(kw,updated_at_beijing=now());atomic_json(run/"status.json",state)
 def start_train(gpu,variant):
  with (run/f"train_{variant}.log").open("ab",buffering=0) as log:
   child=subprocess.Popen([str(PYTHON),"-u","-B","-m","amg_d_graph_compare.train_worker","--run",str(run/(variant+"_plan")),"--base-epoch",str(p["variant_bases"][variant])],cwd=ROOT,env=environment(gpu),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  allchildren.append(child);training[gpu]=(variant,child);atomic_json(run/f"training_gpu_{gpu}.json",dict(state="training",variant=variant,pid=child.pid,gpu=gpu,remaining_queue=queues[gpu],started_at_beijing=now()))
 def start_infer(gpu):
  infer[gpu]=[launch(run,"amg_d_graph_compare.infer_worker",["--gpu",str(gpu),"--slot",str(slot)],f"inference_gpu_{gpu}_slot_{slot}.log",gpu) for slot in range(4)];allchildren.extend(infer[gpu])
 try:
  for gpu in [0,1]:
   h=locked(ROOT/"amg_finetune_nogc"/f"gpu_{gpu}.lock");require(h is not None,"GPU owned by another run");gpu_locks.append(h)
  for gpu in [0,1]:start_train(gpu,queues[gpu].pop(0))
  update(phase="training",training={str(g):dict(variant=v,pid=c.pid) for g,(v,c) in training.items()})
  while True:
   for gpu in [0,1]:
    if gpu in training:
     variant,proc=training[gpu]
     if proc.poll() is not None:
      require(proc.returncode==0 and read(run/variant/"status.json")["state"]=="complete","Training failed: "+variant)
      require(len(read(run/variant/"checkpoints.json"))==5,"Training did not publish five weights")
      completed[gpu].append(variant);training.pop(gpu)
      atomic_json(run/f"training_gpu_{gpu}.json",dict(state="waiting_for_next" if queues[gpu] else "complete",gpu=gpu,completed=completed[gpu],finished_at_beijing=now()))
    if gpu not in training and queues[gpu]:
     variant=queues[gpu][0]
     if True:
      queues[gpu].pop(0);start_train(gpu,variant)
    if gpu not in training and not queues[gpu] and not infer[gpu]:start_infer(gpu)
    if infer[gpu]:
     snapshots=[]
     for slot in range(4):
      f=run/f"inference_gpu_{gpu}_slot_{slot}.json";snapshots.append(read(f) if f.exists() else {})
     if gpu not in probe_go and all(s.get("state")=="probe_loaded" for s in snapshots):
      atomic_json(run/f"probe_go_gpu_{gpu}.json",dict(time_beijing=now(),concurrent_models=4));probe_go.add(gpu)
     if gpu not in probe_accepted and all(s.get("capacity_passed",False) for s in snapshots):
      atomic_json(run/f"probe_accepted_gpu_{gpu}.json",dict(passed=True,concurrent_models=4,source_only_full_window=True,reports=snapshots,time_beijing=now()));probe_accepted.add(gpu)
     for slot,proc in enumerate(infer[gpu]):
      if proc.poll() not in [None,0] and complete_count(run)<p["logical_jobs"]:
       require(gpu in probe_accepted,"Four-lane source capacity probe failed")
       restarts[(gpu,slot)]+=1;require(restarts[(gpu,slot)]<=3,"Inference worker repeatedly failed")
       infer[gpu][slot]=launch(run,"amg_d_graph_compare.infer_worker",["--gpu",str(gpu),"--slot",str(slot)],f"inference_gpu_{gpu}_slot_{slot}.log",gpu);allchildren.append(infer[gpu][slot])
   c=complete_count(run)
   update(phase="training_and_inference" if training or any(queues.values()) else "inference",training={str(g):dict(variant=v,pid=x.pid) for g,(v,x) in training.items()},training_completed=completed,queued=queues,inference_pids={str(g):[x.pid for x in xs] for g,xs in infer.items()},inference_jobs_complete=c,inference_jobs_total=p["logical_jobs"])
   if c==p["logical_jobs"] and not training and not any(queues.values()):break
   time.sleep(15)
  update(phase="waiting_for_inference_exit")
  for xs in infer.values():
   for proc in xs:proc.wait(timeout=180);require(proc.returncode==0,"Inference process did not exit cleanly")
  for gpu in [0,1]:
   deadline=time.monotonic()+120
   while True:
    usage=subprocess.check_output(["nvidia-smi","--id="+str(gpu),"--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip()
    if int(usage)<256:break
    require(time.monotonic()<deadline,"GPU memory not released before judge launch");time.sleep(3)
  atomic_json(run/"evaluation_barrier.json",dict(passed=True,all_inference_jobs=p["logical_jobs"],training_weights=10,inference_processes_exited=True,gpus_released=[0,1],time_beijing=now()))
  scorers=[launch(run,"amg_d_graph_compare.score_worker",["--gpu",str(g)],f"evaluation_gpu_{g}.log",g) for g in [0,1]];allchildren.extend(scorers)
  update(phase="dual_gpu_evaluation",evaluation_pids=[x.pid for x in scorers])
  score_restarts=[0,0]
  while True:
   n=summarize(run,p);update(scores_complete=n,evaluation_pids=[x.pid for x in scorers])
   if n==p["logical_jobs"]:break
   for gpu,proc in enumerate(scorers):
    if proc.poll() is not None:
     score_restarts[gpu]+=1;require(score_restarts[gpu]<=3,"Judge repeatedly failed")
     stop(proc)
     from amg_inference.priority_controller import wait_gpu_free
     wait_gpu_free(gpu)
     scorers[gpu]=launch(run,"amg_d_graph_compare.score_worker",["--gpu",str(gpu)],f"evaluation_gpu_{gpu}.log",gpu);allchildren.append(scorers[gpu])
   time.sleep(15)
  for proc in scorers:proc.wait(timeout=180);require(proc.returncode==0,"Judge process exit failure")
  update(phase="complete",weights=10,predictions=14000,scores=p["logical_jobs"],finished_at_beijing=now(),summary=str(run/"RESULTS.md"))
 except BaseException as exc:
  for proc in allchildren:stop(proc)
  update(phase="failed",error=repr(exc),traceback=traceback.format_exc());raise
 finally:
  for h in gpu_locks:h.close()
  owner.close()
if __name__=="__main__":main()

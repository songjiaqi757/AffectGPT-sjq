import concurrent.futures,traceback
from .common import *
from .prepare import part
if __name__=="__main__":
 run=Path(read(G/"amg_v21_batch_20261106/current_run.json")["path"]);p=load_plan(run);verify_code(run);rows=read(run/"train_records.json")
 tasks=[(str(run),"train",i,rows[i*1000:(i+1)*1000]) for i in range(16,(len(rows)+999)//1000)]
 try:
  status(run,"cpu_assist_A100",state="preparing",parts=len(tasks),workers=16)
  done=0
  with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:
   for f in concurrent.futures.as_completed([pool.submit(part,t) for t in tasks]):
    r=f.result();done+=1;status(run,"cpu_assist_A100",state="preparing",parts=len(tasks),parts_complete=done,last_part=r["name"])
  status(run,"cpu_assist_A100",state="complete",parts_complete=done)
 except BaseException as exc:status(run,"cpu_assist_A100",state="failed",error=repr(exc),traceback=traceback.format_exc());raise

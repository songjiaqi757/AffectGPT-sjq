from pathlib import Path
import json
run=Path(__file__).resolve().parent
def read(name):
 p=run/name
 return json.loads(p.read_text()) if p.exists() else None
summary={"run":str(run),"pipeline":read("status.json"),"cache_workers":[read("cache_worker_0_status.json"),read("cache_worker_1_status.json")],"gpu_queues":[read("gpu_0_queue_status.json"),read("gpu_1_queue_status.json")],"experiments":{str(e):read("experiment_"+str(e)+"_status.json") for e in [30,35,40,45,50]}}
print(json.dumps(summary,ensure_ascii=False,indent=2))

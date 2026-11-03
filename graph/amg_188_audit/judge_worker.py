from graph_paths import resolve_path as _graph_resolve_path

import argparse,copy,sys,traceback
from .common import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--run",required=True);ap.add_argument("--gpu",type=int,required=True);ap.add_argument("--stage",choices=["openset","sentiment"],required=True);a=ap.parse_args()
 run=Path(a.run);p=plan(run);verify_code(run)
 require(read(run/"evaluation_barrier.json")["passed"],"Inference must exit first")
 rows=read(run/("judge_inputs_"+a.stage+".json"));rows=[x for x in rows if int(x["key"][:8],16)%2==a.gpu]
 dest=run/f"judge_{a.stage}_gpu_{a.gpu}.json";state=dict(state="loading",pid=os.getpid(),stage=a.stage,gpu=a.gpu,total=len(rows))
 def update(**kw):state.update(kw,time_beijing=now());atomic_json(dest,state)
 try:
  update();pending=[x for x in rows if not (run/"judge_cache"/a.stage/(x["key"]+".json")).exists()]
  if pending:
   os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"));import evaluation
   llm,t,params=evaluation.func_read_batch_calling_model("Qwen25")
   fn=evaluation.reason_to_openset_qwen if a.stage=="openset" else evaluation.openset_to_sentiment_qwen
   for start in range(0,len(pending),8):
    batch=pending[start:start+8];settings=[]
    for x in batch:q=copy.deepcopy(params);q.seed=x["seed"];settings.append(q)
    outputs=fn(llm=llm,tokenizer=t,sampling_params=settings,batch_reasons=[x["text"] for x in batch])
    require(len(outputs)==len(batch),"Judge batch cardinality changed")
    for x,y in zip(batch,outputs):
     require(isinstance(y,str),"Judge output is not text");atomic_json(run/"judge_cache"/a.stage/(x["key"]+".json"),dict(**x,output=y,judge_protocol_id=p["judge_protocol_id"]))
    update(state="scoring",completed=start+len(batch),pending_total=len(pending))
  update(state="complete",completed=len(rows))
 except BaseException as exc:update(state="failed",error=repr(exc),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

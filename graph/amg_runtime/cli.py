"""Server-only CLI for P2 Cue prediction and P3 evidence querying."""
import argparse,json
from graph_paths import Path
from .common import atomic_json,read,release_path
def main():
 p=argparse.ArgumentParser()
 p.add_argument("operation",choices=["predict","query","run"])
 p.add_argument("--release");p.add_argument("--input",required=True);p.add_argument("--output",required=True)
 p.add_argument("--device",default="cuda:0");p.add_argument("--profile",choices=["engineering","deployment"],default="engineering")
 p.add_argument("--query-config");p.add_argument("--audit-log")
 args=p.parse_args();directory=release_path(args.release);records=read(args.input)
 if isinstance(records,dict):records=[records]
 if args.operation in ("predict","run"):
  from .student import StudentRunner
  scores=StudentRunner(directory,args.device,args.profile).predict_records(records)
 else:scores=records
 if args.operation=="predict":result=scores
 else:
  from .engine import GraphQueryEngine
  engine=GraphQueryEngine.from_release(directory,args.query_config)
  result=[engine.query(row) for row in scores]
 atomic_json(args.output,result)
 if args.audit_log:
  # Exclusive creation prevents silently appending incompatible experiment versions.
  with Path(args.audit_log).open("x") as f:
   for row in result:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n")
 print(json.dumps(dict(output=str(Path(args.output).resolve()),samples=len(result),operation=args.operation),ensure_ascii=False))
if __name__=="__main__":main()

"""Execute the pre-registered stages after fresh prediction completion."""
import argparse,datetime,os,subprocess,sys,time,traceback
from pathlib import Path
from zoneinfo import ZoneInfo
from amg_runtime.common import ROOT,read,sha,atomic_json,require
def main(run):
 run=Path(run);reg=read(run/"preregistration.json")
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1")
 try:
  while True:
   statuses=[read(run/("worker_"+str(w)+"_status.json")) for w in range(2)]
   require(all(s["state"]!="failed" for s in statuses),"A prediction worker failed")
   if all(s["state"]=="complete" for s in statuses):break
   atomic_json(run/"status.json",dict(phase="waiting_for_predictions",completed=sum(s["completed"] for s in statuses),total=3076,preregistration_id=reg["preregistration_id"]))
   time.sleep(5)
  code={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/"amg_validation").glob("*.py"))}
  atomic_json(run/"evaluation_code_manifest.json",dict(source_code_sha256=code,preregistration_id=reg["preregistration_id"],frozen_before_parameter_metrics=True,frozen_at_beijing=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()))
  with (run/"stage_A.log").open("w") as log:
   result=subprocess.run([sys.executable,"-u","-m","amg_validation.prepare","--run",str(run)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
  require(result.returncode==0,"Stage A failed; see stage_A.log")
  atomic_json(run/"status.json",dict(phase="stage_B_profiles",preregistration_id=reg["preregistration_id"],profiles=4))
  children=[]
  for index in range(4):
   with (run/("profile_"+str(index)+".log")).open("w") as log:p=subprocess.Popen([sys.executable,"-u","-m","amg_validation.profile_worker","--run",str(run),"--index",str(index)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
   children.append(p)
  codes=[p.wait() for p in children]
  require(codes==[0]*4,"Profile worker failure: "+str(codes))
  with (run/"finalize.log").open("w") as log:
   result=subprocess.run([sys.executable,"-u","-m","amg_validation.finalize","--run",str(run)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
  require(result.returncode==0,"Final native replay/freeze failed; see finalize.log")
  print("P4 SELECTION COMPLETE",flush=True)
 except Exception as exc:
  atomic_json(run/"evaluation_failure.json",dict(error=str(exc),traceback=traceback.format_exc()))
  raise
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);args=p.parse_args();main(args.run)

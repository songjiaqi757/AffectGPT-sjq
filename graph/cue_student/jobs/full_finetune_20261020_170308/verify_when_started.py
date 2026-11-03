from pathlib import Path
import json,time,subprocess,sys,os
ROOT=Path(__file__).resolve().parent
deadline=time.monotonic()+1800
while True:
 s=json.loads((ROOT/"status.json").read_text())
 if s["phase"]=="failed":raise RuntimeError(s.get("error"))
 if s["phase"]=="training" and len(s.get("runs",{}))==4:break
 if time.monotonic()>deadline:raise RuntimeError("Startup verification timeout")
 time.sleep(10)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",OMP_NUM_THREADS="2",OPENBLAS_NUM_THREADS="2",MKL_NUM_THREADS="2")
r=subprocess.run([sys.executable,"-u",str(ROOT/"final_audit.py")],cwd=ROOT,env=env)
r.check_returncode()
print("ALL_NINE_VERIFIED",flush=True)

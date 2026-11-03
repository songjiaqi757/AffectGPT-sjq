from pathlib import Path
import os,subprocess,time,sys
ROOT=Path(__file__).resolve().parent
deadline=time.monotonic()+600
while not (ROOT/"data_audit.json").exists():
    if time.monotonic()>deadline:raise RuntimeError("Data rebuild timeout")
    time.sleep(2)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",OMP_NUM_THREADS="2",MKL_NUM_THREADS="2",OPENBLAS_NUM_THREADS="2")
with (ROOT/"unit_tests.log").open("w") as log:
    result=subprocess.run([sys.executable,"-m","unittest","discover","-s","cue_student/tests","-p","test_*.py"],cwd=ROOT/"source",env=env,stdout=log,stderr=subprocess.STDOUT)
print("UNIT_RETURN",result.returncode,flush=True)
result.check_returncode()

from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
ROOT=Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
OUT=ROOT/"amg/experiments/single-seed42-face-ckpt35-bias-validation-v1/recovery-v2"
PY="/ai/sjq/miniconda3/envs/vllm/bin/python"
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",
 TRANSFORMERS_OFFLINE="1",OMP_NUM_THREADS="2",MKL_NUM_THREADS="2",CUDA_VISIBLE_DEVICES="",PYTHONUNBUFFERED="1")
args=[PY,"-B","-m","amg.run_bias_recovery","--protocol",str(OUT/"protocol.json"),"--output-dir",str(OUT)]
if (OUT/"state.json").exists() or (OUT/"pipeline.pid").exists():
    raise FileExistsError("Never duplicate a recovery")
with (OUT/"validation.log").open("x") as log:
    subprocess.run(args+["--validate-only"],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
with (OUT/"pipeline.log").open("x") as log:
    proc=subprocess.Popen(args,cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,
                          stderr=subprocess.STDOUT,start_new_session=True)
(OUT/"pipeline.pid").write_text(str(proc.pid)+"\n")
record={"launched_at":datetime.now(timezone.utc).isoformat(),"runner_pid":proc.pid,
        "argv":args,"detached":True,"no_retraining":True,"all_artifacts_server_only":True}
(OUT/"LAUNCH.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps(record),flush=True)

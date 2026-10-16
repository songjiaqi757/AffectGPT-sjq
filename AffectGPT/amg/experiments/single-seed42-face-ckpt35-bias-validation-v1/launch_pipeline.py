"""Validate and detach the server-only bias pipeline; no models are loaded here."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
ROOT=Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
OUT=ROOT/"amg/experiments/single-seed42-face-ckpt35-bias-validation-v1"
PY="/ai/sjq/miniconda3/envs/vllm/bin/python"
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",
         TRANSFORMERS_OFFLINE="1",OMP_NUM_THREADS="2",MKL_NUM_THREADS="2",
         CUDA_VISIBLE_DEVICES="",PYTHONUNBUFFERED="1")
args=[PY,"-B","-m","amg.run_bias_validation","--protocol",str(OUT/"protocol.json"),
      "--output-dir",str(OUT)]
if (OUT/"state.json").exists() or (OUT/"pipeline.pid").exists():
    raise FileExistsError("Do not duplicate an existing trial")
with (OUT/"validation.log").open("x") as log:
    subprocess.run(args+["--validate-only"],cwd=ROOT,env=env,stdout=log,
                   stderr=subprocess.STDOUT,check=True)
with (OUT/"pipeline.log").open("x") as log:
    process=subprocess.Popen(args,cwd=ROOT,env=env,stdin=subprocess.DEVNULL,
                             stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(OUT/"pipeline.pid").write_text(str(process.pid)+"\n")
record={"launched_at":datetime.now(timezone.utc).isoformat(),"runner_pid":process.pid,
        "argv":args,"server_only":True,"detached":True,
        "user_preference":"End assistant turn after launch/PID validation; no continuous monitoring"}
(OUT/"LAUNCH.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(record),flush=True)

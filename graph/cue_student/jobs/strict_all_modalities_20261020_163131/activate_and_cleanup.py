from pathlib import Path
import json,time,subprocess,sys,os
ROOT=Path(__file__).resolve().parent
deadline=time.monotonic()+900
while True:
 path=ROOT/"status.json"
 if path.exists():
  status=json.loads(path.read_text())
  if status["phase"]=="failed":raise RuntimeError(status.get("error"))
  if len(status.get("runs",{}))==5:
   if any(r.get("state")=="failed" for r in status["runs"].values()):raise RuntimeError("New trainer failed")
   ready=True
   for run in status["runs"].values():
    p=Path(run["output"])/"events.jsonl"
    if not p.exists() or not any(json.loads(line).get("event")=="train" for line in p.read_text().splitlines()):ready=False
   if ready:break
 if time.monotonic()>deadline:raise RuntimeError("Timed out waiting for all five new updates")
 time.sleep(5)
print("ALL_FIVE_FRESH_RUNS_UPDATING",flush=True)
result=subprocess.run([sys.executable,"-u",str(ROOT/"cleanup_old.py")],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
result.check_returncode()
print("CLEANUP_COMPLETE",flush=True)

from pathlib import Path
import json,os,signal,time
ROOT=Path(__file__).resolve().parent
plan=json.loads((ROOT/"stop_plan.json").read_text())
def cmdline(pid):
 try:return Path("/proc",str(pid),"cmdline").read_bytes().replace(b"\0",b" ").decode()
 except FileNotFoundError:return ""
for pid in plan["supervisors"]:
 cmd=cmdline(pid)
 if "rolling_resume.py" in cmd or "audio_temporal_" in cmd and "launch.py" in cmd:
  os.kill(pid,signal.SIGTERM)
 else:raise RuntimeError("Supervisor PID mismatch "+str(pid)+" "+cmd)
for name,pid in plan["trainers"].items():
 cmd=cmdline(pid)
 if "-m cue_student.train" not in cmd:raise RuntimeError("Trainer PID mismatch "+str(pid)+" "+cmd)
 os.kill(pid,signal.SIGUSR1)
deadline=time.monotonic()+600
while True:
 active={name:pid for name,pid in plan["trainers"].items() if cmdline(pid)}
 (ROOT/"stop_status.json").write_text(json.dumps(dict(active=active,complete=not active),indent=2)+"\n")
 if not active:break
 if time.monotonic()>deadline:raise RuntimeError("Graceful stop deadline exceeded")
 time.sleep(2)
print("ALL_FIVE_STOPPED",flush=True)

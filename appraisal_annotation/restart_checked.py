"""Check the same Qwen endpoint, then resume the existing durable queue."""
from pathlib import Path
import fcntl,json,os,subprocess,sys,time
import requests
root=Path("/ai/sjq/AffectGPT-sjq/appraisal_annotation/runs/mercaptionplus_v2_4")
print("READY_FOR_API_KEY",flush=True)
key=sys.stdin.readline().strip()
assert key,"Missing API credential"
with (root/"runner.lock").open("a") as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 cfg=json.loads((root/"runtime_config.json").read_text())
 cfg["workers"]=48
 tmp=root/"runtime_config.json.resume.tmp"
 tmp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2));tmp.replace(root/"runtime_config.json")
 response=requests.post("https://maas.qianwenaiapi.com/compatible-mode/v1/chat/completions",
  headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},
  json={"model":"qwen3.8-omni-flash","messages":[{"role":"user","content":"Reply with OK."}],"temperature":0,"max_tokens":32,"stream":False,"modalities":["text"],"reasoning_effort":"none"},
  proxies={"http":"socks5h://127.0.0.1:1080","https":"socks5h://127.0.0.1:1080"},timeout=(20,90),allow_redirects=False)
 try:body=response.json()
 except ValueError:body={"text":response.text[:500]}
 result={"checked_unix":time.time(),"http_status":response.status_code,"model":"qwen3.8-omni-flash","workers":48,
  "error":body.get("error") if isinstance(body,dict) else None}
 if response.status_code!=200:
  (root/"restart_preflight.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
  print("PREFLIGHT_FAILED",json.dumps(result,ensure_ascii=False),flush=True)
  sys.exit(2)
 assert body.get("choices"),"No completion returned"
 result["passed"]=True
 (root/"restart_preflight.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
print("PREFLIGHT_PASSED",flush=True)
env=dict(os.environ,QWEN_HTTPS_PROXY="socks5h://127.0.0.1:1080",PYTHONDONTWRITEBYTECODE="1")
with (root/"execution.log").open("a") as log:
 proc=subprocess.Popen([sys.executable,"-u",str(root.parents[1]/"annotate_full.py"),"--run"],
  cwd=str(root.parents[1]),stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
 proc.stdin.write((key+"\n").encode());proc.stdin.close()
launch={"pid":proc.pid,"started_unix":time.time(),"credential_delivery":"anonymous_stdin_pipe_in_memory","detached":True,"workers":48,"preflight_passed":True}
(root/"launch.json").write_text(json.dumps(launch,ensure_ascii=False,indent=2))
print("DETACHED_RUNNER_STARTED",proc.pid,flush=True)

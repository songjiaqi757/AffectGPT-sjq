"""Launch two bounded AV/Adapter diagnostics and aggregate automatically."""
from pathlib import Path
import concurrent.futures as cf
import datetime, fcntl, hashlib, json, os, signal, subprocess, sys, threading, time, traceback

ROOT=Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
HERE=Path(__file__).resolve().parent
PYTHON="/ai/sjq/miniconda3/envs/vllm/bin/python"
STOP=threading.Event()
LOCK=threading.RLock()
CHILDREN={}
STATE={"schema":"amg-adapter-sensitivity-state-v1","status":"preparing","jobs":{}}

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def read(p):
    return json.loads(Path(p).read_text())

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return h.hexdigest()

def save(p,o):
    tmp=p.with_name(p.name+".tmp")
    tmp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n")
    tmp.replace(p)

def event(name,stage,**extra):
    item={"time":now(),"name":name,"stage":stage,**extra}
    with LOCK:
        STATE["updated_at"]=item["time"]
        STATE["jobs"][name]=item
        save(HERE/"state.json",STATE)
        with (HERE/"events.jsonl").open("a") as f:f.write(json.dumps(item,ensure_ascii=False)+"\n")
        print(json.dumps(item,ensure_ascii=False),flush=True)

def validate(p):
    locked=read(HERE/"READY.json")["locked_files"]
    required={str(HERE/"protocol.json"),str(HERE/"run_sensitivity.py"),str(HERE/"diagnose_adapter.py"),p["bank"]+".json"}
    required.update(p[k] for k in ["base_config","bank","fit_manifest","manifest","amg_checkpoint","normal_trace","random_trace","normal_metadata","random_metadata","normal_predictions","random_predictions","normal_report","random_report","intervention_state"])
    required.update(str(x.resolve()) for x in (ROOT/"amg").glob("*.py"))
    if not required.issubset(locked):raise ValueError("Missing locked inputs: "+repr(sorted(required-set(locked))))
    for name,expected in locked.items():
        if sha(name)!=expected:raise ValueError("Locked input changed: "+name)
    a,b=read(p["normal_metadata"]),read(p["random_metadata"])
    for k in ["amg_sha256","base_sha256","manifest_sha256","memory_sha256","config_sha256",
              "trained_mode","seed","decoding","face_or_frame","prompt_sha256"]:
        if a[k]!=b[k]:raise ValueError("Reference mismatch: "+k)
    assert a["amg_sha256"]==p["amg_sha256"]==sha(p["amg_checkpoint"])
    assert a["trained_mode"]=="retrieval" and a["memory_mode"]=="retrieval" and b["memory_mode"]=="random"
    assert a["successes"]==b["successes"]==p["N"]==500
    assert a["errors"]==b["errors"]==0
    assert a["seed"]==p["seed"]==42
    assert read(p["intervention_state"])["status"]=="complete"
    return {"validated":True,"locked_files":len(locked),"amg_sha256":p["amg_sha256"]}

def env_for(gpu):
    e=os.environ.copy()
    e.update(PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",
             OMP_NUM_THREADS="2",MKL_NUM_THREADS="2",PYTHONUNBUFFERED="1",
             CUDA_VISIBLE_DEVICES="" if gpu is None else str(gpu))
    return e

def stop_child(proc):
    if proc.poll() is not None:return
    try:
        os.killpg(proc.pid,signal.SIGTERM)
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid,signal.SIGKILL);proc.wait()
    except ProcessLookupError:pass

def command(args,name,gpu):
    if STOP.is_set():raise RuntimeError("Stopped")
    log=HERE/(name+".log")
    with log.open("x") as out:
        out.write(json.dumps({"argv":args,"gpu":gpu,"time":now()})+"\n");out.flush()
        proc=subprocess.Popen(args,cwd=ROOT,env=env_for(gpu),stdin=subprocess.DEVNULL,
                              stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        with LOCK:CHILDREN[proc.pid]=proc
        event(name,"running",gpu=gpu,child_pid=proc.pid,process_group=proc.pid,log=str(log))
        try:
            while proc.poll() is None:
                if STOP.wait(1):
                    stop_child(proc);raise RuntimeError("Stopped")
            if proc.returncode:raise RuntimeError(f"{name} exited {proc.returncode}; see {log}")
        finally:
            stop_child(proc)
            with LOCK:CHILDREN.pop(proc.pid,None)
    event(name,"complete",gpu=gpu)

def run_worker(p,gpu,start,end):
    while not STOP.is_set():
        s=subprocess.check_output(["nvidia-smi","--query-gpu=index,memory.free",
                                   "--format=csv,noheader,nounits"],text=True,timeout=20)
        free={int(a):int(b) for a,b in (x.split(",") for x in s.strip().splitlines())}
        if free[gpu]>=p["min_free_mib"]:break
        event(f"worker{gpu}","waiting_gpu",gpu=gpu,free_mib=free[gpu])
        STOP.wait(30)
    if STOP.is_set():raise RuntimeError("Stopped")
    output=HERE/f"worker{gpu}"
    assert not output.exists(),"Refusing to overwrite worker output"
    args=[PYTHON,"-B",str(HERE/"diagnose_adapter.py"),"--protocol",str(HERE/"protocol.json"),
          "--start",str(start),"--end",str(end),"--output-dir",str(output),"--device","cuda:0"]
    command(args,f"worker{gpu}",gpu)
    assert (output/"worker_done.json").is_file(),"Worker has no completion record"

def main():
    p=read(HERE/"protocol.json")
    checked=validate(p)
    if "--validate-only" in sys.argv:
        print(json.dumps(checked));return
    with (HERE/".run.lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert not (HERE/"state.json").exists(),"Refusing to overwrite earlier run"
        assert not (HERE/"worker0").exists() and not (HERE/"worker1").exists()
        STATE.update(status="running",runner_pid=os.getpid(),started_at=now(),
                     no_training=True,no_qwen=True,no_text_generation=True)
        event("pipeline","validated",**checked)
        try:
            with cf.ThreadPoolExecutor(max_workers=2) as pool:
                fs=[pool.submit(run_worker,p,0,0,250),pool.submit(run_worker,p,1,250,500)]
                for f in cf.as_completed(fs):
                    try:f.result()
                    except BaseException:STOP.set();raise
            command([PYTHON,"-B",str(HERE/"diagnose_adapter.py"),"--aggregate",str(HERE)],
                    "aggregate",None)
            assert (HERE/"summary.json").is_file() and (HERE/"SUMMARY.md").is_file()
            STATE.update(status="complete",completed_at=now())
            event("pipeline","complete",summary=str(HERE/"SUMMARY.md"))
        except BaseException as error:
            STOP.set()
            with LOCK:children=list(CHILDREN.values())
            for proc in children:stop_child(proc)
            STATE.update(status="failed",error=repr(error))
            event("pipeline","failed",error=repr(error),traceback=traceback.format_exc())
            raise

if __name__=="__main__":
    for sig in [signal.SIGTERM,signal.SIGINT]:signal.signal(sig,lambda *_:STOP.set())
    main()

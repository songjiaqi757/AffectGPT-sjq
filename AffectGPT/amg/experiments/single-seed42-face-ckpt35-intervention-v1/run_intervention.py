"""Fixed-checkpoint Memory interventions; all project artifacts remain on this server."""
from pathlib import Path
import concurrent.futures as cf
import datetime, fcntl, hashlib, json, os, signal, subprocess, sys, threading, time, traceback

ROOT = Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
HERE = Path(__file__).resolve().parent
PYTHON = "/ai/sjq/miniconda3/envs/vllm/bin/python"
sys.path.insert(0, str(ROOT))
STOP = threading.Event()
LOCK = threading.RLock()
CHILDREN = {}
STATE = {"schema": "amg-fixed-checkpoint-intervention-state-v1", "status": "preparing", "jobs": {}}

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def read(path):
    return json.loads(Path(path).read_text())

def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def save(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)

def event(mode, stage, **fields):
    item = {"timestamp": now(), "mode": mode, "stage": stage, **fields}
    with LOCK:
        STATE["updated_at"] = item["timestamp"]
        STATE["jobs"][mode] = item
        save(HERE / "state.json", STATE)
        with (HERE / "events.jsonl").open("a") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(json.dumps(item, ensure_ascii=False), flush=True)

def validate(p):
    ready = read(HERE / "READY.json")
    for path, expected in ready["locked_files"].items():
        if sha(path) != expected:
            raise ValueError("Locked input changed: " + path)
    original = read(p["original_state"])
    assert original["status"] == "complete"
    meta = read(p["normal_metadata"])
    report = read(p["normal_report"])
    assert meta["trained_mode"] == meta["memory_mode"] == "retrieval"
    assert meta["amg_sha256"] == p["amg_sha256"] == report["metadata"]["checkpoint_sha256"]
    assert meta["base_sha256"] == p["baseline_sha256"]
    assert meta["manifest_sha256"] == p["manifest_sha256"]
    assert meta["memory_sha256"] == p["bank_sha256"]
    assert sha(p["normal_predictions"]) == report["metadata"]["predictions_sha256"]
    assert sha(p["normal_metadata"]) == report["metadata"]["inference_metadata_sha256"]
    assert report["metrics"]["N"] == p["N"] == meta["selected_clips"] == 500
    assert meta["successes"] == 500 and meta["errors"] == 0
    assert meta["seed"] == p["seed"] == 42
    assert meta["decoding"] == p["decoding"]
    assert meta["infer_sha256"] == sha(ROOT / "amg/infer.py")
    return {"validated": True, "locked_files": len(ready["locked_files"]), "same_amg_sha256": p["amg_sha256"]}

def env_for(gpu=None):
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
               OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", PYTHONUNBUFFERED="1",
               CUDA_VISIBLE_DEVICES="" if gpu is None else str(gpu))
    return env

def stop_child(proc):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    except ProcessLookupError:
        pass

def command(argv, log, mode, stage, gpu=None, allowed=(0,)):
    if STOP.is_set():
        raise RuntimeError("Stopped")
    with Path(log).open("x") as out:
        out.write(json.dumps({"time": now(), "argv": argv, "gpu": gpu}) + "\n")
        out.flush()
        proc = subprocess.Popen(argv, cwd=ROOT, env=env_for(gpu), stdin=subprocess.DEVNULL,
                                stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
        with LOCK:
            CHILDREN[proc.pid] = proc
        event(mode, stage, gpu=gpu, child_pid=proc.pid, process_group=proc.pid, log=str(log))
        try:
            while proc.poll() is None:
                if STOP.wait(1):
                    stop_child(proc)
                    raise RuntimeError("Stopped")
            if proc.returncode not in allowed:
                raise RuntimeError(f"{mode} {stage} exited {proc.returncode}; see {log}")
            return proc.returncode
        finally:
            stop_child(proc)
            with LOCK:
                CHILDREN.pop(proc.pid, None)

def wait_gpu(gpu, minimum):
    while not STOP.is_set():
        output = subprocess.check_output(["nvidia-smi", "--query-gpu=index,memory.free",
                                          "--format=csv,noheader,nounits"], text=True, timeout=20)
        free = {int(a): int(b) for a,b in (line.split(",") for line in output.strip().splitlines())}
        if free[gpu] >= minimum:
            return
        event(str(gpu), "waiting_gpu", gpu=gpu, free_mib=free[gpu], required_mib=minimum)
        STOP.wait(30)
    raise RuntimeError("Stopped while waiting for GPU")

def verify_prediction(p, mode):
    directory = HERE / mode
    meta = read(directory / "dev.meta.json")
    normal = read(p["normal_metadata"])
    keys = ["amg_sha256", "base_sha256", "memory_sha256", "manifest_sha256", "trained_mode",
            "dataset", "task", "question", "seed", "face_or_frame", "prompt_sha256",
            "config_sha256", "max_length", "memory_tokens_reserved", "decoding",
            "infer_sha256", "base_dataset_sha256", "budget_source_sha256"]
    for key in keys:
        if meta.get(key) != normal.get(key):
            raise ValueError("Intervention metadata mismatch: " + key)
    assert meta["memory_mode"] == mode and meta["trained_mode"] == "retrieval"
    left, right = rows(p["normal_predictions"]), rows(directory / "dev.jsonl")
    assert len(left) == len(right) == p["N"]
    assert [r["name"] for r in left] == [r["name"] for r in right]
    budget_checked = 0
    for a,b in zip(left,right):
        assert a["group_id"] == b["group_id"]
        if "budget" in b:
            assert a["budget"] == b["budget"]
            budget_checked += 1
        trace = b.get("retrieval")
        if "error" not in b:
            assert trace is not None
            assert trace["memory_enabled"] == [mode != "off"]
            if mode == "off":
                assert trace["retrieved_ids"] is None
            else:
                fit_ids = p["_fit_ids"]
                ids = trace["retrieved_ids"][0]
                assert len(ids) == len(set(ids)) == 5
                assert all(n in fit_ids and n != b["name"] for n in ids)
    save(directory / "identity-validation.json", {"same_checkpoint": True, "same_prompt_and_policy": True,
         "same_ordered_ids": True, "budget_rows_checked": budget_checked, "N": len(right),
         "amg_sha256": p["amg_sha256"], "trained_mode": "retrieval", "memory_mode": mode})
    return meta

def run_mode(p, mode, gpu):
    wait_gpu(gpu, p["min_free_mib"])
    directory = HERE / mode
    directory.mkdir(exist_ok=False)
    argv = [PYTHON, "-B", str(HERE / "infer_with_limit.py"), "--config", p["config"],
            "--baseline-checkpoint", p["baseline_checkpoint"], "--amg-checkpoint", p["amg_checkpoint"],
            "--memory-bank", p["memory_bank"], "--manifest", p["manifest"],
            "--output", str(directory / "dev.jsonl"), "--device", "cuda:0", "--dataset", "MERCaptionPlus",
            "--memory-mode", mode, "--task", "ovlabel", "--max-new-tokens", "128", "--seed", "42"]
    rc = command(argv, HERE / (mode + "-infer.log"), mode, "generating", gpu, allowed=(0,1))
    meta = verify_prediction(p, mode)
    argv = [PYTHON, "-B", "-m", "amg.evaluate", "--manifest", p["manifest"], "--split", "dev",
            "--predictions", str(directory / "dev.jsonl"), "--resource", p["resource"],
            "--output", str(directory / "dev.metrics.json")]
    command(argv, HERE / (mode + "-evaluate.log"), mode, "scoring")
    report = read(directory / "dev.metrics.json")
    assert report["metrics"]["N"] == 500
    event(mode, "complete", gpu=gpu, inference_returncode=rc, successes=meta["successes"],
          errors=meta["errors"], micro_f1=report["metrics"]["micro_f1"])
    return report

def comparisons(p, reports):
    from amg.evaluate import paired_comparison
    directory = HERE / "paired"
    directory.mkdir(exist_ok=False)
    def one(left, right):
        result = paired_comparison(reports[left], reports[right], resamples=1000, bootstrap_seed=42)
        a,b = reports[left]["metadata"], reports[right]["metadata"]
        assert a["checkpoint_sha256"] == b["checkpoint_sha256"] == p["amg_sha256"]
        assert a["trained_mode"] == b["trained_mode"] == "retrieval"
        left_rows = {r["name"]: r for r in reports[left]["per_clip"]}
        right_rows = {r["name"]: r for r in reports[right]["per_clip"]}
        result.update(left_mode=left, right_mode=right, trained_mode="retrieval",
                      checkpoint_sha256=p["amg_sha256"],
                      identical_label_sets=sum(left_rows[k]["prediction_labels"] == right_rows[k]["prediction_labels"] for k in left_rows),
                      identical_prediction_text=sum(left_rows[k]["prediction"] == right_rows[k]["prediction"] for k in left_rows))
        save(directory / (left + "-vs-" + right + ".json"), result)
        return left + "-vs-" + right, result
    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(one,*pair) for pair in [("retrieval","off"),("retrieval","random"),("random","off")]]
        results = dict(f.result() for f in cf.as_completed(futures))
    output = {"schema":"amg-fixed-checkpoint-intervention-results-v1", "completed_at":now(),
              "checkpoint":p["amg_checkpoint"], "checkpoint_sha256":p["amg_sha256"],
              "trained_mode":"retrieval", "seed":42, "development_only":True,
              "normal_predictions_reused":p["normal_predictions"],
              "metrics":{k:r["metrics"] for k,r in reports.items()}, "comparisons":results,
              "limitations":["Single trained seed; bootstrap measures sample uncertainty",
              "Baseline supervised on all source clips", "No holdout or target evaluation",
              "Off removes inserted tokens; random retains token count while changing content",
              "Interventions assess the trained retrieval model, not the value of retraining other modes"]}
    save(HERE / "summary.json", output)
    lines = ["# Fixed-checkpoint Memory interventions", "",
             "All variants use the same retrieval-trained checkpoint, seed 42 and 500 source dev clips.",
             "Normal retrieval predictions were reused after hash validation; no retraining.", "",
             "|Memory mode|micro-F1|sample macro-F1|Failed|",
             "|---|---:|---:|---:|"]
    for k in ["retrieval","off","random"]:
        m=reports[k]["metrics"]
        lines.append(f"|{k}|{m['micro_f1']:.6f}|{m['sample_macro_f1']:.6f}|{m['failed_predictions']}|")
    lines.extend(["", "|Left minus right|micro-F1 delta|95% paired interval|Same label sets|",
                  "|---|---:|---|---:|"])
    for k,v in sorted(results.items()):
        ci=v["bootstrap"]["intervals"]["micro_f1"]
        lines.append(f"|{k}|{v['delta']['micro_f1']:.6f}|[{ci[0]:.6f}, {ci[1]:.6f}]|{v['identical_label_sets']}/500|")
    lines.extend(["", "Intervals use 1,000 paired group bootstrap resamples; current group IDs are clip IDs.",
                  "These are source development normalized label-set scores, not paper EW or target scores.",
                  "Interpret with cpu-diagnostics/ and the separate five-method training experiment."])
    (HERE / "SUMMARY.md").write_text("\n".join(lines)+"\n")
    return output

def main():
    p=read(HERE / "protocol.json")
    checked=validate(p)
    if "--validate-only" in sys.argv:
        print(json.dumps(checked)); return
    with (HERE / ".run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not (HERE / "state.json").exists(), "Refusing to overwrite an earlier run"
        for name in ["off","random"]:
            assert not (HERE / name).exists(), "Refusing to overwrite intervention output"
        STATE.update(status="running",started_at=now(),runner_pid=os.getpid(),
                     checkpoint_sha256=p["amg_sha256"], trained_mode="retrieval",gpus={"off":0,"random":1})
        event("pipeline","validated",**checked)
        p["_fit_ids"]={r["name"] for r in rows(p["fit_manifest"])}
        assert len(p["_fit_ids"])==4000
        reports={"retrieval":read(p["normal_report"])}
        try:
            with cf.ThreadPoolExecutor(max_workers=2) as pool:
                futures={pool.submit(run_mode,p,mode,gpu):mode for mode,gpu in [("off",0),("random",1)]}
                for future in cf.as_completed(futures):
                    try:
                        reports[futures[future]]=future.result()
                    except BaseException:
                        STOP.set()
                        raise
            comparisons(p,reports)
            STATE.update(status="complete",completed_at=now())
            event("pipeline","complete",summary=str(HERE/"SUMMARY.md"),paired_comparisons=3)
        except BaseException as error:
            STOP.set()
            with LOCK:
                children=list(CHILDREN.values())
            for proc in children:
                stop_child(proc)
            STATE.update(status="failed",error=repr(error))
            event("pipeline","failed",error=repr(error),traceback=traceback.format_exc())
            raise

if __name__=="__main__":
    for sig in [signal.SIGTERM,signal.SIGINT]:
        signal.signal(sig,lambda *_:STOP.set())
    main()

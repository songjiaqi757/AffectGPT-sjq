"""Server-only, provenance-locked M0 experiment with two independent GPU workers.

Run from the project root with --protocol ABSOLUTE_JSON --output-dir ABSOLUTE_DIR.
The output directory must contain READY.json and no existing state.json. Each GPU
runs one method's training and generation at a time. Paired scoring starts only
after all methods have generated and received a full-denominator dev score.
"""
from __future__ import annotations

import argparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

PROJECT = Path(__file__).resolve().parents[1]
METHODS = ("off", "retrieval", "learned", "current", "random")
DEFAULT_PYTHON = "/ai/sjq/miniconda3/envs/vllm/bin/python"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def absolute(value, label):
    path = Path(value)
    if not path.is_absolute():
        raise ValueError(label + " must be an absolute server path")
    return path.resolve()


def run_gpu_queue(methods, gpus, run_job, stop_event, on_failure=lambda: None):
    """Assign the first job to the first GPU, then share a bounded work queue.

    A GPU worker cannot obtain its next method until run_job has returned.
    Exceptions cancel queued work and invoke cleanup before waiting for workers.
    This also makes retrieval finishing before off safe: no paired work is here.
    """
    methods, gpus = tuple(methods), tuple(gpus)
    if len(gpus) != 2 or len(set(gpus)) != 2:
        raise ValueError("Exactly two distinct GPU IDs are required")
    if len(methods) < len(gpus) or len(set(methods)) != len(methods):
        raise ValueError("A unique initial method is required for each GPU")
    pending = deque(methods[len(gpus):])
    lock = threading.Lock()

    def worker(gpu, first):
        mode = first
        while mode is not None:
            if stop_event.is_set():
                return
            try:
                run_job(mode, gpu)
            except BaseException:
                stop_event.set()
                on_failure()
                raise
            with lock:
                mode = pending.popleft() if pending and not stop_event.is_set() else None

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="amg-gpu") as pool:
        jobs = [pool.submit(worker, gpu, methods[index]) for index, gpu in enumerate(gpus)]
        for job in as_completed(jobs):
            job.result()
    if stop_event.is_set():
        raise InterruptedError("GPU queue cancelled")


def require_comparison_inputs(output, methods):
    """Check every dependency before any paired scorer or exposure reader runs."""
    for mode in methods:
        for name in ("coverage.json", "exposure.jsonl", "dev.metrics.json"):
            path = Path(output) / mode / name
            if not path.is_file():
                raise RuntimeError(f"Paired comparison requires completed {mode}: {path}")


def exposure_signature(path):
    digest, count = hashlib.sha256(), 0
    with Path(path).open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            selected = {"iteration": row["iteration"], "microstep": row["microstep"],
                        "examples": [{key: item[key] for key in
                            ("requested_clip_id", "actual_clip_id", "task_type", "budget")}
                            for item in row["examples"]]}
            count += len(selected["examples"])
            digest.update(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode())
    return digest.hexdigest(), count


def compare_exposure(output, mode):
    output = Path(output)
    reference, reference_count = exposure_signature(output / "off/exposure.jsonl")
    actual, count = exposure_signature(output / mode / "exposure.jsonl")
    record = {"schema": "amg-paired-exposure-v1", "baseline": "off", "method": mode,
              "examples": count, "baseline_examples": reference_count,
              "actual_sha256": actual, "baseline_sha256": reference,
              "identical_requested_actual_task_and_budget": actual == reference and count == reference_count,
              "ignored_fields": ["memory_enabled", "actual_inserted_input_length", "timing"]}
    write_json(output / mode / "exposure-alignment.json", record)
    if not record["identical_requested_actual_task_and_budget"]:
        raise RuntimeError(f"Exposure mismatch for {mode}: results cannot be attributed directly to Memory")
    return record


def first_five_validation(path):
    """Inspect real training telemetry; no extra preflight model is trained."""
    rows = []
    with Path(path).open(encoding="utf-8") as stream:
        for line in stream:
            if len(rows) == 5:
                break
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                break  # The training process may still be appending the last line.
            rows.append(row)
    if len(rows) < 5:
        return None
    if [row["iteration"] for row in rows] != list(range(1, 6)):
        raise RuntimeError("First five training iterations are missing or out of order")
    if any(not math.isfinite(float(row["loss"])) for row in rows):
        raise RuntimeError("Nonfinite loss in the first five real training iterations")
    attempts, updates = [row["optimizer_attempts"] for row in rows], [row["optimizer_updates"] for row in rows]
    if any(not isinstance(value, int) or value < 0 for value in attempts + updates):
        raise RuntimeError("Invalid real optimizer telemetry")
    if attempts != sorted(attempts) or updates != sorted(updates):
        raise RuntimeError("Optimizer telemetry must be cumulative")
    if any(update > attempt for update, attempt in zip(updates, attempts)) or updates[-1] < 1:
        raise RuntimeError("No successful optimizer update within the first five iterations")
    return {"schema": "amg-first-five-training-validation-v1", "recorded_at": now(),
            "all_losses_finite": True, "optimizer_attempts": attempts[-1],
            "optimizer_updates": updates[-1], "rows": rows,
            "amp_overflow_iterations": [row["iteration"] for row in rows if row.get("amp_overflow")],
            "gradient_nonfinite_iterations": [row["iteration"] for row in rows if row.get("grad_norm_nonfinite")],
            "policy": "AMP may skip overflowing updates; at least one real update and five finite losses required"}


class Experiment:
    def __init__(self, protocol_path, output_dir, *, python=DEFAULT_PYTHON):
        self.protocol_path = absolute(protocol_path, "protocol")
        self.output = absolute(output_dir, "output-dir")
        if self.output == PROJECT / "output" or PROJECT / "output" in self.output.parents:
            raise ValueError("AMG experiments must be outside the original training output tree")
        self.protocol = read_json(self.protocol_path)
        self.python = str(absolute(python, "python"))
        self.stop_event = threading.Event()
        self.lock = threading.RLock()
        self.children = {}
        self.interrupted_signal = None
        self.state = {"schema": "amg-single-seed-run-state-v2", "started_at": now(),
                      "runner_pid": os.getpid(), "seed": self.protocol.get("seed"),
                      "protocol": str(self.protocol_path), "status": "preparing", "methods": {}}
        schedule = self.protocol.get("scheduling", {})
        self.gpus = tuple(schedule.get("gpus", [0, 1]))
        self.min_free_mib = int(schedule.get("min_free_mib", 32000))
        self.poll_seconds = float(schedule.get("poll_seconds", 30))
        self.cpu_workers = int(schedule.get("cpu_workers", 2))
        self.bank_metadata = None

    def event(self, mode, stage, **extra):
        with self.lock:
            event = {"timestamp": now(), "pid": os.getpid(), "method": mode, "stage": stage, **extra}
            previous = self.state["methods"].get(mode, {})
            self.state["methods"][mode] = {**previous, **event}
            self.state["updated_at"] = event["timestamp"]
            write_json(self.output / "state.json", self.state)
            with (self.output / "events.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, ensure_ascii=False) + "\n")
            print(json.dumps(event, ensure_ascii=False), flush=True)

    def stop_children(self):
        """Signal only process groups created by this runner, never other runs."""
        self.stop_event.set()
        with self.lock:
            active = list(self.children.values())
        for proc in active:
            if proc.poll() is None:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass

    def signal_handler(self, signum, _frame):
        self.interrupted_signal = signum
        self.stop_children()

    def check_cancelled(self):
        if self.stop_event.is_set():
            raise InterruptedError("Experiment interrupted or another method failed")

    def validate(self):
        p, t = self.protocol, self.protocol["training"]
        if p.get("seed") != 42 or tuple(p.get("methods", [])) != METHODS:
            raise ValueError("This experiment requires seed 42 and off/retrieval/learned/current/random in order")
        if self.gpus != (0, 1) or p.get("max_concurrent_new_gpu_jobs", 2) != 2:
            raise ValueError("This experiment is locked to two workers on physical GPUs 0 and 1")
        if self.cpu_workers != 2 or self.min_free_mib < 32000 or self.poll_seconds <= 0:
            raise ValueError("Require two CPU workers, >=32000 MiB free per GPU, and positive poll interval")
        expected = {"iterations": 1334, "batch_size": 1, "grad_accum": 3,
                    "nominal_examples": 4002, "num_tokens": 4, "train_peft": True}
        if any(t.get(key) != value for key, value in expected.items()):
            raise ValueError("Training budget or PEFT setting differs from the fixed single-seed protocol")
        if float(t.get("cuda_memory_fraction", 0)) != 0.35:
            raise ValueError("Each new GPU process requires a 0.35 CUDA allocator fraction")
        if t["hidden_dim"] <= 0 or t["workers"] < 0 or t["lr"] <= 0 or not 0 <= t["memory_dropout"] < 1:
            raise ValueError("Invalid training hyperparameters")
        if p["generation"].get("do_sample") is not False or p["generation"].get("num_beams") != 1:
            raise ValueError("Generation must remain deterministic greedy decoding")
        if p["generation"].get("seed", 42) != p["seed"]:
            raise ValueError("Generation and training seeds differ")
        required = {self.protocol_path, Path(__file__).resolve()}
        for key in ("baseline_checkpoint", "config", "memory_bank", "evaluation_resource"):
            required.add(absolute(p[key], key))
        for split in ("fit", "dev", "holdout"):
            required.add(absolute(p["splits"][split]["path"], split))
        bank_path = Path(p["memory_bank"])
        required.add(Path(str(bank_path) + ".json"))
        required.update(PROJECT.joinpath("amg").glob("*.py"))
        required.update(PROJECT / relative for relative in (
            "config.py", "my_affectgpt/models/affectgpt.py", "my_affectgpt/models/encoder.py",
            "my_affectgpt/datasets/datasets/base_dataset.py", "my_affectgpt/datasets/datasets/mercaptionplus_dataset.py"))
        ready = read_json(self.output / "READY.json")
        locked = ready.get("locked_files", {})
        if not required.issubset({Path(path) for path in locked}):
            missing = sorted(str(path) for path in required if str(path) not in locked)
            raise ValueError("READY must lock all protocol/data/source/baseline/bank artifacts: " + repr(missing))
        actual = {}
        for path, digest in locked.items():
            absolute(path, "READY artifact")
            if not isinstance(digest, str) or len(digest) != 64:
                raise ValueError("Invalid READY artifact SHA256: " + path)
            actual[path] = sha(path)
            if actual[path] != digest:
                raise RuntimeError("Locked artifact changed: " + path)
        if actual[p["baseline_checkpoint"]] != p["baseline_sha256"]:
            raise RuntimeError("Baseline differs from the protocol SHA256")
        from .manifest import read_manifest
        used_ids, used_groups = set(), set()
        for split, expected_count in (("fit", 4000), ("dev", 500), ("holdout", 500)):
            declaration = p["splits"][split]
            if actual[declaration["path"]] != declaration["sha256"]:
                raise RuntimeError("Split manifest differs from locked protocol: " + split)
            records = read_manifest(declaration["path"])
            ids, groups = {row["name"] for row in records}, {row["group_id"] for row in records}
            if len(records) != expected_count or used_ids & ids or used_groups & groups:
                raise RuntimeError("Split count or clip/group separation differs from protocol: " + split)
            used_ids.update(ids)
            used_groups.update(groups)
        bank = read_json(str(bank_path) + ".json")
        if (bank.get("schema") != "amg-m0-bank-v1" or bank.get("complete") is not True
                or bank.get("partial_for_testing") is not False
                or bank.get("records") != 4000 or bank.get("total_manifest_records") != 4000):
            raise RuntimeError("A complete 4000-record fit Memory bank is required; partial banks are refused")
        if Path(bank["manifest_path"]).resolve() != Path(p["splits"]["fit"]["path"]).resolve():
            raise RuntimeError("Memory bank was built from a different manifest path")
        if bank["manifest_sha256"] != p["splits"]["fit"]["sha256"]:
            raise RuntimeError("Memory bank was built from a different manifest SHA256")
        if bank["bank_sha256"] != actual[str(bank_path)]:
            raise RuntimeError("Memory bank bytes differ from the locked metadata")
        if bank["config_sha256"] != actual[p["config"]]:
            raise RuntimeError("Memory feature configuration differs from experiment configuration")
        version_material = {key: value for key, value in bank.items()
                            if key not in {"version", "bank_sha256", "created_at"}}
        version = "amg-m0-" + hashlib.sha256(json.dumps(version_material, sort_keys=True).encode()).hexdigest()
        if bank["version"] != version:
            raise RuntimeError("Memory version does not describe its locked metadata")
        for key, value in (("memory_bank_sha256", bank["bank_sha256"]), ("memory_bank_version", version)):
            if key in p and p[key] != value:
                raise RuntimeError("Memory differs from protocol " + key)
        self.bank_metadata = bank
        self.state.update(protocol_sha256=actual[str(self.protocol_path)],
                          baseline_checkpoint=p["baseline_checkpoint"], baseline_sha256=p["baseline_sha256"],
                          memory_bank_sha256=bank["bank_sha256"], memory_bank_version=version,
                          gpus=list(self.gpus), max_concurrent_new_gpu_jobs=2)
        return {"validated": True, "locked_files": len(locked), "baseline_sha256": p["baseline_sha256"],
                "memory_bank_version": version, "gpus": list(self.gpus)}

    def wait_gpu(self, gpu, mode):
        while True:
            self.check_cancelled()
            output = subprocess.check_output(["nvidia-smi", f"--id={gpu}",
                "--query-gpu=memory.free", "--format=csv,noheader,nounits"], text=True, timeout=30)
            free = int(output.strip())
            if free >= self.min_free_mib:
                return
            self.event(mode, "waiting_for_memory", gpu=gpu, free_mib=free, required_mib=self.min_free_mib)
            self.stop_event.wait(self.poll_seconds)

    @staticmethod
    def terminate_group(proc):
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=15)

    def execute(self, args, log_path, *, mode, stage, gpu=None, allowed=(0,), monitor=None):
        self.check_cancelled()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1",
                   TRANSFORMERS_OFFLINE="1", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", PYTHONUNBUFFERED="1")
        env["CUDA_VISIBLE_DEVICES"] = "" if gpu is None else str(gpu)
        proc = None
        with Path(log_path).open("x", encoding="utf-8") as stream:
            stream.write(json.dumps({"timestamp": now(), "runner_pid": os.getpid(), "gpu": gpu,
                                     "method": mode, "stage": stage, "argv": args}, ensure_ascii=False) + "\n")
            stream.flush()
            try:
                with self.lock:
                    self.check_cancelled()
                    proc = subprocess.Popen(args, cwd=PROJECT, env=env, stdout=stream,
                                            stderr=subprocess.STDOUT, start_new_session=True)
                    self.children[proc.pid] = proc
                self.event(mode, stage, gpu=gpu, child_pid=proc.pid, process_group=proc.pid, log=str(log_path))
                while proc.poll() is None:
                    self.check_cancelled()
                    if monitor is not None:
                        monitor()
                    self.stop_event.wait(1)
                self.check_cancelled()
                if monitor is not None:
                    monitor()
                rc = proc.returncode
                if rc not in allowed:
                    raise RuntimeError(f"{mode} {stage} failed rc={rc}; see {log_path}")
                stream.write(json.dumps({"timestamp": now(), "child_pid": proc.pid, "returncode": rc}) + "\n")
                stream.flush()
                return rc
            finally:
                if proc is not None:
                    self.terminate_group(proc)
                    with self.lock:
                        self.children.pop(proc.pid, None)

    def train_args(self, mode, output):
        p, t = self.protocol, self.protocol["training"]
        return [self.python, "-B", "-m", "amg.train", "--config", p["config"],
                "--baseline-checkpoint", p["baseline_checkpoint"], "--manifest", p["splits"]["fit"]["path"],
                "--memory-bank", p["memory_bank"], "--output-dir", str(output), "--mode", mode,
                "--steps", str(t["iterations"]), "--batch-size", str(t["batch_size"]),
                "--grad-accum", str(t["grad_accum"]), "--seed", str(p["seed"]),
                "--lr", str(t["lr"]), "--weight-decay", str(t["weight_decay"]),
                "--memory-dropout", str(t["memory_dropout"]), "--num-tokens", str(t["num_tokens"]),
                "--hidden-dim", str(t["hidden_dim"]), "--workers", str(t["workers"]),
                "--save-every", str(t["iterations"]), "--log-every", "25", "--device", "cuda:0",
                "--cuda-memory-fraction", str(t["cuda_memory_fraction"])]

    def infer_args(self, checkpoint, output):
        p, generation = self.protocol, self.protocol["generation"]
        fraction = float(p["training"]["cuda_memory_fraction"])
        wrapper = (f"import torch,runpy; torch.cuda.set_per_process_memory_fraction({fraction!r},0); "
                   "runpy.run_module('amg.infer',run_name='__main__')")
        return [self.python, "-B", "-c", wrapper, "--config", p["config"],
                "--baseline-checkpoint", p["baseline_checkpoint"], "--amg-checkpoint", str(checkpoint),
                "--memory-bank", p["memory_bank"], "--manifest", p["splits"]["dev"]["path"],
                "--output", str(output), "--device", "cuda:0", "--task", generation["task"],
                "--max-new-tokens", str(generation["max_new_tokens"]), "--seed", str(p["seed"])]

    def score_args(self, mode, paired=None):
        p, run = self.protocol, self.output / mode
        suffix = "" if paired is None else ".vs-" + paired
        args = [self.python, "-B", "-m", "amg.evaluate", "--manifest", p["splits"]["dev"]["path"],
                "--split", "dev", "--task", p["generation"]["task"], "--resource", p["evaluation_resource"],
                "--predictions", str(run / "dev.jsonl"), "--output", str(run / f"dev{suffix}.metrics.json")]
        if paired is not None:
            args += ["--paired-report", str(self.output / paired / "dev.metrics.json"),
                     "--bootstrap-seed", str(p["seed"]), "--bootstrap-resamples", "1000"]
        return args

    def validate_training(self, mode, output):
        p, t = self.protocol, self.protocol["training"]
        coverage, config = read_json(output / "coverage.json"), read_json(output / "config.json")
        if (coverage["completed_iterations"] != t["iterations"]
                or coverage["examples"] != t["nominal_examples"] or coverage["missing_actual_ids"]
                or coverage["actual_covered_ids"] != 4000 or coverage["optimizer_updates"] < 1):
            raise RuntimeError(f"{mode}: actual training budget/coverage differs from locked protocol")
        expected = {"mode": mode, "base_checkpoint": p["baseline_checkpoint"], "base_sha256": p["baseline_sha256"],
                    "memory_sha256": self.bank_metadata["bank_sha256"], "memory_version": self.bank_metadata["version"],
                    "manifest_sha256": p["splits"]["fit"]["sha256"], "seed": p["seed"], "allow_partial_bank": False}
        if any(config.get(key) != value for key, value in expected.items()):
            raise RuntimeError(f"{mode}: saved training configuration differs from locked provenance")
        audit = coverage["parameter_changes"]
        if not audit["all_finite"]:
            raise RuntimeError(f"{mode}: nonfinite parameter values or parameter changes")
        required_groups = ["lora"] + (["memory_adapter"] if mode in {"retrieval", "random", "current"}
                                      else ["learned_tokens"] if mode == "learned" else [])
        if any(audit["groups"][group]["changed_tensors"] < 1 for group in required_groups):
            raise RuntimeError(f"{mode}: expected trainable parameter group did not change")
        return coverage

    def validate_score(self, mode, report_path):
        report = read_json(report_path)
        metadata = report["metadata"]
        with Path(self.protocol["splits"]["dev"]["path"]).open(encoding="utf-8") as manifest:
            expected_count = sum(bool(line.strip()) for line in manifest)
        if report["metrics"]["N"] != expected_count or len(report["per_clip"]) != expected_count:
            raise RuntimeError(f"{mode}: score did not retain the full dev denominator")
        if metadata["base_checkpoint_sha256"] != self.protocol["baseline_sha256"]:
            raise RuntimeError(f"{mode}: score used a different baseline checkpoint")
        if metadata.get("trained_mode") != mode or metadata.get("memory_mode") != mode:
            raise RuntimeError(f"{mode}: scoring mode differs from its trained method")
        return report

    def run_method(self, mode, gpu):
        output = self.output / mode
        early_written = False

        def monitor():
            nonlocal early_written
            path = output / "train.jsonl"
            if not early_written and path.is_file():
                record = first_five_validation(path)
                if record is not None:
                    write_json(output / "first-five-validation.json", record)
                    early_written = True
                    self.event(mode, "training", gpu=gpu, first_five_finite=True,
                               first_five_optimizer_updates=record["optimizer_updates"])
        try:
            self.wait_gpu(gpu, mode)
            self.execute(self.train_args(mode, output), self.output / f"{mode}-train.log",
                         mode=mode, stage="training", gpu=gpu, monitor=monitor)
            if not early_written:
                raise RuntimeError(f"{mode}: missing first-five training validation")
            coverage = self.validate_training(mode, output)
            self.event(mode, "train_complete", gpu=gpu, optimizer_updates=coverage["optimizer_updates"],
                       covered=coverage["actual_covered_ids"], actual_exposures=coverage["examples"])
            checkpoint = output / f"checkpoint_{self.protocol['training']['iterations']:06d}.pth"
            if not checkpoint.is_file():
                raise RuntimeError(f"{mode}: missing final locked checkpoint")
            self.wait_gpu(gpu, mode)
            rc = self.execute(self.infer_args(checkpoint, output / "dev.jsonl"),
                              self.output / f"{mode}-infer.log", mode=mode, stage="generating_dev",
                              gpu=gpu, allowed=(0, 1))
            # rc=1 denotes reported per-clip generation failures. The scorer must
            # still receive every manifest row and charge failures in the denominator.
            self.event(mode, "generation_complete", gpu=gpu, inference_returncode=rc)
            self.execute(self.score_args(mode), self.output / f"{mode}-evaluate.log",
                         mode=mode, stage="scoring_dev")
            self.validate_score(mode, output / "dev.metrics.json")
            self.event(mode, "complete", gpu=gpu, metrics_path=str(output / "dev.metrics.json"),
                       completed_at=now())
        except BaseException as error:
            self.event(mode, "cancelled" if self.stop_event.is_set() else "failed", gpu=gpu,
                       error=f"{type(error).__name__}: {error}")
            raise

    def paired_phase(self):
        require_comparison_inputs(self.output, METHODS)
        for mode in METHODS:
            if self.state["methods"].get(mode, {}).get("stage") != "complete":
                raise RuntimeError("Paired scoring cannot run with an incomplete or failed method: " + mode)
        self.event("paired", "checking_exposure")
        with ThreadPoolExecutor(max_workers=self.cpu_workers, thread_name_prefix="amg-exposure") as pool:
            jobs = [pool.submit(compare_exposure, self.output, mode) for mode in METHODS if mode != "off"]
            for job in as_completed(jobs):
                alignment = job.result()
                if alignment["examples"] != self.protocol["training"]["nominal_examples"]:
                    raise RuntimeError("Exposure log count differs from the locked actual exposure budget")
        pairs = [(mode, "off") for mode in METHODS if mode != "off"]
        pairs += [("retrieval", baseline) for baseline in ("random", "current", "learned")]
        self.event("paired", "scoring", cpu_workers=self.cpu_workers, comparisons=len(pairs))

        def score_pair(pair):
            mode, baseline = pair
            self.execute(self.score_args(mode, baseline), self.output / f"{mode}-vs-{baseline}.log",
                         mode="paired-" + mode + "-vs-" + baseline, stage="paired_scoring")
            report = self.validate_score(mode, self.output / mode / f"dev.vs-{baseline}.metrics.json")
            if report["paired"]["N"] != report["metrics"]["N"]:
                raise RuntimeError("Paired comparison denominator differs from dev report")
        with ThreadPoolExecutor(max_workers=self.cpu_workers, thread_name_prefix="amg-paired") as pool:
            jobs = [pool.submit(score_pair, pair) for pair in pairs]
            try:
                for job in as_completed(jobs):
                    job.result()
            except BaseException:
                self.stop_children()
                for job in jobs:
                    job.cancel()
                raise
        self.event("paired", "complete", comparisons=len(pairs))

    def write_summary(self):
        methods = []
        for mode in METHODS:
            run = self.output / mode
            report, coverage, config = (read_json(run / name) for name in
                                        ("dev.metrics.json", "coverage.json", "config.json"))
            methods.append({"mode": mode, "metrics": report["metrics"],
                            "trainable_parameters": config["trainable_parameters"],
                            "actual_exposures": coverage["examples"], "covered_ids": coverage["actual_covered_ids"],
                            "optimizer_updates": coverage["optimizer_updates"],
                            "parameter_changes": coverage["parameter_changes"], "resources": coverage.get("resources", {}),
                            "report": str(run / "dev.metrics.json"),
                            "first_five_validation": str(run / "first-five-validation.json")})
        comparisons = {baseline: read_json(self.output / "retrieval" / f"dev.vs-{baseline}.metrics.json")["paired"]
                       for baseline in ("off", "random", "current", "learned")}
        result = {"schema": "amg-single-seed-result-v2", "seed": self.protocol["seed"],
                  "development_only": True, "metric_is_paper_ew": False,
                  "baseline_checkpoint": self.protocol["baseline_checkpoint"],
                  "baseline_sha256": self.protocol["baseline_sha256"],
                  "memory_bank_sha256": self.bank_metadata["bank_sha256"],
                  "memory_bank_version": self.bank_metadata["version"],
                  "gpus": list(self.gpus), "max_concurrent_new_gpu_jobs": 2,
                  "methods": methods, "retrieval_comparisons": comparisons,
                  "limitations": ["Single seed: no estimate of training-seed variance",
                      "Shared baseline was already supervised on all 31K source clips",
                      "Current source groups are clip IDs; no complete near-duplicate audit",
                      "Source normalized-label F1 differs from nine-benchmark EW",
                      "No target evaluation and no holdout-based tuning were performed"],
                  "protocol_sha256": sha(self.protocol_path), "completed_at": now()}
        write_json(self.output / "summary.json", result)
        lines = ["# Single-seed M0 source development results", "",
                 f"Seed {self.protocol['seed']}; GPUs 0/1; fit 4000, dev 500; fixed final checkpoint.", "",
                 "Baseline: " + self.protocol["baseline_checkpoint"],
                 "Baseline SHA256: " + self.protocol["baseline_sha256"], "",
                 "|Method|microF1|sample macroF1|Failed|Unmapped clips|Exposure|Covered IDs|Optimizer updates|",
                 "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for row in methods:
            metrics = row["metrics"]
            lines.append(f"|{row['mode']}|{metrics['micro_f1']:.6f}|{metrics['sample_macro_f1']:.6f}|"
                         f"{metrics['failed_predictions']}|{metrics['unmapped_prediction_clips']}|"
                         f"{row['actual_exposures']}|{row['covered_ids']}|{row['optimizer_updates']}|")
        lines += ["", "|Retrieval minus baseline|microF1 delta|95% paired group interval|Negative per-clip gain fraction|",
                  "|---|---:|---|---:|"]
        for baseline, comparison in comparisons.items():
            lines.append(f"|{baseline}|{comparison['delta']['micro_f1']:.6f}|"
                         f"{comparison['bootstrap']['intervals']['micro_f1']}|"
                         f"{comparison['negative_gain_fraction']:.4f}|")
        lines += ["", "These source normalized open-label-set scores are exploratory and differ from paper EW.",
                  "Bootstrap describes sample uncertainty for this seed. The shared baseline had supervision on all 31K source clips.",
                  "Exposure alignment passed for requested IDs, actual IDs, task types and budgets. group_id is currently clip ID.",
                  "All prediction failures remain in the full dev denominator. Holdout and target sets remain unscored."]
        (self.output / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run(self):
        self.validate()
        self.state["status"] = "running"
        self.event("pipeline", "running", note="Two GPU workers; no extra real-model preflight")
        try:
            run_gpu_queue(METHODS, self.gpus, self.run_method, self.stop_event, self.stop_children)
            self.paired_phase()
            self.write_summary()
            self.state["status"] = "complete"
            self.state["completed_at"] = now()
            self.event("pipeline", "complete", summary=str(self.output / "SUMMARY.md"))
        except BaseException as error:
            self.stop_children()
            self.state["status"] = "interrupted" if self.interrupted_signal else "failed"
            self.state["failed_at"] = now()
            self.event("pipeline", self.state["status"], error=f"{type(error).__name__}: {error}")
            raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--python", default=DEFAULT_PYTHON)
    parser.add_argument("--validate-only", action="store_true", help="Verify READY hashes; never load a GPU model")
    args = parser.parse_args(argv)
    experiment = Experiment(args.protocol, args.output_dir, python=args.python)
    if args.validate_only:
        print(json.dumps(experiment.validate(), ensure_ascii=False), flush=True)
        return 0
    experiment.output.mkdir(parents=True, exist_ok=True)
    with (experiment.output / ".run.lock").open("a") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Another runner owns this output directory") from error
        if (experiment.output / "state.json").exists():
            raise RuntimeError("Refusing to reuse an experiment directory with existing state.json")
        handlers = {number: signal.getsignal(number) for number in (signal.SIGTERM, signal.SIGINT)}
        for number in handlers:
            signal.signal(number, experiment.signal_handler)
        try:
            experiment.run()
        except InterruptedError:
            if experiment.interrupted_signal:
                return 128 + experiment.interrupted_signal
            raise
        finally:
            experiment.stop_children()
            for number, handler in handlers.items():
                signal.signal(number, handler)
    return 0


if __name__ == "__main__":
    sys.exit(main())

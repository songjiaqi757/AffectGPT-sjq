"""CPU-only concurrency, provenance, dependency and child-cleanup regressions."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

from amg import run_experiment as runner


def dump(path, value):
    Path(path).write_text(json.dumps(value), encoding="utf-8")


def telemetry(step, *, loss=1.0, updates=None, overflow=False):
    return {"iteration": step, "loss": loss, "optimizer_attempts": step,
            "optimizer_updates": step if updates is None else updates,
            "amp_overflow": overflow, "grad_norm_nonfinite": overflow,
            "grad_norm": None if overflow else 0.1, "no_update": overflow}


class SchedulerTests(unittest.TestCase):
    def test_two_workers_distinct_gpu_and_dynamic_next_job(self):
        lock, first_jobs = threading.Lock(), threading.Barrier(2)
        active, peak, calls, records = {}, [0], [], []
        learned_started, retrieval_done = threading.Event(), threading.Event()

        def job(mode, gpu):
            with lock:
                self.assertNotIn(gpu, active)
                active[gpu] = mode
                peak[0] = max(peak[0], len(active))
                calls.append((mode, gpu))
            if mode in ("off", "retrieval"):
                first_jobs.wait(timeout=3)
            if mode == "off":
                self.assertTrue(learned_started.wait(timeout=3))
            if mode == "learned":
                self.assertTrue(retrieval_done.is_set())
                learned_started.set()
            for stage in ("train", "infer", "score"):
                with lock:
                    records.append((mode, gpu, stage))
                time.sleep(.004)
            if mode == "retrieval":
                retrieval_done.set()
            with lock:
                del active[gpu]
        runner.run_gpu_queue(runner.METHODS, (0, 1), job, threading.Event())
        self.assertEqual(peak[0], 2)
        self.assertEqual(set(calls[:2]), {("off", 0), ("retrieval", 1)})
        self.assertIn(("learned", 1), calls)
        self.assertEqual({mode for mode, _ in calls}, set(runner.METHODS))
        for mode in runner.METHODS:
            self.assertEqual([stage for name, _, stage in records if name == mode], ["train", "infer", "score"])
        self.assertEqual(active, {})

    def test_failure_cancels_remaining_and_calls_cleanup(self):
        barrier, stop, cleanup = threading.Barrier(2), threading.Event(), Mock()
        calls = []

        def job(mode, gpu):
            calls.append(mode)
            barrier.wait(timeout=3)
            if mode == "retrieval":
                raise RuntimeError("training failed")
            self.assertTrue(stop.wait(timeout=3))
        with self.assertRaisesRegex(RuntimeError, "training failed"):
            runner.run_gpu_queue(runner.METHODS, (0, 1), job, stop, cleanup)
        cleanup.assert_called_once_with()
        self.assertEqual(set(calls), {"off", "retrieval"})
        self.assertTrue(stop.is_set())

    def test_duplicate_gpu_rejected(self):
        with self.assertRaisesRegex(ValueError, "distinct GPU"):
            runner.run_gpu_queue(runner.METHODS, (0, 0), Mock(), threading.Event())

    def test_cancelled_queue_never_runs(self):
        stop, job = threading.Event(), Mock()
        stop.set()
        with self.assertRaises(InterruptedError):
            runner.run_gpu_queue(runner.METHODS, (0, 1), job, stop)
        job.assert_not_called()


class OutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="amg-runner-test-")
        self.output = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def exposure(self, mode, actual="clip", task="ovlabel", memory=True):
        directory = self.output / mode
        directory.mkdir(exist_ok=True)
        row = {"iteration": 1, "microstep": 1, "examples": [{"requested_clip_id": "clip",
                "actual_clip_id": actual, "task_type": task, "budget": {"memory_tokens": 4},
                "memory_enabled": memory, "input_length": 100 + int(memory)}]}
        (directory / "exposure.jsonl").write_text(json.dumps(row) + "\n")

    def test_retrieval_finishing_before_off_cannot_start_pairing(self):
        directory = self.output / "retrieval"
        directory.mkdir()
        for name in ("coverage.json", "exposure.jsonl", "dev.metrics.json"):
            (directory / name).write_text("{}")
        with self.assertRaisesRegex(RuntimeError, "requires completed off"):
            runner.require_comparison_inputs(self.output, runner.METHODS)

    def test_all_five_dependencies_required(self):
        for mode in runner.METHODS:
            directory = self.output / mode
            directory.mkdir()
            for name in ("coverage.json", "exposure.jsonl", "dev.metrics.json"):
                (directory / name).write_text("{}")
        runner.require_comparison_inputs(self.output, runner.METHODS)
        (self.output / "random/dev.metrics.json").unlink()
        with self.assertRaisesRegex(RuntimeError, "completed random"):
            runner.require_comparison_inputs(self.output, runner.METHODS)

    def test_exposure_allows_memory_insertion_difference(self):
        self.exposure("off", memory=False)
        self.exposure("retrieval", memory=True)
        record = runner.compare_exposure(self.output, "retrieval")
        self.assertTrue(record["identical_requested_actual_task_and_budget"])
        self.assertEqual(record["examples"], 1)

    def test_actual_clip_mismatch_blocks_attribution(self):
        self.exposure("off")
        self.exposure("retrieval", actual="replacement")
        with self.assertRaisesRegex(RuntimeError, "Exposure mismatch"):
            runner.compare_exposure(self.output, "retrieval")
        record = runner.read_json(self.output / "retrieval/exposure-alignment.json")
        self.assertFalse(record["identical_requested_actual_task_and_budget"])

    def test_actual_task_mismatch_blocks_attribution(self):
        self.exposure("off")
        self.exposure("retrieval", task="description")
        with self.assertRaises(RuntimeError):
            runner.compare_exposure(self.output, "retrieval")

    def test_first_five_retains_amp_and_update_status(self):
        rows = [telemetry(step, updates=max(0, step - 2), overflow=step <= 2) for step in range(1, 6)]
        path = self.output / "train.jsonl"
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        record = runner.first_five_validation(path)
        self.assertTrue(record["all_losses_finite"])
        self.assertEqual(record["optimizer_updates"], 3)
        self.assertEqual(record["amp_overflow_iterations"], [1, 2])

    def test_first_five_waits_for_complete_lines(self):
        path = self.output / "train.jsonl"
        path.write_text(json.dumps(telemetry(1)) + "\n{\"iteration\":")
        self.assertIsNone(runner.first_five_validation(path))

    def test_first_five_rejects_no_update_and_nonfinite_loss(self):
        path = self.output / "train.jsonl"
        for rows, message in (([telemetry(step, updates=0) for step in range(1, 6)], "No successful"),
                              ([telemetry(step, loss=float("nan") if step == 2 else 1.)
                                for step in range(1, 6)], "Nonfinite loss")):
            path.write_text("\n".join(json.dumps(row) for row in rows))
            with self.assertRaisesRegex(RuntimeError, message):
                runner.first_five_validation(path)

    def test_state_updates_are_atomic_across_threads(self):
        protocol = self.output / "protocol.json"
        dump(protocol, {"seed": 42})
        experiment = runner.Experiment(protocol, self.output, python=sys.executable)
        with patch("builtins.print"):
            with ThreadPoolExecutor(max_workers=2) as pool:
                jobs = [pool.submit(experiment.event, mode, "training", gpu=gpu, child_pid=123 + gpu)
                        for mode, gpu in (("off", 0), ("retrieval", 1))]
                for job in jobs:
                    job.result()
        state = runner.read_json(self.output / "state.json")
        self.assertEqual(set(state["methods"]), {"off", "retrieval"})
        for mode in state["methods"]:
            self.assertIn("timestamp", state["methods"][mode])
            self.assertIn("pid", state["methods"][mode])
            self.assertIn("gpu", state["methods"][mode])
        self.assertEqual(len((self.output / "events.jsonl").read_text().splitlines()), 2)
        self.assertFalse((self.output / "state.json.tmp").exists())

    def test_subprocess_failure_raises_without_success(self):
        protocol = self.output / "protocol.json"
        dump(protocol, {"seed": 42})
        experiment = runner.Experiment(protocol, self.output, python=sys.executable)
        with patch("builtins.print"):
            with self.assertRaisesRegex(RuntimeError, "rc=2"):
                experiment.execute([sys.executable, "-c", "raise SystemExit(2)"],
                    self.output / "process.log", mode="off", stage="training")
        self.assertEqual(experiment.children, {})
        self.assertNotEqual(experiment.state["methods"]["off"]["stage"], "complete")

    def test_inference_rc_one_is_retained_for_full_denominator_scoring(self):
        protocol = self.output / "protocol.json"
        dump(protocol, {"seed": 42})
        experiment = runner.Experiment(protocol, self.output, python=sys.executable)
        with patch("builtins.print"):
            rc = experiment.execute([sys.executable, "-c", "raise SystemExit(1)"],
                self.output / "infer.log", mode="retrieval", stage="generating_dev", allowed=(0, 1))
        self.assertEqual(rc, 1)

    def test_monitor_exception_terminates_own_process_group(self):
        protocol = self.output / "protocol.json"
        dump(protocol, {"seed": 42})
        experiment = runner.Experiment(protocol, self.output, python=sys.executable)
        monitor = Mock(side_effect=RuntimeError("nonfinite loss"))
        with patch("builtins.print"):
            with self.assertRaisesRegex(RuntimeError, "nonfinite loss"):
                experiment.execute([sys.executable, "-c", "import time; time.sleep(60)"],
                    self.output / "monitor.log", mode="off", stage="training", monitor=monitor)
        child = experiment.state["methods"]["off"]["child_pid"]
        with self.assertRaises(ProcessLookupError):
            os.kill(child, 0)
        self.assertEqual(experiment.children, {})

    def test_sigterm_signals_only_registered_child_groups(self):
        protocol = self.output / "protocol.json"
        dump(protocol, {"seed": 42})
        experiment = runner.Experiment(protocol, self.output, python=sys.executable)
        active, finished = Mock(pid=111), Mock(pid=222)
        active.poll.return_value, finished.poll.return_value = None, 0
        experiment.children = {111: active, 222: finished}
        with patch.object(runner.os, "killpg") as killpg:
            experiment.signal_handler(signal.SIGTERM, None)
        killpg.assert_called_once_with(111, signal.SIGTERM)
        self.assertTrue(experiment.stop_event.is_set())
        self.assertEqual(experiment.interrupted_signal, signal.SIGTERM)


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="amg-lock-test-")
        self.project = Path(self.temp.name) / "project"
        self.project.mkdir()
        self.output = self.project / "amg/experiments/fresh"
        self.output.mkdir(parents=True)
        self.protocol_path = self.output / "protocol.json"
        self.base = self.project / "checkpoint_000035_loss_0.723.pth"
        self.base.write_bytes(b"fake cpu baseline")
        self.config = self.project / "config.yaml"
        self.config.write_text("fake: config\n")
        self.bank = self.project / "bank.pt"
        self.bank.write_bytes(b"fake complete frozen encoder bank")
        self.resource = self.project / "resource.json"
        self.resource.write_text("{}")
        self.splits = {}
        for split, count in (("fit", 4000), ("dev", 500), ("holdout", 500)):
            path = self.project / (split + ".jsonl")
            path.write_text("".join(json.dumps({"name": f"{split}-{index}", "group_id": f"{split}-{index}", "subtitle": "", "description": "neutral", "ovlabel": "neutral"}) + "\n" for index in range(count)))
            self.splits[split] = {"path": str(path), "sha256": runner.sha(path)}
        meta = {"schema": "amg-m0-bank-v1", "complete": True, "partial_for_testing": False,
                "records": 4000, "total_manifest_records": 4000,
                "manifest_path": self.splits["fit"]["path"],
                "manifest_sha256": self.splits["fit"]["sha256"], "config_sha256": runner.sha(self.config)}
        meta["version"] = "amg-m0-" + hashlib.sha256(json.dumps(meta, sort_keys=True).encode()).hexdigest()
        meta.update(bank_sha256=runner.sha(self.bank), created_at="now")
        dump(str(self.bank) + ".json", meta)
        self.protocol = {"seed": 42, "methods": list(runner.METHODS), "baseline_checkpoint": str(self.base),
                         "baseline_sha256": runner.sha(self.base), "config": str(self.config),
                         "memory_bank": str(self.bank), "evaluation_resource": str(self.resource),
                         "splits": self.splits, "max_concurrent_new_gpu_jobs": 2,
                         "training": {"iterations": 1334, "batch_size": 1, "grad_accum": 3,
                            "nominal_examples": 4002, "num_tokens": 4, "hidden_dim": 256,
                            "train_peft": True, "workers": 2, "lr": 1e-5, "memory_dropout": .2,
                            "weight_decay": .05, "cuda_memory_fraction": .35},
                         "generation": {"do_sample": False, "num_beams": 1, "seed": 42,
                                        "task": "ovlabel", "max_new_tokens": 128}}
        self.extra_source = self.project / "amg/train.py"
        for relative in ("amg/train.py", "config.py", "my_affectgpt/models/affectgpt.py",
                         "my_affectgpt/models/encoder.py", "my_affectgpt/datasets/datasets/base_dataset.py",
                         "my_affectgpt/datasets/datasets/mercaptionplus_dataset.py"):
            path = self.project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# CPU fixture\n")
        self.project_patch = patch.object(runner, "PROJECT", self.project)
        self.project_patch.start()
        self.lock()

    def tearDown(self):
        self.project_patch.stop()
        self.temp.cleanup()

    def lock(self):
        dump(self.protocol_path, self.protocol)
        paths = {self.protocol_path, Path(runner.__file__).resolve(), self.base, self.config, self.bank,
                 Path(str(self.bank) + ".json"), self.resource}
        paths.update(self.project.rglob("*.py"))
        paths.update(self.project / (split + ".jsonl") for split in self.splits)
        self.ready = {"locked_files": {str(path): runner.sha(path) for path in paths}}
        dump(self.output / "READY.json", self.ready)

    def experiment(self):
        return runner.Experiment(self.protocol_path, self.output, python=sys.executable)

    def test_full_locked_provenance_accepts(self):
        validated = self.experiment().validate()
        self.assertTrue(validated["validated"])
        self.assertEqual(validated["gpus"], [0, 1])

    def test_changed_source_rejected(self):
        self.extra_source.write_text("# changed after locking\n")
        with self.assertRaisesRegex(RuntimeError, "Locked artifact changed"):
            self.experiment().validate()

    def test_missing_source_lock_rejected(self):
        del self.ready["locked_files"][str(self.extra_source)]
        dump(self.output / "READY.json", self.ready)
        with self.assertRaisesRegex(ValueError, "READY must lock"):
            self.experiment().validate()

    def test_protocol_baseline_digest_mismatch_rejected(self):
        self.protocol["baseline_sha256"] = "0" * 64
        self.lock()
        with self.assertRaisesRegex(RuntimeError, "Baseline differs"):
            self.experiment().validate()

    def test_partial_bank_rejected_even_with_valid_file_lock(self):
        metadata = runner.read_json(str(self.bank) + ".json")
        metadata.update(complete=False, records=2, partial_for_testing=True)
        dump(str(self.bank) + ".json", metadata)
        self.lock()
        with self.assertRaisesRegex(RuntimeError, "complete 4000-record"):
            self.experiment().validate()

    def test_bank_version_tampering_rejected(self):
        metadata = runner.read_json(str(self.bank) + ".json")
        metadata["version"] = "amg-m0-" + "0" * 64
        dump(str(self.bank) + ".json", metadata)
        self.lock()
        with self.assertRaisesRegex(RuntimeError, "Memory version"):
            self.experiment().validate()

    def test_configured_gpu_bound_and_training_budget_enforced(self):
        for key, value, message in (("max_concurrent_new_gpu_jobs", 1, "two workers"),
                                    ("seed", 7, "seed 42")):
            original = self.protocol[key]
            self.protocol[key] = value
            self.lock()
            with self.assertRaisesRegex(ValueError, message):
                self.experiment().validate()
            self.protocol[key] = original
        self.protocol["training"]["grad_accum"] = 1
        self.lock()
        with self.assertRaisesRegex(ValueError, "Training budget"):
            self.experiment().validate()

    def test_fake_complete_pipeline_pairs_only_after_all_five_methods(self):
        experiment = self.experiment()
        completed_scores, gpu_active, lock = set(), {}, threading.Lock()
        peak, pairs = [0], []

        def execute(args, log_path, *, mode, stage, gpu=None, allowed=(0,), monitor=None):
            def value(flag):
                return args[args.index(flag) + 1]
            with lock:
                if gpu is not None:
                    self.assertNotIn(gpu, gpu_active)
                    gpu_active[gpu] = mode
                    peak[0] = max(peak[0], len(gpu_active))
            try:
                time.sleep(.01)
                if "amg.train" in args:
                    out = Path(value("--output-dir"))
                    out.mkdir()
                    config = {"mode": mode, "base_checkpoint": self.protocol["baseline_checkpoint"],
                              "base_sha256": self.protocol["baseline_sha256"],
                              "memory_sha256": experiment.bank_metadata["bank_sha256"],
                              "memory_version": experiment.bank_metadata["version"],
                              "manifest_sha256": self.splits["fit"]["sha256"],
                              "seed": 42, "allow_partial_bank": False, "trainable_parameters": 123}
                    dump(out / "config.json", config)
                    groups = {name: {"changed_tensors": 1} for name in ("lora", "memory_adapter", "learned_tokens")}
                    dump(out / "coverage.json", {"completed_iterations": 1334, "examples": 4002,
                         "actual_covered_ids": 4000, "missing_actual_ids": [], "optimizer_updates": 1334,
                         "parameter_changes": {"all_finite": True, "groups": groups}})
                    (out / "train.jsonl").write_text("".join(json.dumps(telemetry(step)) + "\n" for step in range(1, 6)))
                    (out / "checkpoint_001334.pth").write_bytes(b"fake cpu trained checkpoint")
                    row = {"iteration": 1, "microstep": 1, "examples": [{"requested_clip_id": "clip",
                           "actual_clip_id": "clip", "task_type": "ovlabel", "budget": {"memory_tokens": 4}}]}
                    (out / "exposure.jsonl").write_text((json.dumps(row) + "\n") * 4002)
                    monitor()
                elif "amg.evaluate" in args:
                    report_mode = Path(value("--predictions")).parent.name
                    report = {"metadata": {"base_checkpoint_sha256": self.protocol["baseline_sha256"],
                                           "trained_mode": report_mode, "memory_mode": report_mode},
                              "metrics": {"N": 500, "micro_f1": .5, "sample_macro_f1": .5,
                                          "failed_predictions": 0, "unmapped_prediction_clips": 0},
                              "per_clip": [{}] * 500}
                    with lock:
                        if "--paired-report" in args:
                            self.assertEqual(completed_scores, set(runner.METHODS))
                            pairs.append((report_mode, Path(value("--paired-report")).parent.name))
                            report["paired"] = {"N": 500, "delta": {"micro_f1": 0.},
                                 "bootstrap": {"intervals": {"micro_f1": [0., 0.]}}, "negative_gain_fraction": 0.}
                        else:
                            completed_scores.add(report_mode)
                    dump(value("--output"), report)
                else:
                    Path(value("--output")).write_text("fake cpu generation\n")
                return 0
            finally:
                with lock:
                    if gpu is not None:
                        del gpu_active[gpu]
        with patch.object(experiment, "execute", side_effect=execute), \
             patch.object(experiment, "wait_gpu"), patch("builtins.print"):
            experiment.run()
        self.assertEqual(peak[0], 2)
        self.assertEqual(len(pairs), 7)
        self.assertEqual(experiment.state["status"], "complete")
        summary = runner.read_json(self.output / "summary.json")
        self.assertEqual(len(summary["methods"]), 5)
        self.assertEqual(summary["baseline_sha256"], self.protocol["baseline_sha256"])
        self.assertTrue((self.output / "SUMMARY.md").is_file())

    def test_failed_method_cannot_enter_paired_phase(self):
        experiment = self.experiment()
        for mode in runner.METHODS:
            directory = self.output / mode
            directory.mkdir()
            for name in ("coverage.json", "exposure.jsonl", "dev.metrics.json"):
                (directory / name).write_text("{}")
            experiment.state["methods"][mode] = {"stage": "complete"}
        experiment.state["methods"]["off"]["stage"] = "failed"
        with patch.object(experiment, "execute") as execute:
            with self.assertRaisesRegex(RuntimeError, "incomplete or failed method"):
                experiment.paired_phase()
        execute.assert_not_called()

    def test_args_take_checkpoint_from_protocol(self):
        experiment = self.experiment()
        train_args = experiment.train_args("off", self.output / "off")
        infer_args = experiment.infer_args(self.output / "off/checkpoint_001334.pth", self.output / "off/dev.jsonl")
        for args in (train_args, infer_args):
            self.assertEqual(args[args.index("--baseline-checkpoint") + 1], str(self.base))
        self.assertEqual(train_args[train_args.index("--steps") + 1], "1334")
        self.assertNotIn("--allow-partial-bank", train_args)


if __name__ == "__main__":
    unittest.main()

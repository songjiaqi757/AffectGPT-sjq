"""CPU trainer regression tests; no AffectGPT weights, GPU, or real training."""
from contextlib import nullcontext, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch
from torch import nn
from torch.utils.data import Dataset

from amg import train


class ToyDataset(Dataset):
    def __init__(self, active, replace_first=False):
        self.active = list(active)
        self.replace_first = replace_first

    def __len__(self):
        return len(self.active)

    def __getitem__(self, index):
        actual = 1 if self.replace_first and index == 0 else index
        return {"clip": str(actual), "requested": str(index), "active": self.active[actual],
                "task_type": "description" if actual % 2 == 0 else "ovlabel",
                "failures": [{"clip_id": "0", "error": "OSError: unreadable media"}]
                            if actual != index else []}

    @staticmethod
    def collater(rows):
        ids = [row["clip"] for row in rows]
        return {"clip_ids": ids, "original_ids": [row["requested"] for row in rows], "actual_ids": ids,
                "replacement_failures": [row["failures"] for row in rows],
                "task_types": [row["task_type"] for row in rows],
                "budget_metadata": [{"asr_truncated_tokens": 2} for _ in rows],
                "active": torch.tensor([row["active"] for row in rows], dtype=torch.bool)}


class ToyModel(nn.Module):
    MODES = {"retrieval", "random", "off", "current", "learned"}

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.weight = nn.Parameter(torch.tensor(1.0))

    def forward(self, batch):
        active = batch["active"]
        loss = self.weight.square() if bool(active.any()) else self.weight.new_tensor(1.0)
        return {"loss": loss, "memory_enabled": active, "input_lengths": 5 + active.long() * 4}

    def trainable_state(self):
        return {"weight": self.weight.detach().cpu().clone()}


class FirstStepSkippingScaler:
    """CPU stand-in for GradScaler found_inf skip; no CUDA allocation."""
    def __init__(self, *args, **kwargs):
        self.factor = 16.0
        self.skip_next = True
        self.skipped = False

    def scale(self, loss):
        return loss

    def unscale_(self, optimizer):
        pass

    def get_scale(self):
        return self.factor

    def step(self, optimizer):
        self.skipped = self.skip_next
        self.skip_next = False
        if not self.skipped:
            optimizer.step()

    def update(self):
        if self.skipped:
            self.factor /= 2

    def state_dict(self):
        return {"scale": self.factor}


class TrainerTests(unittest.TestCase):
    def run_mock(self, active, *, steps=2, batch_size=2, grad_accum=2, replace_first=False, skip_first_update=False):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            run = {"manifest": "unused-manifest", "memory_bank": None,
                   "base_checkpoint": "unused-base", "schema": "cpu-test"}
            prepared = (object(), [{"name": str(i)} for i in range(len(active))],
                        None, run, output)
            argv = ["--baseline-checkpoint", "unused", "--manifest", "unused",
                    "--output-dir", str(output), "--device", "cpu", "--workers", "0",
                    "--steps", str(steps), "--batch-size", str(batch_size),
                    "--grad-accum", str(grad_accum), "--save-every", "1",
                    "--log-every", "1", "--lr", "0.1"]
            dataset = ToyDataset(active, replace_first=replace_first)
            scaler_patch = patch.object(train.torch.amp, "GradScaler", FirstStepSkippingScaler) if skip_first_update else nullcontext()
            with scaler_patch, patch.object(train, "prepare_run", return_value=prepared), \
                 patch.object(train, "build_dataset", return_value=dataset), \
                 patch.object(train, "load_base", return_value=object()), \
                 patch.object(train, "AMGAffectGPT", ToyModel), \
                 patch.object(train.torch.cuda, "set_per_process_memory_fraction") as fraction, \
                 redirect_stdout(io.StringIO()):
                train.main(argv)
                fraction.assert_not_called()
            rows = [json.loads(line) for line in (output / "train.jsonl").read_text().splitlines()]
            path = output / f"checkpoint_{steps:06d}.pth"
            self.assertTrue(path.is_file())
            payload = torch.load(path, map_location="cpu", weights_only=True)
            self.assertEqual(payload["step"], steps)
            self.assertEqual(payload["schema"], "amg-m0-train-v1")
            self.assertFalse(payload["resume_supported"])
            self.assertTrue((output / "config.json").is_file())
            self.assertFalse(path.with_name(path.name + ".tmp").exists())
            exposure = [json.loads(line) for line in (output / "exposure.jsonl").read_text().splitlines()]
            coverage = json.loads((output / "coverage.json").read_text())
            self.assertFalse((output / "coverage.json.tmp").exists())
            return rows, payload, exposure, coverage

    def test_differentiable_batches_update_and_save_actual_exposure(self):
        rows, checkpoint, exposure, coverage = self.run_mock([True, True, True])
        self.assertEqual([row["no_update"] for row in rows], [False, False])
        self.assertEqual([row["optimizer_updates"] for row in rows], [1, 2])
        self.assertEqual([row["examples"] for row in rows], [3, 3])
        self.assertEqual([row["cumulative_examples"] for row in rows], [3, 6])
        self.assertLess(float(checkpoint["model"]["weight"]), 1.0)
        self.assertGreater(len(checkpoint["optimizer"]["state"]), 0)
        changes = coverage["parameter_changes"]
        self.assertTrue(changes["all_finite"])
        self.assertEqual(changes["groups"]["other"]["changed_tensors"], 1)
        self.assertGreater(changes["groups"]["other"]["max_abs_delta"], 0)
        self.assertEqual(changes, checkpoint["progress"]["parameter_changes"])
        resources = coverage["resources"]
        self.assertEqual(resources["processed_examples"], 6)
        self.assertGreater(resources["elapsed_s"], 0)
        self.assertGreater(resources["examples_per_second"], 0)
        self.assertIsNone(resources["cuda_max_memory_allocated_bytes"])
        self.assertIsNone(resources["cuda_max_memory_reserved_bytes"])
        self.assertEqual(resources, checkpoint["progress"]["resources"])
        self.assertEqual([row["iteration"] for row in rows], [1, 2])
        self.assertEqual([row["optimizer_attempts"] for row in rows], [1, 2])
        self.assertEqual([len(row["examples"]) for row in exposure], [2, 1, 2, 1])
        self.assertEqual([row["global_microstep"] for row in exposure], [1, 2, 3, 4])
        self.assertEqual([row["microstep"] for row in exposure], [1, 2, 1, 2])
        self.assertEqual(coverage["completed_iterations"], 2)
        self.assertEqual(coverage["processed_microsteps"], 4)
        self.assertEqual(coverage["optimizer_updates"], 2)
        self.assertEqual(coverage["examples"], 6)
        self.assertEqual(coverage["actual_covered_ids"], 3)
        self.assertEqual(coverage["missing_actual_ids"], [])
        self.assertEqual([item["actual"] for item in coverage["ids"].values()], [2, 2, 2])
        self.assertEqual(checkpoint["progress"]["optimizer_updates"], 2)
        for row in exposure:
            for item in row["examples"]:
                self.assertEqual(item["requested_clip_id"], item["actual_clip_id"])
                self.assertEqual(item["input_length"], 9)
                self.assertTrue(item["memory_enabled"])
                self.assertEqual(item["budget"]["asr_truncated_tokens"], 2)

    def test_entirely_dropped_batches_skip_backward_decay_and_still_save(self):
        rows, checkpoint, exposure, coverage = self.run_mock([False, False, False])
        self.assertEqual([row["no_update"] for row in rows], [True, True])
        self.assertEqual([row["optimizer_updates"] for row in rows], [0, 0])
        self.assertEqual([row["grad_norm"] for row in rows], [0.0, 0.0])
        self.assertEqual([row["memory_enabled"] for row in rows], [0, 0])
        self.assertEqual([row["cumulative_examples"] for row in rows], [3, 6])
        self.assertEqual(float(checkpoint["model"]["weight"]), 1.0)
        self.assertEqual(checkpoint["optimizer"]["state"], {})
        changes = coverage["parameter_changes"]["groups"]["other"]
        self.assertEqual(changes["changed_tensors"], 0)
        self.assertEqual(changes["max_abs_delta"], 0.0)
        self.assertEqual(coverage["optimizer_attempts"], 0)
        self.assertEqual(coverage["optimizer_updates"], 0)
        self.assertEqual(coverage["optimizer_skipped_iterations"], 2)
        self.assertFalse(coverage["resume_supported"])
        self.assertEqual(coverage["examples"], 6)
        self.assertTrue(all(item["input_length"] == 5 and not item["memory_enabled"]
                            for row in exposure for item in row["examples"]))

    def test_mixed_microbatches_with_and_without_gradient_complete(self):
        rows, checkpoint, exposure, coverage = self.run_mock([True, False], steps=1,
                                         batch_size=1, grad_accum=2)
        self.assertFalse(rows[0]["no_update"])
        self.assertEqual(rows[0]["optimizer_updates"], 1)
        self.assertEqual(rows[0]["memory_enabled"], 1)
        self.assertEqual(rows[0]["examples"], 2)
        self.assertLess(float(checkpoint["model"]["weight"]), 1.0)


    def test_scaler_skip_changes_actual_update_count_but_preserves_exposure_budget(self):
        rows, checkpoint, exposure, coverage = self.run_mock(
            [True, True, True], skip_first_update=True)
        self.assertEqual([row["optimizer_attempts"] for row in rows], [1, 2])
        self.assertEqual([row["optimizer_updates"] for row in rows], [0, 1])
        self.assertEqual([row["amp_overflow"] for row in rows], [True, False])
        self.assertEqual([row["no_update"] for row in rows], [True, False])
        self.assertEqual(coverage["examples"], 6)
        self.assertEqual(coverage["actual_covered_ids"], 3)
        self.assertEqual(coverage["optimizer_updates"], 1)
        self.assertEqual(checkpoint["progress"]["optimizer_updates"], 1)

    def test_replacements_change_actual_coverage_and_task_counts_without_hiding_requested_ids(self):
        rows, checkpoint, exposure, coverage = self.run_mock(
            [True, True, True], replace_first=True)
        self.assertEqual(coverage["requested_covered_ids"], 3)
        self.assertEqual(coverage["actual_covered_ids"], 2)
        self.assertEqual(coverage["missing_requested_ids"], [])
        self.assertEqual(coverage["missing_actual_ids"], ["0"])
        self.assertEqual(coverage["ids"]["0"]["requested"], 2)
        self.assertEqual(coverage["ids"]["0"]["actual"], 0)
        self.assertEqual(coverage["ids"]["0"]["failed_reads"], 2)
        self.assertEqual(coverage["ids"]["1"]["actual"], 4)
        self.assertEqual(coverage["task_types"], {"description": 2, "ovlabel": 4})
        self.assertEqual(coverage["failed_reads"], 2)
        self.assertEqual(coverage["replaced_examples"], 2)
        replaced = [item for row in exposure for item in row["examples"] if item["was_replaced"]]
        self.assertEqual(len(replaced), 2)
        for item in replaced:
            self.assertEqual(item["requested_clip_id"], "0")
            self.assertEqual(item["actual_clip_id"], "1")
            self.assertEqual(item["task_type"], "ovlabel")
            self.assertEqual(item["replacement_failures"][0]["clip_id"], "0")

    def test_exposure_rejects_unknown_identity_task_and_metadata_shape(self):
        batch = ToyDataset.collater([ToyDataset([True])[0]])
        result = ToyModel()(batch)
        bad_identity = dict(batch, actual_ids=["outside"], clip_ids=["outside"])
        bad_task = dict(batch, task_types=["hybrid"])
        bad_shape = dict(batch, task_types=[])
        for broken, message in ((bad_identity, "outside training manifest"),
                                (bad_task, "task type"),
                                (bad_shape, "batch size")):
            with self.subTest(message=message):
                audit = train.ExposureAudit([{"name": "0"}])
                with self.assertRaisesRegex(ValueError, message):
                    audit.record(broken, result, iteration=1, microstep=1)



class TrainingInputBoundaryTests(unittest.TestCase):
    def test_observed_evaluation_manifest_rejected_during_preflight(self):
        from amg import train
        from unittest.mock import patch
        import tempfile, json
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            manifest=Path(directory)/"evaluation-observed.jsonl"
            manifest.write_text(json.dumps({"name":"eval_only", "subtitle":"observed", "group_id":"eval_only"})+"\n")
            args=train.parser().parse_args(["--baseline-checkpoint","unused.pth",
                "--manifest",str(manifest),"--output-dir",str(Path(directory)/"out"),
                "--mode","off","--steps","1","--dry-run"])
            with patch.object(train,"load_config",return_value=None):
                with self.assertRaisesRegex(ValueError,"required fields"):
                    train.prepare_run(args)


class CUDAMemoryFractionPreflightTests(unittest.TestCase):
    def arguments(self, fraction, device="cuda:0"):
        return train.parser().parse_args(["--baseline-checkpoint", "unused.pth",
            "--manifest", "unused.jsonl", "--output-dir", "unused",
            "--steps", "1", "--mode", "off", "--device", device,
            "--cuda-memory-fraction", str(fraction)])

    def test_invalid_fraction_rejected_before_configuration_or_model_loading(self):
        for value in (-0.1, 0, 1.1, float("nan")):
            with self.subTest(value=value), patch.object(train, "load_config") as load:
                with self.assertRaisesRegex(ValueError, "fraction"):
                    train.prepare_run(self.arguments(value))
                load.assert_not_called()

    def test_fraction_requires_a_cuda_device(self):
        with patch.object(train, "load_config") as load:
            with self.assertRaisesRegex(ValueError, "CUDA device"):
                train.prepare_run(self.arguments(0.35, device="cpu"))
            load.assert_not_called()


class GroupedParameters(nn.Module):
    def __init__(self):
        super().__init__()
        self.base = nn.Module()
        self.base.lora_delta = nn.Parameter(torch.tensor([1.0, 2.0]))
        self.base.frozen_weight = nn.Parameter(torch.ones(5), requires_grad=False)
        self.memory_adapter = nn.Linear(2, 1, bias=False)
        self.learned_tokens = nn.Parameter(torch.zeros(1, 2))
        self.other = nn.Parameter(torch.tensor([3.0]))

    def snapshot(self):
        return {name: parameter.detach().to(device="cpu", copy=True)
                for name, parameter in self.named_parameters() if parameter.requires_grad}


class ParameterChangeAuditTests(unittest.TestCase):
    def test_grouped_actual_changes_use_independent_cpu_snapshot_and_exclude_frozen_base(self):
        model = GroupedParameters()
        audit = train.ParameterChangeAudit(model)
        self.assertNotIn("base.frozen_weight", audit.initial)
        for name, parameter in model.named_parameters():
            if parameter.requires_grad:
                self.assertEqual(audit.initial[name].device.type, "cpu")
                self.assertNotEqual(audit.initial[name].data_ptr(), parameter.data_ptr())
        initial_lora = audit.initial["base.lora_delta"].clone()
        with torch.no_grad():
            model.base.lora_delta[0] += 0.5
            model.memory_adapter.weight.add_(0.25)
            model.other.sub_(2.0)
            model.base.frozen_weight.add_(100)
        summary = audit.summarize(model.snapshot())
        self.assertTrue(summary["all_finite"])
        self.assertFalse(summary["includes_frozen_parameters"])
        self.assertEqual(summary["initial_snapshot_bytes"], 7 * 4)
        self.assertEqual(summary["groups"]["lora"]["changed_tensors"], 1)
        self.assertEqual(summary["groups"]["lora"]["max_abs_delta"], 0.5)
        self.assertEqual(summary["groups"]["memory_adapter"]["changed_tensors"], 1)
        self.assertAlmostEqual(summary["groups"]["memory_adapter"]["max_abs_delta"], 0.25, places=6)
        self.assertEqual(summary["groups"]["learned_tokens"]["changed_tensors"], 0)
        self.assertEqual(summary["groups"]["learned_tokens"]["max_abs_delta"], 0.0)
        self.assertEqual(summary["groups"]["other"]["max_abs_delta"], 2.0)
        torch.testing.assert_close(audit.initial["base.lora_delta"], initial_lora, rtol=0, atol=0)

    def test_initial_final_and_delta_nonfinite_are_reported_without_nonstandard_json_numbers(self):
        model = GroupedParameters()
        with torch.no_grad():
            model.learned_tokens[0, 0] = float("nan")
        audit = train.ParameterChangeAudit(model)
        with torch.no_grad():
            model.memory_adapter.weight[0, 0] = float("inf")
        summary = audit.summarize(model.snapshot())
        self.assertFalse(summary["all_finite"])
        self.assertFalse(summary["groups"]["learned_tokens"]["initial_finite"])
        self.assertFalse(summary["groups"]["learned_tokens"]["delta_finite"])
        self.assertFalse(summary["groups"]["memory_adapter"]["final_finite"])
        self.assertIsNone(summary["groups"]["memory_adapter"]["max_abs_delta"])
        self.assertIsNone(summary["groups"]["learned_tokens"]["max_abs_delta"])
        json.dumps(summary, allow_nan=False)

    def test_snapshot_keys_shape_and_dtype_must_match_initial_trainable_parameters(self):
        model = GroupedParameters()
        audit = train.ParameterChangeAudit(model)
        missing = model.snapshot()
        missing.pop("other")
        with self.assertRaisesRegex(ValueError, "exact trainable checkpoint keys"):
            audit.summarize(missing)
        for value in (torch.zeros(2), torch.zeros(1, dtype=torch.float64)):
            current = model.snapshot()
            current["other"] = value
            with self.assertRaisesRegex(ValueError, "shape/dtype mismatch"):
                audit.summarize(current)


if __name__ == "__main__":
    unittest.main()

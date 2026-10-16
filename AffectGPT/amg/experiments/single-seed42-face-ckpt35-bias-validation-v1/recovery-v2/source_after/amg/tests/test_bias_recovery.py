"""CPU regression checks for disabled-memory inference trace validation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from amg.run_bias_validation import BiasExperiment


class BiasRecoveryTraceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.predictions = self.directory / "dev.jsonl"
        self.checkpoint = self.directory / "checkpoint.pth"
        self.experiment = object.__new__(BiasExperiment)
        self.experiment.dev_rows = [
            {"name": "clip_%04d" % index} for index in range(500)
        ]
        self.experiment.fit_ids = {"fit_%d" % index for index in range(5)}
        self.experiment.protocol = {
            "baseline_sha256": "baseline-sha",
            "splits": {"dev": {"sha256": "dev-sha"}},
            "memory_bank_sha256": "bank-sha",
            "seed": 42,
        }

    def write_fixture(self, *, mode, enabled):
        rows = [
            {"name": item["name"], "error": None,
             "retrieval": {"retrieved_ids": None, "memory_enabled": [enabled]}}
            for item in self.experiment.dev_rows
        ]
        self.predictions.write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        metadata = {
            "base_sha256": "baseline-sha",
            "amg_sha256": "checkpoint-sha",
            "manifest_sha256": "dev-sha",
            "memory_sha256": "bank-sha",
            "trained_mode": "retrieval",
            "memory_mode": mode,
            "seed": 42,
            "selected_clips": 500,
            "manifest_records": 500,
            "dry_run": False,
            "successes": 500,
            "errors": 0,
            "model_intervention": {
                "policy": "none", "applied": False, "changed_parameters": []
            },
        }
        self.predictions.with_name("dev.meta.json").write_text(
            json.dumps(metadata), encoding="utf-8"
        )

    def validate(self, mode):
        with patch("amg.run_bias_validation.sha", return_value="checkpoint-sha"):
            return self.experiment.validate_inference(
                self.predictions, self.checkpoint, mode, "none"
            )

    def test_off_null_neighbors_and_disabled_memory_are_accepted(self):
        self.write_fixture(mode="off", enabled=False)
        result = self.validate("off")
        self.assertEqual(result["rows"], 500)
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["memory_mode"], "off")

    def test_off_enabled_memory_is_rejected(self):
        self.write_fixture(mode="off", enabled=True)
        with self.assertRaisesRegex(RuntimeError, "Off intervention actually enabled memory"):
            self.validate("off")

    def test_retrieval_null_neighbors_are_rejected(self):
        self.write_fixture(mode="retrieval", enabled=True)
        with self.assertRaisesRegex(RuntimeError, "Expected five non-self fit memories"):
            self.validate("retrieval")


if __name__ == "__main__":
    unittest.main()

"""CPU-only scoring/provenance/paired comparison tests; no model/media/API."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from amg.evaluate import (RESOURCE, aggregate, audit_original_format, canonicalise,
                          description_labels, evaluate, load_resource, main,
                          paired_comparison, parse_ovlabel, read_predictions,
                          set_scores, word_overlap_f1)
from amg.manifest import sha256_file


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resource = load_resource()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.manifest = self.root / "dev.jsonl"
        self.predictions = self.root / "predictions.jsonl"
        self.refs = [
            {"name": "a", "group_id": "group1", "subtitle": "observed a",
             "ovlabel": "anger, anxiety", "description": "The person is angry and anxious."},
            {"name": "b", "group_id": "group1", "subtitle": "observed b",
             "ovlabel": "joy", "description": "The person expresses joy."},
            {"name": "c", "group_id": "group2", "subtitle": "observed c",
             "ovlabel": "fearless", "description": "The person is fearless."},
            {"name": "d", "group_id": "group3", "subtitle": "observed d",
             "ovlabel": "sadness", "description": "The person appears sad."}]
        self.write_jsonl(self.manifest, self.refs)
        self.meta = {"schema": "amg-m0-inference-v1", "dataset": "MERCaptionPlus",
                     "manifest_sha256": sha256_file(self.manifest), "dry_run": False,
                     "task": "ovlabel", "seed": 42, "amg_checkpoint": "/fixture/only_final.pth",
                     "amg_sha256": "1" * 64, "base_sha256": "2" * 64,
                     "memory_sha256": None, "memory_bank": None, "max_new_tokens": 128,
                     "trained_mode": "off", "memory_mode": "off",
                     "do_sample": False, "num_beams": 1, "prompt_sha256": "3" * 64,
                     "face_or_frame": "frame_audio_text", "config_sha256": "4" * 64}
        self.pred_rows = [{"name": "a", "group_id": "group1",
                           "prediction": "The character's emotional state is angry."},
                          {"name": "b", "error": "unreadable audio"},
                          {"name": "d", "prediction": "sad, previously-unseen-feeling"}]
        self.write_run()

    @staticmethod
    def write_jsonl(path, rows):
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def write_run(self):
        self.write_jsonl(self.predictions, self.pred_rows)
        self.predictions.with_name("predictions.meta.json").write_text(json.dumps(self.meta))

    def run_eval(self, **kwargs):
        return evaluate(self.manifest, self.predictions, split="dev", **kwargs)

    def test_actual_wrapper_json_and_delimited_label_parsing(self):
        expected = ["anger", "anxiety"]
        for value in ("The character's emotional state is angry, anxious.",
                      "The character’s emotional states are angry and anxious.",
                      '["angry", "anxiety"]', "['angry', 'anxiety']",
                      "Emotions: angry; anxious", "- angry\n- anxious",
                      "1. angry\n2. anxious"):
            self.assertEqual(parse_ovlabel(value, self.resource)["labels"], expected, value)
        self.assertEqual(parse_ovlabel("Assistant: happy.###Human:", self.resource)["labels"],
                         ["happiness"])
        self.assertEqual(parse_ovlabel("angry, anger, angry", self.resource)["labels"], ["anger"])

    def test_fearlessness_is_never_fear(self):
        self.assertEqual(canonicalise("fearless", self.resource), "fearlessness")
        self.assertEqual(canonicalise("fearful", self.resource), "fear")
        self.assertEqual(canonicalise("afraid", self.resource), "fear")
        self.assertEqual(set_scores(["fear"], ["fearlessness"])["f1"], 0)
        actual = description_labels("She is fearless and not angry.", self.resource)["labels"]
        self.assertIn("fearlessness", actual)
        self.assertNotIn("fear", actual)
        self.assertNotIn("anger", actual)

    def test_unknown_and_negated_predictions_are_retained(self):
        parsed = parse_ovlabel("not angry, unusual imaginary emotion", self.resource)
        self.assertIn("not angry", parsed["labels"])
        self.assertIn("unusual imaginary emotion", parsed["unmapped"])
        self.assertNotIn("anger", parsed["labels"])
        self.assertEqual(set_scores(["anger"], parsed["labels"])["fp"], 2)
        self.assertTrue(parse_ovlabel("[]", self.resource)["empty"])
        self.assertTrue(parse_ovlabel("", self.resource)["empty"])

    def test_full_denominator_failure_missing_and_unknown_counts(self):
        report = self.run_eval()
        metrics = report["metrics"]
        self.assertEqual(metrics["N"], 4)
        self.assertEqual((metrics["tp"], metrics["fp"], metrics["fn"]), (2, 1, 3))
        self.assertAlmostEqual(metrics["micro_f1"], .5)
        self.assertAlmostEqual(metrics["sample_macro_f1"], 1 / 3)
        self.assertEqual(metrics["successful_predictions"], 2)
        self.assertEqual(metrics["failed_predictions"], 2)
        self.assertEqual(metrics["generation_errors"], 1)
        self.assertEqual(metrics["missing_predictions"], 1)
        self.assertEqual(metrics["empty_predictions"], 2)
        self.assertEqual(metrics["unmapped_prediction_clips"], 1)
        self.assertFalse(report["is_paper_nine_benchmark_ew"])
        self.assertEqual(report["metadata"]["prompt_provenance"], "inference_metadata")

    def test_intervention_and_shared_start_provenance_survive_scoring(self):
        self.meta["requested_value_last_bias_override"] = "zero"
        self.meta["model_intervention"] = {
            "policy": "zero", "runtime_adapter_sha256": "a" * 64,
            "source_adapter_sha256": "b" * 64, "applied": True}
        self.meta["training_initialization"] = {
            "adapter_init_state_sha256": "c" * 64, "value_last_bias_init": "zero"}
        self.write_run()
        provenance = self.run_eval()["metadata"]
        for key in ("requested_value_last_bias_override", "model_intervention", "training_initialization"):
            self.assertEqual(provenance[key], self.meta[key])

    def test_legacy_runtime_fingerprint_is_explicitly_unknown(self):
        provenance = self.run_eval()["metadata"]
        self.assertEqual(provenance["requested_value_last_bias_override"], "none")
        self.assertIsNone(provenance["model_intervention"]["runtime_adapter_sha256"])
        self.assertIn("legacy", provenance["model_intervention"]["provenance"])

    def test_reference_outside_frozen_fit_vocabulary_can_exact_match(self):
        self.refs[0]["ovlabel"] = "a deliberately unseen emotional phrase"
        self.write_jsonl(self.manifest, self.refs)
        self.meta["manifest_sha256"] = sha256_file(self.manifest)
        self.pred_rows[0]["prediction"] = self.refs[0]["ovlabel"]
        self.write_run()
        report = self.run_eval()
        self.assertEqual(report["per_clip"][0]["f1"], 1)
        self.assertIn(self.refs[0]["ovlabel"],
                      report["per_clip"][0]["reference_labels_outside_fit_vocabulary"])

    def test_duplicates_foreign_ids_groups_and_mixed_modes_are_rejected(self):
        self.write_jsonl(self.predictions, self.pred_rows + [self.pred_rows[0]])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_eval()
        self.write_jsonl(self.predictions, self.pred_rows + [{"name": "foreign", "prediction": "anger"}])
        with self.assertRaisesRegex(ValueError, "outside"):
            self.run_eval()
        self.pred_rows[0]["group_id"] = "wrong"
        self.write_run()
        with self.assertRaisesRegex(ValueError, "group"):
            self.run_eval()
        self.pred_rows[0]["group_id"] = "group1"
        self.pred_rows[0]["memory_mode"] = "retrieval"
        self.write_run()
        with self.assertRaisesRegex(ValueError, "Mixed"):
            self.run_eval()

    def test_target_dataset_metadata_rejected_before_reading_labels(self):
        self.meta["dataset"] = "OVMERDPlus"
        self.write_run()
        with patch("amg.evaluate.read_manifest", side_effect=AssertionError("must not read labels")):
            with self.assertRaisesRegex(ValueError, "source"):
                self.run_eval()

    def test_different_manifest_dry_run_and_checkpoint_override_rejected(self):
        self.meta["manifest_sha256"] = "0" * 64
        self.write_run()
        with self.assertRaisesRegex(ValueError, "manifest"):
            self.run_eval()
        self.meta["manifest_sha256"] = sha256_file(self.manifest)
        self.meta["dry_run"] = True
        self.write_run()
        with self.assertRaisesRegex(ValueError, "completed"):
            self.run_eval()
        self.meta["dry_run"] = False
        self.pred_rows[0]["amg_checkpoint"] = "/different/epoch.pth"
        self.write_run()
        with self.assertRaisesRegex(ValueError, "checkpoint"):
            self.run_eval()

    def test_resource_and_run_provenance_are_hashed(self):
        report = self.run_eval()
        meta = report["metadata"]
        for field in ("manifest_sha256", "predictions_sha256", "inference_metadata_sha256",
                      "resource_sha256", "scorer_source_sha256", "prompt_sha256"):
            self.assertEqual(len(meta[field]), 64)
        self.assertEqual(meta["resource_sha256"], sha256_file(RESOURCE))
        self.assertEqual(meta["generation_policy"]["max_new_tokens"], 128)
        self.assertEqual(meta["checkpoint_selection"], "one_preselected_checkpoint_no_epoch_search")

    def test_nested_infer_decoding_provenance_is_used_for_pairing(self):
        self.meta["decoding"] = {"max_new_tokens": 128, "num_beams": 1, "do_sample": False}
        self.write_run()
        baseline = self.run_eval()
        self.meta["decoding"]["num_beams"] = 2
        self.write_run()
        current = self.run_eval()
        self.assertEqual(current["metadata"]["generation_policy"]["num_beams"], 2)
        with self.assertRaisesRegex(ValueError, "generation_policy"):
            paired_comparison(current, baseline, resamples=0)

    def test_output_cannot_replace_input_even_with_explicit_overwrite(self):
        original = self.predictions.read_bytes()
        with self.assertRaisesRegex(ValueError, "differ"):
            main(["--manifest", str(self.manifest), "--split", "dev",
                  "--predictions", str(self.predictions),
                  "--output", str(self.predictions), "--overwrite"])
        self.assertEqual(self.predictions.read_bytes(), original)

    def test_legacy_prompt_provenance_is_explicit(self):
        self.meta.pop("prompt_sha256")
        self.write_run()
        report = self.run_eval()
        self.assertEqual(report["metadata"]["prompt_provenance"],
                         "legacy_metadata_current_source_fallback")

    def test_description_scores_are_explicit_lexical_diagnostics(self):
        self.meta["task"] = "description"
        self.pred_rows[0]["prediction"] = self.refs[0]["description"]
        self.write_run()
        report = self.run_eval(task="description")
        self.assertTrue(report["description_is_lexical_diagnostic"])
        self.assertEqual(report["per_clip"][0]["description_word_overlap_f1"], 1)
        self.assertEqual(word_overlap_f1("a b", "a c"), .5)
        self.assertEqual(word_overlap_f1("", ""), 0)

    def test_paired_deltas_negative_fraction_and_group_bootstrap(self):
        baseline = self.run_eval()
        self.pred_rows[0]["prediction"] = "anger, anxiety"
        self.pred_rows[2]["prediction"] = "anger"
        self.write_run()
        current = self.run_eval()
        result = paired_comparison(current, baseline, resamples=25, bootstrap_seed=42)
        self.assertAlmostEqual(result["negative_gain_fraction"], .25)
        self.assertAlmostEqual(result["positive_gain_fraction"], .25)
        self.assertEqual(result["bootstrap"]["independent_groups"], 3)
        self.assertEqual(result["bootstrap"]["resamples"], 25)
        self.assertEqual(result, paired_comparison(current, baseline, resamples=25, bootstrap_seed=42))
        self.assertAlmostEqual(result["delta"]["sample_macro_f1"], -1 / 12)

    def test_paired_different_protocols_and_references_rejected(self):
        baseline = self.run_eval()
        for field, replacement in (("seed", 7), ("prompt_sha256", "f" * 64),
                                   ("manifest_sha256", "f" * 64), ("resource_sha256", "f" * 64),
                                   ("generation_policy", {"max_new_tokens": 256})):
            changed = copy.deepcopy(baseline)
            changed["metadata"][field] = replacement
            with self.assertRaisesRegex(ValueError, field):
                paired_comparison(changed, baseline, resamples=0)
        changed = copy.deepcopy(baseline)
        changed["per_clip"][0]["reference_labels"] = ["sadness"]
        with self.assertRaisesRegex(ValueError, "references"):
            paired_comparison(changed, baseline, resamples=0)

    def test_original_format_audit_is_readonly_and_not_used(self):
        path = Path(__file__).resolve().parents[2] / "emotion_wheel/format.csv"
        before = sha256_file(path)
        audit = audit_original_format(path)
        self.assertFalse(audit["used_for_scoring"])
        self.assertIn("fear", audit["cross_polarity_shared_variants"])
        self.assertIn("feared", audit["cross_polarity_shared_variants"])
        self.assertEqual(sha256_file(path), before)

    def test_cli_reports_are_reviewable_and_refuse_implicit_overwrite(self):
        output = self.root / "scores.json"
        argv = ["--manifest", str(self.manifest), "--split", "dev",
                "--predictions", str(self.predictions), "--output", str(output)]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(argv), 0)
        report = json.loads(output.read_text())
        self.assertIn("per_clip", report)
        self.assertEqual(len(report["per_clip"]), 4)
        with self.assertRaises(FileExistsError):
            main(argv)


if __name__ == "__main__":
    unittest.main()


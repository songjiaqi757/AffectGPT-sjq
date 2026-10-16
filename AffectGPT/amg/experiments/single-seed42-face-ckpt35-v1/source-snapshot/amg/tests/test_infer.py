"""CPU-only inference input and dry-run tests; no media or model weights."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import torch
from amg.infer import (load_inference_records, prepare_generation_sample,
                       _validate_generation_override, canonical_dataset,
                       export_ovmerdplus_manifest, _build_input_builder, main)
from amg.runtime import sha256_file
from amg.data import QUESTION_MARKER
from amg.tests.test_data import CharacterTokenizer


class InputBuilder:
    def __init__(self):
        self.tokenizer = CharacterTokenizer()
        self.face_or_frame = "multiframe_audio_frame_text"
        self.max_length = 4096

    @staticmethod
    def func_get_qa_description(sample, question_only=False):
        assert question_only and sample == {}
        return "Describe emotion."

    @staticmethod
    def func_get_qa_ovlabel(sample, question_only=False):
        assert question_only and sample == {}
        return "List emotions."

    @staticmethod
    def get_prompt_for_multimodal(mode, subtitle, question):
        return "###Human: <Audio><AudioHere></Audio>. <Subtitle>" + subtitle + "</Subtitle>. " + QUESTION_MARKER + " " + question + " ###Assistant: "

    @staticmethod
    def replace_token_for_multimodal(prompt):
        return prompt.replace("<AudioHere>", "<AudioHere><AudioHere>")


class InferenceTests(unittest.TestCase):
    def test_manifest_uses_only_observed_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.jsonl"
            source = {"name": "clip", "subtitle": "observed", "group_id": "group",
                      "description": {"invalid_target": True}, "ovlabel": 123}
            path.write_text(json.dumps(source) + "\n")
            self.assertEqual(load_inference_records(path), [{"name": "clip", "subtitle": "observed", "group_id": "group"}])
            path.write_text((json.dumps(source) + "\n") * 2)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_inference_records(path)

    def test_prompt_is_target_free_and_has_bos_without_eos(self):
        row = {"name": "clip", "subtitle": "observed", "group_id": "group",
               "description": "SECRET_ANSWER", "ovlabel": "SECRET_LABEL"}
        builder = InputBuilder()
        with patch("amg.runtime.media_sample", side_effect=AssertionError("must not read media")):
            batch, prompt = prepare_generation_sample(builder, row, read_media=False)
        self.assertNotIn("SECRET", prompt)
        self.assertNotIn("labels", batch)
        self.assertEqual(batch["input_ids"][0, 0].item(), builder.tokenizer.bos_token_id)
        self.assertNotEqual(batch["input_ids"][0, -1].item(), builder.tokenizer.eos_token_id)
        position = batch["memory_insert_indices"].item()
        self.assertEqual(position, prompt.rfind(QUESTION_MARKER) + 1)
        self.assertEqual(batch["input_ids"][0, position].item(), ord("N") + 10)
        self.assertEqual(prompt.count("<AudioHere>"), 2)
        self.assertEqual(batch["subtitles"], ["observed"])

    def test_no_media_replacement_and_no_prompt_truncation(self):
        row = {"name": "requested", "subtitle": "observed", "group_id": "group"}
        with patch("amg.runtime.media_sample", side_effect=OSError("specific clip failed")):
            with self.assertRaisesRegex(OSError, "specific clip failed"):
                prepare_generation_sample(InputBuilder(), row)
        builder = InputBuilder()
        builder.max_length = 10
        with self.assertRaisesRegex(ValueError, "no silent truncation"):
            prepare_generation_sample(builder, row, read_media=False)

    def test_generation_budget_reserves_memory_and_output_and_trims_only_asr(self):
        row = {"name": "long", "subtitle": "x" * 100, "group_id": "group"}
        builder = InputBuilder()
        fixed = builder.replace_token_for_multimodal(builder.get_prompt_for_multimodal(
            builder.face_or_frame, "", "List emotions."))
        builder.max_length = len(fixed) + 1 + 7 + 13 + 5
        batch, prompt = prepare_generation_sample(builder, row, read_media=False,
                                                  memory_tokens=7, max_new_tokens=13)
        self.assertEqual(batch["input_ids"].shape[1] + 7 + 13, builder.max_length)
        self.assertEqual(prompt, fixed.replace("<Subtitle></Subtitle>", "<Subtitle>xxxxx</Subtitle>"))
        self.assertEqual(batch["subtitles"], [row["subtitle"]])
        budget = batch["budget_metadata"][0]
        self.assertEqual(budget["subtitle_tokens_original"], 100)
        self.assertEqual(budget["subtitle_tokens_truncated"], 95)
        self.assertEqual(budget["memory_tokens_reserved"], 7)
        self.assertEqual(budget["generation_tokens_reserved"], 13)
        self.assertEqual(budget["total_tokens_with_generation"], builder.max_length)
        self.assertEqual(batch["max_length"], builder.max_length)
        self.assertEqual(batch["task_types"], ["ovlabel"])
        self.assertEqual(batch["input_ids"][0, batch["memory_insert_indices"].item()].item(), ord("N") + 10)
        with self.assertRaisesRegex(ValueError, "only ASR"):
            prepare_generation_sample(builder, row, read_media=False,
                                      memory_tokens=7, max_new_tokens=builder.max_length)

    def test_dataset_aliases_and_flat_ov_face_paths_without_constructors(self):
        import config
        from my_affectgpt.datasets.datasets.mercaptionplus_dataset import MERCaptionPlus_Dataset
        from my_affectgpt.datasets.datasets.ovmerdplus_dataset import OVMERDPlus_Dataset
        model = SimpleNamespace(max_length=1024, llama_model="Qwen25",
            num_video_query_token=1, num_audio_query_token=1, num_multi_query_token=1,
            num_image_query_token=1, vis_processor=SimpleNamespace(train=SimpleNamespace(n_frms=8)))
        cfg = SimpleNamespace(model=model, datasets=SimpleNamespace(mercaptionplus=
                              SimpleNamespace(face_or_frame="multiframe_audio_frame_text")))
        with patch("amg.data.load_fast_training_tokenizer", return_value=CharacterTokenizer()), \
             patch.object(MERCaptionPlus_Dataset, "__init__", side_effect=AssertionError("no source constructor")), \
             patch.object(OVMERDPlus_Dataset, "__init__", side_effect=AssertionError("no labels constructor")):
            target = _build_input_builder(cfg, with_processors=False, dataset="OV-MERD+")
            source = _build_input_builder(cfg, with_processors=False, dataset="source")
        row = {"name": "clip"}
        self.assertEqual(target.dataset, "OVMERDPlus")
        self.assertEqual(target._get_video_path(row), str(Path(config.PATH_TO_RAW_VIDEO["OVMERDPlus"]) / "clip.mp4"))
        self.assertEqual(target._get_audio_path(row), str(Path(config.PATH_TO_RAW_AUDIO["OVMERDPlus"]) / "clip.wav"))
        self.assertEqual(target._get_face_path(row), str(Path(config.PATH_TO_RAW_FACE["OVMERDPlus"]) / "clip.npy"))
        self.assertEqual(source._get_face_path(row), str(Path(config.PATH_TO_RAW_FACE["MERCaptionPlus"]) / "clip/clip.npy"))
        self.assertEqual(canonical_dataset("OVMERDPlus"), "OVMERDPlus")
        self.assertEqual(canonical_dataset("MER-Caption+"), "MERCaptionPlus")

    def test_observed_export_preserves_empty_subtitles_and_no_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            csv = root / "subtitles.csv"
            csv.write_text('name,sentence\nclip1,"English, observed"\nclip2,\n')
            output = root / "observed.jsonl"
            metadata = export_ovmerdplus_manifest(output, subtitle_csv=csv, expected_count=2)
            rows = load_inference_records(output)
            self.assertEqual(rows[1], {"name": "clip2", "subtitle": "", "group_id": "clip2"})
            self.assertEqual(set(json.loads(output.read_text().splitlines()[0])), {"name", "subtitle", "group_id"})
            self.assertFalse(metadata["labels_read"])
            self.assertEqual(metadata["records"], 2)
            self.assertEqual(metadata["manifest_sha256"], sha256_file(output))
            with self.assertRaisesRegex(ValueError, "Expected 532"):
                export_ovmerdplus_manifest(root / "bad.jsonl", subtitle_csv=csv)

    def test_override_does_not_enable_unsaved_parameter_groups(self):
        _validate_generation_override("retrieval", "off")
        _validate_generation_override("retrieval", "random")
        _validate_generation_override("retrieval", "current")
        with self.assertRaises(ValueError):
            _validate_generation_override("off", "retrieval")
        with self.assertRaises(ValueError):
            _validate_generation_override("retrieval", "learned")

    def test_dry_run_checks_hashes_and_loads_no_model_or_media(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_path, baseline, checkpoint = root / "config.yaml", root / "base.pth", root / "amg.pth"
            manifest, output = root / "input.jsonl", root / "predictions.jsonl"
            config_path.write_text("fixture: true\n")
            baseline.write_bytes(b"hash-only baseline fixture")
            manifest.write_text(json.dumps({"name": "clip", "subtitle": "observed", "group_id": "group"}) + "\n")
            saved = {"mode": "off", "num_tokens": 4, "hidden_dim": 256, "memory_dropout": 0.2,
                     "train_peft": True, "base_checkpoint": str(baseline),
                     "base_sha256": sha256_file(baseline), "memory_bank": None, "memory_sha256": None,
                     "config_sha256": sha256_file(config_path), "face_or_frame": "multiframe_audio_frame_text"}
            torch.save({"schema": "amg-m0-train-v1", "model": {}, "config": saved}, checkpoint)
            cfg = SimpleNamespace(datasets=SimpleNamespace(mercaptionplus=SimpleNamespace(face_or_frame=saved["face_or_frame"])))
            args = ["--config", str(config_path), "--baseline-checkpoint", str(baseline),
                    "--amg-checkpoint", str(checkpoint), "--manifest", str(manifest),
                    "--output", str(output), "--device", "cuda:0", "--dry-run"]
            with patch("amg.runtime.load_config", return_value=cfg), \
                 patch("amg.runtime.load_base", side_effect=AssertionError("no model")) as load, \
                 patch("amg.runtime.media_sample", side_effect=AssertionError("no media")) as media, \
                 patch("amg.runtime.seed_all", side_effect=AssertionError("no CUDA seeding")), \
                 patch("amg.infer._build_input_builder", return_value=InputBuilder()), \
                 contextlib.redirect_stdout(io.StringIO()) as result:
                self.assertEqual(main(args), 0)
            load.assert_not_called()
            media.assert_not_called()
            dry_metadata = json.loads(result.getvalue())
            self.assertTrue(dry_metadata["dry_run"])
            self.assertEqual(dry_metadata["prompt_version"], "amg-source-question-v1")
            self.assertEqual(len(dry_metadata["prompt_sha256"]), 64)
            self.assertEqual(len(dry_metadata["infer_sha256"]), 64)
            self.assertEqual(len(dry_metadata["base_dataset_sha256"]), 64)
            self.assertEqual(dry_metadata["config_sha256"], sha256_file(config_path))
            self.assertEqual(dry_metadata["decoding"]["do_sample"], False)
            self.assertEqual(dry_metadata["decoding"]["num_beams"], 1)
            self.assertEqual(dry_metadata["previews"][0]["budget"]["memory_tokens_reserved"], 4)
            self.assertFalse(output.exists())
            long_builder = InputBuilder()
            long_builder.max_length = 10
            with patch("amg.runtime.load_config", return_value=cfg), \
                 patch("amg.infer._build_input_builder", return_value=long_builder), \
                 patch("amg.runtime.load_base", side_effect=AssertionError("no real model")), \
                 contextlib.redirect_stdout(io.StringIO()) as result:
                self.assertEqual(main(args), 1)
            dry = json.loads(result.getvalue())
            self.assertFalse(dry["validated"])
            self.assertEqual(dry["preview_errors"][0]["name"], "clip")
            self.assertIn("no silent truncation", dry["preview_errors"][0]["error"])

            class NoGenerationModel:
                def __init__(self, *args, **kwargs): pass
                def restore_trainable_state(self, state): pass
                def to(self, device): return self
                def eval(self): return self
                def generate_samples(self, *args, **kwargs):
                    raise AssertionError("long prompt must not enter generation")

            formal_args = [value for value in args if value != "--dry-run"]
            formal_args[formal_args.index("--device") + 1] = "cpu"
            with patch("amg.runtime.load_config", return_value=cfg), \
                 patch("amg.infer._build_input_builder", return_value=long_builder), \
                 patch("amg.runtime.load_base", return_value=None), \
                 patch("amg.model.AMGAffectGPT", NoGenerationModel), \
                 patch("amg.runtime.seed_all"), patch("amg.infer._stopping_criteria", return_value=[]), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(formal_args), 1)
            failure = json.loads(output.read_text())
            self.assertEqual(failure["name"], "clip")
            self.assertIn("no silent truncation", failure["error"])
            formal_metadata = json.loads((root / "predictions.meta.json").read_text())
            self.assertEqual(formal_metadata["errors"], 1)
            self.assertEqual(formal_metadata["preview_errors"][0]["name"], "clip")
            self.assertEqual(formal_metadata["target_denominator"], 1)
            self.assertEqual(formal_metadata["dataset"], "MERCaptionPlus")
            baseline.write_bytes(b"changed baseline")
            with patch("amg.runtime.load_config", return_value=cfg):
                with self.assertRaisesRegex(ValueError, "Baseline checkpoint SHA256"):
                    main(args)


if __name__ == "__main__":
    unittest.main()

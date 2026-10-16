"""CPU tests: reproducible manifests, prompt boundary and replacement identity."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import torch

from amg.manifest import (build_source_records, normalise_ovlabel, read_manifest,
                          sha256_file, split_records, write_manifests)
from amg.data import AMGTrainingDataset, QUESTION_MARKER, memory_insert_index
from amg.budget import budget_prompt
import config


class Encoded(dict):
    def __getattr__(self, key):
        return self[key]


class CharacterTokenizer:
    """Mock only tokenization; dataset prompt, retry and collation are real."""
    is_fast = True
    bos_token_id, eos_token_id, pad_token_id = 1, 2, 0

    def get_vocab(self):
        return {token: 3000 + index for index, token in enumerate((
            config.DEFAULT_IMAGE_PATCH_TOKEN, config.DEFAULT_AUDIO_PATCH_TOKEN,
            config.DEFAULT_FRAME_PATCH_TOKEN, config.DEFAULT_FACE_PATCH_TOKEN,
            config.DEFAULT_MULTI_PATCH_TOKEN))}

    def __call__(self, text, **kwargs):
        length = min(len(text), kwargs["max_length"]) if kwargs.get("truncation") else len(text)
        values = [ord(char) + 10 for char in text[:length]]
        offsets = [(index, index + 1) for index in range(length)]
        if kwargs.get("return_tensors") == "pt":
            result = Encoded(input_ids=torch.tensor([values], dtype=torch.long))
            if kwargs.get("return_offsets_mapping"):
                result["offset_mapping"] = torch.tensor([offsets], dtype=torch.long)
        else:
            result = Encoded(input_ids=values)
            if kwargs.get("return_offsets_mapping"):
                result["offset_mapping"] = offsets
        return result


def record(name, group_id=None, subtitle="observed subtitle"):
    return {"name": name, "group_id": group_id or name, "subtitle": subtitle,
            "description": f"private target for {name}", "ovlabel": "joy"}


class ManifestTests(unittest.TestCase):
    def test_source_roundtrip_full_retention_and_reproducible_sha(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rows = [record(f"clip{index}") for index in range(12)]
            for filename, columns, content in (
                ("track2_train_mercaptionplus.csv", ["name", "openset"],
                 [{"name": row["name"], "openset": "[joy, surprise]"} for row in rows]),
                ("track3_train_mercaptionplus.csv", ["name", "reason"],
                 [{"name": row["name"], "reason": row["description"]} for row in rows]),
                ("subtitle_chieng.csv", ["name", "english"],
                 [{"name": row["name"], "english": row["subtitle"]} for row in rows])):
                with (root / filename).open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.DictWriter(stream, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(content)
            output = root / "output"
            first = write_manifests(root, output, sizes=(4, 2, 2), expected_count=12)
            second = write_manifests(root, output, sizes=(4, 2, 2), expected_count=12)
            self.assertEqual(first["version_sha256"], second["version_sha256"])
            self.assertEqual(len(read_manifest(output / "main.jsonl")), 12)
            self.assertEqual(first["outputs"]["main"]["sha256"], sha256_file(output / "main.jsonl"))
            self.assertFalse(first["deduplication_claim"])
            self.assertEqual(first["group_policy"], "clip_id_only")
            with self.assertRaises(ValueError):
                build_source_records(root, expected_count=31327)

    def test_group_splits_do_not_share_groups(self):
        rows = [record(f"clip{index}", f"source{index // 2}") for index in range(20)]
        splits = split_records(rows, seed=42, sizes=(4, 2, 2))
        self.assertEqual(splits, split_records(rows, seed=42, sizes=(4, 2, 2)))
        groups = [{row["group_id"] for row in splits[key]} for key in ("fit", "dev", "holdout")]
        self.assertFalse(groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
        self.assertEqual([len(splits[key]) for key in ("fit", "dev", "holdout")], [4, 2, 2])

    def test_labels_and_duplicate_manifests(self):
        self.assertEqual(normalise_ovlabel("['concern', 'care']"), "concern, care")
        self.assertEqual(normalise_ovlabel("[]"), "neutral")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.jsonl"
            path.write_text((json.dumps(record("same")) + "\n") * 2)
            with self.assertRaises(ValueError):
                read_manifest(path)


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "samples.jsonl"
        self.rows = [record("bad", "group_bad"), record("good", "group_good", "ASR only, no target")]
        self.path.write_text("".join(json.dumps(row) + "\n" for row in self.rows))
        self.tokenizer = CharacterTokenizer()
        self.model_cfg = SimpleNamespace(max_length=4096, num_video_query_token=1,
                                         num_audio_query_token=1, num_multi_query_token=1,
                                         num_image_query_token=1, llama_model="Qwen25",
                                         vis_processor=SimpleNamespace(train=SimpleNamespace(n_frms=8)))
        self.dataset_cfg = SimpleNamespace(label_type="description", face_or_frame="multiframe_audio_frame_text")

    def dataset(self, max_retries=2):
        return AMGTrainingDataset(dataset_cfg=self.dataset_cfg, model_cfg=self.model_cfg,
                                  manifest_path=self.path, tokenizer=self.tokenizer,
                                  max_retries=max_retries)

    def test_constructor_does_not_read_media(self):
        with patch.object(AMGTrainingDataset, "read_frame_face_audio_text", side_effect=AssertionError("read")) as read:
            dataset = self.dataset()
        read.assert_not_called()
        self.assertEqual(len(dataset), 2)

    def test_replacement_metadata_and_collated_insertion(self):
        dataset = self.dataset()

        def media(video_path, *args):
            if Path(video_path).stem == "bad":
                raise OSError("corrupt media fixture")
            return {key: torch.zeros(1) for key in ("face", "raw_face", "frame", "raw_frame", "audio", "raw_audio", "image", "raw_image")}

        dataset.read_frame_face_audio_text = media
        with patch("amg.data.random.randint", return_value=1):
            sample = dataset[0]
        self.assertEqual((sample["original_id"], sample["actual_id"], sample["clip_id"]), ("bad", "good", "good"))
        self.assertEqual(sample["group_id"], "group_good")
        self.assertEqual(sample["subtitle"], "ASR only, no target")
        self.assertNotIn("private target", sample["subtitle"])
        self.assertTrue(sample["was_replaced"])
        self.assertEqual(sample["replacement_failures"][0]["clip_id"], "bad")
        batch = dataset.collater([sample])
        self.assertEqual(batch["clip_ids"], ["good"])
        self.assertEqual(batch["original_ids"], ["bad"])
        self.assertEqual(batch["group_ids"], ["group_good"])
        self.assertEqual(batch["subtitles"], ["ASR only, no target"])
        position = batch["memory_insert_indices"].item()
        self.assertEqual(batch["input_ids"][0, position].item(), ord("N") + 10)
        self.assertEqual(batch["labels"][0, position].item(), config.IGNORE_INDEX)
        self.assertEqual(batch["input_ids"][0, 0].item(), self.tokenizer.bos_token_id)
        self.assertIn("raw_audios", batch)
        self.assertEqual(batch["task_types"], ["description"])
        self.assertEqual(batch["max_length"], dataset.max_length)
        self.assertEqual(batch["budget_metadata"][0]["subtitle_tokens_original"], len(sample["subtitle"]))

    def test_training_budget_preserves_full_target_instruction_modalities_and_bos_eos(self):
        dataset = self.dataset(max_retries=1)
        dataset.read_frame_face_audio_text = lambda *args: {}
        dataset.annotation[0]["subtitle"] = "ASR " * 100
        dataset.memory_tokens = 11  # CLI can reserve a non-default memory width.
        qa = dataset.get_qa_pairs(dataset.dataset, "description", dataset.annotation[0])
        fixed = dataset.replace_token_for_multimodal(dataset.get_prompt_for_multimodal(
            dataset.face_or_frame, "", qa["question"]))
        expected_target = self.tokenizer(qa["answer"] + "###")["input_ids"]
        dataset.max_length = len(fixed) + len(expected_target) + 2 + dataset.memory_tokens + 23
        sample = dataset[0]
        batch = dataset.collater([sample])
        budget = sample["budget_metadata"]
        self.assertEqual(budget["subtitle_tokens_original"], 400)
        self.assertEqual(budget["subtitle_tokens_kept"], 23)
        self.assertEqual(budget["subtitle_tokens_truncated"], 377)
        self.assertEqual(budget["memory_tokens_reserved"], 11)
        self.assertEqual(budget["bos_tokens"] + budget["eos_tokens"], 2)
        self.assertEqual(budget["final_tokens_with_memory"], dataset.max_length)
        self.assertEqual(batch["input_ids"].shape[1] + 11, dataset.max_length)
        supervised = sample["label"][sample["label"].ne(config.IGNORE_INDEX)].tolist()
        self.assertEqual(supervised, expected_target)
        prompt_ids = sample["text_input"][:-len(expected_target)].tolist()
        prompt = "".join(chr(value - 10) for value in prompt_ids)
        self.assertIn(QUESTION_MARKER + " " + qa["question"] + " ###Assistant: ", prompt)
        for token in ("<MultiHere>", "<AudioHere>", "<FrameHere>"):
            self.assertEqual(prompt.count(token), fixed.count(token))
        self.assertEqual(sample["subtitle"], "ASR " * 100)
        self.assertEqual(batch["input_ids"][0, 0].item(), self.tokenizer.bos_token_id)
        self.assertEqual(batch["labels"][0, -1].item(), self.tokenizer.eos_token_id)

    def test_fixed_content_cannot_be_truncated_to_squeeze_in_target(self):
        dataset = self.dataset(max_retries=1)
        dataset.read_frame_face_audio_text = lambda *args: {}
        dataset.max_length = 30
        with self.assertRaisesRegex(RuntimeError, "full target.*only ASR"):
            dataset[0]

    def test_shared_budget_reencodes_boundaries_and_is_unchanged_when_short(self):
        render = lambda subtitle: "AV" + subtitle + "TASK"
        unchanged = budget_prompt(self.tokenizer, render, "abc", max_length=30,
                                  target_tokens=5, bos_tokens=1, eos_tokens=1, memory_tokens=4)
        self.assertEqual(unchanged.prompt, "AVabcTASK")
        self.assertEqual(unchanged.metadata["subtitle_tokens_truncated"], 0)
        limited = budget_prompt(self.tokenizer, render, "x" * 50, max_length=30,
                                bos_tokens=1, memory_tokens=7, generation_tokens=12)
        self.assertEqual(limited.prompt, "AVxxxxTASK")
        self.assertEqual(limited.metadata["total_tokens_with_generation"], 30)
        self.assertEqual(limited.metadata["subtitle_tokens_truncated"], 46)
        with self.assertRaisesRegex(ValueError, "integer"):
            budget_prompt(self.tokenizer, render, "x", max_length=30.0)
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            budget_prompt(self.tokenizer, render, "x", max_length=30, memory_tokens=-1)

    def test_retry_exhaustion_reports_ids(self):
        dataset = self.dataset(max_retries=1)
        dataset.read_frame_face_audio_text = lambda *args: (_ for _ in ()).throw(OSError("broken"))
        with self.assertRaisesRegex(RuntimeError, "requested=bad"):
            dataset[0]

    def test_offsets_use_last_marker_and_explicit_bos(self):
        prompt = "subtitle: " + QUESTION_MARKER + " quoted. " + QUESTION_MARKER + " Actual task"
        start = prompt.rfind(QUESTION_MARKER)
        self.assertEqual(memory_insert_index(self.tokenizer, prompt), start + 1)
        self.assertEqual(memory_insert_index(self.tokenizer, prompt, bos_offset=0), start)
        with self.assertRaisesRegex(ValueError, "truncated"):
            memory_insert_index(self.tokenizer, prompt, max_length=5)
        with self.assertRaisesRegex(ValueError, "does not contain"):
            memory_insert_index(self.tokenizer, "missing marker")


if __name__ == "__main__":
    unittest.main()

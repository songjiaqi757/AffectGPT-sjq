"""Small CPU fixtures for strict manifest traversal and versioned bank output."""
import json
from concurrent.futures import ThreadPoolExecutor
import threading
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import torch
from torch import nn

from amg.build_memory import FrozenAVExtractor, build_bank
from amg.memory import MemoryBank
from amg.runtime import sha256_file


class FakeReader:
    needed_data = ["face", "audio"]
    def __init__(self):
        self.seen = []
    def _get_video_path(self, record):
        return record["name"]
    def read_frame_face_audio_text(self, video, face, audio, image):
        self.seen.append(video)
        return {"clip_id": video}


class FakeExtractor:
    def __init__(self, fail_id=None):
        self.fail_id = fail_id
    def __call__(self, media, device):
        if media["clip_id"] == self.fail_id:
            raise IOError("deliberate fixture read failure")
        return torch.ones(768), torch.ones(1024), True, True


class ConcurrentReader(FakeReader):
    """Force clip-b to finish before clip-a without timing-based sleeps."""
    def __init__(self, fail_id=None):
        super().__init__()
        self.fail_id = fail_id
        self.second_ready = threading.Event()
        self.lock = threading.Lock()
        self.completed = []

    def read_frame_face_audio_text(self, video, face, audio, image):
        with self.lock:
            self.seen.append(video)
        if video == "clip-a":
            if not self.second_ready.wait(timeout=5):
                raise AssertionError("The second media read never ran concurrently")
        with self.lock:
            self.completed.append(video)
        if video == "clip-b":
            self.second_ready.set()
        if video == self.fail_id:
            raise IOError("deliberate parallel read failure")
        return {"clip_id": video}


class TrackingExtractor:
    def __init__(self, clip_ids, fail_id=None):
        self.clip_ids = clip_ids
        self.fail_id = fail_id
        self.seen = []
        self.thread_ids = []
        self.on_first = None

    def __call__(self, media, device):
        name = media["clip_id"]
        if not self.seen and self.on_first is not None:
            self.on_first()
        self.seen.append(name)
        self.thread_ids.append(threading.get_ident())
        if name == self.fail_id:
            raise IOError("deliberate parallel extraction failure")
        index = self.clip_ids.index(name)
        visual, audio = torch.zeros(768), torch.zeros(1024)
        visual[index], audio[index] = 1.0, 1.0
        return visual, audio, True, True


class StubEncoder(nn.Module):
    def __init__(self, dimension):
        super().__init__()
        self.hidden_size = dimension
        self.scale = nn.Parameter(torch.ones(dimension))
        self.dropout = nn.Dropout(0.9)
    def forward(self, processed, raw):
        return self.dropout(torch.ones(1, 2, self.hidden_size) * self.scale)


class BuildMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="amg-bank-test-")
        self.root = Path(self.temp.name)
        self.config = self.root / "config.yaml"
        self.config.write_text("""model:
  visual_encoder: CLIP_VIT_LARGE
  acoustic_encoder: HUBERT_LARGE
  vis_processor:
    train:
      n_frms: 8
datasets:
  mercaptionplus:
    face_or_frame: multiface_audio_face_text
""")
        self.manifest = self.root / "main.jsonl"
        rows = [{"name": name, "group_id": name, "subtitle": "ASR",
                 "description": "ANSWER MUST NOT ENTER ENCODER", "ovlabel": "happy"}
                for name in ("clip-a", "clip-b", "clip-c")]
        self.manifest.write_text("".join(json.dumps(r) + "\n" for r in rows))
        self.reader = FakeReader()
    def tearDown(self):
        self.temp.cleanup()
    def run_build(self, name, *, limit=None, fail_id=None):
        return build_bank(self.config, self.manifest, self.root / name, limit=limit,
            reader_loader=lambda cfg: self.reader,
            extractor_loader=lambda cfg, needed, device: (FakeExtractor(fail_id), {"fixture": True}))

    def test_full_bank_preserves_order_and_checksums(self):
        meta = self.run_build("full.pt")
        bank = MemoryBank.load(self.root / "full.pt", expected_version=meta["version"])
        self.assertEqual(bank.clip_ids, ["clip-a", "clip-b", "clip-c"])
        self.assertEqual(self.reader.seen, bank.clip_ids)
        self.assertTrue(meta["complete"])
        self.assertFalse(meta["partial_for_testing"])
        self.assertEqual(meta["records"], meta["total_manifest_records"])
        self.assertEqual(meta["bank_sha256"], sha256_file(self.root / "full.pt"))
        self.assertEqual(meta["manifest_sha256"], sha256_file(self.manifest))
        self.assertEqual(json.loads((self.root / "full.pt.json").read_text()), meta)
        self.assertEqual(meta["schema"], "amg-m0-bank-v1")

    def test_limit_cannot_claim_complete_even_when_it_covers_all_rows(self):
        meta = self.run_build("limited.pt", limit=99)
        self.assertEqual(meta["records"], 3)
        self.assertFalse(meta["complete"])
        self.assertTrue(meta["partial_for_testing"])

    def test_failure_aborts_without_replacement_or_output(self):
        with self.assertRaisesRegex(RuntimeError, "row 2, clip_id=clip-b"):
            self.run_build("failure.pt", fail_id="clip-b")
        self.assertEqual(self.reader.seen, ["clip-a", "clip-b"])
        self.assertFalse((self.root / "failure.pt").exists())
        self.assertFalse((self.root / "failure.pt.json").exists())

    def test_limit_only_extracts_requested_prefix(self):
        meta = self.run_build("one.pt", limit=1)
        self.assertEqual(self.reader.seen, ["clip-a"])
        self.assertEqual(meta["records"], 1)
        self.assertEqual(meta["total_manifest_records"], 3)
        self.assertFalse(meta["complete"])
        with self.assertRaises(FileExistsError):
            self.run_build("one.pt", limit=1)

    def test_parallel_out_of_order_reads_keep_bank_mapping_and_bounded_queue(self):
        names = ["clip-" + chr(ord("a") + index) for index in range(12)]
        rows = [{"name": name, "group_id": name, "subtitle": "ASR",
                 "description": "private", "ovlabel": "happy"} for name in names]
        self.manifest.write_text("".join(json.dumps(row) + "\n" for row in rows))
        reader = ConcurrentReader()
        extractor = TrackingExtractor(names)
        caller_thread = threading.get_ident()
        submitted = []

        class RecordingPool(ThreadPoolExecutor):
            def submit(self, fn, *args, **kwargs):
                submitted.append(args[-1]["name"])
                return super().submit(fn, *args, **kwargs)

        # Two pending reads plus the current clip, rather than the full manifest.
        extractor.on_first = lambda: self.assertEqual(len(submitted), 3)
        with patch("amg.build_memory.ThreadPoolExecutor", RecordingPool):
            meta = build_bank(self.config, self.manifest, self.root / "parallel.pt", workers=2,
                reader_loader=lambda cfg: reader,
                extractor_loader=lambda cfg, needed, device: (extractor, {"fixture": True}))
        bank = MemoryBank.load(self.root / "parallel.pt")
        self.assertEqual(reader.completed[0], "clip-b")
        self.assertEqual(bank.clip_ids, names)
        self.assertEqual(bank.group_ids, names)
        self.assertEqual(extractor.seen, names)
        self.assertEqual(extractor.thread_ids, [caller_thread] * len(names))
        self.assertEqual(sorted(reader.seen), sorted(names))
        self.assertEqual(len(reader.seen), len(names))
        self.assertEqual(bank.features[:, :768].argmax(1).tolist(), list(range(len(names))))
        self.assertEqual(bank.features[:, 768:].argmax(1).tolist(), list(range(len(names))))
        self.assertTrue(bank.valid_mask.all())
        self.assertTrue(meta["complete"])
        self.assertEqual(meta["feature_contract"], "original-prefusion-hidden-float32-global-mean-v1")

    def test_parallel_read_failure_aborts_in_manifest_order_without_outputs(self):
        names = ["clip-a", "clip-b", "clip-c"]
        reader = ConcurrentReader(fail_id="clip-b")
        extractor = TrackingExtractor(names)
        with self.assertRaisesRegex(RuntimeError, "row 2, clip_id=clip-b.*parallel read failure"):
            build_bank(self.config, self.manifest, self.root / "read-failure.pt", workers=2,
                reader_loader=lambda cfg: reader,
                extractor_loader=lambda cfg, needed, device: (extractor, {"fixture": True}))
        self.assertEqual(extractor.seen, ["clip-a"])
        self.assertEqual(reader.completed[0], "clip-b")
        self.assertEqual(len(reader.seen), len(set(reader.seen)))
        self.assertFalse((self.root / "read-failure.pt").exists())
        self.assertFalse((self.root / "read-failure.pt.json").exists())

    def test_parallel_extraction_failure_never_extracts_later_clips(self):
        names = ["clip-a", "clip-b", "clip-c"]
        reader = ConcurrentReader()
        extractor = TrackingExtractor(names, fail_id="clip-b")
        with self.assertRaisesRegex(RuntimeError, "row 2, clip_id=clip-b.*parallel extraction failure"):
            build_bank(self.config, self.manifest, self.root / "extract-failure.pt", workers=4,
                reader_loader=lambda cfg: reader,
                extractor_loader=lambda cfg, needed, device: (extractor, {"fixture": True}))
        self.assertEqual(extractor.seen, ["clip-a", "clip-b"])
        self.assertFalse((self.root / "extract-failure.pt").exists())
        self.assertFalse((self.root / "extract-failure.pt.json").exists())

    def test_extractor_is_frozen_eval_and_pools_original_hidden(self):
        visual, audio = StubEncoder(768), StubEncoder(1024)
        extractor = FrozenAVExtractor(visual, audio, ["face", "audio"])
        extractor.train()
        self.assertFalse(visual.training)
        self.assertFalse(audio.training)
        self.assertFalse(any(p.requires_grad for p in extractor.parameters()))
        media = {key: torch.ones(2, 2) for key in ("face", "raw_face", "audio", "raw_audio")}
        v, a, vv, av = extractor(media, "cpu")
        torch.testing.assert_close(v, torch.ones(768))
        torch.testing.assert_close(a, torch.ones(1024))
        self.assertTrue(vv and av)
        self.assertFalse(v.requires_grad)
        with self.assertRaisesRegex(ValueError, "Missing required face"):
            extractor({}, "cpu")


if __name__ == "__main__":
    unittest.main()

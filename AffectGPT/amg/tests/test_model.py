"""CPU integration checks independent of AffectGPT model downloads and GPUs."""
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

import torch
from torch import nn
import torch.nn.functional as F

from amg.memory import MemoryBank
from amg.model import AMGAffectGPT


class FakeLLM(nn.Module):
    """Tiny causal recurrence: answer loss depends on preceding memory tokens."""
    def __init__(self, dim=12, vocab=32):
        super().__init__()
        self.embedding = nn.Embedding(vocab, dim)
        self.output = nn.Linear(dim, vocab)
        self.lora_delta = nn.Parameter(torch.eye(dim) * 0.03)
        self.last_call = None
        self.generation_call = None

    def get_input_embeddings(self):
        return self.embedding

    def forward(self, inputs_embeds, attention_mask, labels=None,
                position_ids=None, return_dict=True):
        b, width, _ = inputs_embeds.shape
        if position_ids is None:
            position_ids = torch.arange(width, device=inputs_embeds.device).expand(b, -1)
        self.last_call = (inputs_embeds, attention_mask, position_ids, labels)
        positional = position_ids[..., None].to(inputs_embeds.dtype) * 0.01
        hidden = torch.cumsum((inputs_embeds + positional) * attention_mask[..., None], dim=1)
        hidden = hidden + hidden @ self.lora_delta
        logits = self.output(hidden)
        loss = None
        if labels is not None:
            loss = F.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]),
                                   labels[:, 1:].reshape(-1), ignore_index=-100)
        return SimpleNamespace(loss=loss, logits=logits)

    def generate(self, **kwargs):
        self.generation_call = kwargs
        return torch.tensor([[7, 8]], device=kwargs["inputs_embeds"].device)


class FakeBase(nn.Module):
    FRAME_PATCH_TOKEN_ID = 100
    FACE_PATCH_TOKEN_ID = 101
    AUDIO_PATCH_TOKEN_ID = 102
    IMAGE_PATCH_TOKEN_ID = 103
    MULTI_PATCH_TOKEN_ID = 104

    def __init__(self):
        super().__init__()
        self.llama_model = FakeLLM()
        self.llama_tokenizer = SimpleNamespace(pad_token_id=0)
        self.visual_encoder = nn.Sequential(nn.Linear(5, 768), nn.Dropout(0.5))
        self.acoustic_encoder = nn.Sequential(nn.Linear(7, 1024), nn.Dropout(0.5))
        self.visual_proj = nn.Linear(768, 12)
        self.audio_proj = nn.Linear(1024, 12)
        self.multi_proj = nn.Linear(1792, 12)

    def maybe_autocast(self):
        return nullcontext()

    def encode_video_merge(self, values, raw_values):
        raw = self.visual_encoder(values)
        return raw, self.visual_proj(raw.mean(1))[:, None].expand(-1, 2, -1)

    encode_image_merge = encode_video_merge

    def encode_audio_merge(self, values, raw_values):
        raw = self.acoustic_encoder(values)
        return raw, self.audio_proj(raw.mean(1))[:, None].expand(-1, 2, -1)

    def encode_multi_merge(self, visual, audio):
        raw = torch.cat([visual.mean(1), audio.mean(1)], -1)
        return raw, self.multi_proj(raw)[:, None].expand(-1, 2, -1)

    def forward(self, samples):
        """Reproduce the original replace-in-place path without AMG assembly."""
        vr, vl = self.encode_video_merge(samples["frames"], samples["raw_frames"])
        ar, al = self.encode_audio_merge(samples["audios"], samples["raw_audios"])
        _, ml = self.encode_multi_merge(vr, ar)
        replacements = {self.FRAME_PATCH_TOKEN_ID: vl,
                        self.AUDIO_PATCH_TOKEN_ID: al,
                        self.MULTI_PATCH_TOKEN_ID: ml}
        ids = samples["input_ids"]
        safe = ids.clone()
        for key in replacements:
            safe[ids == key] = 0
        embeds = self.llama_model.get_input_embeddings()(safe)
        for row in range(ids.shape[0]):
            for key, values in replacements.items():
                positions = ids[row].eq(key)
                if bool(positions.any()):
                    embeds[row, positions] = values[row]
        return {"loss": self.llama_model(inputs_embeds=embeds,
                         attention_mask=samples["attention_masks"],
                         labels=samples["labels"]).loss}


def make_samples(batch=1, fused=False, dtype=torch.float32):
    if fused:
        ids = [1, 104, 104, 3, 0, 0]
        mask = [1, 1, 1, 1, 0, 0]
        labels = [-100, -100, -100, 3, 0, -100]
    else:
        ids = [1, 100, 100, 2, 102, 102, 3, 0]
        mask = [1, 1, 1, 1, 1, 1, 1, 0]
        labels = [-100, -100, -100, -100, -100, -100, 3, 0]
    return {"input_ids": torch.tensor([ids] * batch),
            "attention_masks": torch.tensor([mask] * batch),
            "labels": torch.tensor([labels] * batch),
            "frames": torch.randn(batch, 3, 5, dtype=dtype),
            "raw_frames": torch.empty(0),
            "audios": torch.randn(batch, 3, 7, dtype=dtype),
            "raw_audios": torch.empty(0),
            "face_or_frame": "multiframe" if fused else "frame",
            "clip_ids": ["q"] * batch,
            "group_ids": ["g"] * batch,
            "memory_insert_indices": torch.full((batch,), 3, dtype=torch.long)}


def make_bank():
    return MemoryBank(torch.randn(5, 768), torch.randn(5, 1024),
                      ["q", "sibling", "a", "b", "c"], ["g", "g", "h", "i", "j"])


class ModelTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(41)

    def test_off_matches_independent_original_forward_including_masked_eos(self):
        for fused in (False, True):
            with self.subTest(fused=fused):
                base = FakeBase().eval()
                model = AMGAffectGPT(base, memory_mode="off", hidden_dim=16).eval()
                samples = make_samples(batch=2, fused=fused)
                expected = base(samples)["loss"]
                result = model(samples)
                torch.testing.assert_close(result["loss"], expected, rtol=0, atol=0)
                self.assertEqual(result["memory_enabled"].tolist(), [False, False])
                self.assertIsNone(result["retrieved_ids"])
                self.assertEqual(result["input_lengths"].tolist(), [5 if fused else 8] * 2)
                self.assertEqual(result["attended_lengths"].tolist(), [4 if fused else 7] * 2)
                assembled, _, _ = model.prepare(samples)
                self.assertEqual(assembled.labels[0, assembled.lengths[0] - 1].item(), 0)
                self.assertEqual(assembled.attention_mask[0, assembled.lengths[0] - 1].item(), 0)

    def test_retrieval_loss_reaches_adapter_and_lora_but_not_frozen_base(self):
        model = AMGAffectGPT(FakeBase(), make_bank(), hidden_dim=16, memory_dropout=0.0)
        model.train()
        result = model(make_samples(fused=True))
        self.assertEqual(result["memory_enabled"].tolist(), [True])
        self.assertEqual(set(x for x in result["retrieved_ids"][0] if x), {"a", "b", "c"})
        result["loss"].backward()
        for p in (model.memory_adapter.queries,
                  model.memory_adapter.output_projection[1].weight,
                  model.memory_adapter.gate_projection.weight,
                  model.base.llama_model.lora_delta):
            self.assertIsNotNone(p.grad)
            self.assertGreater(float(p.grad.abs().sum()), 0)
        for name, p in model.base.named_parameters():
            if "lora_" not in name:
                self.assertFalse(p.requires_grad)
                self.assertIsNone(p.grad)

    def test_train_freezes_av_dropout_and_exact_parameter_scope(self):
        for train_peft in (False, True):
            with self.subTest(train_peft=train_peft):
                model = AMGAffectGPT(FakeBase(), make_bank(), hidden_dim=16,
                                     train_peft=train_peft)
                model.train()
                self.assertFalse(model.base.visual_encoder.training)
                self.assertFalse(model.base.acoustic_encoder.training)
                self.assertEqual(model.base.llama_model.training, train_peft)
                self.assertFalse(model.base.training)
                trainable = set(model.trainable_state())
                self.assertEqual("base.llama_model.lora_delta" in trainable, train_peft)
                self.assertNotIn("learned_tokens", trainable)
                self.assertTrue(all(name.startswith("memory_adapter.") or
                                    (train_peft and "lora_" in name) for name in trainable))
        off = AMGAffectGPT(FakeBase(), memory_mode="off", hidden_dim=16, train_peft=False)
        self.assertEqual(off.trainable_state(), {})
        learned = AMGAffectGPT(FakeBase(), memory_mode="learned", hidden_dim=16, train_peft=False)
        self.assertEqual(set(learned.trainable_state()), {"learned_tokens"})

    def test_fp16_base_keeps_only_trainable_lora_in_float32(self):
        model = AMGAffectGPT(FakeBase().half(), make_bank(), hidden_dim=16)
        self.assertEqual(model.base.llama_model.lora_delta.dtype, torch.float32)
        self.assertTrue(model.base.llama_model.lora_delta.requires_grad)
        self.assertEqual(model.base.llama_model.embedding.weight.dtype, torch.float16)
        self.assertEqual(model.base.visual_encoder[0].weight.dtype, torch.float16)
        self.assertFalse(model.base.visual_encoder[0].weight.requires_grad)
        frozen = AMGAffectGPT(FakeBase().half(), memory_mode="off",
                              hidden_dim=16, train_peft=False)
        self.assertEqual(frozen.base.llama_model.lora_delta.dtype, torch.float16)

    def test_learned_memory_uses_same_per_sample_dropout_as_retrieval(self):
        model = AMGAffectGPT(FakeBase(), memory_mode="learned",
                             hidden_dim=16, memory_dropout=1.0)
        model.train()
        dropped, _, _ = model.prepare(make_samples(batch=2))
        self.assertEqual(dropped.memory_enabled.tolist(), [False, False])
        self.assertEqual(dropped.lengths.tolist(), [8, 8])
        model.eval()
        enabled, _, _ = model.prepare(make_samples(batch=2))
        self.assertEqual(enabled.memory_enabled.tolist(), [True, True])
        self.assertEqual(enabled.lengths.tolist(), [12, 12])

    def test_training_retrieval_rejects_missing_identity(self):
        model = AMGAffectGPT(FakeBase(), make_bank(), hidden_dim=16)
        for key in ("clip_ids", "group_ids"):
            with self.subTest(missing=key):
                samples = make_samples()
                del samples[key]
                with self.assertRaisesRegex(ValueError, "clip_ids and group_ids"):
                    model(samples)

    def test_generation_requires_eval_and_single_example_and_uses_eval_retrieval(self):
        model = AMGAffectGPT(FakeBase(), make_bank(), hidden_dim=16)
        with self.assertRaisesRegex(RuntimeError, "eval"):
            model.generate_samples(make_samples())
        model.eval()
        with self.assertRaisesRegex(ValueError, "single-example"):
            model.generate_samples(make_samples(batch=2))
        output, report = model.generate_samples(make_samples(fused=True), max_new_tokens=2)
        self.assertEqual(output.tolist(), [[7, 8]])
        self.assertEqual(report["memory_enabled"], [True])
        self.assertIn("q", report["retrieved_ids"][0])
        self.assertEqual(model.base.llama_model.generation_call["max_new_tokens"], 2)
        self.assertNotIn("labels", model.base.llama_model.generation_call)
        self.assertNotIn("position_ids", model.base.llama_model.generation_call)

    def test_generation_budget_counts_memory_and_masked_eos(self):
        model = AMGAffectGPT(FakeBase(), make_bank(), hidden_dim=16).eval()
        samples = make_samples(fused=True)
        samples["max_length"] = 11
        model.generate_samples(samples, max_new_tokens=2)
        result = model(samples)
        self.assertEqual(result["input_lengths"].tolist(), [9])
        self.assertEqual(result["attended_lengths"].tolist(), [8])
        # Inference has no supervised EOS, so its retained prompt is 8 tokens.
        samples["max_length"] = 9
        with self.assertRaisesRegex(ValueError, "generation exceeds"):
            model.generate_samples(samples, max_new_tokens=2)
        with self.assertRaisesRegex(ValueError, "explicit max_new_tokens"):
            model.generate_samples(samples)
        samples["max_length"] = 8
        with self.assertRaisesRegex(ValueError, "max_length"):
            model(samples)

    def test_trainable_checkpoint_is_snapshot_and_weights_only_roundtrips(self):
        model = AMGAffectGPT(FakeBase(), make_bank(), hidden_dim=16)
        snapshot = model.trainable_state()
        stored = {name: value.clone() for name, value in snapshot.items()}
        with torch.no_grad():
            for p in model.parameters():
                if p.requires_grad:
                    p.add_(1)
        for name in snapshot:
            torch.testing.assert_close(snapshot[name], stored[name], rtol=0, atol=0)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trainable.pt"
            torch.save(snapshot, path)
            loaded = torch.load(path, weights_only=True)
            model.restore_trainable_state(loaded)
        current = model.trainable_state()
        for name in snapshot:
            torch.testing.assert_close(current[name], snapshot[name], rtol=0, atol=0)
        with self.assertRaisesRegex(ValueError, "mismatch"):
            model.restore_trainable_state({})
        corrupt = dict(snapshot)
        first = next(iter(corrupt))
        corrupt[first] = torch.zeros(1)
        with self.assertRaisesRegex(ValueError, "shape mismatch"):
            model.restore_trainable_state(corrupt)

    def test_adapter_converts_retrieved_float32_to_module_dtype(self):
        model = AMGAffectGPT(FakeBase().double(), make_bank(), hidden_dim=16,
                             memory_dropout=0.0).double().eval()
        assembled, result, _ = model.prepare(make_samples(dtype=torch.float64))
        self.assertEqual(result.values.dtype, torch.float32)
        self.assertEqual(assembled.inputs_embeds.dtype, torch.float64)
        self.assertTrue(bool(torch.isfinite(model(make_samples(dtype=torch.float64))["loss"])))

    def test_no_placeholder_media_is_not_an_error_but_missing_media_is(self):
        model = AMGAffectGPT(FakeBase(), make_bank(), hidden_dim=16).eval()
        # Fused mode computes AV raw features although only MULTI enters the LLM.
        model(make_samples(fused=True))
        sample = make_samples()
        del sample["frames"]
        del sample["raw_frames"]
        with self.assertRaisesRegex(ValueError, "frame placeholder"):
            model(sample)


if __name__ == "__main__":
    unittest.main()


import tempfile
import unittest
from pathlib import Path

import torch
from torch import nn

from amg.memory import MemoryBank, MemoryAdapter, VISUAL_DIM, AUDIO_DIM


def axis(n, dim, index=0):
    out = torch.zeros(n, dim)
    out[:, index] = 1
    return out


class MemoryBankTests(unittest.TestCase):
    def test_training_filters_all_duplicate_ids_and_same_group_only_when_requested(self):
        bank = MemoryBank(axis(5, VISUAL_DIM), axis(5, AUDIO_DIM),
                          ["q", "q", "sibling", "other", "unknown"],
                          ["g", "g", "g", "h", None])
        train = bank.retrieve(axis(1, VISUAL_DIM), axis(1, AUDIO_DIM),
                              clip_ids=["q"], group_ids=["g"], training=True)
        self.assertEqual(set(x for x in train.ids[0] if x), {"other", "unknown"})
        self.assertEqual(int(train.mask.sum()), 2)
        inferred_group = bank.retrieve(axis(1, VISUAL_DIM), axis(1, AUDIO_DIM),
                                       clip_ids=["q"], training=True)
        self.assertEqual(set(x for x in inferred_group.ids[0] if x), {"other", "unknown"})
        inference = bank.retrieve(axis(1, VISUAL_DIM), axis(1, AUDIO_DIM),
                                  clip_ids=["q"], group_ids=["g"])
        self.assertEqual(int(inference.mask.sum()), 5)
        self.assertIn("q", inference.ids[0])
        with self.assertRaisesRegex(ValueError, "requires query clip_ids"):
            bank.retrieve(axis(1, VISUAL_DIM), None, training=True)

    def test_equal_weight_cosine_and_missing_modalities(self):
        visual = axis(3, VISUAL_DIM)
        audio = axis(3, AUDIO_DIM)
        audio[0] *= -1
        visual[1, 0], visual[1, 1] = 0.6, 0.8
        audio[1, 0], audio[1, 1] = 0.6, 0.8
        bank = MemoryBank(visual * 3, audio * 7, ["both_disagree", "both_ok", "visual_only"],
                          audio_valid=torch.tensor([True, True, False]))
        result = bank.retrieve(axis(1, VISUAL_DIM), axis(1, AUDIO_DIM))
        self.assertEqual(result.ids[0][:3], ["visual_only", "both_ok", "both_disagree"])
        torch.testing.assert_close(result.scores[0, :3], torch.tensor([1.0, 0.6, 0.0]))
        self.assertEqual(result.query_mask.tolist(), [[True, True]])
        torch.testing.assert_close(result.values[0, 0, VISUAL_DIM:], torch.zeros(AUDIO_DIM))
        audio_only = bank.retrieve(None, axis(1, AUDIO_DIM))
        self.assertNotIn("visual_only", audio_only.ids[0])
        self.assertEqual(audio_only.query_mask.tolist(), [[False, True]])

    def test_empty_bank_and_all_missing_have_finite_zero_outputs(self):
        empty = MemoryBank(None, None, [])
        result = empty.retrieve(axis(2, VISUAL_DIM), None)
        self.assertEqual(tuple(result.values.shape), (2, 5, VISUAL_DIM + AUDIO_DIM))
        self.assertFalse(bool(result.mask.any()))
        self.assertTrue(bool(torch.isfinite(result.values).all()))
        self.assertEqual(result.ids, [[None] * 5, [None] * 5])
        bank = MemoryBank(axis(1, VISUAL_DIM), None, ["x"])
        result = bank.retrieve(torch.zeros(2, VISUAL_DIM), None)
        self.assertFalse(bool(result.mask.any()))
        self.assertEqual(result.query_mask.tolist(), [[False, False], [False, False]])
        self.assertEqual(int(result.scores.count_nonzero()), 0)
        filtered = bank.retrieve(axis(1, VISUAL_DIM), None, clip_ids=["x"], training=True)
        self.assertFalse(bool(filtered.mask.any()))

    def test_random_control_respects_filters_and_is_reproducible(self):
        bank = MemoryBank(torch.randn(12, VISUAL_DIM), None,
                          [str(i) for i in range(12)])
        kwargs = dict(visual=axis(1, VISUAL_DIM), audio=None, clip_ids=["0"],
                      training=True, mode="random", k=4)
        one = bank.retrieve(**kwargs, generator=torch.Generator().manual_seed(42))
        two = bank.retrieve(**kwargs, generator=torch.Generator().manual_seed(42))
        self.assertEqual(one.ids, two.ids)
        self.assertNotIn("0", one.ids[0])
        self.assertEqual(len(set(one.ids[0])), 4)

    def test_weights_only_roundtrip_and_version(self):
        bank = MemoryBank(torch.randn(3, VISUAL_DIM), None,
                          ["a", "b", "c"], ["g", None, "h"], version="unit-v1")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.pt"
            bank.save(path)
            torch.load(path, weights_only=True)
            restored = MemoryBank.load(path, expected_version="unit-v1").to("cpu")
            self.assertEqual(restored.clip_ids, bank.clip_ids)
            self.assertEqual(restored.group_ids, bank.group_ids)
            torch.testing.assert_close(restored.features, bank.features)
            self.assertEqual(restored.valid_mask.tolist(), bank.valid_mask.tolist())
            with self.assertRaisesRegex(ValueError, "version mismatch"):
                MemoryBank.load(path, expected_version="unit-v2")

    def test_invalid_shapes_and_finite_features_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "shape"):
            MemoryBank(torch.zeros(2, 9), None, ["a", "b"])
        invalid = axis(1, VISUAL_DIM)
        invalid[0, 2] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            MemoryBank(invalid, None, ["a"])
        valid = MemoryBank(invalid, None, ["a"], visual_valid=torch.tensor([False]))
        self.assertFalse(bool(valid.valid_mask.any()))


class AdapterTests(unittest.TestCase):
    def make_adapter(self):
        torch.manual_seed(9)
        return MemoryAdapter(d_query=10, d_value=10, d_hidden=16,
                             llm_dim=12, num_tokens=3, memory_dropout=0.0)

    def test_generation_gradient_reaches_adapter_and_empty_rows_skip(self):
        adapter = self.make_adapter()
        query = torch.randn(3, 10)
        values = torch.randn(3, 4, 10)
        mask = torch.tensor([[True, True, False, False], [False] * 4, [True] * 4])
        output = adapter(query, values, mask, enabled=torch.tensor([True, True, False]))
        self.assertEqual(output.enabled.tolist(), [True, False, False])
        self.assertTrue(bool(torch.isfinite(output.tokens).all()))
        self.assertEqual(int(output.tokens[1:].count_nonzero()), 0)
        decoder = nn.Linear(12, 5)
        loss = nn.functional.cross_entropy(decoder(output.tokens[0].mean(0))[None],
                                          torch.tensor([2]))
        loss.backward()
        for parameter in (adapter.queries, adapter.query_projection[0].weight,
                          adapter.value_projection[0].weight,
                          adapter.output_projection[1].weight,
                          adapter.gate_projection.weight):
            self.assertIsNotNone(parameter.grad)
            self.assertGreater(float(parameter.grad.abs().sum()), 0)

    def test_all_masked_and_forced_dropout_never_softmax_all_masked(self):
        adapter = self.make_adapter()
        query, values = torch.randn(2, 10), torch.randn(2, 4, 10)
        empty = adapter(query, values, torch.zeros(2, 4, dtype=torch.bool))
        self.assertFalse(bool(empty.enabled.any()))
        self.assertTrue(bool(torch.isfinite(empty.tokens).all()))
        dropped = adapter(query, values, torch.ones(2, 4, dtype=torch.bool), dropout_p=1.0)
        self.assertFalse(bool(dropped.enabled.any()))
        self.assertEqual(int(dropped.tokens.count_nonzero()), 0)
        adapter.eval()
        enabled = adapter(query, values, torch.ones(2, 4, dtype=torch.bool))
        self.assertTrue(bool(enabled.enabled.all()))

    def test_zero_candidates_and_dtype_conversion(self):
        adapter = self.make_adapter().double()
        result = adapter(torch.randn(2, 10), torch.empty(2, 0, 10),
                         torch.empty(2, 0, dtype=torch.bool))
        self.assertEqual(result.tokens.dtype, torch.float64)
        self.assertFalse(bool(result.enabled.any()))


if __name__ == "__main__":
    unittest.main()


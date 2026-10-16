"""CPU-only contract tests; no real BGE download or GPU allocation."""
from types import SimpleNamespace
import unittest

import torch
from torch import nn

from amg.text import FrozenBGETextEncoder, TextEvidenceConstructor, _validate_loading_info


class StubTokenizer:
    def __init__(self):
        self.seen = []

    def __call__(self, texts, *, padding, truncation, max_length, return_tensors):
        self.seen.extend(texts)
        lengths = [min(max_length, len(text.split()) + 2) for text in texts]
        count = max(lengths)
        ids = torch.zeros(len(texts), count, dtype=torch.long)
        mask = torch.zeros_like(ids)
        for row, length in enumerate(lengths):
            ids[row, :length] = torch.arange(1, length + 1)
            mask[row, :length] = 1
        return {"input_ids": ids, "attention_mask": mask}


class StubEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.config = SimpleNamespace(hidden_size=1024)
        self.scale = nn.Parameter(torch.linspace(0.1, 1.0, 1024))
        self.dropout = nn.Dropout(0.8)
        self.calls = 0

    def forward(self, input_ids, attention_mask):
        self.calls += 1
        hidden = input_ids.unsqueeze(-1).float() * self.scale
        return SimpleNamespace(last_hidden_state=self.dropout(hidden))


class TextTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(31)
        self.raw_encoder = StubEncoder()
        self.tokenizer = StubTokenizer()
        self.encoder = FrozenBGETextEncoder(
            tokenizer=self.tokenizer, encoder=self.raw_encoder, encoder_revision="stub-v1"
        )

    def test_frozen_eval_even_when_parent_trains(self):
        module = TextEvidenceConstructor(self.encoder)
        module.train()
        self.assertTrue(module.training)
        self.assertFalse(self.raw_encoder.training)
        self.assertTrue(all(not p.requires_grad for p in self.raw_encoder.parameters()))
        first = self.encoder(subtitles=["英文 ASR"])
        self.raw_encoder.train()  # Defensive forward must restore eval.
        second = self.encoder(subtitles=["英文 ASR"])
        self.assertFalse(self.raw_encoder.training)
        self.assertTrue(torch.equal(first.token_hidden, second.token_hidden))
        self.assertFalse(first.token_hidden.requires_grad)

    def test_shapes_dense_and_padding(self):
        result = self.encoder(subtitles=["hello world", "", "好", " \t"])
        self.assertEqual(result.token_hidden.shape, (4, 4, 1024))
        self.assertEqual(result.dense.shape, (4, 1024))
        self.assertEqual(result.valid_mask.tolist(), [True, False, True, False])
        self.assertFalse(result.attention_mask[1].any())
        self.assertFalse(result.attention_mask[3].any())
        self.assertEqual(result.token_hidden[1].count_nonzero().item(), 0)
        self.assertEqual(result.token_hidden[2, 3].count_nonzero().item(), 0)
        torch.testing.assert_close(result.dense[[0, 2]].norm(dim=-1), torch.ones(2))
        self.assertEqual(result.dense[[1, 3]].count_nonzero().item(), 0)
        self.assertEqual(self.tokenizer.seen, ["hello world", "好"])
        self.assertEqual(result.metadata["input_contract"], "raw-subtitles-only")
        self.assertTrue(torch.isfinite(result.token_hidden).all())

    def test_empty_batch_and_missing_text_skip_encoder(self):
        for subtitles in ([], ["", "   "]):
            result = self.encoder(subtitles=subtitles)
            self.assertEqual(result.token_hidden.shape, (len(subtitles), 0, 1024))
            self.assertEqual(result.dense.shape, (len(subtitles), 1024))
            self.assertFalse(result.valid_mask.any())
            self.assertTrue(torch.isfinite(result.dense).all())
        self.assertEqual(self.raw_encoder.calls, 0)
        module = TextEvidenceConstructor(self.encoder)
        for subtitles in ([], ["", "   "]):
            result = module(subtitles=subtitles)
            self.assertEqual(result.evidence.shape, (len(subtitles), 2, 256))
            self.assertFalse(result.valid_mask.any())
            self.assertTrue(torch.isfinite(result.evidence).all())
            self.assertEqual(result.evidence.count_nonzero().item(), 0)
        self.assertEqual(self.raw_encoder.calls, 0)

    def test_trainable_projection_and_query_gradients(self):
        module = TextEvidenceConstructor(self.encoder)
        result = module(subtitles=["hello world", ""])
        self.assertEqual(result.valid_mask.tolist(), [[True, True], [False, False]])
        self.assertEqual(result.dense.shape[-1], 1024)
        result.evidence[0, 0, 0].backward()
        self.assertGreater(module.input_projection.weight.grad.abs().sum().item(), 0)
        self.assertGreater(module.queries.grad.abs().sum().item(), 0)
        self.assertIsNone(self.raw_encoder.scale.grad)
        self.assertEqual(result.evidence[1].count_nonzero().item(), 0)

    def test_reject_assembled_batch_interfaces(self):
        for subtitles in ("hello", {"input_ids": [1]}, [None]):
            with self.assertRaises(TypeError):
                self.encoder(subtitles=subtitles)
        with self.assertRaises(TypeError):
            self.encoder(input_ids=torch.ones(1, 2))

    def test_concepts_use_same_frozen_encoder(self):
        result = self.encoder.encode_concepts(definitions=["Conflict: disagreement or confrontation."])
        self.assertEqual(result.metadata["input_contract"], "concept-definitions-only")
        self.assertEqual(result.metadata["encoder_revision"], "stub-v1")
        self.assertEqual(self.raw_encoder.calls, 1)
        self.assertEqual(result.dense.shape, (1, 1024))

    def test_load_info_only_allows_unused_pooler(self):
        _validate_loading_info({"unexpected_keys": ["pooler.dense.weight", "pooler.dense.bias"]})
        for info in (
            {"missing_keys": ["encoder.layer.0.attention.self.query.weight"]},
            {"unexpected_keys": ["other.weight"]},
            {"mismatched_keys": [("weight", (1,), (2,))]},
            {"error_msgs": ["checkpoint corruption"]},
        ):
            with self.assertRaises(RuntimeError):
                _validate_loading_info(info)


if __name__ == "__main__":
    unittest.main()

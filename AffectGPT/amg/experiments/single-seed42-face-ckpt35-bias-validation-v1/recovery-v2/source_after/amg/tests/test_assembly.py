import unittest

import torch
from torch import nn

from amg.assembly import assemble_inputs


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(3)
        self.embedding = nn.Embedding(12, 8)
        # AV placeholder is intentionally outside the language model vocabulary.
        self.ids = torch.tensor([[1, 99, 99, 4, 0, 0],
                                 [1, 99, 99, 5, 6, 0]])
        self.mask = torch.tensor([[1, 1, 1, 1, 0, 0],
                                  [1, 1, 1, 1, 1, 0]])
        # EOS=PAD has a real target label despite its original zero attention.
        self.labels = torch.tensor([[-100, -100, -100, 4, 0, -100],
                                    [-100, -100, -100, 5, 6, 0]])
        self.av = torch.randn(2, 2, 8, requires_grad=True)
        self.memory = torch.randn(2, 3, 8, requires_grad=True)

    def call(self, **kwargs):
        args = dict(input_ids=self.ids, base_embedding=self.embedding,
                    attention_mask=self.mask, labels=self.labels,
                    modality_replacements={99: self.av})
        args.update(kwargs)
        return assemble_inputs(**args)

    def test_true_off_matches_original_embeddings_labels_and_eos_positions(self):
        baseline = self.call()
        off = self.call(memory_tokens=self.memory, memory_enabled=torch.zeros(2, dtype=torch.bool),
                        insert_indices=torch.tensor([1, 1]))
        self.assertEqual(off.lengths.tolist(), [5, 6])
        torch.testing.assert_close(off.inputs_embeds, baseline.inputs_embeds, rtol=0, atol=0)
        torch.testing.assert_close(off.attention_mask, baseline.attention_mask, rtol=0, atol=0)
        torch.testing.assert_close(off.labels, baseline.labels, rtol=0, atol=0)
        torch.testing.assert_close(off.position_ids, baseline.position_ids, rtol=0, atol=0)
        self.assertEqual(off.labels[0, 4].item(), 0)
        self.assertEqual(off.attention_mask[0, 4].item(), 0)
        self.assertEqual(off.position_ids[0, 4].item(), 4)
        self.assertEqual(off.labels[1, 5].item(), 0)
        torch.testing.assert_close(off.inputs_embeds[:, 1:3], self.av)
        torch.testing.assert_close(off.inputs_embeds[0, 0], self.embedding(torch.tensor(1)))

    def test_mixed_batch_insertion_preserves_bos_eos_and_supervision(self):
        result = self.call(memory_tokens=self.memory,
                           memory_enabled=torch.tensor([True, False]),
                           insert_indices=torch.tensor([1, 1]))
        self.assertEqual(result.lengths.tolist(), [8, 6])
        self.assertEqual(result.memory_enabled.tolist(), [True, False])
        self.assertEqual(tuple(result.inputs_embeds.shape), (2, 8, 8))
        torch.testing.assert_close(result.inputs_embeds[0, 0], self.embedding(torch.tensor(1)))
        torch.testing.assert_close(result.inputs_embeds[0, 1:4], self.memory[0])
        torch.testing.assert_close(result.inputs_embeds[0, 4:6], self.av[0])
        self.assertEqual(result.labels[0].tolist(), [-100, -100, -100, -100, -100, -100, 4, 0])
        self.assertEqual(result.attention_mask[0].tolist(), [1, 1, 1, 1, 1, 1, 1, 0])
        self.assertEqual(result.position_ids[0].tolist(), list(range(8)))
        self.assertEqual(result.position_ids[1].tolist(), [0, 1, 2, 3, 4, 5, 0, 0])
        self.assertEqual(result.labels[1].tolist(), [-100, -100, -100, 5, 6, 0, -100, -100])
        self.assertEqual(result.attention_mask[1].tolist(), [1, 1, 1, 1, 1, 0, 0, 0])
        result.inputs_embeds.square().sum().backward()
        self.assertGreater(float(self.memory.grad[0].abs().sum()), 0)
        self.assertEqual(float(self.memory.grad[1].abs().sum()), 0)
        self.assertGreater(float(self.av.grad.abs().sum()), 0)

    def test_internal_zero_attention_is_retained_without_compression(self):
        ids = torch.tensor([[1, 2, 3, 4, 0]])
        mask = torch.tensor([[1, 0, 1, 1, 0]])
        result = assemble_inputs(ids, self.embedding, mask)
        self.assertEqual(result.lengths.tolist(), [4])
        self.assertEqual(result.attention_mask.tolist(), [[1, 0, 1, 1]])
        torch.testing.assert_close(result.inputs_embeds, self.embedding(ids[:, :4]), rtol=0, atol=0)
        self.assertEqual(result.position_ids.tolist(), [[0, 1, 2, 3]])

    def test_inference_uses_same_replacement_insertion_and_no_labels(self):
        result = self.call(labels=None, memory_tokens=self.memory,
                           memory_enabled=torch.tensor([False, True]),
                           insert_indices=torch.tensor([1, 1]))
        self.assertIsNone(result.labels)
        self.assertEqual(result.lengths.tolist(), [4, 8])
        torch.testing.assert_close(result.inputs_embeds[1, 1:4], self.memory[1])
        self.assertEqual(result.attention_mask[1].tolist(), [1] * 8)

    def test_total_budget_checks_inserted_memory_and_masked_eos(self):
        enabled = torch.tensor([True, False])
        self.call(memory_tokens=self.memory, memory_enabled=enabled,
                  insert_indices=torch.tensor([1, 1]), max_length=8)
        with self.assertRaisesRegex(ValueError, "assembled length 8 exceeds max_length=7"):
            self.call(memory_tokens=self.memory, memory_enabled=enabled,
                      insert_indices=torch.tensor([1, 1]), max_length=7)
        off = self.call(memory_tokens=self.memory, memory_enabled=torch.zeros(2, dtype=torch.bool),
                        max_length=6)
        self.assertEqual(off.lengths.tolist(), [5, 6])
        with self.assertRaisesRegex(ValueError, "assembled length 6 exceeds max_length=5"):
            self.call(max_length=5)

    def test_malformed_replacement_count_or_insertion_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "occurrences"):
            self.call(modality_replacements={99: self.av[:, :1]})
        with self.assertRaisesRegex(ValueError, "insertion index"):
            self.call(memory_tokens=self.memory, memory_enabled=torch.tensor([True, False]),
                      insert_indices=torch.tensor([7, 0]))
        with self.assertRaisesRegex(ValueError, "requires memory_tokens"):
            self.call(memory_enabled=torch.ones(2, dtype=torch.bool))


if __name__ == "__main__":
    unittest.main()


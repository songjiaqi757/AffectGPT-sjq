"""Frozen ASR-only BGE-M3 features for the later AMG Evidence stage.

This module is independent of the Qwen prompt/target sequence. M0 AV Memory
must not instantiate it implicitly. Native dense retrieval retains all 1024
BGE dimensions; only learned Evidence features are projected into graph space.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import torch
from torch import Tensor, nn
import torch.nn.functional as F


DEFAULT_BGE_PATH = "/ai/sjq/AffectGPT-sjq/AffectGPT/models/bge-m3"
_ALLOWED_UNUSED_KEYS = {"pooler.dense.weight", "pooler.dense.bias"}


def _validate_loading_info(info: Dict[str, Any]) -> None:
    """Only the deliberately unused XLM-R pooler may be present in a checkpoint."""
    missing = list(info.get("missing_keys", []))
    unexpected = set(info.get("unexpected_keys", [])) - _ALLOWED_UNUSED_KEYS
    mismatched = list(info.get("mismatched_keys", []))
    errors = list(info.get("error_msgs", []))
    if missing or unexpected or mismatched or errors:
        raise RuntimeError(
            "Unsafe BGE-M3 checkpoint load: "
            f"missing={missing}, unexpected={sorted(unexpected)}, "
            f"mismatched={mismatched}, errors={errors}"
        )


def _local_metadata(model_path: str, revision: Optional[str]) -> Dict[str, Any]:
    root = Path(model_path).resolve()
    manifest = []
    for item in sorted(root.iterdir()):
        if item.is_file() and (item.suffix in {".json", ".bin", ".safetensors", ".model"}):
            stat = item.stat()
            record = {"name": item.name, "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}
            if item.suffix == ".json":
                record["sha256"] = hashlib.sha256(item.read_bytes()).hexdigest()
            manifest.append(record)
    signature = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    return {
        "encoder": "BAAI/bge-m3",
        "model_path": str(root),
        "encoder_revision": revision,
        "artifact_signature": signature,
        # This detects normal file replacement, not an adversarial same-stat rewrite.
        # E2 must additionally version the complete learned representation snapshot.
        "signature_scheme": "file-stats-and-json-sha256-v1",
        "encoder_frozen": True,
        "dense_pooling": "normalized_cls",
        "hidden_size": 1024,
        "allowed_unused_checkpoint_keys": sorted(_ALLOWED_UNUSED_KEYS),
    }


@dataclass
class TextEncoding:
    token_hidden: Tensor
    attention_mask: Tensor
    valid_mask: Tensor
    dense: Tensor
    metadata: Dict[str, Any]


@dataclass
class TextEvidence:
    evidence: Tensor
    valid_mask: Tensor
    dense: Tensor
    encoding: TextEncoding


class FrozenBGETextEncoder(nn.Module):
    """Encode independent subtitles or concept definitions using local BGE-M3.

    ``forward`` accepts only a batch of raw subtitle strings. Never pass Qwen
    input_ids, an assembled task prompt, emotion labels, or a target caption.
    ``encode_concepts`` is an explicit offline path for concept definitions.
    Empty/whitespace subtitles are missing modalities, even though a tokenizer
    would otherwise create nonempty special-token sequences for them.
    """

    hidden_size = 1024

    def __init__(
        self,
        model_path: str = DEFAULT_BGE_PATH,
        max_length: int = 128,
        *,
        tokenizer: Any = None,
        encoder: Optional[nn.Module] = None,
        encoder_revision: Optional[str] = None,
    ) -> None:
        super().__init__()
        if max_length < 2:
            raise ValueError("max_length must allow at least two special tokens")
        if (encoder is None) != (tokenizer is None):
            raise ValueError("Supply both tokenizer and encoder, or neither")
        self.max_length = int(max_length)
        if encoder is None:
            from transformers import AutoModel, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                model_path, local_files_only=True, trust_remote_code=False
            )
            encoder, info = AutoModel.from_pretrained(
                model_path,
                local_files_only=True,
                trust_remote_code=False,
                add_pooling_layer=False,
                output_loading_info=True,
            )
            _validate_loading_info(info)
            self.metadata = _local_metadata(model_path, encoder_revision)
        else:
            self.metadata = {
                "encoder": "injected-test-encoder",
                "encoder_revision": encoder_revision,
                "encoder_frozen": True,
                "dense_pooling": "normalized_cls",
                "hidden_size": 1024,
            }
        if int(encoder.config.hidden_size) != self.hidden_size:
            raise ValueError("BGE-M3 must produce 1024-dimensional hidden states")
        self.encoder = encoder
        self.tokenizer = tokenizer
        self.metadata.update({"max_length": self.max_length, "input_contract": "raw-subtitles-only"})
        self.encoder.requires_grad_(False)
        self.encoder.eval()

    def train(self, mode: bool = True) -> "FrozenBGETextEncoder":
        super().train(mode)
        self.encoder.eval()
        return self

    def _device_dtype(self):
        for value in self.encoder.parameters():
            return value.device, value.dtype
        for value in self.encoder.buffers():
            return value.device, value.dtype
        return torch.device("cpu"), torch.float32

    @torch.no_grad()
    def _encode(self, texts: Sequence[str], input_contract: str) -> TextEncoding:
        if isinstance(texts, (str, bytes, dict)) or not isinstance(texts, Sequence):
            raise TypeError("Expected a batch of raw text strings")
        if any(not isinstance(text, str) for text in texts):
            raise TypeError("Every text must be str; represent missing subtitles as an empty string")
        self.encoder.eval()
        device, dtype = self._device_dtype()
        batch_size = len(texts)
        valid = torch.tensor([bool(text.strip()) for text in texts], dtype=torch.bool, device=device)
        rows = valid.nonzero(as_tuple=False).flatten()
        metadata = dict(self.metadata, input_contract=input_contract)
        if not rows.numel():
            return TextEncoding(
                torch.zeros(batch_size, 0, self.hidden_size, device=device, dtype=dtype),
                torch.zeros(batch_size, 0, device=device, dtype=torch.bool),
                valid,
                torch.zeros(batch_size, self.hidden_size, device=device, dtype=dtype),
                metadata,
            )
        active_texts = [texts[index] for index in rows.cpu().tolist()]
        encoded = self.tokenizer(
            active_texts, padding=True, truncation=True,
            max_length=self.max_length, return_tensors="pt",
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}
        active_mask = encoded["attention_mask"].bool()
        if not active_mask.any(dim=1).all():
            raise ValueError("Tokenizer returned an all-masked sequence for nonempty text")
        hidden = self.encoder(**encoded).last_hidden_state
        if hidden.shape != (*active_mask.shape, self.hidden_size):
            raise ValueError("Unexpected BGE token hidden shape")
        hidden = hidden.masked_fill(~active_mask.unsqueeze(-1), 0)
        dense_active = F.normalize(hidden[:, 0], p=2, dim=-1, eps=1e-12)
        tokens = hidden.new_zeros(batch_size, hidden.shape[1], self.hidden_size)
        mask = torch.zeros(batch_size, hidden.shape[1], device=device, dtype=torch.bool)
        dense = hidden.new_zeros(batch_size, self.hidden_size)
        tokens[rows] = hidden
        mask[rows] = active_mask
        dense[rows] = dense_active
        return TextEncoding(tokens, mask, valid, dense, metadata)

    def forward(self, *, subtitles: Sequence[str]) -> TextEncoding:
        return self._encode(subtitles, "raw-subtitles-only")

    def encode_concepts(self, *, definitions: Sequence[str]) -> TextEncoding:
        return self._encode(definitions, "concept-definitions-only")


class TextEvidenceConstructor(nn.Module):
    """Trainable projection and queries above a frozen subtitle-only encoder.

    Missing rows bypass attention entirely, preventing all-mask softmax NaNs.
    E1 may train projection/queries/attention; E2 must freeze this entire module
    and assign its own checkpoint/snapshot version before constructing Memory.
    """

    def __init__(
        self, encoder: FrozenBGETextEncoder, graph_dim: int = 256,
        num_queries: int = 2, num_heads: int = 4,
    ) -> None:
        super().__init__()
        if num_queries < 1 or graph_dim < 1 or num_heads < 1 or graph_dim % num_heads:
            raise ValueError("Invalid query count or graph_dim/num_heads")
        self.text_encoder = encoder
        self.graph_dim = graph_dim
        self.num_queries = num_queries
        self.input_projection = nn.Linear(encoder.hidden_size, graph_dim)
        self.input_norm = nn.LayerNorm(graph_dim)
        self.queries = nn.Parameter(torch.randn(num_queries, graph_dim) * 0.02)
        self.attention = nn.MultiheadAttention(graph_dim, num_heads, batch_first=True)
        self.output_norm = nn.LayerNorm(graph_dim)

    def forward(self, *, subtitles: Sequence[str]) -> TextEvidence:
        encoded = self.text_encoder(subtitles=subtitles)
        batch_size = encoded.valid_mask.shape[0]
        evidence = self.queries.new_zeros(batch_size, self.num_queries, self.graph_dim)
        rows = encoded.valid_mask.nonzero(as_tuple=False).flatten()
        if rows.numel():
            hidden = encoded.token_hidden[rows].to(dtype=self.input_projection.weight.dtype)
            hidden = self.input_norm(self.input_projection(hidden))
            query = self.queries.unsqueeze(0).expand(rows.numel(), -1, -1)
            attended, _ = self.attention(
                query, hidden, hidden,
                key_padding_mask=~encoded.attention_mask[rows],
                need_weights=False,
            )
            evidence[rows] = self.output_norm(query + attended)
        mask = encoded.valid_mask.unsqueeze(1).expand(-1, self.num_queries)
        return TextEvidence(evidence, mask, encoded.dense, encoded)

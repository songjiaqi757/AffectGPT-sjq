"""M0 frozen AV memory retrieval and a small trainable memory adapter."""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import torch
from torch import Tensor, nn
import torch.nn.functional as F

VISUAL_DIM = 768
AUDIO_DIM = 1024
MEMORY_DIM = VISUAL_DIM + AUDIO_DIM
SCHEMA_VERSION = 1


@dataclass
class MemoryResult:
    values: Tensor             # [B,K,1792], independently normalized modalities
    scores: Tensor             # [B,K], zero where mask is false
    mask: Tensor               # [B,K]
    ids: List[List[Optional[str]]]
    query_features: Tensor     # [B,1792], missing modalities zeroed
    query_mask: Tensor         # [B,2], visual then audio validity


def _normalize_features(visual, audio, visual_valid, audio_valid, n, device):
    pieces, masks = [], []
    for name, value, valid, dim in (
        ("visual", visual, visual_valid, VISUAL_DIM),
        ("audio", audio, audio_valid, AUDIO_DIM),
    ):
        if valid is not None and tuple(valid.shape) != (n,):
            raise ValueError(f"{name}_valid must have shape [{n}]")
        if value is None:
            if valid is not None and bool(valid.any()):
                raise ValueError(f"{name}_valid cannot mark absent features valid")
            value = torch.zeros(n, dim, device=device, dtype=torch.float32)
            mask = torch.zeros(n, device=device, dtype=torch.bool)
        else:
            if value.ndim != 2 or tuple(value.shape) != (n, dim):
                raise ValueError(f"{name} must have shape [{n},{dim}]")
            value = value.to(device=device, dtype=torch.float32)
            mask = torch.ones(n, device=device, dtype=torch.bool)
            if valid is not None:
                mask = valid.to(device=device, dtype=torch.bool)
            finite = torch.isfinite(value).all(dim=-1)
            if bool((mask & ~finite).any()):
                raise ValueError(f"valid {name} features must be finite")
            value = torch.nan_to_num(value)
            mask = mask & (value.norm(dim=-1) > 1e-12)
            value = F.normalize(value, dim=-1) * mask[:, None]
        pieces.append(value)
        masks.append(mask)
    return torch.cat(pieces, dim=-1), torch.stack(masks, dim=-1)


class MemoryBank:
    """Exact cosine search over per-modality normalized frozen encoder means.

    Scores use equal weights among modalities valid in both query and candidate.
    Scores are computed on the bank device in float32; returned tensors are moved
    to the first query tensor's device. .to(device) controls bank residence.
    Training must supply IDs for mandatory self/group exclusion.
    """
    def __init__(self, visual, audio, clip_ids, group_ids=None,
                 visual_valid=None, audio_valid=None, version="amg-m0-v1"):
        self.clip_ids = [str(x) for x in clip_ids]
        n = len(self.clip_ids)
        if group_ids is None:
            self.group_ids = [None] * n
        else:
            if len(group_ids) != n:
                raise ValueError("group_ids and clip_ids lengths differ")
            self.group_ids = [None if x is None else str(x) for x in group_ids]
        first = visual if visual is not None else audio
        device = first.device if first is not None else torch.device("cpu")
        with torch.no_grad():
            self.features, self.valid_mask = _normalize_features(
                visual, audio, visual_valid, audio_valid, n, device)
        self.features = self.features.detach()
        self.valid_mask = self.valid_mask.detach()
        self.version = str(version)

    def __len__(self):
        return len(self.clip_ids)

    @property
    def device(self):
        return self.features.device

    def to(self, device):
        self.features = self.features.to(device=device, dtype=torch.float32)
        self.valid_mask = self.valid_mask.to(device=device)
        return self

    def save(self, path):
        """Persist only tensors, strings, lists and an integer schema version."""
        torch.save({"schema_version": SCHEMA_VERSION, "version": self.version,
                    "clip_ids": self.clip_ids, "group_ids": self.group_ids,
                    "features": self.features.detach().cpu(),
                    "valid_mask": self.valid_mask.detach().cpu()}, Path(path))

    @classmethod
    def load(cls, path, map_location="cpu", expected_version=None):
        payload = torch.load(Path(path), map_location=map_location, weights_only=True)
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported memory bank schema version")
        if expected_version is not None and payload.get("version") != expected_version:
            raise ValueError("memory bank version mismatch")
        features, valid = payload["features"], payload["valid_mask"]
        n = len(payload["clip_ids"])
        if tuple(features.shape) != (n, MEMORY_DIM) or tuple(valid.shape) != (n, 2):
            raise ValueError("invalid serialized memory bank shapes")
        return cls(features[:, :VISUAL_DIM], features[:, VISUAL_DIM:],
                   payload["clip_ids"], payload["group_ids"],
                   valid[:, 0], valid[:, 1], payload["version"])

    @torch.no_grad()
    def retrieve(self, visual, audio, visual_valid=None, audio_valid=None,
                 clip_ids=None, group_ids=None, training=False, exclude_self=False,
                 k=5, mode="retrieval", generator=None):
        if not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive integer")
        if mode not in ("retrieval", "random"):
            raise ValueError("mode must be retrieval or random")
        first = visual if visual is not None else audio
        if first is None:
            if clip_ids is None:
                raise ValueError("query batch size requires features or clip_ids")
            b, output_device = len(clip_ids), self.device
        else:
            b, output_device = first.shape[0], first.device
        if clip_ids is not None and len(clip_ids) != b:
            raise ValueError("query clip_ids length differs from batch size")
        if group_ids is not None and len(group_ids) != b:
            raise ValueError("query group_ids length differs from batch size")
        if (training or exclude_self) and clip_ids is None:
            raise ValueError("training/self exclusion requires query clip_ids")
        query, query_mask = _normalize_features(
            visual, audio, visual_valid, audio_valid, b, self.device)
        qv, qa = query[:, :VISUAL_DIM], query[:, VISUAL_DIM:]
        bv, ba = self.features[:, :VISUAL_DIM], self.features[:, VISUAL_DIM:]
        shared = query_mask[:, None, :] & self.valid_mask[None, :, :]
        denominator = shared.sum(dim=-1)
        score = ((qv @ bv.T) * shared[:, :, 0] +
                 (qa @ ba.T) * shared[:, :, 1]) / denominator.clamp_min(1)
        candidate_mask = denominator > 0
        if training or exclude_self:
            for i in range(b):
                qid = str(clip_ids[i])
                qgroups = {gid for cid, gid in zip(self.clip_ids, self.group_ids)
                           if cid == qid and gid is not None}
                if group_ids is not None and group_ids[i] is not None:
                    qgroups.add(str(group_ids[i]))
                blocked = [cid == qid or (gid is not None and gid in qgroups)
                           for cid, gid in zip(self.clip_ids, self.group_ids)]
                candidate_mask[i] &= ~torch.tensor(blocked, device=self.device, dtype=torch.bool)
        count = min(k, len(self))
        values = self.features.new_zeros((b, k, MEMORY_DIM))
        scores = self.features.new_zeros((b, k))
        mask = torch.zeros((b, k), device=self.device, dtype=torch.bool)
        ids = [[None] * k for _ in range(b)]
        if count:
            rank = score if mode == "retrieval" else torch.rand(
                score.shape, device=self.device, generator=generator)
            indices = rank.masked_fill(~candidate_mask, -torch.inf).topk(count, dim=1).indices
            selected_mask = candidate_mask.gather(1, indices)
            values[:, :count] = self.features[indices] * selected_mask[:, :, None]
            scores[:, :count] = score.gather(1, indices) * selected_mask
            mask[:, :count] = selected_mask
            selected_mask_cpu = selected_mask.cpu().tolist()
            for i, row in enumerate(indices.cpu().tolist()):
                for j, idx in enumerate(row):
                    if selected_mask_cpu[i][j]:
                        ids[i][j] = self.clip_ids[idx]
        return MemoryResult(values.to(output_device), scores.to(output_device),
                            mask.to(output_device), ids, query.to(output_device),
                            query_mask.to(output_device))


@dataclass
class AdapterOutput:
    tokens: Tensor             # [B,num_tokens,llm_dim], adapter device and dtype
    enabled: Tensor            # false means caller must insert no tokens
    gate: Tensor               # [B,1], zero for inactive samples


class MemoryAdapter(nn.Module):
    def __init__(self, d_query=MEMORY_DIM, d_value=MEMORY_DIM, d_hidden=256,
                 llm_dim=3584, num_tokens=4, num_heads=4, memory_dropout=0.1):
        super().__init__()
        if d_hidden % num_heads:
            raise ValueError("d_hidden must be divisible by num_heads")
        if not 0 <= memory_dropout <= 1:
            raise ValueError("memory_dropout must be in [0,1]")
        self.d_query, self.d_value = d_query, d_value
        self.num_tokens, self.llm_dim = num_tokens, llm_dim
        self.memory_dropout = float(memory_dropout)
        self.query_projection = nn.Sequential(nn.Linear(d_query, d_hidden), nn.GELU(),
                                               nn.Linear(d_hidden, d_hidden))
        self.value_projection = nn.Sequential(nn.Linear(d_value, d_hidden), nn.GELU(),
                                               nn.Linear(d_hidden, d_hidden))
        self.queries = nn.Parameter(torch.empty(num_tokens, d_hidden))
        nn.init.normal_(self.queries, std=0.02)
        self.attention = nn.MultiheadAttention(d_hidden, num_heads, batch_first=True)
        self.output_projection = nn.Sequential(nn.LayerNorm(d_hidden),
                                                nn.Linear(d_hidden, llm_dim))
        self.gate_projection = nn.Linear(d_query, 1)
        nn.init.zeros_(self.gate_projection.weight)
        nn.init.constant_(self.gate_projection.bias, -2.0)

    def forward(self, query_features, values, mask, enabled=None,
                dropout_p=None, generator=None):
        b = query_features.shape[0]
        if tuple(query_features.shape) != (b, self.d_query):
            raise ValueError("query_features has the wrong shape")
        if values.ndim != 3 or values.shape[0] != b or values.shape[2] != self.d_value:
            raise ValueError("values has the wrong shape")
        if tuple(mask.shape) != tuple(values.shape[:2]):
            raise ValueError("mask and values shapes differ")
        device, dtype = self.queries.device, self.queries.dtype
        query_features = query_features.to(device=device, dtype=dtype)
        values = values.to(device=device, dtype=dtype)
        mask = mask.to(device=device, dtype=torch.bool)
        active = mask.any(dim=1)
        if enabled is not None:
            if tuple(enabled.shape) != (b,):
                raise ValueError("enabled must have shape [B]")
            active = active & enabled.to(device=device, dtype=torch.bool)
        p = self.memory_dropout if dropout_p is None and self.training else (dropout_p or 0.0)
        if not 0 <= p <= 1:
            raise ValueError("dropout_p must be in [0,1]")
        if p:
            active = active & (torch.rand(b, device=device, generator=generator) >= p)
        tokens = query_features.new_zeros((b, self.num_tokens, self.llm_dim))
        gate = query_features.new_zeros((b, 1))
        if bool(active.any()):
            q = self.query_projection(query_features[active])[:, None, :] + self.queries[None]
            v = self.value_projection(values[active])
            attended, _ = self.attention(q, v, v, key_padding_mask=~mask[active], need_weights=False)
            active_gate = torch.sigmoid(self.gate_projection(query_features[active]))
            active_tokens = self.output_projection(attended) * active_gate[:, None, :]
            tokens = tokens.to(dtype=active_tokens.dtype)
            gate = gate.to(dtype=active_gate.dtype)
            tokens[active] = active_tokens
            gate[active] = active_gate
        return AdapterOutput(tokens, active, gate)


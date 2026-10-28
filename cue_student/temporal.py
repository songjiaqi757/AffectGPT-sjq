"""Position- and timestamp-aware audio/video heads with sample-level supervision."""
from __future__ import annotations
import math
import torch
from torch import nn

POSITION_VERSION = "index_and_elapsed_seconds_sinusoidal_v1"

def temporal_spec(cfg):
    """Effective architecture for checkpoint compatibility and inference metadata."""
    kind = cfg.get("temporal_model", "none")
    if kind not in ("none", "transformer"):
        raise ValueError("temporal_model must be none or transformer")
    if kind == "none":
        return {"temporal_model": "none"}
    if cfg.get("pooling", "mean") != "mean":
        raise ValueError("The temporal Transformer currently uses mean pooling")
    if cfg["modality"] not in ("audio", "visual"):
        raise ValueError("The temporal Transformer supports audio and visual")
    spec = dict(temporal_model=kind, temporal_dim=cfg.get("temporal_dim", 256),
                temporal_heads=cfg.get("temporal_heads", 4),
                temporal_layers=cfg.get("temporal_layers", 2),
                temporal_ffn_dim=cfg.get("temporal_ffn_dim", 1024),
                temporal_dropout=cfg.get("temporal_dropout", cfg.get("dropout", .1)),
                temporal_time_unit_seconds=cfg.get("temporal_time_unit_seconds", 1.),
                temporal_position_encoding=cfg.get("temporal_position_encoding", POSITION_VERSION))
    for key in ("temporal_dim", "temporal_heads", "temporal_layers", "temporal_ffn_dim"):
        if type(spec[key]) is not int or spec[key] < 1:
            raise ValueError(key + " must be a positive integer")
    if spec["temporal_dim"] % 2 or spec["temporal_dim"] % spec["temporal_heads"]:
        raise ValueError("temporal_dim must be even and divisible by temporal_heads")
    for key in ("temporal_dropout", "temporal_time_unit_seconds"):
        if not isinstance(spec[key], (int, float)) or not math.isfinite(spec[key]):
            raise ValueError(key + " must be finite")
    if not 0 <= spec["temporal_dropout"] < 1:
        raise ValueError("temporal_dropout must be in [0, 1)")
    if spec["temporal_time_unit_seconds"] <= 0:
        raise ValueError("temporal_time_unit_seconds must be positive")
    if spec["temporal_position_encoding"] != POSITION_VERSION:
        raise ValueError("Unsupported temporal position encoding version")
    if cfg["modality"] == "audio":
        spec.update(audio_sample_rate=16000,
                    audio_feature_stride_samples=cfg.get("audio_feature_stride_samples", 320),
                    audio_feature_receptive_field_samples=cfg.get("audio_feature_receptive_field_samples", 400),
                    audio_timebase="hubert_conv_window_centers_relative_v1")
        for key in ("audio_feature_stride_samples", "audio_feature_receptive_field_samples"):
            if type(spec[key]) is not int or spec[key] < 1:
                raise ValueError(key + " must be a positive integer")
    return spec

def relative_frame_times(sequences):
    """Subtract the origin in Python float64 before creating a float32 tensor."""
    if not sequences:
        raise ValueError("Empty video timestamp batch")
    offsets = []
    for values in sequences:
        if not values or not all(math.isfinite(t) for t in values):
            raise ValueError("Missing/non-finite video timestamps")
        if any(b <= a for a, b in zip(values, values[1:])):
            raise ValueError("Video timestamps must be strictly increasing")
        offsets.append(torch.tensor([t - values[0] for t in values], dtype=torch.float32))
    return nn.utils.rnn.pad_sequence(offsets, batch_first=True)

class VideoTemporalHead(nn.Module):
    def __init__(self, input_dim, cfg, n_cues=10):
        super().__init__()
        self.spec = temporal_spec(cfg)
        if self.spec["temporal_model"] != "transformer":
            raise ValueError("VideoTemporalHead requires temporal_model=transformer")
        dim = self.spec["temporal_dim"]
        self.projection = nn.Sequential(nn.Linear(input_dim, dim), nn.LayerNorm(dim))
        self.register_buffer("frequencies", torch.exp(
            -math.log(10000.) * torch.arange(0, dim, 2, dtype=torch.float32) / dim),
            persistent=False)
        layer = nn.TransformerEncoderLayer(
            d_model=dim, nhead=self.spec["temporal_heads"],
            dim_feedforward=self.spec["temporal_ffn_dim"],
            dropout=self.spec["temporal_dropout"], activation="gelu",
            batch_first=True, norm_first=True)
        self.transformer = nn.TransformerEncoder(
            layer, num_layers=self.spec["temporal_layers"],
            norm=nn.LayerNorm(dim), enable_nested_tensor=False)
        # TransformerEncoder clones its template: initialize each layer separately.
        for block in self.transformer.layers:
            nn.init.xavier_uniform_(block.self_attn.in_proj_weight)
            nn.init.zeros_(block.self_attn.in_proj_bias)
            for module in block.modules():
                if isinstance(module, nn.Linear):
                    nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None: nn.init.zeros_(module.bias)
        self.dropout = nn.Dropout(self.spec["temporal_dropout"])
        self.classifier = nn.Sequential(nn.Linear(dim, 256), nn.GELU(),
                                        nn.Dropout(cfg.get("dropout", .1)), nn.Linear(256, n_cues))

    def position_encoding(self, coordinates):
        angles = coordinates.float().unsqueeze(-1) * self.frequencies.float()
        return torch.stack((angles.sin(), angles.cos()), dim=-1).flatten(-2)

    def forward(self, features, mask, frame_time_offsets):
        if features.ndim != 3 or mask.dtype != torch.bool or features.shape[:2] != mask.shape:
            raise ValueError("Video features/mask dimensions differ")
        if frame_time_offsets.shape != mask.shape or not torch.is_floating_point(frame_time_offsets):
            raise ValueError("Video timestamp tensor must match the sequence mask")
        if not mask.any(1).all() or (~mask[:, :-1] & mask[:, 1:]).any():
            raise ValueError("Video mask must be a nonempty valid prefix")
        if not torch.isfinite(features[mask]).all() or not torch.isfinite(frame_time_offsets[mask]).all():
            raise ValueError("Non-finite valid video feature/timestamp")
        if ((frame_time_offsets[:, 1:] <= frame_time_offsets[:, :-1]) & mask[:, 1:]).any():
            raise ValueError("Video timestamps must be strictly increasing")
        # Remove padding before any arithmetic; even a NaN padding value is harmless.
        safe = features.masked_fill(~mask.unsqueeze(-1), 0)
        seconds = (frame_time_offsets.float() - frame_time_offsets[:, :1].float()).masked_fill(~mask, 0)
        ordinal = (mask.long().cumsum(1) - 1).clamp_min(0)
        position = (self.position_encoding(ordinal) +
                    self.position_encoding(seconds / self.spec["temporal_time_unit_seconds"])) * .5
        projected = self.projection(safe)
        hidden = self.dropout(projected + position.to(projected.dtype))
        hidden = hidden.masked_fill(~mask.unsqueeze(-1), 0)
        hidden = self.transformer(hidden, src_key_padding_mask=~mask)
        hidden = hidden.masked_fill(~mask.unsqueeze(-1), 0)
        pooled = hidden.sum(1) / mask.sum(1, keepdim=True).to(hidden.dtype)
        return self.classifier(pooled)


class AudioTemporalHead(VideoTemporalHead):
    """All HuBERT frames, masked self-attention, no extra subsampling or truncation."""
    def __init__(self, input_dim, cfg):
        if cfg["modality"] != "audio":
            raise ValueError("AudioTemporalHead requires audio modality")
        super().__init__(input_dim, cfg, n_cues=17)

    def forward(self, features, mask):
        step = self.spec["audio_feature_stride_samples"] / self.spec["audio_sample_rate"]
        offsets = torch.arange(features.shape[1], device=features.device, dtype=torch.float32)
        offsets = (offsets * step).expand(mask.shape[0], -1).masked_fill(~mask, 0)
        return super().forward(features, mask, offsets)

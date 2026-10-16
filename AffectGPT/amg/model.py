"""M0 wrapper. The original AffectGPT modules and entry points are untouched."""
from __future__ import annotations
from contextlib import nullcontext
import torch
from torch import nn
from .assembly import assemble_inputs
from .memory import MemoryAdapter

class AMGAffectGPT(nn.Module):
    MODES = {"retrieval", "random", "off", "current", "learned"}

    def __init__(self, base, bank=None, *, memory_mode="retrieval", num_tokens=4,
                 hidden_dim=256, memory_dropout=0.2, train_peft=True, attention_logit_scale=1.0, semantic_values=None, semantic_content="none"):
        super().__init__()
        if memory_mode not in self.MODES:
            raise ValueError(f"Unknown memory mode: {memory_mode}")
        self.base = base
        self.bank = bank
        self.memory_mode = memory_mode
        self.semantic_values = semantic_values
        self.semantic_content = semantic_content
        if (semantic_values is None) != (semantic_content == "none"):
            raise ValueError("Semantic values/content must be configured together")
        self.memory_dropout = float(memory_dropout)
        if not 0 <= self.memory_dropout <= 1:
            raise ValueError("memory_dropout must be in [0,1]")
        self.num_tokens = int(num_tokens)
        dim = base.llama_model.get_input_embeddings().embedding_dim
        self.memory_adapter = MemoryAdapter(d_query=1792, d_value=1792 + (1024 if semantic_values is not None else 0),
            d_hidden=hidden_dim, llm_dim=dim, num_tokens=num_tokens, attention_logit_scale=attention_logit_scale)
        self.learned_tokens = nn.Parameter(torch.empty(num_tokens, dim))
        nn.init.normal_(self.learned_tokens, std=0.01)
        for p in self.base.parameters():
            p.requires_grad_(False)
        if train_peft:
            for name, p in self.base.llama_model.named_parameters():
                if "lora_" in name:
                    p.requires_grad_(True)
                    # The frozen Qwen body is fp16. GradScaler requires fp32
                    # trainable parameters; PEFT handles mixed LoRA input casts.
                    p.data = p.data.float()
        if memory_mode in {"off", "learned"}:
            for p in self.memory_adapter.parameters():
                p.requires_grad_(False)
        self.learned_tokens.requires_grad_(memory_mode == "learned")
        self.train(self.training)

    def train(self, mode=True):
        super().train(mode)
        # All original AV modules are frozen, including optional Q-Formers.
        # Keep their dropout disabled; only LoRA needs the LLM in train mode.
        self.base.eval()
        if any(p.requires_grad for p in self.base.llama_model.parameters()):
            self.base.llama_model.train(mode)
        return self

    @staticmethod
    def _pool(hidden):
        if hidden.ndim < 2:
            raise ValueError("Encoder hidden must have batch and feature dimensions")
        return hidden.float().reshape(hidden.shape[0], -1, hidden.shape[-1]).mean(1)

    def encode_inputs(self, samples):
        """Use exactly the original AV projection and pre-fusion paths."""
        mode = samples["face_or_frame"]
        if not isinstance(mode, str):
            raise ValueError("A batch must have a single face_or_frame mode")
        self.base.face_or_frame = mode
        llm = {}
        raw = {}
        with torch.no_grad():
            if "frames" in samples:
                raw["frame"], llm["frame"] = self.base.encode_video_merge(
                    samples["frames"], samples["raw_frames"])
            if "faces" in samples:
                raw["face"], llm["face"] = self.base.encode_video_merge(
                    samples["faces"], samples["raw_faces"])
            if "audios" in samples:
                raw["audio"], llm["audio"] = self.base.encode_audio_merge(
                    samples["audios"], samples["raw_audios"])
            if "images" in samples:
                raw["image"], llm["image"] = self.base.encode_image_merge(
                    samples["images"], samples["raw_images"])
            ids = samples["input_ids"]
            if (ids == self.base.MULTI_PATCH_TOKEN_ID).any():
                vkey = "face" if mode.startswith("multiface") else "frame"
                if vkey not in raw or "audio" not in raw:
                    raise ValueError("Multi token requires the configured visual and audio input")
                _, llm["multi"] = self.base.encode_multi_merge(raw[vkey], raw["audio"])
        replacements = {}
        for key, attr in (("frame", "FRAME_PATCH_TOKEN_ID"),
                          ("face", "FACE_PATCH_TOKEN_ID"),
                          ("audio", "AUDIO_PATCH_TOKEN_ID"),
                          ("image", "IMAGE_PATCH_TOKEN_ID"),
                          ("multi", "MULTI_PATCH_TOKEN_ID")):
            if (ids == getattr(self.base, attr)).any():
                if key not in llm:
                    raise ValueError(f"Prompt contains {key} placeholder without matching media")
                replacements[getattr(self.base, attr)] = llm[key]
        visual_key = "face" if "face" in raw else ("frame" if "frame" in raw else "image")
        b = ids.shape[0]
        device = ids.device
        visual = self._pool(raw[visual_key]) if visual_key in raw else torch.zeros(b, 768, device=device)
        audio = self._pool(raw["audio"]) if "audio" in raw else torch.zeros(b, 1024, device=device)
        vv = samples.get("visual_valid", torch.full((b,), visual_key in raw, device=device, dtype=torch.bool))
        av = samples.get("audio_valid", torch.full((b,), "audio" in raw, device=device, dtype=torch.bool))
        if visual.shape[-1] != 768 or audio.shape[-1] != 1024:
            raise ValueError("M0 bank requires the selected CLIP-768 / HuBERT-1024 encoders")
        return replacements, visual, audio, vv, av

    def prepare(self, samples, *, labels=True, memory_mode=None):
        mode = memory_mode or self.memory_mode
        if mode not in self.MODES:
            raise ValueError(f"Unknown memory mode: {mode}")
        replacements, visual, audio, vv, av = self.encode_inputs(samples)
        b = visual.shape[0]
        tokens = None
        enabled = torch.zeros(b, dtype=torch.bool, device=visual.device)
        retrieval = None
        gate = None
        if mode == "learned":
            tokens = self.learned_tokens.unsqueeze(0).expand(b, -1, -1)
            enabled = vv | av
            if self.training and self.memory_dropout:
                enabled = enabled & (torch.rand(b, device=enabled.device) >= self.memory_dropout)
        elif mode != "off":
            if mode == "current":
                from torch.nn import functional as F
                query = torch.cat([F.normalize(visual, dim=-1) * vv[:, None],
                                   F.normalize(audio, dim=-1) * av[:, None]], -1)
                values = query[:, None]
                mask = (vv | av)[:, None]
            else:
                if self.bank is None:
                    raise ValueError("retrieval/random mode requires a versioned MemoryBank")
                if self.training and ("clip_ids" not in samples or "group_ids" not in samples):
                    raise ValueError("Training retrieval requires clip_ids and group_ids")
                retrieval = self.bank.retrieve(visual, audio, visual_valid=vv, audio_valid=av,
                    clip_ids=samples.get("clip_ids"), group_ids=samples.get("group_ids"),
                    training=self.training, k=5, mode=mode)
                query, values, mask = retrieval.query_features, retrieval.values, retrieval.mask
            prefix_control = getattr(self, "prefix_control", "none")
            if prefix_control == "bank_mean":
                if self.bank is None:
                    raise ValueError("bank_mean control needs the checkpoint bank")
                values = self.bank.features.mean(0).to(values).view(1, 1, -1).expand_as(values)
            if self.semantic_values is not None:
                if mode == "current" or prefix_control != "none":
                    raise ValueError("Semantic experiments require historical retrieval/random and no prefix control")
                text_values, source_ids = self.semantic_values.lookup(retrieval.ids,
                    samples["clip_ids"], samples["group_ids"], self.semantic_content)
                values = torch.cat([values, text_values.to(values)], -1)
                retrieval.semantic_source_ids = source_ids
            adapted = self.memory_adapter(query, values, mask,
                dropout_p=self.memory_dropout if self.training else 0.0)
            tokens, enabled, gate = adapted.tokens, adapted.enabled, adapted.gate
            if prefix_control == "zero":
                tokens = torch.zeros_like(tokens)
        embed = self.base.llama_model.get_input_embeddings()
        if tokens is not None:
            tokens = tokens.to(device=embed.weight.device, dtype=embed.weight.dtype)
        assembled = assemble_inputs(samples["input_ids"], embed,
            attention_mask=samples.get("attention_masks"),
            labels=samples.get("labels") if labels else None,
            modality_replacements=replacements, memory_tokens=tokens,
            memory_enabled=enabled, insert_indices=samples.get("memory_insert_indices"),
            pad_token_id=self.base.llama_tokenizer.pad_token_id,
            max_length=samples.get("max_length"))
        return assembled, retrieval, gate

    def forward(self, samples, *, memory_mode=None):
        assembled, retrieval, gate = self.prepare(samples, memory_mode=memory_mode)
        with self.base.maybe_autocast():
            result = self.base.llama_model(inputs_embeds=assembled.inputs_embeds,
                attention_mask=assembled.attention_mask,
                position_ids=assembled.position_ids,
                labels=assembled.labels, return_dict=True)
        return {"loss": result.loss, "memory_enabled": assembled.memory_enabled,
                "retrieved_ids": None if retrieval is None else retrieval.ids,
                "semantic_source_ids": getattr(retrieval, "semantic_source_ids", None),
                "gate": gate, "input_lengths": assembled.lengths,
                "attended_lengths": assembled.attention_mask.sum(-1)}

    @torch.no_grad()
    def generate_samples(self, samples, *, memory_mode=None, **generation):
        if self.training:
            raise RuntimeError("Call model.eval() before inference")
        if samples["input_ids"].shape[0] != 1:
            raise ValueError("M0 generation is single-example; no ambiguous right-padded generation")
        assembled, retrieved, gate = self.prepare(samples, labels=False, memory_mode=memory_mode)
        if samples.get("max_length") is not None:
            max_new_tokens = generation.get("max_new_tokens")
            if max_new_tokens is None:
                raise ValueError("A bounded generation requires explicit max_new_tokens")
            if bool((assembled.lengths + int(max_new_tokens) > int(samples["max_length"])).any()):
                raise ValueError("Assembled input plus generation exceeds max_length")
        # Generation computes positions from its evolving attention mask.
        # Passing a static prompt position_ids can freeze positions during decoding.
        with self.base.maybe_autocast():
            output = self.base.llama_model.generate(inputs_embeds=assembled.inputs_embeds,
                attention_mask=assembled.attention_mask, **generation)
        return output, {"retrieved_ids": None if retrieved is None else retrieved.ids,
                        "semantic_source_ids": getattr(retrieved, "semantic_source_ids", None),
                        "semantic_content": self.semantic_content,
                        "memory_enabled": assembled.memory_enabled.detach().cpu().tolist(),
                        "gate": None if gate is None else gate.detach().cpu().tolist()}

    def trainable_state(self):
        return {name: p.detach().cpu().clone() for name, p in self.named_parameters() if p.requires_grad}

    def restore_trainable_state(self, state):
        own = dict(self.named_parameters())
        expected = {name for name, p in own.items() if p.requires_grad}
        if set(state) != expected:
            raise ValueError(f"Trainable checkpoint mismatch missing={expected-set(state)} extra={set(state)-expected}")
        with torch.no_grad():
            for name, tensor in state.items():
                if own[name].shape != tensor.shape:
                    raise ValueError(f"Checkpoint shape mismatch: {name}")
                own[name].copy_(tensor.to(own[name]))

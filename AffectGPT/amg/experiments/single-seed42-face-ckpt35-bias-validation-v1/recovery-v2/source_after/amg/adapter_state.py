"""Deterministic Adapter fingerprints, explicit interventions and shared init loads."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import torch

INIT_SCHEMA = "amg-adapter-initialization-v1"
TARGET_BIAS = "value_projection.2.bias"

def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def tensor_sha256(tensor):
    if not torch.is_tensor(tensor):
        raise TypeError("Fingerprint values must be tensors")
    value = tensor.detach().cpu().contiguous()
    header = json.dumps({"dtype": str(value.dtype), "shape": list(value.shape)},
                        sort_keys=True, separators=(",", ":")).encode("utf-8")
    raw = value.reshape(-1).view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(len(header).to_bytes(8, "big") + header + raw).hexdigest()

def state_hashes(state):
    if not state or any(not isinstance(name, str) for name in state):
        raise ValueError("A nonempty string-keyed tensor state is required")
    parameter_sha256 = {name: tensor_sha256(state[name]) for name in sorted(state)}
    digest = hashlib.sha256(json.dumps(parameter_sha256, sort_keys=True,
                                      separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"state_sha256": digest, "parameter_sha256": parameter_sha256}

def adapter_state_hashes(adapter):
    return state_hashes(adapter.state_dict())

def adapter_config(adapter):
    return {"d_query": int(adapter.d_query), "d_value": int(adapter.d_value),
            "d_hidden": int(adapter.query_projection[0].out_features),
            "llm_dim": int(adapter.llm_dim), "num_tokens": int(adapter.num_tokens),
            "num_heads": int(adapter.attention.num_heads)}

def _bias_summary(tensor):
    value = tensor.detach().float()
    return {"sha256": tensor_sha256(tensor), "shape": list(tensor.shape),
            "dtype": str(tensor.dtype), "numel": tensor.numel(),
            "nonzero": int(torch.count_nonzero(value)), "l2_norm": float(value.norm()),
            "max_abs": float(value.abs().max()) if value.numel() else 0.0,
            "all_finite": bool(torch.isfinite(value).all())}

def apply_value_last_bias_override(adapter, policy="none"):
    if policy not in ("none", "zero"):
        raise ValueError("Value last bias policy must be none or zero")
    own = dict(adapter.named_parameters())
    if TARGET_BIAS not in own:
        raise ValueError("Adapter has no expected value last projection bias")
    target = own[TARGET_BIAS]
    before = adapter_state_hashes(adapter)
    bias_before = _bias_summary(target)
    flags = {name: value.requires_grad for name, value in own.items()}
    if policy == "zero":
        with torch.no_grad():
            target.zero_()
    after = adapter_state_hashes(adapter)
    changed = [name for name in before["parameter_sha256"]
               if before["parameter_sha256"][name] != after["parameter_sha256"][name]]
    if set(changed) - {TARGET_BIAS}:
        raise AssertionError("Explicit bias override modified another parameter")
    if flags != {name: value.requires_grad for name, value in adapter.named_parameters()}:
        raise AssertionError("Explicit bias override changed trainable flags")
    return {"schema": "amg-value-last-bias-intervention-v1", "policy": policy,
            "target_parameter": "memory_adapter." + TARGET_BIAS,
            "applied": policy == "zero", "changed_parameters": changed,
            "source_adapter_sha256": before["state_sha256"],
            "runtime_adapter_sha256": after["state_sha256"],
            "target_before": bias_before, "target_after": _bias_summary(target)}

def strict_load_adapter_init(adapter, path, *, expected_baseline_sha256,
                             expected_config_sha256, expected_seed):
    path = Path(path).resolve()
    payload = torch.load(path, map_location="cpu", weights_only=True)
    if payload.get("schema") != INIT_SCHEMA:
        raise ValueError("Unexpected shared Adapter initialization schema")
    for key, expected in (("baseline_sha256", expected_baseline_sha256),
                          ("config_sha256", expected_config_sha256), ("seed", expected_seed)):
        if payload.get(key) != expected:
            raise ValueError("Shared Adapter initialization differs in " + key)
    if payload.get("adapter_config") != adapter_config(adapter):
        raise ValueError("Shared Adapter dimensions/configuration differ")
    state = payload.get("state_dict")
    if not isinstance(state, dict) or not state:
        raise ValueError("Shared Adapter initialization lacks state_dict")
    if any(not torch.is_tensor(tensor) or not bool(torch.isfinite(tensor).all())
           for tensor in state.values()):
        raise ValueError("Shared Adapter initialization contains invalid/nonfinite tensors")
    actual = state_hashes(state)
    if (actual["state_sha256"] != payload.get("state_sha256") or
            actual["parameter_sha256"] != payload.get("parameter_sha256")):
        raise ValueError("Shared Adapter initialization tensor hashes differ")
    adapter.load_state_dict(state, strict=True)
    loaded = adapter_state_hashes(adapter)
    if loaded != actual:
        raise ValueError("Shared Adapter initialization changed during restoration")
    return {"path": str(path), "file_sha256": file_sha256(path), "schema": INIT_SCHEMA,
            "seed": payload["seed"], "provenance": payload.get("provenance"),
            "adapter_config": payload["adapter_config"], "loaded_adapter": loaded,
            "baseline_lora_float32": payload.get("baseline_lora_float32")}

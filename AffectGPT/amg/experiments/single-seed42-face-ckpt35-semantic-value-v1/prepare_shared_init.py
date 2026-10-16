"""Create one CPU seed42 capacity-matched AV+semantic-value Adapter initialization."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
sys.path.insert(0, str(ROOT))

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--baseline-checkpoint", type=Path, required=True)
    parser.add_argument("--baseline-sha256")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--hidden-dim", type=int, default=256)
    parser.add_argument("--num-tokens", type=int, default=4)
    args = parser.parse_args(argv)
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import torch
    from omegaconf import OmegaConf
    from amg.memory import MemoryAdapter
    from amg.adapter_state import (INIT_SCHEMA, adapter_config, adapter_state_hashes,
                                   file_sha256, state_hashes, tensor_sha256)
    import config
    torch.set_num_threads(2)
    if args.seed != 42:
        raise ValueError("This registered matched trial uses only seed 42")
    args.config, args.baseline_checkpoint, args.output = (
        path.resolve() for path in (args.config, args.baseline_checkpoint, args.output))
    sidecar = Path(str(args.output) + ".json")
    if args.output.exists() or sidecar.exists():
        raise FileExistsError("Refusing to overwrite a shared initialization")
    cfg = OmegaConf.load(args.config)
    llm_config_path = (ROOT / config.PATH_TO_LLM[str(cfg.model.llama_model)] / "config.json").resolve()
    llm_config = json.loads(llm_config_path.read_text())
    llm_dim = int(llm_config["hidden_size"])
    baseline_sha = file_sha256(args.baseline_checkpoint)
    if args.baseline_sha256 is not None and baseline_sha != args.baseline_sha256:
        raise ValueError("Baseline checkpoint SHA256 mismatch")
    raw = torch.load(args.baseline_checkpoint, map_location="cpu", weights_only=True, mmap=True)
    baseline = raw["model"] if "model" in raw else raw
    lora = {name: value.detach().float().cpu() for name, value in baseline.items() if "lora_" in name}
    if not lora or not all(bool(torch.isfinite(t).all()) for t in lora.values()):
        raise ValueError("Baseline has no finite LoRA state")
    lora_hashes = state_hashes(lora)
    del raw, baseline, lora
    # New matched-trial definition. This deliberately bypasses old Qwen/loader
    # constructor RNG consumption and makes no claim about the old initial state.
    torch.manual_seed(args.seed)
    rng_before = torch.get_rng_state().clone()
    adapter = MemoryAdapter(d_query=1792, d_value=2816, d_hidden=args.hidden_dim,
                            llm_dim=llm_dim, num_tokens=args.num_tokens, num_heads=4).float()
    rng_after = torch.get_rng_state().clone()
    state = {name: tensor.detach().cpu().clone() for name,tensor in adapter.state_dict().items()}
    hashes = adapter_state_hashes(adapter)
    provenance = {
        "initialization_definition": "fresh_cpu_seed42_memory_adapter_only",
        "shared_between_matched_runs": True,
        "reproduces_old_training_initialization": False,
        "constructor_order": "torch.manual_seed(42) -> MemoryAdapter(...) once on CPU",
        "old_loader_rng_chain_replayed": False,
        "lora_initialization": "Both arms restore all LoRA weights from the same baseline checkpoint",
        "zero_bias_arm": "Load this complete shared state, then zero only value_projection.2.bias; keep it trainable",
        "no_qwen_loaded": True, "no_gpu_used": True, "no_training": True,
    }
    payload = {
        "schema": INIT_SCHEMA, "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": args.seed, "baseline_checkpoint": str(args.baseline_checkpoint),
        "baseline_sha256": baseline_sha, "config": str(args.config),
        "config_sha256": file_sha256(args.config), "adapter_config": adapter_config(adapter),
        "state_dict": state, **hashes, "baseline_lora_float32": lora_hashes,
        "provenance": provenance,
        "rng": {"kind": "torch_cpu", "before_construction": rng_before,
                "after_construction": rng_after,
                "before_construction_sha256": tensor_sha256(rng_before),
                "after_construction_sha256": tensor_sha256(rng_after)},
        "sources": {str(path): file_sha256(path) for path in (
            Path(__file__).resolve(), ROOT/"amg/memory.py", ROOT/"amg/adapter_state.py",
            ROOT/"config.py", llm_config_path)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        torch.save(payload, stream)
    metadata = {key:value for key,value in payload.items() if key not in ("state_dict","rng")}
    metadata["rng"] = {key:value for key,value in payload["rng"].items() if not torch.is_tensor(value)}
    metadata.update(file_sha256=file_sha256(args.output), tensor_count=len(state),
                    baseline_lora_tensor_count=len(lora_hashes["parameter_sha256"]),
                    shared_file=str(args.output))
    with sidecar.open("x") as stream:
        json.dump(metadata, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output":str(args.output),"metadata":str(sidecar),
                      "state_sha256":hashes["state_sha256"],
                      "baseline_lora_state_sha256":lora_hashes["state_sha256"],
                      "adapter_tensors":len(state),"lora_tensors":metadata["baseline_lora_tensor_count"]}), flush=True)

if __name__ == "__main__":
    main()

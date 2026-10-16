"""Independent fixed-budget M0 trainer; never enters the original run directory."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import torch
from torch.utils.data import DataLoader
from .memory import MemoryBank
from .manifest import read_manifest
from .model import AMGAffectGPT
from .runtime import (DEFAULT_CONFIG, PROJECT, atomic_torch_save, build_dataset,
    checkpoint_payload, load_base, load_config, move_batch,
    seed_all, sha256_file, validate_bank_metadata)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--baseline-checkpoint", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--memory-bank")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--face-or-frame")
    p.add_argument("--mode", choices=sorted(AMGAffectGPT.MODES), default="retrieval")
    p.add_argument("--steps", type=int, required=True, help="Accumulation iterations; each consumes grad-accum microbatches (actual optimizer updates may be skipped)")
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=1)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--weight-decay", type=float, default=0.05)
    p.add_argument("--memory-dropout", type=float, default=0.2)
    p.add_argument("--num-tokens", type=int, default=4)
    p.add_argument("--hidden-dim", type=int, default=256)
    p.add_argument("--freeze-peft", action="store_true")
    p.add_argument("--adapter-init-state", help="Absolute shared Adapter initialization file for a new matched trial")
    p.add_argument("--value-last-bias-init", choices=("preserve", "zero"), default="preserve",
                   help="With --adapter-init-state, preserve or only zero the trainable value_projection.2.bias")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--cuda-memory-fraction", type=float, help="Optional allocator limit for this new CUDA process only, in (0, 1]")
    p.add_argument("--save-every", type=int, default=500)
    p.add_argument("--log-every", type=int, default=10)
    p.add_argument("--allow-partial-bank", action="store_true", help="Smoke tests only")
    p.add_argument("--dry-run", action="store_true", help="Validate provenance; do not load encoders/LLM or create a run")
    return p


def prepare_run(args):
    for name in ("steps", "batch_size", "grad_accum", "num_tokens", "hidden_dim", "save_every", "log_every"):
        if getattr(args, name) <= 0:
            raise ValueError(f"{name} must be positive")
    if args.hidden_dim % 4:
        raise ValueError("hidden_dim must be divisible by the four attention heads")
    if args.workers < 0 or args.lr <= 0 or not 0 <= args.memory_dropout < 1:
        raise ValueError("Invalid workers/lr/memory_dropout")
    if args.cuda_memory_fraction is not None and not 0 < args.cuda_memory_fraction <= 1:
        raise ValueError("cuda_memory_fraction must be in (0, 1]")
    if args.cuda_memory_fraction is not None and torch.device(args.device).type != "cuda":
        raise ValueError("cuda_memory_fraction requires a CUDA device")
    shared_init = getattr(args, "adapter_init_state", None)
    bias_policy = getattr(args, "value_last_bias_init", "preserve")
    if bias_policy != "preserve" and shared_init is None:
        raise ValueError("value-last-bias-init=zero requires --adapter-init-state")
    if shared_init is not None:
        shared_init = Path(shared_init)
        if not shared_init.is_absolute():
            raise ValueError("adapter-init-state must be an absolute server path")
        shared_init = shared_init.resolve()
        if not shared_init.is_file():
            raise FileNotFoundError(shared_init)
        if args.mode not in {"retrieval", "random", "current"}:
            raise ValueError("Shared Adapter initialization requires a trainable Adapter mode")
    cfg = load_config(args.config, face_or_frame=args.face_or_frame)
    manifest = Path(args.manifest).resolve()
    # Validate the training schema before any bank/model loading, including dry-run.
    # Evaluation-only observed manifests omit training descriptions and labels.
    rows = read_manifest(manifest)
    if any(not r.get("group_id") for r in rows):
        raise ValueError("Training manifest requires an explicit nonempty group_id per clip")
    baseline = Path(args.baseline_checkpoint).resolve()
    bank_path = Path(args.memory_bank).resolve() if args.memory_bank else None
    meta = None
    if args.mode in {"retrieval", "random"} and bank_path is None:
        raise ValueError("retrieval/random requires --memory-bank")
    if bank_path is not None:
        meta = validate_bank_metadata(bank_path, cfg, allow_partial=args.allow_partial_bank)
        # Every controlled training strategy uses precisely its training split bank.
        if meta["manifest_sha256"] != sha256_file(manifest):
            raise ValueError("Training Memory must be built from this exact training manifest")
    output = Path(args.output_dir).resolve()
    old_output = (PROJECT / "output").resolve()
    if output == old_output or old_output in output.parents:
        raise ValueError("AMG output must be outside the original AffectGPT/output tree")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output directory is not empty; use a fresh run directory")
    run = {
        "schema": "amg-m0-config-v1", "mode": args.mode,
        "num_tokens": args.num_tokens, "hidden_dim": args.hidden_dim,
        "memory_dropout": args.memory_dropout, "train_peft": not args.freeze_peft,
        "base_checkpoint": str(baseline), "base_sha256": sha256_file(baseline),
        "memory_bank": str(bank_path) if bank_path else None,
        "memory_sha256": meta["bank_sha256"] if meta else None,
        "memory_version": meta.get("version") if meta else None,
        "config_path": str(Path(args.config).resolve()), "config_sha256": sha256_file(args.config),
        "face_or_frame": str(cfg.datasets.mercaptionplus.face_or_frame),
        "manifest": str(manifest), "manifest_sha256": sha256_file(manifest),
        "records": len(rows), "seed": args.seed, "steps": args.steps,
        "budget_unit": "accumulation_iteration", "planned_microsteps": args.steps * args.grad_accum,
        "maximum_optimizer_updates": args.steps, "resume_supported": False,
        "cuda_memory_fraction": args.cuda_memory_fraction,
        "batch_size": args.batch_size, "grad_accum": args.grad_accum,
        "lr": args.lr, "weight_decay": args.weight_decay,
        "allow_partial_bank": args.allow_partial_bank,
        "objective": "original hybrid causal generation only",
        "encoder_policy": "frozen AV encoders eval; original AV projections frozen",
        "group_policy": "manifest group_id; default clip_id, no near-duplicate claim",
    }
    if shared_init is not None:
        run.update(adapter_init_state=str(shared_init),
                   adapter_init_state_sha256=sha256_file(shared_init),
                   value_last_bias_init=bias_policy)
    return cfg, rows, meta, run, output


def load_shared_adapter_initialization(model, args, run):
    """New opt-in matched trial only; no random initialization is performed here.

    The shared payload is an explicitly new experimental initialization, not a
    claim to reproduce a previous run's unsaved random Adapter. The base/LoRA
    checkpoint has already been restored independently by load_base.
    """
    if getattr(args, "adapter_init_state", None) is None:
        return None
    from .adapter_state import (apply_value_last_bias_override,
                                strict_load_adapter_init)
    loaded = strict_load_adapter_init(model.memory_adapter, run["adapter_init_state"],
        expected_baseline_sha256=run["base_sha256"],
        expected_config_sha256=run["config_sha256"], expected_seed=run["seed"])
    if loaded["file_sha256"] != run["adapter_init_state_sha256"]:
        raise ValueError("Shared Adapter initialization changed after preflight")
    bias = model.memory_adapter.value_projection[2].bias
    if bias is None or not bias.requires_grad:
        raise ValueError("Shared trial must retain a trainable value last-layer bias")
    policy = getattr(args, "value_last_bias_init", "preserve")
    override = apply_value_last_bias_override(model.memory_adapter,
                                             policy="none" if policy == "preserve" else "zero")
    return {"shared": loaded, "policy": policy, "bias_override": override}


def save_initialization_audit(model, parameter_audit, run, output, initialization):
    """Reuse the existing CPU parameter snapshot; never copy the frozen base.

    Called before optimizer construction. Exact float32 native-key LoRA hashes
    verify each trial really starts at the shared payload's baseline checkpoint.
    """
    from .adapter_state import state_hashes
    lora = {name.removeprefix("base."): value.float()
            for name, value in parameter_audit.initial.items() if "lora_" in name}
    if not lora:
        raise ValueError("Matched initialization requires trainable baseline LoRA")
    lora_hashes = state_hashes(lora)
    if lora_hashes != initialization["shared"]["baseline_lora_float32"]:
        raise ValueError("Actual initial LoRA differs from the shared baseline float32 hashes")
    adapter = {name.removeprefix("memory_adapter."): value
               for name, value in parameter_audit.initial.items()
               if name.startswith("memory_adapter.")}
    if set(adapter) != set(model.memory_adapter.state_dict()):
        raise ValueError("Initial Adapter snapshot must contain every trainable Adapter tensor")
    adapter_hashes = state_hashes(adapter)
    output.mkdir(parents=True, exist_ok=True)
    snapshot = output / "adapter_initial_state.pth"
    audit_path = output / "adapter_initialization.json"
    if snapshot.exists() or audit_path.exists():
        raise FileExistsError("Refusing to overwrite Adapter initialization audit")
    payload = {"schema": "amg-trained-run-adapter-initial-v1", "state_dict": adapter,
               "seed": run["seed"], "baseline_sha256": run["base_sha256"],
               "config_sha256": run["config_sha256"],
               "shared_init_file_sha256": initialization["shared"]["file_sha256"],
               "value_last_bias_init": initialization["policy"],
               "adapter_hashes": adapter_hashes, "baseline_lora_float32": lora_hashes}
    atomic_torch_save(payload, snapshot)
    record = {"schema": "amg-training-initialization-audit-v1", **initialization,
              "initial_adapter": adapter_hashes, "initial_lora_float32": lora_hashes,
              "snapshot": str(snapshot), "snapshot_sha256": sha256_file(snapshot),
              "snapshot_excludes_frozen_base": True,
              "saved_before_optimizer_and_first_update": True}
    write_json_atomic(audit_path, record)
    run.update(adapter_initialization=record,
               initial_adapter_state_sha256=adapter_hashes["state_sha256"],
               initial_adapter_parameter_sha256=adapter_hashes["parameter_sha256"],
               initial_lora_state_sha256=lora_hashes["state_sha256"],
               initial_lora_parameter_sha256=lora_hashes["parameter_sha256"])


class ExposureAudit:
    """Persist actual consumed examples, including short last batches and retries.

    Requested coverage is the sampler budget; actual coverage can differ after
    failed-read replacement. Final retained length includes masked supervised EOS,
    unlike an attention-mask sum. Checkpoint summaries can be reconstructed from
    the append-only microstep log if a run fails between saves.
    """

    def __init__(self, manifest_rows):
        self.ids = {row["name"]: {"requested": 0, "actual": 0,
                    "task_types": {}, "memory_enabled": 0,
                    "failed_reads": 0, "input_length_min": None,
                    "input_length_max": None} for row in manifest_rows}
        self.microsteps = 0
        self.examples = 0
        self.tasks = Counter()
        self.replacements = 0
        self.failed_reads = 0

    def record(self, batch, result, *, iteration, microstep):
        ids = batch["clip_ids"]
        fields = {name: batch[name] for name in
                  ("original_ids", "actual_ids", "task_types", "replacement_failures")}
        fields["memory_enabled"] = result["memory_enabled"].detach().cpu().tolist()
        fields["input_lengths"] = result["input_lengths"].detach().cpu().tolist()
        budgets = batch.get("budget_metadata", [{} for _ in ids])
        if any(len(values) != len(ids) for values in [*fields.values(), budgets]):
            raise ValueError("Exposure metadata differs from the actual batch size")
        examples = []
        for i, clip_id in enumerate(ids):
            requested, actual = fields["original_ids"][i], fields["actual_ids"][i]
            if actual != clip_id or requested not in self.ids or actual not in self.ids:
                raise ValueError(f"Exposure identity is outside training manifest: {requested} -> {actual}/{clip_id}")
            task = fields["task_types"][i]
            if task not in {"description", "ovlabel"}:
                raise ValueError(f"Unknown actual training task type: {task!r}")
            failures = fields["replacement_failures"][i]
            enabled = bool(fields["memory_enabled"][i])
            length = int(fields["input_lengths"][i])
            entry = {"requested_clip_id": requested, "actual_clip_id": actual,
                     "task_type": task, "replacement_failures": failures,
                     "was_replaced": requested != actual, "memory_enabled": enabled,
                     "input_length": length, "budget": budgets[i]}
            examples.append(entry)
            self.ids[requested]["requested"] += 1
            seen = self.ids[actual]
            seen["actual"] += 1
            seen["task_types"][task] = seen["task_types"].get(task, 0) + 1
            seen["memory_enabled"] += int(enabled)
            seen["input_length_min"] = length if seen["input_length_min"] is None else min(length, seen["input_length_min"])
            seen["input_length_max"] = length if seen["input_length_max"] is None else max(length, seen["input_length_max"])
            self.tasks[task] += 1
            self.replacements += int(requested != actual)
            self.failed_reads += len(failures)
            for failure in failures:
                failed_id = failure["clip_id"]
                if failed_id in self.ids:
                    self.ids[failed_id]["failed_reads"] += 1
        self.microsteps += 1
        self.examples += len(examples)
        return {"iteration": iteration, "microstep": microstep,
                "global_microstep": self.microsteps, "examples": examples}

    def summary(self, *, completed_iterations, optimizer_attempts, optimizer_updates):
        return {"schema": "amg-m0-exposure-v1", "resume_supported": False,
                "completed_iterations": completed_iterations,
                "processed_microsteps": self.microsteps, "examples": self.examples,
                "optimizer_attempts": optimizer_attempts, "optimizer_updates": optimizer_updates,
                "optimizer_skipped_iterations": completed_iterations - optimizer_updates,
                "manifest_records": len(self.ids),
                "requested_covered_ids": sum(row["requested"] > 0 for row in self.ids.values()),
                "actual_covered_ids": sum(row["actual"] > 0 for row in self.ids.values()),
                "missing_requested_ids": sorted(key for key, row in self.ids.items() if row["requested"] == 0),
                "missing_actual_ids": sorted(key for key, row in self.ids.items() if row["actual"] == 0),
                "task_types": dict(self.tasks), "replaced_examples": self.replacements,
                "failed_reads": self.failed_reads, "ids": self.ids}


class ParameterChangeAudit:
    """Compare actual checkpoint values to initial trainable values on CPU.

    Frozen base weights are never copied. The initial copy uses no extra CUDA
    storage; checkpoint comparisons reuse the existing CPU checkpoint snapshot.
    """

    GROUPS = ("lora", "memory_adapter", "learned_tokens", "other")

    def __init__(self, model):
        self.initial = {name: parameter.detach().to(device="cpu", copy=True)
                        for name, parameter in model.named_parameters() if parameter.requires_grad}

    @staticmethod
    def group(name):
        if name.startswith("memory_adapter."):
            return "memory_adapter"
        if name == "learned_tokens":
            return "learned_tokens"
        if "lora_" in name:
            return "lora"
        return "other"

    def summarize(self, checkpoint_state):
        if set(checkpoint_state) != set(self.initial):
            raise ValueError("Parameter change audit requires the exact trainable checkpoint keys")
        groups = {name: {"tensors": 0, "parameters": 0, "changed_tensors": 0,
                        "max_abs_delta": 0.0, "initial_finite": True,
                        "final_finite": True, "delta_finite": True}
                  for name in self.GROUPS}
        for name, initial in self.initial.items():
            current = checkpoint_state[name].detach()
            if current.device.type != "cpu":
                raise ValueError("Parameter change audit requires the existing CPU checkpoint snapshot")
            if current.shape != initial.shape or current.dtype != initial.dtype:
                raise ValueError(f"Parameter change audit shape/dtype mismatch: {name}")
            group = groups[self.group(name)]
            group["tensors"] += 1
            group["parameters"] += initial.numel()
            group["changed_tensors"] += int(not torch.equal(initial, current))
            initial_finite = bool(torch.isfinite(initial).all())
            final_finite = bool(torch.isfinite(current).all())
            # Promote FP16/BF16 for subtraction; preserve double precision.
            dtype = torch.float64 if initial.dtype == torch.float64 else torch.float32
            delta = (current.to(dtype=dtype) - initial.to(dtype=dtype)).abs()
            delta_finite = bool(torch.isfinite(delta).all())
            group["initial_finite"] &= initial_finite
            group["final_finite"] &= final_finite
            group["delta_finite"] &= delta_finite
            if initial_finite and final_finite and delta_finite:
                maximum = float(delta.max()) if delta.numel() else 0.0
                if group["max_abs_delta"] is not None:
                    group["max_abs_delta"] = max(group["max_abs_delta"], maximum)
            else:
                group["max_abs_delta"] = None
        return {"schema": "amg-trainable-parameter-change-v1",
                "comparison": "exact initial versus checkpoint trainable values on CPU",
                "includes_frozen_parameters": False,
                "initial_snapshot_bytes": sum(value.numel() * value.element_size()
                                              for value in self.initial.values()),
                "all_finite": all(group[key] for group in groups.values()
                                  for key in ("initial_finite", "final_finite", "delta_finite")),
                "groups": groups}


def write_json_atomic(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def main(argv=None):
    args = parser().parse_args(argv)
    cfg, rows, meta, run, output = prepare_run(args)
    if args.dry_run:
        print(json.dumps({"validated": True, "run": run}, ensure_ascii=False, indent=2))
        return
    seed_all(args.seed)
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError(f"CUDA requested but unavailable: {device}")
    if device.type == "cpu":
        torch.set_num_threads(4)
    elif args.cuda_memory_fraction is not None:
        torch.cuda.set_per_process_memory_fraction(args.cuda_memory_fraction, device)
    dataset = build_dataset(cfg, run["manifest"], memory_tokens=args.num_tokens)
    generator = torch.Generator().manual_seed(args.seed)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.workers,
        collate_fn=dataset.collater, generator=generator, pin_memory=device.type == "cuda",
        persistent_workers=args.workers > 0)
    bank = MemoryBank.load(run["memory_bank"]).to(device) if run["memory_bank"] else None
    if bank is not None and len(bank) != meta["records"]:
        raise ValueError("Memory record count differs from metadata")
    if bank is not None and not args.allow_partial_bank:
        if set(bank.clip_ids) != {r["name"] for r in rows}:
            raise ValueError("Memory clip IDs differ from training manifest")
    base = load_base(cfg, run["base_checkpoint"], device)
    model = AMGAffectGPT(base, bank, memory_mode=args.mode, num_tokens=args.num_tokens,
        hidden_dim=args.hidden_dim, memory_dropout=args.memory_dropout,
        train_peft=not args.freeze_peft).to(device).train()
    initialization = load_shared_adapter_initialization(model, args, run)
    params = [p for p in model.parameters() if p.requires_grad]
    if not params:
        raise ValueError("No trainable parameters; off requires PEFT")
    parameter_audit = ParameterChangeAudit(model)
    if initialization is not None:
        save_initialization_audit(model, parameter_audit, run, output, initialization)
    optimizer = torch.optim.AdamW(params, lr=args.lr, weight_decay=args.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    output.mkdir(parents=True, exist_ok=True)
    run.update(trainable_parameters=sum(p.numel() for p in params),
               parameter_change_audit="initial CPU trainable snapshot versus each checkpoint",
               started_at=datetime.now(timezone.utc).isoformat())
    (output / "config.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n")
    iterator = iter(loader)
    start = time.monotonic()
    cumulative_examples = optimizer_updates = optimizer_attempts = 0
    audit = ExposureAudit(rows)
    with (output / "train.jsonl").open("a", buffering=1) as log, \
         (output / "exposure.jsonl").open("a", buffering=1) as exposure_log:
        for step in range(1, args.steps + 1):
            optimizer.zero_grad(set_to_none=True)
            loss_total, active_total, n, replacements = 0., 0, 0, []
            backward_count = 0
            for micro in range(args.grad_accum):
                try:
                    batch = next(iterator)
                except StopIteration:
                    iterator = iter(loader)
                    batch = next(iterator)
                replacements.extend({"requested": a, "actual": b, "failures": fail}
                    for a, b, fail in zip(batch["original_ids"], batch["actual_ids"], batch["replacement_failures"]) if a != b or fail)
                batch = move_batch(batch, device)
                result = model(batch)
                exposure = audit.record(batch, result, iteration=step, microstep=micro + 1)
                exposure_log.write(json.dumps(exposure, ensure_ascii=False) + "\n")
                loss = result["loss"]
                if not torch.isfinite(loss):
                    raise FloatingPointError(f"Non-finite loss at step {step}: {batch['clip_ids']}")
                if loss.requires_grad:
                    scaler.scale(loss / args.grad_accum).backward()
                    backward_count += 1
                loss_total += float(loss.detach()) / args.grad_accum
                active_total += int(result["memory_enabled"].sum())
                n += len(batch["clip_ids"])
            norm = 0.0
            overflow = norm_nonfinite = False
            if backward_count:
                optimizer_attempts += 1
                scaler.unscale_(optimizer)
                norm = torch.nn.utils.clip_grad_norm_(params, 1.0, error_if_nonfinite=False)
                norm_nonfinite = not bool(torch.isfinite(norm))
                if norm_nonfinite and device.type != "cuda":
                    raise FloatingPointError(f"Non-finite unscaled gradients at step {step}")
                # GradScaler lowers its scale exactly when found_inf skips the
                # optimizer step. A norm can overflow even when individual grads
                # are finite, so the norm alone is not an update counter.
                scale_before = scaler.get_scale()
                scaler.step(optimizer)
                scaler.update()
                overflow = scaler.get_scale() < scale_before
                optimizer_updates += int(not overflow)
            # With frozen PEFT, an entirely dropped/empty memory batch has no
            # differentiable path. Do not fabricate zero grads or decay inactive weights.
            cumulative_examples += n
            row = {"step": step, "iteration": step, "processed_microsteps": audit.microsteps,
                   "optimizer_attempts": optimizer_attempts, "loss": loss_total, "grad_norm": None if norm_nonfinite else float(norm),
                   "grad_norm_nonfinite": norm_nonfinite, "amp_overflow": overflow,
                   "examples": n, "cumulative_examples": cumulative_examples, "optimizer_updates": optimizer_updates,
                   "no_update": backward_count == 0 or overflow,
                   "memory_enabled": active_total, "elapsed_s": time.monotonic() - start,
                   "replacements": replacements}
            log.write(json.dumps(row, ensure_ascii=False) + "\n")
            if step == 1 or step % args.log_every == 0:
                print(json.dumps(row, ensure_ascii=False), flush=True)
            if step % args.save_every == 0 or step == args.steps:
                payload = checkpoint_payload(model, optimizer, step=step, config=run)
                payload["scaler"] = scaler.state_dict()
                summary = audit.summary(completed_iterations=step,
                    optimizer_attempts=optimizer_attempts, optimizer_updates=optimizer_updates)
                summary["parameter_changes"] = parameter_audit.summarize(payload["model"])
                elapsed = time.monotonic() - start
                summary["resources"] = {
                    "elapsed_s": elapsed, "processed_examples": audit.examples,
                    "examples_per_second": audit.examples / elapsed if elapsed > 0 else None,
                    "device": str(device),
                    "cuda_max_memory_allocated_bytes": int(torch.cuda.max_memory_allocated(device))
                        if device.type == "cuda" else None,
                    "cuda_max_memory_reserved_bytes": int(torch.cuda.max_memory_reserved(device))
                        if device.type == "cuda" else None,
                    "timing_scope": "training loop and audits; excludes model loading and current checkpoint write",
                    "cuda_memory_scope": "process allocator peaks since startup, including model loading",
                }
                payload["resume_supported"] = False
                payload["progress"] = {key: value for key, value in summary.items() if key != "ids"}
                write_json_atomic(output / "coverage.json", summary)
                atomic_torch_save(payload, output / f"checkpoint_{step:06d}.pth")
    print(json.dumps({"completed_steps": args.steps, "completed_iterations": args.steps,
        "optimizer_updates": optimizer_updates, "actual_covered_ids": summary["actual_covered_ids"],
        "output_dir": str(output)}, ensure_ascii=False))

if __name__ == "__main__":
    main()

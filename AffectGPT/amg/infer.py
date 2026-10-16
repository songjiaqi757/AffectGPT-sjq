"""Single-clip AMG M0 inference without target text or training-data retries.

Example: python -m amg.infer --config train_configs/mercaptionplus_frame_gpu1.yaml
  --baseline-checkpoint BASE.pth --amg-checkpoint AMG.pth --memory-bank BANK.pt
  --manifest amg/artifacts/manifests/holdout.jsonl --output predictions.jsonl
  --device cuda:0 --limit 10 --dry-run
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

MODES = ("retrieval", "random", "off", "current", "learned")
CHECKPOINT_FIELDS = ("mode", "num_tokens", "hidden_dim", "memory_dropout", "train_peft",
                     "base_checkpoint", "base_sha256", "memory_bank", "memory_sha256", "face_or_frame")



def canonical_dataset(value):
    key = str(value).strip().lower().replace("-", "").replace("_", "")
    aliases = {"source": "MERCaptionPlus", "mercaptionplus": "MERCaptionPlus",
               "mercaption+": "MERCaptionPlus", "ovmerdplus": "OVMERDPlus", "ovmerd+": "OVMERDPlus"}
    if key not in aliases:
        raise argparse.ArgumentTypeError("dataset must be MERCaptionPlus/source or OVMERDPlus/OV-MERD+")
    return aliases[key]


def export_ovmerdplus_manifest(destination, *, subtitle_csv=None, expected_count=532):
    """Export only subtitle CSV observations; never open ovlabel.csv.

    The original read_test_names uses exactly this CSV's name column. Empty
    sentence fields are preserved as empty subtitles. Source IDs are unchanged.
    """
    import config
    from .manifest import sha256_file
    source = Path(subtitle_csv or config.PATH_TO_TRANSCRIPTIONS["OVMERDPlus"]).resolve()
    records, seen = [], set()
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"name", "sentence"}.issubset(reader.fieldnames or ()):
            raise ValueError("OV-MERD+ subtitle CSV requires name and sentence columns")
        for row in reader:
            name = row["name"]
            if not name or name in seen:
                raise ValueError(f"Empty or duplicate OV-MERD+ clip ID: {name!r}")
            seen.add(name)
            records.append({"name": name, "subtitle": row["sentence"] or "", "group_id": name})
    if len(records) != expected_count:
        raise ValueError(f"Expected {expected_count} OV-MERD+ subtitle rows, got {len(records)}")
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    metadata = {"schema": "amg-observed-manifest-v1", "dataset": "OVMERDPlus",
                "records": len(records), "target_denominator": expected_count,
                "source_csv": str(source), "source_sha256": sha256_file(source),
                "manifest_sha256": sha256_file(destination), "fields": ["name", "subtitle", "group_id"],
                "group_policy": "clip_id_only", "labels_read": False}
    Path(str(destination) + ".json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def load_inference_records(path):
    """Select observed fields immediately; description/ovlabel are never used."""
    rows, seen = [], set()
    with Path(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            source = json.loads(line)
            row = {key: source[key] for key in ("name", "subtitle", "group_id")}
            if any(not isinstance(value, str) for value in row.values()):
                raise ValueError(f"{path}:{number}: name/subtitle/group_id must be strings")
            if not row["name"] or not row["group_id"] or row["name"] in seen:
                raise ValueError(f"{path}:{number}: empty IDs or duplicate clip {row['name']!r}")
            seen.add(row["name"])
            rows.append(row)
    if not rows:
        raise ValueError("Inference manifest is empty")
    return rows


def _load_checkpoint(path):
    import torch
    checkpoint = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
    if checkpoint.get("schema") != "amg-m0-train-v1":
        raise ValueError("Expected an amg-m0-train-v1 checkpoint")
    saved = checkpoint.get("config", {})
    missing = set(CHECKPOINT_FIELDS) - set(saved)
    if missing:
        raise ValueError(f"AMG checkpoint config lacks {sorted(missing)}")
    if saved["mode"] not in MODES or not isinstance(saved.get("train_peft"), bool):
        raise ValueError("Invalid checkpoint mode or train_peft")
    if (int(saved["num_tokens"]) < 1 or int(saved["hidden_dim"]) < 1
            or int(saved["hidden_dim"]) % 4 or not 0 <= float(saved["memory_dropout"]) <= 1):
        raise ValueError("Invalid checkpoint adapter dimensions or dropout")
    if not isinstance(checkpoint.get("model"), dict):
        raise ValueError("AMG checkpoint lacks its trainable model state")
    return checkpoint


def _verify_artifacts(args, saved, cfg):
    from .runtime import sha256_file, validate_bank_metadata
    baseline = Path(args.baseline_checkpoint).resolve()
    if not baseline.is_file():
        raise FileNotFoundError(baseline)
    actual_base = sha256_file(baseline)
    if actual_base != saved["base_sha256"]:
        raise ValueError("Baseline checkpoint SHA256 differs from the AMG training checkpoint")
    configured_bank = args.memory_bank or saved["memory_bank"]
    bank = Path(configured_bank).resolve() if configured_bank else None
    if saved["memory_sha256"] is not None:
        if bank is None or not bank.is_file():
            raise FileNotFoundError("The versioned training memory bank is required")
        if sha256_file(bank) != saved["memory_sha256"]:
            raise ValueError("Memory bank SHA256 differs from the AMG training checkpoint")
        validate_bank_metadata(bank, cfg, allow_partial=False)
    elif bank is not None:
        raise ValueError("Checkpoint has no versioned memory bank; refusing an unrelated bank")
    return baseline, bank


def _build_input_builder(cfg, *, with_processors, dataset="MERCaptionPlus"):
    """Reuse original media paths and prompt templates, with no target dataset."""
    import config
    from .data import load_fast_training_tokenizer
    from my_affectgpt.datasets.datasets.base_dataset import BaseDataset
    from my_affectgpt.common.registry import registry

    selected_dataset = canonical_dataset(dataset)

    class InferenceInputs(BaseDataset):
        def __init__(self):
            self.dataset = selected_dataset
            BaseDataset.__init__(self, model_cfg=None, dataset_cfg=None,
                                 vis_root=config.PATH_TO_RAW_VIDEO[self.dataset],
                                 wav_root=config.PATH_TO_RAW_AUDIO[self.dataset],
                                 face_root=config.PATH_TO_RAW_FACE[self.dataset])
            self.face_or_frame = cfg.datasets.mercaptionplus.face_or_frame
            self.needed_data = self.get_needed_data(self.face_or_frame)
            self.max_length = cfg.model.max_length
            self.n_frms = cfg.model.vis_processor.train.n_frms
            self.tokenizer = load_fast_training_tokenizer(cfg.model.llama_model)
            for name in ("num_video_query_token", "num_audio_query_token",
                         "num_multi_query_token", "num_image_query_token"):
                setattr(self, name, getattr(cfg.model, name))
            if with_processors:
                pc = cfg.inference
                for field, attribute in (("vis_processor", "vis_processor"),
                                         ("text_processor", "txt_processor"),
                                         ("img_processor", "img_processor")):
                    item = pc.get(field)
                    if item is None:
                        from my_affectgpt.processors.base_processor import BaseProcessor
                        value = BaseProcessor()
                    else:
                        value = registry.get_processor_class(item.train.name).from_config(item.train)
                    setattr(self, attribute, value)

        def _get_video_path(self, sample):
            return str(Path(self.vis_root) / (sample["name"] + ".mp4"))

        def _get_audio_path(self, sample):
            return str(Path(self.wav_root) / (sample["name"] + ".wav"))

        def _get_face_path(self, sample):
            name = sample["name"]
            if self.dataset == "OVMERDPlus":
                return str(Path(self.face_root) / (name + ".npy"))
            return str(Path(self.face_root) / name / (name + ".npy"))

    return InferenceInputs()


def prepare_generation_sample(builder, record, *, task="ovlabel", question=None, read_media=True,
                              memory_tokens=4, max_new_tokens=512):
    """Produce prompt+BOS, no target/EOS; no random replacement on read errors."""
    import torch
    from .data import _index_from_offsets
    from .budget import budget_prompt
    from .runtime import media_sample
    if question is None:
        method = (builder.func_get_qa_description if task == "description"
                  else builder.func_get_qa_ovlabel)
        question = method({}, question_only=True)
    budgeted = budget_prompt(builder.tokenizer,
        lambda subtitle: builder.replace_token_for_multimodal(builder.get_prompt_for_multimodal(
            builder.face_or_frame, subtitle, question)),
        record["subtitle"], max_length=int(builder.max_length), bos_tokens=1,
        memory_tokens=int(memory_tokens), generation_tokens=int(max_new_tokens))
    prompt = budgeted.prompt
    ids = torch.tensor(budgeted.input_ids, dtype=torch.long)
    bos = torch.tensor([builder.tokenizer.bos_token_id], dtype=ids.dtype)
    ids = torch.cat((bos, ids)).unsqueeze(0)
    sample = {"input_ids": ids, "attention_masks": ids.ne(builder.tokenizer.pad_token_id),
              "memory_insert_indices": torch.tensor([
                  _index_from_offsets(prompt, budgeted.offsets, bos_offset=1)], dtype=torch.long),
              "face_or_frame": builder.face_or_frame, "dataset": getattr(builder, "dataset", "MERCaptionPlus").lower(),
              "clip_ids": [record["name"]], "group_ids": [record["group_id"]],
              "subtitles": [record["subtitle"]], "task_types": [task],
              "max_length": int(builder.max_length), "budget_metadata": [budgeted.metadata]}
    if read_media:
        media = media_sample(builder, record)
        for name in ("frame", "raw_frame", "face", "raw_face", "audio", "raw_audio", "image", "raw_image"):
            if media.get(name) is not None:
                sample[name + "s"] = media[name].unsqueeze(0)
    return sample, prompt


def _stopping_criteria(tokenizer):
    from transformers import StoppingCriteria, StoppingCriteriaList

    class EndOfTurn(StoppingCriteria):
        def __call__(self, input_ids, scores, **kwargs):
            # Single-example CLI. Decoding the short suffix handles contextual
            # Qwen BPE variants of ### without a tokenizer-specific hardcode.
            return "###" in tokenizer.decode(input_ids[0, -8:], skip_special_tokens=False)

    return StoppingCriteriaList([EndOfTurn()])


def _decode_output(tokenizer, output):
    ids = output.sequences if hasattr(output, "sequences") else output
    response = tokenizer.decode(ids[0], skip_special_tokens=True)
    response = response.split("###", 1)[0]
    return response.split("Assistant:")[-1].strip()


def _validate_generation_override(trained, effective):
    # Frozen parameter groups were intentionally omitted from trainable_state.
    # Do not silently generate with a newly randomized, never-saved adapter.
    if effective in {"retrieval", "random", "current"} and trained in {"off", "learned"}:
        raise ValueError(f"Cannot use {effective} with a {trained} checkpoint: no trained adapter was saved")
    if effective == "learned" and trained != "learned":
        raise ValueError("learned mode requires a checkpoint trained in learned mode")


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config", type=Path, required=True)
    result.add_argument("--baseline-checkpoint", type=Path, required=True)
    result.add_argument("--amg-checkpoint", type=Path, required=True)
    result.add_argument("--memory-bank", type=Path, help="Defaults to the bank saved in the AMG checkpoint")
    result.add_argument("--manifest", type=Path, required=True)
    result.add_argument("--dataset", type=canonical_dataset, default="MERCaptionPlus",
                        help="Media paths: MERCaptionPlus/source (default) or OVMERDPlus/OV-MERD+")
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--device", default="cuda:0")
    result.add_argument("--cuda-memory-fraction", type=float)
    result.add_argument("--prefix-control", choices=("none", "zero", "bank_mean"), default="none")
    result.add_argument("--semantic-content-override", choices=("av_only", "subtitle", "caption", "shuffled_caption"))
    result.add_argument("--limit", type=int)
    result.add_argument("--memory-mode", choices=MODES, help="Generation override; checkpoint loading uses its trained mode")
    result.add_argument("--task", choices=("ovlabel", "description"), default="ovlabel")
    result.add_argument("--value-last-bias-override", choices=("none", "zero"), default="none",
                        help="Explicit post-checkpoint inference intervention; zero only the trained value last-layer bias")
    result.add_argument("--question", help="Optional explicit question, used instead of the task's default prompt")
    result.add_argument("--max-new-tokens", type=int, default=512)
    result.add_argument("--seed", type=int, default=42)
    result.add_argument("--overwrite", action="store_true")
    result.add_argument("--dry-run", action="store_true", help="Validate metadata, hashes and prompts without model/media loading")
    return result


def main(argv=None):
    import torch
    from .runtime import load_config, load_base, move_batch, seed_all, sha256_file
    args = parser().parse_args(argv)
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive")
    if args.max_new_tokens < 1:
        raise ValueError("--max-new-tokens must be positive")
    # Resolve caller paths before load_config intentionally changes cwd.
    for name in ("config", "baseline_checkpoint", "amg_checkpoint", "manifest", "output", "memory_bank"):
        if getattr(args, name) is not None:
            setattr(args, name, getattr(args, name).resolve())
    if args.cuda_memory_fraction is not None:
        if not 0 < args.cuda_memory_fraction <= 1 or not args.device.startswith("cuda"):
            raise ValueError("cuda-memory-fraction requires CUDA and a value in (0,1]")
        if not args.dry_run:
            torch.cuda.set_per_process_memory_fraction(args.cuda_memory_fraction, torch.device(args.device))
    checkpoint = _load_checkpoint(args.amg_checkpoint)
    saved = checkpoint["config"]
    if saved.get("config_sha256") is not None and sha256_file(args.config) != saved["config_sha256"]:
        raise ValueError("Model config file SHA256 differs from the training checkpoint")
    # Training can explicitly override face/frame without editing its YAML.
    cfg = load_config(args.config, face_or_frame=saved["face_or_frame"])
    baseline, bank_path = _verify_artifacts(args, saved, cfg)
    effective = args.memory_mode or saved["mode"]
    if args.prefix_control != "none" and effective != "retrieval":
        raise ValueError("Prefix controls require retrieval mode on a trained retrieval adapter")
    _validate_generation_override(saved["mode"], effective)
    semantic_content = args.semantic_content_override or saved.get("semantic_content", "none")
    if args.semantic_content_override and not saved.get("semantic_values"):
        raise ValueError("Semantic override requires a semantic-trained checkpoint")
    if saved.get("semantic_values") and sha256_file(saved["semantic_values"]) != saved["semantic_values_sha256"]:
        raise ValueError("Checkpoint semantic artifact hash differs")
    if args.value_last_bias_override == "zero" and saved["mode"] not in {"retrieval", "random", "current"}:
        raise ValueError("Bias override requires a checkpoint with a trained Memory Adapter")
    if effective in {"retrieval", "random"} and bank_path is None:
        raise ValueError(f"{effective} generation requires the checkpoint's versioned memory bank")
    records = load_inference_records(args.manifest)
    selected = records[:args.limit] if args.limit else records
    builder = _build_input_builder(cfg, with_processors=not args.dry_run, dataset=args.dataset)
    previews, preview_errors = [], []
    for row in selected:
        preview = {"name": row["name"]}
        try:
            sample, _ = prepare_generation_sample(builder, row, task=args.task,
                                                  question=args.question, read_media=False,
                                                  memory_tokens=int(saved["num_tokens"]),
                                                  max_new_tokens=args.max_new_tokens)
            preview.update(prompt_tokens=sample["input_ids"].shape[1],
                           memory_insert_index=sample["memory_insert_indices"].item(),
                           budget=sample["budget_metadata"][0])
        except Exception as error:
            preview["error"] = f"{type(error).__name__}: {error}"
            preview_errors.append(preview.copy())
        if len(previews) < 3:
            previews.append(preview)
    metadata = {"schema": "amg-m0-inference-v1", "baseline_checkpoint": str(baseline),
                "base_sha256": saved["base_sha256"], "amg_checkpoint": str(args.amg_checkpoint),
                "amg_sha256": sha256_file(args.amg_checkpoint),
                "memory_bank": str(bank_path) if bank_path else None,
                "memory_sha256": saved["memory_sha256"], "manifest": str(args.manifest),
                "manifest_sha256": sha256_file(args.manifest), "selected_clips": len(selected),
                "dataset": args.dataset, "manifest_records": len(records),
                "target_denominator": 532 if args.dataset == "OVMERDPlus" else len(records),
                "preview_errors": preview_errors, "validated": not preview_errors,
                "trained_mode": saved["mode"], "memory_mode": effective,
                "prefix_control": args.prefix_control,
                "semantic_content": semantic_content, "trained_semantic_content": saved.get("semantic_content", "none"),
                "semantic_values": saved.get("semantic_values"), "semantic_values_sha256": saved.get("semantic_values_sha256"),
                "attention_logit_scale": float(saved.get("attention_logit_scale", 1.0)),
                "cuda_memory_fraction": args.cuda_memory_fraction,
                "task": args.task, "question": args.question, "seed": args.seed,
                "face_or_frame": saved["face_or_frame"], "previews": previews,
                "dry_run": args.dry_run, "max_new_tokens": args.max_new_tokens,
                "requested_value_last_bias_override": args.value_last_bias_override,
                "model_intervention": {"schema": "amg-value-last-bias-intervention-v1",
                    "policy": args.value_last_bias_override, "applied": False,
                    "runtime_adapter_sha256": None, "provenance": "not_executed_yet"},
                "training_initialization": {key: saved.get(key) for key in (
                    "adapter_init_state", "adapter_init_state_sha256", "value_last_bias_init",
                    "initial_adapter_state_sha256", "initial_lora_state_sha256")},
                "prompt_version": "amg-source-question-v1",
                "infer_sha256": sha256_file(Path(__file__).resolve()),
                "base_dataset_sha256": sha256_file(
                    Path(__file__).resolve().parents[1] / "my_affectgpt/datasets/datasets/base_dataset.py"),
                "budget_schema": "amg-context-budget-v1",
                "budget_source_sha256": sha256_file(Path(__file__).resolve().with_name("budget.py")),
                "config_sha256": sha256_file(args.config),
                "max_length": int(builder.max_length),
                "memory_tokens_reserved": int(saved["num_tokens"]),
                "decoding": {"do_sample": False, "num_beams": 1,
                             "max_new_tokens": args.max_new_tokens,
                             "eos_token_id": builder.tokenizer.eos_token_id,
                             "pad_token_id": builder.tokenizer.pad_token_id}}
    prompt_identity = {key: metadata[key] for key in
                       ("prompt_version", "base_dataset_sha256", "task", "question")}
    metadata["prompt_sha256"] = hashlib.sha256(json.dumps(
        prompt_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if args.dry_run:
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        return 1 if preview_errors else 0
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError(f"CUDA requested but unavailable: {args.device}")
    trace_path = args.output.with_name(args.output.stem + ".retrieval.jsonl")
    metadata_path = args.output.with_name(args.output.stem + ".meta.json")
    if not args.overwrite:
        for path in (args.output, trace_path, metadata_path):
            if path.exists():
                raise FileExistsError(f"Refusing to overwrite {path}; use --overwrite explicitly")
    seed_all(args.seed)
    from .memory import MemoryBank
    from .model import AMGAffectGPT
    bank = MemoryBank.load(bank_path).to(args.device) if bank_path else None
    semantic_values = None
    if saved.get("semantic_values"):
        from .semantic_values import SemanticValues
        semantic_values = SemanticValues.load(saved["semantic_values"], bank, saved["semantic_values_sha256"])
        if semantic_values.bank_sha256 != saved["memory_sha256"]:
            raise ValueError("Semantic values differ from the checkpoint AV bank")
    base = load_base(cfg, baseline, args.device)
    # Restore with the checkpoint's trained parameter set before any ablation.
    model = AMGAffectGPT(base, bank, memory_mode=saved["mode"],
                        num_tokens=int(saved["num_tokens"]), hidden_dim=int(saved["hidden_dim"]),
                        memory_dropout=float(saved["memory_dropout"]), train_peft=saved["train_peft"],
                        attention_logit_scale=float(saved.get("attention_logit_scale", 1.0)),
                        semantic_values=semantic_values, semantic_content=semantic_content)
    model.restore_trainable_state(checkpoint["model"])
    model.prefix_control = args.prefix_control
    if saved["mode"] in {"retrieval", "random", "current"}:
        from .adapter_state import apply_value_last_bias_override
        metadata["model_intervention"] = apply_value_last_bias_override(
            model.memory_adapter, args.value_last_bias_override)
    else:
        metadata["model_intervention"] = {
            "schema": "amg-value-last-bias-intervention-v1", "policy": "none", "applied": False,
            "runtime_adapter_sha256": None, "provenance": "adapter_unused_and_not_in_checkpoint"}
    del checkpoint
    model.to(args.device).eval()
    stopping = _stopping_criteria(builder.tokenizer)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    successes = errors = 0
    write_mode = "w" if args.overwrite else "x"
    with metadata_path.open(write_mode, encoding="utf-8") as meta_output:
        meta_output.write(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    with args.output.open(write_mode, encoding="utf-8") as output, trace_path.open(write_mode, encoding="utf-8") as traces:
        for row in selected:
            trace = None
            result = {"name": row["name"], "group_id": row["group_id"], "dataset": args.dataset,
                      "trained_mode": saved["mode"], "memory_mode": effective,
                "prefix_control": args.prefix_control,
                "semantic_content": semantic_content, "trained_semantic_content": saved.get("semantic_content", "none"),
                "semantic_values": saved.get("semantic_values"), "semantic_values_sha256": saved.get("semantic_values_sha256"),
                "attention_logit_scale": float(saved.get("attention_logit_scale", 1.0)),
                "cuda_memory_fraction": args.cuda_memory_fraction, "task": args.task}
            try:
                sample, _ = prepare_generation_sample(builder, row, task=args.task,
                                                      question=args.question, read_media=True,
                                                      memory_tokens=int(saved["num_tokens"]),
                                                      max_new_tokens=args.max_new_tokens)
                result["budget"] = sample["budget_metadata"][0]
                with torch.inference_mode():
                    generated, trace = model.generate_samples(move_batch(sample, args.device),
                        memory_mode=effective, max_new_tokens=args.max_new_tokens, do_sample=False,
                        num_beams=1, stopping_criteria=stopping,
                        eos_token_id=builder.tokenizer.eos_token_id,
                        pad_token_id=builder.tokenizer.pad_token_id)
                result["prediction"] = _decode_output(builder.tokenizer, generated)
                result["retrieval"] = trace
                successes += 1
            except Exception as error:
                # Record the requested clip. Never swap it for a readable clip.
                result["error"] = f"{type(error).__name__}: {error}"
                errors += 1
            output.write(json.dumps(result, ensure_ascii=False) + "\n")
            traces.write(json.dumps({"name": row["name"], "group_id": row["group_id"], "dataset": args.dataset,
                                     "retrieval": trace, "error": result.get("error")}, ensure_ascii=False) + "\n")
            output.flush()
            traces.flush()
    metadata.update(successes=successes, errors=errors)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "retrieval_trace": str(trace_path),
                      "metadata": str(metadata_path), "successes": successes, "errors": errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

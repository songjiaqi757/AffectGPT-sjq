"""Deterministic source-dev/holdout scoring for one preselected AMG checkpoint.

This is an exact normalized open-label-set metric, NOT the paper's nine-dataset
emotion-wheel (EW) metric. No API, model, target labels, epoch search or GPU is
used. Missing/error/empty predictions remain in the full manifest denominator.
The description task is a lexical diagnostic only, not reasoning quality.

Example:
 python -m amg.evaluate --manifest amg/artifacts/manifests/dev.jsonl --split dev \
   --predictions RUN/dev.jsonl --output RUN/dev.metrics.json
Use --paired-report OFF/dev.metrics.json for paired deltas and group bootstrap.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import re
import unicodedata

from .manifest import read_manifest, sha256_file

SCHEMA = "amg-source-evaluation-v1"
PARSER_VERSION = "source-label-parser-v1"
SCORER_VERSION = "source-open-set-f1-v1"
RESOURCE = Path(__file__).with_name("resources") / "source_evaluation_v1.json"
QUESTIONS = {
    "ovlabel": "Please recognize all possible emotional states of the character.",
    "description": "Please infer the person's emotional state and provide your reasoning process.",
}


def object_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def normalise_text(value):
    value = unicodedata.normalize("NFKC", str(value)).casefold()
    return re.sub(r"\s+", " ", value.replace("\u2019", "'").replace("\u2013", "-")
                  .replace("\u2014", "-")).strip()


def load_resource(path=RESOURCE):
    path = Path(path)
    resource = json.loads(path.read_text(encoding="utf-8"))
    if resource.get("schema") != "amg-source-label-resource-v1":
        raise ValueError("Unsupported label resource schema")
    aliases = {}
    for canonical, variants in resource["alias_groups"].items():
        for variant in [canonical, *variants]:
            variant = normalise_text(variant)
            if variant in aliases and aliases[variant] != canonical:
                raise ValueError("Conflicting label alias: " + variant)
            aliases[variant] = canonical
    resource["_aliases"] = aliases
    resource["_known"] = set(resource["known_canonical_labels"])
    resource["_path"] = str(path.resolve())
    resource["_sha256"] = sha256_file(path)
    return resource


def canonicalise(value, resource):
    label = normalise_text(value).strip(" \t\r\n.,;:!?\"'[](){}")
    return resource["_aliases"].get(label, label)


def parse_ovlabel(text, resource):
    """Recognize actual training wrapper, lists, or explicit delimited labels.

    Arbitrary unknown label phrases are retained and charged as false positives.
    We do not keyword-search ovlabel prose, stem words or collapse synonyms.
    Negated labels remain distinct strings, so 'not angry' never becomes anger.
    """
    if not isinstance(text, str):
        raise ValueError("Prediction must be a string")
    value = unicodedata.normalize("NFKC", text).replace("\u2019", "'")
    value = value.split("###", 1)[0].split("Assistant:")[-1].strip()
    if normalise_text(value) in {"", "none", "no emotions", "no emotion", "n/a", "[]"}:
        return {"labels": [], "unmapped": [], "empty": True, "parser": "empty"}
    fragments = None
    if value.startswith("["):
        for loader in (json.loads, ast.literal_eval):
            try:
                parsed = loader(value)
            except (ValueError, SyntaxError, TypeError):
                continue
            if isinstance(parsed, (list, tuple)) and all(isinstance(x, str) for x in parsed):
                fragments = list(parsed)
                break
        if fragments is None:
            # Malformed output is retained, rather than silently becoming no FP.
            fragments = [value]
        parser = "list"
    else:
        value = re.sub(r"^\s*(?:the\s+)?(?:character|person|individual)(?:'s)?"
                       r"\s+emotional\s+states?\s*(?:is|are|includes?|:)\s*",
                       "", value, flags=re.I)
        value = re.sub(r"^\s*(?:emotions?|emotional states?|labels?)\s*:\s*",
                       "", value, flags=re.I)
        value = re.sub(r"(?m)^\s*(?:[-*]|\d+[.)])\s*", "", value)
        fragments = re.split(r"[,;\n]|\s+(?:and|&)\s+", value)
        parser = "delimited"
    labels = sorted({canonicalise(x, resource) for x in fragments if canonicalise(x, resource)})
    return {"labels": labels,
            "unmapped": [x for x in labels if x not in resource["_known"]],
            "empty": not labels, "parser": parser}


def description_labels(text, resource):
    """Frozen fit-vocabulary lexical diagnostic; limited immediate negation."""
    value = normalise_text(text)
    candidates = {x: x for x in resource["_known"]}
    candidates.update(resource["_aliases"])
    matches = []
    # Longest phrase wins, avoiding a second match for 'blame' in 'self-blame'.
    for phrase, canonical in candidates.items():
        for match in re.finditer(r"(?<![\w-])" + re.escape(phrase) + r"(?![\w-])", value):
            prefix = value[max(0, match.start() - 30):match.start()]
            if re.search(r"\b(?:not|no|never|without)\s+(?:very\s+)?$", prefix):
                continue
            matches.append((match.start(), match.end(), canonical))
    occupied, labels = [], set()
    for start, end, canonical in sorted(matches, key=lambda x: (-(x[1] - x[0]), x[0], x[2])):
        if any(start < other_end and end > other_start for other_start, other_end in occupied):
            continue
        occupied.append((start, end))
        labels.add(canonical)
    return {"labels": sorted(labels), "unmapped": [], "empty": not labels,
            "parser": "fit-vocabulary-lexical-diagnostic"}


def set_scores(reference, prediction):
    reference, prediction = set(reference), set(prediction)
    tp = len(reference & prediction)
    fp, fn = len(prediction - reference), len(reference - prediction)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def word_overlap_f1(reference, prediction):
    reference = Counter(re.findall(r"[a-z0-9]+", normalise_text(reference)))
    prediction = Counter(re.findall(r"[a-z0-9]+", normalise_text(prediction)))
    overlap = sum((reference & prediction).values())
    denominator = sum(reference.values()) + sum(prediction.values())
    return 2 * overlap / denominator if denominator else 0.0


def aggregate(rows):
    tp, fp, fn = (sum(row[key] for row in rows) for key in ("tp", "fp", "fn"))
    count = len(rows)
    return {"N": count, "tp": tp, "fp": fp, "fn": fn,
            "micro_precision": tp / (tp + fp) if tp + fp else 0.0,
            "micro_recall": tp / (tp + fn) if tp + fn else 0.0,
            "micro_f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
            "sample_macro_precision": sum(row["precision"] for row in rows) / count if count else 0.0,
            "sample_macro_recall": sum(row["recall"] for row in rows) / count if count else 0.0,
            "sample_macro_f1": sum(row["f1"] for row in rows) / count if count else 0.0}


def read_predictions(path):
    rows = {}
    with Path(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            name = row.get("name")
            if not isinstance(name, str) or not name or name in rows:
                raise ValueError(f"{path}:{number}: empty/duplicate prediction name")
            if "checkpoint" in row or "amg_checkpoint" in row:
                raise ValueError("Per-row checkpoint overrides are unsupported; use one inference run")
            rows[name] = row
    return rows


def _valid_hash(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def validate_metadata(metadata, manifest_path, task):
    if metadata.get("schema") != "amg-m0-inference-v1" or metadata.get("dry_run"):
        raise ValueError("A completed amg.infer metadata sidecar is required")
    if metadata.get("dataset") != "MERCaptionPlus":
        raise ValueError("This evaluator accepts source MERCaptionPlus only, never target labels")
    if metadata.get("manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("Inference and evaluation manifest SHA256 differ")
    if metadata.get("task") != task:
        raise ValueError("Inference task differs from scoring task")
    for field in ("amg_sha256", "base_sha256"):
        if not _valid_hash(metadata.get(field)):
            raise ValueError("Missing/invalid single-checkpoint hash: " + field)
    if not isinstance(metadata.get("amg_checkpoint"), str) or not metadata["amg_checkpoint"]:
        raise ValueError("Exactly one preselected checkpoint path is required")
    if not isinstance(metadata.get("seed"), int):
        raise ValueError("Inference seed is required for paired comparisons")
    if metadata.get("memory_sha256") is not None and not _valid_hash(metadata["memory_sha256"]):
        raise ValueError("Invalid memory bank SHA256")


def evaluate(manifest_path, predictions_path, *, split, task="ovlabel",
             metadata_path=None, resource_path=RESOURCE):
    if split not in {"dev", "holdout"}:
        raise ValueError("Only declared source dev/holdout splits are supported")
    manifest_path, predictions_path = Path(manifest_path), Path(predictions_path)
    metadata_path = Path(metadata_path) if metadata_path else predictions_path.with_name(
        predictions_path.stem + ".meta.json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    validate_metadata(metadata, manifest_path, task)
    references = read_manifest(manifest_path)
    predictions = read_predictions(predictions_path)
    extra = set(predictions) - {row["name"] for row in references}
    if extra:
        raise ValueError("Prediction IDs outside evaluation manifest: " + repr(sorted(extra)[:5]))
    resource = load_resource(resource_path)
    rows = []
    for reference in references:
        name = reference["name"]
        prediction = predictions.get(name)
        error, state, text = None, "success", ""
        if prediction is None:
            state, error = "missing", "No prediction row"
        else:
            if prediction.get("dataset", "MERCaptionPlus") != "MERCaptionPlus":
                raise ValueError(f"Target/foreign dataset prediction: {name}")
            if prediction.get("group_id", reference["group_id"]) != reference["group_id"]:
                raise ValueError(f"Prediction group differs from manifest: {name}")
            if prediction.get("task", task) != task:
                raise ValueError(f"Mixed prediction tasks: {name}")
            for field in ("memory_mode", "trained_mode"):
                if field in prediction and prediction[field] != metadata.get(field):
                    raise ValueError(f"Mixed inference {field}: {name}")
            if prediction.get("error") is not None:
                state, error = "error", str(prediction["error"])
            elif not isinstance(prediction.get("prediction"), str):
                state, error = "error", "Missing/non-string prediction"
            else:
                text = prediction["prediction"]
        parsed = (parse_ovlabel(text, resource) if task == "ovlabel"
                  else description_labels(text, resource))
        truth = parse_ovlabel(reference["ovlabel"], resource)
        if not truth["labels"]:
            raise ValueError("Empty source reference labels: " + name)
        scores = set_scores(truth["labels"], parsed["labels"])
        rows.append({"name": name, "group_id": reference["group_id"], "status": state,
                     "error": error, "empty_prediction": not text.strip() or parsed["empty"],
                     "prediction": text, "reference_labels": truth["labels"],
                     "prediction_labels": parsed["labels"], "unmapped_prediction_labels": parsed["unmapped"],
                     "reference_labels_outside_fit_vocabulary": truth["unmapped"],
                     "description_word_overlap_f1": word_overlap_f1(reference["description"], text)
                     if task == "description" else None, **scores})
    counts = Counter(row["status"] for row in rows)
    metrics = aggregate(rows)
    metrics.update(successful_predictions=counts["success"],
                   failed_predictions=counts["error"] + counts["missing"],
                   generation_errors=counts["error"], missing_predictions=counts["missing"],
                   empty_predictions=sum(row["empty_prediction"] for row in rows),
                   empty_successful_predictions=sum(row["empty_prediction"] and row["status"] == "success"
                                                    for row in rows),
                   unmapped_prediction_clips=sum(bool(row["unmapped_prediction_labels"]) for row in rows),
                   unmapped_prediction_labels=sum(len(row["unmapped_prediction_labels"]) for row in rows),
                   reference_clips_outside_fit_vocabulary=sum(
                       bool(row["reference_labels_outside_fit_vocabulary"]) for row in rows))
    if task == "description":
        metrics["description_word_overlap_f1"] = sum(
            row["description_word_overlap_f1"] for row in rows) / len(rows)
    code_root = Path(__file__).parent.parent
    prompt_sources = {str(path.relative_to(code_root)): sha256_file(path) for path in (
        code_root / "amg/infer.py",
        code_root / "my_affectgpt/datasets/datasets/base_dataset.py") if path.is_file()}
    prompt_hash = metadata.get("prompt_sha256")
    prompt_provenance = "inference_metadata"
    if not _valid_hash(prompt_hash):
        prompt_hash = object_hash({"question": metadata.get("question") or QUESTIONS[task],
                                   "task": task, "current_prompt_sources": prompt_sources})
        prompt_provenance = "legacy_metadata_current_source_fallback"
    provenance = {
        "dataset": "MERCaptionPlus", "split": split, "task": task, "seed": metadata["seed"],
        "checkpoint_selection": "one_preselected_checkpoint_no_epoch_search",
        "checkpoint": metadata["amg_checkpoint"], "checkpoint_sha256": metadata["amg_sha256"],
        "base_checkpoint_sha256": metadata["base_sha256"],
        "memory_bank": metadata.get("memory_bank"), "memory_bank_sha256": metadata.get("memory_sha256"),
        "trained_mode": metadata.get("trained_mode"), "memory_mode": metadata.get("memory_mode"),
        "manifest": str(manifest_path.resolve()), "manifest_sha256": sha256_file(manifest_path),
        "predictions": str(predictions_path.resolve()), "predictions_sha256": sha256_file(predictions_path),
        "inference_metadata": str(metadata_path.resolve()), "inference_metadata_sha256": sha256_file(metadata_path),
        "resource_version": resource["version"], "resource_sha256": resource["_sha256"],
        "resource_fit_manifest_sha256": resource.get("fit_manifest_sha256"),
        "parser_version": PARSER_VERSION, "scorer_version": SCORER_VERSION,
        "parser_source_sha256": sha256_file(__file__), "scorer_source_sha256": sha256_file(__file__),
        "prompt_sha256": prompt_hash, "prompt_version": metadata.get("prompt_version"),
        "inference_source_sha256": metadata.get("infer_sha256"),
        "base_dataset_sha256": metadata.get("base_dataset_sha256"),
        "prompt_provenance": prompt_provenance, "prompt_source_hashes_at_evaluation": prompt_sources,
        "model_intervention": metadata.get("model_intervention", {
            "policy": "none", "runtime_adapter_sha256": None,
            "provenance": "legacy_inference_runtime_fingerprint_not_recorded"}),
        "requested_value_last_bias_override": metadata.get("requested_value_last_bias_override", "none"),
        "training_initialization": metadata.get("training_initialization"),
        "generation_policy": {key: metadata.get("decoding", {}).get(key, metadata.get(key)) for key in (
            "max_new_tokens", "do_sample", "num_beams", "eos_token_id", "pad_token_id",
            "face_or_frame", "config_sha256", "max_length", "budget_schema", "budget_source_sha256")},
    }
    return {"schema": SCHEMA, "metric_name": "source_normalized_open_label_set",
            "is_paper_nine_benchmark_ew": False, "primary_metrics": ["micro_f1", "sample_macro_f1"],
            "description_is_lexical_diagnostic": task == "description",
            "rules": {"all_manifest_clips_in_denominator": True,
                      "unknown_prediction_labels": "retained_as_false_positives_unless_exact_gold_match",
                      "empty_reference_and_prediction_f1": 0.0,
                      "unknown_gold_labels": "retained_exact_identity",
                      "group_policy": "manifest_group_id_may_be_clip_id_only",
                      "description_negation": "only_immediately_preceding_no_not_never_without"},
            "metadata": provenance, "metrics": metrics, "per_clip": rows}


def _percentile(values, probability):
    values = sorted(values)
    position = (len(values) - 1) * probability
    left, right = int(position), min(int(position) + 1, len(values) - 1)
    return values[left] + (values[right] - values[left]) * (position - left)


def paired_comparison(report, baseline, *, resamples=1000, bootstrap_seed=42):
    if baseline.get("schema") != SCHEMA or report.get("schema") != SCHEMA:
        raise ValueError("Paired comparison requires source evaluation reports")
    for field in ("dataset", "split", "task", "seed", "manifest_sha256", "base_checkpoint_sha256",
                  "resource_sha256", "parser_version", "scorer_version", "scorer_source_sha256",
                  "prompt_sha256", "generation_policy"):
        if report["metadata"].get(field) != baseline["metadata"].get(field):
            raise ValueError("Paired reports differ in " + field)
    current = {row["name"]: row for row in report["per_clip"]}
    previous = {row["name"]: row for row in baseline["per_clip"]}
    if current.keys() != previous.keys():
        raise ValueError("Paired reports have different clip IDs")
    groups, pairs = defaultdict(list), []
    for name, row in current.items():
        prior = previous[name]
        if (row["group_id"] != prior["group_id"]
                or row["reference_labels"] != prior["reference_labels"]):
            raise ValueError("Paired report references/groups differ: " + name)
        delta = row["f1"] - prior["f1"]
        pairs.append({"name": name, "group_id": row["group_id"], "delta_f1": delta})
        groups[row["group_id"]].append(name)
    deltas = {key: report["metrics"][key] - baseline["metrics"][key]
              for key in ("micro_f1", "sample_macro_f1")}
    result = {"definition": "current_minus_paired_baseline", "N": len(pairs),
              "delta": deltas,
              "negative_gain_fraction": sum(row["delta_f1"] < 0 for row in pairs) / len(pairs),
              "positive_gain_fraction": sum(row["delta_f1"] > 0 for row in pairs) / len(pairs),
              "zero_gain_fraction": sum(row["delta_f1"] == 0 for row in pairs) / len(pairs),
              "per_clip": pairs}
    if resamples < 0:
        raise ValueError("bootstrap resamples must be non-negative")
    if resamples:
        rng, keys = random.Random(bootstrap_seed), sorted(groups)
        samples = {key: [] for key in deltas}
        for _ in range(resamples):
            names = [name for _ in keys for name in groups[rng.choice(keys)]]
            left, right = aggregate([current[name] for name in names]), aggregate([previous[name] for name in names])
            for key in samples:
                samples[key].append(left[key] - right[key])
        result["bootstrap"] = {
            "unit": "manifest_group_id", "independent_groups": len(keys),
            "seed": bootstrap_seed, "resamples": resamples, "confidence": 0.95,
            "interval_method": "percentile_paired_group_resampling",
            "intervals": {key: [_percentile(values, .025), _percentile(values, .975)]
                          for key, values in samples.items()},
            "interpretation": "sample_uncertainty_for_this_seed_not_training_seed_variability"}
    return result


def audit_original_format(path):
    """Read the original resource only; do not use it as scorer normalization."""
    path = Path(path)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = {row["name"]: row["format"].split(",") for row in csv.DictReader(stream)}
    fear = set(rows.get("fear", ())) | set(rows.get("fearful", ()))
    fearless = set(rows.get("fearless", ()))
    return {"path": str(path.resolve()), "sha256": sha256_file(path),
            "used_for_scoring": False, "fear_variants": sorted(fear),
            "fearless_variants": sorted(fearless),
            "cross_polarity_shared_variants": sorted(fear & fearless),
            "action": "original_unchanged_independent_explicit_alias_resource"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split", choices=("dev", "holdout"), required=True)
    parser.add_argument("--predictions", type=Path, required=True,
                        help="Exactly one amg.infer JSONL; no directory/glob or checkpoint sweep")
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--task", choices=("ovlabel", "description"), default="ovlabel")
    parser.add_argument("--resource", type=Path, default=RESOURCE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--paired-report", type=Path)
    parser.add_argument("--bootstrap-resamples", type=int, default=1000)
    parser.add_argument("--bootstrap-seed", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    if args.bootstrap_resamples < 0:
        parser.error("--bootstrap-resamples must be non-negative")
    protected_inputs = [args.manifest, args.predictions, args.resource]
    if args.metadata:
        protected_inputs.append(args.metadata)
    if args.paired_report:
        protected_inputs.append(args.paired_report)
    if args.output.resolve() in {path.resolve() for path in protected_inputs}:
        raise ValueError("Evaluation output must differ from every input path")
    if args.output.exists() and not args.overwrite:
        raise FileExistsError("Refusing to overwrite evaluation report: " + str(args.output))
    report = evaluate(args.manifest, args.predictions, split=args.split, task=args.task,
                      metadata_path=args.metadata, resource_path=args.resource)
    audit_path = Path(__file__).parent.parent / "emotion_wheel/format.csv"
    if audit_path.is_file():
        report["original_format_audit"] = audit_original_format(audit_path)
    if args.paired_report:
        baseline = json.loads(args.paired_report.read_text(encoding="utf-8"))
        report["paired"] = paired_comparison(
            report, baseline, resamples=args.bootstrap_resamples, bootstrap_seed=args.bootstrap_seed)
        report["paired"]["baseline_report_sha256"] = sha256_file(args.paired_report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w" if args.overwrite else "x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(args.output.resolve()), "metrics": report["metrics"],
                      "paired_delta": report.get("paired", {}).get("delta")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


"""Reproducible MER-Caption+ manifests; source data stay on the server.

The full main manifest retains every training clip, including the accepted 99
OV-MERD+ overlaps. Development subsets are group-disjoint, not a claim of global
video deduplication. Without an explicit mapping, group_id is only the clip ID.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

DEFAULT_SOURCE = Path(__file__).resolve().parents[2] / "dataset/mer2025-dataset"
REQUIRED_FIELDS = ("name", "subtitle", "description", "ovlabel", "group_id")
SCHEMA_VERSION = 1


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _read_csv(path: Path, required: Iterable[str]) -> dict[str, dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = set(required) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        rows = {}
        for line, row in enumerate(reader, 2):
            name = row["name"]
            if not name or name in rows:
                raise ValueError(f"{path}:{line}: empty or duplicate name {name!r}")
            rows[name] = row
    return rows


def normalise_ovlabel(value: str | None) -> str:
    """Match the existing string_to_list + ', '.join, without pandas imports."""
    value = (value or "").strip()
    if value.startswith("["):
        value = value[1:]
    if value.endswith("]"):
        value = value[:-1]
    labels = [part.strip() for part in re.split(r"['\",]", value) if part.strip()]
    return ", ".join(labels or ["neutral"])


def build_source_records(source_dir: str | Path = DEFAULT_SOURCE,
                         group_map: dict[str, str] | None = None,
                         expected_count: int | None = 31327) -> list[dict]:
    source_dir = Path(source_dir)
    ov = _read_csv(source_dir / "track2_train_mercaptionplus.csv", ("name", "openset"))
    reasons = _read_csv(source_dir / "track3_train_mercaptionplus.csv", ("name", "reason"))
    subtitles = _read_csv(source_dir / "subtitle_chieng.csv", ("name", "english"))
    if expected_count is not None and len(ov) != expected_count:
        raise ValueError(f"Expected {expected_count} source clips, got {len(ov)}")
    group_map = group_map or {}
    records = []
    for name, row in ov.items():
        if name not in reasons or name not in subtitles:
            raise ValueError(f"Missing description or subtitle row for {name}")
        group_id = group_map.get(name, name)
        if not isinstance(group_id, str) or not group_id:
            raise ValueError(f"Invalid group_id for {name}: {group_id!r}")
        records.append({"name": name, "subtitle": subtitles[name]["english"] or "",
                        "description": reasons[name]["reason"],
                        "ovlabel": normalise_ovlabel(row["openset"]), "group_id": group_id})
    return records


def read_manifest(path: str | Path) -> list[dict]:
    records, seen = [], set()
    with Path(path).open(encoding="utf-8") as stream:
        for line, text in enumerate(stream, 1):
            if not text.strip():
                continue
            row = json.loads(text)
            if any(key not in row for key in REQUIRED_FIELDS):
                raise ValueError(f"{path}:{line}: required fields are {REQUIRED_FIELDS}")
            if any(not isinstance(row[key], str) for key in REQUIRED_FIELDS):
                raise ValueError(f"{path}:{line}: manifest values must be strings")
            if not row["name"] or not row["group_id"] or row["name"] in seen:
                raise ValueError(f"{path}:{line}: empty/duplicate name or empty group_id")
            seen.add(row["name"])
            records.append(row)
    if not records:
        raise ValueError(f"{path}: manifest is empty")
    return records


def split_records(records: list[dict], seed: int = 42,
                  sizes: tuple[int, int, int] = (4000, 500, 500)) -> dict[str, list[dict]]:
    """Take approximately the requested rows, preserving each supplied group.

    Overshoot can be up to the size of the last selected group. Remaining rows
    still belong to main; they are not silently promoted into the 5K pilot.
    """
    if len(sizes) != 3 or any(size < 0 for size in sizes):
        raise ValueError("sizes must contain three non-negative integers")
    groups = defaultdict(list)
    for row in records:
        groups[row["group_id"]].append(row)
    ordered_groups = sorted(groups)
    random.Random(seed).shuffle(ordered_groups)
    result, cursor = {}, 0
    for split, target in zip(("fit", "dev", "holdout"), sizes):
        selected = []
        while len(selected) < target and cursor < len(ordered_groups):
            selected.extend(groups[ordered_groups[cursor]])
            cursor += 1
        if len(selected) < target:
            raise ValueError(f"Not enough independent groups/rows for {split}={target}")
        result[split] = selected
    return result


def write_manifests(source_dir: str | Path, output_dir: str | Path, *, seed: int = 42,
                    sizes: tuple[int, int, int] = (4000, 500, 500),
                    group_map_path: str | Path | None = None,
                    expected_count: int | None = 31327) -> dict:
    source_dir, output_dir = Path(source_dir).resolve(), Path(output_dir).resolve()
    group_map = None
    if group_map_path is not None:
        with Path(group_map_path).open(encoding="utf-8") as stream:
            group_map = json.load(stream)
        if not isinstance(group_map, dict):
            raise ValueError("group map must be a JSON object {clip_id: group_id}")
    records = build_source_records(source_dir, group_map, expected_count)
    splits = {"main": records, **split_records(records, seed, sizes)}
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, rows in splits.items():
        path = output_dir / f"{name}.jsonl"
        path.write_bytes(b"".join(_json_bytes(row) + b"\n" for row in rows))
        outputs[name] = {"file": path.name, "rows": len(rows), "sha256": sha256_file(path)}
    source_files = ["track2_train_mercaptionplus.csv", "track3_train_mercaptionplus.csv", "subtitle_chieng.csv"]
    metadata = {"schema_version": SCHEMA_VERSION, "seed": seed, "requested_split_sizes": list(sizes),
                "group_policy": "supplied_mapping_with_clip_id_fallback" if group_map_path else "clip_id_only",
                "deduplication_claim": False, "retain_all_training_clips": True,
                "accepted_ovmerdplus_overlap_count": 99,
                "source_dir": str(source_dir),
                "source_sha256": {name: sha256_file(source_dir / name) for name in source_files},
                "group_map_sha256": sha256_file(group_map_path) if group_map_path else None,
                "outputs": outputs}
    metadata["version_sha256"] = hashlib.sha256(_json_bytes(metadata)).hexdigest()
    (output_dir / "version.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=Path("amg/artifacts/manifests"))
    parser.add_argument("--group-map", type=Path, help="Optional JSON clip_id -> source group_id mapping")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fit-size", type=int, default=4000)
    parser.add_argument("--dev-size", type=int, default=500)
    parser.add_argument("--holdout-size", type=int, default=500)
    parser.add_argument("--expected-count", type=int, default=31327, help="Set 0 only for a deliberate non-production fixture")
    args = parser.parse_args(argv)
    result = write_manifests(args.source_dir, args.output_dir, seed=args.seed,
                            sizes=(args.fit_size, args.dev_size, args.holdout_size),
                            group_map_path=args.group_map, expected_count=args.expected_count or None)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

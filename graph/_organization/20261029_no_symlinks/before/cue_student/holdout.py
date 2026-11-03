"""Frozen human-audit membership and training/validation leakage guards."""
from __future__ import annotations
import json
from pathlib import Path
from .common import PROJECT,canonical_hash,sha256
from .eligibility import POLICY

DIRECTORY=PROJECT/"cue_student/splits/holdout300"

def load_fixed_holdout(directory=None):
    directory=Path(directory) if directory is not None else DIRECTORY
    path=directory/"manifest.json"
    if not path.exists():
        if directory.exists(): raise ValueError("Incomplete fixed holdout directory")
        return None
    manifest=json.loads(path.read_text())
    content={k:v for k,v in manifest.items() if k!="holdout_id"}
    if canonical_hash(content)!=manifest["holdout_id"]: raise ValueError("Fixed holdout manifest changed")
    ids=manifest["sample_ids"]
    if manifest.get("sample_eligibility")!=POLICY or set(ids)&set(manifest.get("excluded_failed_sample_ids",[])):
        raise ValueError("Fixed holdout must exclude every failed-annotation sample")
    if len(ids)!=300 or len(set(ids))!=300: raise ValueError("Fixed holdout needs 300 distinct IDs")
    for name,digest in manifest["files"].items():
        if sha256(directory/name)!=digest: raise ValueError("Fixed holdout file changed: "+name)
    members=json.loads((directory/"members.json").read_text())
    if [r["sample_id"] for r in members]!=ids: raise ValueError("Holdout member order/identity differs")
    return manifest

def fingerprint_sets(manifest):
    return {m:{r[m+"_sha256"] for r in manifest["media_fingerprints"].values()} for m in ("audio","visual")}

def assert_holdout_separation(rows,manifest):
    if manifest is None: return
    reserved=set(manifest["sample_ids"]);fingerprints=fingerprint_sets(manifest)
    reserved_groups=set()
    for row in rows:
        assets=row.get("media_assets",{})
        same_media=any(assets.get(m,{}).get("sha256") in fingerprints[m] for m in ("audio","visual"))
        if row["sample_id"] in reserved or same_media:
            reserved_groups.add(row["group_id"])
    for row in rows:
        if row.get("role") in ("pseudo_train","pseudo_validation") and row["group_id"] in reserved_groups:
            raise ValueError("Fixed holdout leak into training/validation: "+row["sample_id"])

def heldout_group_ids(rows,manifest):
    if manifest is None: return set()
    fingerprints=fingerprint_sets(manifest);ids=set(manifest["sample_ids"]);groups=set()
    for row in rows:
        assets=row.get("media_assets",{})
        if row["sample_id"] in ids or any(assets.get(m,{}).get("sha256") in fingerprints[m] for m in ("audio","visual")):
            groups.add(row["group_id"])
    return groups

"""Create a frozen server-side data package. Smoke packages are explicitly barred from formal training."""
from __future__ import annotations
import argparse, csv, json, sqlite3, random, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from .common import PROJECT, MODALITIES, STATES, absolute, atomic_json, canonical_hash, sha256
from .holdout import load_fixed_holdout,heldout_group_ids,assert_holdout_separation,DIRECTORY
from .eligibility import annotation_eligibility,assert_eligible_members

RUN = PROJECT / "cue_annotation/runs/mercaptionplus"

def load_labels(samples, ontology, csv_path):
    ids = [s["sample_id"] for s in samples]
    if len(set(ids)) != len(ids): raise ValueError("Duplicate sample ID")
    cues = [c for m in MODALITIES for c in ontology["cue_ids"][m]]
    if len(set(cues)) != len(cues) or [len(ontology["cue_ids"][m]) for m in MODALITIES] != [15, 17, 10]:
        raise ValueError("Expected ordered 15/17/10 ontology")
    sid_index = {s: i for i, s in enumerate(ids)}
    cue_index = {c: k for k, c in enumerate(cues)}
    cue_modality = {c: m for m in MODALITIES for c in ontology["cue_ids"][m]}
    shape = (len(samples), len(cues)); states = np.full(shape, 255, dtype=np.uint8)
    targets = np.zeros(shape, dtype=np.float32); mask = np.zeros(shape, dtype=bool)
    with Path(csv_path).open() as stream:
        for r in csv.DictReader(stream):
            if r["sample_id"] not in sid_index or r["cue_id"] not in cue_index: raise ValueError("Unexpected label key")
            i, k = sid_index[r["sample_id"]], cue_index[r["cue_id"]]
            if r["modality"] != cue_modality[r["cue_id"]]: raise ValueError("Wrong cue modality")
            if states[i, k] != 255: raise ValueError("Duplicate label key")
            st = r["state"]
            if st not in STATES: raise ValueError("Illegal state")
            expected = ("1", "1") if st == "positive" else ("0", "1") if st == "negative" else ("", "0")
            if (r["y"], r["mask"]) != expected: raise ValueError("state/y/mask disagreement")
            states[i, k] = STATES.index(st)
            if st in ("positive", "negative"): targets[i, k] = float(st == "positive"); mask[i, k] = True
    if (states == 255).any(): raise ValueError("Missing label keys")
    return targets, mask, states

class UnionFind:
    def __init__(self, ids): self.parent = {x: x for x in ids}
    def root(self, x):
        if self.parent[x] != x: self.parent[x] = self.root(self.parent[x])
        return self.parent[x]
    def union(self, a, b):
        a, b = self.root(a), self.root(b)
        if a != b: self.parent[max(a, b)] = min(a, b)

def assign_roles(rows, y, mask, audit_size, diagnostic_size, val_ratio=.1, exposure=(), fixed_audit_ids=None):
    groups = defaultdict(list)
    for i, r in enumerate(rows): groups[r["group_id"]].append(i)
    if not 0 < val_ratio < 1: raise ValueError("validation fraction")
    exposed = set(exposure); pool = [g for g in sorted(groups) if not any(rows[i]["sample_id"] in exposed for i in groups[g])]
    rng = random.Random(42); rng.shuffle(pool)
    for g in pool: rng.shuffle(groups[g])
    if fixed_audit_ids is not None:
        if len(fixed_audit_ids)!=audit_size or len(set(fixed_audit_ids))!=audit_size:
            raise ValueError("Fixed audit size differs; do not silently redraw")
        index={r["sample_id"]:i for i,r in enumerate(rows)}
        if not set(fixed_audit_ids)<=set(index): raise ValueError("Fixed holdout members missing from release")
        selected=[index[sid] for sid in fixed_audit_ids]
        if any(rows[i]["group_id"] not in pool for i in selected):
            raise ValueError("Fixed holdout group conflicts with development exposure; review provenance instead of redrawing")
    else:
        selected = []; round_id = 0
        while len(selected) < audit_size:
            available = [g for g in pool if len(groups[g]) > round_id]
            if not available: raise ValueError("Insufficient unexposed audit candidates")
            rng.shuffle(available)
            for g in available:
                if len(selected) == audit_size: break
                selected.append(groups[g][round_id])
            round_id += 1
    audit_groups = {rows[i]["group_id"] for i in selected}
    rest = [g for g in pool if g not in audit_groups]; rng.shuffle(rest)
    diagnostic_groups = set(); n = 0
    for g in rest:
        if n >= diagnostic_size: break
        diagnostic_groups.add(g); n += len(groups[g])
    if n < diagnostic_size: raise ValueError("Insufficient diagnostic candidates")
    available = [g for g in sorted(groups) if g not in audit_groups | diagnostic_groups]
    if len(available) < 2: raise ValueError("Need at least two remaining training groups")
    rng = random.Random(44); rng.shuffle(available)
    vectors = {g: np.concatenate([((y[groups[g]] == 1) & mask[groups[g]]).sum(0),
                                  ((y[groups[g]] == 0) & mask[groups[g]]).sum(0)]).astype(float) for g in available}
    target = sum(vectors.values()) * val_ratio
    desired_n = max(1, round(sum(len(groups[g]) for g in available) * val_ratio))
    current = np.zeros_like(target); current_n = 0; val_groups = set()
    while available and current_n < desired_n and len(available) > 1:
        choices = available[:64]
        def cost(g):
            err = np.mean(((current + vectors[g] - target) / np.maximum(target, 1)) ** 2)
            return err + 2 * ((current_n + len(groups[g]) - desired_n) / desired_n) ** 2
        best = min(choices, key=cost); available.remove(best); val_groups.add(best)
        current += vectors[best]; current_n += len(groups[best])
    audited = set(selected)
    for i, r in enumerate(rows):
        g = r["group_id"]
        r["role"] = ("gold_audit" if i in audited else "audit_group_excluded") if g in audit_groups else (
            "diagnostic_reserved" if g in diagnostic_groups else "pseudo_validation" if g in val_groups else "pseudo_train")
    roles = defaultdict(set)
    for r in rows: roles[r["group_id"]].add(r["role"])
    for rs in roles.values():
        if len(rs) > 1 and not rs <= {"gold_audit", "audit_group_excluded"}: raise ValueError("Group leakage")
    return dict(audit_seed=42, double_annotation_seed=43, split_seed=44,
                audit_sample_ids=[rows[i]["sample_id"] for i in selected],
                double_annotation_sample_ids=random.Random(43).sample([rows[i]["sample_id"] for i in selected], min(60, audit_size)),
                role_counts=dict(Counter(r["role"] for r in rows)))

def verify_member(r, run, ontology, tasks, all_index, state_all):
    import soundfile as sf
    import av
    annotation_records = 0; checked_media = 0
    r["media_assets"] = {}
    offset = 0
    for m in MODALITIES:
        k = len(ontology["cue_ids"][m]); i = all_index[r["sample_id"]]
        ann_path = run / "annotations" / (r["sample_id"] + "." + m + ".json")
        if tasks[(r["sample_id"], m)] == "succeeded":
            rec = json.loads(ann_path.read_text())["annotation"]
            if rec["sample_id"] != r["sample_id"] or rec["modality"] != m or set(rec["labels"]) != set(ontology["cue_ids"][m]):
                raise ValueError(f"Annotation schema mismatch: {ann_path}")
            for j,cue in enumerate(ontology["cue_ids"][m]):
                label = rec["labels"][cue]
                if label["state"] != STATES[state_all[i,offset+j]]: raise ValueError("Annotation/CSV state mismatch")
            annotation_records += 1
        elif ann_path.exists(): raise ValueError("Stale failed annotation file")
        if m != "text":
            path = Path(r["audio_path" if m == "audio" else "video_path"]).resolve()
            st = path.stat(); digest = sha256(path); checked_media += 1
            metadata = run / "inputs" / (r["sample_id"] + "." + m + ".json")
            meta = json.loads(metadata.read_text()) if metadata.exists() else {}
            if meta.get("source_sha256") and digest != meta["source_sha256"]: raise ValueError("Source media changed since annotation")
            if m == "audio":
                info = sf.info(path); duration = info.frames / info.samplerate
            else:
                with av.open(str(path)) as c:
                    v = c.streams.video[0]; duration = float(v.duration * v.time_base) if v.duration is not None else meta.get("duration_sec")
            if not duration or duration <= 0: raise ValueError(f"Invalid duration: {path}")
            r[m + "_duration"] = duration
            r["media_assets"][m] = dict(path=str(path), bytes=st.st_size, mtime_ns=st.st_mtime_ns, sha256=digest)
        offset += k
    return r, annotation_records, checked_media

def build(args):
    import soundfile as sf
    import av
    run = absolute(args.run); out = absolute(args.output)
    if out.exists(): raise FileExistsError(f"Refusing to overwrite release: {out}")
    fixed=load_fixed_holdout()
    if fixed is not None and args.scope!="smoke" and sha256(run/"samples.json")!=fixed["source_samples_sha256"]:
        raise ValueError("Fixed holdout belongs to a different source manifest")
    all_samples = json.loads((run / "samples.json").read_text())
    ontology = json.loads((run / "ontology.json").read_text())
    y_all, mask_all, state_all = load_labels(all_samples, ontology, run / "labels.csv")
    all_index = {s["sample_id"]: i for i, s in enumerate(all_samples)}
    db = sqlite3.connect("file:" + str(run / "tasks.sqlite3") + "?mode=ro", uri=True)
    tasks = {(sid, m): status for sid, m, status in db.execute("select sid,modality,state from tasks")}; db.close()
    if len(tasks) != len(all_samples) * 3 or any(s not in ("succeeded", "failed") for s in tasks.values()):
        raise ValueError("Queue not settled or task keys incomplete")
    eligibility=annotation_eligibility(run,all_samples)
    allowed=set(eligibility["eligible_sample_ids"])
    if fixed is not None:assert_eligible_members(fixed["sample_ids"],eligibility)
    start = 0
    for m in MODALITIES:
        k = len(ontology["cue_ids"][m])
        for i, sample in enumerate(all_samples):
            success = tasks[(sample["sample_id"], m)] == "succeeded"
            missing = state_all[i, start:start+k] == STATES.index("unlabeled")
            if (success and missing.any()) or (not success and not missing.all()): raise ValueError("DB/CSV mismatch")
        start += k
    if args.scope == "smoke":
        reserved=set(fixed["sample_ids"]) if fixed else set()
        eligible=[i for i,r in enumerate(all_samples) if r["sample_id"] not in reserved and r["sample_id"] in allowed]
        n=min(args.max_samples,len(eligible))
        extras=[eligible[0]]
        empty=next((i for i in eligible if not all_samples[i]["text"].get("english","").strip()),None)
        if empty is not None and empty not in extras:extras.append(empty)
        extras=extras[:n]
        rng=random.Random(42);chosen=sorted(extras+rng.sample([i for i in eligible if i not in extras],n-len(extras)))
    else: chosen = [i for i,r in enumerate(all_samples) if r["sample_id"] in allowed]
    rows = [dict(all_samples[i]) for i in chosen]
    y, mask, states = y_all[chosen], mask_all[chosen], state_all[chosen]
    uf = UnionFind([r["sample_id"] for r in rows]); group_meta = {}
    if args.groups:
        with absolute(args.groups).open() as stream:
            mapping = {r["sample_id"]: r for r in csv.DictReader(stream)}
        first = {}
        for r in rows:
            entry = mapping[r["sample_id"]]
            if entry.get("source_status") not in ("verified_source", "verified_duplicate", "unknown"):
                raise ValueError("groups.csv needs source_status")
            g = entry["group_id"]; group_meta[r["sample_id"]] = entry["source_status"]
            if g in first: uf.union(first[g], r["sample_id"])
            first[g] = r["sample_id"]
    elif args.scope != "smoke" and not args.allow_unverified_groups:
        raise ValueError("Supply verified groups or explicitly use --allow-unverified-groups for a limited engineering release")
    from concurrent.futures import ThreadPoolExecutor
    from functools import partial
    workers = getattr(args, "workers", 8)
    if workers < 1: raise ValueError("workers must be positive")
    verify = partial(verify_member, run=run, ontology=ontology, tasks=tasks,
                     all_index=all_index, state_all=state_all)
    seen_hash = {"audio": {}, "visual": {}}; annotation_records = 0; checked_media = 0
    # map yields original member order; only the main thread mutates group unions.
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for r, records, media in executor.map(verify, rows):
            annotation_records += records; checked_media += media
            for m in ("audio", "visual"):
                digest = r["media_assets"][m]["sha256"]
                if digest in seen_hash[m]: uf.union(r["sample_id"], seen_hash[m][digest])
                seen_hash[m][digest] = r["sample_id"]
    for r in rows:
        r["group_id"] = uf.root(r["sample_id"])
        r["source_status"] = group_meta.get(r["sample_id"], "unknown")
    exposure_path = PROJECT / "cue_student/artifacts/development_exposure.json"
    exposure = json.loads(exposure_path.read_text()).get("sample_ids", []) if exposure_path.exists() else []
    if args.scope=="smoke" and fixed is not None:
        blocked=heldout_group_ids(rows,fixed)
        keep=np.array([r["group_id"] not in blocked for r in rows],dtype=bool)
        rows=[r for r,k in zip(rows,keep) if k];y,mask,states=y[keep],mask[keep],states[keep]
    split = assign_roles(rows, y, mask, args.audit_size, args.diagnostic_size, args.val_fraction,
                         exposure=exposure if args.scope != "smoke" else (),
                         fixed_audit_ids=fixed["sample_ids"] if fixed is not None and args.scope!="smoke" else None)
    assert_holdout_separation(rows,fixed)
    group_limitations = []
    if any(r["source_status"] != "verified_source" for r in rows):
        group_limitations.append("Original video provenance not verified for all members; exact file duplicates merged, but near-duplicate/source leakage not ruled out.")
    support = {}
    for role in sorted(set(r["role"] for r in rows)):
        sel = np.array([r["role"] == role for r in rows])
        support[role] = dict(positive=((y[sel] == 1) & mask[sel]).sum(0).tolist(),
                             negative=((y[sel] == 0) & mask[sel]).sum(0).tolist(),
                             masked=(~mask[sel]).sum(0).tolist())
    out.mkdir(parents=True)
    np.savez_compressed(out / "labels.npz", targets=y, mask=mask, states=states)
    atomic_json(out / "members.json", rows); atomic_json(out / "ontology.json", ontology)
    assert_eligible_members([r["sample_id"] for r in rows],eligibility)
    atomic_json(out / "eligibility.json",eligibility)
    manifest = dict(format_version=1, scope=args.scope, n_samples=len(rows), full_source_n_samples=len(all_samples),
                    source_artifacts={n: sha256(run/n) for n in ("samples.json","labels.csv","ontology.json","protocol.json")},
                    files={n: sha256(out/n) for n in ("members.json","labels.npz","ontology.json","eligibility.json")},
                    sample_eligibility=eligibility["policy"],excluded_samples=len(eligibility["excluded_sample_ids"]),
                    verified_annotation_records=annotation_records, verified_original_media=checked_media, preparation_workers=workers,
                    group_limitations=group_limitations, exact_duplicate_check="raw source SHA256, per modality",
                    near_duplicate_audit_completed=False, gold_human_labels_available=False,
                    fixed_holdout_id=fixed["holdout_id"] if fixed else None,
                    fixed_holdout_directory=str(DIRECTORY) if fixed else None,
                    audit_sampling_population=("fixed random sample holdout with known group exclusions" if fixed and args.scope!="smoke" else "group-balanced smoke audit logic; not formal holdout"),
                    split=split, support=support)
    manifest["release_id"] = canonical_hash(manifest)
    atomic_json(out / "manifest.json", manifest)
    if args.scope == "smoke":
        atomic_json(exposure_path, dict(sample_ids=sorted(set(exposure) | {r["sample_id"] for r in rows}),
                                       reason="Engineering data touched by smoke implementation/tests; exclude these groups from future gold sampling."))
    print(json.dumps(dict(output=str(out), release_id=manifest["release_id"], scope=args.scope,
                          samples=len(rows), roles=split["role_counts"], limitations=group_limitations), ensure_ascii=False))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", default=str(RUN)); p.add_argument("--output", required=True)
    p.add_argument("--scope", choices=("engineering","smoke"), default="engineering")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--groups"); p.add_argument("--allow-unverified-groups", action="store_true")
    p.add_argument("--max-samples", type=int, default=96); p.add_argument("--audit-size", type=int, default=300)
    p.add_argument("--diagnostic-size", type=int, default=200); p.add_argument("--val-fraction", type=float, default=.1)
    args = p.parse_args()
    if args.audit_size < 1 or args.diagnostic_size < 0: p.error("Invalid reserved set size")
    build(args)
if __name__ == "__main__": main()

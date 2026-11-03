"""Draw 300 samples once, without looking at Cue/emotion/description labels."""
from __future__ import annotations
import csv,fcntl,json,random
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from .common import PROJECT,atomic_json,canonical_hash,sha256
from .holdout import DIRECTORY,load_fixed_holdout
from .eligibility import annotation_eligibility,assert_eligible_members

RUN=PROJECT/"cue_annotation/runs/mercaptionplus"

def create():
    DIRECTORY.parent.mkdir(parents=True,exist_ok=True)
    with (DIRECTORY.parent/"holdout300.lock").open("w") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        existing=load_fixed_holdout()
        if existing:
            print(json.dumps(dict(status="already_frozen",holdout_id=existing["holdout_id"],samples=300,path=str(DIRECTORY)),ensure_ascii=False))
            return
        samples=json.loads((RUN/"samples.json").read_text())
        index={r["sample_id"]:r for r in samples}
        eligibility=annotation_eligibility(RUN,samples)
        exposure_path=PROJECT/"cue_student/artifacts/development_exposure.json"
        exposure=json.loads(exposure_path.read_text()).get("sample_ids",[]) if exposure_path.exists() else []
        if len(index)!=len(samples) or not set(exposure)<=set(index): raise ValueError("Source/development membership mismatch")
        cache={}
        def fingerprint(sid):
            if sid in cache: return cache[sid]
            row=index[sid];record={}
            for m,key in (("audio","audio_path"),("visual","video_path")):
                source=Path(row[key]);digest=sha256(source)
                meta_path=RUN/"inputs"/(sid+"."+m+".json")
                if meta_path.exists():
                    expected=json.loads(meta_path.read_text()).get("source_sha256")
                    if expected and digest!=expected: raise ValueError("Original input changed: "+str(source))
                record[m+"_sha256"]=digest
            cache[sid]=record
            return record
        dev_hashes={"audio":set(),"visual":set()}
        for sid in sorted(exposure):
            r=fingerprint(sid)
            for m in dev_hashes: dev_hashes[m].add(r[m+"_sha256"])
        candidates=sorted(set(eligibility["eligible_sample_ids"])-set(exposure))
        rng=random.Random(42);rng.shuffle(candidates)
        selected=[];rejected=[]
        for sid in candidates:
            r=fingerprint(sid)
            if any(r[m+"_sha256"] in dev_hashes[m] for m in dev_hashes):
                rejected.append(sid);continue
            selected.append(sid)
            if len(selected)==300:break
        if len(selected)!=300: raise ValueError("Not enough development-independent candidates")
        if DIRECTORY.exists(): raise FileExistsError("Refusing to replace holdout directory")
        DIRECTORY.mkdir()
        members=[dict(index[sid],**cache[sid]) for sid in selected]
        atomic_json(DIRECTORY/"members.json",members)
        (DIRECTORY/"sample_ids.txt").write_text("\n".join(selected)+"\n")
        with (DIRECTORY/"sample_ids.csv").open("w") as stream:
            writer=csv.DictWriter(stream,fieldnames=["sample_id","role"]);writer.writeheader()
            writer.writerows(dict(sample_id=sid,role="heldout_audit_300") for sid in selected)
        manifest=dict(format_version=1,created_at_beijing=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            seed=42,sample_ids=selected,sample_eligibility=eligibility["policy"],excluded_failed_sample_ids=eligibility["excluded_sample_ids"],source_task_states_sha256=eligibility["source_task_states_sha256"],source_samples_sha256=sha256(RUN/"samples.json"),source_samples=len(samples),
            explicit_development_exclusions=sorted(exposure),development_exposure_sha256=sha256(exposure_path) if exposure_path.exists() else None,
            candidates_before_media_screen=len(candidates),rejected_development_media_duplicates=rejected,
            sampling="Uniform seeded permutation of sorted non-development sample IDs; take first 300 not sharing raw audio/video SHA256 with development samples. No Cue/emotion/description labels consulted.",
            intended_role="Held out from all Student training, validation, early stopping and model selection; manual labels not yet created.",
            annotation_labels_modified=False,human_gold_labels_available=False,
            group_limitations="Original-video provenance and near duplicates remain unverified. Data preparation must exclude known source/duplicate groups and reject any later discovered development-group conflict.",
            media_fingerprints={sid:cache[sid] for sid in selected},
            files={name:sha256(DIRECTORY/name) for name in ("members.json","sample_ids.txt","sample_ids.csv")})
        manifest["holdout_id"]=canonical_hash(manifest)
        atomic_json(DIRECTORY/"manifest.json",manifest)
        loaded=load_fixed_holdout()
        assert loaded["holdout_id"]==manifest["holdout_id"]
        print(json.dumps(dict(status="frozen",holdout_id=manifest["holdout_id"],source_samples=len(samples),
            excluded_development=len(exposure),selected=len(selected),rejected_exact_media_duplicates=len(rejected),
            path=str(DIRECTORY)),ensure_ascii=False),flush=True)

if __name__=="__main__":create()

"""Whole-sample exclusion if any one of the three annotation tasks failed."""
from pathlib import Path
import sqlite3
from .common import MODALITIES,canonical_hash,sha256

POLICY="all_modalities_succeeded_v1"

def annotation_eligibility(run,samples):
    run=Path(run);ids=[r["sample_id"] for r in samples]
    if len(ids)!=len(set(ids)):raise ValueError("Duplicate source sample ID")
    db=sqlite3.connect("file:"+str(run/"tasks.sqlite3")+"?mode=ro",uri=True)
    try:rows=sorted(db.execute("select sid,modality,state from tasks").fetchall())
    finally:db.close()
    expected={(sid,m) for sid in ids for m in MODALITIES}
    if len(rows)!=len(expected) or {(sid,m) for sid,m,state in rows}!=expected:
        raise ValueError("Annotation task keys incomplete/duplicated/unexpected")
    if any(state not in ("succeeded","failed") for sid,m,state in rows):
        raise ValueError("Annotation queue is not settled")
    failed=[dict(sample_id=sid,modality=m) for sid,m,state in rows if state=="failed"]
    excluded=sorted({r["sample_id"] for r in failed})
    return dict(policy=POLICY,source_samples_sha256=sha256(run/"samples.json"),
                source_task_states_sha256=canonical_hash(rows),source_samples=len(ids),
                failed_tasks=len(failed),excluded_sample_ids=excluded,failed_tasks_detail=failed,
                eligible_sample_ids=sorted(set(ids)-set(excluded)))

def assert_eligible_members(sample_ids,eligibility):
    if eligibility.get("policy")!=POLICY:raise ValueError("Whole-sample annotation eligibility policy missing")
    allowed=set(eligibility["eligible_sample_ids"]);excluded=set(eligibility["excluded_sample_ids"])
    if allowed&excluded:raise ValueError("Eligibility sets overlap")
    bad=set(sample_ids)-allowed
    if bad or set(sample_ids)&excluded:raise ValueError("Failed/ineligible annotation sample included: "+str(sorted(bad)[:5]))

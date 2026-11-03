from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import sys,json,random,csv,collections,os
import numpy as np
ROOT=Path(__file__).resolve().parent;PROJECT=Path("/ai/sjq/AffectGPT-sjq");sys.path.insert(0,str(ROOT/"source"))
from cue_student.common import atomic_json,sha256,canonical_hash
from cue_student.eligibility import annotation_eligibility,assert_eligible_members
from cue_student.prepare import assign_roles
from cue_student.holdout import load_fixed_holdout,assert_holdout_separation
from cue_student.data import Release
RUN=PROJECT/"cue_annotation/runs/mercaptionplus";OLD=PROJECT/"cue_student/artifacts/release_full_20261020_145012"
all_samples=json.loads((RUN/"samples.json").read_text());elig=annotation_eligibility(RUN,all_samples)
assert elig["failed_tasks"]==78 and len(elig["excluded_sample_ids"])==72
atomic_json(ROOT/"eligibility.json",elig);eligible=set(elig["eligible_sample_ids"]);failed=set(elig["excluded_sample_ids"])
old_manifest=json.loads((OLD/"manifest.json").read_text())
assert canonical_hash({k:v for k,v in old_manifest.items() if k!="release_id"})==old_manifest["release_id"]
for name,h in old_manifest["files"].items():assert sha256(OLD/name)==h
for name,h in old_manifest["source_artifacts"].items():assert sha256(RUN/name)==h
rows=json.loads((OLD/"members.json").read_text());index={r["sample_id"]:r for r in rows}
exposure=json.loads((PROJECT/"cue_student/artifacts/development_exposure.json").read_text())["sample_ids"]
previous=json.loads((ROOT/"original_holdout_manifest.json").read_text());oldids=previous["sample_ids"]
removed=[sid for sid in oldids if sid not in eligible];retained=[sid for sid in oldids if sid in eligible]
assert len(removed)==1
touched_groups={r["group_id"] for r in rows if r["role"] in ("pseudo_train","pseudo_validation") or r["sample_id"] in exposure}
touched_hashes={m:{r["media_assets"][m]["sha256"] for r in rows if r["group_id"] in touched_groups} for m in ("audio","visual")}
held_hashes={m:{previous["media_fingerprints"][sid][m+"_sha256"] for sid in retained} for m in ("audio","visual")}
candidates=sorted(r["sample_id"] for r in rows if r["role"]=="diagnostic_reserved" and r["sample_id"] in eligible and r["sample_id"] not in exposure and r["group_id"] not in touched_groups and
                  all(r["media_assets"][m]["sha256"] not in touched_hashes[m]|held_hashes[m] for m in ("audio","visual")))
shuffled=candidates.copy();random.Random(42).shuffle(shuffled);replacement=shuffled[:len(removed)]
assert len(replacement)==len(removed);it=iter(replacement);selected=[next(it) if sid in removed else sid for sid in oldids]
assert len(set(selected))==300;assert_eligible_members(selected,elig)
hold=ROOT/"source/cue_student/splits/holdout300";hold.mkdir()
source_index={r["sample_id"]:r for r in all_samples}
fingerprints={sid:{m+"_sha256":index[sid]["media_assets"][m]["sha256"] for m in ("audio","visual")} for sid in selected}
atomic_json(hold/"members.json",[dict(source_index[sid],**fingerprints[sid]) for sid in selected])
(hold/"sample_ids.txt").write_text("\n".join(selected)+"\n")
with (hold/"sample_ids.csv").open("w") as f:
 w=csv.DictWriter(f,fieldnames=["sample_id","role"]);w.writeheader();w.writerows(dict(sample_id=sid,role="heldout_audit_300") for sid in selected)
manifest=dict(format_version=2,created_at_beijing=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),seed=42,sample_ids=selected,
 source_samples_sha256=sha256(RUN/"samples.json"),source_samples=len(all_samples),sample_eligibility=elig["policy"],
 excluded_failed_sample_ids=elig["excluded_sample_ids"],source_task_states_sha256=elig["source_task_states_sha256"],
 previous_holdout_id=previous["holdout_id"],previous_sample_ids=oldids,removed_failed_sample_ids=removed,
 retained_sample_ids=retained,replacement_seed=42,replacement_candidate_ids=candidates,replacement_sample_ids=replacement,
 explicit_development_exclusions=exposure,development_exposure_sha256=sha256(PROJECT/"cue_student/artifacts/development_exposure.json"),
 candidates_before_media_screen=len(candidates),rejected_development_media_duplicates=[],
 sampling="Keep the 299 eligible previous members. Replace failed member by seeded permutation of all-modality-success old diagnostic-reserved IDs, excluding previous train/validation/development groups and exact media overlaps. No cue/emotion labels consulted.",
 intended_role="Independent manual holdout; excluded from all five Student training/validation/model selection.",
 annotation_labels_modified=False,human_gold_labels_available=False,media_fingerprints=fingerprints,
 group_limitations=previous["group_limitations"],files={n:sha256(hold/n) for n in ("members.json","sample_ids.txt","sample_ids.csv")})
manifest["holdout_id"]=canonical_hash(manifest);atomic_json(hold/"manifest.json",manifest)
assert load_fixed_holdout()["holdout_id"]==manifest["holdout_id"]
keep=np.array([r["sample_id"] in eligible for r in rows],dtype=bool)
filtered=[dict(r) for r,k in zip(rows,keep) if k]
with np.load(OLD/"labels.npz",allow_pickle=False) as z:y=z["targets"][keep];mask=z["mask"][keep].astype(bool);states=z["states"][keep]
# Validate immutable-media metadata for every retained member; raw SHA256 was frozen by the original verified preparation.
for i,r in enumerate(filtered):
 for m in ("audio","visual"):
  asset=r["media_assets"][m];st=Path(asset["path"]).stat()
  assert st.st_size==asset["bytes"] and st.st_mtime_ns==asset["mtime_ns"],asset["path"]
 if (i+1)%5000==0:print("VERIFIED_METADATA",i+1,flush=True)
split=assign_roles(filtered,y,mask,300,200,.1,exposure=exposure,fixed_audit_ids=selected)
assert_holdout_separation(filtered,manifest)
assert_eligible_members([r["sample_id"] for r in filtered],elig)
support={}
for role in sorted({r["role"] for r in filtered}):
 sel=np.array([r["role"]==role for r in filtered])
 support[role]=dict(positive=((y[sel]==1)&mask[sel]).sum(0).tolist(),negative=((y[sel]==0)&mask[sel]).sum(0).tolist(),masked=(~mask[sel]).sum(0).tolist())
out=PROJECT/"cue_student/artifacts"/("release_"+ROOT.name);out.mkdir()
np.savez_compressed(out/"labels.npz",targets=y,mask=mask,states=states)
atomic_json(out/"members.json",filtered);atomic_json(out/"ontology.json",json.loads((OLD/"ontology.json").read_text()));atomic_json(out/"eligibility.json",elig)
new=dict(old_manifest);new.pop("release_id")
new.update(n_samples=len(filtered),full_source_n_samples=len(all_samples),sample_eligibility=elig["policy"],excluded_samples=len(failed),
 verified_annotation_records=len(filtered)*3,verified_original_media=len(filtered)*2,preparation_workers=8,
 derived_from_release_id=old_manifest["release_id"],derivation="Verified source annotation hashes, parent package hashes, and retained media byte/mtime identities; whole-sample eligibility filter; regrouped roles with replacement holdout.",
 files={n:sha256(out/n) for n in ("members.json","labels.npz","ontology.json","eligibility.json")},fixed_holdout_id=manifest["holdout_id"],
 fixed_holdout_directory=str(PROJECT/"cue_student/splits/holdout300"),audit_sampling_population=manifest["sampling"],split=split,support=support)
new["release_id"]=canonical_hash(new);atomic_json(out/"manifest.json",new)
(ROOT/"source/cue_student/artifacts"/out.name).symlink_to(out,target_is_directory=True)
# A fresh small test package drawn only from eligible non-holdout members, with original frozen geometry.
pool=[i for i,r in enumerate(filtered) if r["role"] in ("pseudo_train","pseudo_validation")]
rng=random.Random(42);chosen=sorted(rng.sample(pool,96));smrows=[dict(filtered[i]) for i in chosen]
for k,r in enumerate(smrows):r["role"]="pseudo_train" if k<80 else "pseudo_validation"
sm=ROOT/"source/cue_student/artifacts/smoke_release_v1";sm.mkdir()
np.savez_compressed(sm/"labels.npz",targets=y[chosen],mask=mask[chosen],states=states[chosen])
for name,value in (("members.json",smrows),("ontology.json",json.loads((out/"ontology.json").read_text())),("eligibility.json",elig)):atomic_json(sm/name,value)
smm=dict(new);smm.pop("release_id");smm.update(scope="smoke",n_samples=96,verified_annotation_records=288,verified_original_media=192,
 files={n:sha256(sm/n) for n in ("members.json","labels.npz","ontology.json","eligibility.json")},
 split=dict(role_counts=dict(collections.Counter(r["role"] for r in smrows))))
smm["release_id"]=canonical_hash(smm);atomic_json(sm/"manifest.json",smm)
full=Release(out);small=Release(sm)
summary=dict(release=str(out),release_id=new["release_id"],eligible_samples=len(filtered),excluded_sample_ids=sorted(failed),failed_tasks=78,
 fixed_holdout_id=manifest["holdout_id"],holdout_removed=removed,holdout_replacements=replacement,retained_holdout=299,
 role_counts=split["role_counts"],all_excluded_intersections={role:sorted(failed&{r["sample_id"] for r in filtered if r["role"]==role}) for role in split["role_counts"]},
 holdout_failed_intersection=sorted(failed&set(selected)),smoke_release=str(sm))
atomic_json(ROOT/"data_audit.json",summary)
print(json.dumps(summary,ensure_ascii=False),flush=True)

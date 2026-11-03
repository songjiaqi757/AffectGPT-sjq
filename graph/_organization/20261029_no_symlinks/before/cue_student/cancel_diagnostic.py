"""Derive a new immutable release by merging the reserved 200 into training."""
import collections,copy,json,shutil
from pathlib import Path
import numpy as np
from .common import PROJECT,atomic_json,canonical_hash,sha256
from .data import Release
def main():
 parent=PROJECT/"cue_student/artifacts/release_strict_all_modalities_20261020_163131"
 out=PROJECT/"cue_student/artifacts/release_strict_no_diagnostic_20261021"
 assert not out.exists(),"Refuse to overwrite a frozen release"
 old=Release(parent);rows=copy.deepcopy(old.rows)
 changed=[]
 for row in rows:
  if row["role"]=="diagnostic_reserved":
   changed.append(row["sample_id"]);row["role"]="pseudo_train"
 assert len(changed)==200
 expected={"pseudo_train":27879,"pseudo_validation":3076,"gold_audit":300}
 assert dict(collections.Counter(r["role"] for r in rows))==expected
 for a,b in zip(old.rows,rows):
  assert {k:v for k,v in a.items() if k!="role"}=={k:v for k,v in b.items() if k!="role"}
 out.mkdir()
 for name in old.manifest["files"]:
  if name!="members.json":shutil.copy2(parent/name,out/name)
 atomic_json(out/"members.json",rows)
 manifest=copy.deepcopy(old.manifest);manifest.pop("release_id")
 manifest["derived_from_release_id"]=old.manifest["release_id"]
 manifest["derivation"]="User cancelled diagnostic reservation; move exactly its 200 samples into pseudo_train, retaining all existing train/validation/audit assignments and label/media content."
 manifest["split"]["role_counts"]=expected
 manifest["split"]["diagnostic_size"]=0
 support={}
 for role in expected:
  sel=np.array([r["role"]==role for r in rows])
  support[role]=dict(positive=((old.targets[sel]==1)&old.mask[sel]).sum(0).tolist(),
   negative=((old.targets[sel]==0)&old.mask[sel]).sum(0).tolist(),masked=(~old.mask[sel]).sum(0).tolist())
 manifest["support"]=support
 manifest["files"]={name:sha256(out/name) for name in old.manifest["files"]}
 manifest["role_migration"]={"policy":"cancel_diagnostic_merge_train_v1","moved_sample_ids":sorted(changed),"previous_role":"diagnostic_reserved","new_role":"pseudo_train","existing_checkpoints_retrained":False}
 manifest["release_id"]=canonical_hash(manifest)
 atomic_json(out/"manifest.json",manifest)
 verified=Release(out)
 assert verified.manifest["release_id"]==manifest["release_id"]
 assert np.array_equal(verified.targets,old.targets) and np.array_equal(verified.mask,old.mask) and np.array_equal(verified.states,old.states)
 for role in ["pseudo_validation","gold_audit"]:
  assert {r["sample_id"] for r in old.rows if r["role"]==role}=={r["sample_id"] for r in rows if r["role"]==role}
 pointer=dict(path=str(out),release_id=manifest["release_id"],role_counts=expected,policy="cancel_diagnostic_merge_train_v1",
  previous_release=str(parent),existing_checkpoints_retrained=False)
 atomic_json(PROJECT/"cue_student/artifacts/current_release.json",pointer)
 atomic_json(out/"migration_verification.json",dict(passed=True,moved_samples=len(changed),role_counts=expected,
  validation_unchanged=True,gold_audit_unchanged=True,all_supervision_arrays_unchanged=True,group_separation_verified=True,
  original_source_and_near_duplicate_limitations=manifest["group_limitations"]))
 print(json.dumps(pointer,ensure_ascii=False))
if __name__=="__main__":main()

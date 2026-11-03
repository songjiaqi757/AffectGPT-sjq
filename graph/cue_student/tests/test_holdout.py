import copy,json,random,shutil,tempfile,unittest
from graph_paths import Path
import numpy as np
import torch
from cue_student.common import PROJECT,atomic_json,canonical_hash,sha256
from cue_student.holdout import load_fixed_holdout,assert_holdout_separation,DIRECTORY
from cue_student.data import Release,CueDataset
from cue_student.prepare import assign_roles
from cue_student.models import TemporalHead

class FixedHoldoutTests(unittest.TestCase):
    def setUp(self):
        self.manifest=load_fixed_holdout()
    def test_300_unique_and_development_disjoint(self):
        ids=set(self.manifest["sample_ids"])
        exposure=json.loads((PROJECT/"cue_student/artifacts/development_exposure.json").read_text())["sample_ids"]
        self.assertEqual(len(ids),300);self.assertFalse(ids&set(exposure))
    def test_label_blind_seeded_selection_reproduces(self):
        samples=json.loads((PROJECT/"cue_annotation/runs/mercaptionplus/samples.json").read_text())
        if "replacement_candidate_ids" in self.manifest:
            candidates=self.manifest["replacement_candidate_ids"].copy()
            random.Random(self.manifest["replacement_seed"]).shuffle(candidates)
            removed=set(self.manifest["removed_failed_sample_ids"])
            replacements=iter(candidates[:len(removed)])
            expected=[next(replacements) if sid in removed else sid for sid in self.manifest["previous_sample_ids"]]
            self.assertEqual(expected,self.manifest["sample_ids"])
            return
        candidates=sorted({r["sample_id"] for r in samples}-set(self.manifest["explicit_development_exclusions"])-set(self.manifest.get("excluded_failed_sample_ids",[])))
        random.Random(42).shuffle(candidates)
        rejected=set(self.manifest["rejected_development_media_duplicates"])
        self.assertEqual([s for s in candidates if s not in rejected][:300],self.manifest["sample_ids"])
    def test_direct_ids_blocked_in_train_and_validation(self):
        sid=self.manifest["sample_ids"][0]
        for role in ("pseudo_train","pseudo_validation"):
            with self.assertRaisesRegex(ValueError,"Fixed holdout leak"):
                assert_holdout_separation([dict(sample_id=sid,group_id="g",role=role)],self.manifest)
    def test_known_same_group_is_excluded(self):
        sid=self.manifest["sample_ids"][0]
        rows=[dict(sample_id=sid,group_id="g",role="gold_audit"),dict(sample_id="other",group_id="g",role="pseudo_train")]
        with self.assertRaisesRegex(ValueError,"Fixed holdout leak"):assert_holdout_separation(rows,self.manifest)
    def test_renamed_duplicate_media_blocked(self):
        fp=next(iter(self.manifest["media_fingerprints"].values()))
        rows=[dict(sample_id="renamed",group_id="other",role="pseudo_validation",media_assets={"visual":{"sha256":fp["visual_sha256"]}})]
        with self.assertRaisesRegex(ValueError,"Fixed holdout leak"):assert_holdout_separation(rows,self.manifest)
    def test_fixed_roles_preserve_ids_and_exclude_siblings(self):
        rows=[dict(sample_id=str(i),group_id=str(i//2)) for i in range(40)]
        y=np.tile([[1.,0.],[0.,1.]],(20,1));mask=np.ones_like(y,bool)
        fixed=["0","2","4","6"]
        result=assign_roles(rows,y,mask,4,4,.25,fixed_audit_ids=fixed)
        self.assertEqual(result["audit_sample_ids"],fixed)
        self.assertEqual([rows[int(s)+1]["role"] for s in fixed],["audit_group_excluded"]*4)
    def test_exposed_fixed_group_fails_without_redrawing(self):
        rows=[dict(sample_id=str(i),group_id=str(i//2)) for i in range(40)]
        y=np.ones((40,2));mask=np.ones_like(y,bool)
        with self.assertRaisesRegex(ValueError,"conflicts"):
            assign_roles(rows,y,mask,4,4,.25,exposure=["1"],fixed_audit_ids=["0","2","4","6"])
    def test_old_smoke_package_remains_separate(self):
        release=Release(PROJECT/"cue_student/artifacts/smoke_release_v1")
        self.assertEqual(release.fixed_holdout_id,self.manifest["holdout_id"])
        self.assertFalse({r["sample_id"] for r in release.rows}&set(self.manifest["sample_ids"]))
        with self.assertRaisesRegex(ValueError,"Only pseudo_train"):CueDataset(release,"text","gold_audit",training=True)
    def test_release_membership_guard_after_valid_file_hashes(self):
        with tempfile.TemporaryDirectory(dir=PROJECT/"cue_student/artifacts") as tmp:
            dest=Path(tmp)/"bad";shutil.copytree(PROJECT/"cue_student/artifacts/smoke_release_v1",dest)
            rows=json.loads((dest/"members.json").read_text())
            next(r for r in rows if r["role"]=="pseudo_train")["sample_id"]=self.manifest["sample_ids"][0]
            atomic_json(dest/"members.json",rows)
            m=json.loads((dest/"manifest.json").read_text());m["files"]["members.json"]=sha256(dest/"members.json")
            m["release_id"]=canonical_hash({k:v for k,v in m.items() if k!="release_id"});atomic_json(dest/"manifest.json",m)
            with self.assertRaisesRegex(ValueError,"Fixed holdout leak"):Release(dest)
    def test_holdout_manifest_tamper_detected(self):
        with tempfile.TemporaryDirectory(dir=PROJECT/"cue_student/artifacts") as tmp:
            dest=Path(tmp)/"roster";shutil.copytree(DIRECTORY,dest)
            m=json.loads((dest/"manifest.json").read_text());m["seed"]=99;atomic_json(dest/"manifest.json",m)
            with self.assertRaisesRegex(ValueError,"manifest changed"):load_fixed_holdout(dest)
    def test_baseline_pooling_does_not_encode_order(self):
        torch.manual_seed(42);features=torch.randn(2,7,4);mask=torch.ones(2,7,dtype=torch.bool)
        order=torch.tensor([6,2,0,4,1,5,3])
        for kind in ("mean","attention","topk"):
            head=TemporalHead(4,3,kind,0).eval()
            torch.testing.assert_close(head(features,mask),head(features[:,order],mask[:,order]),atol=1e-6,rtol=1e-5)

if __name__=="__main__":unittest.main()

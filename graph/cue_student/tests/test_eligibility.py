import json,sqlite3,tempfile,unittest,shutil
from graph_paths import Path
import numpy as np
from cue_student.common import PROJECT,atomic_json,canonical_hash,sha256
from cue_student.eligibility import POLICY,annotation_eligibility,assert_eligible_members
from cue_student.data import Release
from cue_student.holdout import load_fixed_holdout

class StrictEligibilityTests(unittest.TestCase):
    def fixture(self,path,states):
        ids=sorted({sid for sid,m,state in states})
        samples=[dict(sample_id=sid) for sid in ids]
        atomic_json(path/"samples.json",samples)
        db=sqlite3.connect(path/"tasks.sqlite3")
        db.execute("create table tasks (sid text,modality text,state text)")
        db.executemany("insert into tasks values (?,?,?)",states);db.commit();db.close()
        return samples
    def test_any_single_modality_failure_excludes_whole_sample(self):
        states=[(sid,m,"failed" if sid==m else "succeeded") for sid in ("good","text","audio","visual") for m in ("text","audio","visual")]
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);samples=self.fixture(path,states);e=annotation_eligibility(path,samples)
            self.assertEqual(e["eligible_sample_ids"],["good"]);self.assertEqual(e["excluded_sample_ids"],["audio","text","visual"])
            self.assertEqual(e["failed_tasks"],3)
            for sid in ("text","audio","visual"):
                with self.assertRaisesRegex(ValueError,"ineligible"):assert_eligible_members(["good",sid],e)
    def test_multiple_failed_tasks_deduplicated(self):
        rows=[("a",m,"failed") for m in ("text","audio","visual")]
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);e=annotation_eligibility(path,self.fixture(path,rows))
            self.assertEqual(e["failed_tasks"],3);self.assertEqual(e["excluded_sample_ids"],["a"])
    def test_incomplete_duplicate_or_unsettled_tasks_rejected(self):
        good=[("s",m,"succeeded") for m in ("text","audio","visual")]
        for rows in (good[:-1],good+[good[0]],[good[0],good[1],("s","visual","running")]):
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp);samples=self.fixture(path,rows)
                with self.assertRaises(ValueError):annotation_eligibility(path,samples)
    def test_release_and_holdout_exclude_all_failed_samples(self):
        release=Release(PROJECT/"cue_student/artifacts/smoke_release_v1")
        failed=set(release.eligibility["excluded_sample_ids"])
        self.assertEqual(len(failed),72);self.assertEqual(release.eligibility["failed_tasks"],78)
        self.assertFalse(failed&{r["sample_id"] for r in release.rows})
        self.assertFalse(failed&set(load_fixed_holdout()["sample_ids"]))
    def test_loader_rejects_failed_member_after_valid_file_hashes(self):
        with tempfile.TemporaryDirectory(dir=PROJECT/"cue_student/artifacts") as tmp:
            dest=Path(tmp)/"bad";shutil.copytree(PROJECT/"cue_student/artifacts/smoke_release_v1",dest)
            e=json.loads((dest/"eligibility.json").read_text());rows=json.loads((dest/"members.json").read_text())
            rows[0]["sample_id"]=e["excluded_sample_ids"][0];atomic_json(dest/"members.json",rows)
            m=json.loads((dest/"manifest.json").read_text());m["files"]["members.json"]=sha256(dest/"members.json")
            m["release_id"]=canonical_hash({k:v for k,v in m.items() if k!="release_id"});atomic_json(dest/"manifest.json",m)
            with self.assertRaisesRegex(ValueError,"ineligible"):Release(dest)
    def test_legacy_policy_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"policy"):assert_eligible_members([],dict(policy="old",eligible_sample_ids=[],excluded_sample_ids=[]))
if __name__=="__main__":unittest.main()

"""Checks for real-directory relocation and precise frozen-record compatibility."""
import hashlib,json,os,unittest
from pathlib import Path as NativePath
from graph_paths import Path,resolve_path,hash_matches,sha256_file,GRAPH_ROOT,PROJECT_ROOT,AUDIT
class ActualDirectoryTests(unittest.TestCase):
    def test_real_directories_and_removed_aliases(self):
        moves=json.loads((GRAPH_ROOT/'_organization/20261029/plan.json').read_text())['moves']
        for old,new in moves.items():
            self.assertFalse(NativePath(old).exists(),old)
            self.assertFalse(NativePath(old).is_symlink(),old)
            self.assertTrue(NativePath(new).exists(),new)
            self.assertFalse(NativePath(new).is_symlink(),new)
            self.assertEqual(resolve_path(old),new)
            self.assertEqual(str(Path(old)),new)
    def test_original_dependencies_use_actual_project_directories(self):
        for name in ['AffectGPT','dataset']:
            self.assertFalse((GRAPH_ROOT/name).exists())
            self.assertFalse((GRAPH_ROOT/name).is_symlink())
            self.assertEqual(Path(GRAPH_ROOT)/name,PROJECT_ROOT/name)
            self.assertTrue((PROJECT_ROOT/name).is_dir())
    def test_sha_is_truthful_and_only_exact_migrations_are_accepted(self):
        data=json.loads((AUDIT/'source_migration.json').read_text())
        rel='amg_runtime/common.py'
        record=data['files'][rel];path=GRAPH_ROOT/rel
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(sha256_file(path),actual)
        self.assertEqual(actual,record['after_sha256'])
        self.assertNotEqual(actual,record['before_sha256'])
        self.assertTrue(hash_matches(path,record['before_sha256'],actual))
        self.assertFalse(hash_matches(path,'0'*64,actual))
        self.assertFalse(hash_matches(path,record['before_sha256'],'0'*64))
        self.assertFalse(hash_matches(GRAPH_ROOT/'run.py',record['before_sha256'],actual))
    def test_frozen_experiment_records_remain_byte_identical(self):
        data=json.loads((AUDIT/'source_migration.json').read_text())
        for rel,want in data['frozen_sha256'].items():
            self.assertEqual(hashlib.sha256((GRAPH_ROOT/rel).read_bytes()).hexdigest(),want,rel)
    def test_runtime_root_and_saved_plan_paths(self):
        from amg_runtime.common import ROOT
        self.assertEqual(str(ROOT),str(GRAPH_ROOT))
        from amg_method_decision.generate import verify
        run=GRAPH_ROOT/'amg_method_decision/runs/decision_20261028_200538'
        plan=verify(Path(run))
        for old in plan['input_files']:
            self.assertTrue(NativePath(resolve_path(old)).is_file())
if __name__=='__main__':unittest.main()

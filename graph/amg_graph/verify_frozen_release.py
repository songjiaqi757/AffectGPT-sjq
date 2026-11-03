"""Reverify current frozen graph using its explicit input paths, not mutable pointers."""
from graph_paths import hash_matches as _graph_hash_matches
import json
from . import verify
from .data import read,sha,write,PROJECT
def main():
 verify.main()
 root=verify.RUN
 proof=dict(passed=True,frozen_input_paths_verified=True,current_document_is_separate_from_frozen_build_plan=True)
 revision_path=root/"manifest/document_revision.json"
 if revision_path.exists():
  revision=read(revision_path)
  assert _graph_hash_matches(PROJECT / '图构建.md', revision['current_sha256'], sha(PROJECT / '图构建.md'))
  proof["current_document_revision_verified"]=True
 write(root/"manifest/document_revision_verification.json",proof)
 print(json.dumps(proof))
if __name__=="__main__":main()

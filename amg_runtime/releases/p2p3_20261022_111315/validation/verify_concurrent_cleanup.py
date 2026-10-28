from pathlib import Path
import difflib,json,sys
ROOT=Path("/ai/sjq/AffectGPT-sjq");sys.path.insert(0,str(ROOT))
from amg_runtime.common import read,sha,atomic_json,require
from amg_graph.data import load
directory=Path(sys.argv[1]);inputs=read(directory/"inputs_p0.json");root=Path(inputs["graph"]["path"]);protocol=read(root/"manifest/protocol.json")
p0=read(ROOT/"amg_graph/preflight/current.json");lock=read(p0["version_lock"])
cleanup=ROOT/"data_migrations/appraisal_media_cleanup_20261022";report=read(cleanup/"final_verification.json")
snapshot=cleanup/"图构建_v2_8_before_media_cleanup.md"
before=snapshot.read_bytes();after=(ROOT/"图构建.md").read_bytes()
require(sha(snapshot)==lock["input_fingerprints"][str(ROOT/"图构建.md")],"Cleanup snapshot differs from P0 plan")
prefix=0
while prefix<min(len(before),len(after)) and before[prefix]==after[prefix]:prefix+=1
suffix=0
while suffix<len(before)-prefix and suffix<len(after)-prefix and before[-suffix-1]==after[-suffix-1]:suffix+=1
reconstructed=after[:prefix]+(after[len(after)-suffix:] if suffix else b"")
require(reconstructed==before,"Existing method bytes were modified")
inserts=[after[prefix:len(after)-suffix if suffix else len(after)].decode("utf-8")]
require(bool(inserts[0]),"Expected documented storage note insertion")
revision=read(root/"manifest/document_revision.json")
require(revision["current_sha256"]==sha(ROOT/"图构建.md"),"Current document revision SHA mismatch")
require(revision["frozen_input_plan_sha256"]==protocol["input_fingerprints"]["图构建.md"],"Frozen build plan revision mismatch")
require(revision["media_cleanup_revision"]["graph_and_annotation_inputs_unchanged"] and report["passed"],"Cleanup provenance incomplete")
paths=protocol["source_paths"]
print("Original method text preserved; reverifying frozen graph inputs",flush=True)
data=load(release_path=paths["release"],emotion_run=paths["emotion_run"],plan_path=paths["source_plan"],annotation_verification=paths["annotation_verification"])
require(data["source_hashes"]==protocol["input_fingerprints"],"Frozen graph input fingerprints changed")
result=dict(passed=True,classification="Concurrent storage cleanup documentation update only",graph_release_id=protocol["release_id"],all_frozen_graph_input_fingerprints_reverified=True,selected_appraisal_annotation_ordered_digest=data["source_hashes"]["appraisal_selected_annotations_ordered_digest"],current_method_document_sha256=sha(ROOT/"图构建.md"),p0_method_document_sha256=sha(snapshot),existing_method_text_byte_preserved=True,inserted_storage_notes=inserts,changed_graph_metadata_path=str(root/"manifest/document_revision.json"),changed_graph_metadata_sha256=sha(root/"manifest/document_revision.json"),cleanup_audit_path=str(cleanup/"final_verification.json"),cleanup_audit_sha256=sha(cleanup/"final_verification.json"),frozen_source_plan_sha256=sha(Path(paths["source_plan"])),note="No old graph or documentation records were edited by this P2/P3 task. The external cleanup updated one mutable documentation record, outside the graph release identity.")
atomic_json(directory/"validation/concurrent_cleanup_verification.json",result);print(json.dumps(result,ensure_ascii=False))

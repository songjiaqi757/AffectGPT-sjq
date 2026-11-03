"""Fail closed on input, implementation, graph or policy version drift."""
from pathlib import Path
from .common import ROOT,canonical,read,require,sha,p0_context
def load_release(directory):
 directory=Path(directory).resolve()
 manifest=read(directory/"release_manifest.json")
 require(canonical({k:v for k,v in manifest.items() if k!="release_id"})==manifest["release_id"],"Runtime release manifest identity mismatch")
 _,lock,inputs=p0_context()
 require(manifest["p0_lock_id"]==lock["lock_id"],"P0 version lock drift")
 require(manifest["cue_release_id"]==inputs["cue_release"]["release_id"] and manifest["graph_release_id"]==inputs["graph"]["release_id"],"Runtime input release drift")
 for name,expected in manifest["files"].items():require(sha(directory/name)==expected,"Runtime artifact fingerprint mismatch: "+name)
 for name,expected in manifest["source_code_sha256"].items():require(sha(ROOT/name)==expected,"Runtime source fingerprint mismatch: "+name)
 original=read(Path(read(ROOT/"amg_graph/preflight/current.json")["path"])/"source_code_fingerprints.json")
 for name,expected in original["current_sources"].items():
  if name.startswith(("cue_student/","amg_graph/")) and "/preflight/" not in name:
   require(sha(ROOT/name)==expected,"Original P0 implementation drift: "+name)
 protocol_path=Path(inputs["graph"]["path"])/"manifest/protocol.json";protocol=read(protocol_path)
 require(canonical({k:v for k,v in protocol.items() if k!="release_id"})==inputs["graph"]["release_id"],"Frozen graph identity mismatch")
 for relative in ["graph/graph.json","graph/paths_cue_appraisal_emotion.csv"]:
  require(sha(Path(inputs["graph"]["path"])/relative)==protocol["artifacts"][relative],"Frozen graph artifact fingerprint mismatch")
 return manifest

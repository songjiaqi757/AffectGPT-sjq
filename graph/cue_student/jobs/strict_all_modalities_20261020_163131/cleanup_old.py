from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,shutil,os,threading
ROOT=Path(__file__).resolve().parent;PROJECT=Path("/ai/sjq/AffectGPT-sjq");STUDENT=PROJECT/"cue_student"
status=json.loads((ROOT/"status.json").read_text())
assert status["phase"]=="training" and len(status["runs"])==5
assert json.loads((ROOT/"integration_report.json").read_text())["passed"]
assert json.loads((ROOT/"stop_status.json").read_text())["complete"]
for run in status["runs"].values():
 p=Path(run["output"])/"events.jsonl"
 assert p.exists() and any(json.loads(line).get("event")=="train" for line in p.read_text().splitlines())
keep_artifacts={"release_"+ROOT.name,"model_fingerprints","development_exposure.json","smoke_release_v1"}
keep_reports={"strict_all_modalities_20261020.md","strict_all_modalities_20261020.json"}
roots=[]
roots.extend(p for p in (STUDENT/"output").iterdir() if p.name!=ROOT.name)
roots.extend(p for p in (STUDENT/"jobs").iterdir() if p.is_dir() and p!=ROOT)
roots.extend(p for p in (STUDENT/"artifacts").iterdir() if p.name not in keep_artifacts)
roots.extend(p for p in (STUDENT/"reports").iterdir() if p.name not in keep_reports)
roots.extend(p for p in (ROOT/"smoke_outputs",ROOT/"old_members_for_rebuild.json",ROOT/"original_holdout_manifest.json") if p.exists())
targets=[];empty_parents=[]
for p in roots:
 assert p!=ROOT and STUDENT in p.parents and p!=Path(status["release"])
 # Disjoint old modality directories may be removed concurrently.
 if p.is_dir() and not p.is_symlink() and p.parent==STUDENT/"output":
  targets.extend(p.iterdir());empty_parents.append(p)
 else:targets.append(p)
records=[];lock=threading.Lock()
def remove(p):
 print("REMOVING",str(p),flush=True)
 if p.is_symlink() or p.is_file():p.unlink()
 else:shutil.rmtree(p)
 with lock:
  records.append(dict(path=str(p)))
  (ROOT/"cleanup_progress.json").write_text(json.dumps(dict(removed=records),ensure_ascii=False,indent=2)+"\n")
 print("REMOVED",str(p),flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
 futures=[pool.submit(remove,p) for p in targets]
 for future in as_completed(futures):future.result()
for p in empty_parents:p.rmdir();records.append(dict(path=str(p)))
summary=dict(removed=records,removed_roots=[str(p) for p in roots],previously_removed="Original text output had already been removed before parallel cleanup resumed.",
 kept="Current strict release, current five runs, current validation/source/provenance, raw media, original annotations, and pretrained assets.")
(ROOT/"cleanup_report.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print("CLEANUP_COMPLETE",json.dumps(summary,ensure_ascii=False),flush=True)

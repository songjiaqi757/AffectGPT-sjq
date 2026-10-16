"""Create a new locked continuation; preserve the failed run and partial outputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
ROOT=Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
PARENT=ROOT/"amg/experiments/single-seed42-face-ckpt35-bias-validation-v1"
OUT=PARENT/"recovery-v2"
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b""):h.update(block)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
for name in ("protocol.json","READY.json"):
    if (OUT/name).exists():raise FileExistsError(OUT/name)
tests=(OUT/"unit_tests.log").read_text()
if "\nOK\n" not in tests or "FAILED (" in tests:
    raise RuntimeError("Full CPU regression suite has not passed")
old_ready=read(PARENT/"READY.json")
patch=read(OUT/"PATCH.json")
for name,digest in old_ready["locked_files"].items():
    expected=patch["after_sha256"] if name==patch["changed_file"] else digest
    if sha(name)!=expected:raise RuntimeError("Unexpected original input/source change: "+name)
p=read(PARENT/"protocol.json")
p["experiment_directory"]=str(OUT)
p["recovery"]={"parent_directory":str(PARENT),"parent_protocol_sha256":sha(PARENT/"protocol.json"),
 "reason":"off retrieved_ids=None validation bug stopped post-training scoring",
 "no_retraining":True,"original_failure_preserved":str(PARENT/"FAILURE.txt"),
 "shared_init_unchanged":True,"seed_unchanged":True,
 "inference_model_and_prompt_and_scoring_sources_unchanged":True,
 "reused":"both final trained checkpoints; all completed Stage A and Stage B retrieval results; complete zero_init/off",
 "gpu_plan":{"0":["control/off fresh500","control/random500"],"1":["zero_init/random500"]},
 "trained_checkpoints":{}}
for arm in ("control","zero_init"):
    path=PARENT/"training"/arm/"checkpoint_001334.pth"
    meta=read(PARENT/"training"/arm/"inference/retrieval/dev.meta.json")
    assert meta["amg_sha256"]==sha(path)
    p["recovery"]["trained_checkpoints"][arm]={"path":str(path),"sha256":meta["amg_sha256"]}
partial=PARENT/"training/control/inference/off/dev.jsonl"
p["recovery"]["partial_control_off_preserved"]={
 "path":str(partial),"rows":len(partial.read_text().splitlines()),"sha256":sha(partial),
 "used_for_final_score":False}
assert p["recovery"]["partial_control_off_preserved"]["rows"]==495
p["created_at"]=datetime.now(timezone.utc).isoformat()
write(OUT/"protocol.json",p)
note="""# Evaluation recovery v2

Both seed42 training arms are complete. The original pipeline stopped because
its off-mode validator iterated over the intentional retrieved_ids=null trace.
The one-line normalization fix changes validation only; model, training,
inference, decoding, budget and scoring sources remain unchanged.

Reuse both trained checkpoints, all complete normal predictions/reports and the
complete zero_init/off500 output. Preserve the partial control/off495 output as
failure evidence; generate a fresh complete500 in this directory. GPU0 runs
control/off then control/random; GPU1 runs zero_init/random. No training occurs.

Exact initial states and all4002 training exposures are revalidated before GPU
work. Completed predictions and metadata are fingerprinted; partial495 is never
silently scored as a complete run. Final paired scoring and SUMMARY.md contain
the same predeclared11 comparisons and exploratory decision rules.

All files remain on server. Original state.json/FAILURE.txt/READY.json are
preserved. Current progress is recovery-v2/state.json; completed output is
recovery-v2/SUMMARY.md and summary.json. End assistant turn after launch checks.
"""
(OUT/"PROTOCOL.md").write_text(note)
locked={Path(name) for name in old_ready["locked_files"]}
locked.update((ROOT/"amg").glob("*.py"))
locked.update((ROOT/"amg/tests").glob("test_*.py"))
locked.update(PARENT/"reports"/name for name in (
 "ref-normal.json","ref-off.json","ref-random.json","ref-off_trained.json",
 "stage-a-zero-retrieval.json","stage-a-zero-random.json",
 "stage-a-zero-retrieval-vs-ref-normal.json","stage-a-zero-random-vs-ref-random.json",
 "stage-a-zero-retrieval-vs-stage-a-zero-random.json","stage-a-zero-retrieval-vs-ref-off.json",
 "stage-b-control-retrieval.json","stage-b-zero_init-retrieval.json"))
for arm in ("control","zero_init"):
    training=PARENT/"training"/arm
    for name in ("checkpoint_001334.pth","config.json","coverage.json","train.jsonl",
                 "exposure.jsonl","adapter_initialization.json","adapter_initial_state.pth",
                 "first-five-validation.json"):
        locked.add(training/name)
    for mode in ("retrieval","off"):
        for name in ("dev.jsonl","dev.meta.json","dev.retrieval.jsonl"):
            locked.add(training/"inference"/mode/name)
for name in ("state.json","FAILURE.txt","READY.json","matched-initialization.json"):
    locked.add(PARENT/name)
for name in ("PATCH.json","run_bias_validation.before.py","protocol.json","PROTOCOL.md",
             "prepare_recovery.py","unit_tests.log","regression-tests.log","launch_recovery.py"):
    locked.add(OUT/name)
snapshot=OUT/"source_after";snapshot.mkdir()
for path in sorted(locked):
    if path.suffix==".py" and ROOT in path.parents:
        target=snapshot/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
write(OUT/"READY.json",{"schema":"amg-bias-recovery-ready-v1",
 "created_at":datetime.now(timezone.utc).isoformat(),"all_artifacts_server_only":True,
 "locked_files":{str(path):sha(path) for path in sorted(locked)},
 "original_source_changes":[patch]})
print(json.dumps({"locked_files":len(locked),"protocol":str(OUT/"protocol.json"),
                  "no_retraining":True}))

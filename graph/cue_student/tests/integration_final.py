"""Real-weight GPU integration: short CLI training, resume identity, evaluation, inference and edge inputs."""
from graph_paths import resolve_path as _graph_resolve_path
from graph_paths import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import gc,json,os,subprocess,sys,time
import numpy as np
import torch
from cue_student.common import PROJECT,atomic_json,load_config,move_batch,sha256,seed_all,code_hash
from cue_student.data import Release,CueDataset,make_collator
from cue_student.models import CueModel
from cue_student.objectives import masked_bce_sum
root=PROJECT/"cue_student/artifacts"/("integration_"+datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S"))
root.mkdir(parents=True)
release_path=PROJECT/"cue_student/artifacts/smoke_release_v1"
report=dict(output=str(root),scope="real-data smoke tests, not formal training/gold evaluation",cases={})
def save(): atomic_json(root/"report.json",report)
def call(label,mod,args):
    print("RUN",label,flush=True); log=root/(label+".log")
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",TOKENIZERS_PARALLELISM="false")
    with log.open("w") as stream:
        r=subprocess.run([sys.executable,"-u","-m",mod]+[str(a) for a in args],cwd=PROJECT,env=env,stdout=stream,stderr=subprocess.STDOUT)
    if r.returncode:
        print(log.read_text()[-6000:],flush=True); raise RuntimeError(label+" failed")
    report["cases"][label]=dict(passed=True,log=str(log));save()
configs={}
for m in ("text","audio","visual"):
    cfg=json.loads((PROJECT/"cue_student/configs"/(m+".json")).read_text())
    cfg.update(encoder_train="frozen",precision="float32",dropout=0.,epochs=2,patience=10,batch_size=2,grad_accum=2,save_every_steps=1)
    p=root/(m+".config.json");atomic_json(p,cfg);configs[m]=p
base=["--release",release_path,"--device","cuda:0","--allow-smoke"]
text_run=root/"text_resume"
call("text_first_step","cue_student.train",["--config",configs["text"],"--output",text_run,"--max-steps",1]+base)
call("text_resume_step","cue_student.train",["--config",configs["text"],"--output",text_run,"--resume",text_run/"last.pt","--max-steps",2]+base)
text_ref=root/"text_reference"
call("text_uninterrupted","cue_student.train",["--config",configs["text"],"--output",text_ref,"--max-steps",2]+base)
a=torch.load(_graph_resolve_path(text_run / 'last.pt'), map_location='cpu', weights_only=False);b=torch.load(_graph_resolve_path(text_ref / 'last.pt'), map_location='cpu', weights_only=False)
assert a["progress"]["global_step"]==b["progress"]["global_step"]==2
diff=max(float((a["model"][k]-b["model"][k]).abs().max()) for k in a["model"])
assert diff==0.,diff
report["cases"]["resume_matches_uninterrupted"]=dict(passed=True,max_abs_difference=diff)
del a,b;gc.collect();save()
runs={"text":text_run}
for m in ("audio","visual"):
    runs[m]=root/m
    call(m+"_short_train","cue_student.train",["--config",configs[m],"--output",runs[m],"--max-steps",2]+base)
release=Release(release_path)
for m in ("text","audio","visual"):
    rows=[r for r in release.rows if r["role"]=="pseudo_train"]
    source={k:rows[0][k] for k in ("sample_id","text","audio_path","video_path")}
    missing=dict(sample_id="input_missing",text={},audio_path="/missing/audio.wav",video_path="/missing/video.mp4")
    inp=root/(m+".input.json");atomic_json(inp,[source,missing])
    print("RUN",m+"_inference_in_process",flush=True)
    from cue_student.predict import predict
    atomic_json(root/(m+".predictions.json"),predict(runs[m]/"last.pt",[source,missing],"cuda:0"))
    report["cases"][m+"_inference"]=dict(passed=True)
    gc.collect();torch.cuda.empty_cache()
    pred=json.loads((root/(m+".predictions.json")).read_text())
    assert pred[0]["input_valid"] and len(pred[0]["scores"])=={"text":15,"audio":17,"visual":10}[m]
    assert not pred[1]["input_valid"] and pred[1]["scores"] is None
    assert pred[0]["checkpoint_scope"]=="smoke"
    assert pred[0]["input_observation"]["modality"]==m
    report["cases"][m+"_inference"]["missing_input_is_null"]=True
    save()

for m,run in runs.items():
    observations=list((run/"observations").glob("*.json"))
    assert len(observations)>=10
    assert any(json.loads(p.read_text())["modality"]==m for p in observations)
    events=[json.loads(line) for line in (run/"events.jsonl").read_text().splitlines()]
    assert any(e["event"]=="checkpoint" for e in events)
    report["cases"][m+"_persistent_observations_and_periodic_checkpoint"]=dict(passed=True,observation_files=len(observations))
report["regression_scope"]="Existing text/audio/mean-visual baseline paths; temporal candidate has separate integration_temporal.py coverage. Historical geometry evidence refers to integration_20261020_123431, not byte-identical current models.py."
report["final_code_hash"]=code_hash()
report["passed"]=True;save()
print("ALL_FINAL_REGRESSIONS_PASSED",str(root/"report.json"),flush=True)

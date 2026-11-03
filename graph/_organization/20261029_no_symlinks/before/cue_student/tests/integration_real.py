"""Real-weight GPU integration: short CLI training, resume identity, evaluation, inference and edge inputs."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import gc,json,os,subprocess,sys,time
import numpy as np
import torch
from cue_student.common import PROJECT,atomic_json,load_config,move_batch,sha256,seed_all
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
    cfg.update(encoder_train="frozen",precision="float32",dropout=0.,epochs=2,patience=10,batch_size=2,grad_accum=2)
    p=root/(m+".config.json");atomic_json(p,cfg);configs[m]=p
base=["--release",release_path,"--device","cuda:0","--allow-smoke"]
text_run=root/"text_resume"
call("text_first_step","cue_student.train",["--config",configs["text"],"--output",text_run,"--max-steps",1]+base)
call("text_resume_step","cue_student.train",["--config",configs["text"],"--output",text_run,"--resume",text_run/"last.pt","--max-steps",2]+base)
text_ref=root/"text_reference"
call("text_uninterrupted","cue_student.train",["--config",configs["text"],"--output",text_ref,"--max-steps",2]+base)
a=torch.load(text_run/"last.pt",map_location="cpu",weights_only=False);b=torch.load(text_ref/"last.pt",map_location="cpu",weights_only=False)
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
    call(m+"_evaluation","cue_student.evaluate",["--checkpoint",runs[m]/"last.pt","--release",release_path,"--output",root/(m+".metrics.json"),"--bootstrap",10])
    rows=[r for r in release.rows if r["role"]=="pseudo_train"]
    source={k:rows[0][k] for k in ("sample_id","text","audio_path","video_path")}
    missing=dict(sample_id="input_missing",text={},audio_path="/missing/audio.wav",video_path="/missing/video.mp4")
    inp=root/(m+".input.json");atomic_json(inp,[source,missing])
    call(m+"_inference","cue_student.predict",["--checkpoint",runs[m]/"last.pt","--input",inp,"--output",root/(m+".predictions.json")])
    pred=json.loads((root/(m+".predictions.json")).read_text())
    assert pred[0]["input_valid"] and len(pred[0]["scores"])=={"text":15,"audio":17,"visual":10}[m]
    assert not pred[1]["input_valid"] and pred[1]["scores"] is None
    report["cases"][m+"_inference"]["missing_input_is_null"]=True
    save()
torch.set_num_threads(8)
# The largest original WAV is used only for geometry/coverage, not for model selection or accuracy.
all_rows=json.loads((PROJECT/"cue_annotation/runs/mercaptionplus/samples.json").read_text())
long_row=max(all_rows,key=lambda r:Path(r["audio_path"]).stat().st_size)
exposure_path=PROJECT/"cue_student/artifacts/development_exposure.json"
exposure=json.loads(exposure_path.read_text());exposure["sample_ids"]=sorted(set(exposure["sample_ids"])|{long_row["sample_id"]});atomic_json(exposure_path,exposure)
for m in ("text","audio","visual"):
    print("RUN",m+"_real_model_checks",flush=True)
    cfg=load_config(configs[m]);seed_all(42);model=CueModel(cfg).cuda();collator=make_collator(cfg)
    ds=CueDataset(release,m,"pseudo_train",training=True)
    ordered=sorted(range(len(ds)),key=lambda i:ds.costs[i])
    items=[ds[ordered[0]],ds[ordered[-1]]]
    batch=move_batch(collator(items),"cuda:0");single=move_batch(collator(items[:1]),"cuda:0")
    model.eval()
    with torch.no_grad():
        together=model(batch);alone=model(single)
    delta=float((together[0]-alone[0]).abs().max())
    assert delta<2e-4,(m,delta)
    poisoned=dict(batch,targets=torch.ones_like(batch["targets"]),label_mask=torch.zeros_like(batch["label_mask"]))
    with torch.no_grad():torch.testing.assert_close(model(batch),model(poisoned),rtol=0,atol=0)
    initial_param=next(model.encoder.parameters()).detach().reshape(-1)[:32].clone()
    optimizer=torch.optim.AdamW(model.head.parameters(),lr=.01)
    losses=[]
    model.train();assert not model.encoder.training
    for step in range(8):
        optimizer.zero_grad(set_to_none=True)
        logits=model(batch);loss,n=masked_bce_sum(logits,batch["targets"],batch["label_mask"]);loss=loss/n
        assert torch.isfinite(loss);loss.backward();optimizer.step();losses.append(float(loss.detach()))
    assert losses[-1]<losses[0],(m,losses)
    assert all(p.grad is None for p in model.encoder.parameters())
    torch.testing.assert_close(initial_param,next(model.encoder.parameters()).detach().reshape(-1)[:32],rtol=0,atol=0)
    case=dict(passed=True,padding_max_abs_difference=delta,teacher_targets_not_model_features=True,small_subset_first_loss=losses[0],small_subset_last_loss=losses[-1],frozen_encoder_unchanged=True)
    if m!="text":
        edge=dict(long_row,targets=np.zeros(len(ds.cue_ids),np.float32),label_mask=np.zeros(len(ds.cue_ids),bool))
        long_batch=move_batch(collator([edge]),"cuda:0")
        model.eval()
        with torch.no_grad(): result=model(long_batch)
        assert torch.isfinite(result).all()
        if m=="audio":
            import soundfile as sf
            info=sf.info(long_row["audio_path"])
            case["edge_audio_duration"]=info.duration;case["edge_audio_samples"]=int(long_batch["audio_lengths"][0])
            assert abs(case["edge_audio_samples"]/16000-info.duration)<1/16000
        else:
            times=long_batch["frame_times"][0]
            case["edge_video_frames"]=len(times);case["edge_video_first_pts"]=times[0];case["edge_video_last_pts"]=times[-1]
            assert len(times)>8 and times[-1]>20
        del long_batch,result
    report["cases"][m+"_real_model_checks"]=case;save()
    del model,optimizer,batch,single,poisoned,together,alone;gc.collect();torch.cuda.empty_cache()
print("RUN text_full_encoder_backward",flush=True)
cfg=load_config(configs["text"]);cfg["encoder_train"]="full"
model=CueModel(cfg).cuda();collator=make_collator(cfg);ds=CueDataset(release,"text","pseudo_train",training=True)
batch=move_batch(collator([ds[0]]),"cuda:0")
loss,n=masked_bce_sum(model(batch),batch["targets"],batch["label_mask"]);(loss/n).backward()
assert model.encoder.embeddings.word_embeddings.weight.grad is not None
assert torch.isfinite(model.encoder.embeddings.word_embeddings.weight.grad).all()
report["cases"]["text_full_encoder_backward"]=dict(passed=True,embedding_gradient_finite=True)
del model,batch;gc.collect();torch.cuda.empty_cache()
report["passed"]=True;save()
print("ALL_INTEGRATION_PASSED",str(root/"report.json"),flush=True)

"""Real CLIP integration for the temporal candidate; never uses the 300 holdout."""
from graph_paths import resolve_path as _graph_resolve_path
from graph_paths import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import copy,gc,json,os,subprocess,sys
import numpy as np
import torch
from cue_student.common import PROJECT,atomic_json,load_config,move_batch,sha256,seed_all,code_hash,model_assets
from cue_student.data import Release,CueDataset,make_collator,epoch_batches
from cue_student.models import CueModel,build_optimizer
from cue_student.temporal import temporal_spec
from cue_student.objectives import masked_bce_sum
from cue_student.train import autocast
from cue_student.holdout import load_fixed_holdout

torch.set_num_threads(8)
root=PROJECT/"cue_student/artifacts"/("video_temporal_"+datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S"))
root.mkdir(parents=True)
release_path=PROJECT/"cue_student/artifacts/smoke_release_v1"
holdout=load_fixed_holdout()
report=dict(output=str(root),scope="Real CLIP smoke tests; no formal validation comparison/full training/human performance claim.",
            code_hash=code_hash(),cases={},holdout_id=holdout["holdout_id"])
def save():atomic_json(root/"report.json",report)
def passed(name,**details):
    report["cases"][name]=dict(passed=True,**details);save();print("PASS",name,flush=True)
def call(name,mod,args):
    print("RUN",name,flush=True);log=root/(name+".log")
    with log.open("w") as f:
        result=subprocess.run([sys.executable,"-u","-m",mod]+[str(a) for a in args],cwd=PROJECT,
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",TOKENIZERS_PARALLELISM="false"),stdout=f,stderr=subprocess.STDOUT)
    if result.returncode:print(log.read_text()[-7000:],flush=True)
    result.check_returncode();passed(name,log=str(log))

cfg=load_config(PROJECT/"cue_student/configs/visual_temporal.json")
cfg.update(epochs=2,patience=10,batch_size=2,grad_accum=2,save_every_steps=1)
config_path=root/"config.json";atomic_json(config_path,cfg)
base=["--config",config_path,"--release",release_path,"--device","cuda:0","--allow-smoke"]
resumed=root/"resumed";reference=root/"reference"
call("bf16_first_step","cue_student.train",base+["--output",resumed,"--max-steps",1])
call("bf16_resume","cue_student.train",base+["--output",resumed,"--resume",resumed/"last.pt","--max-steps",2])
call("bf16_uninterrupted","cue_student.train",base+["--output",reference,"--max-steps",2])
a=torch.load(_graph_resolve_path(resumed / 'last.pt'), map_location='cpu', weights_only=False)
b=torch.load(_graph_resolve_path(reference / 'last.pt'), map_location='cpu', weights_only=False)
difference=max(float((a["model"][k]-b["model"][k]).abs().max()) for k in a["model"])
assert a["progress"]["global_step"]==b["progress"]["global_step"]==2
assert difference==0.,difference
assert a["fixed_holdout_id"]==holdout["holdout_id"]
assert a["temporal_architecture"]==temporal_spec(cfg)
assert any(k.startswith("head.transformer.layers.1.") for k in a["model"])
assert not any(k.startswith("encoder.") for k in a["model"])
passed("resume_and_checkpoint",max_abs_difference=difference,temporal_architecture=a["temporal_architecture"],
       saved_tensors=len(a["model"]),external_frozen_clip=True)
del b

release=Release(release_path);ds=CueDataset(release,"visual","pseudo_train",training=True)
assert not {r["sample_id"] for r in release.rows}&set(holdout["sample_ids"])
passed("fixed_holdout_separated",release_id=release.manifest["release_id"],smoke_members=len(release.rows))
rows=sorted([ds[i] for i in range(len(ds))],key=lambda r:r["visual_duration"])
items=[rows[0],rows[-1]]
inp=[{k:r[k] for k in ("sample_id","text","audio_path","video_path")} for r in items]
inp.append(dict(sample_id="missing_video",video_path="/missing/not_a_video.mp4"))
atomic_json(root/"input.json",inp)
call("temporal_inference","cue_student.predict",["--checkpoint",resumed/"last.pt","--input",root/"input.json","--output",root/"predictions.json"])
pred=json.loads((root/"predictions.json").read_text())
assert all(p["input_valid"] and len(p["scores"])==10 for p in pred[:2])
assert pred[-1]["scores"] is None and not pred[-1]["input_valid"]
for p in pred[:2]:
    assert p["temporal_architecture"]==temporal_spec(cfg)
    observation=p["input_observation"]
    assert observation["model_frame_time_offsets_seconds"][0]==0.
    assert len(observation["model_frame_time_offsets_seconds"])==len(observation["actual_frame_pts_seconds"])
passed("inference_metadata_and_missing_video",missing_is_null=True)
call("temporal_evaluation","cue_student.evaluate",["--checkpoint",resumed/"last.pt","--release",release_path,"--output",root/"evaluation.json"])

seed_all(42);model=CueModel(cfg).cuda()
initial={k:v.clone() for k,v in model.checkpoint_state().items()}
model.restore_weights(a["model"])
updated=max(float((initial[k]-a["model"][k]).abs().max()) for k in initial if k.startswith("head.transformer"))
assert updated>0
passed("transformer_parameters_updated",max_abs_parameter_change=updated)
del initial,a;gc.collect()
collator=make_collator(cfg)
batch=move_batch(collator(items),"cuda:0");single=move_batch(collator(items[:1]),"cuda:0")
model.eval()
with torch.no_grad():
    joint=model(batch);alone=model(single)
    with autocast(cfg,torch.device("cuda:0")):
        joint_bf16=model(batch);alone_bf16=model(single)
fp32_difference=float((joint[0]-alone[0]).abs().max())
bf16_difference=float((joint_bf16[0]-alone_bf16[0]).abs().max())
assert fp32_difference<2e-4,(fp32_difference,bf16_difference)
assert bf16_difference<.02,(fp32_difference,bf16_difference)
passed("real_padding_consistency",fp32_max_abs_difference=fp32_difference,bf16_max_abs_difference=bf16_difference)

with torch.no_grad():
    encoded=[]
    for pixels in batch["pixel_values"].split(cfg["frame_batch_size"]):
        encoded.append(model.encoder(pixel_values=pixels).image_embeds)
    from cue_student.models import segment_pad
    features,mask=segment_pad(torch.cat(encoded),batch["frame_owners"],batch["batch_size"])
    times=batch["frame_time_offsets"]
    original=model.head(features,mask,times)
    reversed_features=features.clone()
    for i in range(len(features)):
        n=int(mask[i].sum());reversed_features[i,:n]=features[i,:n].flip(0)
    reverse=model.head(reversed_features,mask,times)
    slower=model.head(features,mask,times*2.)
order_difference=float((original-reverse).abs().max())
timing_difference=float((original-slower).abs().max())
assert order_difference>1e-6 and timing_difference>1e-6,(order_difference,timing_difference)
passed("real_order_and_timing_sensitivity",reversed_order_logit_change=order_difference,doubled_time_logit_change=timing_difference)
with torch.no_grad():
    poisoned=dict(batch,targets=torch.ones_like(batch["targets"]),label_mask=torch.zeros_like(batch["label_mask"]))
    torch.testing.assert_close(model(batch),model(poisoned),atol=0,rtol=0)
    one=model.head(features[:1,:1],mask[:1,:1],times[:1,:1])
    assert tuple(one.shape)==(1,10) and torch.isfinite(one).all()
passed("single_frame_and_no_teacher_input",single_frame_supported=True,teacher_targets_do_not_change_logits=True)

encoder_snapshot=[p.detach().reshape(-1)[:16].clone() for p in model.encoder.parameters()]
optimizer=torch.optim.AdamW(model.head.parameters(),lr=1e-3,weight_decay=0)
model.head.train()
# Dropout remains active: record deterministic evaluation loss before/after optimization.
def eval_loss():
    model.head.eval()
    with torch.no_grad():
        loss,n=masked_bce_sum(model.head(features,mask,times),batch["targets"],batch["label_mask"])
    model.head.train()
    return float(loss/n)
before=eval_loss()
for _ in range(16):
    optimizer.zero_grad(set_to_none=True)
    logits=model.head(features,mask,times)
    loss,n=masked_bce_sum(logits,batch["targets"],batch["label_mask"]);(loss/n).backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.head.parameters())
    torch.nn.utils.clip_grad_norm_(model.head.parameters(),1.)
    optimizer.step()
after=eval_loss()
assert after<before,(before,after)
assert all(p.grad is None for p in model.encoder.parameters())
assert all(torch.equal(saved,p.detach().reshape(-1)[:16]) for saved,p in zip(encoder_snapshot,model.encoder.parameters()))
passed("real_feature_subset_learning",first_eval_bce=before,last_eval_bce=after,steps=16,frozen_clip_unchanged=True)
model.eval()

exposed=set(json.loads((PROJECT/"cue_student/artifacts/development_exposure.json").read_text())["sample_ids"])
all_rows=json.loads((PROJECT/"cue_annotation/runs/mercaptionplus/samples.json").read_text())
long_row=max((r for r in all_rows if r["sample_id"] in exposed),key=lambda r:Path(r["audio_path"]).stat().st_size)
assert long_row["sample_id"] not in holdout["sample_ids"]
edge=dict(long_row,targets=np.zeros(10,np.float32),label_mask=np.zeros(10,bool))
long_batch=move_batch(collator([edge]),"cuda:0")
with torch.no_grad(),autocast(cfg,torch.device("cuda:0")):long_result=model(long_batch)
assert torch.isfinite(long_result).all()
pts=long_batch["frame_times"][0]
assert len(pts)>8 and pts[-1]-pts[0]>20
passed("full_long_video",sample_id=long_row["sample_id"],frames=len(pts),first_pts=pts[0],last_pts=pts[-1],
       last_model_time_offset=float(long_batch["frame_time_offsets"][0,-1]),no_truncation=True)
del model,optimizer,batch,single,long_batch,features,encoded,encoder_snapshot;gc.collect();torch.cuda.empty_cache()

old=PROJECT/"cue_student/artifacts/integration_20261020_142603"
call("old_mean_checkpoint_inference","cue_student.predict",["--checkpoint",old/"visual/last.pt","--input",old/"visual.input.json","--output",root/"old_mean_predictions.json"])
prior=json.loads((old/"visual.predictions.json").read_text())
now=json.loads((root/"old_mean_predictions.json").read_text())
baseline_difference=max(abs(x-y) for x,y in zip(prior[0]["scores"],now[0]["scores"]))
assert baseline_difference<1e-6
assert now[0]["temporal_architecture"]=={"temporal_model":"none"}
passed("mean_baseline_compatibility",max_abs_score_difference=baseline_difference)

observations=list((resumed/"observations").glob("*.json"))
assert observations
for p in observations:
    record=json.loads(p.read_text())
    assert record["temporal_architecture"]==temporal_spec(cfg)
    assert record["model_frame_time_offsets_seconds"][0]==0.
passed("persistent_temporal_observations",files=len(observations))
assert code_hash()==report["code_hash"]
report.update(passed=True,source_sha256={str(p.relative_to(PROJECT)):sha256(p) for p in sorted((PROJECT/"cue_student").glob("*.py"))},
              config_sha256=sha256(PROJECT/"cue_student/configs/visual_temporal.json"),
              note="Smoke loss/order sensitivity do not establish generalization improvement over mean. Formal same-split validation comparison is pending.")
save();print("ALL_VIDEO_TEMPORAL_PASSED",str(root/"report.json"),flush=True)

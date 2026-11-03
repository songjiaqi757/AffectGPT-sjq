from pathlib import Path
import os,sys,json,time,traceback
ROOT=Path(__file__).resolve().parent;PROJECT=Path("/ai/sjq/AffectGPT-sjq");sys.path.insert(0,str(PROJECT))
import torch
torch.cuda.set_device(0)
# Bound this single preflight process to 20% of its one visible 80GB GPU.
torch.cuda.set_per_process_memory_fraction(0.20,0)
from cue_student.common import load_config,move_batch,atomic_json,code_hash,seed_all
from cue_student.data import Release,CueDataset,make_collator
from cue_student.models import CueModel,build_optimizer
from cue_student.objectives import masked_bce_sum
from cue_student.train import autocast
torch.set_num_threads(8)
name=sys.argv[1];report=dict(name=name,passed=False,code_hash=code_hash(),gpu_uuid=os.environ["CUDA_VISIBLE_DEVICES"],memory_fraction_cap=0.20)
def main():
 plan=json.loads((ROOT/"experiment_plan.json").read_text());cfg=load_config(ROOT/"configs"/(name+".json"))
 seed_all(cfg["seed"]);release=Release(plan["release"])
 assert release.manifest["release_id"]==plan["release_id"] and release.fixed_holdout_id==plan["fixed_holdout_id"]
 ds=CueDataset(release,cfg["modality"],"pseudo_train",training=True)
 order=sorted(range(len(ds)),key=lambda i:ds.costs[i],reverse=True);items=[ds[i] for i in order[:2]]
 assert not set(r["sample_id"] for r in items)&set(release.eligibility["excluded_sample_ids"])
 batch=move_batch(make_collator(cfg)(items),"cuda:0")
 model=CueModel(cfg).cuda()
 if cfg["modality"]=="audio":
  model.encoder.config.layerdrop=0.0
  report["worst_case_all_encoder_layers_active"]=True
 assert all(p.requires_grad for p in model.encoder.parameters())
 assert model.encoder.is_gradient_checkpointing
 opt=build_optimizer(model,cfg);encoder_params=dict(model.encoder.named_parameters())
 first_conv=next((k for k in encoder_params if "feature_extractor.conv_layers.0.conv.weight" in k),None)
 representative=[k for k,p in encoder_params.items() if p.numel()>128 and ("q_proj.weight" in k or k==first_conv)]
 before={k:encoder_params[k].detach().flatten()[:128].float().cpu().clone() for k in representative}
 head_before={k:p.detach().flatten()[:128].float().cpu().clone() for k,p in model.head.named_parameters()}
 torch.cuda.reset_peak_memory_stats();start=time.monotonic();model.train();opt.zero_grad(set_to_none=True)
 with autocast(cfg,torch.device("cuda:0")):
  logits=model(batch);loss,n=masked_bce_sum(logits,batch["targets"],batch["label_mask"]);loss=loss/n
 assert torch.isfinite(loss) and torch.isfinite(logits).all();loss.backward()
 grads={k:p.grad for k,p in encoder_params.items() if p.grad is not None}
 assert grads and all(torch.isfinite(g).all() for g in grads.values())
 assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.head.parameters())
 norm=torch.nn.utils.clip_grad_norm_(model.parameters(),cfg["clip_grad_norm"]);assert torch.isfinite(norm)
 opt.step();torch.cuda.synchronize()
 updated={k:float((encoder_params[k].detach().flatten()[:128].float().cpu()-v).abs().max()) for k,v in before.items()}
 assert any(v>0 for k,v in updated.items() if "q_proj.weight" in k),updated
 if first_conv:assert updated[first_conv]>0
 head_delta=max(float((dict(model.head.named_parameters())[k].detach().flatten()[:128].float().cpu()-v).abs().max()) for k,v in head_before.items());assert head_delta>0
 report.update(passed=True,encoder_parameters=sum(p.numel() for p in model.encoder.parameters()),trainable_encoder_parameters=sum(p.numel() for p in model.encoder.parameters() if p.requires_grad),
  encoder_parameter_tensors=len(encoder_params),encoder_tensors_with_gradients=len(grads),no_gradient_tensors=[k for k,p in encoder_params.items() if p.grad is None],
  sampled_encoder_updates=updated,head_max_update=head_delta,loss=float(loss.detach()),grad_norm=float(norm),seconds=time.monotonic()-start,
  peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20,peak_reserved_mib=torch.cuda.max_memory_reserved()/2**20,
  input_samples=[r["sample_id"] for r in items],input_durations=[r[cfg["modality"]+"_duration"] for r in items],
  input_shape=list(batch["input_values"].shape if cfg["modality"]=="audio" else batch["pixel_values"].shape),
  train_samples=len(ds),validation_samples=len(CueDataset(release,cfg["modality"],"pseudo_validation")),release_id=release.manifest["release_id"],fixed_holdout_id=release.fixed_holdout_id,
  gradient_checkpointing=True,precision=cfg["precision"],
  note="One bounded preflight only. Two longest training examples together exceed the production duration budget. No holdout/validation examples used for backward. HuBERT LayerDrop/inactive SpecAugment can leave individual tensors without gradients.")
 atomic_json(ROOT/(name+".preflight.json"),report);print(json.dumps(report,ensure_ascii=False),flush=True)
try:main()
except BaseException:
 report["error"]=traceback.format_exc();atomic_json(ROOT/(name+".preflight.json"),report);raise

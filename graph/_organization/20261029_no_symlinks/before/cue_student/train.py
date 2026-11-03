"""Single-GPU, sample-level masked-BCE trainer with exact effective-batch normalization."""
from __future__ import annotations
import argparse, contextlib, fcntl, json, math, os, tempfile, time, signal
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader
from .common import absolute, atomic_json, canonical_hash, code_hash, load_config, model_assets, move_batch, restore_rng, rng_state, seed_all
from .data import Release, CueDataset, epoch_batches, make_collator
from .models import CueModel, build_optimizer
from .objectives import masked_bce_sum, training_weights, binary_metrics
from .observations import write_observations
from .temporal import temporal_spec

def autocast(cfg, device):
    if cfg.get("precision")=="bf16" and device.type=="cuda":
        if not torch.cuda.is_bf16_supported(): raise RuntimeError("bf16 unsupported; select float32 explicitly")
        return torch.autocast("cuda",dtype=torch.bfloat16)
    return contextlib.nullcontext()

from .loading import loader_for

@torch.inference_mode()
def evaluate(model,dataset,collator,cfg,device,eligible=None,observation_dir=None):
    model.eval(); batches=epoch_batches(dataset,cfg.get("batch_size",2),shuffle=False,max_units=cfg.get("max_batch_units"))
    ys=[]; scores=[]; masks=[]; ids=[]; numerator=0.; denominator=0
    for batch in loader_for(dataset,batches,collator,cfg):
        if observation_dir is not None: write_observations(batch,observation_dir,cfg["modality"],cfg)
        batch=move_batch(batch,device)
        with autocast(cfg,device): logits=model(batch)
        if not torch.isfinite(logits).all(): raise FloatingPointError("Non-finite validation logits")
        loss,count=masked_bce_sum(logits,batch["targets"],batch["label_mask"])
        numerator+=float(loss); denominator+=count
        ys.append(batch["targets"].cpu().numpy()); masks.append(batch["label_mask"].cpu().numpy())
        scores.append(logits.float().sigmoid().cpu().numpy()); ids.extend(batch["sample_ids"])
    y=np.concatenate(ys); s=np.concatenate(scores); m=np.concatenate(masks)
    metrics=binary_metrics(y,s,m,dataset.cue_ids,eligible=eligible)
    metrics["masked_bce"]=numerator/denominator if denominator else None
    metrics["samples"]=len(ids); metrics["valid_labels"]=denominator
    return metrics,dict(targets=y,scores=s,mask=m,sample_ids=ids)

def save_torch(path,value):
    path=Path(path); fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=path.name+".",suffix=".tmp"); os.close(fd)
    try: torch.save(value,tmp); os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def signature(cfg,release,assets,cues):
    return canonical_hash(dict(config=cfg,release_id=release.manifest["release_id"],assets=assets,
                               cue_ids=cues,code_hash=code_hash(),fixed_holdout_id=release.fixed_holdout_id))

def run(args):
    cfg=load_config(args.config); seed_all(cfg.get("seed",42)); torch.set_num_threads(args.cpu_threads)
    if int(os.environ.get("WORLD_SIZE","1"))!=1: raise ValueError("This trainer is single process; DDP is not implemented")
    device=torch.device(args.device)
    if device.type=="cuda": torch.cuda.set_device(device)
    release=Release(args.release)
    if release.manifest["scope"]=="smoke" and not args.allow_smoke: raise ValueError("Smoke package requires --allow-smoke; never a formal model")
    if release.manifest["scope"]!="smoke" and release.manifest["group_limitations"] and not args.allow_unverified_groups:
        raise ValueError("Unverified provenance: use --allow-unverified-groups only for a disclosed engineering baseline")
    train=CueDataset(release,cfg["modality"],"pseudo_train",training=True)
    val=CueDataset(release,cfg["modality"],"pseudo_validation")
    collator=make_collator(cfg)
    eligible=[k for k in range(len(train.cue_ids)) if np.any(val.label_mask[:,k] & (val.targets[:,k]==1)) and np.any(val.label_mask[:,k] & (val.targets[:,k]==0))]
    weights,pos,neg=training_weights(train.targets,train.label_mask,cfg.get("weighted_bce",False))
    assets=model_assets(cfg["model_dir"]); sig=signature(cfg,release,assets,train.cue_ids)
    out=absolute(args.output); out.mkdir(parents=True,exist_ok=True)
    with (out/"runner.lock").open("w") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (out/"last.pt").exists() and not args.resume: raise FileExistsError("Output already contains last.pt; explicitly resume or use a new directory")
        if args.resume and absolute(args.resume).parent!=out: raise ValueError("Resume within the original output directory to preserve best checkpoint history")
        if cfg.get("save_every_steps",200)<0: raise ValueError("save_every_steps must be nonnegative")
        model=CueModel(cfg).to(device); optimizer=build_optimizer(model,cfg)
        batches_per_epoch=[len(epoch_batches(train,cfg["batch_size"],epoch,cfg.get("seed",42),max_units=cfg.get("max_batch_units"))) for epoch in range(cfg["epochs"])]
        accum=cfg.get("grad_accum",1)
        if accum<1 or cfg["batch_size"]<1 or cfg["epochs"]<1: raise ValueError("Positive batch/epoch/accumulation counts required")
        total_steps=sum(math.ceil(n/accum) for n in batches_per_epoch)
        warmup=max(1,round(total_steps*cfg.get("warmup_fraction",.1)))
        def scale(step):
            return (step+1)/warmup if step<warmup else max(0.,(total_steps-step)/max(1,total_steps-warmup))
        scheduler=torch.optim.lr_scheduler.LambdaLR(optimizer,scale)
        progress=dict(epoch=0,next_batch=0,global_step=0,best_score=None,best_loss=None,bad_epochs=0,skipped_empty_groups=0)
        if args.init_from and args.resume: raise ValueError("Choose init-from or resume")
        if args.init_from:
            old=torch.load(absolute(args.init_from),map_location="cpu",weights_only=False)
            if old["assets"]!=assets or old["cue_ids"]!=train.cue_ids: raise ValueError("Initializer assets/ontology mismatch")
            for key in ("modality","pooling","max_length","text_overlap","fps","spatial"):
                if old["config"].get(key)!=cfg.get(key): raise ValueError("Initializer architecture/preprocessing differs: "+key)
            if temporal_spec(old["config"])!=temporal_spec(cfg): raise ValueError("Initializer temporal architecture differs")
            model.restore_weights(old["model"],initializing=True)
        if args.resume:
            ckpt=torch.load(absolute(args.resume),map_location="cpu",weights_only=False)
            if ckpt["signature"]!=sig: raise ValueError("Resume requires identical config, code, release, ontology and encoder assets")
            model.restore_weights(ckpt["model"]); optimizer.load_state_dict(ckpt["optimizer"]); scheduler.load_state_dict(ckpt["scheduler"])
            progress=ckpt["progress"]; restore_rng(ckpt["rng"])
        atomic_json(out/"config.resolved.json",cfg)
        atomic_json(out/"training_manifest.json",dict(signature=sig,release=str(release.path),release_id=release.manifest["release_id"],
                    scope=release.manifest["scope"],fixed_holdout_id=release.fixed_holdout_id,temporal_architecture=temporal_spec(cfg),group_limitations=release.manifest["group_limitations"],model_assets=assets,
                    cue_ids=train.cue_ids,train_positive=pos.tolist(),train_negative=neg.tolist(),pos_weight=weights.tolist(),
                    eligible_validation_cues=[train.cue_ids[k] for k in eligible],code_hash=code_hash(),total_planned_steps=total_steps,
                    train_samples=len(train),validation_samples=len(val),excluded_no_supervision=sum(r["role"]=="pseudo_train" for r in release.rows)-len(train),
                    note="Teacher fitting baseline; thresholds 0.5 uncalibrated; no gold performance claim"))
        weight=torch.tensor(weights,device=device)
        def emit(event):
            with (out/"events.jsonl").open("a") as f:
                f.write(json.dumps(dict(time_unix=time.time(),**event),ensure_ascii=False,allow_nan=False)+"\n"); f.flush()
            print(json.dumps(event,ensure_ascii=False,allow_nan=False),flush=True)
        def checkpoint_payload(validation=None):
            return dict(format_version=1,signature=sig,code_hash=code_hash(),config=cfg,release_id=release.manifest["release_id"],assets=assets,
                      cue_ids=train.cue_ids,train_positive=pos.tolist(),train_negative=neg.tolist(),
                      model=model.checkpoint_state(),optimizer=optimizer.state_dict(),scheduler=scheduler.state_dict(),scaler=None,
                      progress=dict(progress),rng=rng_state(),validation=validation,scope=release.manifest["scope"],fixed_holdout_id=release.fixed_holdout_id,
                      temporal_architecture=temporal_spec(cfg))
        def validate_save(reason):
            metrics,pred=evaluate(model,val,collator,cfg,device,eligible,observation_dir=out/"observations")
            primary=metrics["macro_ap"] if eligible else (-metrics["masked_bce"] if metrics["masked_bce"] is not None else -1e30)
            loss=metrics["masked_bce"] if metrics["masked_bce"] is not None else 1e30
            better=(progress["best_score"] is None or primary>progress["best_score"]+1e-12 or
                    (abs(primary-progress["best_score"])<=1e-12 and loss<progress["best_loss"]-1e-12))
            if better: progress.update(best_score=primary,best_loss=loss,bad_epochs=0)
            elif reason=="epoch": progress["bad_epochs"]+=1
            ckpt=checkpoint_payload(metrics)
            save_torch(out/"last.pt",ckpt)
            if better: save_torch(out/"best.pt",ckpt)
            atomic_json(out/"validation.last.json",metrics)
            np.savez_compressed(out/"validation.last.npz",**{k:v for k,v in pred.items() if k!="sample_ids"},sample_ids=np.array(pred["sample_ids"]))
            emit(dict(event="validation",reason=reason,epoch=progress["epoch"],step=progress["global_step"],
                      macro_ap=metrics["macro_ap"],masked_bce=metrics["masked_bce"],best_updated=better))
        stop_requested=False
        def request_stop(signum,frame):
            nonlocal stop_requested
            stop_requested=True
        signal.signal(signal.SIGUSR1,request_stop)
        signal.signal(signal.SIGTERM,request_stop)
        def stop_safely():
            save_torch(out/"last.pt",checkpoint_payload())
            emit(dict(event="graceful_stop",step=progress["global_step"],next_batch=progress["next_batch"]))
        if args.max_steps is not None and progress["global_step"]>=args.max_steps:
            emit(dict(event="already_at_step_limit",step=progress["global_step"])); return
        while progress["epoch"]<cfg["epochs"]:
            epoch=progress["epoch"]; batches=epoch_batches(train,cfg["batch_size"],epoch,cfg.get("seed",42),max_units=cfg.get("max_batch_units"))
            start=progress["next_batch"]
            stream=iter(loader_for(train,batches[start:],collator,cfg))
            for group_start in range(start,len(batches),accum):
                if stop_requested: stop_safely(); return
                group=batches[group_start:group_start+accum]
                count=int(sum(train.label_mask[idx].sum() for idx in group))
                optimizer.zero_grad(set_to_none=True); model.train()
                numerator=0.
                for _ in group:
                    raw_batch=next(stream)
                    write_observations(raw_batch,out/"observations",cfg["modality"],cfg)
                    batch=move_batch(raw_batch,device)
                    with autocast(cfg,device): logits=model(batch)
                    if not torch.isfinite(logits).all(): raise FloatingPointError("Non-finite training logits")
                    loss,n=masked_bce_sum(logits,batch["targets"],batch["label_mask"],weight)
                    numerator+=float(loss.detach())
                    if count: (loss/count).backward()
                progress["next_batch"]=group_start+len(group)
                if count:
                    norm=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],cfg.get("clip_grad_norm",1.))
                    if not torch.isfinite(norm): raise FloatingPointError("Non-finite gradients")
                    optimizer.step(); scheduler.step(); progress["global_step"]+=1
                    emit(dict(event="train",epoch=epoch,step=progress["global_step"],valid_labels=count,masked_bce=numerator/count,grad_norm=float(norm)))
                else: progress["skipped_empty_groups"]+=1
                every=cfg.get("save_every_steps",200)
                if count and every and progress["global_step"]%every==0:
                    save_torch(out/"last.pt",checkpoint_payload())
                    emit(dict(event="checkpoint",step=progress["global_step"],next_batch=progress["next_batch"]))
                if stop_requested: stop_safely(); return
                if args.max_steps is not None and progress["global_step"]>=args.max_steps:
                    if progress["next_batch"]==len(batches): progress.update(epoch=epoch+1,next_batch=0)
                    validate_save("step_limit"); return
            progress.update(epoch=epoch+1,next_batch=0)
            validate_save("epoch")
            if stop_requested: stop_safely(); return
            if progress["bad_epochs"]>=cfg.get("patience",3):
                emit(dict(event="early_stop",step=progress["global_step"])); break
        emit(dict(event="complete",step=progress["global_step"],epochs=progress["epoch"]))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",required=True); p.add_argument("--release",required=True); p.add_argument("--output",required=True)
    p.add_argument("--device",default="cuda:0"); p.add_argument("--cpu-threads",type=int,default=8)
    p.add_argument("--resume"); p.add_argument("--init-from"); p.add_argument("--max-steps",type=int)
    p.add_argument("--allow-smoke",action="store_true"); p.add_argument("--allow-unverified-groups",action="store_true")
    args=p.parse_args()
    if args.max_steps is not None and args.max_steps<1: p.error("--max-steps must be positive")
    run(args)
if __name__=="__main__": main()

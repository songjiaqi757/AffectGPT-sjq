"""Single-GPU, five-epoch AffectGPT continuation with frozen graph evidence."""
import argparse,copy,json,math,os,random,sys,time,traceback
from pathlib import Path
import numpy as np
import torch
from amg_runtime.common import read,sha,canonical,atomic_json,require
from .common import ROOT,load_plan,now,verify_code

def seed_worker(index):
 seed=torch.initial_seed()%2**32;np.random.seed(seed);random.seed(seed);torch.set_num_threads(1)
def to_device(value,device):
 if torch.is_tensor(value):return value.to(device,non_blocking=True)
 if isinstance(value,dict):return {k:to_device(v,device) for k,v in value.items()}
 if isinstance(value,list):return [to_device(v,device) for v in value]
 return value
def build_optimizer(model,settings):
 decay=[];no_decay=[];names=[]
 for name,p in model.named_parameters():
  if not p.requires_grad:continue
  names.append(name)
  (no_decay if p.ndim<2 or any(x in name for x in ["bias","ln","bn"]) else decay).append(p)
 optimizer=torch.optim.AdamW([dict(params=decay,weight_decay=settings["weight_decay"]),dict(params=no_decay,weight_decay=0)],lr=settings["learning_rate"],weight_decay=settings["weight_decay"],betas=(.9,.999))
 return optimizer,names
def save_checkpoint(model,optimizer,scaler,config,epoch,stats,output,metadata):
 grad={k:p.requires_grad for k,p in model.named_parameters()}
 state={k:v for k,v in model.state_dict().items() if (k not in grad or grad[k]) and not k.startswith("polarity_head.")}
 obj=dict(model=state,polarity_head=model.polarity_head.state_dict() if hasattr(model,"polarity_head") else None,optimizer=optimizer.state_dict(),config=config,scaler=scaler.state_dict(),epoch=epoch,amg_finetune=metadata,training_stats=stats,rng_state=dict(torch=torch.get_rng_state(),cuda=torch.cuda.get_rng_state_all(),python=random.getstate(),numpy=dict(name=np.random.get_state()[0],keys=np.random.get_state()[1].tolist(),position=int(np.random.get_state()[2]),has_gauss=int(np.random.get_state()[3]),cached_gaussian=float(np.random.get_state()[4]))))
 target=output/f"checkpoint_{epoch:06d}_loss_{stats['loss']:.3f}.pth";tmp=target.with_suffix(".pth.tmp")
 torch.save(obj,tmp);tmp.replace(target)
 return dict(path=str(target),sha256=sha(target),epoch=epoch,loss=stats["loss"])
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);p.add_argument("--base-epoch",type=int,required=True);args=p.parse_args()
 run=Path(args.run).resolve();plan=load_plan(run);verify_code(run)
 spec=next(s for s in plan["checkpoints"] if s["base_epoch"]==args.base_epoch);output=Path(spec["output"]);output.mkdir(exist_ok=False)
 status=dict(state="loading",llm_gradient_checkpointing=False,base_epoch=args.base_epoch,physical_gpu=os.environ.get("CUDA_VISIBLE_DEVICES"),pid=os.getpid(),plan_id=plan["plan_id"],started_at_beijing=now(),completed_steps=0,completed_epochs=0,total_steps=25000,additional_epochs=5)
 status_path=run/f"experiment_{args.base_epoch}_status.json"
 def update(**fields):
  status.update(fields,updated_at_beijing=now());atomic_json(status_path,status);atomic_json(output/"status.json",status)
 try:
  update()
  require(read(Path(plan["pipeline_run"])/"cpu_preflight.json")["passed"],"CPU preflight has not passed; GPU update verified inside training")
  for relative,key in [("train_records.json","train_records_sha256"),("human_audit_500.json","audit_records_sha256")]:
   require(sha(run/relative)==plan["inputs"][key],"Current-run data manifest changed")
  assets=read(run/"model_assets_manifest.json")
  for filename,binding in assets["assets"].items():
   st=Path(filename).stat();require(st.st_size==binding["bytes"] and st.st_mtime_ns==binding["mtime_ns"],"Pretrained model asset changed")
  ready=read(run/"cache_manifest.json");require(ready["complete"] and ready["samples"]==plan["training_count"] and ready["plan_id"]==plan["plan_id"],"Graph evidence preflight incomplete")
  require(sha(run/"query_engine_config.json")==plan["inputs"]["query_config_sha256"],"Frozen query configuration changed")
  require(sha(spec["path"])==spec["sha256"],"Original checkpoint changed")
  torch.set_num_threads(4);random.seed(42);np.random.seed(42);torch.manual_seed(42);torch.cuda.manual_seed_all(42);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  os.chdir(ROOT/"AffectGPT");sys.path.insert(0,str(ROOT/"AffectGPT"))
  from omegaconf import OmegaConf
  from my_affectgpt.models.affectgpt import AffectGPT
  from .dataset import GraphContinueDataset
  config=read(run/"original_config.json");config=copy.deepcopy(config)
  config["model"].update(ckpt="",ckpt_2="",ckpt_3="",max_length=plan["training"]["max_sequence_tokens"])
  config["run"].update(distributed=False,world_size=1,max_epoch=args.base_epoch+5,output_dir=str(output),resume_ckpt_path=spec["path"],warmup_steps=0)
  config["amg_finetune"]=dict(variant=plan["active_variant"],plan_id=plan["plan_id"],query_config_id=plan["query_config_id"],cache_manifest_sha256=sha(run/"cache_manifest.json"),base_checkpoint_sha256=spec["sha256"],memory_execution_sha256=sha(run/"training_execution.json"),llm_gradient_checkpointing=False,graph_oof=True,oof_reference_plan_id=plan["oof_reference_plan_id"],evidence_policy_id=canonical(plan["policy"]),graph_probability=plan["variant_settings"][plan["active_variant"]]["graph_probability"],polarity_loss_weight=plan["variant_settings"][plan["active_variant"]]["polarity_loss_weight"],polarity_plan_id=plan["polarity_plan_id"])
  atomic_json(output/"config.json",config)
  cfg=OmegaConf.create(config["model"])
  checkpoint=torch.load(spec["path"],map_location="cpu",weights_only=True)
  require(checkpoint["epoch"]==args.base_epoch,"Base checkpoint epoch mismatch")
  model=AffectGPT.from_config(cfg)
  trainable={k:p for k,p in model.named_parameters() if p.requires_grad}
  unexpected=set(checkpoint["model"])-set(model.state_dict());missing=set(trainable)-set(checkpoint["model"])
  require(not unexpected and not missing,"Checkpoint architecture/trainable mismatch: "+repr((unexpected,missing)))
  for name,value in checkpoint["model"].items():require(tuple(value.shape)==tuple(model.state_dict()[name].shape),"Checkpoint tensor shape mismatch: "+name)
  result=model.load_state_dict(checkpoint["model"],strict=False);require(not result.unexpected_keys and not (set(result.missing_keys)&set(trainable)),"Trainable weight loading incomplete")
  # Only frozen base/encoder tensors may be absent from this trainable-only checkpoint.
  for name in trainable:require(torch.equal(trainable[name].detach().cpu(),checkpoint["model"][name]),"Restored weight mismatch: "+name)
  model=model.to("cuda:0");model.train()
  model.llama_model.gradient_checkpointing_disable()
  require(not model.llama_model.is_gradient_checkpointing,"LLM gradient checkpointing is still active")
  model.llama_model.config.use_cache=False
  atomic_json(output/"memory_execution.json",read(run/"training_execution.json"))
  optimizer,names=build_optimizer(model,plan["training"])
  auxiliary=None;aux_settings=dict(plan["training"],polarity_loss_weight=plan["variant_settings"][plan["active_variant"]]["polarity_loss_weight"])
  has_head=checkpoint.get("polarity_head") is not None
  require(has_head==(args.base_epoch==40),"Continuation must restore the current D head, while original35 starts a new head")
  if has_head:
   require(aux_settings["polarity_loss_weight"]>0,"Cannot discard saved polarity head")
   from .auxiliary import PolarityLoss
   auxiliary=PolarityLoss(model,optimizer,aux_settings)
   model.polarity_head.load_state_dict(checkpoint["polarity_head"],strict=True)
   require(all(torch.equal(v.detach().cpu(),checkpoint["polarity_head"][k]) for k,v in model.polarity_head.state_dict().items()),"Saved polarity head restoration failed")
  require([len(g["params"]) for g in optimizer.param_groups]==[len(g["params"]) for g in checkpoint["optimizer"]["param_groups"]],"Optimizer parameter group sizes differ")
  optimizer.load_state_dict(checkpoint["optimizer"])
  for group,saved_group in zip(optimizer.param_groups,checkpoint["optimizer"]["param_groups"]):
   for parameter,saved_id in zip(group["params"],saved_group["params"]):
    saved_state=checkpoint["optimizer"]["state"].get(saved_id)
    if saved_state is None:
     require(parameter not in optimizer.state or not optimizer.state[parameter],"Previously unused parameter gained optimizer state")
     continue
    state=optimizer.state[parameter]
    require(set(state)==set(saved_state),"Optimizer state keys mismatch")
    for key,value in state.items():
     if torch.is_tensor(value):require(torch.equal(value.detach().cpu(),saved_state[key].detach().cpu()),"Optimizer state value changed: "+key)
     else:require(value==saved_state[key],"Optimizer scalar state changed")
    for key in ["exp_avg","exp_avg_sq"]:require(state[key].shape==parameter.shape,"Optimizer parameter alignment mismatch")
  for group in optimizer.param_groups:group["lr"]=plan["training"]["learning_rate"]
  scaler=torch.amp.GradScaler("cuda");scaler.load_state_dict(checkpoint["scaler"])
  if auxiliary is None and aux_settings["polarity_loss_weight"]>0:
   from .auxiliary import PolarityLoss
   auxiliary=PolarityLoss(model,optimizer,aux_settings)
  restored_rng=False
  if "rng_state" in checkpoint:
   rs=checkpoint["rng_state"];torch.set_rng_state(rs["torch"]);torch.cuda.set_rng_state_all(rs["cuda"]);random.setstate(rs["python"])
   ns=rs["numpy"];np.random.set_state((ns["name"],np.array(ns["keys"],dtype=np.uint32),ns["position"],ns["has_gauss"],ns["cached_gaussian"]));restored_rng=True
  load_report=dict(passed=True,base_epoch=args.base_epoch,base_checkpoint_sha256=spec["sha256"],trainable_tensor_count=len(trainable),all_trainable_weights_equal_before_training=True,optimizer_restored=True,all_saved_optimizer_states_equal=True,optimizer_groups=[len(g["params"]) for g in optimizer.param_groups],optimizer_parameter_order_sha256=canonical(names),scaler_restored=True,initial_scaler=scaler.state_dict(),next_epoch=args.base_epoch+1,final_epoch=args.base_epoch+5,missing_frozen_tensors=len(result.missing_keys),llm_gradient_checkpointing=model.llama_model.is_gradient_checkpointing,polarity_head_restored=has_head,rng_state_restored=restored_rng,data_loader_state="reconstructed with original fixed seed42; old checkpoints did not store sampler and per-worker RNG state")
  atomic_json(output/"checkpoint_load_report.json",load_report);del checkpoint
  if auxiliary is not None:
   atomic_json(output/"polarity_head_setup.json",dict(enabled=True,loss_weight=auxiliary.weight,head_restored=has_head,optimizer_head_moments_restored=has_head,head_parameters=sum(x.numel() for x in model.polarity_head.parameters()),representation="last prompt token after Qwen final norm",answer_tokens_used=False,label_mapping=plan["polarity_label_mapping"],ignored_label=-100))
  dataset=GraphContinueDataset(run,cfg)
  require(len(dataset)==plan["training_count"],"Training membership changed")
  generator=torch.Generator();generator.manual_seed(42)
  loader=torch.utils.data.DataLoader(dataset,batch_size=plan["training"]["batch_size"],shuffle=True,drop_last=True,num_workers=plan["training"]["num_workers"],collate_fn=dataset.collater,worker_init_fn=seed_worker,generator=generator,pin_memory=True,persistent_workers=True,multiprocessing_context="spawn",prefetch_factor=2)
  iterator=iter(loader);optimizer.zero_grad(set_to_none=True);started=time.time();completed=0;optimizer_updates=0;skipped=0;checkpoints=[];smoke_passed=False
  probe_name=next(n for n in trainable if "lora_B" in n);probe=model.get_parameter(probe_name);initial_probe=probe.detach().clone()
  settings=plan["training"];metrics_file=(output/"steps.jsonl").open("a",buffering=1)
  update(state="training",current_epoch=args.base_epoch+1,epoch_step=0,trainable_parameters=sum(p.numel() for p in trainable.values()),gpu_memory_allocated=int(torch.cuda.memory_allocated()))
  for epoch in spec["epochs"]:
   losses=[];epoch_started=time.time()
   for step in range(settings["iters_per_epoch"]):
    try:batch=next(iterator)
    except StopIteration:iterator=iter(loader);batch=next(iterator)
    require(batch["labels"].shape[1]<=settings["certified_actual_max_tokens"],"Actual batch context exceeds the certified no-GC memory envelope")
    require(all(not r["fallback"] or r["graph_tokens"]==0 for r in batch["prompt_info"]),"Fallback evidence contract violated")
    if not smoke_passed and step<2:
     atomic_json(output/f"first_batch_{step}.json",dict(sample_ids=batch["sample_ids"],prompt_info=batch["prompt_info"],shape=list(batch["input_ids"].shape),supervised_tokens=[int((r!=-100).sum()) for r in batch["labels"]],graph_tokens_masked_from_loss=True))
    batch=to_device(batch,torch.device("cuda:0"))
    with torch.amp.autocast("cuda",dtype=torch.float16):
     if auxiliary is None:
      loss=model(batch)["loss"];loss_report=dict(generation_loss=float(loss.detach().float()),polarity_loss=0.0,polarity_weight=0.0,polarity_valid_samples=0)
     else:
      loss,polarity_loss,loss_report=auxiliary.forward(batch)
    if auxiliary is not None and not auxiliary.smoke_checked and loss_report["polarity_valid_samples"]:
     grads=torch.autograd.grad(polarity_loss,[probe,model.polarity_head.weight],retain_graph=True)
     require(all(bool(torch.isfinite(g).all()) and bool(torch.count_nonzero(g)) for g in grads),"Polarity loss must update both existing LoRA and new head")
     atomic_json(output/"polarity_gradient_smoke.json",dict(passed=True,polarity_loss=loss_report["polarity_loss"],loss_weight=auxiliary.weight,existing_lora_parameter=probe_name,lora_gradient_norm=float(grads[0].float().norm()),head_gradient_norm=float(grads[1].float().norm()),pooling="last unsupervised prompt position",positions=loss_report["prompt_positions"],no_answer_token_pooling=True,ignored_samples_skip_only_polarity_loss=True))
     auxiliary.smoke_checked=True;del grads
    require(bool(torch.isfinite(loss)),"Non-finite training loss")
    scale_before=scaler.get_scale();scaler.scale(loss).backward();scaler.step(optimizer);scaler.update();optimizer.zero_grad(set_to_none=True)
    successful=scaler.get_scale()>=scale_before;optimizer_updates+=int(successful);skipped+=int(not successful)
    value=float(loss.detach().float());losses.append(value);completed+=1
    row=dict(time_beijing=now(),epoch=epoch,epoch_step=step+1,global_additional_step=completed,loss=value,learning_rate=optimizer.param_groups[0]["lr"],optimizer_step_applied=successful,grad_scaler=scaler.get_scale(),sequence_tokens=int(batch["input_ids"].shape[1]),sample_ids=batch["sample_ids"],prompt_info=batch["prompt_info"])
    row.update(loss_report)
    metrics_file.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+"\n")
    if not smoke_passed and optimizer_updates>=2:
     changed=not torch.equal(initial_probe,probe.detach());require(changed,"No LoRA parameter update after successful optimizer steps")
     smoke_passed=True
     atomic_json(output/"smoke_report.json",dict(passed=True,finite_forward_backward=True,successful_optimizer_updates=optimizer_updates,restored_optimizer=True,changed_parameter=probe_name,changed_parameter_maximum_absolute_difference=float((initial_probe-probe.detach()).abs().max()),graph_evidence_present=any(x["graph_tokens"]>0 for x in batch["prompt_info"]),batch_size=settings["batch_size"],actual_sequence_tokens=int(batch["input_ids"].shape[1]),counted_within_requested_25000_iterations=True))
     del initial_probe
    require(completed<50 or smoke_passed,"No successful optimizer progress within first 50 iterations")
    if completed%10==0 or completed<=3:
     elapsed=time.time()-started;update(state="training",current_epoch=epoch,epoch_step=step+1,completed_steps=completed,optimizer_updates=optimizer_updates,amp_skipped_steps=skipped,last_loss=value,mean_loss_current_epoch=math.fsum(losses)/len(losses),elapsed_training_seconds=elapsed,seconds_per_step=elapsed/completed,smoke_passed=smoke_passed,gpu_memory_allocated=int(torch.cuda.memory_allocated()),gpu_memory_peak=int(torch.cuda.max_memory_allocated()),gpu_memory_reserved=int(torch.cuda.memory_reserved()))
     print(json.dumps(dict(epoch=epoch,step=step+1,completed_steps=completed,loss=value,optimizer_updates=optimizer_updates,smoke_passed=smoke_passed)),flush=True)
    if auxiliary is not None:auxiliary.release();del polarity_loss
    del batch,loss
   require(smoke_passed,"GPU smoke test did not pass")
   require(auxiliary is None or auxiliary.smoke_checked,"Polarity gradient verification missing")
   stats=dict(loss=math.fsum(losses)/len(losses),iterations=len(losses),epoch_seconds=time.time()-epoch_started)
   metadata=dict(config["amg_finetune"],base_epoch=args.base_epoch,additional_epoch=epoch-args.base_epoch,additional_steps=completed,training_members_digest=plan["training_ids_digest"],audit_excluded=True)
   saved=save_checkpoint(model,optimizer,scaler,config,epoch,stats,output,metadata);checkpoints.append(saved)
   atomic_json(output/"checkpoints.json",checkpoints)
   update(completed_epochs=epoch-args.base_epoch,checkpoints=checkpoints)
  metrics_file.close();require(completed==25000 and status["completed_epochs"]==5,"Continuation did not complete exactly five epochs")
  update(state="complete",completed_steps=completed,finished_at_beijing=now(),elapsed_training_seconds=time.time()-started)
 except Exception as exc:
  update(state="failed",error=type(exc).__name__+": "+str(exc),traceback=traceback.format_exc());raise
if __name__=="__main__":main()

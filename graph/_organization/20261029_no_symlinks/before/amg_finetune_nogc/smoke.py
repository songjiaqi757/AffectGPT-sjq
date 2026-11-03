"""Real original-checkpoint GPU update on three cached training members; no checkpoint overwrite."""
import os,sys,time,copy,traceback
from pathlib import Path
import torch
from amg_runtime.common import read,sha,atomic_json,require
from .common import ROOT,load_plan,now
from .train_worker import build_optimizer,to_device

def main():
 run=Path(read(ROOT/"amg_finetune/runs/current.json")["path"]);plan=load_plan(run);started=time.time()
 path=run/"gpu_smoke_report.json"
 try:
  os.chdir(ROOT/"AffectGPT");sys.path.insert(0,str(ROOT/"AffectGPT"))
  from omegaconf import OmegaConf
  from my_affectgpt.models.affectgpt import AffectGPT
  from .dataset import GraphContinueDataset
  torch.manual_seed(42);torch.set_num_threads(4);torch.backends.cudnn.benchmark=False
  cfg=OmegaConf.create(read(run/"original_config.json")["model"]);cfg.max_length=2048;cfg.ckpt="";cfg.ckpt_2="";cfg.ckpt_3=""
  spec=plan["checkpoints"][0];checkpoint=torch.load(spec["path"],map_location="cpu",weights_only=True)
  model=AffectGPT.from_config(cfg);trainable={n:p for n,p in model.named_parameters() if p.requires_grad}
  result=model.load_state_dict(checkpoint["model"],strict=False);require(not result.unexpected_keys and not (set(result.missing_keys)&set(trainable)),"Incomplete trainable restoration")
  for name,p in trainable.items():require(torch.equal(p.detach().cpu(),checkpoint["model"][name]),"Weight restoration mismatch")
  model.to("cuda:0");model.train()
  model.llama_model.gradient_checkpointing_disable();model.llama_model.config.use_cache=False
  require(not model.llama_model.is_gradient_checkpointing,"No-GC preflight unexpectedly enabled gradient checkpointing")
  require(not [n for n,m in model.named_modules() if getattr(m,"gradient_checkpointing",False) is True],"A model submodule still has gradient checkpointing enabled")
  optimizer,names=build_optimizer(model,plan["training"]);optimizer.load_state_dict(checkpoint["optimizer"])
  scaler=torch.amp.GradScaler("cuda");scaler.load_state_dict(checkpoint["scaler"]);del checkpoint
  lengths=[]
  with (Path(plan["cache_source_run"])/"cache_inventory.jsonl").open() as f:
   for line in f:
    row=__import__("json").loads(line);task=row["tasks"]["description"];lengths.append((task["prompt_tokens"]+task["answer_tokens"]+2,row["sample_id"]))
  ids=[sid for length,sid in sorted(lengths,reverse=True)[:3]];require(len(ids)==3,"Need three maximum-length accepted cached examples")
  dataset=GraphContinueDataset(run,cfg,subset_ids=ids);dataset.label_type_candidates=["description","description"];items=[dataset[i] for i in range(3)];batch=dataset.collater(items)
  for info in batch["prompt_info"]:require(info["graph_tokens"]>0,"Smoke sample lacks graph evidence")
  name=next(n for n in trainable if "lora_B" in n);parameter=model.get_parameter(name);before=parameter.detach().clone()
  batch=to_device(batch,torch.device("cuda:0"));steps=[];updates=0
  for i in range(10):
   optimizer.zero_grad(set_to_none=True)
   with torch.amp.autocast("cuda",dtype=torch.float16):loss=model(batch)["loss"]
   require(bool(torch.isfinite(loss)),"Non-finite GPU smoke loss")
   scale=scaler.get_scale();scaler.scale(loss).backward();scaler.step(optimizer);scaler.update()
   updates+=int(scaler.get_scale()>=scale);steps.append(dict(iteration=i+1,loss=float(loss.detach().float()),scale=scaler.get_scale(),updates=updates))
   print(steps[-1],flush=True)
   if updates>=2:break
  require(updates>=2 and not torch.equal(before,parameter.detach()),"GPU smoke produced no optimizer update")
  # Maximum planned context stress test; synthetic suffix is unsupervised and no step is applied.
  optimizer.zero_grad(set_to_none=True)
  del loss
  torch.cuda.empty_cache()
  actual_tokens=int(batch["input_ids"].shape[1]);stress_tokens=plan["training"]["certified_actual_max_tokens"];padding=stress_tokens-actual_tokens
  require(padding>=0,"Real sample already exceeds context limit")
  filler=dataset.tokenizer.encode("test",add_special_tokens=False)[0]
  stress=dict(batch)
  stress["input_ids"]=torch.cat([batch["input_ids"],torch.full((3,padding),filler,dtype=torch.long,device="cuda")],dim=1)
  stress["labels"]=torch.cat([batch["labels"],torch.full((3,padding),-100,dtype=torch.long,device="cuda")],dim=1)
  stress["attention_masks"]=torch.cat([batch["attention_masks"],torch.ones((3,padding),dtype=torch.bool,device="cuda")],dim=1)
  torch.cuda.reset_peak_memory_stats()
  with torch.amp.autocast("cuda",dtype=torch.float16):stress_loss=model(stress)["loss"]
  require(bool(torch.isfinite(stress_loss)),"Non-finite maximum-context stress loss")
  scaler.scale(stress_loss).backward()
  stress_report=dict(passed=True,batch_size=3,sequence_tokens=stress_tokens,finite_loss=float(stress_loss.detach().float()),peak_gpu_memory_allocated=int(torch.cuda.max_memory_allocated()),peak_gpu_memory_reserved=int(torch.cuda.max_memory_reserved()),gradient_checkpointing_active=model.llama_model.is_gradient_checkpointing,synthetic_suffix_masked_from_loss=True,optimizer_step_applied=False)
  optimizer.zero_grad(set_to_none=True)
  report=dict(passed=True,maximum_context_stress=stress_report,llm_gradient_checkpointing=False,completed_at_beijing=now(),base_epoch=30,base_checkpoint_sha256=spec["sha256"],sample_ids=ids,actual_sequence_tokens=int(batch["input_ids"].shape[1]),graph_prompt_info=batch["prompt_info"],steps=steps,trainable_parameter_updated=name,max_absolute_parameter_change=float((before-parameter.detach()).abs().max()),peak_gpu_memory_allocated=int(torch.cuda.max_memory_allocated()),optimizer_and_scaler_restored=True,original_checkpoint_unchanged=sha(spec["path"])==spec["sha256"],elapsed_seconds=time.time()-started,semantics="Disposable preflight update only; requested five-epoch experiments start separately from original checkpoints")
  atomic_json(path,report);print(report,flush=True)
 except Exception as exc:atomic_json(path,dict(passed=False,error=type(exc).__name__+": "+str(exc),traceback=traceback.format_exc()));raise
if __name__=="__main__":main()

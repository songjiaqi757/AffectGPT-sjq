"""Explicit CPU integration check against a real existing AffectGPT checkpoint.

Not part of unittest discovery; loads the full LLM. No optimizer is run.
"""
import argparse
import json
from pathlib import Path
import time
import torch
from .runtime import (DEFAULT_CONFIG, load_config, build_dataset, load_base,
                      sha256_file, validate_bank_metadata)
from .memory import MemoryBank
from .model import AMGAffectGPT

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline-checkpoint",required=True)
    p.add_argument("--memory-bank",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--config",default=str(DEFAULT_CONFIG))
    p.add_argument("--backward",action="store_true")
    args=p.parse_args(argv)
    if torch.cuda.is_available():
        raise RuntimeError("Set CUDA_VISIBLE_DEVICES= for this CPU-only validation")
    torch.set_num_threads(2)
    start=time.monotonic()
    cfg=load_config(args.config)
    validate_bank_metadata(args.memory_bank,cfg,allow_partial=True)
    dataset=build_dataset(cfg,args.manifest,evaluation=True)
    torch.manual_seed(42)
    batch=dataset.collater([dataset[0]])
    print("Media loaded",batch["clip_ids"],batch["input_ids"].shape,flush=True)
    base=load_base(cfg,args.baseline_checkpoint,"cpu").eval()
    with torch.no_grad():
        reference=base(batch)["loss"].float()
    print("Original loss",float(reference),flush=True)
    bank=MemoryBank.load(args.memory_bank)
    model=AMGAffectGPT(base,bank,memory_dropout=0.,train_peft=False).eval()
    with torch.no_grad():
        off=model(batch,memory_mode="off")
        on=model(batch)
    assert torch.isfinite(on["loss"]) and torch.isfinite(off["loss"])
    torch.testing.assert_close(reference,off["loss"].float(),atol=0,rtol=0)
    print("Original vs off exact match; on finite",flush=True)
    first=int((batch["labels"][0]!=-100).nonzero()[0])
    prompt=dict(batch)
    prompt["input_ids"]=batch["input_ids"][:,:first]
    prompt["attention_masks"]=batch["attention_masks"][:,:first]
    prompt.pop("labels")
    ids,trace=model.generate_samples(prompt,max_new_tokens=2,do_sample=False,
        pad_token_id=base.llama_tokenizer.pad_token_id,eos_token_id=base.llama_tokenizer.eos_token_id)
    grad_norm=None
    train_retrieved=None
    if args.backward:
        model.train()
        trained=model(batch)
        trained["loss"].backward()
        grads=[p.grad.detach().float().norm() for p in model.memory_adapter.parameters() if p.grad is not None]
        grad_norm=float(torch.stack(grads).norm()) if grads else 0.
        if not 0 < grad_norm < float("inf"):
            raise AssertionError("Real generation loss failed to reach Memory Adapter")
        train_retrieved=trained["retrieved_ids"]
        if batch["clip_ids"][0] in train_retrieved[0]:
            raise AssertionError("Self retrieval during training")
        print("Adapter real generation gradient",grad_norm,flush=True)
    result={"schema":"amg-m0-real-cpu-validation-v1","clip_ids":batch["clip_ids"],
        "baseline_checkpoint":str(Path(args.baseline_checkpoint).resolve()),
        "baseline_sha256":sha256_file(args.baseline_checkpoint),
        "bank_sha256":sha256_file(args.memory_bank),
        "original_loss":float(reference),"memory_off_loss":float(off["loss"]),
        "memory_on_loss":float(on["loss"]),"off_exact_match":True,
        "memory_enabled":on["memory_enabled"].tolist(),"retrieved_ids":on["retrieved_ids"],
        "generated_ids":ids.tolist(),"generation_trace":trace,"adapter_grad_norm":grad_norm,
        "training_retrieved_ids":train_retrieved,"elapsed_s":time.monotonic()-start,
        "note":"Untrained adapter smoke only; no optimizer, no performance claim, CPU float32"}
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__ == "__main__":
    main()

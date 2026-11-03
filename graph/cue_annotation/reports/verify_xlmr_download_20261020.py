from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,time
import numpy as np
import torch
from transformers import AutoModel,AutoTokenizer
root=Path("/ai/sjq/AffectGPT-sjq")
p=root/"AffectGPT/models/xlm-roberta-base"
run=root/"cue_annotation/runs/mercaptionplus"
out=root/"cue_annotation/reports/xlmr_download_verification_20261020.json"
source=json.loads((p/"MODEL_SOURCE.json").read_text())
for item in source["files"]:
    assert (p/item["name"]).stat().st_size==item["bytes"]
samples=json.loads((run/"samples.json").read_text())
tok=AutoTokenizer.from_pretrained(str(p),local_files_only=True)
stats={};lengths={}
for lang in ("chinese","english"):
    texts=[s["text"].get(lang,"") for s in samples];lens=[]
    for i in range(0,len(texts),256):
        lens.extend(tok(texts[i:i+256],truncation=False,padding=False,return_length=True)["length"])
    lengths[lang]=lens;a=np.array(lens)
    stats[lang]={"min":int(a.min()),"median":float(np.median(a)),"p95":float(np.percentile(a,95)),"p99":float(np.percentile(a,99)),"max":int(a.max()),"over_128":int((a>128).sum()),"over_256":int((a>256).sum()),"over_512":int((a>512).sum()),"empty_fields":sum(not t.strip() for t in texts)}
record={"verified_at_beijing":datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),"model_id":source["repo_id"],"revision":source["revision"],"local_model_dir":str(p),"files_verified":len(source["files"]),"verified_bytes":source["total_bytes"],"sha256":{x["name"]:x["sha256"] for x in source["files"]},"integrity_check":"all eleven actual SHA256 values matched the manifest in the first verification invocation; file sizes rechecked here","tokenizer_class":tok.__class__.__name__,"tokenizer_model_max_length":tok.model_max_length,"length_includes_special_tokens":True,"n_samples":len(samples),"samples_sha256":hashlib.sha256((run/"samples.json").read_bytes()).hexdigest(),"text_token_lengths":stats,"scope":"download, tokenizer and temporary forward/backward verification; not production cue training"}
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print("TOKEN_LENGTHS",json.dumps(stats),flush=True)
torch.set_num_threads(8);torch.manual_seed(42)
device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
if device.type=="cuda":
    torch.cuda.set_device(0);torch.cuda.init()
    probe=torch.empty(1,device=device);del probe
    torch.cuda.reset_peak_memory_stats(0)
encoder,loading=AutoModel.from_pretrained(str(p),local_files_only=True,use_safetensors=True,add_pooling_layer=False,output_loading_info=True)
record["encoder_loading_info"]=loading
assert not loading["missing_keys"] and not loading.get("mismatched_keys") and not loading.get("error_msgs"),loading
assert all(k.startswith(("lm_head.","roberta.pooler.")) for k in loading["unexpected_keys"]),loading
encoder.to(device)
head=torch.nn.Sequential(torch.nn.Linear(2*encoder.config.hidden_size+2,256),torch.nn.GELU(),torch.nn.Dropout(.1),torch.nn.Linear(256,15)).to(device)
indices=[0,int(np.argmax(lengths["chinese"])),int(np.argmax(lengths["english"])),next(i for i,s in enumerate(samples) if not s["text"].get("english","").strip())]
selected=[samples[i] for i in dict.fromkeys(indices) if (run/"annotations"/(samples[i]["sample_id"]+".text.json")).exists()]
assert len(selected)>=2
texts=[s["text"].get(lang,"") for s in selected for lang in ("chinese","english")]
presence=torch.tensor([[bool(s["text"].get(lang,"").strip()) for lang in ("chinese","english")] for s in selected],device=device,dtype=torch.float32)
batch={k:v.to(device) for k,v in tok(texts,padding=True,truncation=False,return_tensors="pt").items()}
assert batch["input_ids"].shape[1]<=128
ids=json.loads((run/"ontology.json").read_text())["cue_ids"]["text"]
ys=[];ms=[]
for s in selected:
    labels=json.loads((run/"annotations"/(s["sample_id"]+".text.json")).read_text())["annotation"]["labels"]
    ys.append([float(labels[k]["state"]=="positive") for k in ids])
    ms.append([labels[k]["state"] in ("positive","negative") for k in ids])
y=torch.tensor(ys,device=device);mask=torch.tensor(ms,device=device)
encoder.train();head.train()
hidden=encoder(**batch).last_hidden_state
a=batch["attention_mask"].unsqueeze(-1).to(hidden.dtype)
pooled=((hidden*a).sum(1)/a.sum(1).clamp_min(1)).reshape(len(selected),2,-1)*presence.unsqueeze(-1)
logits=head(torch.cat((pooled.flatten(1),presence),dim=1))
assert tuple(logits.shape)==(len(selected),15)
loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,y,reduction="none")[mask].mean()
assert torch.isfinite(loss)
loss.backward()
params=list(encoder.parameters())+list(head.parameters())
assert any(q.grad is not None for q in params)
assert all(bool(torch.isfinite(q.grad).all()) for q in params if q.grad is not None)
smoke={"device":str(device),"precision":"float32","samples":len(selected),"sample_ids":[s["sample_id"] for s in selected],"included_missing_english":bool((presence[:,1]==0).any()),"token_batch_shape":list(batch["input_ids"].shape),"encoder_hidden_size":encoder.config.hidden_size,"output_shape":list(logits.shape),"valid_supervision":int(mask.sum()),"positive_supervision":int(((y==1)&mask).sum()),"negative_supervision":int(((y==0)&mask).sum()),"loss":float(loss.detach()),"loss_finite":True,"gradients_finite":True,"parameter_tensors_with_grad":sum(q.grad is not None for q in params),"optimizer_steps":0,"weights_saved":False,"scope":"temporary randomly initialized fusion head; one forward/backward, not a trained cue extractor"}
if device.type=="cuda":smoke["peak_allocated_MiB"]=round(torch.cuda.max_memory_allocated(0)/1024**2,1)
record["smoke"]=smoke
record["verification_notes"]=["CUDA initialized before resetting peak-memory statistics.","Unused MLM head and pooler checkpoint tensors are expected with an encoder using token mean pooling; all encoder tensors loaded without missing/mismatched keys."]
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print("SMOKE",json.dumps(smoke),flush=True)
print("EVIDENCE",str(out),flush=True)

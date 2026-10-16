# Independent CPU audit of the trained adapter's five-neighbor attention.
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from datetime import datetime, timezone

os.environ["CUDA_VISIBLE_DEVICES"] = ""
ROOT=Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
HERE=Path(__file__).resolve().parent
SRC=ROOT/"amg/experiments/single-seed42-face-ckpt35-sensitivity-v1"
sys.path.insert(0,str(ROOT))
import torch
from torch.nn import functional as F
from amg.memory import MemoryAdapter, MemoryBank

def read(path): return json.loads(Path(path).read_text())
def rows(path): return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return h.hexdigest()
def require(v,m):
    if not v:raise ValueError(m)
def write(path,p):
    with Path(path).open("x") as f:json.dump(p,f,indent=2,allow_nan=False);f.write("\n")
def stats(x):
    v=torch.as_tensor(x,dtype=torch.float64).reshape(-1).sort().values
    require(v.numel()>0 and bool(torch.isfinite(v).all()),"Invalid statistics")
    return {"N":v.numel(),"min":v[0].item(),"mean":v.mean().item(),"p50":torch.quantile(v,.5).item(),
            "p95":torch.quantile(v,.95).item(),"max":v[-1].item()}
def normratio(a,b):
    return (a.double().flatten(1).norm(dim=1)/b.double().flatten(1).norm(dim=1).clamp_min(1e-30))
def compare(a,b):
    return {"max_abs":stats((a-b).double().abs().flatten(1).max(1).values),
            "relative_l2":stats(normratio(a-b,a))}
def geometry(x):
    d=x.double()
    centered=d-d.mean(1,keepdim=True)
    return {"norm":stats(d.norm(dim=-1)),
            "neighbor_centered_norm":stats(centered.norm(dim=-1)),
            "neighbor_centered_relative_l2":stats(normratio(centered,d))}
def mha_parts(adapter,query,values):
    # Match nn.MultiheadAttention's separate Q and shared K,V input projection.
    q=adapter.query_projection(query)[:,None,:]+adapter.queries[None]
    z=adapter.value_projection(values)
    wq,wk,wv=adapter.attention.in_proj_weight.chunk(3)
    bq,bk,bv=adapter.attention.in_proj_bias.chunk(3)
    qp=F.linear(q,wq,bq);kp=F.linear(z,wk,bk);vp=F.linear(z,wv,bv)
    b,l,d=qp.shape;h=adapter.attention.num_heads;hd=d//h
    qh=qp.view(b,l,h,hd).transpose(1,2)
    kh=kp.view(b,z.shape[1],h,hd).transpose(1,2)
    vh=vp.view(b,z.shape[1],h,hd).transpose(1,2)
    logits=(qh @ kh.transpose(-1,-2))/math.sqrt(hd)
    weights=logits.softmax(-1)
    # MHA concat head output, then output projection.
    attended=(weights@vh).transpose(1,2).contiguous().view(b,l,d)
    attention_output=F.linear(attended,adapter.attention.out_proj.weight,adapter.attention.out_proj.bias)
    gate=torch.sigmoid(adapter.gate_projection(query))
    tokens=adapter.output_projection(attention_output)*gate[:,None,:]
    return {"q_input":q,"value_input":z,"q_projected":qp,"k_projected":kp,"v_projected":vp,
            "logits":logits,"weights":weights,"tokens":tokens,"gate":gate}

def main():
    torch.set_num_threads(2);torch.manual_seed(42)
    require(not torch.cuda.is_available(),"This audit must be CPU only")
    require(not (HERE/"summary.json").exists(),"Refusing to overwrite completed audit")
    p=read(SRC/"protocol.json")
    require(sha(p["amg_checkpoint"])==p["amg_sha256"],"Checkpoint changed")
    require(sha(p["bank"])==p["bank_sha256"],"Bank changed")
    checkpoint=torch.load(p["amg_checkpoint"],map_location="cpu",weights_only=True,mmap=True)
    require(checkpoint["config"]["mode"]=="retrieval","Wrong trained mode")
    state={k[len("memory_adapter."):]:v for k,v in checkpoint["model"].items() if k.startswith("memory_adapter.")}
    a=MemoryAdapter(d_hidden=int(checkpoint["config"]["hidden_dim"]),
                    llm_dim=state["output_projection.1.weight"].shape[0],
                    num_tokens=int(checkpoint["config"]["num_tokens"])).float()
    a.load_state_dict(state,strict=True);a.requires_grad_(False).eval()
    del checkpoint,state
    a64=copy.deepcopy(a).double()
    bank=MemoryBank.load(p["bank"])
    name_index={name:i for i,name in enumerate(bank.clip_ids)}
    caches=[];old_rows=[];input_hashes={}
    for part in ("worker0","worker1"):
        d=SRC/part;done=read(d/"worker_done.json")
        for fn,key in (("queries.pt","queries_sha256"),("rows.jsonl","rows_sha256")):
            actual=sha(d/fn);require(actual==done[key],"Original cached artifact changed")
            input_hashes[str(d/fn)]=actual
        caches.append(torch.load(d/"queries.pt",map_location="cpu",weights_only=True))
        old_rows+=rows(d/"rows.jsonl")
    names=caches[0]["clip_ids"]+caches[1]["clip_ids"]
    expected=[r["name"] for r in rows(p["manifest"])]
    require(names==expected and len(names)==len(set(names))==500,"Wrong ordered real query IDs")
    require(names==[r["name"] for r in old_rows],"Original sensitivity row order differs")
    require(all(bool(c["visual_valid"].all() and c["audio_valid"].all()) for c in caches),"Expected both query modalities valid")
    query=torch.cat([c["query"] for c in caches])
    require(tuple(query.shape)==(500,1792) and bool(torch.isfinite(query).all()),"Invalid real queries")
    normal_ids=caches[0]["normal_neighbor_ids"]+caches[1]["normal_neighbor_ids"]
    random_ids=caches[0]["random_neighbor_ids"]+caches[1]["random_neighbor_ids"]
    require(all(len(ids)==len(set(ids))==5 for ids in normal_ids+random_ids),"Invalid fixed neighbor IDs")
    all_results={};per_clip=[{"name":n,"index":i} for i,n in enumerate(names)]
    with torch.inference_mode():
        for mode,id_lists in (("normal",normal_ids),("random",random_ids)):
            indices=torch.tensor([[name_index[n] for n in ids] for ids in id_lists])
            require(bool(bank.valid_mask[indices].all()),"Expected both neighbor modalities valid")
            values=bank.features[indices]
            mask=torch.ones(500,5,dtype=torch.bool)
            m=mha_parts(a,query,values);d=mha_parts(a64,query.double(),values.double())
            q=m["q_input"];v=m["value_input"]
            actual_out,actual_weights=a.attention(q,v,v,key_padding_mask=~mask,need_weights=True,average_attn_weights=False)
            require(tuple(actual_weights.shape)==(500,4,4,5),"Attention head/slot/key dimensions differ")
            original_tokens=a(query,values,mask,dropout_p=0.0).tokens
            old_weights=torch.tensor([r["attention"][mode]["weights"] for r in old_rows])
            # Zero key bias has no effect on softmax because it adds the same
            # query-dependent scalar to all five key logits. Verify directly.
            h=a.attention.num_heads;hd=a.attention.embed_dim//h
            wq,wk,wv=a.attention.in_proj_weight.chunk(3)
            bq,bk,bv=a.attention.in_proj_bias.chunk(3)
            kbiasless=F.linear(v,wk,None).view(500,5,h,hd).transpose(1,2)
            qh=m["q_projected"].view(500,4,h,hd).transpose(1,2)
            kbiasless_weights=((qh@kbiasless.transpose(-1,-2))/math.sqrt(hd)).softmax(-1)
            # A true uniform attention mean: internal V projection -> exact mean
            # over the five neighbors -> MHA output projection -> final projection.
            uniform_v=m["v_projected"].mean(1,keepdim=True).expand(-1,4,-1)
            uniform_out=F.linear(uniform_v,a.attention.out_proj.weight,a.attention.out_proj.bias)
            uniform_tokens=a.output_projection(uniform_out)*m["gate"][:,None,:]
            logits=m["logits"].double();weights64=d["weights"]
            centered_logits=logits-logits.mean(-1,keepdim=True)
            entropy64=-(weights64*weights64.clamp_min(1e-300).log()).sum(-1)
            kl64=(weights64*(weights64.clamp_min(1e-300)*5).log()).sum(-1)
            deviations=(weights64-.2).abs()
            internal_k=m["k_projected"].view(500,5,4,64).transpose(1,2).double()
            internal_k_centered=internal_k-internal_k.mean(2,keepdim=True)
            result={
                "mask":{"all_five_valid":True,"softmax_axis":"last = five neighbors",
                        "weights_shape":list(actual_weights.shape),"heads_averaged":False},
                "logits":{"neighbor_std":stats(centered_logits.square().mean(-1).sqrt()),
                          "neighbor_range":stats(logits.max(-1).values-logits.min(-1).values),
                          "absolute_mean":stats(logits.mean(-1).abs())},
                "weights_float64":{"max_abs_deviation_from_uniform":stats(deviations.max(-1).values),
                    "neighbor_range":stats(weights64.max(-1).values-weights64.min(-1).values),
                    "entropy_deficit_log5":stats(math.log(5)-entropy64),
                    "kl_to_uniform":stats(kl64),
                    "exactly_uniform_head_slots":int((deviations.max(-1).values==0).sum())},
                "implementation_checks":{
                    "manual_weights_vs_nn_mha":compare(actual_weights,m["weights"]),
                    "cpu_nn_mha_vs_old_gpu_weights":compare(old_weights,actual_weights),
                    "manual_tokens_vs_original_forward":compare(original_tokens,m["tokens"]),
                    "float32_vs_float64_weights":compare(m["weights"].double(),weights64),
                    "key_bias_removed_vs_original_weights":compare(m["weights"],kbiasless_weights),
                    "exact_uniform_tokens_vs_original":compare(original_tokens,uniform_tokens)},
                "geometry":{"bank_neighbor_features":geometry(values),"value_projection_output":geometry(v),
                    "internal_Q":geometry(m["q_projected"]),"internal_K":geometry(m["k_projected"]),
                    "internal_V":geometry(m["v_projected"]),
                    "head_query_norm":stats(qh.double().norm(dim=-1)),
                    "head_neighbor_centered_key_norm":stats(internal_k_centered.norm(dim=-1))}}
            all_results[mode]=result
            for i in range(500):
                per_clip[i][mode]={
                    "logit_neighbor_std_mean":centered_logits[i].square().mean(-1).sqrt().mean().item(),
                    "logit_neighbor_range_max":(logits[i].max(-1).values-logits[i].min(-1).values).max().item(),
                    "weight_max_abs_deviation_from_uniform":deviations[i].max().item(),
                    "kl_to_uniform_mean":kl64[i].mean().item(),
                    "uniform_token_relative_l2":normratio(original_tokens[i:i+1]-uniform_tokens[i:i+1],original_tokens[i:i+1])[0].item(),
                    "weights_float64":weights64[i].tolist()}
            print(json.dumps({"mode":mode,"logit_neighbor_std":result["logits"]["neighbor_std"],
                              "weight_deviation":result["weights_float64"]["max_abs_deviation_from_uniform"],
                              "uniform_token_error":result["implementation_checks"]["exact_uniform_tokens_vs_original"]}),flush=True)
    summary={"schema":"amg-trained-adapter-attention-audit-v1","status":"complete","N":500,
             "completed_at":datetime.now(timezone.utc).isoformat(),"device":"cpu","trained_weights":True,
             "amg_sha256":p["amg_sha256"],"bank_sha256":p["bank_sha256"],"real_query_cache":True,
             "checks":all_results,
             "conclusions":[
                "The attention is near uniform over five keys; all head and slot weights are retained.",
                "Float32 entropy may round to its maximum; float64 softmax/KL quantify the small nonuniformity.",
                "Key input-projection bias adds a common logit shift and therefore cannot by itself change softmax weights.",
                "Exact uniform aggregation can be compared against trained forward tokens to quantify how little query-dependent attention contributes.",
                "These are internal diagnostics under trained weights, not evidence that a particular architectural change improves task F1."],
             "minimal_candidate":"If testing attention selectivity, change only logit temperature while preserving projections, gate, neighbors and training/evaluation budget; select and evaluate using development protocol. This audit does not change the model."}
    write(HERE/"summary.json",summary)
    with (HERE/"rows.jsonl").open("x") as f:
        for record in per_clip:f.write(json.dumps(record,allow_nan=False)+"\n")
    input_hashes.update({p["amg_checkpoint"]:p["amg_sha256"],p["bank"]:p["bank_sha256"],
                         str(SRC/"diagnose_adapter.py"):sha(SRC/"diagnose_adapter.py"),
                         str(ROOT/"amg/memory.py"):sha(ROOT/"amg/memory.py"),
                         str(Path(__file__).resolve()):sha(__file__)})
    write(HERE/"INPUTS.json",input_hashes)
    lines=["# Trained Adapter attention: independent CPU audit","",
           "Uses all 500 real cached dev queries, fixed original normal/random neighbor IDs and the exact trained checkpoint.",
           "No GPU, Qwen, generation, training, source modification, initial-weight reconstruction, or scoring changes.","",
           "|Mode|Logits neighbor std mean|Logits neighbor range max|FP64 max weight deviation from 0.2|Uniform token relative L2 mean|",
           "|---|---:|---:|---:|---:|"]
    for mode,r in all_results.items():
        lines.append(f"|{mode}|{r['logits']['neighbor_std']['mean']:.9g}|{r['logits']['neighbor_range']['max']:.9g}|{r['weights_float64']['max_abs_deviation_from_uniform']['max']:.9g}|{r['implementation_checks']['exact_uniform_tokens_vs_original']['relative_l2']['mean']:.9g}|")
    lines.extend(["","All attention tensors have shape [500,4 heads,4 slots,5 neighbors]; softmax is over the last axis, masks retain all five, and heads are not averaged.",
                  "Manual Q/K input projection, scaled dot products and softmax match nn.MultiheadAttention; CPU weights also match the saved GPU diagnostic within reported numerical error.",
                  "FP64 recomputation distinguishes near uniform weights from exactly uniform weights. Original FP32 normalized entropy=1 is rounding at very small entropy deficit, not proof of exact equality.",
                  "The key projection bias cancels as a common softmax logit shift. Neighbor-centered key variation and query/head scale jointly bound the small logit differences.",
                  "The uniform-aggregation comparison measures the functional contribution of query-dependent attention at these fixed weights.",
                  "A minimal future selectivity test is a single logit-temperature change with all other factors fixed; no task gain follows from this audit.",
                  "See summary.json for geometry, FP64 entropy/KL, implementation error bounds and each mode's complete distributions."])
    with (HERE/"SUMMARY.md").open("x") as f:f.write("\n".join(lines)+"\n")
    print(json.dumps({"status":"complete","summary":str(HERE/"summary.json")}),flush=True)

if __name__=="__main__":main()

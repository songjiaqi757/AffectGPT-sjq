"""CPU-only layer/bias diagnostics on the saved 500 real dev queries."""
from pathlib import Path
import sys,json,hashlib,math,datetime
ROOT=Path("/ai/sjq/AffectGPT-sjq/AffectGPT")
sys.path.insert(0,str(ROOT))
import torch
import torch.nn.functional as F
from amg.memory import MemoryAdapter,MemoryBank
torch.set_num_threads(2)
BASE=ROOT/"amg/experiments"
S=BASE/"single-seed42-face-ckpt35-sensitivity-v1"
OUT=BASE/"single-seed42-face-ckpt35-adapter-audit-v1/layer-audit"
OUT.mkdir(parents=True,exist_ok=False)
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest()
def rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def write(name,o):
 with (OUT/name).open("x") as f:json.dump(o,f,ensure_ascii=False,indent=2,allow_nan=False);f.write("\n")
def dist(v):
 v=v.detach().float().reshape(-1)
 assert torch.isfinite(v).all()
 a=v.sort().values
 return {"mean":float(a.mean()),"p05":float(torch.quantile(a,.05)),"p50":float(torch.quantile(a,.5)),"p95":float(torch.quantile(a,.95)),"max":float(a.max()),"min":float(a.min())}
def pair(a,b):
 a,b=a.float().reshape(500,-1),b.float().reshape(500,-1)
 return {"cosine":dist(F.cosine_similarity(a,b,dim=-1)),"relative_l2":dist((a-b).norm(dim=-1)/a.norm(dim=-1).clamp_min(1e-12)),"left_norm":dist(a.norm(dim=-1)),"right_norm":dist(b.norm(dim=-1))}
def geom(x):
 x=x.float().reshape(-1,x.shape[-1]);m=x.mean(0)
 return {"mean_vector_norm":float(m.norm()),"mean_row_norm":float(x.norm(dim=-1).mean()),"common_energy_fraction":float((m.square().sum()/x.square().sum(-1).mean()).clamp(0,1)),"centered_rms":float((x-m).square().mean().sqrt()),"raw_rms":float(x.square().mean().sqrt())}
p=read(S/"protocol.json"); ready=read(S/"READY.json")["locked_files"]
for f in [ROOT/"amg/memory.py",Path(p["amg_checkpoint"]),Path(p["bank"]),Path(p["manifest"])]:
 assert sha(f)==ready[str(f)]
caches=[]
for name in ["worker0","worker1"]:
 d=S/name;done=read(d/"worker_done.json")
 assert sha(d/"queries.pt")==done["queries_sha256"]
 caches.append(torch.load(d/"queries.pt",weights_only=True,map_location="cpu"))
names=caches[0]["clip_ids"]+caches[1]["clip_ids"]
assert names==[r["name"] for r in rows(p["manifest"])] and len(set(names))==500
query=torch.cat([c["query"] for c in caches])
assert all(c["visual_valid"].all() and c["audio_valid"].all() for c in caches)
nids=caches[0]["normal_neighbor_ids"]+caches[1]["normal_neighbor_ids"]
rids=caches[0]["random_neighbor_ids"]+caches[1]["random_neighbor_ids"]
bank=MemoryBank.load(p["bank"]);lookup={x:i for i,x in enumerate(bank.clip_ids)}
n=bank.features[torch.tensor([[lookup[x] for x in ids] for ids in nids])]
r=bank.features[torch.tensor([[lookup[x] for x in ids] for ids in rids])]
checkpoint=torch.load(p["amg_checkpoint"],map_location="cpu",weights_only=True,mmap=True)
cfg=checkpoint["config"]
state={k.removeprefix("memory_adapter."):v for k,v in checkpoint["model"].items() if k.startswith("memory_adapter.")}
a=MemoryAdapter(d_hidden=cfg["hidden_dim"],num_tokens=cfg["num_tokens"],llm_dim=3584).eval().requires_grad_(False)
a.load_state_dict(state,strict=True)
del checkpoint,state
mask=torch.ones(500,5,dtype=torch.bool)
with torch.inference_mode():
 gate=torch.sigmoid(a.gate_projection(query))
 nq=a(query,n,mask,dropout_p=0);rq=a(query,r,mask,dropout_p=0)
 q=a.query_projection(query)[:,None,:]+a.queries[None]
 def layers(x):
  z1=F.linear(x,a.value_projection[0].weight,None)
  z2=z1+a.value_projection[0].bias
  z3=F.gelu(z2)
  z4=F.linear(z3,a.value_projection[2].weight,None)
  z5=z4+a.value_projection[2].bias
  return {"input":x,"linear1_no_bias":z1,"linear1_with_bias":z2,"gelu":z3,"linear2_no_bias":z4,"linear2_with_bias":z5}
 nl,rl=layers(n),layers(r)
 stage={k:pair(nl[k].mean(1),rl[k].mean(1)) for k in nl}
 stages_geometry={k:geom(v) for k,v in layers(bank.features).items()}
 signals={}
 for idx,pre in [(0,"linear1_no_bias"),(2,"linear2_no_bias")]:
  signals[str(idx)]={"bias_norm":float(a.value_projection[idx].bias.norm()),"weight_frobenius":float(a.value_projection[idx].weight.norm()),"normal_signal_norm":dist(nl[pre].norm(dim=-1)),"random_signal_norm":dist(rl[pre].norm(dim=-1))}
 def attend(qin,nv,rv):
  no,_=a.attention(qin,nv,nv,key_padding_mask=~mask,need_weights=False)
  ro,_=a.attention(qin,rv,rv,key_padding_mask=~mask,need_weights=False)
  _,nw=a.attention(qin,nv,nv,key_padding_mask=~mask,need_weights=True,average_attn_weights=False)
  _,rw=a.attention(qin,rv,rv,key_padding_mask=~mask,need_weights=True,average_attn_weights=False)
  nln,rln=a.output_projection[0](no),a.output_projection[0](ro)
  nt,rt=a.output_projection[1](nln)*gate[:,None,:],a.output_projection[1](rln)*gate[:,None,:]
  def attention(w):
   h=-(w*w.clamp_min(1e-30).log()).sum(-1)/math.log(5)
   return {"entropy_normalized":dist(h),"max_weight":dist(w.max(-1).values),"max_minus_min":dist(w.max(-1).values-w.min(-1).values)}
  return {"attention_output":pair(no,ro),"after_layernorm":pair(nln,rln),"tokens":pair(nt,rt),"normal_attention":attention(nw),"random_attention":attention(rw)},nt,rt
 orig,nt,rt=attend(q,nl["linear2_with_bias"],rl["linear2_with_bias"])
 fidelity={"normal_max_abs_error":float((nt-nq.tokens).abs().max()),"random_max_abs_error":float((rt-rq.tokens).abs().max())}
 assert fidelity["normal_max_abs_error"]<2e-6 and fidelity["random_max_abs_error"]<2e-6
 variants={}
 # These are internal counterfactual probes; they do not establish generation gains.
 value_nob2=attend(q,nl["linear2_no_bias"],rl["linear2_no_bias"])[0]
 variants["remove_value_second_linear_bias_only"]=value_nob2
 def nobias(x):return F.linear(F.gelu(F.linear(x,a.value_projection[0].weight)),a.value_projection[2].weight)
 variants["remove_both_value_linear_biases"]=attend(q,nobias(n),nobias(r))[0]
 variants["layernorm_attention_inputs"]=attend(F.layer_norm(q,(256,)),F.layer_norm(nl["linear2_with_bias"],(256,)),F.layer_norm(rl["linear2_with_bias"],(256,)))[0]
 result={"schema":"amg-adapter-layer-cpu-audit-v1","created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"N":500,"real_queries":True,"same_trained_checkpoint":p["amg_sha256"],"source":str(Path(__file__).resolve()),"source_sha256":sha(__file__),"cpu_only":True,"no_training":True,"faithful_forward_error":fidelity,"value_stages":stage,"value_bank_geometry":stages_geometry,"value_linear_scales":signals,"original_attention_and_output":orig,"counterfactual_internal_probes":variants,"limitations":["CPU float32 replay of saved real dev features, not a new generation experiment.","Bias removals and normalization probes change computation without retraining; internal differentiation is not evidence of task improvement.","No exact random initialization reconstruction was attempted.","Stage comparisons use unordered-set means and may reflect both common bias and learned weighting, not a unique optimization history."]}
 write("summary.json",result)
 lines=["# Adapter layer and bias audit","","500 saved real dev queries; CPU only; same trained retrieval Adapter; no model or score changes.","",f"Forward replay error: {fidelity}","","|Value stage|Normal/random mean cosine|Relative L2|Common energy over full bank|","|---|---:|---:|---:|"]
 for k,v in stage.items():lines.append(f"|{k}|{v['cosine']['mean']:.8f}|{v['relative_l2']['mean']:.6f}|{stages_geometry[k]['common_energy_fraction']:.6f}|")
 lines.extend(["","|Internal probe|Token cosine|Token relative L2|Normal max attention weight|","|---|---:|---:|---:|"])
 for k,v in [("original",orig),*variants.items()]:lines.append(f"|{k}|{v['tokens']['cosine']['mean']:.8f}|{v['tokens']['relative_l2']['mean']:.6f}|{v['normal_attention']['max_weight']['mean']:.6f}|")
 lines.extend(["","These probes are mechanistic diagnostics; no generation quality or improvement is inferred.",
               "All model/source weights remain unchanged. See summary.json for geometry, linear bias scales and limitations."])
 (OUT/"SUMMARY.md").write_text("\n".join(lines)+"\n")
 print(json.dumps({"status":"complete","summary":str(OUT/"SUMMARY.md"),"forward_error":fidelity,"value_stages":{k:{"cos":v["cosine"]["mean"],"relL2":v["relative_l2"]["mean"]} for k,v in stage.items()}},ensure_ascii=False),flush=True)

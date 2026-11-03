"""CPU-only diagnostics of completed path/list intervention."""
import os,sys,json,runpy,collections,warnings,math
from pathlib import Path
os.environ["CUDA_VISIBLE_DEVICES"]=""
import numpy as np
from amg_d_graph_compare.common import ROOT,read,plan,canonical,atomic_json,sha,now
r=Path(read(ROOT/"amg_188_path_noemotion/current_run.json")["run"]);p=plan(r);out=r/"analysis"
assert read(r/"final_verification.json")["passed"],"Full scoring must finish first"
with warnings.catch_warnings():
 warnings.simplefilter("ignore",RuntimeWarning)
 h=runpy.run_path(str(ROOT/"analysis_reports/sample_audit_75_43_20261028/common.py"))
conds=["C","E","P","H"];pairs=[("H","C"),("H","P"),("E","C"),("P","E")]
L={(x["dataset"],x["condition"]):x for x in read(r/"metrics_all.json")}
active=collections.defaultdict(set)
for s in range(8):
 for x in read(r/"workers"/("tasks_"+str(s)+".json")):active[x["dataset"]].add(x["name"])
result=dict(created_at_beijing=now(),datasets={},all_path_counts=collections.Counter(),all_raw_contrasts=collections.defaultdict(collections.Counter),notes=["Active subset metrics are descriptive, not separately preregistered confirmatory tests.","Path-label coverage measures output adoption, not correctness or grounded reasoning.","H retains original path Emotion endpoints; it is not an Emotion-free condition."])
for d,di in p["datasets"].items():
 rows={x["name"]:x for x in read(di["path"])};A={c:h["arrays"](L[d,c]["raw_path"],d) for c in conds};raw={c:h["npdict"](L[d,c]["raw_path"]) for c in conds};names=A["C"]["names"]
 mask=np.array([n in active[d] for n in names]);ix=np.where(mask[A["C"]["valid"]] if "valid" in A["C"] else mask)[0]
 structure=collections.Counter();term_counts=[];list_counts=[];coverage={c:[0,0] for c in conds};external={c:[] for c in conds};contrasts={}
 for n in sorted(active[d]):
  row=rows[n];b=read(r/"prompt_cache"/(canonical(row["sample_id"])+".json"));pt=b["texts"]["P"];ht=b["texts"]["H"]
  assert ht=="\n".join(z for z in pt.splitlines() if not z.startswith("Emotion hypotheses: "))
  links=next(z.split(": ",1)[1] for z in ht.splitlines() if z.startswith("Supporting links: "))
  paths=[z.split(" -> ") for z in links.split("; ")];terms={z[-1] for z in paths};term_counts.append(len(terms))
  emoline=next(z.split(": ",1)[1] for z in pt.splitlines() if z.startswith("Emotion hypotheses: "))
  list_counts.append(len(emoline.split(", ")))
  for path in paths:structure[str(len(path)-1)+"_hop_paths"]+=1
  for w in range(5):
   t=h["mapped"](", ".join(sorted(terms)),w)
   for c in conds:
    z=h["mapped"](A[c]["opens"][n],w)
    coverage[c][0]+=len(z&t);coverage[c][1]+=len(t)
    if d in ["MER2023","MER2024","MELD","IEMOCAPFour","OVMERDPlus"]:
     gt=h["mapped"](h["refs"][d][n],w)
     if gt:external[c].append(len(z-gt))
 for c,b in pairs:
  key=c+"-"+b;changed=sum(raw[c][n]!=raw[b][n] for n in active[d]);opchanged=sum(A[c]["opens"][n]!=A[b]["opens"][n] for n in active[d])
  contrasts[key]=dict(active_samples=len(active[d]),raw_answer_changed=changed,raw_answer_changed_pct=100*changed/len(active[d]),extraction_changed=opchanged)
  result["all_raw_contrasts"][key].update(active_samples=len(active[d]),raw_answer_changed=changed,extraction_changed=opchanged)
 metrics={}
 for c in conds:
  z=dict(main_pct=100*float(h["metric"](A[c],d,ix)))
  if d in ["MER2023","MER2024","MELD","IEMOCAPFour"]:z["M_pct"]=100*float(h["metric"](A[c],d,ix,key="m"))
  if d=="OVMERDPlus":
   z.update(P_pct=100*float(np.nanmean(A[c]["prec"][ix],axis=0).mean()),R_pct=100*float(np.nanmean(A[c]["rec"][ix],axis=0).mean()))
  metrics[c]=z
 result["datasets"][d]=dict(active_samples=len(active[d]),scorable_active_samples=(len(ix) if d in ["CMUMOSI","CMUMOSEI","SIMS","SIMSv2"] else int(np.any(np.isfinite(A["C"]["hit"][ix]),axis=1).sum())),path_structure=dict(structure),mean_unique_path_emotions=float(np.mean(term_counts)),mean_list_emotions=float(np.mean(list_counts)),active_metrics=metrics,contrasts=contrasts,path_label_coverage={c:coverage[c][0]/coverage[c][1] if coverage[c][1] else None for c in conds},mean_reference_external_mapped_labels_active={c:float(np.mean(external[c])) if external[c] else None for c in conds})
 result["all_path_counts"].update(structure)
 print("DIAGNOSED",d,flush=True)
result["input_sha256"]={str(r/f):sha(r/f) for f in ["plan.json","metrics_all.json","final_verification.json","analysis/summary.json"]}
atomic_json(out/"ADDITIONAL_DIAGNOSTICS.json",result)
print(json.dumps({k:result[k] for k in ["all_path_counts","all_raw_contrasts"]},ensure_ascii=False),flush=True)

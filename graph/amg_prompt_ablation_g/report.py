"""G results with read-only references to the completed A-F experiment."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import csv,io,math
from .common import *
def summarize(run,p,final=False):
 rows=[read(f) for f in sorted((run/"scores").glob("*.json"))]
 out=[]
 for r in rows:out.append(dict(r,weight=p["weight_by_variant"][r["variant"]],ablation="G",**r["metrics"]))
 atomic_json(run/"metrics_all.json",out)
 buf=io.StringIO();fields=["weight","ablation","dataset","epoch","samples","main_metric","main_score","HIT","M","WAF","ACC","F_s","P_s","R_s","mean_extracted_labels","empty_extracted_labels"]
 w=csv.DictWriter(buf,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(out)
 temp=run/"metrics_all.csv.tmp";temp.write_text(buf.getvalue());temp.replace(run/"metrics_all.csv")
 source=Path(p["reference_run"]);original=read(source/"metrics_all.json")
 refs={(r["weight"],r["ablation"],r["dataset"]):r for r in original}
 deltas=[]
 for r in out:
  for c in ["A","B","C","E","F"]:
   ref=refs[(r["weight"],c,r["dataset"])]
   deltas.append(dict(weight=r["weight"],dataset=r["dataset"],comparison="G-"+c,
    delta_percentage_points={k:100*(v-ref["metrics"][k]) for k,v in r["metrics"].items() if k in ref["metrics"] and k not in ["mean_extracted_labels","empty_extracted_labels"]},
    reference_score=ref["job_id"],reference_plan_id=ref["plan_id"]))
 atomic_json(run/"paired_deltas.json",deltas)
 if len(rows)==p["logical_jobs"]:
  current={(r["weight"],r["dataset"]):r for r in out}
  lines=["# G: Cue + explicit-alternative Appraisal; no Emotion candidates","",
   "Two frozen weights. Same graph, gate, decoding and per-sample random stream as A-F. Existing unified evaluation pipeline unchanged.",
   "A-F values are read-only references from the completed experiment. G contains 1718 reused exact-prompt F answers and 1082 new answers.",
   "","|Weight|Condition|MER HIT|MER M|SIMS WAF|SIMS ACC|OV F|OV P|OV R|","|---|---|---:|---:|---:|---:|---:|---:|---:|"]
  for weight in p["weights"]:
   for c in ["A","B","C","D","E","F","G"]:
    def get(d):return current[(weight,d)] if c=="G" else refs[(weight,c,d)]
    m,s,o=[get(d)["metrics"] for d in ["MER2023","SIMS","OVMERDPlus"]]
    values=[m["HIT"],m["M"],s["WAF"],s["ACC"],o["F_s"],o["P_s"],o["R_s"]]
    lines.append("|"+weight+"|"+c+"|"+"|".join(f"{100*v:.3f}" for v in values)+"|")
  lines+=["","## Paired point differences",""]
  for d in deltas:lines.append(d["weight"]+" "+d["dataset"]+" "+d["comparison"]+": "+", ".join(k+f" {v:+.3f}" for k,v in d["delta_percentage_points"].items()))
  lines+=["","Exploratory target-test results. Point differences do not establish uncertainty or multi-seed robustness. No parameter training, graph fitting or target-driven prompt adjustment."]
  (run/"RESULTS.md").write_text("\n".join(lines)+"\n")
 if final:
  import numpy as np
  require(len(rows)==6 and complete_count(run)==6,"Incomplete G results")
  generated=reused=total=0
  for job in jobs(run):
   r=read(run/"scores"/(job["job_id"]+".json"))
   require(_graph_hash_matches(r['raw_path'], r['raw_sha256'], sha(r['raw_path'])),"Scored raw changed")
   require(r["checkpoint"]["sha256"]==p["checkpoint_by_variant"][job["variant"]]["sha256"],"Wrong checkpoint")
   values=np.load(_graph_resolve_path(r['raw_path']), allow_pickle=True)["name2reason"].item()
   require(len(values)==job["samples"],"Wrong prediction count")
   with Path(job["prediction_path"]).open() as f:
    for line in f:
     x=json.loads(line);require(x["plan_id"]==p["plan_id"] and x["prompt_info"]["ablation"]=="G","Invalid G provenance")
     require(x["prompt_info"]["emotion_candidates_displayed"]==0 and x["prompt_info"]["displayed_paths"]==0,"G field leak")
     reused+=int(x.get("reused",False));generated+=int(not x.get("reused",False));total+=1
  require((total,reused,generated)==(2800,1718,1082),"Wrong reuse/generation counts")
  atomic_json(run/"final_verification.json",dict(passed=True,total_predictions=total,reused_predictions=reused,new_predictions=generated,
   score_jobs=6,unified_original_evaluator_preserved=True,completed_at_beijing=now()))
 return len(rows)

import csv,io,math
from .common import *
def report(run,p):
 with lock(run/"comparison.lock",True):
  scores=[read(f) for f in (run/"scores").glob("*.json")]
  comparisons=[]
  for x in scores:
   key=str(x["base_epoch"]);d=x["dataset"];parent=p["parent_scores"][key][d];best=p["baseline_winners"][d]
   comparisons.append(dict(dataset=d,original_base=p["branch_origins"][key],parent_epoch=x["base_epoch"],epoch=x["epoch"],main_metric=x["main_metric"],main_score=x["main_score"],parent_score=parent["main_score"],delta_parent_pp=100*(x["main_score"]-parent["main_score"]),previous_best=best["main_score"],delta_best_pp=100*(x["main_score"]-best["main_score"])))
  winners=[]
  for d,b in p["baseline_winners"].items():
   xs=[x for x in comparisons if x["dataset"]==d];best=max(xs,key=lambda x:x["main_score"]) if xs else None
   winners.append(dict(dataset=d,previous_best=b["main_score"],new_best=best["main_score"] if best else None,retained_best=max(b["main_score"],best["main_score"]) if best else b["main_score"],new_checkpoint=best))
  prior=math.fsum(x["main_score"] for x in p["baseline_winners"].values())/9
  retained=math.fsum(x["retained_best"] for x in winners)/9
  complete=len(scores)==p["expected_inference_jobs"]
  write(run/"comparison_summary.json",dict(complete=complete,scored=len(scores),expected=p["expected_inference_jobs"],comparisons=comparisons,dataset_best=winners,previous_nine_dataset_best_mean=prior,retained_nine_dataset_best_mean=retained,delta_pp=100*(retained-prior),at=now()))
  fields=["dataset","original_base","parent_epoch","epoch","main_metric","main_score","parent_score","delta_parent_pp","previous_best","delta_best_pp"]
  rows=sorted(comparisons,key=lambda x:(x["original_base"],x["epoch"],x["dataset"]))
  stream=io.StringIO();w=csv.DictWriter(stream,fields);w.writeheader();w.writerows(rows)
  f=run/"paired_comparison.csv";f.with_suffix(".tmp").write_text(stream.getvalue());f.with_suffix(".tmp").replace(f)
  lines=["# Two additional logical epochs; corresponding datasets only","",f"Completed {len(scores)}/{p['expected_inference_jobs']} dataset evaluations.","","Frozen judge: temperature=0, top_p=1, repetition_penalty=1.05, max_tokens=512.","","|Original branch|Parent|Added epoch|Dataset|Score (%)|Parent (%)|Change (pp)|","|---:|---:|---:|---|---:|---:|---:|"]
  for x in rows:lines.append(f"|{x['original_base']}|{x['parent_epoch']}|{x['epoch']}|{x['dataset']}|{100*x['main_score']:.2f}|{100*x['parent_score']:.2f}|{x['delta_parent_pp']:+.2f}|")
  lines += ["",f"Previous dataset-wise best mean across nine datasets: {100*prior:.6f}%.",f"Retained best mean including these new artifacts: {100*retained:.6f}%.","Four datasets outside the assigned set keep their previous scores. Different dataset winners may use different checkpoints. New scores are single inference runs under the preserved stochastic generation settings."]
  f=run/"RESULTS.md";f.with_suffix(".tmp").write_text("\n".join(lines)+"\n");f.with_suffix(".tmp").replace(f)

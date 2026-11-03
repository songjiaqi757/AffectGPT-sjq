
"""Repository metric functions, fed globally consistent judge caches."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import sys,collections,csv,io,math
from .common import *
def judge_key(p,stage,text):return canonical(dict(protocol=p["judge_protocol_id"],stage=stage,input=text))
def npdict(path):
 import numpy as np
 z=np.load(_graph_resolve_path(path), allow_pickle=True)
 return z["name2reason"].item() if "name2reason" in z else dict(zip(z["filenames"].tolist(),z["fileitems"].tolist()))
def npwrite(path,**arrays):
 import numpy as np
 temp=Path(str(path)+".tmp")
 with temp.open("wb") as f:np.savez_compressed(_graph_resolve_path(f), **arrays)
 temp.replace(path)
def prepare(run,stage):
 run=Path(run);p=plan(run);items={}
 for j in jobs(run):
  if stage=="sentiment" and j["dataset"] not in POLARITY:continue
  for text in npdict(j["official_npz"]).values():
   if stage=="sentiment":text=read(run/"judge_cache"/"openset"/(judge_key(p,"openset",text)+".json"))["output"]
   k=judge_key(p,stage,text);items[k]=dict(key=k,text=text,seed=(20261028+int(k[:8],16))%2**32)
 values=[items[k] for k in sorted(items)];atomic_json(run/("judge_inputs_"+stage+".json"),values);return len(values)
def assemble(run):
 import numpy as np
 run=Path(run);p=plan(run);refs=read(run/"references.json")
 os.chdir(_graph_resolve_path(ROOT / 'AffectGPT'));sys.path.insert(0,str(ROOT/"AffectGPT"));import evaluation
 lock=read(run/"evaluation_resources.json")
 for f,digest in lock["files"].items():require(_graph_hash_matches(f, digest, sha(f)),"Evaluation resource drift")
 values=[];identical_answers={}
 for j in jobs(run):
  d=j["dataset"];v=j["variant"];raw=Path(j["official_npz"]);answers=npdict(raw);names=list(refs[d])
  require(set(answers)==set(names),"Prediction/truth membership mismatch")
  opens={n:read(run/"judge_cache"/"openset"/(judge_key(p,"openset",answers[n])+".json"))["output"] for n in names}
  for n in names:
   if answers[n] in identical_answers:require(identical_answers[answers[n]]==opens[n],"Identical answers received unequal extraction")
   identical_answers[answers[n]]=opens[n]
  op=raw.with_name(raw.stem+"-openset.npz");npwrite(op,filenames=names,fileitems=[opens[n] for n in names])
  if d in POLARITY:
   sent={n:read(run/"judge_cache"/"sentiment"/(judge_key(p,"sentiment",opens[n])+".json"))["output"] for n in names}
   npwrite(raw.with_name(raw.stem+"-openset-sentiment.npz"),filenames=names,fileitems=[sent[n] for n in names])
   value,acc=evaluation.calculate_dimension_zeroshot(str(raw),refs[d],None,None,None,False);ms=dict(WAF=float(value),ACC=float(acc));main="WAF"
  elif d in CATEGORICAL:
   value,m=evaluation.calculate_discrete_zeroshot(str(raw),refs[d],None,None,None,False);ms=dict(HIT=float(value),M=float(m));main="HIT"
  else:
   value,pre,rec=evaluation.calculate_ov_zeroshot(str(raw),refs[d],None,None,None,False);ms=dict(F_s=float(value),P_s=float(pre),R_s=float(rec));main="F_s"
  sizes=[len(evaluation.string_to_list(opens[n])) for n in names];ms.update(mean_extracted_labels=float(np.mean(sizes)),empty_extracted_labels=int(sum(x==0 for x in sizes)))
  require(all(math.isfinite(x) for x in ms.values()),"Nonfinite metric")
  score=dict(job_id=j["job_id"],variant=v,dataset=d,condition=p["ablation_by_variant"][v],samples=len(names),main_metric=main,main_score=float(value),metrics=ms,checkpoint=j["checkpoint"],raw_path=str(raw),raw_sha256=sha(raw),plan_id=p["plan_id"],judge_protocol_id=p["judge_protocol_id"])
  atomic_json(run/"scores"/(j["job_id"]+".json"),score);values.append(score)
 atomic_json(run/"metrics_all.json",values)
 columns=["dataset","condition","main_metric","main_score","HIT","M","WAF","ACC","F_s","P_s","R_s","mean_extracted_labels","empty_extracted_labels"]
 out=io.StringIO();writer=csv.DictWriter(out,fieldnames=columns,extrasaction="ignore");writer.writeheader()
 for x in values:writer.writerow(dict(x,**x["metrics"]))
 (run/"metrics_all.csv").write_text(out.getvalue())
 lookup={(x["dataset"],x["condition"]):x for x in values};deltas=[]
 for d in p["datasets"]:
  for c,b in [("B","A"),("C","B"),("D","B"),("E","C"),("E","D"),("E","B"),("P","E")]:
   x,y=lookup[d,c],lookup[d,b];deltas.append(dict(dataset=d,condition=c,reference=b,delta_percentage_points=100*(x["main_score"]-y["main_score"])))
 atomic_json(run/"paired_deltas.json",deltas)
 import runpy,warnings
 with warnings.catch_warnings():
  warnings.simplefilter("ignore",RuntimeWarning);helpers=runpy.run_path(str(ROOT/"analysis_reports/sample_audit_75_43_20261028/common.py"))
 ar=helpers["arrays"];detail=[]
 for d in p["datasets"]:
  for c,b in [("B","A"),("C","B"),("D","B"),("E","C"),("E","D"),("P","E")]:
   x=ar(lookup[d,c]["raw_path"],d);y=ar(lookup[d,b]["raw_path"],d)
   if d in POLARITY:
    old=y["y"]==y["z"];new=x["y"]==x["z"];item=dict(corrected=int(np.sum(~old&new)),harmed=int(np.sum(old&~new)),unchanged=int(np.sum(old==new)))
   else:
    diff=np.nanmean(x["hit"]-y["hit"],axis=1) if d in CATEGORICAL else np.nanmean(x["prec"]+x["rec"]-y["prec"]-y["rec"],axis=1)
    item=dict(improved=int(np.sum(diff>1e-12)),worsened=int(np.sum(diff< -1e-12)),notes="HIT direction, or OV mean(P+R) diagnostic; not sum of official score contributions.")
   detail.append(dict(dataset=d,condition=c,reference=b,**item))
 atomic_json(run/"sample_effects.json",detail)
 lines=["# 原188类图：九集赢家证据干预","","固定各集原赢家；A-E无路径，P为原始完整提示。全部组重新生成；完全相同prompt/checkpoint/seed/media复用一次生成。评分按唯一内容绑定seed并缓存。","原仓库评分函数/词典/提示/temperature0.7等保留；新增内容seed与全局缓存，是新配对评分协议，不能与历史成绩作纯因果差值。历史P另保留。","","|数据集|A无证据|B Cue|C Cue+App|D Cue+Emotion|E全部无路径|P原完整|历史P|","|---|---:|---:|---:|---:|---:|---:|---:|"]
 for d in p["datasets"]:lines.append("|"+d+"|"+"|".join(f'{100*lookup[d,c]["main_score"]:.3f}' for c in p["conditions"])+"|"+f'{100*p["historical_anchors"][d]["main_score"]:.3f}'+"|")
 lines+=["","逐样本净纠错/伤害见sample_effects.json；主指标差见paired_deltas.json。","本轮为已查看测试集上的机制诊断，不用于宣布新泛化最好值，不触发自动改图/训练。"]
 (run/"RESULTS.md").write_text("\n".join(lines)+"\n")
 atomic_json(run/"final_verification.json",dict(passed=True,jobs=len(values),logical_predictions=sum(x["samples"] for x in values),unique_generation_inputs=len(list((run/"generation_cache").glob("*.json"))),unique_raw_answers=len(identical_answers),same_answer_same_extraction=True,same_openset_same_sentiment=True,score_protocol=p["judge_protocol_id"],finished_at_beijing=now()))
 return len(values)

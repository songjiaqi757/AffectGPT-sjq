"""Choose and freeze only the pre-registered source-validation query parameters."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,copy,csv,datetime,json,math,time
from graph_paths import Path
from zoneinfo import ZoneInfo
import numpy as np
from amg_runtime.common import ROOT,read,sha,canonical,atomic_json,require
from amg_runtime.versioning import load_release
from .evaluation import predictions,engine_for,rerank,emotion_case,case_summary,appraisal_metrics,result_appraisal,preview,FIELDS

def selection_key(row):
 m=row["metrics"]
 return (-round(m["objective"],12),-round(m["emotion_valid_query_coverage"],12),-round(m["appraisal_valid_dimension_coverage"],12),row["emotion_top_k"],-row["minimum_coverage"],-row["query_min_support_groups"],-row["query_path_min_joint_support_groups"],abs(row["direct_two_hop_lambda"]-.5),-row["direct_two_hop_lambda"])

def final_config(run,winner,path_k):
 run=Path(run);reg=read(run/"preregistration.json");cfg=read(Path(reg["runtime_path"])/"query_config.engineering.json")
 cfg["purpose"]="source_validation_frozen"
 cfg["notes"]="P4 "+reg["preregistration_id"]+"; selected only on 3,076 source pseudo_validation members. Teacher retrieval consistency, not human or independent target accuracy. Cue threshold 0.5 and engineering active/deferred policy unchanged."
 cfg["query_parameters"].update(query_min_support_groups=winner["query_min_support_groups"],query_path_min_joint_support_groups=winner["query_path_min_joint_support_groups"],dimension_min_evidence=winner["dimension_min_evidence"],minimum_coverage=winner["minimum_coverage"],emotion_top_k=winner["emotion_top_k"],path_top_k=path_k,direct_two_hop_lambda=winner["direct_two_hop_lambda"],branch="full")
 return cfg

def finalize(run):
 run=Path(run);reg=read(run/"preregistration.json");runtime=load_release(reg["runtime_path"])
 require(runtime["release_id"]==reg["runtime_release_id"],"Runtime drift")
 refs=read(run/"references.json");qs=predictions(run);grid=[]
 for index in range(4):
  require(read(run/("profile_"+str(index)+"_status.json"))["state"]=="complete","A profile is unfinished")
  profile=read(run/("profile_"+str(index)+"_results.json"))
  require(profile["preregistration_id"]==reg["preregistration_id"],"Profile protocol mismatch")
  for row in profile["summaries"]:
   for support in reg["candidate_grid"]["query_min_support_groups"]:
    for joint in reg["candidate_grid"]["query_path_min_joint_support_groups"]:
     item=dict(row,query_min_support_groups=support,query_path_min_joint_support_groups=joint)
     item["candidate_id"]=canonical({k:v for k,v in item.items() if k!="metrics"});grid.append(item)
 require(len(grid)==720,"Unexpected staged grid size")
 winner=sorted(grid,key=selection_key)[0]
 for row in grid:row["selected_stage_B"]=row["candidate_id"]==winner["candidate_id"]
 atomic_json(run/"stage_B_grid_results.json",dict(results=grid,selected=winner,effective_retrieval_configurations=60,declared_with_support_aliases=720,preregistration_id=reg["preregistration_id"]))
 with (run/"query_validation_results.csv").open("w",newline="") as f:
  fields=["candidate_id","profile_index","minimum_coverage","dimension_min_evidence","direct_two_hop_lambda","emotion_top_k","query_min_support_groups","query_path_min_joint_support_groups","selected_stage_B"]+list(winner["metrics"])
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for row in grid:
   writer.writerow({k:(json.dumps(row[k],sort_keys=True) if k=="dimension_min_evidence" else row[k]) for k in fields if k not in row["metrics"]}|row["metrics"])
 atomic_json(run/"status.json",dict(phase="stage_C_native_replay",completed=0,total=len(qs),stage_B_selected=winner,preregistration_id=reg["preregistration_id"]))
 params=dict(query_min_support_groups=winner["query_min_support_groups"],query_path_min_joint_support_groups=winner["query_path_min_joint_support_groups"],dimension_min_evidence=winner["dimension_min_evidence"],minimum_coverage=winner["minimum_coverage"],emotion_top_k=winner["emotion_top_k"],direct_two_hop_lambda=winner["direct_two_hop_lambda"],path_top_k=20,branch="full")
 engine=engine_for(run,params);path_options=reg["candidate_grid"]["path_top_k"]
 data=np.zeros((len(path_options),len(qs),len(FIELDS)),float);apps=[];start=time.time()
 cache=run/"selected_native_query_cache.jsonl"
 with cache.open("w") as f:
  for i,(cue,ref) in enumerate(zip(qs,refs)):
   result=engine.query(cue);apps.append(result_appraisal(result,engine.dimensions))
   full=rerank(result,winner["direct_two_hop_lambda"],winner["emotion_top_k"],20)
   require(full["emotion_candidates"]==result["emotion_candidates"] and full["explanation_paths"]==result["explanation_paths"],"Native final reranking mismatch")
   for j,k in enumerate(path_options):
    view=dict(full,explanation_paths=full["explanation_paths"][:k]);data[j,i]=emotion_case(ref,view)
   f.write(json.dumps(result,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n")
   if (i+1)%100==0 or i+1==len(qs):
    atomic_json(run/"status.json",dict(phase="stage_C_native_replay",completed=i+1,total=len(qs),elapsed_seconds=time.time()-start,preregistration_id=reg["preregistration_id"]));print(json.dumps(dict(native_replay=i+1,total=len(qs))),flush=True)
 app=appraisal_metrics(refs,apps,engine.dimensions)
 require(app==read(run/("profile_"+str(winner["profile_index"])+"_results.json"))["appraisal_metrics"],"Native appraisal aggregate mismatch")
 path_results=[]
 for j,k in enumerate(path_options):
  metrics=case_summary(data[j],refs)
  for field in ["emotion_sample_macro_precision","emotion_sample_macro_recall","emotion_sample_macro_f1","emotion_valid_query_coverage"]:
   require(abs(metrics[field]-winner["metrics"][field])<1e-15,"Native retrieval metric differs from grid: "+field)
  path_results.append(dict(path_top_k=k,metrics=metrics))
 maximum=max(r["metrics"]["explained_candidate_fraction_mean"] for r in path_results)
 eligible=[r for r in path_results if r["metrics"]["explained_candidate_fraction_mean"]>=.95*maximum-1e-15]
 selected_path=sorted(eligible,key=lambda r:(r["path_top_k"],r["metrics"]["context_utf8_bytes_mean"]))[0]
 k=selected_path["path_top_k"];idx=path_options.index(k);cfg=final_config(run,winner,k)
 atomic_json(run/"query_engine_config.json",cfg);config_id=canonical(cfg);atomic_json(run/"stage_C_path_results.json",dict(results=path_results,maximum_explained_fraction=maximum,required_fraction=.95,selected=selected_path))
 np.savez_compressed(_graph_resolve_path(run / 'selected_per_sample_metrics.npz'), values=data[idx], sample_ids=np.asarray(reg['validation_sample_ids']), fields=np.asarray(FIELDS))
 # Path Top-K changes presentation only. Rewrite the native replay with the final frozen configuration;
 # fixed ordinals are compared against fresh frozen-engine calls to prove the transformation.
 engine.config=cfg;engine._validate_config();verify_ids={0,997,2049,3075};proofs=0
 with cache.open() as source,(run/"per_sample_query_results.jsonl").open("w") as output,(run/"per_sample_metrics.csv").open("w",newline="") as metrics_file:
  fields=["sample_id","role","emotion_reference_valid","emotion_reference_count"]+FIELDS+["fallback_required","fallback_reason"]
  writer=csv.DictWriter(metrics_file,fieldnames=fields);writer.writeheader()
  for i,line in enumerate(source):
   result=json.loads(line);result["query_config"]=copy.deepcopy(cfg);result["query_config_id"]=config_id;result["explanation_paths"]=result["explanation_paths"][:k]
   result.pop("query_result_id");result["query_result_id"]=canonical(result)
   if i in verify_ids:require(result==engine.query(qs[i]),"Final presentation/native result mismatch");proofs+=1
   output.write(json.dumps(result,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n")
   values={name:(float(data[idx,i,j]) if math.isfinite(data[idx,i,j]) else "") for j,name in enumerate(FIELDS)}
   writer.writerow(dict(sample_id=refs[i]["sample_id"],role="pseudo_validation",emotion_reference_valid=refs[i]["emotion_valid"],emotion_reference_count=len(refs[i]["emotion_ids"]),**values,fallback_required=result["fallback"]["required"],fallback_reason=result["fallback"]["reason"]))
 inputs=read(Path(reg["runtime_path"])/"inputs_p0.json");before=read(run/"graph_before.json")
 for relative,expected in before["artifact_sha256"].items():require(_graph_hash_matches(Path(inputs['graph']['path']) / relative, expected, sha(Path(inputs['graph']['path']) / relative)),"Frozen graph changed: "+relative)
 require(_graph_hash_matches(Path(reg['runtime_path']) / 'cue_policy.json', reg['cue_policy']['sha256'], sha(Path(reg['runtime_path']) / 'cue_policy.json')),"Cue policy changed during P4")
 final_metrics=dict(selected_path["metrics"],appraisal=app,objective=.5*(app["macro_state_f1"]+selected_path["metrics"]["emotion_sample_macro_f1"]))
 sizes=data[idx,:,FIELDS.index("context_characters")];bytes_=data[idx,:,FIELDS.index("context_utf8_bytes")]
 final_metrics["context_size_distribution"]=dict(characters_p50=float(np.quantile(sizes,.5)),characters_p95=float(np.quantile(sizes,.95)),characters_max=float(np.max(sizes)),utf8_bytes_p50=float(np.quantile(bytes_,.5)),utf8_bytes_p95=float(np.quantile(bytes_,.95)),utf8_bytes_max=float(np.max(bytes_)),semantics="Fixed JSON evidence preview only; final AffectGPT prompt token length remains a P5 measurement")
 atomic_json(run/"selected_metrics.json",final_metrics)
 code={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/"amg_validation").glob("*.py"))}
 locked=read(run/"evaluation_code_manifest.json")
 require(code==locked["source_code_sha256"],"P4 implementation changed after evaluation began")
 report=dict(schema_version="amg_P4_selection_v1",status="P4_source_validation_selected_and_frozen",completed_at_beijing=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),preregistration_id=reg["preregistration_id"],runtime_release_id=reg["runtime_release_id"],cue_release_id=reg["cue_release_id"],graph_release_id=reg["graph_release_id"],validation_samples=len(qs),emotion_valid_samples=sum(r["emotion_valid"] for r in refs),config_path=str(run/"query_engine_config.json"),config_id=config_id,config_sha256=sha(run/"query_engine_config.json"),parameters=cfg["query_parameters"],metrics=final_metrics,selection=dict(stage_A_candidates=120,stage_B_effective=60,stage_B_declared_with_support_aliases=720,stage_C_path_options=3,selected_stage_B_candidate=winner["candidate_id"],support_and_joint_selected_by_tie_break=True),verification=dict(all_3076_members_verified=True,native_replay_samples=len(qs),native_retrieval_metrics_match_grid=True,final_presentation_native_comparisons=proofs,graph_artifact_hashes_unchanged=True,cue_policy_unchanged=True,training_calls=0,teacher_calls=0,gold_reserved_target_used=False),limitations=["Source Teacher pseudo-label retrieval consistency; not human psychological accuracy or target performance","Same source validation was already used for Student model development; this is parameter selection, not an independent test","Engineering Cue policy and uncalibrated 0.5 threshold unchanged; human active/deferred still pending","Final AffectGPT token budget and model integration belong to P5"],inputs=dict(preregistration_sha256=sha(run/"preregistration.json"),predictions_sha256=sha(run/"cue_predictions.jsonl"),references_sha256=sha(run/"references.json"),evaluation_code_sha256=sha(run/"evaluation_code_manifest.json")),final_target_evaluation_allowed=False)
 report["selection_release_id"]=canonical(report);atomic_json(run/"selection_manifest.json",report)
 lines=["# P4 源域查询参数选择","","状态：只使用3,076条固定pseudo_validation完成预注册参数选择并冻结；未使用人工审计、独立保留或目标集。","",f"预注册：{reg['preregistration_id']}",f"Runtime：{reg['runtime_release_id']}",f"最终配置ID：{config_id}","","## 选择方法","","先逐维选择delta，再在4个覆盖率profile上比较lambda和Emotion K，最后选择路径K。评价分母保留全部固定验证样本；各Teacher参考mask单独生效，缺失/无效标注不当负例。有效Appraisal维度上的弃判计为漏检。","主目标为Appraisal宏状态F1与Emotion样本宏F1@K均值；按预注册规则打破平局。","查询支持5/10/20、联合支持0/1/3/5在当前冻结正式图上等价，最终20/5来自平局规则，不表示重新比较构图统计后发现最优。","","## 冻结参数","","\`\`\`json",json.dumps(cfg["query_parameters"],ensure_ascii=False,indent=2),"\`\`\`","","## 源域Teacher一致性检索表现","",f"- Appraisal宏状态F1@1：{app['macro_state_f1']:.10f}",f"- Appraisal宏状态Recall@1：{app['macro_state_recall']:.10f}",f"- 有效Appraisal维度查询覆盖率：{app['valid_dimension_coverage']:.10f}",f"- Emotion样本宏Precision@K：{final_metrics['emotion_sample_macro_precision']:.10f}",f"- Emotion样本宏Recall@K：{final_metrics['emotion_sample_macro_recall']:.10f}",f"- Emotion样本宏F1@K：{final_metrics['emotion_sample_macro_f1']:.10f}",f"- Emotion有效参考：{report['emotion_valid_samples']}条；查询覆盖率：{final_metrics['emotion_valid_query_coverage']:.10f}",f"- 两项F1均值：{final_metrics['objective']:.10f}",f"- 证据预览平均字符：{final_metrics['context_characters_mean']:.2f}；平均UTF8字节：{final_metrics['context_utf8_bytes_mean']:.2f}。这不是最终AffectGPT token长度。","","## 分维度结果","","|维度|有效参考|宏状态Precision|宏状态Recall|宏状态F1|覆盖率|弃判率|","|---|---:|---:|---:|---:|---:|---:|"]
 for d,m in app["per_dimension"].items():lines.append(f"|{d}|{m['valid_reference']}|{m['macro_precision']:.6f}|{m['macro_recall']:.6f}|{m['macro_f1']:.6f}|{m['coverage']:.6f}|{m['abstention']:.6f}|")
 lines+=["","## 验证与产物","","所有3,076条预测均由P0/P2锁定的best权重重新生成，并保存原始模态指纹；没有使用validation.last.npz。四个profile对全部样本的Appraisal输出均与冻结引擎一致；每个profile固定4个样本的全部15个lambda/K组合与原引擎精确一致；最终配置在全部3,076条样本上重放，聚合指标与网格一致。","冻结图文件指纹、Cue阈值与策略未变；无训练和Teacher调用。","", "- query_engine_config.json：P5使用的冻结查询参数。","- query_validation_results.csv / stage_B_grid_results.json：720项声明候选及60种不同行为的结果。","- stage_A_results.json / stage_A_profiles.json：逐维delta选择及完整状态计数。","- stage_C_path_results.json：路径K、解释覆盖和上下文大小。","- per_sample_query_results.jsonl / per_sample_metrics.csv：逐样本证据与评分。","- prediction_manifest.json / reference_manifest.json / evaluation_code_manifest.json：输入与实现指纹。","- selection_manifest.json：版本、方法、指标、限制及最终配置hash。","","这些是源域伪标签检索结果，不是人工心理状态准确率、独立测试成绩或目标集表现。后续不得根据目标集反馈调整这些参数。人工active/deferred、P1审计及P5-P7仍须按原协议完成。",""]
 (run/"P4_REPORT.md").write_text("\n".join(lines).replace("\\`","`"))
 atomic_json(run/"status.json",dict(phase="complete",selection_release_id=report["selection_release_id"],config_id=config_id,preregistration_id=reg["preregistration_id"]))
 files={str(p.relative_to(run)):sha(p) for p in sorted(run.iterdir()) if p.is_file() and p.name not in ["run.log","delivery_manifest.json"] and p.suffix in [".json",".csv",".md",".npz"]}
 files["per_sample_query_results.jsonl"]=sha(run/"per_sample_query_results.jsonl")
 atomic_json(run/"delivery_manifest.json",dict(selection_release_id=report["selection_release_id"],files_sha256=files))
 atomic_json(ROOT/"amg_validation/runs/current.json",dict(path=str(run),selection_release_id=report["selection_release_id"],runtime_release_id=reg["runtime_release_id"],query_config=str(run/"query_engine_config.json"),query_config_id=config_id,report=str(run/"P4_REPORT.md"),status=report["status"],final_target_evaluation_allowed=False))
 print(json.dumps(dict(status=report["status"],config_id=config_id,parameters=cfg["query_parameters"],metrics=final_metrics),ensure_ascii=False))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--run",required=True);args=p.parse_args();finalize(args.run)

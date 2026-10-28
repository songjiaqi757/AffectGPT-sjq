"""Final P2/P3 acceptance and publication, executed only on the server."""
import datetime,json,os,re,subprocess,sys
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path("/ai/sjq/AffectGPT-sjq");sys.path.insert(0,str(ROOT))
from amg_runtime.common import read,sha,canonical,atomic_json,require
from amg_runtime.versioning import load_release
def main(directory):
 directory=Path(directory).resolve();validation=directory/"validation"
 manifest=load_release(directory);integration=read(validation/"integration_report.json");oracle=read(validation/"dense_oracle_report.json")
 require(integration["passed"] and oracle["passed"],"Integration/oracle checks not complete")
 require(integration["runtime_release_id"]==oracle["runtime_release_id"]==manifest["release_id"],"Validation release mismatch")
 require(not (validation/"integration_failure.json").exists(),"Unresolved integration failure")
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",OMP_NUM_THREADS="4",OPENBLAS_NUM_THREADS="4")
 unit=subprocess.run([sys.executable,"-m","unittest","amg_runtime.tests.test_runtime","-v"],cwd=ROOT,env=env,capture_output=True,text=True)
 (validation/"unit_tests_final.log").write_text(unit.stdout+unit.stderr)
 require(unit.returncode==0,"Final unit tests failed")
 match=re.search(r"Ran (\d+) tests",unit.stdout+unit.stderr);require(match is not None,"Missing unit test summary")
 unit_count=int(match.group(1));atomic_json(validation/"unit_test_report.json",dict(passed=True,tests=unit_count,returncode=unit.returncode,source_code_sha256=manifest["source_code_sha256"],runtime_release_id=manifest["release_id"]))
 cli=[sys.executable,"-m","amg_runtime.cli"]
 query_path=validation/"cli_query_results.json";query_log=validation/"cli_query_audit.jsonl"
 for p in [query_path,query_log]:
  require(not p.exists(),"Do not overwrite previous CLI acceptance outputs")
 command=cli+["query","--release",str(directory),"--input",str(validation/"cue_smoke_predictions.json"),"--output",str(query_path),"--audit-log",str(query_log)]
 result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True)
 (validation/"cli_query.log").write_text(result.stdout+result.stderr);require(result.returncode==0,"CLI query failed")
 require(read(query_path)==read(validation/"query_smoke_results.json"),"CLI/API query results differ")
 atomic_json(validation/"cli_missing_input.json",[dict(sample_id="cli_missing_all",text={})])
 result=subprocess.run(cli+["run","--release",str(directory),"--input",str(validation/"cli_missing_input.json"),"--output",str(validation/"cli_missing_output.json")],cwd=ROOT,env=env,capture_output=True,text=True)
 (validation/"cli_missing.log").write_text(result.stdout+result.stderr);require(result.returncode==0,"CLI empty-input run failed")
 missing=read(validation/"cli_missing_output.json");require(len(missing)==1 and missing[0]["fallback"]["required"],"CLI fallback failed")
 inputs=read(directory/"inputs_p0.json")
 p0=read(ROOT/"amg_graph/preflight/current.json");lock=read(p0["version_lock"]);inventory=read(Path(p0["path"])/"checkpoint_inventory.json")
 protected_prefixes=[str(Path(inputs["cue_release"]["path"])),str(Path(inputs["graph"]["path"])),str(ROOT/"emotion_nodes/runs/affectgpt_original_v1")]
 unchanged=0
 for filename,digest in lock["input_fingerprints"].items():
  if any(filename.startswith(prefix+"/") for prefix in protected_prefixes):
   require(sha(filename)==digest,"Protected original artifact changed: "+filename);unchanged+=1
 for name,row in inventory.items():
  stat=Path(row["checkpoint"]).stat()
  require((stat.st_size,stat.st_mtime_ns)==(row["bytes"],row["mtime_ns"]),"Original checkpoint stat changed: "+name)
 members=read(Path(inputs["cue_release"]["path"])/"members.json")
 smoke_set=set(integration["source_validation_sample_ids"])
 original_inputs=[{k:r[k] for k in ["sample_id","text","audio_path","video_path"]} for r in members if r["sample_id"] in smoke_set]
 require(all(r["role"]=="pseudo_validation" for r in members if r["sample_id"] in smoke_set),"Smoke input role drift")
 atomic_json(validation/"source_smoke_inputs.json",original_inputs)
 export=read(directory/"weight_exports.json")
 report=dict(status="P2_P3_engineering_complete",runtime_release_id=manifest["release_id"],p0_lock_id=manifest["p0_lock_id"],completed_at_beijing=datetime.datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),P2=dict(implemented=True,weights_frozen=True,scores=42,order="Text15/Audio17/Visual10",same_original_preprocessing_and_forward=True,lossless_safetensors_exports_verified=True,threshold_status="uncalibrated_0.5",engineering_policy_frozen=True,human_deployment_active_deferred_frozen=False),P3=dict(implemented=True,direct_and_two_hop_queries=True,joint_support_in_scoring=True,per_dimension_abstention=True,empty_and_failure_baseline_callback=True,full_json_and_jsonl_trace=True,final_query_parameters_selected_by_P4=False),validation=dict(unit_tests_passed=unit_count,integration_checks_passed=integration["check_count"],real_source_prediction_cases=integration["cue_prediction_cases"],source_validation_sample_ids=integration["source_validation_sample_ids"],synthetic_dense_oracle_queries=oracle["synthetic_queries"],candidate_scores_compared=oracle["candidate_scores_compared"],max_oracle_absolute_error=oracle["max_absolute_error"],cli_matches_api=True,cli_empty_query_fallback=True,original_artifact_hashes_unchanged=unchanged,original_checkpoint_stats_unchanged=len(inventory)),no_training_or_teacher_calls=True,target_datasets_used=False,final_target_evaluation_allowed=False,pending=["P1 human Cue/Appraisal and original-source/near-duplicate audits","Formal Cue deployment active/deferred and any human calibration under the Cue protocol","P4 preregistered finite source validation parameter selection","P5 AffectGPT model integration","P6/P7 experiments and final frozen target evaluation"],entrypoints=dict(cue_policy=str(directory/"cue_policy.json"),query_config=str(directory/"query_config.engineering.json"),schemas=str(directory/"schemas"),code=str(ROOT/"amg_runtime"),release_manifest=str(directory/"release_manifest.json"),tests=str(validation)))
 atomic_json(validation/"acceptance_report.json",report)
 lines=["# P2/P3 工程实现与验收","","状态：P2/P3 工程实现完成并通过验证；正式部署及最终目标集评测仍关闭。","",f"完成时间（北京时间）：{report['completed_at_beijing']}",f"Runtime release ID：{manifest['release_id']}",f"P0 lock ID：{manifest['p0_lock_id']}","","## 实现","","- P2：锁定 text / audio_full / visual_full；固定42维顺序；分开记录 scores、模态可用性、active/deferred、requested/selected 及版本诊断。","- 原始 checkpoint 仅静态读取张量，三路 safetensors 逐张量无损核验；运行时不执行 checkpoint pickle。原预处理与 CueModel.forward 保留。","- 工程模式沿用0.5未校准阈值，并明确标记42槽位尚未完成人工 active 判断；部署模式全部暂缓，返回回退请求。","- P3：直接关联、Appraisal 状态支持与覆盖率、联合支持比 R、维度加权两跳、缺失分支回退、融合、Top-K 和解释路径。","- 查询只过滤现有正式图。构图边20组、路径5组准入规则保持不变；查询过滤不会恢复被排除的路径。","- 每条查询保留输入快照、有效 Cue、配置和版本 hash、边/路径 ID、权重、来源组支持、联合支持、门控和回退状态。","","## 验证","",f"- {unit_count}项单元/边界测试通过，包括独立手算公式、门控、阈值边界、mask、缺失输入、身份漂移和标签拒绝。",f"- {integration['check_count']}项真实GPU集成检查通过；{integration['cue_prediction_cases']}种预测/查询样例来自2条源域验证样本及其边界变体。",f"- 重复推理、单样本与batch接口输出逐项一致。batch接口按原predict的方式逐样本执行，未声称张量批量提速。",f"- 真实冻结图上用{oracle['synthetic_queries']}组无标签合成Cue分数进行独立NumPy矩阵对照，比较{oracle['candidate_scores_compared']}个候选分数，最大绝对误差{oracle['max_absolute_error']:.3g}。","- CLI与API图查询结果完全一致；无输入时CLI输出明确回退。",f"- {unchanged}个原数据/图/Emotion文件哈希不变，9组原checkpoint的大小/mtime不变。","","## 产物与复现","","- release_manifest.json：代码、配置、schema及输入版本。","- cue_policy.json：两种明确标记的策略profile。","- query_config.engineering.json：仅供工程契约测试的可运行参数，未经P4选择。","- weights/与export_*.json：推理权重与无损转换证据。","- schemas/：原始输入、42维Cue、图结果、查询配置JSON schema。","- validation/acceptance_report.json：机器可读验收报告。","- validation/source_smoke_inputs.json：服务器上的源域复现实例。","- validation/cue_smoke_predictions.json / query_smoke_results.json / query_audit.jsonl：完整输出与日志。","- validation/integration_report.json / dense_oracle_report.json / unit_test_report.json：验证证据。","- amg_runtime/README.md：CLI用法与语义说明。","","所有模型和数据操作均在服务器进行，无模型训练、Teacher请求、图重建或目标集标签使用。真实AffectGPT模型接入属于P5；本次验证的是回退回调契约，不声称已运行AffectGPT。",""]
 (directory/"P2P3_REPORT.md").write_text("\n".join(lines))
 artifacts={}
 for p in sorted(directory.rglob("*")):
  if p.is_file() and "weights" not in p.relative_to(directory).parts and p.name not in ["delivery_manifest.json"]:
   artifacts[str(p.relative_to(directory))]=sha(p)
 atomic_json(directory/"delivery_manifest.json",dict(runtime_release_id=manifest["release_id"],files_sha256=artifacts,inference_weight_sha256={m:e["sha256"] for m,e in export["exports"].items()}))
 atomic_json(ROOT/"amg_runtime/releases/current.json",dict(path=str(directory),release_id=manifest["release_id"],release_manifest=str(directory/"release_manifest.json"),report=str(directory/"P2P3_REPORT.md"),acceptance_report=str(validation/"acceptance_report.json"),cue_policy=str(directory/"cue_policy.json"),query_config=str(directory/"query_config.engineering.json"),status="P2_P3_engineering_complete",final_target_evaluation_allowed=False))
 require(load_release(directory)["release_id"]==read(ROOT/"amg_runtime/releases/current.json")["release_id"],"Publication mismatch")
 print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main(sys.argv[1])

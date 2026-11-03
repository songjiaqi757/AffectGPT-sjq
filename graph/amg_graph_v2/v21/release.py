"""Freeze an internally validated v2.1 policy without changing baseline membership or models."""
import collections,gzip,json,os,shutil,subprocess,sys,time
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from .common import *
from .runtime import SampleGraphV21
from .calibration import mapped,evaluate_calibration

def cp(src,dst):
 dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)

def main():
 complete=read(ROOT/'work/fit_complete.json');assert complete['complete'];c=read(ROOT/'config.json');prep=read(ROOT/'data/prepared.json');policy=read(ROOT/'work/cue_admission_policy.json');data=dict(np.load(ROOT/'data/development.npz'));evaluation=dict(np.load(ROOT/'data/internal_evaluation.npz'));baseline_manifest=read(BASELINE/'release_manifest.json');binding=read(BASELINE/'runtime/student_binding.json');codehash={f.name:sha(f) for f in ROOT.glob('*.py')};rid='amg_v2_1_cue_admission_'+digest(dict(config=sha(ROOT/'config.json'),policy=sha(ROOT/'work/cue_admission_policy.json'),development=sha(ROOT/'data/development.npz'),baseline=prep['baseline_G1_sha256'],code=codehash))[:16];release=BASE/'releases'/rid
 if (release/'release_manifest.json').exists() and read(release/'release_manifest.json').get('status')=='verified_internal_v21':raise FileExistsError('Frozen release exists; do not overwrite')
 release.mkdir(parents=True,exist_ok=True)
 for f in ROOT.joinpath('data').iterdir():
  if f.is_file():cp(f,release/'data'/f.name)
 for folder in ['ontology','learned_relations','paths']:
  for f in (BASELINE/folder).iterdir():
   if f.is_file():cp(f,release/folder/f.name)
 for f in (BASELINE/'source_snapshot').iterdir():
  if f.is_file():cp(f,release/'source_snapshot'/f.name)
 for f in ROOT.glob('*.py'):cp(f,release/'source_snapshot/v21'/f.name)
 for name in ['runtime.py','common.py','models.py']:cp(BASE/name,release/'source_snapshot/frozen_v2'/name)
 for f in (ROOT/'source_snapshot').iterdir():
  if f.is_file():cp(f,release/'source_snapshot'/f.name)
 cp(ROOT/'config.json',release/'config.json');cp(BASELINE/'runtime/student_binding.json',release/'runtime/student_binding.json');cp(BASELINE/'calibration/relation_calibration.json',release/'calibration/frozen_relation_calibration.json')
 mapping={'cue_calibration_final.json':'calibration','cue_calibration_oof.json':'calibration','cue_calibration_metrics.json':'calibration','cue_scores_and_oof.npz':'calibration','cue_admission_policy.json':'admission','cue_candidate_thresholds.json':'admission','cue_evidence_thresholds.json':'admission','cue_threshold_stability.json':'admission','cue_group_bootstrap.json':'admission','nested_group_cv_report.json':'validation','cue_precision_recall_report.json':'validation','cue_reliability_report.json':'validation','fit_complete.json':'validation'}
 for name,folder in mapping.items():cp(ROOT/'work'/name,release/folder/name)
 for f in (ROOT/'schemas').iterdir():cp(f,release/'runtime'/f.name)
 for f in (ROOT/'work/cues').iterdir():cp(f,release/'validation/cue_replays'/f.name)
 # Raw metrics remain available even when a rare Cue cannot support any calibration fit.
 allraw=[];calmetrics=read(release/'calibration/cue_calibration_metrics.json')
 for j,p in enumerate(policy['cues']):
  v=data['label_mask'][:,j]&data['available'][:,j];raw=evaluate_calibration(data['targets'][v,j],data['scores'][v,j],c['ece_bins']);allraw.append(dict(cue_id=p['cue_id'],**raw));calmetrics['cues'][j]['raw']=raw
 write(release/'calibration/cue_calibration_metrics.json',calmetrics);write(release/'validation/cue_raw_score_metrics_all42.json',dict(cues=allraw,label_provenance=c['label_provenance']))
 # Prompt capacity is fixed from development Evidence activations, never from evaluation labels.
 dev_evidence=np.zeros((len(data['scores']),42),bool)
 for j,p in enumerate(policy['cues']):
  if p['calibration']['method']!='deferred' and p['evidence']['threshold'] is not None:dev_evidence[:,j]=data['available'][:,j]&(mapped(data['scores'][:,j],p['calibration'],c)>=p['evidence']['threshold'])
 prompt_policy=dict(cue_top_k=int(np.clip(np.ceil(np.quantile(dev_evidence.sum(1),.75)),1,42)),selection='Pre-specified 75th percentile of formal-Cue count on calibration development; no evaluation/target labels',candidate_enters_prompt=False,mode_options=['node_only','relation_aware'],downstream_evaluation='not_run_this_internal_round');write(release/'runtime/prompt_policy.json',prompt_policy)
 manifest=dict(release_id=rid,status='assembling',baseline_release_id=baseline_manifest['release_id'],baseline_manifest_sha256=prep['baseline_manifest_sha256'],baseline_G1_sha256=prep['baseline_G1_sha256'],student_retrained=False,G1_refitted=False,Student_checkpoint_sha256={k:v['sha256'] for k,v in binding['checkpoints'].items()},Student_config_sha256={k:digest(v['config']) for k,v in binding['checkpoints'].items()},source_plan_sha256=prep['source_plan_sha256'],created_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),config_sha256=sha(ROOT/'config.json'),code_hashes=codehash,code_git_commit=subprocess.check_output(['git','-C',str(PROJECT),'rev-parse','HEAD'],text=True).strip(),original_membership_preserved=True,development_samples=1538,internal_evaluation_samples=1538,excluded_samples=0,cue_calibration_oof=True,Student_oof=False,Student_parameter_training_overlap_in_calibration=0,target_datasets_used=False,human_audit_performed=False,human_audit_required_this_round=False,independent_precision_guarantee=False,label_provenance=c['label_provenance'],source_group_limitation=read(ROOT/'data/group_manifest.json')['limitations'],threshold_scope='Per-Cue marginal Group Bootstrap bounds; no simultaneous 42-Cue guarantee',counts=complete)
 write(release/'release_manifest.json',manifest)
 graph=read(BASELINE/'graph.json');graph.update(release_id=rid,schema_version='amg_global_graph_v2_1',calibration_admission_policy='admission/cue_admission_policy.json',original_models_frozen=True,Student_retrained=False,raw_G1_input_unchanged=True)
 for node in graph['nodes']:
  if node['node_type']=='CueType':
   p=policy['cues'][policy['cue_ids'].index(node['id'])];node.update(calibration_status=p['calibration']['method'],candidate_status=p['candidate']['status'],evidence_status=p['evidence']['status'],candidate_threshold=p['candidate']['threshold'],evidence_threshold=p['evidence']['threshold'])
 write(release/'graph.json',graph)
 from ..release import graphml,viewer
 graphml(graph,release/'graph.graphml');viewer(graph,release/'graph_viewer.html');vf=release/'graph_viewer.html';vf.write_text(vf.read_text().replace('AMG v2 ·','AMG v2.1 ·').replace('内部源域实验，非 OOF','内部源域实验，校准 OOF；Student 不重训'))
 from .verify import verify
 acceptance=verify(release);assert acceptance['passed']
 from graph_paths import resolve_path
 student_assets=[]
 for modality,spec in binding['exports'].items():
  actual=Path(resolve_path(spec['path']));actual_hash=sha(actual);assert actual_hash==spec['sha256'];student_assets.append(dict(modality=modality,sha256=actual_hash,unchanged=True))
 write(release/'validation/student_weights_unchanged.json',dict(passed=True,assets=student_assets,Student_retrained=False))
 event('v21_acceptance_passed',checks=len(acceptance['checks']))
 # Actual runtime regression and complete per-sample contribution ledgers, gzip on server.
 engine=SampleGraphV21(release);cache=Path(binding['source_cache']);examples=release/'runtime/examples';examples.mkdir(parents=True,exist_ok=True);stats=collections.Counter();patterns=collections.Counter();statecounts=collections.Counter();sizes=[];cuecounts=[];hiddenCA=[];hiddenCE=[];closure=0.;maxmodeldiff=0.;saved=set();groups=evaluation['groups']
 with gzip.open(release/'runtime/internal_evaluation_sample_graphs.jsonl.gz','wt',encoding='utf-8',compresslevel=4) as out:
  for i,sid in enumerate(evaluation['sample_ids']):
   cue=read(cache/(str(sid)+'.json'))['cue'];g=engine.build_from_old_cue(cue);prompt=engine.prompt(g,'open_vocabulary','relation_aware');out.write(json.dumps(g,ensure_ascii=False,separators=(',',':'))+'\n');cov=g['coverage'];stats['samples']+=1;stats['fallback']+=int(g['fallback']['required']);stats['CueSignal']+=cov['cue_signal_count'];stats['CueEvidence']+=cov['cue_count'];stats['CandidateCue']+=cov['candidate_only_count'];stats['Prompt_CueEvidence']+=g['prompt_audit']['serialized_formal_cue_count'];stats['AppraisalEvidence']+=cov['appraisal_supported_count'];stats['EmotionEvidence']+=cov['emotion_candidate_count'];statecounts.update(a['admission_status'] for a in g['cue_audit']);patterns['fallback' if g['fallback']['required'] else 'with_formal_relation' if cov['appraisal_supported_count'] or cov['emotion_candidate_count'] else 'cue_only']+=1;sizes.append(len(g['nodes']));cuecounts.append(cov['cue_count'])
   for typ,hidden in [('CA',hiddenCA),('CE',hiddenCE)]:
    ledger=g['relation_contributions'][typ];mat=np.array(ledger['contributions']);bias=np.array(ledger['bias']);logits=np.array(ledger['logits']);closure=max(closure,float(np.max(np.abs(mat.sum(0)+bias-logits))));qm=np.where(evaluation['available'][i],evaluation['scores'][i],0.);maxmodeldiff=max(maxmodeldiff,float(np.max(np.abs(qm@engine.model[typ]+engine.model[typ+'_bias']-logits))));visible=np.array(ledger['graph_relation_exposure_mask']);hidden.append(float((np.abs(mat)*(~visible)).sum()/max(1e-12,np.abs(mat).sum())))
   pattern='fallback' if g['fallback']['required'] else 'candidate_and_evidence' if cov['candidate_only_count'] else 'evidence_only'
   if pattern not in saved:
    write(examples/(pattern+'.json'),g);(examples/(pattern+'_prompt.txt')).write_text(prompt);saved.add(pattern)
   if i%200==0:event('v21_samples_exported',done=i,total=len(evaluation['scores']))
 empty=engine.build('empty_example',[None]*42);engine.prompt(empty);write(examples/'empty_fallback.json',empty)
 metrics=dict(samples=stats['samples'],mean_CueSignal=stats['CueSignal']/stats['samples'],mean_CueEvidence=stats['CueEvidence']/stats['samples'],mean_CandidateCue=stats['CandidateCue']/stats['samples'],mean_Prompt_CueEvidence=stats['Prompt_CueEvidence']/stats['samples'],mean_AppraisalEvidence=stats['AppraisalEvidence']/stats['samples'],mean_EmotionEvidence=stats['EmotionEvidence']/stats['samples'],mean_nodes=float(np.mean(sizes)),fallback_ratio=stats['fallback']/stats['samples'],patterns=dict(patterns),cue_state_counts=dict(statecounts),mean_not_serialized_relation_absolute_contribution_ratio_CA=float(np.mean(hiddenCA)),mean_not_serialized_relation_absolute_contribution_ratio_CE=float(np.mean(hiddenCE)),scope='Actual sample/edge exposure, including absent formal targets. All hidden contributions retained in ledger.',model_input_and_weight_changed=False)
 write(release/'validation/cue_coverage_report.json',metrics);assert closure<1e-10 and maxmodeldiff<1e-10;write(release/'validation/cue_provenance_consistency.json',dict(passed=True,samples=stats['samples'],cells_per_sample_CA=42*16,cells_per_sample_CE=42*188,all_input_contributions_recorded=True,maximum_logit_closure_error=closure,maximum_difference_from_original_G1_logits=maxmodeldiff,graph_vs_prompt_exposure_recorded_separately=True,candidate_prompt_count=0,Student_and_G1_unchanged=True))
 write(release/'validation/locked_audit_report.json',dict(status='not_required_this_internal_round',performed=False,human_labels_used_for_tuning=False,reason='User asked to finish internal strategy implementation first; existing positive-only Teacher-visible review is not substituted for an independent precision audit.'))
 write(release/'validation/affectgpt_downstream_comparison.json',dict(status='not_run',reason='This release validates calibration, admission and runtime provenance internally. AffectGPT paired generation and nine-target downstream evaluation are a separate subsequent stage; no downstream gain is claimed.',target_labels_used_for_selection=False,models_frozen=True))
 # Source-domain reliability diagrams with counts retained in companion JSON.
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(7,6,figsize=(18,21),constrained_layout=True)
 for j,ax in enumerate(axes.flat):
  ax.plot([0,1],[0,1],color='#aaaaaa',lw=.7,ls='--');r=calmetrics['cues'][j]
  for name,color in [('raw','#c46a38'),('platt_oof','#2878b5')]:
   metric=r.get(name)
   if not metric:continue
   bins=[b for b in metric['reliability_bins'] if b['count']];ax.plot([b['mean_score'] for b in bins],[b['observed_frequency'] for b in bins],color=color,lw=.8,label=name);ax.scatter([b['mean_score'] for b in bins],[b['observed_frequency'] for b in bins],s=[6+np.sqrt(b['count']) for b in bins],color=color,alpha=.7)
  ax.set(xlim=(0,1),ylim=(0,1),title=policy['cue_ids'][j]);ax.title.set_fontsize(7);ax.tick_params(labelsize=6);ax.text(.03,.93,'n='+str(allraw[j]['samples'])+' / pos='+str(allraw[j]['positive']),fontsize=6,transform=ax.transAxes);ax.grid(alpha=.15)
 axes.flat[0].legend(fontsize=6);fig.suptitle('AMG v2.1 source pseudo-label reliability (OOF Platt vs raw); marker area follows bin count',fontsize=12);fig.savefig(release/'validation/cue_reliability_diagrams.svg');fig.savefig(release/'validation/cue_reliability_diagrams.png',dpi=130);plt.close(fig)
 comparison=read(release/'validation/cue_precision_recall_report.json');lines=['# AMG v2.1：校准、双层准入与贡献追溯内部验证版','',f"Release：`{rid}`",'','冻结并复用原 Cue Student、G1 参数和原始连续输入；不训练提取器，不重训关系模型。旧版发布保持不变。','', '**按用户要求不排除样本：开发 1,538 条，内部评估 1,538 条。10 条长文本相似性关联仅作为审计提示保留，不作为删样本依据；文本相似不能直接证明来自同一原视频。**','',f"最终校准器：{json.dumps(complete['calibration'],ensure_ascii=False)}。Candidate 准入 {complete['candidate_admitted']} 个 Cue；Evidence 准入 {complete['evidence_admitted']} 个；Evidence deferred {complete['evidence_deferred']} 个。",'', '## 实现与内部评估','', '逐 Cue Group OOF Platt / Identity / Deferred；外层留组评估整个校准与阈值选择过程；双层阈值；1,000 次 Group Bootstrap；每次稳定性重采样重新搜索阈值并重新估计其 Precision 下界。失败重复保留在分母中，不丢弃。','', '准入初始门槛采用方案建议：Candidate Precision≥0.65、LCB≥0.55、预测≥30、来源组≥20；Evidence Precision≥0.80、LCB≥0.70、预测≥50、来源组≥30、重采样存在可行阈值比例≥0.80。这些是源域伪标签下的选择约束，不是目标域或人工审计精度保证。','', '|策略|内部回归 Micro Precision|Micro Recall|有输出的 Cue 数|预测正例总数|','|---|---:|---:|---:|---:|']
 for name,value in comparison['internal_regression'].items():
  v=value['summary'];lines.append(f"|{name}|{v['micro_precision'] if v['micro_precision'] is not None else 'null'}|{v['micro_recall'] if v['micro_recall'] is not None else 'null'}|{v['emitting_cues']}|{v['predictions']}|")
 lines+=['', 'T0_frozen 为旧发布的实际固定策略；T1 为 OOF 校准加旧单阈值约束；T2 为组区间 Candidate 单层准入；T3 为双层但未加稳定性筛选的 Evidence；T4 为完整 Evidence 策略。T2 是候选层消融，其候选在正式运行时不进入 Prompt。Nested CV 另报告在外层训练部分重拟合的 T0 工作流，避免把旧发布已经见过的开发样本伪装成外层未见。','',f"实际导出 {metrics['samples']} 份样本图，平均正式 CueEvidence {metrics['mean_CueEvidence']:.3f}，实际 Prompt Cue {metrics['mean_Prompt_CueEvidence']:.3f}，fallback {metrics['fallback_ratio']:.2%}。",'', '每份样本保留全部 42×16 CA 和 42×188 CE 有符号贡献、bias、logits、CueSignal、CandidateCue、独立 masks、逐输出 hidden/visible 支持状态，以及实际图边和 Prompt 单元暴露标记。只有 evidence_active 创建正式 CueEvidence。model_only / partially_supported 的关系输出留在审计层，不伪装成可见证据的完整结论；没有正式关系但存在正式 Cue 的样本可走 Cue-only 路由。','',f"自动验收 {len(acceptance['checks'])} 项通过；全部内部样本的原始 G1 logit 最大差异 {maxmodeldiff:.3g}，贡献加 bias 闭合最大误差 {closure:.3g}。",'', '## 人工审计与后续边界','', '本轮不要求人工审计、不新增人工标注、不使用人工标签调参。现有工作台 positive-only / Teacher-visible 结果未被当作完整独立精度审计。当前是完成内部验证的工程版本；后续若要宣称独立人工验证的 Evidence Precision，仍需另做合适审计。','', '本轮未运行 AffectGPT 配对生成或九目标数据集下游评测，不宣称下游净收益。源域开发样本有历史 Student 选模和旧版校准曝光；全部校准监督为现有 Teacher 伪标签。来源组缺少原始视频/Speaker/Session 元数据，Group Bootstrap 不等于已解决全部来源相关性。42 个 Cue 的区间是边际区间，不是全体同时保证。','', '## 使用','', '```python','from amg_graph_v2.v21.runtime import SampleGraphV21',f"engine = SampleGraphV21({str(release)!r})",'sample_graph = engine.build_from_old_cue(old_cue_output)',"prompt = engine.prompt(sample_graph, task='open_vocabulary', mode='relation_aware')",'# 可对照 mode=node_only；Candidate 永远只在审计层。','```','', '主要文件：`graph.json`、`graph.graphml`、`graph_viewer.html`；`admission/` 双层策略与稳定性；`calibration/` OOF/最终校准器；`validation/` Nested CV、T0–T4、可靠性图与验收；`runtime/internal_evaluation_sample_graphs.jsonl.gz` 完整样本图及贡献账本。']
 (release/'REPORT.md').write_text('\n'.join(lines)+'\n')
 manifest.update(status='verified_internal_v21',acceptance_passed=True,coverage=metrics,artifact_sha256={str(f.relative_to(release)):sha(f) for f in sorted(release.rglob('*')) if f.is_file() and f.name!='release_manifest.json'});write(release/'release_manifest.json',manifest)
 for f,expected in manifest['artifact_sha256'].items():assert sha(release/f)==expected
 write(BASE/'current_v21.json',dict(path=str(release),release_id=rid,status=manifest['status'],report=str(release/'REPORT.md'),student_retrained=False,G1_refitted=False,excluded_samples=0,human_audit_required_this_round=False))
 (ROOT/'README.md').write_text('AMG v2.1 内部验证版本。入口：上级 current_v21.json。原 current.json 仍指向 T0，不覆盖旧发布。原开发/内部评估各1538条完整保留，文本相似性只审计、不排除；人工审计本轮不要求。Student/G1权重和原始输入不变。详见冻结发布 REPORT.md。\n')
 event('v21_release_verified',release=str(release),calibration=complete['calibration'],candidate=complete['candidate_admitted'],evidence=complete['evidence_admitted'],samples=1538,checks=len(acceptance['checks']),excluded=0)
if __name__=='__main__':main()

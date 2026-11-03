# AMG v2.1：校准、双层准入与贡献追溯内部验证版

Release：`amg_v2_1_cue_admission_8a8994fe1e7495f0`

冻结并复用原 Cue Student、G1 参数和原始连续输入；不训练提取器，不重训关系模型。旧版发布保持不变。

**按用户要求不排除样本：开发 1,538 条，内部评估 1,538 条。10 条长文本相似性关联仅作为审计提示保留，不作为删样本依据；文本相似不能直接证明来自同一原视频。**

最终校准器：{"platt": 31, "identity": 3, "deferred": 8}。Candidate 准入 33 个 Cue；Evidence 准入 26 个；Evidence deferred 16 个。

## 实现与内部评估

逐 Cue Group OOF Platt / Identity / Deferred；外层留组评估整个校准与阈值选择过程；双层阈值；1,000 次 Group Bootstrap；每次稳定性重采样重新搜索阈值并重新估计其 Precision 下界。失败重复保留在分母中，不丢弃。

准入初始门槛采用方案建议：Candidate Precision≥0.65、LCB≥0.55、预测≥30、来源组≥20；Evidence Precision≥0.80、LCB≥0.70、预测≥50、来源组≥30、重采样存在可行阈值比例≥0.80。这些是源域伪标签下的选择约束，不是目标域或人工审计精度保证。

|策略|内部回归 Micro Precision|Micro Recall|有输出的 Cue 数|预测正例总数|
|---|---:|---:|---:|---:|
|T0_frozen|0.6644696969696969|0.8980239582266817|39|13200|
|T1|0.6513212066771465|0.8908569673389987|34|13359|
|T2|0.6512466206067888|0.8878877853998157|33|13316|
|T3|0.7989641686925272|0.7739326302856557|28|9461|
|T4|0.7994226451405966|0.7655370123886557|26|9353|

T0_frozen 为旧发布的实际固定策略；T1 为 OOF 校准加旧单阈值约束；T2 为组区间 Candidate 单层准入；T3 为双层但未加稳定性筛选的 Evidence；T4 为完整 Evidence 策略。T2 是候选层消融，其候选在正式运行时不进入 Prompt。Nested CV 另报告在外层训练部分重拟合的 T0 工作流，避免把旧发布已经见过的开发样本伪装成外层未见。

实际导出 1538 份样本图，平均正式 CueEvidence 7.236，实际 Prompt Cue 6.644，fallback 0.00%。

每份样本保留全部 42×16 CA 和 42×188 CE 有符号贡献、bias、logits、CueSignal、CandidateCue、独立 masks、逐输出 hidden/visible 支持状态，以及实际图边和 Prompt 单元暴露标记。只有 evidence_active 创建正式 CueEvidence。model_only / partially_supported 的关系输出留在审计层，不伪装成可见证据的完整结论；没有正式关系但存在正式 Cue 的样本可走 Cue-only 路由。

自动验收 33 项通过；全部内部样本的原始 G1 logit 最大差异 0，贡献加 bias 闭合最大误差 3.55e-15。

## 人工审计与后续边界

本轮不要求人工审计、不新增人工标注、不使用人工标签调参。现有工作台 positive-only / Teacher-visible 结果未被当作完整独立精度审计。当前是完成内部验证的工程版本；后续若要宣称独立人工验证的 Evidence Precision，仍需另做合适审计。

本轮未运行 AffectGPT 配对生成或九目标数据集下游评测，不宣称下游净收益。源域开发样本有历史 Student 选模和旧版校准曝光；全部校准监督为现有 Teacher 伪标签。来源组缺少原始视频/Speaker/Session 元数据，Group Bootstrap 不等于已解决全部来源相关性。42 个 Cue 的区间是边际区间，不是全体同时保证。

## 使用

```python
from amg_graph_v2.v21.runtime import SampleGraphV21
engine = SampleGraphV21('/ai/sjq/AffectGPT-sjq/graph/amg_graph_v2/releases/amg_v2_1_cue_admission_8a8994fe1e7495f0')
sample_graph = engine.build_from_old_cue(old_cue_output)
prompt = engine.prompt(sample_graph, task='open_vocabulary', mode='relation_aware')
# 可对照 mode=node_only；Candidate 永远只在审计层。
```

主要文件：`graph.json`、`graph.graphml`、`graph_viewer.html`；`admission/` 双层策略与稳定性；`calibration/` OOF/最终校准器；`validation/` Nested CV、T0–T4、可靠性图与验收；`runtime/internal_evaluation_sample_graphs.jsonl.gz` 完整样本图及贡献账本。

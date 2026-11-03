# P4 源域查询参数选择

状态：只使用3,076条固定pseudo_validation完成预注册参数选择并冻结；未使用人工审计、独立保留或目标集。

预注册：e26564f91580a5003afe1d9af271c88f5ef95521c04be16f7af56e520c42a45a
Runtime：9975dfee6976c0ad18e971394501d7effb6cf95a08020cc9369ab95d621786aa
最终配置ID：ac35200d82683b116f9cb1ad0f58d119d6eda556339edf87cf3c7f4c69c7f3ff

## 选择方法

先逐维选择delta，再在4个覆盖率profile上比较lambda和Emotion K，最后选择路径K。评价分母保留全部固定验证样本；各Teacher参考mask单独生效，缺失/无效标注不当负例。有效Appraisal维度上的弃判计为漏检。
主目标为Appraisal宏状态F1与Emotion样本宏F1@K均值；按预注册规则打破平局。
查询支持5/10/20、联合支持0/1/3/5在当前冻结正式图上等价，最终20/5来自平局规则，不表示重新比较构图统计后发现最优。

## 冻结参数

```json
{
  "query_min_support_groups": 20,
  "query_path_min_joint_support_groups": 5,
  "dimension_min_evidence": {
    "APP_GOAL_RELEVANCE": 0.0,
    "APP_GOAL_CONGRUENCE": 0.01,
    "APP_EXPECTEDNESS": 0.025,
    "APP_AGENCY": 0.025,
    "APP_CERTAINTY": 0.025,
    "APP_COPING_POTENTIAL": 0.0
  },
  "minimum_coverage": 0.0,
  "emotion_top_k": 3,
  "path_top_k": 10,
  "direct_two_hop_lambda": 0.75,
  "branch": "full"
}
```

## 源域Teacher一致性检索表现

- Appraisal宏状态F1@1：0.4520601147
- Appraisal宏状态Recall@1：0.5349481368
- 有效Appraisal维度查询覆盖率：0.9780332933
- Emotion样本宏Precision@K：0.2359213595
- Emotion样本宏Recall@K：0.2650156297
- Emotion样本宏F1@K：0.2401045158
- Emotion有效参考：3001条；查询覆盖率：1.0000000000
- 两项F1均值：0.3460823152
- 证据预览平均字符：10420.49；平均UTF8字节：10420.49。这不是最终AffectGPT token长度。

## 分维度结果

|维度|有效参考|宏状态Precision|宏状态Recall|宏状态F1|覆盖率|弃判率|
|---|---:|---:|---:|---:|---:|---:|
|APP_GOAL_RELEVANCE|1424|0.508845|0.621891|0.213382|0.915730|0.084270|
|APP_GOAL_CONGRUENCE|988|0.542028|0.582485|0.557136|1.000000|0.000000|
|APP_EXPECTEDNESS|497|0.611175|0.636963|0.605138|1.000000|0.000000|
|APP_AGENCY|960|0.307284|0.331468|0.279269|0.992708|0.007292|
|APP_CERTAINTY|1694|0.689149|0.767916|0.689974|0.999410|0.000590|
|APP_COPING_POTENTIAL|264|0.504502|0.477435|0.475829|1.000000|0.000000|

## 验证与产物

所有3,076条预测均由P0/P2锁定的best权重重新生成，并保存原始模态指纹；没有使用validation.last.npz。四个profile对全部样本的Appraisal输出均与冻结引擎一致；每个profile固定4个样本的全部15个lambda/K组合与原引擎精确一致；最终配置在全部3,076条样本上重放，聚合指标与网格一致。
冻结图文件指纹、Cue阈值与策略未变；无训练和Teacher调用。

- query_engine_config.json：P5使用的冻结查询参数。
- query_validation_results.csv / stage_B_grid_results.json：720项声明候选及60种不同行为的结果。
- stage_A_results.json / stage_A_profiles.json：逐维delta选择及完整状态计数。
- stage_C_path_results.json：路径K、解释覆盖和上下文大小。
- per_sample_query_results.jsonl / per_sample_metrics.csv：逐样本证据与评分。
- prediction_manifest.json / reference_manifest.json / evaluation_code_manifest.json：输入与实现指纹。
- selection_manifest.json：版本、方法、指标、限制及最终配置hash。

这些是源域伪标签检索结果，不是人工心理状态准确率、独立测试成绩或目标集表现。后续不得根据目标集反馈调整这些参数。人工active/deferred、P1审计及P5-P7仍须按原协议完成。

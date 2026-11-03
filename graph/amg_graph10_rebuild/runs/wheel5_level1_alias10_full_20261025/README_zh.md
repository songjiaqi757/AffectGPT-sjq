# 十Emotion节点图：完整重新构建
服务器目录：/ai/sjq/AffectGPT-sjq/amg_graph10_rebuild/runs/wheel5_level1_alias10_full_20261025
按用户要求重新执行数据筛选、统计筛边、边权估计、完整路径筛选、结果审计。没有执行构图后的模型训练、模型推理、目标基准测评或部署切换。

## 数据重筛和标签
从31327个源样本重新读取三模态任务状态，78个失败任务涉及72个样本，按整样本排除，保留31255。
重新从源Cue CSV重建42维标签/掩码，与冻结版一致，逐条核对93765份Cue标注。
使用被冻结的角色划分：pseudo_train27679拟合、pseudo_validation3076选择门槛、gold_audit300与diagnostic_reserved200保留排除。
精确重复组按冻结SHA重新核对；检查62510个原媒体的大小/mtime。本轮未重哈希媒体内容，未执行新的人工作业或近重复/原始来源审计。
Emotion从原始openset标签重新执行五套AffectGPT原版case3 Level1映射、取并集、显式17到10同义合并和逐样本去重。
训练27115个样本映射非空、564个空映射屏蔽Emotion；验证3003个非空、73个空映射。仍保留空Emotion样本的有效Cue/Appraisal。
Appraisal已有逐样本标注重新读取、格式验证和维度有效性检查。没有重新调用Teacher。

## 统计重算和门槛选择
独立重新计算全部1252候选边，1000次共享分组bootstrap，采用NPMI95%置信区间下界为边权。
完整关系族BH q<0.05、有效bootstrap>=950、CI下界>0，边支持门槛在5/10/20中选择。
路径联合门槛在0/1/3/5中选择，门槛0仍要求三者实际共同出现；选择目标与旧图一致，为Appraisal宏状态Recall@1与Emotion样本宏Recall@5的等权均值。
以下是源域Teacher标签结构代理指标，不能作为模型或目标数据集性能，也不宜跨188/10类本体直接比较。
每一行均比较了四种路径门槛；四种路径门槛在各行的上述指标相同。
| 边支持门槛 | 统计边数 | Appraisal宏状态Recall@1 | Emotion样本宏Recall@5 | 等权结构分数 |
|---:|---:|---:|---:|---:|
| 5 | 397 | 0.5242856240 | 0.7439619904 | 0.6341238072 |
| 10 | 396 | 0.5242856240 | 0.7439619904 | 0.6341238072 |
| 20 | 389 | 0.5268405413 | 0.7439619904 | 0.6354012659 |
最终选择边门槛20、路径门槛5：边门槛20分数最高，路径门槛并列时按预先规则选择更大门槛5。

## 构图结果
74节点：Cue42、AppraisalDimension6、AppraisalState16、Emotion10。
统计边389：Cue→Appraisal177、Cue→Emotion155、Appraisal→Emotion57；另有HAS_STATE固定边16，总边405。
780条候选三元路径中773条准入，7条因同样本共同支持不足5排除。
准入节点、边权、路径与上一版固定20/5的十节点图一致；本轮从数据筛选和统计估计重新执行，并实际重选全部12组合，没有直接复用上一版统计量。
原188节点图和上一版10节点图及代码保持原样。

## 独立审计
- 原始标签到十Emotion节点：30755样本逐条独立核验。
- 候选2x2统计表、精确单侧检验：全部1252条独立核验；BH完整关系族和bootstrapCI复算。
- 三元联合支持：780条候选路径逐条复算。
- 12组网格指标、排序和最终选择：另一实现独立复算。
- 输入/产物/代码哈希校验；新旧版本保留检查通过。
- 本轮完成统计和文件一致性审计；既有人工与来源/近重复审计限制仍保留。

## 主要文件
- graph/graph.json：最终完整图JSON。
- graph/paths_cue_appraisal_emotion.csv：773条准入完整路径。
- graph/candidate_edge_audit.csv / .parquet：1252条全部候选边。
- graph/candidate_path_audit.csv：780条候选路径审计。
- validation/grid_results.json / .csv：全部12组合及选择。
- manifest/verification.json：全量边和路径独立核验。
- manifest/grid_verification.json：网格指标和选择独立核验。
- manifest/rebuild_comparison.json：与上一版统计/边/路径对比。
- manifest/complete_audit.json：各阶段结果和文件哈希。
- ../../preflight/input_selection.json、selection_audit.csv：数据重筛记录及31327逐样本去留。
- ../../emotion_release/labels.jsonl、verification.json：新情绪标签与核验。
- manifest/source_code_snapshot/：本轮冻结代码。

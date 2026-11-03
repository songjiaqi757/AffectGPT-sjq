# 十个Emotion节点图
服务器目录：/ai/sjq/AffectGPT-sjq/amg_graph10/runs/wheel5_level1_alias10_20261025
映射：从原始openset标签分别调用AffectGPT原始case3、wheel1至wheel5、level1；取五轮终点并集，执行下表同义词合并，逐样本去重。
这是图本体附加合并层；原版映射代码、资源及已有测评方式未修改。genius保持wheel4原名。
节点总数74：Cue42、Appraisal维度6、Appraisal状态16、Emotion10。
统计边389：Cue→Appraisal177、Cue→Emotion155、Appraisal→Emotion57；另有HAS_STATE固定边16，全部边合计405。
完整三元路径773，三元候选780，7条因同样本联合支持不足5排除。

## 数据和规则
训练池27679：27115个样本有Emotion映射，564个空映射样本屏蔽全部Emotion监督；保留其有效Cue/Appraisal信息。
验证池3076：3003个有Emotion映射，73个空映射。验证仅做结构诊断，不参与边拟合或参数选择。
未使用gold_audit、diagnostic_reserved或目标基准数据集。
筛边沿用原图：正样本支持不少于20、1000次共享分组bootstrap、NPMI置信区间下界大于0、完整关系族BH q<0.05、有效bootstrap不少于950次。
边权采用NPMI 95%置信区间下界。路径需要两边均准入且同一训练样本联合支持不少于5。阈值预先固定，没有搜索。
空映射不置neutral，不当作十类全负例。多标签计数按样本去重，别名支持数不相加。

## 节点及支持
| Emotion | 合并原名 | 训练样本支持数 | Cue→Emotion | Appraisal→Emotion | 完整路径 |
|---|---|---:|---:|---:|---:|
| anger | anger, angry, mad | 11560 | 22 | 6 | 98 |
| disgust | disgust, disgusted | 3435 | 22 | 5 | 89 |
| fear | fear, fearful, scared | 14960 | 22 | 6 | 86 |
| joy | happy, joy, joyful | 12143 | 10 | 7 | 71 |
| sad | sad | 13557 | 27 | 6 | 98 |
| surprised | surprised | 7021 | 13 | 3 | 38 |
| peaceful | peaceful | 4001 | 9 | 5 | 66 |
| powerful | powerful | 8606 | 11 | 7 | 71 |
| bad | bad | 6225 | 11 | 6 | 85 |
| genius | genius | 8879 | 8 | 6 | 71 |

## 文件
- graph/graph.json：完整图JSON。
- graph/paths_cue_appraisal_emotion.csv：准入完整路径。
- graph/candidate_edge_audit.parquet、.csv：全部1252条候选边的计数、显著性、置信区间和排除原因。
- graph/candidate_path_audit.csv：全部780条候选路径审计。
- ontology/emotion_concepts_frozen.json：十节点本体。
- manifest/protocol.json：构图协议、输入/代码/产物哈希。
- manifest/verification.json：全部边、FDR、置信区间、路径独立核验。
- manifest/comparison_to_original.json：旧图未改动及Cue→Appraisal完全一致检查。
- ../../emotion_release/labels.jsonl：30755个样本的原始标签、逐轮结果、别名来源和新标签。
- ../../emotion_release/verification.json：逐样本独立重映射核验。

## 每个Emotion的一条高支持路径
- AUD_INTONATION_FALLING → ACT_CERTAIN → anger；联合支持 3582。
- TXT_EVALUATION_NEGATIVE → AGC_INCONGRUENT → disgust；联合支持 619。
- TXT_EVALUATION_NEGATIVE → AGC_INCONGRUENT → fear；联合支持 2584。
- AUD_INTONATION_FALLING → ACT_CERTAIN → joy；联合支持 3927。
- AUD_INTONATION_FALLING → ACT_CERTAIN → sad；联合支持 4592。
- AUD_INTONATION_RISING → AEX_UNEXPECTED → surprised；联合支持 689。
- AUD_INTONATION_FALLING → ACT_CERTAIN → peaceful；联合支持 1366。
- AUD_INTONATION_FALLING → ACT_CERTAIN → powerful；联合支持 2851。
- TXT_EVALUATION_NEGATIVE → AGC_INCONGRUENT → bad；联合支持 842。
- AUD_INTONATION_FALLING → ACT_CERTAIN → genius；联合支持 2995。
原图和已有训练结果保持原样；新图current指针仅保存在amg_graph10/runs/current.json。
现有训练/推理配置未切换到新图。本次未启动训练、GPU/模型推理或基准测评，没有新的模型性能结论。
图表示源标注统计关联，不代表因果。原始来源/近重复独立性及人工审核的既有限制继续保留。

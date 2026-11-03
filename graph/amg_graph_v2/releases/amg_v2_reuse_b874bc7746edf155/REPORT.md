# AMG v2：复用原 Cue 提取器的图重构结果

Release：`amg_v2_reuse_b874bc7746edf155`

本体 252 个节点；准入学习边 652 条（CA 149、CE 503、AE 0）；另有 16 条 HAS_STATE 固定归属边。

## 范围与实现

按用户要求固定并复用原 Text / Audio / Visual Cue Student，以及已有的 30,755 条源域预测缓存。未训练 Cue 提取器，未训练 AffectGPT，未使用九个目标集。旧图、旧模型和旧运行目录保持原样。

与文档的明确差异：未重新生成 Student 五折 OOF。27,679 条关系训练样本使用旧 Student 的训练内预测；1,538 条用于内部校准和门槛选择，另外 1,538 条用于冻结后的内部关系评估。这些历史验证样本曾参与 Student 选模和 AffectGPT 续训，因此不是全新独立确认集。300 条人工审计与 200 条保留数据未用于本次构建。

CA 为六维独立 Softmax，逐维 Appraisal Mask。AE 使用关系模型交叉拟合的 Appraisal 预测概率训练，未使用 Teacher one-hot 作为输入。CE / AE 为带 Emotion Mask 的多标签 Logistic。完整映射且非空的源标签集合按冻结协议允许闭世界负例；丢词、OOV、部分映射仅保留已知正例，其他位置屏蔽。

保留 NPMI、纯学习 G1、NPMI 弱先验 G2、稀疏有符号 G3 对照；五折符号稳定性；64 次按已知来源组重采样的 CA / CE / AE 重新拟合；边删除 Brier 增量；逐 Cue 校准、逐维 unresolved、Emotion 门控和 fallback。

## 内部源域结果

|方法|CE Macro AP|CE Brier|CE+AE Macro AP|两跳准入|
|---|---:|---:|---:|---|
|G1|0.108044|0.019432|0.108044|False|
|G2|0.105996|0.019431|0.105996|False|
|G3|0.107829|0.019435|0.107829|False|
|G0_NPMI|0.095670|0.019851|0.095490|False|

主方案固定 G1。其融合系数由内部校准材料选择；当前最优 alpha=0，因此未发现可启用的 AE 增量。AE 参数和所有 3,008 条候选关系仍保留在审计表中，正式证据图不强行补 AE 边或两跳路径。

内部评估样本图 1538 份，平均 14.77 个实例节点、38.77 条边（含 INSTANCE_OF）；fallback 0.33%。类型分布：`{"cue_appraisal": 809, "full": 724, "cue_only": 5}`。

验收通过 26 项关键检查，包括集合/组隔离、Mask、Appraisal cross-fit 独立复算、CE 标量复算、不可用与负例区别、deferred / not_requested、互斥状态、Schema、Cue 顺序、回退与极性/开放词汇保护。

## 文件与使用

- `graph.json` / `graph.graphml`：全局本体和准入关系。
- `graph_viewer.html`：离线图检查器；搜索、缩放、点击查看关系审计。
- `learned_relations/G1.npz`：CA / AE / CE 全部参数及 bias；未准入系数仍可审计。
- `learned_relations/edge_audit.csv`：11,576 条候选边的支持量、符号、Bootstrap 区间、删除增量和准入原因。
- `runtime/internal_evaluation_sample_graphs.jsonl`：1,538 份实际样本子图。
- `runtime/examples/`：实际样本类型示例和空图回退示例。
- `validation/`：方法对照、Bootstrap、逐类指标、样本图统计和验收报告。
- `data/`：分组、数据曝光、缓存身份与标签掩码清单。

```python
from amg_graph_v2.runtime import SampleGraph, prompt_evidence
engine = SampleGraph('/ai/sjq/AffectGPT-sjq/graph/amg_graph_v2/releases/amg_v2_reuse_b874bc7746edf155')
sample_graph = engine.build_from_old_cue(old_cue_output)
# old_cue_output 由未改动的原 StudentRunner 生成；无需重训或换模型。
# 仅在需要源域工程检查时查看；尚未做新的下游验证。
text = prompt_evidence(sample_graph, task='open_vocabulary')
```

保留边的负号只表示模型条件贡献方向，不代表心理因果或反证。分数校准仅来自历史内部开发材料。本 release 是完成验收的图重构工程版本，不宣称满足原方案严格 Student OOF P0，也不宣称提升 AffectGPT 下游成绩。

# CPU诊断：35号基线单seed M0

生成时间：2026-10-15T16:34:28.570768+00:00。所有操作与产物仅在服务器。

本报告只使用既有预测、标注文本、检索轨迹和训练日志。未调用模型、未重新评分、未修改原实验或标签资源；未进行视频盲审。相关措辞仅为待复核候选，不能认定语义等价。

## 已确认的事实

- 既有500条配对结果：54条F1提高、58条下降、388条相同；158条规范化预测集合改变。
- retrieval相对off的micro-F1差为−0.003652，95%配对区间[−0.016927, +0.008111]，没有支持净改善的证据。
- 实际dev近邻共2500个槽，1438个不同fit clip，最热19次；random为1869个不同clip，最热5次。全部实际dev近邻均在fit，未发现同ID、同manifest group或单次top5内部重复。
- group_id只是clip ID，以上不代表跨clip同源视频审计。训练端有self/group过滤代码，但原运行未保存训练近邻ID，无法事后逐步核验。
- retrieval训练启用3213/4002（80.28%），dev启用500/500；19/19 Adapter与392/392 LoRA张量均更新且有限。
- retrieval gate均值0.119998，初始sigmoid(-2)=0.119203；变化小不能单凭此认定学习率过小或分支未使用。
- 邻居标签/描述在本报告中用于离线观察；模型Memory输入是冻结AV特征，不读取这些标签和描述。

## 文件

- summary.json：完整审计、机制计数、来源哈希与限制。
- cases.jsonl：112条逐样本证据，含query、两种预测、既有TP/FP/FN/F1、完整5近邻文本和复核候选。
- case_details.md：同样112条证据的人类可读版本。
- all_dev_retrieval_audit.jsonl：500条检索ID、gate、离线精确标签覆盖与既有F1差。
- neighbor_hubs.json：retrieval/random/current的top25近邻频次及原始标签、字幕、描述。

## 严格词面计分的变化机制

以下均来自既有报告的集合差异与TP/FP/FN，不是新评分。各项可重叠。

|机制|下降58条中|提升54条中|
|---|---:|---:|
|移除原有正确标签|42|7|
|新增正确标签|2|35|
|新增未精确匹配gold的标签|51|18|
|移除未精确匹配gold的标签|19|46|
|TP数量不变|16|21|

## 文本复核候选

表面词形候选如positive mood/positive；相关语义候选如anxiety/unease、frustration/dissatisfaction。后者可能表达不同强度、对象或维度。下面的计数仅表示存在需要人工阅读的词对，不是“只是措辞”的裁定，也不是可挽回分数。

|方向|表面词形候选|相关语义候选|
|---|---:|---:|
|下降|3|15|
|提升|3|9|

## 代表案例：仅文本审查

### samplenew3_00001134（ΔF1 -1.000000）

- gold：anxiety, concern, nervousness
- off：anxiety, concern, nervousness
- retrieval：unease, worry
- query字幕：Why can't you rest assured?
- 实际近邻1：samplenew3_00012986；标签：anger, dissatisfaction, frustration, urgency；字幕：I have already requested to see you three times, but you have been blocking me. Please inform the Prime Minister that I also have important matters to discuss.
只能确认冻结词表下命中/多报/漏报的变化；不能仅凭这些文本认定视听情绪正确性或近邻导致输出变化。完整五近邻及标注描述见case_details.md和cases.jsonl。

### samplenew3_00027108（ΔF1 -0.500000）

- gold：anger, frustration
- off：anger, frustration
- retrieval：anger, dissatisfaction
- query字幕：
- 实际近邻1：samplenew3_00110560；标签：anxiety, irritability, tension；字幕：Did you not see those foreign students?
只能确认冻结词表下命中/多报/漏报的变化；不能仅凭这些文本认定视听情绪正确性或近邻导致输出变化。完整五近邻及标注描述见case_details.md和cases.jsonl。

### samplenew3_00096603（ΔF1 -0.428571）

- gold：concern, tension, uncertainty
- off：concern, tension, uncertainty
- retrieval：calm, composed, concern, uncertainty
- query字幕：But Yina hasn't interviewed me yet.
- 实际近邻1：samplenew3_00015992；标签：anger, anxiety, frustration；字幕：Just now I happened to have said a few bad words about Sun.
只能确认冻结词表下命中/多报/漏报的变化；不能仅凭这些文本认定视听情绪正确性或近邻导致输出变化。完整五近邻及标注描述见case_details.md和cases.jsonl。

### samplenew3_00013653（ΔF1 +0.250000）

- gold：gentle, polite, positive, requesting
- off：gentle, polite, positive mood, requesting
- retrieval：gentle, polite, positive, requesting
- query字幕：I would like to ask you to think of a solution.
- 实际近邻1：samplenew3_00109729；标签：calm, contentment, contrast, happiness, inner peace, metaphor；字幕：Doing business is like fighting a war.
只能确认冻结词表下命中/多报/漏报的变化；不能仅凭这些文本认定视听情绪正确性或近邻导致输出变化。完整五近邻及标注描述见case_details.md和cases.jsonl。

### samplenew3_00047065（ΔF1 +1.000000）

- gold：anger, frustration
- off：calm, empathy, rational, understanding
- retrieval：anger, frustration
- query字幕：The queen is only more headache than us, and the queen is not in a hurry, why should we be in a hurry.
- 实际近邻1：samplenew3_00016623；标签：pride, satisfaction；字幕：These clothes still have to be made by yourself.
只能确认冻结词表下命中/多报/漏报的变化；不能仅凭这些文本认定视听情绪正确性或近邻导致输出变化。完整五近邻及标注描述见case_details.md和cases.jsonl。

### samplenew3_00063251（ΔF1 +0.500000）

- gold：cheerful, light-hearted
- off：cheerful, positive
- retrieval：cheerful, light-hearted
- query字幕：When we meet like-minded people on the road, we can set up a game right there.
- 实际近邻1：samplenew3_00037328；标签：pride, satisfaction；字幕：The outcome of me and him should be considered a half-point difference.
只能确认冻结词表下命中/多报/漏报的变化；不能仅凭这些文本认定视听情绪正确性或近邻导致输出变化。完整五近邻及标注描述见case_details.md和cases.jsonl。

## 条件化下一步

1. 先结合本报告的112条证据检查文本与标签口径；保留原评分资源，不能根据结果临时扩同义词。
2. 等待同一retrieval checkpoint的on/off/random推理干预：若on优于同权重off但不优于random，再优先检查检索内容；若on劣于同权重off，则优先检查Memory注入副作用。
3. 若有明确检索相关性问题，再锁定一个retriever/表示改动；若有明确优化/门控证据，再做单因素小规模训练。当前不支持盲目加大学习率或全31K训练。
4. 如要认定某条情绪判断错误或近邻视听不相关，应另做不看方法身份的视听审查。

## 尚不能回答

没有dev相似度分数、attention权重和token范数，不能从已有trace判断检索置信度或真实注入幅度。off与retrieval分别训练的LoRA不同，现有比较不能把变化完全归因于检索内容；同checkpoint干预完成前不作因果定论。

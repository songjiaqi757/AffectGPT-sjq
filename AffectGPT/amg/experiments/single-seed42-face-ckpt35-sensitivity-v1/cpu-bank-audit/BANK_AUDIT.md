# CPU bank与真实dev选中value审计

生成：2026-10-15T17:08:53.703369+00:00。仅服务器CPU；未加载Qwen、未运行Adapter、未调用GPU、未重新生成或评分。

normal来自已训练retrieval checkpoint的500条真实dev trace；random来自同一个checkpoint的随机Memory干预。不是原五组中另行训练的random模型。

## Bank几何

Bank共4000条，每条1792维；视觉768维、音频1024维分别归一化，均为4000条有效。范数与质心使用全量，成对cosine使用seed42的20000个不同ID有序样本对，允许样本对之间重复。

|模态|平均范数|单位向量质心范数|全量不同ID平均cos|抽样cos p50|抽样cos p95|去全局均值后cos p50|
|---|---:|---:|---:|---:|---:|---:|
|visual|1.000000|0.930678|0.866129|0.870507|0.927066|-0.018067|
|audio|1.000000|0.967648|0.936326|0.940219|0.961641|-0.010483|
|combined|1.414214|0.949343|0.901228|0.903379|0.937589|-0.014934|

## 真实dev的normal/random选中集合

- 每路500×5=2500个value槽；不同邻居normal=1438，同checkpoint random=1869。
- 两路有至少一个相同邻居的query为2/500；完全相同的无序集合0/500。交集数量分布：{0: 498, 1: 2}。
- 最热normal邻居出现19次，random最热5次。均fit-only，无self/same-manifest-group/top5内部重复。
- 既有输出：原始文本完全相同491/500，规范化label集合相同491/500，sample-F1不同9/500。

## 每个query中5个选中value的均值比较

以下先对各自5个实际value求均值，再比较normal/random；不代表query→key分数或Adapter输出。

|模态|mean向量cos均值|cos p05|cos p95|L2差均值|对称相对L2差均值|去bank均值后cos均值|
|---|---:|---:|---:|---:|---:|---:|
|visual|0.950781|0.915533|0.974890|0.298393|0.310533|0.016915|
|audio|0.982307|0.967104|0.990055|0.181258|0.185105|0.007832|
|combined|0.966772|0.946717|0.980597|0.350973|0.255802|0.013725|

## 能与不能得出的结论

当前能独立核验bank的几何与真实选中value集合是否不同，以及共同方向对raw cosine的影响。即使raw cosine较高，也不能据此宣称信息完全相同；去均值后差异只用于几何诊断，不更改正式检索。

现有trace没有真实dev query向量，所以不能测query→key cosine、top5边界、query方向或query条件的attention。本报告没有以fit伪query替代dev。

Value集合/均值不能单独确定Adapter是否抹平差异、LLM是否忽略tokens或门控是否过小。等待独立真实dev AV+Adapter诊断定位，不据此直接调学习率、改评分或扩大训练。

## 文件

- per_query.jsonl：按dev清单顺序的500条真实ID、集合/模态几何、gate与既有输出对照。
- actual_value_means.jsonl：每个真实dev query选中的normal/random各1792维value均值，可按name与后续诊断对齐；不是query embedding。
- summary.json：完整定义、样本seed/数量、统计、限制与输入SHA。
- neighbor_hubs.json：两路前25个hub。
- ARTIFACTS.json：输出SHA与大小。

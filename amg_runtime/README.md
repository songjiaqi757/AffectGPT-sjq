# AMG P2/P3 服务器运行包

本包固定使用 P0 锁定的 text / audio_full / visual_full；原 Cue 预处理和 CueModel.forward 不变。只新增独立运行代码，不重训，不调用 Teacher，不改图。

## 入口

在 /ai/sjq/AffectGPT-sjq 执行，Python 为 /ai/sjq/miniconda3/envs/vllm/bin/python。

```bash
/ai/sjq/miniconda3/envs/vllm/bin/python -m amg_runtime.cli run \
  --input /绝对服务器路径/input.json \
  --output /绝对服务器路径/evidence.json \
  --audit-log /绝对服务器路径/query_audit.jsonl
```

- predict：当前样本原始模态 → 固定42维 Cue 输出。
- query：读取该版本 P2 输出 → 图关联证据。
- run：顺序执行 predict 和 query。
- --release：指定本包版本目录；缺省读取 amg_runtime/releases/current.json。
- --query-config：显式传入查询实验配置；每条输出记录配置内容及 hash。
- --profile engineering（默认）：固定0.5未校准阈值，开放原42个监督槽位用于工程检查；不代表人工审核后 active。
- --profile deployment：在人工 active/deferred 冻结前，全部暂缓查询并返回原始 AffectGPT 回退请求。

输入为对象或对象数组，只接受 sample_id、text.chinese/english、audio_path、video_path；媒体使用服务器绝对路径。所有标签、Teacher 输出及历史情绪字段均拒绝输入。

## 语义与版本

scores 始终42维。模态不可用的槽位为 null；availability_mask、active_mask、deferred_mask、requested_mask、selected_mask 分开保存。0.5为未校准工程阈值；既不把低分当不可观察，也不按分数推断 uncertain。

权重通过静态 Torch ZIP 描述读取 model 张量，无 pickle 调用执行；只把三路 model 参数无损导出为 safetensors。原 checkpoint、编码器文件、图、历史 release 均保留。运行时验证代码、图、输入及权重指纹，发生漂移则拒绝加载。

直接和两跳分数按图构建.md 第6节实现。Z 包括全部有效查询 Cue；R 使用实际入选三元路径，缺少三元路径不从两端边推断；每维允许 abstain。只有一个分支可用时直接使用该分支分数。图分数是统计关联支持度，不是校准概率、因果结论或最终情绪标签。

只读取冻结正式图的1,048条统计边和2,595条路径。图构建门槛为边20组、路径5组。query_* 参数仅进一步过滤，不能恢复被排除的边或路径。

query_config.engineering.json 仅用于契约测试；维度/覆盖门槛、Top-K和融合系数尚未经P4选择。最终目标集评测仍被版本门槛关闭。

## 回退与后续

结果含 fallback.required/reason/target。GraphQueryEngine.query_or_fallback 接收原始 baseline 回调，空查询、无候选或查询失败时调用一次。实际 AffectGPT 模型接入属于 P5；本包不假装已经运行该模型。

P1 人工与来源审计、P4 源域有限验证及 P5-P7 尚未完成。人工部署策略需在 Cue 方案下另行冻结，不在 AMG 中拟合阈值。

版本目录的 validation/ 保存单元测试、真实源域推理样例、独立矩阵公式核验、查询 JSON/JSONL 及失败日志。测试只检查工程正确性，不报告目标集或人工准确率。

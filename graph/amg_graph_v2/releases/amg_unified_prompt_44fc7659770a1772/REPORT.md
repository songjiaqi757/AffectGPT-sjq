# 统一 Relation-aware AMG Evidence Prompt：实现与输入验收

Release：`amg_unified_prompt_44fc7659770a1772`
冻结图：`amg_v2_1_cue_admission_8a8994fe1e7495f0`

## 本轮结果

已实现独立的统一 Prompt Adapter 和 AffectGPT 追加式接入桥。正式 build() 没有 task / mode 分支；原 v2.1 接口和发布作为 P0 基线保留。新适配器的证据结构不会因离散情绪、极性或开放词汇问题而切换，原问题本身完整保留。

默认候选 P4 输入：正式 Cue ID、确定性英文短描述、两位小数 source-calibrated score；正式 Appraisal / Emotion 假设及从账本读取的有符号样本贡献 C。默认不展示 W、不展示 raw score、不展示高层节点概率，不包含 Candidate / Deferred / model_only / partially_supported，也不生成 AE。

每个目标只使用实际入选 Cue、正式目标和稳定全局边。枚举最多 8 条候选边的组合，精确找到满足绝对贡献和正贡献覆盖均≥0.90的最小关系集合。贡献来自 raw_score × W 的冻结账本，绝不使用展示的校准分数重算。Bias 单独保留于审计，不算作 Cue 贡献覆盖。

预算使用原 AffectGPT Qwen2Tokenizer；原 load_tokenizer_from_LLM、get_prompt_for_multimodal、replace_token_for_multimodal 的实际函数代码经 AST 隔离执行，以避免加载模型权重。正式推理桥接收真实 reader/chat 直接调用相同接口。检查占位符展开后的完整 Prompt + 预留生成长度，预算不足先移除完整低优先级高层假设，再减少末位 Cue 并重算支持；始终不截断原问题、字幕或多模态输入。

**完整保留 1,538 个内部样本，排除数为 0。16 个代表样本已导出 P0–P5 共 96 组配对输入；35 项验收通过。**

|全量内部输入指标|结果|
|---|---:|
|样本数|1538|
|平均 AMG token|386.51|
|AMG token P95|524.60|
|最大 AMG token|852 / 1000|
|最大完整展开 Prompt token|964 / 1536|
|预留生成长度|512|
|总窗口限制|2048|
|实际 CA 关系数|1366|
|实际 CE 关系数|557|
|实际负贡献关系数|552|
|AMG fallback 样本|0|

## 配对输入消融

|条件|代表样本数|平均 AMG token|最大完整 Prompt token|CA 边|CE 边|
|---|---:|---:|---:|---:|---:|
|P0|16|132.62|282|0|0|
|P1|16|306.81|458|0|0|
|P2|16|359.62|520|0|0|
|P3|16|373.69|520|0|0|
|P4|16|454.81|961|38|32|
|P5|16|482.88|1018|33|32|

P0 为旧 v2.1 open-vocabulary/relation-aware Prompt；P1 描述；P2 描述+Cue 分数；P3 再加高层假设；P4 显式样本贡献 C；P5 追加 W。Score-A/B/C 和 W-only 作为独立离线实验辅助接口提供，生产接口不暴露这些分支。

代表样本覆盖 Cue-only、正式 CA、正式 CE、CA/CE 同时存在、高低分并存、实际负贡献和最大长度样本。“跨模态对比模式”仅指 Cue 组合测试，不冒称人工核验的情绪冲突。来源标签、目标标签均未用于选择或调节 Prompt 参数。

## 验收证据

- 跨任务原问题不同而 AMG 文本一致；原问题、字幕、模态标记和传入特征对象保持原样。
- Cue 分数来自 source_calibrated_score；贡献与原 raw-score 账本逐项一致，正负号保留。
- 正式高层节点、稳定边、Top-8 后二次 90% 支持和最小关系基数均检查。
- 无正式 Cue、极小预算、原输入自身超长、错误图版本、篡改贡献均有相应回退或拒绝。
- 生产默认候选不传 W / raw score / 高层概率；Cue-only 不产生空 CA/CE 段。
- 图、G1、Cue Student、准入策略及全部原图发布产物保持冻结。

## 实际生成状态

**本轮完成的是输入、token 和接入契约验证，不是实际模型生成消融。** 两台服务器 GPU 均被现有任务占满（快照见 validation/）。没有停止、修改或抢占已有作业。录制式 Chat 仅用于验证传参契约，不是真实 AffectGPT 输出。

P0–P5 实际生成和九目标数据集评测均未运行；因此不能声称新 Prompt 提高了性能，也尚未把 P4 定为经过生成验证的正式默认。提供 generation.run_paired_generation()，可在加载同一冻结 AffectGPT Predictor 后，用相同原始多模态特征和相同解码设置执行已冻结的配对输入。

## 接入

```python
from amg_graph_v2.unified_prompt.adapter import UnifiedAMGPromptAdapter
from amg_graph_v2.unified_prompt.integration import AffectGPTUnifiedBridge

adapter = UnifiedAMGPromptAdapter(chat.tokenizer)
bridge = AffectGPTUnifiedBridge(adapter)
prepared = bridge.prepare(reader, chat, sample_graph, original_question, subtitle,
                          max_length=2048, max_new_tokens=512)
# 使用原有模态编码结果；只追加 AMG 文本，原任务与媒体不变。
response, audit = bridge.generate_with_features(
    reader, chat, sample_graph, original_question, subtitle, original_img_list,
    max_length=2048, max_new_tokens=512, do_sample=False)
```

主要资产：prompts/all_internal_P4_packets.jsonl.gz 为全量完整输入；prompts/source_probe_P0_P5.jsonl 为代表样本配对输入；examples 为真实文本与贡献；validation 包含验收、token 预算、原图冻结和实际生成未运行状态；source_snapshot 保存实现与原方案。

所有读取、写入和验证均在服务器内完成，未将项目或产物下载到本地。

# P2/P3 工程实现与验收

状态：P2/P3 工程实现完成并通过验证；正式部署及最终目标集评测仍关闭。

完成时间（北京时间）：2026-10-22T11:50:24.161017+08:00
Runtime release ID：9975dfee6976c0ad18e971394501d7effb6cf95a08020cc9369ab95d621786aa
P0 lock ID：76eac932b109b29455aef081a5da79a48f9f1fa3055fef718c0d1b58fa72bebb

## 实现

- P2：锁定 text / audio_full / visual_full；固定42维顺序；分开记录 scores、模态可用性、active/deferred、requested/selected 及版本诊断。
- 原始 checkpoint 仅静态读取张量，三路 safetensors 逐张量无损核验；运行时不执行 checkpoint pickle。原预处理与 CueModel.forward 保留。
- 工程模式沿用0.5未校准阈值，并明确标记42槽位尚未完成人工 active 判断；部署模式全部暂缓，返回回退请求。
- P3：直接关联、Appraisal 状态支持与覆盖率、联合支持比 R、维度加权两跳、缺失分支回退、融合、Top-K 和解释路径。
- 查询只过滤现有正式图。构图边20组、路径5组准入规则保持不变；查询过滤不会恢复被排除的路径。
- 每条查询保留输入快照、有效 Cue、配置和版本 hash、边/路径 ID、权重、来源组支持、联合支持、门控和回退状态。

## 验证

- 40项单元/边界测试通过，包括独立手算公式、门控、阈值边界、mask、缺失输入、身份漂移和标签拒绝。
- 30项真实GPU集成检查通过；12种预测/查询样例来自2条源域验证样本及其边界变体。
- 重复推理、单样本与batch接口输出逐项一致。batch接口按原predict的方式逐样本执行，未声称张量批量提速。
- 真实冻结图上用52组无标签合成Cue分数进行独立NumPy矩阵对照，比较2516个候选分数，最大绝对误差5.55e-17。
- CLI与API图查询结果完全一致；无输入时CLI输出明确回退。
- 65个原数据/图/Emotion文件哈希不变，9组原checkpoint的大小/mtime不变。
- 另1项旧图文档修订元数据由并发媒体副本清理更新；已独立确认旧正文仅插入存储说明，冻结图的全部源输入指纹与Appraisal摘要仍一致。详情见validation/concurrent_cleanup_verification.json。

## 产物与复现

- release_manifest.json：代码、配置、schema及输入版本。
- cue_policy.json：两种明确标记的策略profile。
- query_config.engineering.json：仅供工程契约测试的可运行参数，未经P4选择。
- weights/与export_*.json：推理权重与无损转换证据。
- schemas/：原始输入、42维Cue、图结果、查询配置JSON schema。
- validation/acceptance_report.json：机器可读验收报告。
- validation/source_smoke_inputs.json：服务器上的源域复现实例。
- validation/cue_smoke_predictions.json / query_smoke_results.json / query_audit.jsonl：完整输出与日志。
- validation/integration_report.json / dense_oracle_report.json / unit_test_report.json：验证证据。
- amg_runtime/README.md：CLI用法与语义说明。

所有模型和数据操作均在服务器进行，无模型训练、Teacher请求、图重建或目标集标签使用。真实AffectGPT模型接入属于P5；本次验证的是回退回调契约，不声称已运行AffectGPT。

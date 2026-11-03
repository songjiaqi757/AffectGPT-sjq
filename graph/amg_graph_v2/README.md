# AMG v2 图重构（复用原 Cue Student）

当前发布入口：`current.json`。仅在服务器目录内工作。旧图和旧 Cue 提取器没有修改。

数据准备 `prepare.py`；旧 Student 缓存身份核验 `reuse_cues.py`；关系学习与审计 `fit.py`；样本图运行时 `runtime.py`；冻结导出 `release.py`；验收 `verify.py`。

Cue Student 保持原发布，未重训、未重新生成 OOF。新建五折仅用于图关系 cross-fitting 和边稳定性。详细差异、源域曝光和准入门槛见发布 REPORT.md。

复现从项目 graph 目录使用 `/ai/sjq/miniconda3/envs/vllm/bin/python -B -m amg_graph_v2...`。冻结发布不可覆盖。临时冻结预训练编码器特征分支在确定用户范围后已停止，未训练预测头，也不参与最终图。

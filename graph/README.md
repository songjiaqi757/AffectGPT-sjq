# 图相关工程与实验

实体目录：/ai/sjq/AffectGPT-sjq/graph

图代码、标注、Cue 学生模型、训练与消融、报告均在此实体目录内，旧根目录入口已移除。
原始 AffectGPT 与数据分别使用 /ai/sjq/AffectGPT-sjq/AffectGPT 和 /ai/sjq/AffectGPT-sjq/dataset 的实际目录。
本次整理创建的 31 个软链接已全部删除。

目录索引及当前结果：paths.json。
当前图构建方案：图构建.md（v2.0，可学习关系图与样本级证据子图；实现 amg_graph_v2/，当前发布入口 amg_graph_v2/current.json）。
v2.1 改进方案：/ai/sjq/AffectGPT-sjq/改进方案.md（Cue 阈值校准与双层证据准入；实现 amg_graph_v2/v21/，入口 amg_graph_v2/current_v21.json）。
历史方案：archive/图构建_v2.9_NPMI_20261022.md（v2.9 全局 NPMI 统计图，已由 v2.0 替代，仅作 v1 时代实验的溯源记录，不再是当前实现）。
Cue 提取与训练方案：Cue 提取与训练执行方案.md。
最新分析：amg_method_decision/runs/decision_20261028_200538/analysis/FINAL_ANALYSIS_20261029.md。
资源配置：amg_188_path_noemotion/server_resources.json，A800/A100 各四路推理。

## 启动

    cd /ai/sjq/AffectGPT-sjq/graph
    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -B -m amg_runtime.cli --help

或从工程根目录运行：

    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -B graph/run.py amg_runtime.cli --help

## 历史记录

历史结果、冻结计划和选择记录保留原始字节；旧路径由 graph_paths.py 在读取时解析到实际位置。
代码和可编辑配置已使用新路径。代码指纹变化逐项记录在
_organization/20261029_no_symlinks/source_migration.json，并保存修改前原文。
历史源代码校验只接受该清单中精确对应的改动；其他漂移仍然失败。
本次没有重新训练或改动指标。完整验证见 _organization/20261029_no_symlinks/。

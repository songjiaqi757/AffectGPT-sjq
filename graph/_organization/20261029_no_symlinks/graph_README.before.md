# 图相关工程与实验

统一实体目录：/ai/sjq/AffectGPT-sjq/graph

本次只整理目录与导航入口；模型、训练设置、推理逻辑、实验结果、冻结计划和源代码内容保持原样。
旧根目录的同名项目是兼容软链接，历史绝对路径、Python 包名和冻结文件哈希仍然有效。
AffectGPT/、dataset/ 在这里是指向原始模型工程和数据的依赖软链接，未复制这些内容。

## 内容位置

| 内容 | 目录或文件 |
| --- | --- |
| 图构建方案 | 图构建.md |
| Cue 提取、训练方案 | Cue 提取与训练执行方案.md |
| Cue/Appraisal 标注 | cue_annotation/、appraisal_annotation/ |
| Cue 学生模型、保留标注集 | cue_student/、human_annotation/ |
| Emotion 节点 | emotion_nodes/ |
| 图构建：188 节点及 10 类版本 | amg_graph/、amg_graph10/、amg_graph10_rebuild/ |
| 图查询运行时 | amg_runtime/ |
| 训练与对照 | amg_finetune*/、amg_bcd*/、amg_d_*/、amg_polarity/ |
| 推理、验证、修复 | amg_inference/、amg_validation/、amg_repair_cpu/ |
| 提示与路径消融 | amg_prompt_ablation*/、amg_188_audit/、amg_188_path_noemotion/ |
| 最新方法判定实验 | amg_method_decision/ |
| 跨实验报告 | analysis_reports/ |
| 历次数据迁移记录 | data_migrations/ |
| 规范路径、当前结果入口 | paths.json |
| 此次整理的清单、备份与验证 | _organization/20261029/ |

## 当前结果与资源配置

- 最终分析：amg_method_decision/runs/decision_20261028_200538/analysis/FINAL_ANALYSIS_20261029.md
- 方法判定：amg_method_decision/runs/decision_20261028_200538/method_decision.json
- A800/A100 配置：amg_188_path_noemotion/server_resources.json
- 当前实验：amg_method_decision/current_run.json

## 执行方法

使用服务器现有环境，保留原来的 Python 包名：

    cd /ai/sjq/AffectGPT-sjq
    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -B graph/run.py amg_runtime.cli --help

也可进入 graph/ 后按原包名执行 python -m amg_runtime.cli --help。
兼容软链接是历史计划和第三方脚本的路径保障，不代表另有一份数据。请勿直接删除。
历史报告内部的旧路径可直接访问，其规范新路径可通过 paths.json 查询。

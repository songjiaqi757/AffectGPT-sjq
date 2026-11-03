# CPU graph evidence experiments

所有文件只在服务器 `/ai/sjq/AffectGPT-sjq/graph` 内保存。现有图、训练与推理配置没有被替换。

## 当前决定

默认保留原十类图。条件分布替换和严格门控没有改善源域整体情绪检索，因此只作为实验分支保留。没有运行新的 GPU 推理或训练。

最终报告：
`/ai/sjq/AffectGPT-sjq/graph/analysis_reports/graph_repair_steps1_3_20261026.md`

之前四项诊断报告：
`/ai/sjq/AffectGPT-sjq/graph/analysis_reports/cpu_four_checks_20261026.md`

最终拟合与结果：
`/ai/sjq/AffectGPT-sjq/graph/amg_repair_cpu/runs/20261026_final/`

- `config.json`：来源、阈值、版本、输入和代码 SHA256、拟合文件校验值。
- `fitted.npz`：训练计数、状态先验、条件分布、适用性 CPU 模型与原图矩阵。
- `results.json`：各分支指标、逐状态混淆、阈值选择、配对 bootstrap、检查。
- `per_sample.jsonl`：3,076 条样本的各分支结果。
- `20261026/exploratory_results.json`：适用性门控之前的探针。
- `runs/20261026_verified/`：加入自动 bootstrap 步骤前的独立复现；正式引用 final。

## 复现

先进入项目目录。输出目录必须是新的目录。

```bash
cd /ai/sjq/AffectGPT-sjq/graph
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/ai/sjq/miniconda3/envs/vllm/bin/python -B -u \
  -m amg_repair_cpu.fit_and_check \
  --output /ai/sjq/AffectGPT-sjq/graph/amg_repair_cpu/runs/NEW_RUN_NAME \
  --native-check
```

只检查接口与门控：

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
/ai/sjq/miniconda3/envs/vllm/bin/python -B \
  -m amg_repair_cpu.verify \
  --run /ai/sjq/AffectGPT-sjq/graph/amg_repair_cpu/runs/20261026_final
```

## 调用接口

```python
from amg_repair_cpu import EvidenceRepair

repair = EvidenceRepair("/ai/sjq/AffectGPT-sjq/graph/amg_repair_cpu/runs/20261026_final")
original = repair.apply(native_ten_class_evidence)  # baseline，原证据深拷贝
candidate = repair.apply(native_ten_class_evidence, ablation="balanced_gated")
```

`native_ten_class_evidence` 应由绑定同一十类图版本的 GraphQueryEngine 生成，并包含冻结 Student 的 input_snapshot。不能把原 188 类图输出直接交给这个接口。

可选分支：
- baseline：原检索/原证据；
- conditional：条件状态分布；
- balanced：除去状态先验的关联分布；
- conditional_gated：条件分布加分维度、适用性及候选门控；
- balanced_gated：去先验分布加上述门控。

`batch(q, ablation=...)` 接受 N×42 非负有限查询权重，用于 CPU 消融。

修复分支返回独立 schema `appraisal_candidate_repair_v1`，包含 Appraisal 状态与逐候选决定。它尚未接入旧提示构建器，不应直接传给原 `format_evidence`。提示表达与同权重生成对照属于下一阶段。

Teacher 的“无有效标注”是缺少源标注支持，不是人工证明心理状态不存在。所有检索指标都不能直接视作九个目标数据集上的模型提升。

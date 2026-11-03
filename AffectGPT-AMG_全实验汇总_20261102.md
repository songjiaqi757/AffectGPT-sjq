# AffectGPT-AMG 全实验汇总

**项目**：`/ai/sjq/AffectGPT-sjq`  
**生成时间**：2026-11-02  
**覆盖范围**：Cue/Appraisal/Emotion 标注与 Cue Student、188 类与 10 类统计图、P4 图检索、图证据续训、九数据集评测、188 类字段消融、路径/提示/软表达消融、最终开发/确认实验，以及 2026-10-31 新增的“七个原始 checkpoint + graph10 推理”实验。  
**数据时点**：新增实验与新结果截至 2026-11-02 15:58；AffectGPT-RL 的图实验仍在运行，OPPO 图实验已完成。

> **阅读提醒**：本文件区分“可部署的单权重成绩”“逐数据集挑最优的拼接成绩”“机制诊断成绩”。三者不能混用；尤其是 75.4334% 是 50 个 checkpoint 在九个测试集上分别挑最高后的 oracle 均值，不对应任何单一模型。

---

## 0. 结论摘要

1. **工程完成度高**：图、查询、Cue Student、标注、版本锁定、哈希与独立复算都做得比较完整；188 类图与 10 类图均可复现加载和查询。
2. **图作为在线推理证据没有稳定增益**：188 类图 A–P 对照中 C 与 P 基本持平；路径条件 H 相对 C/P 在 7/9 集下降；软表达 G 没有超过 Cue-only；最终确认集 Appraisal C−S 区间跨 0。
3. **Appraisal 的语义内容没有被验证**：R40 和 G54 两套权重上，C（正确 Appraisal）相对 S（打乱 Appraisal）都没有稳定优势；R40 上 C 相对 A/B 的提升很可能包含输出稳定性恢复，因为 B 有 11.72% 空回答。
4. **G54+A 的收益主要是权重/训练差异**：确认集 G54+A 相对 R40+A 综合 +3.478pp，但 G54 比 R40 多训练了 45→54，且缺少同预算无图续训对照；不能归因于图。
5. **最佳单权重没有超过既有最好值**：50 个 checkpoint 的最佳单权重 74.0173%，低于上一轮长证据最佳 74.0563%，也低于论文作者缓存逐集最优 74.7689%；只有逐集 oracle 75.4334% 看起来更高。
6. **2026-10-31 新增的七个原始 checkpoint + graph10 实验呈现清晰的任务分裂**：四个离散情绪任务（MER2024、MELD、IEMOCAP 等）提升，四个极性/开放词汇任务（CMUMOSEI、SIMS、SIMSv2、OVMERDPlus）明显下降；七 checkpoint 平均 -0.21pp，最佳单权重仅 +0.69pp。
7. **当前最稳的结论**：图是一个“离散情绪候选先验”，不是稳定的通用增益；它能帮助部分分类任务，但会伤害情感极性/开放词表任务。下一步应优先修证据可判定性、表达、校准与独立验证，而不是继续扩图或扫 checkpoint。

---

## 1. 总体架构

```mermaid
flowchart TD
  S[31,327 源域样本] --> C1[42 Cue Teacher]
  S --> A1[6维16状态 Appraisal Teacher]
  S --> E1[Emotion open-set 标签]
  C1 --> C2[Cue Student: Text/Audio/Visual]
  A1 --> G[全局统计关联图]
  E1 --> G
  C2 --> Q[42维 Cue 概率查询]
  G --> R[直接 Cue→Emotion + 两跳 Cue→Appraisal→Emotion]
  Q --> R
  R --> P[证据分级 level0-3 与 Prompt]
  P --> T[AffectGPT 图证据续训 / 原始权重推理]
  T --> E[九数据集 + 新 MER 材料评测]
```

### 1.1 数据角色

| 角色 | 数量 | 实际用途 |
|---|---:|---|
| `pseudo_train` | 27,679 | Emotion 节点发现、边权、路径联合支持 |
| `pseudo_validation` | 3,076 | P4 查询参数选择；后来并入续训集 |
| `gold_audit` | 300 | 人工审计，不参与建图 |
| `diagnostic_reserved` | 200 | 独立保留，不参与训练/建图/调参 |
| 续训集 | 30,755 | `pseudo_train + pseudo_validation` |
| 人工审计工作台 | 500 | 原 300 + 200 |
| 九个目标测试集 | 12,799 | 评测；但被多轮实验反复使用 |

**关键问题**：`pseudo_validation` 既用于 P4 选参，又进入续训；项目记录 `independent_validation_available=false`，因此不存在真正独立的源域验证集。

### 1.2 图版本

| 版本 | 节点 | 统计边 | 路径 | 状态 |
|---|---:|---:|---:|---|
| `amg_edges_v1_20261022` | 252 | 1,047 | 2,785 | 历史合并 200 诊断集版本 |
| `amg_edges_v2_restore_diagnostic_20261022` | 252 | 1,048 | 2,595 | 当前 188 类图 |
| `amg_graph10` / `graph10_rebuild` | 74 | 389 | 773 | 10 类情绪图 |
| 固定层级边 | — | 16 | — | `AppraisalDimension → AppraisalState` |

---

## 2. 数据、标注与 Cue Student

### 2.1 Cue 标注与 Cue Student

- Cue 本体：42 个，Text 15、Audio 17、Visual 10。
- 原始 31,327 条样本、93,981 个模态任务；成功 93,903，失败 78，涉及 72 个样本，按 `all_modalities_succeeded_v1` 整样本排除。
- 三模态齐全 31,255 条。
- Teacher：`qwen3.8-omni-flash`，分模态独立标注。

Cue Student 九组验证（Teacher 伪标签参考，macro AP）：

| 实验 | macro AP | macro F1@0.5 | micro F1@0.5 |
|---|---:|---:|---:|
| text | **86.32** | 80.14 | 85.22 |
| audio | 78.88 | 70.45 | 79.42 |
| audio_temporal | 77.19 | 69.28 | 79.53 |
| audio_full | **80.37** | 71.43 | 80.33 |
| audio_temporal_full | 79.84 | 71.04 | 80.03 |
| visual | 75.74 | 64.96 | 69.82 |
| visual_temporal | 76.73 | 66.17 | 70.62 |
| visual_full | **81.29** | 72.39 | 76.27 |
| visual_temporal_full | 80.34 | 72.74 | 75.95 |

运行时使用 `text`（XLM-R 全量）、`audio_full`（HuBERT 全量、mean）、`visual_full`（CLIP 全量、mean）。

**限制**：Cue 分数使用 **0.5 未校准阈值**，`calibration=identity/uncalibrated`；engineering profile 42 槽位全部 active，deployment profile 42 槽位全部 deferred，等待人工审计。因此实验使用的是未校准、全槽位的工程策略。

### 2.2 Appraisal 标注

- 31,255 条全部完成；6 维 × 31,255 = 187,530 个维度位置。
- `valid=true`：58,443（**31.16%**）；`valid=false`：129,087（68.84%）。
- 训练分区各维有效样本：

| 维度 | 有效训练样本 |
|---|---:|
| Goal Relevance | 12,395 |
| Goal Congruence | 8,604 |
| Expectedness | 4,645 |
| Agency | 8,258 |
| Certainty | 15,378 |
| Coping Potential | **2,400** |

六个维度可靠性差异很大；Coping Potential 只有 2,400 条有效训练样本，但图查询和提示把它与其他维度同等对待。

### 2.3 Emotion 节点

- 只从 `pseudo_train` 发现并冻结 188 个细粒度 EmotionConcept。
- 原始标签词出现 111,481 次；被原版映射略过 16,507 次（**14.81%**）。
- 训练集 27,115 条有非空映射，564 条为空；验证集 3,003 条非空，73 条为空；2 条验证 OOV 未扩展节点。
- 188 个节点中 **90 个没有任何准入入边**（CE 无入边 91，AE 无入边 114，两者都无 90）。
- CE 入度中位数 1，最大 23；AE 入度中位数 0，最大 6。
- 边权中位数 0.052，95 分位 0.254；大量弱边。

### 2.4 人工审计

500 条工作台：300 `gold_audit` + 200 `diagnostic_reserved`，当前规则 `positive_confirmation_v1`，只确认 positive，可留空；`teacher_visible_assisted_review`，不是盲审。

截至 2026-10-27 的 50 条 submitted 快照：

| 来源 | Precision | Recall | F1 |
|---|---:|---:|---:|
| Text Cue | 73.39 | 89.89 | 80.81 |
| Audio Cue | 59.78 | 76.39 | 67.07 |
| Visual Cue | 68.52 | 87.06 | 76.68 |
| Appraisal | 85.71 | 91.43 | 88.48 |

50 条只能发现问题，不能拟合阈值或宣称人工准确率；300 条 gold 审计仍未完成。

---

## 3. 图构建与查询

### 3.1 188 类图

- 节点：42 Cue + 6 AppraisalDimension + 16 AppraisalState + 188 Emotion = 252。
- 统计边：1,048（CA 177 / CE 670 / AE 201）；固定 `HAS_STATE` 16 条。
- 候选边：11,576；可估计 10,977；准入 1,048。
- 两跳候选路径：3,209；准入 2,595。
- 建图仅用 `pseudo_train`；边权为 NPMI 95% bootstrap 区间下界；准入要求支持组 ≥20、bootstrap 有效 ≥950、NPMI 下界 >0、BH `q<0.05`。
- 路径要求两条边都准入，且同样本三元联合支持 ≥5 个来源组。

**结构问题**：

- 90/188 Emotion 节点不可达；`AAG_SHARED` 和 `ACP_MIXED` 两个 Appraisal 状态没有任何 `Cue→AppraisalState` 入边。
- 42 个 Cue 平均约 14 条 CE 边；一个验证样本平均仍有约 85 个情绪获得某种支持，再截 Top3，区分度很弱。

### 3.2 10 类图

- 节点：42 Cue + 6 Dimension + 16 State + 10 Emotion = 74。
- 统计边：389（CA 177 / CE 155 / AE 57）；路径 773。
- 10 个 Emotion 全部可达；CE 入度 8–27，AE 入度 3–7。
- 合并规则：AffectGPT 原始 case3、wheel1–5、level1，取并集后做显式同义合并；10 类为 anger/disgust/fear/joy/sad/surprised/peaceful/powerful/bad/genius。

### 3.3 P4 源域检索验证

只用 3,076 条 `pseudo_validation`，冻结参数：

- `direct_two_hop_lambda=0.75`
- `emotion_top_k=3`
- `path_top_k=10`
- 每维最多展示 2 个 Appraisal 状态
- 覆盖率门槛 0

| 指标 | 数值 |
|---|---:|
| Appraisal 宏状态 F1@1 | 45.21% |
| Appraisal 宏状态 Recall@1 | 53.49% |
| Emotion 样本宏 Precision@K | 23.59% |
| Emotion 样本宏 Recall@K | 26.50% |
| Emotion 样本宏 F1@K | 24.01% |
| Emotion 查询覆盖率 | 100% |
| 平均证据预览字符数 | 10,420 |

分维度宏 F1：

| 维度 | F1 |
|---|---:|
| Goal Relevance | 21.34% |
| Agency | 27.93% |
| Coping Potential | 47.58% |
| Goal Congruence | 55.71% |
| Expectedness | 60.51% |
| Certainty | 69.00% |

λ 网格（Emotion F1）：0 → 15.48%，0.25 → 19.91%，0.5 → 23.12%，**0.75 → 24.01%**，1.0 → 23.23%。两跳只比纯直接高约 0.78pp；Top 路径约 92% 是 direct，所谓两跳推理大部分退化为直接关联。

### 3.4 查询与提示

查询权重：

$$q_c = p_c \, m_c \, a_c \, \mathbf{1}[p_c \ge \tau_c]$$

图分数是统计关联支持度，不是概率：

$$A(a\mid q)=\frac{\sum_c q_c w_{CA}(c,a)}{Z_q},\qquad D(e\mid q)=\frac{\sum_c q_c w_{CE}(c,e)}{Z_q}$$

$$S_E(e\mid q)=\lambda D(e\mid q)+(1-\lambda)P(e\mid q)$$

证据分级：

| level | 内容 |
|---:|---|
| 0 | 无图证据，回退原始 AffectGPT |
| 1 | 仅弱 Cue |
| 2 | Cue + Appraisal |
| 3 | Cue + Appraisal + Emotion 候选 + 路径 |

训练时 50% 概率强制 level 0；实际 150,000 次训练呈现中 level0 75,173（50.1%）、level1 39（0.03%）、level2 49,268（32.8%）、level3 25,520（17.0%）。只有约 17% 的训练样本真正看到 Emotion 候选/路径。

**表达问题**：每维最多展示 2 个状态，6 维平均约 10.5 个状态；二态维度经常同时展示两个互斥状态（Goal Congruence 92.95%、Expectedness 85.83%、Agency 94.80%、Certainty 87.81%、Coping 80.14%）。提示中删除了支持度、覆盖率、边权，模型看到的是并列候选，不是有强弱的证据。

---

## 4. 全实验总表

| # | 实验 | 设计 | 关键结果 | 结论 |
|---:|---|---|---|---|
| 1 | 原始 AffectGPT face/frame | 7+7 checkpoint × 9 数据集，126 项 | face 最佳单权重 72.98；逐集 oracle 74.09；frame 最佳单权重 72.31 | 原始基线 |
| 2 | 长证据图续训 | 5 起点 × 5 轮 = 25 权重 × 9 = 225 项 | 最佳单权重 74.0563；逐集 oracle 75.0644；五起点平均 +0.38 | 图训练有小幅、不稳定信号 |
| 3 | 第一轮 BCD | B=compact；C=+gate/dropout；D=+Graph-OOF | 五轮三集均值 B 73.54 / C 73.55 / D 74.00 | Graph-OOF 约 +0.45pp，非普遍 |
| 4 | Polarity OOF | B=50%图无极性；C=100%图+极性；D=50%图+极性 | B 73.76 / C 73.51 / D 73.47 | 极性辅助无稳定增益 |
| 5 | 新旧图 D 对比 | 同起点 35，旧图 vs 10 类新图，D36–40 | 新图均值 +0.20，最佳单点 +0.50 | 10 类图仅局部改善 |
| 6 | D multistart10 | 50 checkpoint × 9 = 450 项，639,950 预测 | 最佳单权重 74.0173；oracle 75.4334；50 权重平均 72.5584 | 最佳单权重未超过既有最好值 |
| 7 | 225 推理 | 25 权重 × 9 = 225 项，319,975 预测 | 逐集 oracle 75.0644；最佳单权重 74.0563 | 长证据续训的完整验证 |
| 8 | 188 类 A–P 消融 | 6 条件 × 9 集，76,794 逻辑预测 | C 75.5485、P 75.4293、A 75.0239、E 75.2496 | Appraisal 有局部增量，Emotion 多害 |
| 9 | 路径/列表 H | C/E/P/H，4,777 活跃样本重生成 | H 75.2147；H−C −0.3338；H−P −0.2146 | 删列表保留路径不是修复 |
| 10 | 提示消融 A–F | 2 权重 × 3 集 × 6 组，16,800 回答 | F−E 在 MER M 上 +4.107/+1.786；F 未超 A | 表达影响精确性，但不创造净增益 |
| 11 | G 软表达 | 2 权重 × 3 集，2,800 回答 | graph40 OV G−B +1.159；SIMS −1.748；G−C +0.093 | 不成为统一方案 |
| 12 | 最终开发/确认 | 512+512，2 权重 × 5 条件 × 3 种子，30,720 逻辑回答 | R40 C−S +0.110（跨0）；G54 C−S +0.155（跨0）；G54 A−R40 A +3.478 | Appraisal 未验证；暂定 G54+A |
| 13 | **七原始 checkpoint + graph10** | **7 checkpoint × 9 = 63 项，89,593 预测** | **最佳单权重 73.67；平均 −0.21；分类任务升、极性任务降** | **图是离散情绪先验，不是通用增益** |
| 14 | OPPO + graph10 | 官方权重 × 9 集 | 九集均值 81.2180 vs 纸面 81.05 | 单一运行，无同 checkpoint 无图对照 |
| 15 | AffectGPT-RL + graph10 | 12 checkpoint × 9 = 108 项，166,387 预测 | 进行中 | 尚无结果 |

---

## 5. 最新实验：七个原始 checkpoint + graph10 推理

### 5.1 设置

- 运行目录：`graph/amg_base7_graph10/runs/base7_original_plus_graph10_20261031_122105`
- 权重：`AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230` 的 epoch 30/35/40/45/50/55/60，共 7 个。
- 图：`amg_graph10_rebuild/runs/wheel5_level1_alias10_full_20261025`（release `bfeb27136ed6b95b5cf22e6c285bd62436dbf8208156034c9b0865aa128c5abf`）。
- 条件：Cue + Appraisal + 10 Emotion 节点；policy 为 D（compact+gate），512 token 图预算，最多 2 条路径。
- 数据：九数据集 12,799 条；7 checkpoint × 9 = 63 项；89,593 条预测。
- 生成：保留原版 `do_sample=true, temperature=1.0, top_p=0.9, num_beams=1, max_new_tokens=1200, max_length=2000`；**未额外逐样本固定种子**，单次运行。
- 空输出：1,480 条（1.65%），按原版流程保留并评分。

### 5.2 与原始同 checkpoint 基线的逐 epoch 对比

基线来源：`AffectGPT/output/evaluation_20261016_2140/metrics_all.csv` 的 `face` 变体，同 7 个 checkpoint、同九数据集、同官方主指标。单位：%。

| Epoch | 版本 | MER2023 | MER2024 | MELD | IEMOCAPFour | CMUMOSI | CMUMOSEI | SIMS | SIMSv2 | OV-MERD+ | 九集均值 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 30 | 原始 | 75.20 | 72.16 | 56.02 | 61.52 | 79.81 | 79.81 | 85.22 | 84.98 | 62.06 | 72.98 |
| 30 | graph10 | 78.04 | 78.42 | 58.18 | 65.69 | 80.72 | 74.99 | 85.96 | 84.02 | 57.00 | **73.67** |
| 35 | 原始 | 72.89 | 73.39 | 53.23 | 54.73 | 80.30 | 79.48 | 86.72 | 85.07 | 61.19 | 71.89 |
| 35 | graph10 | 70.83 | 78.92 | 55.71 | 59.84 | 78.43 | 74.89 | 83.82 | 85.35 | 56.63 | 71.60 |
| 40 | 原始 | 75.92 | 75.82 | 54.80 | 57.29 | 79.99 | 76.48 | 88.16 | 85.07 | 61.23 | 72.75 |
| 40 | graph10 | 72.59 | 78.83 | 54.38 | 62.52 | 80.53 | 73.38 | 84.34 | 84.45 | 56.96 | 72.00 |
| 45 | 原始 | 72.75 | 77.31 | 56.23 | 58.58 | 77.54 | 79.81 | 84.46 | 84.20 | 61.79 | 72.52 |
| 45 | graph10 | 73.02 | 79.39 | 60.20 | 65.51 | 79.61 | 75.54 | 84.65 | 83.08 | 56.64 | **73.07** |
| 50 | 原始 | 70.63 | 72.22 | 53.25 | 55.05 | 78.29 | 79.10 | 82.51 | 85.53 | 61.56 | 70.90 |
| 50 | graph10 | 71.51 | 78.65 | 55.16 | 61.75 | 77.13 | 73.45 | 84.06 | 83.56 | 55.32 | 71.18 |
| 55 | 原始 | 75.25 | 75.81 | 54.44 | 59.28 | 77.38 | 79.00 | 85.44 | 85.31 | 59.89 | 72.42 |
| 55 | graph10 | 75.15 | 80.72 | 57.36 | 65.30 | 74.02 | 72.94 | 84.24 | 83.22 | 54.85 | 71.98 |
| 60 | 原始 | 72.71 | 75.30 | 54.38 | 57.95 | 78.01 | 78.59 | 85.95 | 84.97 | 61.56 | 72.16 |
| 60 | graph10 | 72.67 | 79.88 | 54.10 | 62.94 | 78.33 | 70.22 | 81.97 | 82.61 | 52.92 | 70.63 |

逐 epoch 平均变化：

| Epoch | 原始均值 | graph10 均值 | 差值 |
|---:|---:|---:|---:|
| 30 | 72.9764 | 73.6695 | **+0.6931** |
| 35 | 71.8897 | 71.6014 | -0.2883 |
| 40 | 72.7524 | 71.9990 | -0.7535 |
| 45 | 72.5183 | 73.0695 | **+0.5512** |
| 50 | 70.9049 | 71.1776 | +0.2727 |
| 55 | 72.4212 | 71.9780 | -0.4431 |
| 60 | 72.1559 | 70.6259 | **-1.5300** |
| 七 checkpoint 总体 | **72.2313** | **72.0173** | **-0.2140** |

### 5.3 按数据集的七 checkpoint 平均变化

| 数据集 | 原始均值 | graph10 均值 | 差值 | 原始最佳 | graph10 最佳 |
|---|---:|---:|---:|---:|---:|
| MER2023 | 73.62 | 73.40 | **-0.22** | 75.92 | **78.04** |
| MER2024 | 74.57 | 79.26 | **+4.69** | 77.31 | **80.72** |
| MELD | 54.62 | 56.44 | **+1.82** | 56.23 | **60.20** |
| IEMOCAPFour | 57.77 | 63.36 | **+5.59** | 61.52 | **65.69** |
| CMUMOSI | 78.76 | 78.40 | -0.37 | 80.30 | 80.72 |
| CMUMOSEI | 78.90 | 73.63 | **-5.27** | 79.81 | 75.54 |
| SIMS | 85.50 | 84.15 | **-1.35** | 88.16 | 85.96 |
| SIMSv2 | 85.02 | 83.76 | **-1.26** | 85.53 | 85.35 |
| OVMERDPlus | 61.33 | 55.76 | **-5.56** | 62.06 | 57.00 |

**最一致的模式**：

- **离散情绪任务受益**：MER2024 +4.69、IEMOCAP +5.59、MELD +1.82；MER2023 平均 -0.22，但最佳单点 +2.84。
- **极性/开放词汇任务受损**：CMUMOSEI -5.27、OV-MERD+ -5.56、SIMS -1.35、SIMSv2 -1.26。
- 这说明 graph10 提供的主要是**基本情绪类别先验**，而不是情感 valence 先验；对 HIT 类任务可能帮助覆盖，对 WAF/F_s 类任务会把输出推向离散情绪词、破坏整体极性/开放词表。

### 5.4 汇总口径

| 口径 | 原始 7 checkpoint | graph10 7 checkpoint | 差值 |
|---|---:|---:|---:|
| 最佳单权重（九集均值） | 72.9764（epoch30） | **73.6695（epoch30）** | **+0.6931** |
| 逐数据集 oracle（不同 checkpoint 拼接） | 74.0933 | **74.3578** | **+0.2645** |
| 七 checkpoint 总体平均 | 72.2313 | 72.0173 | -0.2140 |
| 对比论文作者缓存逐集最优 | 74.7689 | 74.3578 | -0.4111 |

**结论**：

- graph10 只在 epoch30 这一个权重上带来 +0.69pp 的最佳单点提升；七个 checkpoint 平均反而 -0.21pp。
- 逐集 oracle 仅 +0.26pp，且仍低于论文作者缓存 74.77。
- 不能宣称“推理时加入图普遍提升 AffectGPT”；更准确的表述是“对离散情绪任务有局部帮助，对极性/开放词汇任务有明显伤害”。

### 5.5 证据分布与空输出

每个 epoch 的 gate 分布相同（图缓存冻结）：

| level | 样本数/epoch | 占比 |
|---|---:|---:|
| 0 | 1 | 0.008% |
| 1 | 8 | 0.063% |
| 2 | 9,176 | 71.70% |
| 3 | 3,614 | 28.24% |

即约 28% 的样本看到 3 个 Emotion 候选 + 路径；其余 72% 只看到 Cue + Appraisal。  
空输出按 epoch：30=2、35=41、40=314、45=21、50=340、55=281、60=481；总计 1,480（1.65%），主要来自 MELD 673、CMUMOSEI 344、IEMOCAP 192。晚期 checkpoint 空输出明显增加。

### 5.6 基线公平性说明

- 基线来自原始 `evaluation_20261016_2140` 的 face 七 checkpoint，九数据集、官方主指标、同 checkpoint；但它是**另一次生成运行**，没有逐样本固定种子。
- graph10 运行同样是原版随机采样、单次运行，也没有逐样本种子。
- 因此逐项差值包含生成随机性；±0.5pp 以内不宜过度解释。但 MOSEI/OV 的 -5pp 量级、跨多个 checkpoint 一致，不能全部归为噪声。
- 该实验**没有同一次运行的无图对照**；若要做严格因果比较，需要同一模型、同一次批处理、同随机流下重跑 A（无证据）与 graph10。

---

## 6. 188 类图的关键对照

### 6.1 A–P 字段消融

固定各集历史赢家权重（7 个不同 checkpoint），54 项、76,794 条逻辑预测。九集主指标均值：

| 条件 | 证据 | 九集均值 |
|---|---|---:|
| A | 无额外证据 | 75.0239 |
| B | Cue | 74.5279 |
| C | Cue + Appraisal | **75.5485** |
| D | Cue + Emotion | 74.3943 |
| E | Cue + Appraisal + Emotion，无路径 | 75.2496 |
| P | 原完整提示，含路径 | 75.4293 |

关键差值：

- **C−B = +1.0206pp，7/9 集上升**。
- **E−C = -0.2989pp，8/9 集下降**。
- **P−E = +0.1797pp，6 升 2 降 1 平**。
- **C−P = +0.1192pp，但 9 个逐集区间全部跨 0**。
- C−B 的局部显著：SIMS +3.266 [1.283,5.516]、MER2023 +2.320 [0.369,4.409]；其余多跨 0。
- E−C 在 IEMOCAP -0.887 [-1.584,-0.148]、SIMS -0.250 [-0.812,0.000]、SIMSv2 -0.106 等，整体偏负。

**解释**：Appraisal 块有局部价值，Emotion 候选多数时候有害；但 C 相对 P 没有稳定优势，不能说“删掉路径/Emotion 就更好”。

### 6.2 路径/列表 H 条件

H = P 仅删除 `Emotion hypotheses` 行，路径逐字保留；路径末端仍含情绪词，所以 H 不是“无 Emotion”。

| 条件 | 九集均值 |
|---|---:|
| C（无列表无路径） | 75.5485 |
| E（有列表无路径） | 75.2496 |
| P（有列表有路径） | 75.4293 |
| H（无列表有路径） | **75.2147** |

- H−C = **-0.3338pp**
- H−P = **-0.2146pp**
- 相对 C 和 P 都是 **7/9 集点估计下降**
- 4,777 条活跃样本中保留 9,554 条路径，89.53% 为 direct；路径端点平均仍有 1.86 个情绪。

**结论**：删除显式 Emotion 列表、保留路径，不能修复性能；H 也不是无情绪条件。

### 6.3 提示消融 A–F

两个固定权重（base35、graph40）× 三数据集（MER2023/SIMS/OV）× 六组：

| 权重 | 组 | MER HIT | MER M | SIMS WAF | OV F |
|---|---|---:|---:|---:|---:|
| base35 | A | 70.817 | 50.115 | 86.179 | 61.405 |
| base35 | B | 72.784 | 48.889 | 86.507 | 60.441 |
| base35 | C | 72.339 | 47.804 | 85.716 | 60.757 |
| base35 | D | 73.767 | 46.055 | 86.554 | 59.055 |
| base35 | E | 73.971 | 44.191 | 84.512 | 59.103 |
| base35 | F | 74.845 | 48.299 | 86.260 | 59.804 |
| graph40 | A | 75.774 | 51.399 | 84.257 | 59.825 |
| graph40 | B | 75.453 | 51.408 | 84.765 | 59.554 |
| graph40 | C | 73.778 | 50.087 | 84.765 | 60.621 |
| graph40 | D | 75.388 | 51.590 | 83.997 | 59.775 |
| graph40 | E | 74.281 | 50.541 | 82.994 | 60.476 |
| graph40 | F | 75.712 | 52.327 | 83.027 | 60.232 |

关键：

- base35 E−A：HIT +3.15，但 M **-5.92**；平均预测情绪数 1.479→1.862。
- base35 F−E：M **+4.107** [1.777,6.380]，说明表达确实影响精确性。
- graph40 F−A：HIT -0.062，SIMS -1.231，OV +0.407；F 只是修复 E 的伤害，没有超过 A。
- 没有任何一种证据组合在三个数据集、两个权重上都优于 A。

### 6.4 G 软表达

G = Cue + F 风格软表达 Appraisal，不含 Emotion、不含路径；2,800 条回答，1,718 条复用 F。

| 权重 | 数据集 | G−B 主指标 | 95% 区间 |
|---|---|---:|---|
| base35 | MER2023 | -0.332 | 跨 0 |
| base35 | SIMS | -0.025 | 跨 0 |
| base35 | OV | -0.084 | 跨 0 |
| graph40 | MER2023 | +0.073 | 跨 0 |
| graph40 | SIMS | **-1.748** | [-3.924,+0.302] |
| graph40 | OV | **+1.159** | **[+0.059,+2.285]** |

- 只有 graph40 OV 出现名义正向信号；
- G−C 仅 +0.093，区间跨 0，软表达没有明显优于原 Appraisal；
- G 仍平均展示约 10.5 个状态；Expectedness 85.9%、Certainty 94.8% 的情况同时列出两个互斥状态。

**结论**：删除情绪候选 + 改措辞不是通用修复；OV 可保留为研究分支，但不能升级为统一默认。

---

## 7. 最终开发/确认实验

### 7.1 设计

- 权重：`original_epoch40`（R40）与 `fixed_graph45_to54`（G54）。
- 条件：A 无证据；B Cue；C Cue+原始 Appraisal；S 打乱 Appraisal；P 完整图提示。
- 生成种子：42/2026/2027。
- 开发集与确认集各 512 条（384 MER track1 + 128 MER OV）。
- 共 30,720 条逻辑回答；25,656 次实际生成；5,064 条完全相同提示复用。

### 7.2 确认集结果

| 权重 | 条件 | HIT | M | 极性 WAF | OV F | OV P | OV R |
|---|---|---:|---:|---:|---:|---:|---:|
| R40 | A | 70.637 | 48.279 | 82.779 | 49.642 | 54.812 | 45.592 |
| R40 | B | 68.410 | 44.606 | 85.505 | 51.475 | 54.852 | 48.691 |
| R40 | C | 74.003 | 47.071 | 84.719 | 54.923 | 58.100 | 52.415 |
| R40 | S | 74.801 | 47.301 | 85.372 | 53.905 | 56.180 | 52.144 |
| R40 | P | 73.417 | 46.083 | 83.931 | 53.158 | 55.097 | 51.537 |
| G54 | A | 75.104 | 49.538 | 83.595 | 52.132 | 55.388 | 49.380 |
| G54 | B | 74.823 | 49.617 | 83.208 | 50.436 | 54.490 | 47.060 |
| G54 | C | 74.939 | 50.116 | 83.625 | 52.000 | 55.482 | 49.146 |
| G54 | S | 74.798 | 49.776 | 83.347 | 51.831 | 55.485 | 48.889 |
| G54 | P | 74.843 | 49.934 | 82.840 | 51.603 | 55.469 | 48.429 |

关键配对差值（综合 = HIT 与 OV F 等权）：

| 对照 | 综合差值 | 95% 区间 | 解释 |
|---|---:|---|---|
| R40 C−A | +4.323 | [+2.106,+6.453] | Appraisal 块相对无证据有增益 |
| R40 C−B | +4.520 | [+2.602,+6.451] | 相对 Cue-only 有增益 |
| **R40 C−S** | **+0.110** | **[-1.141,+1.296]** | **相对打乱 Appraisal 无差异** |
| R40 P−A | +3.148 | [+0.393,+5.884] | 完整图提示有增益 |
| G54 B−A | -0.988 | 跨 0 | 图提示无增益 |
| G54 C−A | -0.148 | 跨 0 | 图提示无增益 |
| G54 P−A | -0.394 | 跨 0 | 图提示无增益 |
| **G54 C−S** | **+0.155** | **[-0.347,+0.636]** | **Appraisal 内容无差异** |
| **G54 A−R40 A** | **+3.478** | **[+1.617,+5.325]** | **权重/训练差异显著** |

### 7.3 解释

1. **Appraisal 语义内容没有被验证**：R40 的 C 相对 A/B 看起来很好，但 S 几乎一样好；C−S 只有 +0.11pp。G54 的 C−S 也只有 +0.155pp。提升更可能来自“有结构化提示/输出稳定性”，而不是正确的 Appraisal 语义。
2. **G54+A 的收益主要是权重差异**：G54 比 R40 多训练 45→54，且数据、极性辅助、图呈现都不同；没有同预算无图对照，不能归因于图训练。
3. **G54+A 没有稳定胜过完整图 P**：开发阶段 G54+A 相对 R40+P 仅 +0.439pp，区间跨 0；确认集同口径约 +0.33pp。
4. **R40 空回答严重**：R40 B 为 180/1536（11.72%），C 45、S 55、P 34；G54 全为 0。C 相对 B 的提升可能包含输出稳定性恢复。
5. **确认集上 R40+C/S 的综合分其实高于 G54+A**：R40 C 64.46、R40 S 64.35、G54 A 63.62。但协议规定不能看确认集重选，所以保留 G54+A；这并不说明 G54+A 是确认集观测最优。

### 7.4 最终判定

- `frozen_candidate = fixed_graph45_to54 / A`
- `confirmation_passed = true`
- `Appraisal_validated = false`
- `training_ready = false`
- `source_independence_certified = false`
- 适用范围：新 MER 样本/媒体不相交的暂定实验，不是来源/说话者独立验证，也不是九标准集新最好成绩。

---

## 8. 其他模型：OPPO 与 AffectGPT-RL

### 8.1 OPPO + graph10

- 官方 OPPO 权重 × 九数据集，12,799 条样本；官方 `merbench/evaluation.py`，`full answer`、`use_answer_openset=True`。
- 九集均值：**81.2180%**；纸面均值 81.05%（但九项算术平均为 80.9444%，两组纸面值本身不一致，需核对）。

| 数据集 | 指标 | 纸面值 | OPPO+graph | 差值 |
|---|---|---:|---:|---:|
| CMUMOSI | WAF | 86.50 | 83.88 | -2.62 |
| CMUMOSEI | WAF | 84.63 | 84.03 | -0.60 |
| SIMS | WAF | 86.22 | 88.35 | +2.13 |
| SIMSv2 | WAF | 88.26 | 87.71 | -0.55 |
| MER2023 | HIT | 87.73 | 88.25 | +0.52 |
| MER2024 | HIT | 90.34 | 91.12 | +0.78 |
| MELD | HIT | 64.06 | 67.36 | +3.30 |
| IEMOCAPFour | HIT | 73.60 | 75.38 | +1.78 |
| OVMERDPlus | F_s | 67.16 | 64.88 | -2.28 |

**限制**：没有同 checkpoint、同环境无图对照；与纸面值比较不能隔离图效应。OPPO 与 AffectGPT 的标签空间/评测脚本也不同，不能与上一节直接混算。

### 8.2 AffectGPT-RL + graph10（进行中）

- 范围：AffectGPT-RL epoch 5/10/.../60 共 12 个 checkpoint × 九数据集 = 108 项，166,387 条预测。
- 图：完全复用 `base7_original_plus_graph10_20261031_122105` 的冻结 graph10 缓存与 D compact+gate 格式。
- 推理：RL 保留 1200 new tokens / max_length 2000；官方评分：OV 用 `statistic.py`，其余八集用官方 `evaluation.py`。
- 状态（2026-11-02 15:58）：A800 4 路 + A100 4 路，共 8 路推理进行中；尚无最终 `RESULTS.md`。

### 8.3 base7 noemotion（未完成，不可用）

- `amg_base7_graph10_noemotion/runs/base7_noemotion_20261031_225841` 只完成了少量预测（669 条），没有评分/汇总；不能作为 H 条件或“无 Emotion”对照使用。

---

## 9. 统一结论：什么被证明、什么没有

| 主张 | 证据 | 可靠性 |
|---|---|---|
| 工程实现、版本冻结、哈希复算可靠 | 40+30 项测试、独立 NumPy 对照、manifest | **高** |
| 图检索本身较弱 | P4 Emotion F1 24%、Goal Relevance F1 21%、90/188 节点不可达 | **高** |
| 图作为在线推理证据没有稳定增益 | A–P、C–S、G–B、base7 graph10 多轮对照 | **高** |
| Appraisal 语义内容未被验证 | R40/G54 的 C−S 均跨 0 | **高** |
| Emotion 候选经常有害 | E−C 8/9 集下降；HIT 升但 M/精度降 | **较高** |
| 删除 Emotion 列表/改软表达不是修复 | H、G 结果 | **较高** |
| 10 类图比 188 类图结构更好 | 结构 Recall@5 74.4% vs 33.5%，但下游仅 +0.2~0.5pp | **中等** |
| 图训练有因果收益 | 无同预算无图对照，G54 混杂更多训练 | **未证实** |
| 九数据集达到新 SOTA | 75.4334 是逐集 oracle；最佳单权重 74.0173 < 论文 74.7689 | **不成立** |
| 来源独立泛化 | `source_independence_certified=false`，新集仅 MER | **不成立** |
| 人工心理状态准确率 | 仅 50/500 positive 审计，非盲审 | **不成立** |
| G54+A 是当前最稳候选 | 新 MER 确认集 3 种子通过预设规则 | **暂定/有条件** |
| graph10 对离散情绪任务有局部帮助 | MER2024 +4.69、IEMOCAP +5.59、MELD +1.82（7 checkpoint 平均） | **中等** |
| graph10 对极性/开放词汇任务有害 | MOSEI -5.27、OV -5.56、SIMS -1.35、SIMSv2 -1.26 | **中等偏强** |

---

## 10. 主要风险与限制

1. **没有真正的独立源域验证**：`pseudo_validation` 已用于 P4 选参并进入续训；九测试集被反复查看。
2. **没有同预算无图续训对照**：G54 与 R40 的差异混入训练轮数、数据、极性辅助、图呈现。
3. **来源/说话者独立性未核验**：`source_group_id` 每组仅 1 样本；bootstrap/permutation 实际是样本级；原始视频/说话者映射缺失。
4. **Cue 未校准**：42 个 Cue 全部 0.5 阈值；Teacher→Student 域偏移未知。
5. **Appraisal 稀疏**：valid 31.16%，Coping 仅 2,400；维度可靠性差异大。
6. **Emotion 长尾/不可达**：90/188 无入边；10 类图虽全可达但过于粗糙。
7. **证据表达弱**：平均约 10.5 个状态，互斥状态并列；删除了分数/覆盖率。
8. **评估噪声**：judge 随机性可使完全相同回答极性翻转；多数实验单生成种子；多次比较未校正。
9. **数据重叠**：OV 与训练集有 99 个重复视频；近重复/预训练曝光未完全核清。
10. **空输出**：base7 graph10 为 1.65%，R40 B 为 11.72%；会影响指标解释。
11. **模型/任务混杂**：OPPO、RL、AffectGPT 的标签空间、评测脚本、checkpoint 预算不同，不能直接横比。

---

## 11. 下一步建议

### P0：先修评估与数据基础

1. 冻结当前所有基线（原始 7 checkpoint、G54+A、R40+A/C/S、188 C/P、graph10 7 checkpoint），不再新增同类 checkpoint/提示排列。
2. 统一评分链：所有唯一完整回答/openset 输入按内容 hash 固定 seed 和缓存；同一输入转换一致性必须 100%。
3. 建立真正独立开发集：补齐 1,253 条官方 val 媒体，按视频/说话者/近重复聚类划分；九个已查看测试集不再当开发集。
4. 完成 300 条 gold 审计（至少 150 双标）和 500 条 positive-confirmation；盲审、双人、分维度/分 Cue 报告。
5. 校准 Cue：在独立 held-out 上做 temperature scaling / isotonic / 分 Cue 阈值；区分 active/deferred。

### P1：只做最小的推理对照

固定原始 epoch30/45/55 与 G54，做同一次运行、同一随机流的：

- A 无证据
- B Cue
- C Cue + 正确 Appraisal
- S Cue + 打乱 Appraisal
- G Cue + 软表达 Appraisal，无 Emotion
- H Cue + Appraisal + 路径，无显式 Emotion
- **graph10 完整（Cue+Appraisal+10 Emotion）**
- **graph188 完整**

必须报告：HIT/M、WAF/正负召回、OV P/R、空回答率、平均输出词数、净纠错/伤害；至少 3 个生成种子；按视频/说话者 cluster bootstrap。

**决策规则**：

- 若正确 Appraisal ≈ 打乱 Appraisal：图语义没有被利用，优先改表达/训练目标；
- 若两者都 > 无证据：更像提示格式/输出稳定性效应；
- 若 graph10 只在分类任务升、极性任务降：明确限定使用范围，不要统一默认。

### P2：训练因果对照（只有 P1 通过才做）

必须匹配：同起点、同样本顺序、同 batch、同 lr、同 optimizer、同 5,000/25,000 steps、同极性辅助、同解码/评分；至少 3 个训练种子。

- T0：无图续训
- T1：正确图续训
- T2：打乱图续训
- T3：图 + 候选判别/媒体-图一致性辅助目标

只有 **T1 > T0 且 T1 > T2**，才能说图训练有因果价值。

### P3：如果继续做图，优先改证据表示

1. 每维只输出一个有 margin 的状态，否则 `unknown/abstain`；
2. 提示保留支持度、覆盖率、支持 Cue 数，不要删分数；
3. Appraisal ID 转自然语言；
4. 增加有符号/负向关系，不只保留正 NPMI；
5. 增加主体、时间、评价对象、否定/only/转折范围等实例级字段；
6. 先补 “Cue+Appraisal+路径、无 Emotion” 这个缺失单元；
7. 若 10 类图仍无下游增益，不要再扩 188 类或加 GNN。

### P4：汇报口径

最诚实的叙事是：

> 在大规模多模态情绪模型上，源域统计关联图作为推理提示没有稳定增量；graph10 对离散情绪任务有局部帮助，但会伤害情感极性/开放词表任务。主要瓶颈是证据可判定性、表达、校准和数据来源独立性，而不是图结构本身。

---

## 12. 文件索引

| 文件/目录 | 内容 |
|---|---|
| `graph/图构建.md` | 图 Schema、统计建图、查询公式、P0–P7 计划 |
| `graph/Cue 提取与训练执行方案.md` | 42 Cue 本体、数据划分、Cue Student 训练 |
| `graph/amg_graph/runs/amg_edges_v2_restore_diagnostic_20261022/` | 当前 188 类图、manifest、verification |
| `graph/amg_graph10_rebuild/runs/wheel5_level1_alias10_full_20261025/` | 10 类图完整重建 |
| `graph/amg_runtime/releases/p2p3_20261022_111315/` | P2/P3 Cue 推理 + 查询引擎 |
| `graph/amg_validation/runs/p4_20261022_115620/` | P4 参数选择与检索指标 |
| `graph/amg_finetune_nogc/runs/graph_continue_no_gc_20261022_164836/` | 图证据续训 |
| `graph/amg_inference/runs/graph_225_20261022_174537/` | 25 权重 × 9 数据集 |
| `graph/amg_d_multistart10/runs/d_multistart10_20261025_160152/` | 50 checkpoint 扫描 |
| `graph/amg_188_audit/runs/winner188_20261028_114057/` | A–F–P 字段消融 |
| `graph/amg_188_path_noemotion/runs/path_noemotion_20261028_170538/` | H 条件、路径/列表交互 |
| `graph/amg_prompt_ablation/runs/prompt_ablation_20261027_215553/` | A–F 提示消融 |
| `graph/amg_prompt_ablation_g/runs/g_soft_appraisal_20261028_002141/` | G 软表达 |
| `graph/amg_method_decision/runs/decision_20261028_200538/` | 最终开发/确认实验 |
| **`graph/amg_base7_graph10/runs/base7_original_plus_graph10_20261031_122105/`** | **七原始 checkpoint + graph10 最新实验** |
| `graph/amg_base7_graph10_noemotion/runs/base7_noemotion_20261031_225841/` | noemotion 对照，未完成 |
| `graph/amg_rl_oppo_graph10/runs/official_plus_graph10_20261101_231152/` | OPPO 完成；RL 进行中 |
| `graph/analysis_reports/sample_audit_75_43_20261028/` | 238 例样本审计 |
| `graph/human_annotation/` | 500 条 positive-confirmation 工作台 |
| `graph/appraisal_annotation/` | 6×16 Appraisal Teacher 标注 |
| `graph/cue_annotation/` | 42 Cue Teacher 标注 |
| `graph/cue_student/` | Cue Student 九组训练 |
| `graph/emotion_nodes/` | 188 Emotion 节点与映射 |
| `AffectGPT/output/evaluation_20261016_2140/` | 原始 7+7 checkpoint 基线评测 |
| `AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/..._20261014230/` | 七个原始 checkpoint 权重 |

### 复现入口

```bash
cd /ai/sjq/AffectGPT-sjq/graph

PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -B -m amg_runtime.cli --help
PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m amg_graph.verify
PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m amg_graph.verify_frozen_release
```

### 复现原始 7 checkpoint + graph10 结果

```bash
cd /ai/sjq/AffectGPT-sjq/graph
cat amg_base7_graph10/runs/base7_original_plus_graph10_20261031_122105/RESULTS.md
cat amg_base7_graph10/runs/base7_original_plus_graph10_20261031_122105/STATISTICS.md
column -s, -t < amg_base7_graph10/runs/base7_original_plus_graph10_20261031_122105/per_checkpoint_summary.csv
```

---

## 13. 最终一句话

**AMG 的工程与统计实现已经达到可复现、可审计的水平；但截至 2026-11-02，图作为在线推理证据只在部分离散情绪任务上有局部帮助，在极性/开放词汇任务上反而明显伤害，Appraisal 的语义价值和图训练的因果价值都尚未被严格证明。当前最稳的结论不是“图增强成功”，而是“图是一个任务相关的离散情绪先验，需要更严格的对照、校准和独立验证”。**

# AffectGPT-SJQ / Affective Memory Graph（AMG）阶段性深度分析与后续研究路线

> **文档性质**：研究分析 / 实验复盘 / 方法设计建议  
> **项目**：[songjiaqi757/AffectGPT-sjq](https://github.com/songjiaqi757/AffectGPT-sjq)  
> **重点目录**：[AffectGPT/amg](https://github.com/songjiaqi757/AffectGPT-sjq/tree/master/AffectGPT/amg)  
> **分析对象**：`AffectGPT_深度分析报告.md`、`Affective_Memory_Graph_AffectGPT_方案.md`、`AffectGPT/amg` 实现与现有实验产物  
> **分析日期**：2026-10-16  
> **复核修订**：2026-10-16；已核对代码、逐样本计分、原始实验报告及官方文献。区分已证实事实、机制解释和待验证假设。
> **评测边界**：seed42、4K fit/500 source dev的探索性开发；基础checkpoint已监督全部31,327条source（含dev/holdout）。source normalized open-label micro-F1不是论文九数据集综合分数；bootstrap仅反映本seed样本不确定性，group目前为clip ID。

> **最新实证更新（2026-10-16 21:05）**：语义value四组训练/评测已完成，caption为45.6209%，AV-only为46.0986%，尚无净收益证据；内容替换与完整边界见第47节。

---

## 1. 执行摘要

本项目是在 AffectGPT 基础上探索 **Affective Episodic Memory / Affective Memory Graph（AMG）** 的研究工作。

整个项目应分成三个层次：

1. **AffectGPT 原始能力**
   - 多模态情绪理解；
   - MER-Caption / MER-Caption+；
   - multimodal pre-fusion；
   - 自然语言情绪描述；
   - MER-UniBench。
2. **AMG 的目标方法**
   - 从当前输入构建 Evidence；
   - 从历史训练经验中检索 affective memory；
   - 用 Clip、Situation、Emotion 等节点组织结构化记忆；
   - 通过图传播获得 Graph Tokens；
   - 将 Memory / Graph 信息注入 AffectGPT；
   - 通过 Memory Gate / Abstention 判断何时应该使用或拒绝历史经验。
3. **最初完成并实验验证的 M0（后续实验见第45、47节）**
   - frozen CLIP / HuBERT 特征；
   - AV 特征拼接；
   - exact cosine top-k；
   - MemoryBank；
   - 4 个 Memory Tokens；
   - MemoryAdapter；
   - retrieval / random / current / learned / off 对照；
   - 同 checkpoint intervention；
   - adapter audit；
   - bias recovery / sensitivity validation。

### 最重要的阶段性结论

当前 M0 **没有证明 Memory 有性能收益**：

| 条件        |     micro-F1 |
| --------- | -----------: |
| off       | **46.4437%** |
| retrieval |     46.0784% |
| learned   |     45.8374% |
| current   |     45.9680% |
| random    |     45.7031% |

`retrieval - off = -0.3652 pp`，置信区间跨 0。

更重要的是同 checkpoint 干预：

| 条件        | micro-F1 |
| --------- | -------: |
| retrieval | 46.0784% |
| off       | 46.3749% |
| random    | 46.0733% |

因此：

> `retrieval - random = +0.0051 pp`

几乎为零；500 个 query 中约 **98.2%** 的样本最终得到完全相同的规范化标签集合。

这说明：

> **Retriever返回了不同邻居，但当前系统对正常/随机Memory替换的输出敏感性很低。逐层重放支持Adapter近均值聚合、共同分量主导的解释；尚不能唯一排除原始特征各向异性、token注入与LLM利用方式。**

因此不能把 M0 解释为：

> “Affective Memory 没用。”

更准确的结论是：

> **本次source开发中，现有AV检索与Adapter组合尚无净收益证据。语义化/Situation Memory是值得单独检验的候选方向；现有负结果不证明其必要性或有效性。**

---

# 2. AffectGPT：AMG 为什么值得做

AffectGPT 是 ICML 2025 工作：

> **AffectGPT: A New Dataset, Model, and Benchmark for Emotion Understanding with Multimodal Large Language Models**

论文从三个方面推进多模态情绪理解：

- 数据：MER-Caption；
- 模型：AffectGPT；
- benchmark：MER-UniBench。

论文与项目：

- PMLR：<https://proceedings.mlr.press/v267/lian25a.html>
- arXiv：<https://arxiv.org/abs/2501.16566>
- 官方代码：<https://github.com/zeroQiaoba/AffectGPT>

论文的核心变化，是将 MER 从传统固定类别分类进一步推进到：

> **多模态输入 → 自然语言形式的情绪理解 / 描述。**

MER-Caption 包含超过 115K 样本和 2K+ 细粒度情绪类别；AffectGPT 使用 multimodal pre-fusion 增强不同模态的整合。

## 2.1 AffectGPT 的优势

可以抽象为：

```text
Visual
Audio
Text
  ↓
Multimodal Fusion
  ↓
LLM
  ↓
Natural-language emotion understanding
```

因此 AMG 不应该简单解决：

> “AffectGPT 不知道什么是 sadness。”

真正的问题应该是：

> “AffectGPT 已经具有大量参数化情绪知识，但面对一个具体样本时，能否访问过去的具体情绪经验，并判断哪些历史经验真正与当前情境相关？”

这就是 **parametric memory 与 episodic memory** 的区别。

---

# 3. `AffectGPT_深度分析报告.md` 对 AMG 的关键约束

项目中的深度分析报告：

<https://github.com/songjiaqi757/AffectGPT-sjq/blob/master/AffectGPT\_%E6%B7%B1%E5%BA%A6%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A.md>

其价值不仅在于代码阅读，还在于对数据、训练、checkpoint、评测和可复现性的系统审计。

## 3.1 74.77 不能简单解释成 accuracy

AffectGPT 的综合结果来自多个异质 MER 任务。

因此：

```text
74.77
```

不是一个统一任务上的单一 accuracy。

AMG 后续也必须保持指标定义清晰。

## 3.2 开放式输出与最终 emotion metric 不是同一件事

AffectGPT 的自然语言输出需要进一步抽取 / 映射。

所以：

```text
生成质量
```

与：

```text
最终 emotion metric
```

不是完全等价。

AMG 不应只优化最终标签 shortcut。

## 3.3 checkpoint selection 必须严格避免 test leakage

后续推荐统一遵守：

```text
train → fit
dev   → select
test  → final
```

不能使用 test 选择 checkpoint / 超参数。

## 3.4 checkpoint compatibility 必须显式管理

历史 checkpoint 中存在类似：

```text
video_llama_proj
```

与当前：

```text
affectgpt_proj
```

的命名兼容问题。

因此 AMG 插入 AffectGPT 后必须记录：

- base checkpoint；
- projection mapping；
- AMG checkpoint；
- encoder version；
- feature version。

不能只根据“load 成功”判断实验可比。

---

# 4. 数据重叠：99 个完全相同视频是 AMG 的重要风险

当前分析发现 MER-Caption+ 与 OV-MERD+ 存在：

> **99 个完全相同的视频。**

若 OV-MERD+ 测试集为 532，则：

```text
99 / 532 ≈ 18.61%
```

普通 AffectGPT 中这已经是数据重叠问题。

进入 AMG 后风险更高，因为 Memory 可能保存：

```text
Clip
Situation
Emotion
Caption
```

那么：

```text
Test Video
    ↓
exact / near-exact retrieval
    ↓
Memory
    ↓
Emotion
```

可能形成直接 label leakage。

## 建议

最终实验至少同时披露：

```text
Full Test = 532（主结果）
  ├── confirmed exact overlap = 99
  └── remaining = 433（不等于已完成近重复去重）
```

但不能根据这两个子集选择模型。

应先固定checkpoint/超参数，再做exposure diagnosis。原方案已接受全部31,327条训练并建库、保留99条及532条主评测；本分析不改写该协议，不以剔除99条或重训干净基线作为启动条件。

---

# 5. AMG 真正应该研究的问题

AMG 最有价值的问题不是：

> “HGT 是否比 Transformer 好？”

也不是：

> “RAG 能不能提升 AffectGPT？”

真正的问题是：

# Surface Similarity ≠ Affective Similarity

即：

```text
视觉 / 音频相似
        ≠
情绪经验相似
```

例如两个样本都：

- 低头；
- 少说话；
- 声音较低。

但它们可能分别是：

```text
Situation A:
被拒绝
→ sad / disappointed

Situation B:
比赛前准备
→ nervous / focused
```

raw AV cosine 很可能认为：

```text
A ≈ B
```

但 affective relation 实际是：

```text
Situation A ≠ Situation B
Emotion A ≠ Emotion B
```

所以 AMG 真正应该解决：

> **如何从感知相似性升级到情境化情绪经验相似性。**

---

# 6. 当前 M0 的实现链路

当前 M0 可以抽象成：

```text
Video
  ↓
CLIP frame hidden
  ↓ mean pooling
768-d visual vector

Audio
  ↓
HuBERT hidden
  ↓ mean pooling
1024-d audio vector

       ↓ 各模态分别L2 normalize
       ↓ concat；共同有效模态cosine等权平均

AV retrieval key
       ↓
exact cosine top-k
       ↓
MemoryBank

       ↓
MemoryAdapter
       ↓
4 Memory Tokens
       ↓
AffectGPT
       ↓
emotion prediction
```

这非常适合作为 **minimal baseline**，但不应被视为最终 AMG。

---

# 7. M0 问题一：它还不是完整的 Affective Memory

当前 Memory 主要保存：

```text
visual feature
audio feature
```

所以其含义更接近：

> “这个历史样本在视觉 / 音频空间中与当前样本相似。”

而不是：

> “这个历史样本代表一种与当前情绪情境相关的经验。”

真正的 affective memory 应至少包含：

```text
visual evidence
audio evidence
text evidence
caption
situation
emotion
provenance
```

因此 M0 更准确的名字是：

> **Perceptual Episodic Retrieval**

而不是完整的：

> **Affective Episodic Memory**

---

# 8. M0 问题二：时间信息被过度压缩

当前视觉和音频都进行 mean pooling：

```text
x1
x2
x3
...
xT
 ↓
mean
 ↓
x̄
```

这样会丢失：

- 瞬时表情；
- 音调突然变化；
- 停顿；
- 语速变化；
- 情绪峰值；
- emotion transition。

对于情绪理解，这是危险的。

后续可以考虑：

```text
Temporal Evidence
    ↓
attention pooling
    ↓
K evidence tokens
```

但不建议在当前阶段同时修改 retrieval、adapter、temporal encoder。应逐项实验。

---

# 9. M0 问题三：Retrieval Key 与 Memory Value 没有充分解耦

当前思路容易变成：

```text
feature
 ├── retrieval key
 └── memory value
```

更合理的设计是：

```text
Raw / encoded Memory
        │
        ├──────────────┐
        ↓              ↓
Retrieval Encoder   Value Encoder
        ↓              ↓
projection          projection
        ↓              ↓
L2-normalized key   semantic value
```

例如：

```python
key = normalize(W_k(memory_rep))
value = W_v(memory_rep)
```

而不是：

```python
feature = normalize(raw_feature)
key = feature
value = feature
```

原因是：

- retrieval key 需要稳定、可比较；
- memory value 应尽可能保留语义信息；
- retrieval normalization 不应自动成为 value representation。

---

# 10. M0 问题四：MemoryAdapter 没有表现出真正的选择性

adapter audit 是当前 M0 最重要的诊断之一。

主要发现：

- normal / random 的 Q/K neighbor logit 差异约 `2e-5`；
- attention 接近均匀；
- 5 个 Memory 基本接近平均池化；
- Value MLP 最后一层公共 bias norm 约为 `Wx` 信号的 4.46 倍；
- normal / random 的最终 Value 输出高度共享。

因此：

> 当前MemoryAdapter接近带强共同分量的均值聚合器，query对邻居选择影响很弱。

固定gate后移除Q_MLP(query)，最终token相对L2变化均值仅约4e-7/7e-7。全库不同ID combined平均cosine约0.9012，正常/随机邻居均值raw cosine约0.9668，压缩并非只始于Adapter。共同bias不会消除绝对差值，不能描述成信息不可逆丢失，也不是attention均匀的唯一直接原因。

理想情况应该是：

```text
Memory 1 → high weight
Memory 2 → low
Memory 3 → reject
Memory 4 → high
Memory 5 → low
```

当前更接近：

```text
Memory 1
Memory 2
Memory 3
Memory 4
Memory 5
   ↓
≈ average
```

---

# 11. 同 checkpoint intervention 的意义

同 checkpoint intervention：

```text
固定模型参数
只替换 Memory
```

得到：

| 条件        | micro-F1 |
| --------- | -------: |
| retrieval | 46.0784% |
| off       | 46.3749% |
| random    | 46.0733% |

所以：

```text
retrieval - random = +0.0051 pp
```

几乎为零。

与此同时，retrieval 与 random 在候选层面确实不同：

> 500 个 query 中约 498 个的 top-5 没有交集。

因此不能说：

> “retriever 没有找到不同 Memory。”

更准确的机制图是：

```text
Retriever
  ↓
找到了不同 Memory
  ↓
MemoryAdapter
  ↓
Memory identity 被压缩 / 平均
  ↓
AffectGPT
  ↓
最终预测看不出差异
```

下一阶段先做null-prefix与attention尺度对照，再决定表示改造。不同ID不保证语义相关；attention更尖锐不保证预测更好。

---

# 12. Bias 修复：真实问题，但不是唯一问题

zero-init bias 的 recovery experiment：

```text
普通初始化 retrieval ≈ 45.9177%
zero-init retrieval ≈ 46.3550%
```

变化约：

```text
+0.4373 pp
```

但置信区间：

```text
[-0.0724, +1.0020]
```

点估计未达到预设+0.5pp实际收益门槛，且95%区间跨0；两者是独立判断。

zero-init retrieval 相对自身 off 仍为：

```text
-0.2552 pp
```

因此：

> **bias是已观察到的共同分量来源，单独zero-init尚无净收益证据。**

补充：zero-init retrieval相对自身random为+0.1258pp，micro-F1配对95%区间[+0.0145,+0.2993]pp；仅3/500条sample-F1提高，sample-macro-F1区间仍触0。这是单seed、多项探索性比较中的微弱内容依赖线索，不能写成完全无内容敏感性，也不能认定稳定提升。推理清除已学bias与zero-init重新训练是不同实验；后者bias仍可训练。

至少还要检查：

1. bias；
2. query/key scale；
3. key/value disentanglement；
4. semantic memory content；
5. token injection；
6. LLM 对 Memory 的实际利用。

---

# 13. 为什么 M0 不能否定 Affective Memory

M0 只验证：

```text
Frozen AV feature
+
Global mean pooling
+
Cosine top-k
+
Small MemoryAdapter
+
4 prefix tokens
```

没有验证：

```text
Situation
+
Emotion
+
Caption
+
Learned Evidence
+
Affective retrieval
+
Graph propagation
+
Memory gate
```

所以正确结论是：

```text
当前raw AV + Adapter组合
        ↓
本轮未见净收益
        ↓
分别检验注入/聚合、检索相关性与语义value增益
```

而不是：

```text
Affective Memory
        ↓
useless
```

---

# 14. 相关工作与创新边界

## 14.1 AffectGPT

AffectGPT 解决：

```text
large descriptive emotion data
+
multimodal pre-fusion
+
LLM-based emotion understanding
```

AMG 应解决：

> 参数化情绪知识之外，如何访问具体的历史情绪经验。

---

## 14.2 RAER

> Listen, Watch, and Learn to Feel: Retrieval-Augmented Emotion Reasoning for Compound Emotion Generation

ACL Findings 2025。

官方页面：

<https://aclanthology.org/2025.findings-acl.590/>

RAER 已经涉及：

- retrieval-augmented emotion reasoning；
- multimodal retrieval；
- compound / context-rich emotion；
- reasoning enhancement。

因此 AMG 不能把：

> “首次将 retrieval 引入 multimodal emotion understanding”

作为主要 novelty。

AMG 应强调：

```text
episodic memory
+
situation-aware relation
+
memory reliability / abstention
```

---

## 14.3 AffectAgent

论文：

<https://arxiv.org/abs/2604.12735>

代码：

<https://github.com/Wz1h1NG/AffectAgent>

其流程：

```text
Query Planner
      ↓
Dual-channel Retriever
      ↓
Evidence Filter
      ↓
Emotion Generator
```

并包含：

- cognitive semantic retrieval；
- perceptual audiovisual retrieval；
- evidence filtering；
- retrieval-augmented adaptive fusion；
- modality balancing；
- multi-agent optimization。

因此：

> “retrieval + evidence + emotion reasoning”本身已经不够新。

AMG 应进一步聚焦：

> **memory structure + situation relation + selective memory usage。**

---

## 14.4 HyperEmo-RAG

论文：

<https://arxiv.org/abs/2605.18884>

其方向包括：

- hierarchical emotion taxonomy；
- hyperbolic retrieval；
- evidence graph；
- Tree-Aware Attention；
- EmotionGraphFormer。

与 AMG 在：

```text
Emotion
Graph
RAG
Structured evidence
```

存在概念交叉。

所以：

> **Graph + RAG + Emotion + Token injection 不能单独作为 AMG 的核心创新。**

---

# 15. AMG 最值得收缩出的核心贡献

推荐最终将方法定义为：

# Situation-aware Affective Episodic Memory with Memory Abstention

中文：

> **具有情境感知与记忆拒绝机制的情绪情景记忆。**

三个核心问题：

### 15.1 感知相似不等于情绪相似

```text
AV similarity
      ↓
surface similarity
```

不等于：

```text
affective similarity
```

### 15.2 Memory 必须包含语义

推荐：

```text
Memory_i = {
    visual_evidence,
    audio_evidence,
    text_evidence,
    caption,
    situation,
    emotion,
    provenance
}
```

### 15.3 Memory 不一定应该被使用

不是：

```text
retrieval → always use
```

而是：

```text
retrieval
    ↓
memory quality
    ↓
use / abstain
```

这可能成为 AMG 最有价值的创新之一。

---

# 16. Evidence → Memory → Situation → Emotion 图结构

完整 AMG 可以表示为：

```text
                 Current Evidence
                       │
                       ↓
                 Retrieval Query
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      Memory A      Memory B      Memory C
          │            │            │
       Evidence     Evidence     Evidence
          │            │            │
       Situation    Situation    Situation
          │            │            │
        Emotion      Emotion      Emotion
          └────────────┼────────────┘
                       ↓
                Graph Reasoning
                       ↓
                 Graph Tokens
                       ↓
                  AffectGPT
```

关键不在于“图层数”，而在于：

> **Situation / Emotion 成为判断 Memory 是否相关的结构化中间层。**

---

# 17. R1：检索表示子实验（不替代原方案E1）

原方案E1是Current Evidence→Dynamic Adapter→LLM的生成梯度闭环。本节R1仅研究检索表示，可作为独立预训练/辅助实验；纯contrastive不等于完整E1闭环。

R1要回答：

> raw AV cosine 是否不是好的 affective retrieval representation？

建议：

```text
Current Evidence
      ↓
Evidence Encoder
      ↓
Learned Retrieval Projection
      ↓
Positive / Negative Memory
      ↓
Contrastive Learning
```

## 17.1 Positive

不要简单：

```text
same emotion → positive
```

推荐：

```text
same Situation
+
compatible Emotion
→ positive
```

## 17.2 Negative

至少包括：

### Easy negative

完全不同 Situation。

### Hard negative

AV 很相似，但 Situation 不同。

### Emotion-conflict negative

Situation 相近，但 Emotion 明显冲突。

### Random negative

随机 Memory。

---

# 18. R1辅助loss与完整E1的边界

推荐逐步加入：

```text
R1: L_ret（仅可靠正负pair，unknown忽略）
完整E1: L_gen + λ_s L_sit + λ_r L_ret + λ_p L_pres
Abstention后置为独立实验
```

但不要一开始全部加入。

### R1.1

```text
L_contrastive
```

先验证 retrieval representation。

### R1.2

加入 Situation compatibility。

### R1.3

加入 Emotion compatibility。

### R1.4

Abstention单独验证；完整E1须单独检查L_gen对新Evidence Queries梯度非零，不让辅助loss掩盖生成分支断链。

这样才能知道每个机制的真实作用。

---

# 19. BGE-M3：CLS pooling已核实

`amg/text.py:184`使用`F.normalize(hidden[:, 0], p=2, dim=-1)`。服务器`1_Pooling/config.json`及[官方配置](https://huggingface.co/BAAI/bge-m3/blob/main/1_Pooling/config.json)均明确`pooling_mode_cls_token=true`；[FlagEmbedding官方实现](https://github.com/FlagOpen/FlagEmbedding/blob/master/FlagEmbedding/finetune/embedder/encoder_only/m3/modeling.py)的CLS dense路径同样读取`last_hidden_state[:, 0]`。

当前pooling选择与官方dense路径一致，不应仅凭first-token写法将它列为可疑自定义pooling，也不应无依据改成mean pooling。该项改为已核实配置事实。完整数值等价仍需固定tokenizer、权重revision/hash、max_length（当前128）、截断、normalization和dtype，在相同输入条件下比较；本轮未运行官方库数值一致性测试。文本模块未接入M0，不能解释当前AV-only负结果。

---

# 20. Parametric与Episodic Memory：区分两个研究问题

主协议沿用已接受的全部31,327条训练并建库。P与M重叠不自动使实验无效：可以检验显式检索是否更好地利用已有训练经验，但不能宣称提供了参数训练之外的新经验。

P∩M=∅可作为独立研究分支，不是主方案前置条件。仅从已有全31K checkpoint的Memory删除部分样本不能实现参数曝光隔离。须记录基础项目SFT、Adapter/LoRA、检索监督、概念发现、Memory、dev/test的完整曝光；P∩M=∅本身不保证D/T未曝光，通用预训练曝光未知时应披露。

当前500条source dev/holdout只对新增模块和开发Memory隔离，基础checkpoint已见过它们。现阶段属于增量机制开发；最终532条须披露99条已确认重叠，其余433条不能称完整近重复审计后的干净测试集。

---

# 21. Phase A：先把 MemoryAdapter 机制搞清楚

## A1 已完成

```text
off
retrieval
random
current
learned
```

## A2：Null-prefix control

增加：

```text
null memory
```

即：

> 和 Memory 一样增加 4 个 token，但不携带 Memory 内容。

目的：

区分：

```text
Memory information
```

与：

```text
extra prefix tokens / positional interference
```

这是下一轮优先control。须固定同一训练checkpoint、query、prompt和解码，比较off、retrieval、random、4个零token及bank均值value经原Adapter得到的4个token。bank-mean保留共同表示与query gate、移除邻居身份，不等于严格固定常数prefix；两种null仍占位置且被attention看见，零向量不等于删除token。独立训练learned-prefix不能代替同checkpoint干预。这些是分布外机制探针。

## A3：Key / Value separation

比较：

```text
shared normalized feature
```

与：

```text
normalized retrieval key
+
semantic memory value
```

## A4：Attention temperature

可以测试：

```text
attention(q,k) = softmax(qk / τ)
```

其中 `τ` 可学习。

但一次只改一个变量。

---

# 22. Phase B：真正测试 Memory 内容

固定：

- retrieval；
- top-k；
- adapter架构、输入输出维度及预算；
- AffectGPT基础checkpoint与训练策略。

只改变Memory value内容。新增语义value需要匹配编码/投影及训练；若维度改变，不得直接替换进旧AV Adapter并把分布外结果当公平消融。匹配初始化、容量、token数、曝光和预算，另保留仅增加容量对照。

| Memory                   | 目的                  |
| ------------------------ | ------------------- |
| AV-only                  | M0 baseline         |
| AV + Caption             | 测试语义描述              |
| AV + Situation           | 测试情境                |
| AV + Emotion             | 测试标签信息              |
| AV + Situation + Emotion | 完整 affective memory |
| Label-shuffled           | 检测 label shortcut   |

待检验趋势（不预设一定成立）：

```text
AV-only ≈ off
AV+Caption > AV
AV+Situation > AV
AV+Situation+Emotion > AV+Situation
```

如果出现这种结果，核心论点会很清楚：

> 这些结果可支持语义value增益；Situation结构的贡献仍需排除额外监督、容量、文本长度及普通caption/RAG基线。

---

# 23. Phase C：Situation-aware retrieval

固定同一批候选 Memory。

比较：

```text
Flat Retrieval
      vs
Situation Reranking
      vs
Situation Graph
```

必须保证：

> 三者面对相同候选集。

否则无法判断提升来自：

```text
retrieval improvement
```

还是：

```text
graph reasoning
```

---

# 24. Phase D：Graph 是否真的必要

比较：

### D1

Mean pooling

### D2

Attention pooling

### D3

Set Transformer

### D4

HGT

### D5

HGT + shuffled edges

控制：

```text
same nodes
same memory
same tokens
same training budget
```

如果：

```text
HGT ≈ Set Transformer
```

则不应该强行把 HGT 当核心。

如果：

```text
HGT > Set Transformer
```

并且主要优势出现在：

```text
Situation-conflict
Emotion-conflict
```

场景，则 Graph 才真正有论文价值。

---

# 25. Phase E：Memory Abstention / Gate

当前`memory.py:241`的gate只读取query，不读取Memory或检索分数；固定query替换邻居时gate函数输出不变，不能称已实现Memory可靠性判别。后续gate需显式读取query–memory匹配、分数/分歧、质量及缺失模态。

构造四类Memory；同Situation异Emotion不自动等于有害，需核对主体、事件评价及多标签，不确定关系保留unknown：

## E1 正确 Memory

```text
same situation
compatible emotion
```

## E2 表面相似但错误

```text
high AV similarity
different situation
```

## E3 Situation 相同但 Emotion 冲突

```text
same situation
conflicting emotion
```

## E4 Random

```text
random memory
```

比较：

```text
always-on
vs
learned gate
vs
explicit off
```

---

# 26. 理想的 Gate 结果

真正有说服力的结果不是简单：

```text
AMG +1.2 F1
```

而是：

```text
Correct Memory
→ gate high
→ use memory
→ performance ↑

Random Memory
→ gate low
→ abstain
→ performance ≈ off

Conflicting Memory
→ gate low
→ abstain
→ avoid degradation

Useful Memory
→ gate high
→ improve prediction
```

还需报告use率/coverage、相对同checkpoint off的净增益、受损率及utility regret，排除always-off平凡解。gate低但仍插入零token不保证恢复off；真正abstain须明确跳过token。AUROC/AUPRC衡量区分度，校准另报Brier/ECE或可靠性图。

若上述检验通过，可以支持：

> **模型不是无条件依赖历史经验，而是学会判断什么时候历史经验值得相信。**

---

# 27. 推荐的最终 AMG 架构

```text
                   Multimodal Current Input
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
           Visual        Audio        Text/ASR
              │            │            │
              └────────────┼────────────┘
                           ↓
                    Evidence Encoder
                           ↓
                    Current Evidence
                           │
                           ↓
                  Affective Retriever
                           │
                     Top-K Memory
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
     Clip Node         Situation Node     Emotion Node
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ↓
                    Graph Reasoning
                           ↓
                  Memory Reliability
                           ↓
                    ┌──────┴──────┐
                    ↓             ↓
                  Use          Abstain
                    │             │
                    └──────┬──────┘
                           ↓
                    Graph / Memory Tokens
                           ↓
                       AffectGPT
                           ↓
                 Natural-language Emotion
```

---

# 28. 推荐的 Memory schema

最终 Memory object 至少应包含：

```python
MemoryRecord(
    sample_id,
    source_dataset,
    split,
    visual_key,
    audio_key,
    text_key,
    value,
    caption,
    situation,
    emotion,
    evidence,
    encoder_versions,
    graph_version,
    artifact_hash,
)
```

应区分key/value的用途、编码及版本；共享源特征不是理论错误。当前已有value_projection与MHA独立K/V投影，不能写成完全没有K/V变换。不同语义key/value是待验证设计。

以及：

```text
raw provenance ≠ learned representation
```

---

# 29. Provenance / Reproducibility 建议

当前项目已经有比较好的：

- seed；
- checkpoint；
- artifact；
- hash；
- exposure audit；
- intervention；
- sensitivity；
- bias validation。

建议进一步形成：

```text
Experiment
 ├── dataset manifest
 ├── split manifest
 ├── model checkpoint hash
 ├── feature encoder hash
 ├── retrieval encoder version
 ├── memory artifact hash
 ├── graph artifact hash
 ├── adapter checkpoint
 ├── random seed
 ├── config
 └── evaluation manifest
```

这样未来可以严格回答：

> “这个结果到底来自哪个 Memory 版本？”

---

# 30. 最终论文故事建议

不要写成：

> “我们给 AffectGPT 增加 HGT 和 RAG。”

更好的逻辑是：

## Research Gap

当前 MLLM：

```text
parametric emotion knowledge
```

很强，但缺少：

```text
instance-level affective episodic memory
```

## Problem

普通 multimodal retrieval：

```text
perceptual similarity
```

不能可靠表示：

```text
affective similarity
```

尤其在：

```text
similar appearance
+
different situation
```

时容易误导。

## Method

提出：

> **Situation-aware Affective Episodic Memory**

包含：

1. Evidence construction；
2. affective retrieval；
3. Situation-aware memory relation；
4. structured graph reasoning；
5. memory reliability / abstention；
6. compact token injection into AffectGPT。

## Key Hypotheses

```text
Affective relevance
>
Perceptual similarity
```

以及：

```text
Selective Memory use
>
Always-on Memory
```

---

# 31. 最终实验矩阵

| Experiment    | Retrieval | Memory Content | Situation | Graph | Gate |
| ------------- | --------- | -------------- | --------- | ----- | ---- |
| Baseline      | -         | -              | -         | -     | -    |
| M0            | AV        | AV             | -         | -     | -    |
| Semantic      | learned   | AV+caption     | -         | -     | -    |
| Situation     | learned   | AV+situation   | ✓         | -     | -    |
| Graph         | learned   | full           | ✓         | HGT   | -    |
| Gate          | learned   | full           | ✓         | HGT   | ✓    |
| Conflict      | learned   | full           | ✓         | HGT   | ✓    |
| Random        | random    | full           | ✓         | HGT   | ✓    |
| Label shuffle | learned   | full           | ✓         | HGT   | ✓    |
| Graph shuffle | learned   | full           | shuffled  | HGT   | ✓    |

---

# 32. 最重要的 ablation

如果实验资源有限，优先：

1. `Off vs M0`；
2. `M0 vs AV+Caption`；
3. `AV+Caption vs AV+Situation`；
4. `Flat vs Situation reranking`；
5. `Set Attention vs HGT`；
6. `Always-on vs Gate`；
7. `Correct vs Conflicting Memory`。

这七组比简单堆更多 backbone 更有科研价值。

---

# 33. 建议新增的机制指标

不能只看最终 F1。

## 33.1 Retrieval Recall

```text
Recall@K
```

衡量真正有 affective relevance 的 Memory 是否进入 top-k。

## 33.2 Memory Attention Entropy

```text
H(A)
```

如果始终接近：

```text
log K
```

说明 attention 近似均匀。

## 33.3 Memory Identity Sensitivity

固定：

```text
Current input
```

只改变：

```text
Memory identity
```

测：

```text
Δ output
```

若Δ≈0，仅说明所测替换/分布/输出粒度上不敏感；不能证明所有输入下从未用Memory。联合报告生成文本、标签、token变化及任务收益，变化更多不自动表示利用更好。

## 33.4 Gate区分度与校准

对：

```text
correct
random
conflict
```

分别报告：

```text
mean gate
median gate
AUROC
AUPRC
```

## 33.5 Conflict Robustness

例如：

```text
Performance(correct memory)
-
Performance(conflicting memory)
```

以及：

```text
Gate(correct)
-
Gate(conflicting)
```

---

# 34. 推荐的完整研究路线

```text
                 AffectGPT baseline
                        ↓
                    M0 raw AV
                        ↓
                 negative result
                        ↓
             ┌──────────┴──────────┐
             ↓                     ↓
       Adapter diagnosis     Retrieval diagnosis
             ↓                     ↓
     key/value separation      learned evidence
             ↓                     ↓
             └──────────┬──────────┘
                        ↓
                 semantic memory
                        ↓
                Situation rerank
                        ↓
                  Graph reasoning
                        ↓
                 Memory reliability
                        ↓
                    Abstention
                        ↓
                  full 31K AMG
```

---

# 35. 当前阶段的优先级

## P0：必须解决

1. 同checkpoint Null-prefix及attention尺度单因素实验；
2. key/value独立语义编码为候选消融，非未经验证的硬要求；
3. attention scale / bias audit；
4. BGE-M3 CLS pooling已核实，保留版本追溯；
5. Memory provenance；
6. 已知overlap披露，以及Situation来源/可观察性/unknown与盲审协议。

## P1：核心科研问题

1. AV + Caption Memory；
2. AV + Situation Memory；
3. learned affective retrieval；
4. hard negative；
5. Situation conflict。

## P2：方法增强

1. Situation reranking；
2. Set Attention；
3. HGT；
4. Graph token compression。

## P3：最终创新点

1. Memory Gate；
2. Memory Abstention；
3. harmful-memory benchmark；
4. cross-dataset generalization；
5. 可选parametric/episodic disjoint分支，不替代主协议。

---

# 36. 当前不建议做的事情

## 36.1 直接扩展 31K

原因：

```text
mechanism not validated
```

扩大数据不能解决：

```text
Memory identity lost
```

## 36.2 直接增加 HGT 层数

如果当前 Memory value 本身没有有效信息：

```text
2-layer HGT
3-layer HGT
4-layer HGT
```

都可能只是：

> 更复杂地传播无效信息。

## 36.3 同时修改多个核心组件

例如：

```text
new retrieval
+
new encoder
+
new adapter
+
new HGT
+
new gate
```

即使性能提高，也无法知道真正原因。

## 36.4 只看最终 F1

必须同时记录：

```text
retrieval recall
attention entropy
memory weight
gate probability
memory identity sensitivity
prediction flip rate
conflict sensitivity
```

---

# 37. 当前研究结论的严格表述

### English

> M0 experiments do not provide evidence that raw audiovisual nearest-neighbor memory improves AffectGPT. More specifically, same-checkpoint intervention indicates that the current system has low sensitivity to the tested memory replacements, with replay supporting weak selective attention and dominant common components in the Adapter, making retrieval and random-memory conditions nearly indistinguishable at the final prediction level. This negative result motivates a transition from perceptual episodic retrieval toward semantically structured, situation-aware affective memory rather than abandonment of the memory hypothesis itself.

### 中文

> **M0 实验尚未证明原始视听近邻 Memory 能够提升 AffectGPT。更具体地说，同 checkpoint 干预实验表明，当前系统对所测Memory身份替换敏感性很低；逐层重放支持Adapter选择性弱、共同分量主导的解释，但尚未唯一定位所有性能原因，使 retrieval 与 random-memory 条件在最终预测层面几乎不可区分。因此，该负结果更适合作为从“感知近邻 Memory”转向“语义结构化、情境感知的情绪情景 Memory”的依据，而不应被解释为对 Memory 假设本身的否定。**

---

# 38. 如果只能做三个实验

## 实验一：同checkpoint Null-prefix（先不同时改Key/Value）

目标：

> 检验分支有无、共同prefix与邻居身份的影响，不预设唯一原因。

## 实验二：AV vs AV+Situation Memory

目标：

> 检验语义value在AV、容量及普通caption基线之外的增量。

## 实验三：Correct / Random / Conflict + Gate

目标：

> 检验净收益与有害Memory拒绝能力，同时排除always-off解。

如果第三个实验成功，它很可能成为 AMG 最核心的实验。

---

# 39. 最终判断表

| 模块                           | 当前评价                        |
| ---------------------------- | --------------------------- |
| AffectGPT 深度分析               | **扎实**                      |
| 数据 / 评测审计                    | **很有价值**                    |
| M0 工程实现                      | **完成度较高**                   |
| provenance / hash / exposure | **应继续保持**                   |
| raw AV retrieval             | **适合作为 baseline，不适合作为最终方法** |
| MemoryAdapter                | **存在明确的信息选择性不足**            |
| bias 修复                      | **是真问题，但不是全部问题**            |
| BGE-M3                       | **CLS pooling已核实；完整数值一致性未测**     |
| Situation Memory             | **非常值得继续**                  |
| HGT                          | **需要实验验证，不应预设为核心**          |
| Memory Gate                  | **潜在核心创新**                  |
| Abstention                   | **潜在核心创新**                  |
| 31K full AMG                 | **暂时不要启动**                  |
| 当前是否证明 AMG 有效                | **没有**                      |
| 当前是否证明 AMG 思路失败              | **也没有**                     |

---

# 40. 最终研究定位

如果后续实验能够证明：

```text
Raw AV retrieval
        ↓
weak / no gain

Semantic Memory
        ↓
better

Situation-aware Memory
        ↓
better

Graph reasoning
        ↓
better on situation-conflict cases

Memory Gate
        ↓
uses useful memory
rejects harmful memory
```

那么最终 AMG 的贡献可以自然形成：

> **AffectGPT 提供强大的参数化多模态情绪理解能力，而 AMG 为其增加一种可审计、情境感知、选择性使用的情绪情景记忆机制，使模型能够从历史 affective experiences 中检索与当前情绪情境真正相关的经验，同时在 retrieved memory 不可靠或冲突时主动拒绝其影响。**
>
>

这比：

> “AffectGPT + RAG + HGT”

具有更清晰的科学问题，也更容易与 RAER、AffectAgent、HyperEmo-RAG 等工作形成差异。

---

# 41. 一句话结论

> **现在最重要的不是证明“AMG 能不能提升 AffectGPT”，而是先证明“什么样的 Memory 才是真正的 affective memory，以及模型是否能够选择性地使用它”。**
>
> M0 的负结果恰好提供了这个研究入口：**先分辨注入、表示与相关性瓶颈，再分别检验语义value、Situation关系及可靠性选择；这些机制的必要性和收益尚未得到证明。**

---

# 42. 参考资料

## AffectGPT

Lian et al., 2025.

- PMLR: <https://proceedings.mlr.press/v267/lian25a.html>
- arXiv: <https://arxiv.org/abs/2501.16566>
- Official repository: <https://github.com/zeroQiaoba/AffectGPT>

## RAER

Wen et al., Findings of ACL 2025.

- ACL Anthology: <https://aclanthology.org/2025.findings-acl.590/>
- PDF: <https://aclanthology.org/2025.findings-acl.590.pdf>

## AffectAgent

Wang et al., 2026.

- arXiv: <https://arxiv.org/abs/2604.12735>
- Official repository: <https://github.com/Wz1h1NG/AffectAgent>

## HyperEmo-RAG

Wang et al., 2026.

- arXiv: <https://arxiv.org/abs/2605.18884>

## BGE-M3

BAAI.

- Model card: <https://huggingface.co/BAAI/bge-m3>

---

# 43. 项目内部关键文件

- 深度分析：`AffectGPT_深度分析报告.md`
- AMG 方案：`Affective_Memory_Graph_AffectGPT_方案.md`
- AMG 实验目录：`AffectGPT/amg`
- M0 summary：`AffectGPT/amg/experiments/single-seed42-face-ckpt35-v1/SUMMARY.md`
- Adapter audit：`AffectGPT/amg/experiments/single-seed42-face-ckpt35-adapter-audit-v1/FINDINGS.md`
- 同 checkpoint intervention：`AffectGPT/amg/experiments/single-seed42-face-ckpt35-intervention-v1/INTERPRETATION.md`
- Bias validation：`AffectGPT/amg/experiments/single-seed42-face-ckpt35-bias-validation-v1/recovery-v2/SUMMARY.md`

---

## 最终建议

**不要急于追求更大的模型、更复杂的 HGT 或 31K 全量训练。**

当前最有科研价值的路径是：

```text
M0 negative result
      ↓
证明 Memory identity 是否真的被模型读取
      ↓
semantic / situation Memory
      ↓
learned affective retrieval
      ↓
Situation conflict
      ↓
Graph necessity
      ↓
Memory Gate / Abstention
      ↓
31K full-scale AMG
```

如果这条链被实验逐步验证，AMG 就不再只是一个“给 AffectGPT 加 RAG / Graph”的工程改造，而可以形成一个围绕 **情绪情景记忆、情境化检索与选择性记忆使用** 的完整研究问题。


# 44. 2026-10-16已安排的下一轮受控实验

位置：`AffectGPT/amg/experiments/single-seed42-face-ckpt35-reader-validation-v1`；2026-10-16 19:55已完成，state.json为complete。完整结果见第45节。

用户授权双卡并行、每卡两个实验，最多4个GPU进程；每进程allocator上限0.35（80GB卡约28GB）。先4个null推理，再4个匹配训练；每个slot依序运行，结束后CPU配对分析。

|阶段|GPU0 slot0|GPU0 slot1|GPU1 slot0|GPU1 slot1|
|---|---|---|---|---|
|A：推理诊断|旧retrieval ckpt+零prefix|旧ckpt+bank-mean value|zero-init ckpt+零prefix|zero-init ckpt+bank-mean value|
|B：同预算训练|原尺度+retrieval|原尺度+random|logit×50000+retrieval|logit×50000+random|

B各组从相同共享Adapter初始化开始、末层bias仅zero-init后仍可训练，LoRA同起点；seed42、4K fit、1334 accumulation iterations、grad_accum3、最大4002样本曝光、其余lr/dropout等保持原预算。四组都重新训练以隔离运行实现和随机记忆训练模式；最终仅取checkpoint1334，不按dev挑step。scale50000是单一预声明机制候选（既有logit差约2e-5，放大至量级1），不做尺度搜索，不承诺低熵就是收益。

每组B结束后自动生成同checkpoint retrieval/off/random三种500条source dev输出，保留失败分母、实际更新/曝光、初始化hash、配对bootstrap和固定真实query缓存的attention熵/token敏感性审计。报告原尺度对照及自身off/random；+0.5pp是预声明实用门槛，区间为single-seed探索性证据。第一轮不启动全31K、Situation/HGT或目标测试；这些选择待本轮机制与净收益结果再判断。

# 45. Reader validation完成结果与下一步决策（2026-10-16 19:55）

本轮按双卡各两个进程完成。独立复核见`AffectGPT/amg/experiments/single-seed42-face-ckpt35-reader-validation-v1/COMPLETION_VALIDATION.json`：70个锁定输入/代码哈希未变，22份评分报告从逐样本TP/FP/FN重算一致，新增16组×500=8,000条预测全部成功。四组初始化及请求/实际ID、任务、预算曝光一致，每组4002次曝光、覆盖4000个fit ID，无读取失败/替换。实际optimizer updates为native-random 1331，其余1332，存在预期AMP跳步；不得表述成实际更新次数完全相同。

## 45.1 核心结果：增强选择性没有带来净检索收益

表中retrieval/random/off均为各行训练后同一checkpoint的推理条件；不混同独立训练的off模型。所有数值是source normalized open-label micro-F1（%）。

|训练条件|retrieval推理|random推理|off推理|retrieval − off（pp）|
|---|---:|---:|---:|---:|
|原尺度 / retrieval训练|46.3550|46.2292|46.6102|-0.2552|
|原尺度 / random训练|45.0787|45.1148|46.0836|-1.0048|
|logit×50000 / retrieval训练|45.4992|45.8374|46.5664|-1.0672|
|logit×50000 / random训练|46.0488|46.0488|46.7863|-0.7375|

放大尺度的retrieval模型相对原尺度retrieval模型：-0.8558pp，95%区间[-1.7616,-0.0313]pp。该探索性配对区间未跨0且方向为负；它不支持+0.5pp门槛，也不能解释为attention缩放提高任务性能。

机制审计显示归一化attention熵由约1降至0.7016，最大权重均值由0.2000增至0.5469；固定历史正常/随机邻居的token相对L2差由0.1212增至0.1597。选择性和内部身份敏感性确实增加，但正常检索micro-F1从46.3550%降至45.4992%。本轮最明确的发现是：这个具体尺度放大能改变聚合机制，却没有带来任务净收益。

放大尺度的retrieval相对自身off：-1.0672pp，95%区间[-2.2903,+0.0968]pp；相对自身random：-0.3382pp，95%区间[-1.0480,+0.1616]pp。两项micro-F1区间均跨0，不能宣称已确定对所有样本造成伤害。retrieval/random最终标签集合仍有487/500相同，原尺度为495/500；更强内部变化未转成有效内容利用。

random训练的放大尺度条件相对原尺度random推理为+0.9340pp，95%区间[+0.0415,+1.8850]pp，应保留该正向结果。但其自身off仍为46.7863%，高于random/retrieval推理的46.0488%；不同训练路径的off本身也变化，不能把跨checkpoint提升解释成检索内容收益，更不能把46.7863%作为目标泛化结论。

## 45.2 Null-prefix：共同表示已解释大量相似输出

|同checkpoint推理条件|旧retrieval checkpoint|zero-init checkpoint|
|---|---:|---:|
|正常retrieval|46.0784|46.3550|
|bank-mean value|45.8920|46.2394|
|零prefix|45.6175|45.8632|
|off（不插Memory token）|46.3749|46.6102|

bank-mean相对正常retrieval：旧checkpoint为-0.1865pp，95%区间[-0.5675,+0.1505]pp；zero-init为-0.1156pp，95%区间[-0.3312,+0.0160]pp。对应489/500、495/500条标签集合及原始文本相同。这支持共同表示占比较大的解释，但区间跨0不等于统计等价；本轮未设等价界限或执行等价检验。

零prefix仍占四个有效attention位置，不能当作off。旧/zero-init零prefix相对off分别约−0.7575/−0.7470pp，micro-F1区间均跨0；这是分布外占位干预的结果，不构成位置干扰是唯一原因的证明。bank-mean还保留query gate，因此不是严格固定、范数匹配的常数prefix。

## 45.3 复现边界与后续优先级

原尺度retrieval组与上轮zero-init组的500条逐样本报告完全一致，为受控复现提供了证据；本轮并非新增四个随机种子。依旧只有seed42，基础checkpoint已监督全部source31327，分组当前为clip ID；1000次bootstrap及多项未校正探索性比较不覆盖训练seed不确定性，也不等于论文九benchmark复现。

下一步优先固定原attention尺度与flat结构，审计邻居的情绪/情境相关性，并设计匹配容量、token数及监督预算的AV-only、AV+ASR、AV+训练caption及置乱语义value对照。检索候选先固定，只改value，query仅使用推理可得AV/ASR；训练caption可作合法fit Memory value，不能冒充query输入。若这些对照获得内容相关净收益，再测试learned retrieval/Situation与reliability gate；Graph仍需单独证明增量。

本轮不继续搜索attention温度，不扩大31K/HGT，不自动追加训练任务。语义Memory仍是待检验假设，当前结果既未证明其有效，也未否定Memory总体方向。全部产物保留在服务器。


# 46. 下一轮语义Memory value受控实验（2026-10-16）

目录：`AffectGPT/amg/experiments/single-seed42-face-ckpt35-semantic-value-v1`。本轮于2026-10-16 21:05完成，state.json为complete，结果见第47节。

不继续缩放attention；固定原尺度、AV key和cosine top-5候选，检验Memory value语义内容。四组同一2816维输入Adapter（1792 AV + 1024 BGE）、相同参数数目、相同共享初始化与LoRA起点、4个Memory token；AV-only的额外1024维填零，非复用上一轮不同维度Adapter直接比较。

|GPU/slot|训练value内容|目的|
|---|---|---|
|0/0|AV-only|匹配容量的基线|
|0/1|AV+历史subtitle|检验推理可得语义|
|1/0|AV+历史caption|检验训练经验语义|
|1/1|AV+置乱历史caption|控制文本容量、尺度及非相关监督|

先在两卡并行缓存fit4000的冻结BGE-M3 normalized CLS，统一max_length256并记录缺失与截断比例。该离线Memory value编码器与ASR-only query组件分开；BGE不常驻四组训练进程。query路径、原AV/字幕及prompt不改，不读query caption/gold。历史caption仅来自fit库；训练self/group过滤保留，置乱采用seed42固定全局置换，对同owner/query-group donor做确定性安全修复，逐microstep记录实际候选及语义来源ID。

四组仍seed42、1334 accumulation iterations、batch1/grad_accum3、4002曝光；实际optimizer更新/跳步单列，不能写成完全一致。每组结束后做同checkpoint retrieval/off/random各500条dev；再并行做caption→置乱caption、caption→AV-only、subtitle→AV-only、caption→subtitle四个推理干预（分布外机制探针）。累计计划8000条预测。最终核验四组请求/实际样本、任务、预算及训练/dev实际邻居ID一致。

预声明决策：caption须优于匹配AV-only、置乱caption及自身off/random，+0.5pp作为实际收益门槛，1000次配对bootstrap为单seed探索性区间。同步检查同权重内容替换与text/AV投影信号，避免把额外训练路径收益当Memory内容收益。即使成功，也只支持本轮source开发，不直接扩展成Situation或Graph结论。

全部source模型曝光与既有99条/532条协议保持前述边界；本轮不评分holdout/目标集，不自动启动31K/HGT。修改前的上一轮代码与本轮锁定代码均已在服务器保存快照，便于复核。

# 47. 语义Memory value实验完成结果（2026-10-16 21:05）

本轮双卡各两个进程，21:05:07完成，GPU已释放。独立复核见本轮目录`COMPLETION_VALIDATION.json`：81个初始/派生锁定文件哈希未变，16份报告逐样本TP/FP/FN重算一致，8,000条新增预测全部成功。四组初始化、参数量、实际样本/任务/预算曝光及训练/dev的实际AV检索邻居一致；均1334 accumulation iterations、4002次曝光、覆盖4000个fit ID、1332次实际optimizer更新，无读取失败或替换。全部训练语义来源已重放，未发现query自身或同组caption绕过过滤。

## 47.1 性能：语义value没有通过收益门槛

以下均是本轮容量匹配2816维value Adapter；off为各组训练后同一checkpoint关闭Memory。主模型在所有条件下仍输入视听与当前样本字幕；AV-only仅描述Memory value。

|训练Memory value|retrieval micro-F1 %|random micro-F1 %|off micro-F1 %|retrieval−off（pp）|
|---|---:|---:|---:|---:|
|AV-only|46.0986|46.1990|46.5359|-0.4374|
|AV+历史字幕|45.9124|45.9327|46.2492|-0.3368|
|AV+历史caption|45.6209|45.6564|46.0685|-0.4476|
|AV+置乱caption|45.9530|45.9081|46.2141|-0.2611|

|配对比较|micro-F1差（pp）|探索性95%区间（pp）|
|---|---:|---|
|字幕−AV-only|-0.1862|[-0.7195, +0.3326]|
|caption−AV-only|-0.4777|[-1.0352, +0.0611]|
|caption−置乱caption（分别训练）|-0.3321|[-0.8336, +0.1474]|
|caption−自身off|-0.4476|[-1.4464, +0.5094]|
|caption−自身random|-0.0355|[-0.3447, +0.2446]|

这些关键micro-F1区间均跨0。没有语义组优于AV-only或自身off的证据，也没有达到预声明+0.5pp门槛；不能把负点估计表述成已经证明语义Memory必然有害。

## 47.2 同checkpoint内容替换与内部机制

caption模型正常为45.6209%，将历史caption部分置零（仍保留AV及4 token）为45.6657%，置乱为45.7721%；正常相对两者分别−0.0448pp、−0.1512pp，区间均跨0。对应493/500和494/500条原始文本/标签集合完全相同。caption正常与random Memory也有495/500条相同。字幕模型移除字幕value后491/500条相同，正常相对移除仅+0.0708pp，区间跨0。这些均为推理内容干预，不是重新训练后的最优性能。

内部语义通路并非全零：caption第一层text信号范数均值约0.1921，AV为0.2504；caption tokens相对同Adapter AV-only的L2变化约0.3190，字幕为0.2362。但attention归一化熵仍约1，最大权重约0.20001，最终生成对上述替换变化很小。当前证据支持“语义影响了表示，但尚未形成任务上可测的稳定内容收益”；不能唯一定位为检索器、Adapter或LLM某一组件的原因。

跨训练组caption−AV-only的-0.4777pp，可在这批预测上算术分为off推理下的训练路径差-0.4674pp，加Memory分支差的变化-0.0102pp。因此不能把跨checkpoint降幅直接归因于推理时caption内容。这只是代数分解，不是唯一因果识别。

## 47.3 字幕来源纠正与研究边界

4K fit中73条为空的是english列，已回查原始subtitle_chieng.csv：这73条chinese列均非空。清单只取english且没有中文回退，不能将其解释为没有语音或没有任何字幕。历史caption4000条有效，仅7条超过256-token缓存预算。本轮保持锁定输入，后续若采用英文优先/中文回退，应在所有比较条件统一重建版本；不能据此未经实验认定73条缺失解释了整体负结果。

本轮仍为seed42、source dev500；基础checkpoint已监督全部source31327，分组目前clip ID，bootstrap为1000次、未校正多项探索性比较。结论限于固定AV候选、冻结BGE CLS压缩value、当前Adapter/LoRA与4K预算的组合，不等于所有语义/情境记忆无效，也不等于AMG已有收益。

## 47.4 下一步决策

两轮机制改造均未通过收益门槛，应降低对当前latent Memory注入方案的预期，停止以扩大预算或增加Graph来追求预设结论。先做低成本、有停止条件的诊断：盲审候选的情绪/情境相关性；候选相关时，用少量可读文本Memory及明确标为诊断的高相关正对照检验模型能否利用外部信息。候选质量差再研究检索表示；高相关正对照仍无收益则暂停当前注入路线。不得用query真值构造正式测试输入或调参。

Situation、HGT和可靠性gate继续后置，先建立有用Memory能带来净收益的证据。本轮结束后没有自动启动追加GPU任务。全部文件仍在服务器。

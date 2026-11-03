# AffectGPT-AMG v2.6：全局统计关联图构建与严格证据驱动的 Appraisal 标注方案

**文档状态：** 方法协议修订版；完成实现前仍需核验当前 Cue
release、manifest、模型接口与实际运行结果。\
**核心架构：** 全局统计关联图 + Cue Student 概率驱动的节点/路径查询。\
**不包含：** 样本级 `MemorySample` 节点、历史样本检索、可训练边权、独立
Appraisal 预测器、GNN。\
**与 v2.2 的关系：** 本文覆盖 v2.2 中与当前已确认决策冲突的部分。v2.2
中关于 Cue 本体、Cue Student 数据协议、Emotion
开放词表归一化的有效规定继续沿用；关系矩阵训练、样本级 Memory
检索和"Appraisal 状态只作为样本属性"的旧设计不再适用于本版。

> **实施状态说明：** 本文规定推荐的算法与数据协议，但不代表 Appraisal
> Teacher 标注、300
> 条人工审计、图构建或九个目标集评测已经实际运行。实际计数、人工一致性、边权、阈值和效果必须由真实数据生成，不能预填或虚构。

------------------------------------------------------------------------

**数据划分修订（2026-10-21）：** 按用户决定取消诊断预留集，将原200条全部并入 pseudo_train；
现行划分为 pseudo_train=27,879、pseudo_validation=3,076、gold_audit=300，总计31,255条。
验证与人工审计成员不变；新划分见 cue_student/artifacts/current_release.json。
已训练 Cue checkpoint 仍对应原27,679条训练划分，本次未重训。
正在运行的 Appraisal 保留冻结标注文档与输入快照，结果按 sample_id 对齐现行划分。

## 1. 最终决策摘要

1.  **Cue 本体固定：** 复用 `cue_ontology_v1.2` 中的 42 个 Core
    Cue，顺序为 `[Text 15][Audio 17][Visual 10]`。AMG
    不自行新增、删除、重命名 Cue。
2.  **Appraisal 本体：** 6 个 `AppraisalDimension` 节点 + 16 个
    `AppraisalState` 节点。`AppraisalDimension → AppraisalState`
    使用固定 `HAS_STATE` 层级边。
3.  **Emotion 本体：** 复用 AffectGPT 的 open-set Emotion
    提取、词形/格式归一化、同义词归一化和五套 Emotion Wheel
    映射；节点清单只由源域训练分区发现并冻结。
4.  **统计关联边只有三类：**
    -   `CueType → AppraisalState`
    -   `CueType → EmotionConcept`
    -   `AppraisalState → EmotionConcept`
5.  **全图有四种关系类型：** 上述三类统计关联边 + 一类固定本体边
    `HAS_STATE`。
6.  **边权由源域统计生成：** 只使用 `pseudo_train` 中对齐的 Cue
    Teacher、有效 Appraisal Teacher 与规范化 Emotion
    标签计算来源组加权平滑 NPMI；边准入结合独立来源组支持数、来源组级
    bootstrap 置信区间、多重检验控制与稳定性分析。
7.  **Appraisal 严格证据门槛：**
    不执行独立焦点人物识别，不输出人物识别字段；每个 Appraisal
    状态只有在当前样本存在直接、清晰、可核验证据时才标为有效。仅凭表情、语气、事件结果、常识或隐含心理推测不得标注；证据不足、状态不明确或冲突无法消解时必须
    `state=null, valid=false`。
8.  **Appraisal 输入方式：** Appraisal Teacher 对同一样本可用的
    Text/Audio/Video 联合输入；Cue Teacher
    仍按既有方案分模态独立标注。Appraisal Teacher 不读取 Cue
    输出、Emotion 标签或目标 description。
9.  **Teacher 与 Student 分工：**
    -   Teacher 的 Cue 标注用于统计建图和 Cue Student 监督/审计。
    -   Appraisal Teacher 的有效状态标注用于统计建图。
    -   规范化 Emotion 标签用于统计建图。
    -   推理时只用冻结的 Cue Student 连续概率查询图；目标样本不运行
        Appraisal Teacher。
10. **不训练边权：** 图权重建好后冻结，不训练 `W_CA/W_CE/W_AE`，不做
    GNN。
11. **不检索历史样本：** 不创建或查询 `MemorySample`，不向 AffectGPT
    输入源域历史描述或历史 Emotion 标签。
12. **零样本边界：**
    图节点、统计边、阈值、路径联合支持门槛、覆盖率门槛、路径融合系数、Top-K
    和 Prompt
    规则只由允许的源域数据确定并冻结；九个目标数据集仅用于最终评测。源域
    `pseudo_validation` 复用 Cue 已有验证划分，不另建 AMG 验证集。

------------------------------------------------------------------------

## 2. 数据协议与 Cue 提取器接口

### 2.1 Cue 的唯一事实来源

Cue 的本体、监督标签映射、三个 Student
的结构、输入预处理、训练配置、checkpoint 选择、分数校准、active/deferred
判定与阈值均以最新《Cue 提取与训练执行方案》为准。AMG
不得在图方案中另行发明 Cue 阈值或重解释 Cue Teacher 状态。

当前可读取的 v2.2 文档内嵌的 Cue 执行快照记录：

-   本体：`cue_ontology_v1.2`。
-   Cue 数量与顺序：Text 15、Audio 17、Visual 10，总计 42。
-   三模态 Teacher 分别执行 Text、Audio、Visual
    独立标注任务，保持模态隔离；快照中使用 `qwen3.8-omni-flash` API。
-   Cue Teacher
    状态：`positive`、`negative`、`uncertain`、`unobservable`。`uncertain`
    与 `unobservable` 不能直接当作 `negative`。
-   严格数据策略：`all_modalities_succeeded_v1`；任一模态 Cue
    标注失败，整条样本从相应训练/验证/审计/诊断角色排除。
-   快照中的数据量：原始 31,327 条，三模态均成功 31,255 条，72
    条失败排除；角色为
    `pseudo_train=27,879`、`pseudo_validation=3,076`、`gold_audit=300`。

**执行前必须重新读取最新 Cue 执行方案和服务器 manifest。** 如果实际
release、样本数、角色划分、checkpoint、阈值或本体版本已有更新，以最新已冻结的
Cue
执行方案和服务器实际产物为准，不以本文快照覆盖它们。当前可读取文件中没有独立的
Cue 执行方案全文，因此本文不会猜测未在快照中给出的模型超参数或数值阈值。

### 2.2 Cue Teacher 标注如何进入统计图

每个样本每个 Cue 的 Teacher 状态按既定协议处理：

  ----------------------------------------------------------------------
  Teacher 状态                    统计图中的处理
  ------------------------------- --------------------------------------
  `positive`                      该 Cue 的已观察正向出现，记为 (x_c=1)

  `negative`                      在该样本可观察范围内明确未出现，记为
                                  (x_c=0)

  `uncertain`                     该 Cue 的状态不确定；从涉及该 Cue
                                  的关联统计 eligible set 中排除

  `unobservable`                  该 Cue 在当前输入中不可观察；从涉及该
                                  Cue 的关联统计 eligible set 中排除
  ----------------------------------------------------------------------

只有在 Cue 方案定义为明确正/负的样本上，才把 Cue
作为二元统计变量。`uncertain/unobservable` 不可折算为负例。

### 2.3 Cue Student 输出与图查询接口

推理时由三个冻结的模态 Student 按原 Cue 方案输出分数，再按固定顺序拼接：

$$
\mathbf{p}^{C} =
[\mathbf{p}^{T}_{15};\mathbf{p}^{A}_{17};\mathbf{p}^{V}_{10}]
\in [0,1]^{42}
$$

其中 T/A/V 分别表示 Text/Audio/Visual。若 Cue Student
输出需要分数兼容处理或校准，必须复用 Cue 执行方案已经冻结的操作。

每条查询必须保留：

-   `cue_id_order`（42 个 ID 的精确顺序）；
-   `cue_ontology_version`；
-   三个 Student 的 checkpoint/version；
-   `modality_available_mask_42`；
-   `active_cue_mask_42`、`deferred_cue_mask_42`；
-   校准版本、阈值版本与原始/处理后的 Cue 分数；
-   数据 release、预处理与代码版本。

不能只保存一个稀疏 Cue 列表而丢弃完整 42 维向量。未显示某个 Cue
不代表它确定不存在。

### 2.4 数据角色、标注范围与用途

以下角色名称与数量来自当前可读取的 Cue 方案快照；正式执行前必须以最新
manifest 为准。**Appraisal Teacher 不训练独立 Appraisal
模型，因此所有合格源域角色均可运行同一冻结
Teacher；这不意味着所有标注都进入建图。**

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
  数据角色                Cue/Appraisal/Emotion 标注范围     允许用途                                                       禁止用途
  ----------------------- ---------------------------------- -------------------------------------------------------------- --------------------------------------------
  `pseudo_train`          对合格样本生成并对齐 Cue           唯一用于正式统计边权计数；从此分区冻结 EmotionConcept 节点表   不得混入目标数据；不得使用目标标签
                          Teacher、Appraisal Teacher 与                                                                     
                          Emotion 标签                                                                                      

  `pseudo_validation`     对合格样本生成                     复用 Cue 已有验证划分，选择 AMG                                不加入正式图的边权计数；不得扩展正式
                          Cue/Appraisal/Emotion 标签         图准入规则与查询参数；评估源域检索质量                         EmotionConcept 本体

  `gold_audit`：300 条    同一批 300 条均由 Appraisal        估计 Teacher--human                                            率 不参与图统计、参数选择或 Emotion 本体扩展
                          Teacher                            一致性、人工标注一致性、有效覆盖率与过度推断                   
                          标注，并全部由人工独立标注；至少   Teacher---人工一致性、人工标注一致性、有效覆盖率与过度推断率   
                          150 条双人独立标注                                                                                

  九个目标数据集          不运行 Appraisal Teacher           最终零样本评测                                                 不参与标注规则、图本体、边权、阈值、Prompt
                          生成建图标签；按最终任务协议评测                                                                  或 Top-K 选择
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

`pseudo_validation` 是 Cue Student 已有验证集的复用，不新建另一套 AMG
验证集。它可能已经用于 Cue checkpoint 选择，因此 AMG
参数搜索应使用预注册的有限网格，避免无限制调参。验证集上的 Appraisal
State Recall@K、Emotion Recall@K 等指标反映的是对
Teacher/description-derived pseudo-label
的检索表现，不应表述为真实心理状态准确率。

`gold_audit` 的 300 条必须与 `pseudo_train`、`pseudo_validation` 按
`source_group_id`、原视频来源组和近重复组严格隔离。若现有 manifest
只保证 sample ID
不重叠而未保证来源组不重叠，需在正式审计前修复角色划分或排除跨组冲突。

所有拆分必须遵循 Cue 方案冻结的
`source_group_id`、原视频来源组和近重复组，不能自行随机重拆。正式评测前核验
MER-Caption+
与九个目标数据集之间是否存在源视频、同源样本或近重复重叠。仅未使用目标标签，不足以单独证明严格的数据集级
zero-shot。

------------------------------------------------------------------------

## 3. 全局图 Schema

### 3.1 节点类型

  --------------------------------------------------------------------------
  节点类型                    数量      说明
  ---------------------- -------------- ------------------------------------
  `CueType`                    42       固定 Cue 本体节点，直接使用原 Cue ID

  `AppraisalDimension`         6        Appraisal 维度节点

  `AppraisalState`             16       各维度的具体状态，均是独立全局节点

  `EmotionConcept`           \(E\)      规范化细粒度 Emotion
                                        概念，来自源域训练分区并冻结
  --------------------------------------------------------------------------

### 3.2 Appraisal 六维十六状态

  --------------------------------------------------------------------------------------------------------------------------------------------
  维度节点                 状态节点             标注语义
  ------------------------ -------------------- ----------------------------------------------------------------------------------------------
  `APP_GOAL_RELEVANCE`     `AGR_RELEVANT` /     事件是否与样本中有明确证据支持的目标、需求或关切有实质关系
                           `AGR_IRRELEVANT`     

  `APP_GOAL_CONGRUENCE`    `AGC_CONGRUENT` /    事件结果是否促进、阻碍或对目标产生明确的混合影响
                           `AGC_INCONGRUENT` /  
                           `AGC_MIXED`          

  `APP_EXPECTEDNESS`       `AEX_EXPECTED` /     事件是否符合有证据支持的先前预期；不把广义新颖性直接等同于预期违背
                           `AEX_UNEXPECTED`     

  `APP_AGENCY`             `AAG_SELF` /         事件/结果的主要因果归属；不等同于道德责任
                           `AAG_OTHER` /        
                           `AAG_CIRCUMSTANCE` / 
                           `AAG_SHARED`         

  `APP_CERTAINTY`          `ACT_CERTAIN` /      样本中明确表达或直接体现的相关主体对结果/情境发展的确定性评价；不是标注者是否确定
                           `ACT_UNCERTAIN`      

  `APP_COPING_POTENTIAL`   `ACP_HIGH` /         样本中有明确证据支持的相关主体应对当前情境的能力或资源；不把它与事件控制感、因果归属混为一谈
                           `ACP_LOW` /          
                           `ACP_MIXED`          
  --------------------------------------------------------------------------------------------------------------------------------------------

共计 (2+3+2+4+2+3=16) 个实质状态。

`unknown` 不是第 17 个状态节点。证据不足时标注
`state=null, valid=false`，不连向任何具体状态节点。`mixed`
表示有证据支持的混合/冲突评价，不是 unknown 的替代标签。

固定层级关系：

$$
\texttt{AppraisalDimension}
\xrightarrow{\texttt{HAS\_STATE}}
\texttt{AppraisalState}
$$

`HAS_STATE` 不由训练样本统计，不设统计边权、不参与 Cue
查询分数；它只表达本体层级。

### 3.3 EmotionConcept 本体

优先复用 AffectGPT 当前 checkout 中已有的实现与资源，并先核对版本、样本
ID 和数据 release：

1.  如果存在与当前严格 release 一一对应且可核验的
    `mercaptionplus-emotion.csv`，优先复用。
2.  否则仅对允许的源域 description 使用原仓库 `reason_to_openset_qwen()`
    生成 open-set Emotion 表达。
3.  按 `format.csv` 进行词形/格式归一化。
4.  按 `synonym.xlsx` 进行同义词归一化，得到 canonical
    `EmotionConcept`。
5.  保留 `wheel1.xlsx`--`wheel5.xlsx`
    的五套并行映射视图；不得强行把它们压成唯一父类体系。
6.  认真处理多候选归一化：不得未经语义核验就因 `sorted(...)[0]`
    取字典序第一个候选。
7.  概念节点清单只从 `pseudo_train` 中发现并冻结；`pseudo_validation`
    的新概念不得反向扩展正式本体，只记录 OOV/未映射情况。
8.  低频概念可保留为节点，但如果没有通过统计边准入条件，则是孤立或
    deferred 节点，不能强行制造边。

每个样本可以有零个、一个或多个 canonical Emotion 标签。没有提取到
Emotion 不自动等于 `neutral`。未在 description
标签列表中出现的概念是"未被标注"，不是心理学意义上的确定负类。

------------------------------------------------------------------------

## 4. Appraisal Teacher 标注、英文 Prompt 与 300 条人工审计

### 4.1 标注协议：严格证据门控

Appraisal Teacher 对所有合格源域样本进行全量标注，覆盖
`pseudo_train`、`pseudo_validation` 和 `gold_audit`。**这只是 Teacher 推理标注，不是训练 Appraisal
模型。**

Appraisal Teacher 使用同一样本中实际可用的原始 Text、Audio、Video
模态进行联合判断。Cue Teacher 继续按照既有 Cue 执行方案，分别对
Text、Audio、Visual 执行三个独立标注任务。两种标注方式不改变样本
ID、来源组和角色划分。

本版取消独立的焦点人物识别任务：不要求 Teacher
先识别或选择焦点人物，不输出人物身份、人物角色或 `focus_person`
字段。Teacher 直接检查当前样本是否包含足以支持某一 Appraisal
状态的证据。若某一状态必须依赖对某个人的隐含心理进行猜测，或者证据无法明确关联到相应的评价内容，该维度必须弃标。

**有效状态的必要条件：**

1.  当前样本的原始可用模态中存在直接、清晰、可核验的证据，明确支持该维度的某个合法状态。
2.  `evidence`
    必须具体说明支持该状态的可观察内容；若是文本证据，尽可能引用简短原句。不得只写"从语气看""看起来像"或"结合情境推测"。
3.  证据必须针对该维度的定义。一个事件结果不能自动证明先前预期、目标关系、因果归属、确定性或应对能力。
4.  如果存在多个互相冲突且无法消解的候选状态，不能选择"最可能"的一个；该维度设为无效。
5.  每个维度独立判断。一个维度无效不必连带其他维度无效；但不能用一个维度的证据替代另一个维度所需的证据。
6.  `MIXED`
    只用于同一评价关系有明确证据支持的真实混合状态，不能用来表示证据不足、多个主体的观点冲突或标注者犹豫。

**以下信息禁止提供给 Appraisal Teacher：**

-   MER-Caption 或 MER-Caption+ 的目标 `description`；
-   从目标 description 抽取或归一化的 Emotion 标签；
-   Cue Teacher 的 Cue 标签；
-   Cue Student 的概率、阈值结果或预测标签；
-   AMG 图、图边权、路径分数或检索结果；
-   其他样本的标注；
-   九个目标数据集的标签或任何目标集调参结果。

Appraisal 标签必须从当前样本允许的原始模态独立产生，不得根据 Emotion 或
Cue 标签反推。证据不足时使用 `state=null, valid=false`；`unknown` 不是第
17
个状态。严格门控意味着有效覆盖率可能降低，这是有意的质量控制，而不是需要通过猜测补齐的缺陷。

### 4.2 完整英文 Appraisal Teacher Prompt

Prompt ID 冻结为 `appraisal_teacher_v2.4`。Appraisal
状态集合不变，故本体 ID 仍可使用 `appraisal_ontology_v2.3`；但
Prompt、标注记录和实验配置必须记录新的 Teacher
版本。任何进一步修改均需递增 Prompt 版本并记录实际模型/API 版本。

正式运行前需核验所选多模态模型/API
确实支持在同一次调用中读取当前样本可用的
Text、Audio、Video；如果接口不支持，不得假称完成联合多模态推理，必须记录实际输入模式与限制。

``` text
# Appraisal Teacher v2.4 — Strict Evidence-Gated Multimodal Appraisal Annotation

## 1. Role and Objective

You are an expert annotator specializing in multimodal cognitive appraisal.

Annotate the sample along six appraisal dimensions using the predefined ontology of 16 valid appraisal states:

1. Goal Relevance
2. Goal Congruence
3. Expectedness
4. Agency
5. Certainty
6. Coping Potential

This is an appraisal annotation task, not an emotion classification task. Do not infer or output emotion categories.

Do NOT perform a separate focal-person identification or selection task. Do NOT identify, name, describe, or output a focal person, person role, or "focus_person" field. Your task is to determine whether the current sample contains clear, direct evidence for a specific appraisal state. Annotate a state only when the evidence clearly and unambiguously supports it.

## 2. Input and Information Restrictions

A sample may contain these raw inputs:

- Text: Original textual content or transcript associated with the sample.
- Audio: The original audio associated with the sample.
- Video: The original video associated with the sample.

The actual available modalities will be specified by the input pipeline. A modality may be missing, unavailable, or unreadable.

Analyze the available modalities from this sample jointly. Use only evidence present in the current sample. Do not use external knowledge or information from other samples.

You MUST NOT use:

- MER-Caption or MER-Caption+ target descriptions.
- Emotion labels extracted from those descriptions.
- Cue Teacher annotations or Cue Student predictions.
- Cue probabilities, AMG graph edges, graph scores, or retrieval results.
- Labels or annotations from other samples.
- Labels from any of the nine target evaluation datasets.
- External information about people or events depicted.

Never infer appraisal states by reasoning backward from an emotion label or generated emotion description.

## 3. Strict Evidence-Gating Rules

### 3.1 A state must be clearly evidenced

For each dimension, assign a valid state ONLY if the current sample contains direct, clear, verifiable evidence that supports that exact state.

Evidence may be an explicit verbal statement or an unambiguous observable event/context that directly establishes the appraisal. The evidence must not depend on speculative assumptions about goals, expectations, causes, certainty, resources, intentions, or internal thoughts.

If a state is merely plausible, likely, suggested by a facial expression, inferred from vocal tone, or guessed from the outcome, it is NOT sufficiently supported. Mark the dimension invalid.

Do not choose the "most likely" state to fill the schema. Prefer a null state over a weak inference.

### 3.2 Evidence must be dimension-specific

A piece of evidence that supports one dimension does not automatically support another.

Examples:

- A smile, frown, crying, loud speech, pitch variation, speech rate, or isolated facial expression does not by itself establish goal relevance, goal congruence, expectedness, agency, certainty, or coping potential.
- An event's success or failure does not by itself establish the person's prior expectations, causal attribution, or coping potential.
- An event being unusual, sudden, or novel does not by itself establish that it violated a prior expectation.
- The annotator's uncertainty is not evidence that the person is uncertain.
- An event that appears beneficial or harmful to an outside observer does not establish its relationship to a goal expressed or directly evidenced in the sample.

### 3.3 Do not infer absent information

Do not interpret missing evidence as evidence for a negative state.

In particular:

- An unidentifiable goal does NOT imply AGR_IRRELEVANT.
- An unknown goal-outcome relationship does NOT imply AGC_INCONGRUENT or AGC_MIXED.
- An event with no stated prior expectation does NOT imply AEX_UNEXPECTED.
- An unclear cause does NOT justify AAG_CIRCUMSTANCE.
- A successful outcome does NOT prove ACT_CERTAIN or ACP_HIGH.
- A failed outcome does NOT prove ACT_UNCERTAIN or ACP_LOW.

### 3.4 Multiple participants and conflicting evidence

Do not perform a separate task to identify or select a focal person. However, do not combine different participants' appraisals into one state.

If the evidence for a dimension cannot be clearly linked to one coherent appraisal expressed or directly evidenced in the sample, mark that dimension invalid. If incompatible states are supported and the conflict cannot be resolved from the sample, use the reason code "conflicting_evidence" rather than arbitrarily choosing a state.

Use a MIXED state only when the same appraisal relation is clearly evidenced as mixed. Do not use MIXED to represent uncertainty, ambiguity, or disagreement between different participants.

### 3.5 Invalid-state protocol

If evidence for a dimension is insufficient, indirect, ambiguous, contradictory, or dependent on speculation, output:

- state: null
- valid: false
- evidence: an empty string
- evidence_modalities: an empty array
- unknown_reason: the most specific applicable reason code

Do not provide a guessed state plus a low-confidence explanation. There is no confidence score that can override this evidence requirement.

If a modality is unavailable, do not pretend to have observed it. Assess the remaining available modalities, but mark a dimension invalid if the evidence gate is not met.

### 3.6 Evidence requirements for valid states

For every valid state:

- Provide a concise, verifiable evidence summary.
- Prefer a short quotation from the original text when it directly expresses the appraisal.
- For audio or video evidence, describe only concrete, observable content relevant to the state.
- List only modalities that actually support the state.
- Do not fabricate quotations, actions, events, or internal thoughts.
- Do not use vague evidence such as "the person seems upset", "the tone suggests it", "the situation implies it", or "probably".

If you cannot write a concrete evidence summary that directly supports the selected state, the state must be invalid.

## 4. Appraisal Ontology: Six Dimensions and Sixteen States

Use ONLY the following state IDs. A state is valid only when it passes the strict evidence gate above.

### 4.1 APP_GOAL_RELEVANCE — Goal Relevance

Determine whether the event or situation is materially relevant to a goal, need, or concern that is clearly expressed or directly evidenced in the sample.

Allowed states:

- AGR_RELEVANT: Direct evidence supports that the event is materially relevant to the evidenced goal, need, or concern.
- AGR_IRRELEVANT: Direct evidence supports both the relevant goal/concern and that the event has no material relevance to it.

Mark invalid if the goal or concern is not identifiable from evidence, or if its relationship to the event must be guessed. Lack of evidence for a goal does NOT support AGR_IRRELEVANT.

### 4.2 APP_GOAL_CONGRUENCE — Goal Congruence

Determine whether the event or outcome facilitates, obstructs, or has both beneficial and adverse consequences for a clearly evidenced goal.

Allowed states:

- AGC_CONGRUENT: Direct evidence supports that the event or outcome facilitates, advances, or benefits the evidenced goal.
- AGC_INCONGRUENT: Direct evidence supports that the event or outcome obstructs, undermines, or harms the evidenced goal.
- AGC_MIXED: Direct evidence supports both beneficial and adverse consequences for the same goal relation.

Mark invalid if the goal or its relationship to the event cannot be established without speculation. AGC_MIXED is not an uncertainty label.

### 4.3 APP_EXPECTEDNESS — Expectedness

Determine whether the event or outcome conforms to or violates a prior expectation that is clearly expressed or directly evidenced in the sample.

Allowed states:

- AEX_EXPECTED: Direct evidence supports that the event or outcome was anticipated.
- AEX_UNEXPECTED: Direct evidence supports that the event or outcome violated or deviated from a prior expectation.

Mark invalid if no prior expectation is evidenced. Novelty, suddenness, surprise-like facial expression, or the mere occurrence of an event is insufficient.

### 4.4 APP_AGENCY — Causal Agency

Determine the primary causal attribution for the relevant event or outcome, but only when the causal relation is clearly evidenced in the sample.

Allowed states:

- AAG_SELF: Direct evidence supports that the relevant appraisal holder's own action was the primary cause.
- AAG_OTHER: Direct evidence supports that another person or agent was the primary cause.
- AAG_CIRCUMSTANCE: Direct evidence supports that environmental conditions, chance, or non-agent circumstances were the primary cause.
- AAG_SHARED: Direct evidence supports that multiple agents or factors jointly contributed and no single primary cause can be defensibly identified.

Mark invalid if the cause is not explicit or directly observable, if an action is not clearly linked to the outcome, or if "self" versus "other" cannot be established from the sample without guessing. Causal agency is not equivalent to blame or moral responsibility.

### 4.5 APP_CERTAINTY — Certainty

Determine whether certainty or uncertainty about the relevant outcome or situation is clearly expressed or directly evidenced in the sample.

Allowed states:

- ACT_CERTAIN: Direct evidence supports that the relevant appraisal holder regards the outcome or development as certain or expresses clear confidence in it.
- ACT_UNCERTAIN: Direct evidence supports that the relevant appraisal holder regards the outcome or development as uncertain, doubtful, or unresolved.

Mark invalid if certainty is not clearly expressed or evidenced. The event's occurrence, confident-sounding voice alone, or the annotator's own uncertainty is insufficient.

### 4.6 APP_COPING_POTENTIAL — Coping Potential

Determine whether the sample contains direct evidence of the relevant appraisal holder's ability, resources, or means to cope with the situation.

Allowed states:

- ACP_HIGH: Direct evidence supports relatively sufficient coping ability or resources.
- ACP_LOW: Direct evidence supports insufficient coping ability or resources.
- ACP_MIXED: Direct evidence supports both meaningful coping capacity and substantial limitations.

Mark invalid if capacity or resources must be inferred from facial expression, vocal tone, eventual success/failure, or unsupported assumptions. Coping potential is not equivalent to the eventual outcome or causal agency.

## 5. Output Format

Return exactly one valid JSON object. Do not include Markdown fences, introductory text, explanations outside the JSON object, or trailing commentary.

The object must contain:
- event_context: a concise description of the relevant observable event/context; use an empty string if it cannot be described without speculation.
- dimensions: exactly six objects, one for each required dimension. Each object must contain dimension_id, state, valid, evidence, evidence_modalities, and unknown_reason.

Do NOT include focus_person, person identity, person role, or any person-identification field.

The six required dimension IDs are:

- APP_GOAL_RELEVANCE
- APP_GOAL_CONGRUENCE
- APP_EXPECTEDNESS
- APP_AGENCY
- APP_CERTAINTY
- APP_COPING_POTENTIAL

For a valid state:
- state must be an allowed state ID for that dimension;
- valid must be true;
- evidence must be a concise, verifiable statement directly supporting the state;
- evidence_modalities must list the modalities that actually support it;
- unknown_reason must be null.

For an invalid state:
- state must be JSON null;
- valid must be false;
- evidence must be an empty string;
- evidence_modalities must be an empty array;
- unknown_reason must contain the most specific applicable reason code.

Recommended reason codes:

- state_not_explicitly_supported
- evidence_indirect_only
- goal_not_identifiable
- event_goal_relation_unclear
- prior_expectation_not_identifiable
- causal_attribution_ambiguous
- appraisal_holder_unclear
- certainty_not_expressed
- coping_evidence_absent
- conflicting_evidence
- insufficient_evidence
- dimension_not_applicable

Do not use focus-person identification reason codes. Additional reason codes may be introduced only if documented and consistently applied.

If one dimension is invalid, assess the other dimensions independently. Do not automatically invalidate all six dimensions because one is invalid.

Use this exact JSON structure and the exact state IDs:

{
  "event_context": "The sample contains an explicit statement about an unexpected outcome.",
  "dimensions": [
    {
      "dimension_id": "APP_GOAL_RELEVANCE",
      "state": null,
      "valid": false,
      "evidence": "",
      "evidence_modalities": [],
      "unknown_reason": "goal_not_identifiable"
    },
    {
      "dimension_id": "APP_GOAL_CONGRUENCE",
      "state": null,
      "valid": false,
      "evidence": "",
      "evidence_modalities": [],
      "unknown_reason": "event_goal_relation_unclear"
    },
    {
      "dimension_id": "APP_EXPECTEDNESS",
      "state": "AEX_UNEXPECTED",
      "valid": true,
      "evidence": "The text explicitly states, 'I did not expect that.'",
      "evidence_modalities": ["text"],
      "unknown_reason": null
    },
    {
      "dimension_id": "APP_AGENCY",
      "state": null,
      "valid": false,
      "evidence": "",
      "evidence_modalities": [],
      "unknown_reason": "causal_attribution_ambiguous"
    },
    {
      "dimension_id": "APP_CERTAINTY",
      "state": null,
      "valid": false,
      "evidence": "",
      "evidence_modalities": [],
      "unknown_reason": "certainty_not_expressed"
    },
    {
      "dimension_id": "APP_COPING_POTENTIAL",
      "state": null,
      "valid": false,
      "evidence": "",
      "evidence_modalities": [],
      "unknown_reason": "coping_evidence_absent"
    }
  ]
}

The JSON above is an illustrative schema, not an annotation for the current sample.

## 6. Final Validation Checklist

Before returning the JSON object, verify that:

1. Only the current sample's permitted raw modalities were used.
2. No emotion descriptions, extracted emotion labels, Cue annotations, graph results, or external information were used.
3. No focal-person identification task was performed and no person-identification field is present.
4. Every valid state is directly and unambiguously supported by concrete evidence specific to that dimension.
5. Indirect cues, assumptions, event outcomes, or common-sense guesses have not been used as substitutes for evidence.
6. Insufficient or conflicting evidence is represented by state: null and valid: false.
7. Every state ID belongs to the correct dimension's allowed state set.
8. Exactly six dimension objects are present, with no duplicate or missing dimensions.
9. The JSON is syntactically valid and can be parsed by a standard JSON parser.

When in doubt, abstain. Annotation reliability takes priority over annotation coverage.
```

### 4.3 Runtime input contract

The annotation pipeline should provide one sample per call, with the
following logical fields:

``` text
Sample ID: <sample_id>
Available modalities: <text/audio/video subset>

Text:
<original text or transcript, if available>

Audio:
<raw audio payload supplied through the multimodal API, if available>

Video:
<raw video payload supplied through the multimodal API, if available>
```

The actual audio/video payload must be transmitted using the selected
API's supported media-input mechanism. A filename or file path alone
does not mean the model has observed the media. Do not include target
descriptions, Emotion labels, Cue labels, graph data, or other samples.

### 4.4 Stored annotation record and technical failures

For each sample, store at least:

-   `sample_id`, `source_group_id`, source video ID and data role;
-   parsed six-dimension annotation (without a focus-person field) and
    original raw model response;
-   `event_context`, per-dimension evidence and evidence modalities;
-   actual Teacher model/API version, prompt version
    `appraisal_teacher_v2.4`, ontology version
    `appraisal_ontology_v2.3`, and annotation protocol/schema version
    `appraisal_annotation_schema_v2.4`;
-   available modality mask and media preprocessing/version identifiers;
-   request status, retry count, JSON parse status and technical error
    details.

Semantic invalidity and technical failure must remain distinct:

-   Missing or unavailable modality: record in the availability mask;
    annotate from remaining evidence when possible.
-   Insufficient semantic evidence: `state=null, valid=false` with a
    reason code.
-   API/model failure, media decoding failure, or invalid JSON: record
    as a technical failure; do not silently convert it into semantic
    `unknown`.

### 4.5 Human audit: 300 independent samples

The formal audit contains **300 samples, all manually annotated**. At
least **150 of the 300 samples must be independently annotated by two
annotators**. If resources permit, double-annotating all 300 is
preferable but not required by the default protocol.

Requirements:

1.  Reuse the frozen `gold_audit` sample IDs from the Cue data protocol
    when they satisfy source-group isolation. Do not create a second
    overlapping audit set.
2.  All 300 samples receive independent human appraisal labels. At least
    150 receive two independent human labels before adjudication.
3.  Human annotators must not see Appraisal Teacher outputs, Cue labels,
    Emotion labels, or graph results. They use the same permitted raw
    modalities and the same ontology, and MUST apply the same strict
    evidence gate: no separate focal-person identification, no state
    assignment based only on indirect facial/vocal cues or event
    outcomes, and abstention whenever the exact appraisal state is not
    directly and unambiguously supported.
4.  Preserve the pre-adjudication labels. Adjudication must not replace
    the independent labels used for agreement statistics.
5.  Report per dimension: human-label coverage, invalid/unknown rates
    and reasons, state distribution, human-human raw agreement, nominal
    Krippendorff's alpha with confidence intervals, Teacher-human
    macro-F1/balanced accuracy on valid labels, per-state
    precision/recall, confusion matrices, and
    unsupported-state/over-inference rate. Treat invalid/unknown
    predictions as abstentions and report their coverage separately.
6.  Because states may be imbalanced, do not rely on overall accuracy
    alone. Report rare-state counts and uncertainty; interpret agreement
    statistics in light of prevalence and sample size.
7.  The 300 audit samples are excluded from graph edge statistics, AMG
    parameter selection, EmotionConcept expansion, and Prompt tuning.
8.  Freeze the Prompt before the formal audit. If the audit reveals a
    material defect that requires a Prompt revision, version the change
    and run a new independent audit before claiming the revised Prompt
    has passed; do not tune repeatedly on the same 300 samples.
9.  The audit may support the decision to defer an unreliable appraisal
    dimension from the primary graph. Do not force invalid labels into
    concrete states merely to increase graph coverage.

Do not report any audit score, agreement result, or claim of passing
quality criteria until it has been measured on the actual audit
annotations.

------------------------------------------------------------------------

## 5. 三类统计关联边的构建

### 5.1 建图样本和标注来源

正式边统计只使用 `pseudo_train` 中满足数据质量条件的样本，并且要求同一
`sample_id` 的 Cue、Appraisal、Emotion 标注正确对齐。

每条统计边的来源：

-   `CueType → AppraisalState`：Cue Teacher 的明确 positive/negative +
    Appraisal Teacher
    通过严格证据门控的有效状态；证据不足/间接推断的状态不进入 eligible
    set。
-   `CueType → EmotionConcept`：Cue Teacher 的明确 positive/negative +
    成功规范化的 Emotion 标签。
-   `AppraisalState → EmotionConcept`：Appraisal Teacher
    通过严格证据门控的有效状态 + 成功规范化的 Emotion 标签。

`pseudo_validation`
只用于边准入规则与检索参数选择，不加入正式边权计数。`gold_audit` 不进入图统计。

严格证据门控可能显著降低各维度的有效标注率，并使部分状态或统计边无法达到准入门槛。这是预期的质量---覆盖率权衡：必须报告每个维度的有效覆盖率、各状态支持数和图稀疏度；不得为了增加边数而把间接推断改成有效标签，也不得在目标集上放宽门槛。没有合格边时保留缺边/回退行为。

### 5.2 每条候选边的 eligible set

为避免把缺失或不可观察值误当作负例，每条候选边只使用其两端都可评估的样本。

**A. `CueType(c) → AppraisalState(a)`**

eligible 样本必须同时满足：

-   Cue (c) 的 Teacher 状态为 `positive` 或 `negative`；
-   状态 (a) 所属的 Appraisal 维度 `valid=true`；
-   样本数据质量与来源分组有效。

在 eligible set 中，Cue 变量 (u=1) 表示 `positive`，(u=0) 表示
`negative`；状态变量 (v=1) 表示该样本的维度状态正好是
(a)，其他有效状态记为 (v=0)。unknown/无效 Appraisal 不进入该边 eligible
set。

**B. `CueType(c) → EmotionConcept(e)`**

eligible 样本必须同时满足：

-   Cue (c) 的 Teacher 状态为 `positive` 或 `negative`；
-   该样本的 Emotion open-set 提取/归一化流程成功。

(u=1/0) 对应 Cue positive/negative；(v=1) 表示 canonical Emotion
标签集合包含 (e)，否则 (v=0)。这里的 (v=0) 仅表示"当前 description
的规范化标签集合未标出概念
(e)"，不是声称样本中不存在该情绪。该关系是**标注共现统计**，不是心理学负例或因果结论。

**C. `AppraisalState(a) → EmotionConcept(e)`**

eligible 样本必须同时满足：

-   \(a\) 所属 Appraisal 维度 `valid=true`；
-   Emotion 标签提取/归一化成功。

(u=1) 表示有效 Appraisal 状态正好是 (a)，其他有效状态为 (u=0)；(v=1)
表示 Emotion 标签集合包含
(e)，否则表示该概念没有出现在该样本的规范化描述标签中。unknown Appraisal
不进入该边 eligible set。

### 5.3 来源组加权，避免重复来源主导

同一 `source_group_id` 或原视频来源组可能包含多个样本。对关系类型 $r$ 的
eligible set，令 $M_{g,r}$ 为来源组 $g$
中合格样本数，对每个合格样本赋权：

$$
\omega_i^{(r)}=\frac{1}{M_{g(i),r}}
$$

这样每个来源组在该关系 eligible set 的总权重为
1，避免长视频或重复来源仅因样本条数多而主导统计。`support_count_groups`
另外记录至少有一条同样本正向共标注的独立来源组数量。若已通过去重确保每个来源组只有一个样本，权重即为
1。

### 5.4 平滑 NPMI 作为关联强度

对某条候选边两端的二元变量 $u,v$，在 eligible set 中建立加权 2×2 表：

-   $n_{11}$：同样本 $u=1,v=1$；
-   $n_{10}$：同样本 $u=1,v=0$；
-   $n_{01}$：同样本 $u=0,v=1$；
-   $n_{00}$：同样本 $u=0,v=0$；
-   $N=n_{11}+n_{10}+n_{01}+n_{00}$。

这些是来源组加权后的计数。对四个格子分别加入 0.5 平滑项：

$$
\tilde p(u,v)=\frac{n_{11}+0.5}{N+2}
$$

$$
\tilde p(u)=\frac{n_{11}+n_{10}+1}{N+2},\qquad
\tilde p(v)=\frac{n_{11}+n_{01}+1}{N+2}
$$

$$
\operatorname{PMI}(u,v)=
\log\frac{\tilde p(u,v)}{\tilde p(u)\tilde p(v)}
$$

$$
\operatorname{NPMI}(u,v)=
\frac{\operatorname{PMI}(u,v)}{-\log\tilde p(u,v)}
$$

NPMI 的范围为 $[-1,1]$。正值表示在当前标注数据中共现高于独立性基线；0
表示接近独立性基线；负值表示低于基线。NPMI
只衡量标注共现关联，不能证明因果，也不能保证是真实心理机制。低频边仍可能有不稳定的高点估计，因此不以
NPMI 单值直接决定保留。

如果 eligible set 太小、变量没有变化或计算退化，则将候选边标记为
`not_estimable`，不填入任意权重。

### 5.5 边准入、多重检验控制与最终权重

对每条候选边：

1.  计算 `support_count_groups`，并记录关系类型、eligible-set
    规模、正向支持组数和边两端的边际分布。
2.  以 `source_group_id` 为单位做 1000 次 cluster
    bootstrap，每次重采样完整来源组并重算 NPMI，得到 95%
    区间与边排名/入选稳定性。
3.  对所有可估计的候选边进行来源组结构感知的置换检验，并在每一种关系类型内部对全部可估计假设的
    p 值进行 Benjamini--Hochberg FDR 校正，默认
    `q < 0.05`。置换必须尊重来源组结构，不能把同一来源组中的多个片段当成完全独立观测。`min_support`
    作为额外准入条件在多重检验校正后应用，不能先按观察到的正向共现支持数筛掉假设、再只对剩余假设声称控制了完整候选族的
    FDR。
4.  在源域 `pseudo_validation` 比较 `min_support ∈ {5,10,20}`
    个独立来源组的候选规则；按预先指定的图检索指标（例如 Appraisal State
    Recall@K、Emotion
    Recall@K、路径质量与边排序稳定性）选择规则。验证集不加入正式边权计数。
5.  正式图只保留同时满足以下条件的边：
    -   `support_count_groups >= min_support`；
    -   NPMI bootstrap 95% 区间下界大于 0；
    -   多重检验校正后 `q < 0.05`；
    -   两端节点及其标注来源通过有效性规则。
6.  对最终入图边报告 bootstrap
    重采样中的入选频率或排名稳定性；该结果作为可靠性诊断，不代替边准入条件。
7.  最终边权定义为正关联的保守估计：

$$
w_{uv}=\max\left(0,\operatorname{LCB}_{95\%}
[\operatorname{NPMI}(u,v)]\right)
$$

只对通过准入条件的边写入正式图，因此正式统计边权满足 $w_{uv}>0$ 且不大于
1。未通过的候选边保留在离线统计审计表中，并记录排除原因；"图中没有边"只表示当前数据证据不足，不代表负关系。

`min_support`、置信区间和所有阈值都是本项目的统计工程规则，不是情绪评价理论给出的固定常数。应在看目标集结果前冻结。

### 5.6 全局图保存格式

每条正式统计边至少保存：

``` json
{
  "source_node_id": "CUE_ID",
  "relation_type": "CUE_TO_APPRAISAL_STATE",
  "target_node_id": "AEX_UNEXPECTED",
  "support_count_groups": 42,
  "npmi_point_estimate": 0.31,
  "npmi_ci95": [0.12, 0.47],
  "edge_weight": 0.12,
  "min_support_rule": 10,
  "source_split_version": "strict_source_train_release",
  "cue_ontology_version": "cue_ontology_v1.2",
  "appraisal_schema_version": "appraisal_ontology_v2.3",
  "appraisal_prompt_version": "appraisal_teacher_v2.4",
  "emotion_ontology_version": "frozen_emotion_ontology_id",
  "edge_rule_version": "npmi_cluster_bootstrap_v1"
}
```

示例数字仅用于说明字段格式，不是实际计算结果。正式边文件必须使用真实统计值。

### 5.7 两跳路径的三元联合支持度

两条统计边分别成立，不保证 `Cue → AppraisalState → Emotion`
的完整三元组合在同一批样本中得到支持。因此，除边级支持数外，对候选两跳路径
$(c,a,e)$ 计算路径级联合支持度：

$$
J(c,a,e)=
\left|
\left\{
g:\exists i\in g,\;
c_i=1,\;
a_i=a,\;
e\in E_i
\right\}
\right|
$$

其中，$i$ 表示 `pseudo_train` 中的样本，$g$ 表示独立
`source_group_id`，$c_i=1$ 表示 Cue $c$ 在该样本中为明确
positive，$a_i=a$ 表示 Appraisal 状态与 $a$ 匹配且 `valid=true`，$E_i$
是该样本规范化后的 EmotionConcept 集合。

一个合格三元样本必须满足：

-   Cue $c$ 在同一源域样本中有明确 `positive` 标签；
-   Appraisal 状态 $a$ 在该样本中 `valid=true` 且状态匹配；
-   canonical Emotion 标签集合中包含 $e$；
-   三种标注均正确对齐，样本和来源组通过质量规则。

每个 `source_group_id` 对同一 $(c,a,e)$
最多计数一次。该指标是路径级同样本共标注支持，不是因果证据，也不表示真实情绪发生概率。

正式路径审计表至少保存
`joint_support_groups`、三条标注来源/版本、两条边权、两条边各自的
`support_count_groups`，以及该路径在来源组 bootstrap
下的稳定性。`joint_support_groups` 的计数只使用
`pseudo_train`；`pseudo_validation`
只用于选择路径门槛与评估门槛的源域效果。

`pseudo_validation` 用于比较预注册的路径联合支持门槛，例如 `{0,1,3,5}`
个独立来源组，及其对路径质量、Emotion Recall@K
和覆盖率的影响。冻结后的主系统不得把低于已选门槛的路径作为强证据；若没有满足门槛的两跳路径，回退到其他可用路径。所有门槛只由源域验证确定。

如果一条路径没有三元联合支持，它仍可保留在离线审计表中用于诊断，但不得在主
Prompt 中作为已获得同样本联合支持的解释链呈现。

## 6. Cue 概率驱动的图查询

### 6.1 生成查询 Cue 权重

目标样本输入冻结的三个 Cue Student，得到 42 维概率。按 Cue 执行方案的
score calibration、active/deferred、模态可用性和阈值规则筛选查询入口。

$$
q_c=p_c\,m_c\,a_c\,\mathbb{1}[p_c\ge\tau_c]
$$

其中：

-   $p_c$：经过 Cue 方案规定处理后的 Cue Student 概率；
-   $m_c\in\{0,1\}$：该 Cue 对应模态是否可用；
-   $a_c\in\{0,1\}$：冻结的 active mask；deferred Cue
    不作为首版主图查询入口；
-   $\tau_c$：Cue 执行方案已冻结的阈值，不在 AMG 中重新发明。

$$
C_q=\{c:q_c>0\},\qquad
Z_q=\sum_{c\in C_q}q_c
$$

通过阈值的 Cue 仍保留连续概率，不全部二值化为 1。若 $C_q=\varnothing$ 或
$Z_q=0$，则当前样本没有足够 Cue 查询证据，跳过图增强并回退到原始
AffectGPT 流程。

### 6.2 Cue → AppraisalState

对每个全局 Appraisal 状态 $a$，计算：

$$
A(a\mid q)=
\frac{\sum_{c\in C_q}q_c\,w_{CA}(c,a)}{Z_q}
$$

其中 $w_{CA}$ 是统计图中 `CueType → AppraisalState`
的冻结权重。$A(a\mid q)$
是**图关联支持度**，不是经过校准的心理状态概率，也不是独立训练的
Appraisal 预测器输出。

对每个维度 $d$，定义维度证据量：

$$
G_d=\sum_{a\in\mathcal{A}_d}A(a\mid q)
$$

若 $G_d>0$，计算维度内相对支持度：

$$
\bar A(a\mid q,d)=\frac{A(a\mid q)}{G_d}
$$

只有当 $G_d\ge\delta_d$ 时，才把该维度的状态候选作为可展示的图证据。每个
$\delta_d$
只在源域验证集选择并冻结。未达门槛时不强制输出某个状态；`unknown`
也不是一条统计边。

同一维度的状态是互斥类别，不把所有 $A(a\mid q)$
直接当作彼此独立的概率。展示时可按 $\bar A$ 排序，每个维度最多展示前 2
个状态候选，并同时显示原始支持度、相对支持度和关联边来源。

### 6.2.1 查询覆盖率与缺失边处理

当前分数的分母 $Z_q$ 包含所有通过 Cue 查询协议的有效 Cue
权重。为避免"分数高但只有极少数 Cue
有有效关联边"的情况，另外计算覆盖率。对状态 $a$ 与 Emotion $e$
分别定义：

$$
\operatorname{Coverage}_{CA}(a\mid q)=
\frac{\sum_{c\in C_q:\,w_{CA}(c,a)\text{ is available}}q_c}{Z_q}
$$

$$
\operatorname{Coverage}_{CE}(e\mid q)=
\frac{\sum_{c\in C_q:\,w_{CE}(c,e)\text{ is available}}q_c}{Z_q}
$$

"可用边"指正式冻结图中存在且通过准入规则的统计边。覆盖率衡量当前查询 Cue
权重中有多少落在可用边上，不是正确率、概率或模型置信度。

-   无可用边：标记为 `no_graph_support`，不把缺边当作负向证据。
-   支持分数较高但覆盖率低于冻结门槛：不把该候选作为主 Prompt
    中的强证据。
-   没有任何合格图路径：跳过对应图增强分支，回退原始 AffectGPT 流程。
-   覆盖率门槛只能在 `pseudo_validation`
    上选择并冻结；不在目标集上调节。

对 Appraisal
维度也记录可用状态边的覆盖率。报告分数时必须同时保留支持分数和覆盖率，避免只报告归一化分数而隐藏证据稀疏问题。

### 6.3 Cue → Emotion 直接路径

对每个全局 EmotionConcept $e$，计算：

$$
D(e\mid q)=
\frac{\sum_{c\in C_q}q_c\,w_{CE}(c,e)}{Z_q}
$$

$D(e\mid q)$ 表示当前 Cue 查询通过直接统计边获得的 Emotion
关联支持度，不是情绪概率。若没有任何合格的直接边，该路径不可用，不将"无边"当作反向证据。

### 6.4 Cue → AppraisalState → Emotion 两跳路径

仅仅因为 `Cue → AppraisalState` 与 `AppraisalState → Emotion`
两条边分别存在，不代表当前查询中的完整三元路径一定得到同样本支持。因此，路径联合支持门槛必须进入两跳路径的实际计分，而不能只用于解释文字。

令 $\kappa$ 为在 `pseudo_validation` 上冻结的 `joint_support_groups`
门槛。若 $\kappa=0$，表示关闭路径联合支持过滤；若
$\kappa>0$，则只允许满足 $J(c,a,e)\ge\kappa$
的路径贡献正向证据。定义路径门控函数：

$$
g_\\kappa(c,a,e)=
\\begin{cases}
1, & \\kappa=0\\;\\text{or}\\;J(c,a,e)\\ge\\kappa,\\\\
0, & \\text{otherwise}.
\\end{cases}
$$

对于 Appraisal 状态 $a$ 和 EmotionConcept $e$，计算当前查询中有多少
Cue→Appraisal 支持质量也获得了满足门槛的三元联合支持：

$$
R(a,e\\mid q)=
\\frac{\\sum_{c\\in C_q}q_c\\,w_{CA}(c,a)\\,g_\\kappa(c,a,e)}
{\\sum_{c\\in C_q}q_c\\,w_{CA}(c,a)}
$$

仅当分母大于 0 时，$R(a,e\\mid q)$
才有定义。该量是查询条件下的路径联合支持比例，不是概率或正确率。若分母为
0，或没有任何通过门槛的路径，则对应路径不可用，而不是负证据。

将 Appraisal→Emotion
边权乘以路径联合支持比例，得到查询条件下的有效路径权重：

$$
\\widetilde w_{AE}(a,e\\mid q)=w_{AE}(a,e)R(a,e\\mid q)
$$

对每个有足够图证据的维度 $d$：

$$
P_d(e\\mid q)=
\\sum_{a\\in\\mathcal{A}_d}\\bar A(a\\mid q,d)\\,
\\widetilde w_{AE}(a,e\\mid q)
$$

定义当前 Emotion 候选有有效两跳路径支持的维度集合：

$$
\\mathcal{D}_q(e)=
\\left\\{
d:G_d\\ge\\delta_d,\\;
\\exists a\\in\\mathcal{A}_d:
w_{AE}(a,e)>0\\;\\land\\;R(a,e\\mid q)>0
\\right\\}
$$

将有路径支持的维度按 $G_d$ 加权：

$$
P(e\\mid q)=
\\frac{\\sum_{d\\in\\mathcal{D}_q(e)}G_dP_d(e\\mid q)}
{\\sum_{d\\in\\mathcal{D}_q(e)}G_d}
$$

若 $\\mathcal{D}_q(e)$ 为空，则候选 $e$ 的 Appraisal
两跳路径不可用。系统不能把不可用路径当作零分负证据；该 Emotion
候选只能依赖可用的直接路径，或不获得图候选支持。

该公式使联合支持门槛实际影响路径分数。门槛关闭时
$R(a,e\\mid q)=1$（在分母有效且对应 Appraisal→Emotion
边存在的条件下），退化为不使用联合支持过滤的路径评分。无论采用哪种门槛，都必须记录
$R(a,e\\mid q)$、有效路径数、`joint_support_groups` 与查询覆盖率。

### 6.5 两类路径融合

当两条路径均有证据时：

$$
S_E(e\mid q)=
\lambda D(e\mid q)+(1-\lambda)P(e\mid q)
$$

$\lambda$ 在源域验证集从预注册网格 `{0, 0.25, 0.5, 0.75, 1}`
选择，并在目标评测前冻结。只有直接路径可用时使用 $D$；只有 Appraisal
路径可用时使用 $P$；两者都不可用时不生成图 Emotion 候选。

这里的 $A,D,P,S_E$
全部是图关联分数，不是校准后的概率。不得将它们写成"发生某情绪的概率"或心理因果结论。

### 6.6 可追溯路径分数

为解释某个候选 Emotion，给单条两跳路径定义计分：

$$
s(c,a,e\\mid q)=
\\frac{q_c}{Z_q}w_{CA}(c,a)w_{AE}(a,e)g_\\kappa(c,a,e)
$$

直接路径：

$$
s(c,e\\mid q)=
\\frac{q_c}{Z_q}w_{CE}(c,e)
$$

按路径分数排序，保留 Top-K
路径用于解释。路径输出必须同时保留两条边的权重、两条边各自的
`support_count_groups`、`joint_support_groups`、门控状态、$R(a,e\\mid q)$
和查询覆盖率。路径解释分数用于排序，不替代主 Emotion 聚合分数。

### 6.7 查询参数选择

仅用 `pseudo_validation` 选择并冻结：

-   Cue 阈值与 active/deferred：遵循 Cue 执行方案，不在 AMG 中重估。
-   `min_support`：候选 `{5,10,20}` 个独立来源组。
-   每维 Appraisal 证据门槛 $\delta_d$：按源域验证集的状态检索质量和
    abstention 覆盖率选择。
-   Emotion Top-K：候选 `{3,5,10}`，综合 Emotion Recall@K 与 Prompt
    长度选择。
-   路径 Top-K：根据验证集路径质量、稳定性和上下文长度确定。
-   两跳路径联合支持门槛：候选 `{0,1,3,5}`
    个独立来源组；按验证集路径质量与覆盖率选择。
-   图查询覆盖率门槛：在预注册的有限候选网格上依据验证集检索质量与
    abstention 覆盖率选择。
-   路径融合 $\lambda$：候选 `{0,0.25,0.5,0.75,1}`。

参数网格是预注册的开发起点，不是已验证最优值。不能查看九个目标集标签后调整。

------------------------------------------------------------------------

## 7. 推理时完整流程

``` text
目标样本的原始 Text / Audio / Video
                  │
                  ▼
      冻结的 Text / Audio / Visual Cue Student
                  │
                  ▼
        拼接为固定顺序的 42 维 Cue 概率
                  │
                  ▼
 Cue 方案冻结的校准、可用性 mask、active/deferred 与阈值
                  │
                  ▼
              查询 Cue 集合
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
 Cue → Emotion         Cue → AppraisalState
        │                    │
        │                    ▼
        │          AppraisalState → Emotion
        │                    │
        └─────────┬──────────┘
                  ▼
       直接路径与两跳路径评分/融合
                  │
                  ▼
       Top Emotion 候选 + Top 路径 + 支持度
                  │
                  ▼
  当前原始模态 + 结构化图证据 → AffectGPT
                  │
                  ▼
       最终情绪理解与自然语言描述
```

逐步执行：

1.  校验输入模态、预处理版本与模型 checkpoint。
2.  运行三个冻结的 Cue Student，得到 42 维 Cue 分数。
3.  严格按 Cue 执行方案应用分数兼容处理、availability
    mask、active/deferred mask 和既定阈值。
4.  若无有效查询 Cue，跳过图候选生成并回退到原始 AffectGPT 流程。
5.  查询 `Cue → AppraisalState`，得到各维度的图关联支持度；不运行
    Appraisal Teacher，也不额外训练 Appraisal 预测器。
6.  查询 `Cue → EmotionConcept` 直接路径。
7.  对达到证据门槛的 Appraisal 状态，查询
    `AppraisalState → EmotionConcept`，形成两跳路径。
8.  按冻结的融合系数和 Top-K 规则得到 Emotion 候选与可追溯路径。
9.  将结构化图证据与当前原始模态共同输入
    AffectGPT。图只作为辅助证据，不能替代或覆盖当前样本本身的音视频文本证据。
10. 保存查询输入、模型/本体版本、节点/边
    ID、权重、支持数、路径分数和最终输出，保证可复现。

### 7.1 提供给 AffectGPT 的上下文格式

建议使用简短、结构化且明确带有不确定性提示的格式：

``` text
[Current sample]
- Use the current sample's available text, audio and video as primary evidence.

[Detected cue evidence]
- Cue ID / modality / calibrated student score
- Include only active and available cues selected by the frozen cue protocol.
- A cue not listed is not proof that it is absent.

[Graph-derived appraisal hypotheses]
- Appraisal dimension
- Candidate state
- Graph support score (not a calibrated probability)
- Supporting Cue → AppraisalState edges, independent source-group support, and query coverage
- Mark insufficient evidence as "no reliable graph support"; do not force a state.

[Graph-derived emotion candidates]
- Canonical EmotionConcept
- Fused graph association score (not an emotion probability)
- Supporting direct Cue → Emotion edges and/or
  Cue → AppraisalState → Emotion paths
- Edge weights, independent source-group support, path-level joint support, and query coverage

[Reasoning constraints]
- Graph associations are statistical co-annotation patterns, not causal facts.
- Do not copy a candidate Emotion solely because it ranks highly.
- Prioritize the current sample's original modalities.
- If the graph conflicts with the current sample, explain uncertainty and rely on the current evidence.
- Do not infer person identity, exact temporal evidence or unobserved mental states.
```

实际 Prompt 可根据 AffectGPT
原有接口转为中文或英文，但上述语义约束必须保留。首版不附加历史样本
description，不附加源域历史 Emotion 标签，也不做 few-shot 案例提示。

------------------------------------------------------------------------

## 8. 图存储与实现文件

推荐将图与审计数据分开保存：

``` text
amg_release/
├── ontology/
│   ├── cue_ontology_v1.2.json
│   ├── appraisal_ontology_v2.3.json
│   ├── emotion_concepts_frozen.json
│   ├── emotion_aliases_frozen.json
│   └── emotion_wheel_mappings/
├── graph/
│   ├── nodes_cue.csv
│   ├── nodes_appraisal_dimension.csv
│   ├── nodes_appraisal_state.csv
│   ├── nodes_emotion.csv
│   ├── edges_has_state.csv
│   ├── edges_cue_appraisal.csv
│   ├── edges_cue_emotion.csv
│   ├── edges_appraisal_emotion.csv
│   └── candidate_edge_audit.parquet
├── annotations/
│   ├── appraisal_teacher_train.jsonl
│   ├── appraisal_teacher_validation.jsonl
│   └── appraisal_human_audit.jsonl
├── query/
│   ├── cue_query_config.json
│   ├── graph_scoring_config.json
│   └── prompt_template.txt
└── manifest/
    ├── data_release_manifest.json
    ├── model_and_prompt_versions.json
    └── graph_build_report.json
```

上述为建议的逻辑目录，不代表这些文件已实际生成。具体扩展名可根据仓库现有工程约定调整。

每个节点至少保存稳定 ID、节点类型、规范名称、版本、active/deferred
状态和来源。每条统计边保存 source/target ID、relation
type、支持组数、NPMI 点估计、置信区间、最终权重、准入规则、eligible set
版本和本体版本。

`candidate_edge_audit`
保存所有被评估但未进入正式图的候选边及其排除原因。它不是推理时的负边集合。

------------------------------------------------------------------------

## 9. 必做实验与验证

### 9.1 Appraisal 审计

逐维度报告人工覆盖率、unknown 原因、状态分布、Human--Human
一致性、Teacher--Human
一致性和证据过度推断率。未完成审计时不能宣称六个维度均已可靠。

### 9.2 图统计与检索

在源域验证集报告：

-   每类关系的候选边数、准入边数、权重分布与支持组分布；
-   Bootstrap 区间与边排名稳定性；
-   Appraisal State Recall@K；
-   Emotion Recall@K；
-   低频 Emotion 与低支持状态的分层结果；
-   通过阈值后无有效路径的比例；
-   图查询耗时、每个 Query 返回的节点/边/路径数量。

Emotion 标签来自描述抽取，未标注概念不能直接当作真实负类；因此 Recall@K
等指标必须清楚定义有效标签 mask 与适用样本范围。

### 9.3 端到端对照

至少比较以下条件，保持 AffectGPT
checkpoint、解码参数、任务输入、输出指标和 Prompt 框架尽可能一致：

1.  **AffectGPT baseline：** 不提供图证据。
2.  **Cue-only：** 提供相同的检测 Cue，但不提供图关联候选，用于区分显式
    Cue 提示与图结构收益。
3.  **Direct graph：** 只使用 `Cue → Emotion`。
4.  **Appraisal path：** 只使用 `Cue → AppraisalState → Emotion`。
5.  **Full AMG：** 两类路径融合。
6.  **Degree-preserving random graph：**
    在尽可能保持节点度数与边权分布的条件下随机化连接，检验原图结构是否优于随机结构。
7.  **Simple frequency prior：** 使用源域 Emotion 频率或简单
    Cue--Emotion 共标注频率作为基线，检验 NPMI 与两跳结构的增量价值。
8.  **Full AMG without Appraisal：** 从完整图中移除 Appraisal
    路径。若该条件实现与 `Direct graph` 完全相同，则合并，不重复运行。
9.  **Edge/path threshold sensitivity：**
    比较预注册的支持门槛、联合支持门槛与覆盖率门槛，报告检索质量与
    abstention 的权衡。

控制额外 Prompt 上下文的长度、候选数量和格式。否则 Full AMG
的收益可能来自更丰富的提示信息，而非统计图结构本身。

首版不加入 Sample Retrieval、MemorySample、可训练边权或
GNN，以便把性能变化归因于统计关联图和 Appraisal 路径。

### 9.4 严格零样本评测

在九个 AffectGPT 目标数据集上运行前冻结：

-   Cue Student checkpoints、Cue 本体、active/deferred 与阈值；
-   Appraisal 本体、Teacher Prompt、人工审计决定；
-   EmotionConcept 节点表、alias 与 Wheel 映射；
-   统计边权、边准入规则、路径评分公式、Top-K 和融合系数；
-   AffectGPT 提示词与上下文格式；
-   所有数据 release、预处理、代码和模型版本。

目标集标签不得参与任何上述步骤。需要独立检查源域与目标集的源视频、样本
ID 和近重复重叠；如果存在重叠，必须按真实情况报告并制定排除/敏感性分析。

------------------------------------------------------------------------

## 10. 关键风险与处置

  -----------------------------------------------------------------------------------
  风险                     处理规则
  ------------------------ ----------------------------------------------------------
  Teacher Cue 与 Student   统计边使用 Teacher 的明确标注；查询使用 Student
  概率存在分布差异         概率。用源域 validation
                           检查边检索质量。若差异显著，后续追加
                           OOF/稳健性实验，但不悄悄改写首版协议。

  Appraisal Teacher        人工审计；无证据则 unknown；不以覆盖率作为唯一目标。
  过度推断                 

  Emotion open-set         未出现概念视为未标注，不解释为真实负类；保留标签有效性
  标签不完整               mask。

  高频来源组主导边权       采用来源组加权计数、独立组 support count 与 cluster
                           bootstrap。

  稀有状态/Emotion 的 NPMI 最小独立组支持数 + bootstrap
  不稳定                   下界；不合格边保留在审计表，不进入主图。

  某个 Query               不强行补边、不把缺边当负证据；回退原始 AffectGPT。
  没有合格图路径           

  把统计边解释为心理因果   统一称为统计共标注关联，不称因果边或真实心理定律。

  源域与目标域数据泄漏     组级隔离、近重复检查、固定目标集只评测一次；图、阈值和
                           Prompt 不用目标标签调优。

  Teacher 间共标注偏差     Cue 与 Appraisal 来自同一样本的不同标注通道；边仅解释为
                           统计共标注关联。报告人工审计、路径联合支持和随机图对照，
                           不把关联解释为独立心理机制或因果关系。

  过度搜索 AMG 参数        复用现有
                           pseudo_validation，使用预注册的有限网格；参数冻结后
                           在九个目标数据集上执行最终评测。
  -----------------------------------------------------------------------------------

------------------------------------------------------------------------

## 11. 参考依据与解释边界

-   **Cue 本体、数据划分和模型配置：** 以最新《Cue
    提取与训练执行方案》及服务器 manifest 为唯一事实来源。v2.2 中嵌入的
    2026-10-20 Cue 状态只是快照，不替代最新运行产物。
-   **Appraisal 理论：** Moors et al. (2013), *Appraisal Theories of
    Emotion: State of the Art and Future Development*；Scherer
    (2001, 2009) 关于评价检查与应对潜力；Smith & Ellsworth (1985)
    关于认知评价维度。它们支持把本体明确操作化，但不证明本文六维是唯一或完整体系。
-   **人工审计：** Krippendorff (2004), *Content Analysis: An
    Introduction to Its
    Methodology*。一致性阈值是方法学参考，需要结合置信区间、类别分布和证据可观察性解释。
-   **统计关联：** Bouma (2009), *Normalized (Pointwise) Mutual
    Information in Collocation Extraction*。NPMI
    是归一化共现关联量度；本方案额外结合来源组支持数与 bootstrap
    稳定性，不将它解释为因果效应。

------------------------------------------------------------------------

## 12. 正式开工顺序

1.  从服务器只读核验最新 Cue release、manifest、source group、Cue
    本体、Student checkpoints、阈值、预处理与人工 Cue 审计结果。
2.  锁定严格源域样本 ID、来源组、原视频/近重复关系与所有版本指纹；核验
    `gold_audit` 的 300 条确实与构图、参数选择和诊断数据按来源组隔离。
3.  冻结 Appraisal 六维十六状态本体与英文 Teacher Prompt。确认实际多模态
    API 可读取当前样本可用的 Text/Audio/Video；保存真实 model/API
    版本。若需在正式审计后大幅修改 Prompt，必须使用新独立审计样本复核。
4.  对所有合格源域角色全量运行 Appraisal
    Teacher：`pseudo_train`、`pseudo_validation` 与300 条 `gold_audit`。这只是推理标注，不训练 Appraisal 模型。Cue
    Teacher 标签沿用既有三模态分开标注结果。
5.  对 `gold_audit` 的 300 条全部进行人工 Appraisal 标注，其中至少 150
    条双人独立标注；保留仲裁前标签，报告逐维度一致性、覆盖率与过度推断率。审计样本不进入建图和参数选择。
6.  核验或生成源域 Emotion open-set 标签，完成 canonical 归一化；只用
    `pseudo_train` 冻结 EmotionConcept 节点表。对 `pseudo_validation`
    中的新概念只记录 OOV/未映射情况。
7.  在 `pseudo_train` 对齐 Cue Teacher、Appraisal Teacher 与 Emotion
    标签；排除技术失败、无来源记录、近重复冲突和无效标注记录。只使用
    `pseudo_train` 计算正式图边权。
8.  计算三类候选关系的 eligible set、来源组加权 2×2
    表、NPMI、cluster-bootstrap 置信区间、关系类型内 FDR
    校正与边稳定性；生成完整候选边审计表。
9.  复用现有 `pseudo_validation` 选择
    `min_support`、每维状态证据门槛、路径联合支持门槛、图查询覆盖率门槛、Top-K
    与融合系数；不得把 validation 计数并入正式边权。
10. 计算候选两跳路径的同样本三元联合支持度；根据冻结门槛标记主路径或仅保留在离线审计表中。生成冻结的全局统计关联图。
11. 实现 Query 接口：42 维 Cue 分数 → Cue 查询 → Appraisal
    状态支持度与覆盖率 → Emotion 直接/两跳路径 → 路径联合支持过滤 →
    结构化 Prompt。
12. 完成图检索与端到端对照：AffectGPT baseline、Cue-only、Direct
    graph、Appraisal path、Full AMG、degree-preserving random graph 和
    simple frequency prior。控制 Prompt 上下文长度与候选数量。
13. 冻结模型、Prompt、图、阈值、数据、指标和代码，不再调参。
14. 核验源域与九个目标数据集的数据来源重叠，按预先冻结的任务指标执行最终零样本评测。目标集标签只用于最终评分，不用于修改任何方法组件。

**最终方法结论：** AMG 首版是一张包含 42 个 CueType、6 个
AppraisalDimension、16 个 AppraisalState 和冻结 EmotionConcept
的全局异构统计关联图。图有三类统计边与一类固定 `HAS_STATE`
层级边。Appraisal Teacher
对所有合格源域角色全量联合多模态标注，但不训练独立 Appraisal
模型；正式边权只使用 `pseudo_train`，现有 `pseudo_validation` 复用为 AMG
参数选择集，300 条 `gold_audit` 全部人工标注且至少 150
条双标。边权由来源组加权共标注统计产生，并结合多重检验、bootstrap
稳定性、路径联合支持与查询覆盖率进行控制。推理时只使用冻结 Cue Student
查询图，通过直接 Cue→Emotion 路径与 Cue→AppraisalState→Emotion
两跳路径生成可追溯的统计关联证据。没有 MemorySample
检索、没有可训练边权、没有独立 Appraisal 预测器。

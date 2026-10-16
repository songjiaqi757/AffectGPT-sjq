# Affective Memory Graph 增强 AffectGPT：技术方案（修订版）

> 修订日期：2026-10-15。
> 修订依据：已完成的方案审查、当前代码接口核对及用户确认；原独立评估报告已按用户要求删除。
> 用户确认的数据决策优先：最终使用全部31,327条MER-Caption+训练并建库；已确认与OV-MERD+重叠的99条继续保留，不作为实施阻塞项。
> 本文区分首阶段M0实现与后续研究规格。当前先实施AV Memory及共享输入接口，另提供后续E1可复用的冻结BGE-M3文本组件；Situation、HGT及完整E1/E2/G3尚未实现验证，不宣称已有性能收益。
> 本轮按用户最新指令继续单seed=42的M0训练与受控对照；不改动既有face/frame训练任务、原始CSV或媒体。所有项目文件仅保存在服务器。

---

## 1. 系统定位与可验证目标

目标系统：

**当前音视频/ASR → 实例相关Evidence → 检索训练经验 → Situation关联 → 图表示 → Graph Tokens → AffectGPT生成。**

三类结构分别是：

1. Current Evidence：由当前输入产生的动态表示，实例变化不等同于已经具备精细时序推理。
2. Affective Memory Graph：由允许的训练分区构建的实例经验库；最终训练阶段覆盖全部31,327条。
3. Situation–Emotion Concept Graph：由训练文本、情绪监督及可选心理学先验形成的关联结构。

核心研究问题：

> 在排除训练query对自身答案的直接检索后，可观察Situation组织的训练经验，能否比flat retrieval更有效地区分表面相似、语义不同的情绪表达，并减少错误Memory造成的负增益？

Memory保存训练经验，不会凭空增加当前视频中不可观察的事实。图边表示关联，不称因果关系；概念层的跨域稳定性是待验证假设，不预先冠以“Universal”的实证结论。

保留原AffectGPT的视觉、音频、Multi融合、字幕和任务指令路径。Memory是可关闭的增强分支；先证明简单检索有效，再验证Evidence学习、Situation和图关系的增量价值。

## 2. 数据协议与实验范围

### 2.1 最终主训练清单固定为31,327条

统一使用 **MER-Caption+，31,327条**，不再将其与115,595条MER-Caption混称。

最终协议：

- 全部31,327条参与项目训练及Memory建库。
- 已确认与OV-MERD+重复的99条不剔除。
- 不生成31,228条替代主训练清单，不以“干净重训”作为开始条件。
- 允许沿用已有全31K AffectGPT checkpoint，所有受控对照使用相同来源和曝光条件。
- 训练query的自检索过滤只控制本次召回，不删除训练样本，也不删除最终Memory中的节点。

主数据：

- /ai/sjq/AffectGPT-sjq/dataset/mer2025-dataset/track2_train_mercaptionplus.csv
- /ai/sjq/AffectGPT-sjq/dataset/mer2025-dataset/track3_train_mercaptionplus.csv
- /ai/sjq/AffectGPT-sjq/dataset/mer2025-dataset/subtitle_chieng.csv

记录两张训练表的ID一致性、字幕关联、缺失媒体、CSV哈希及最终实际曝光清单。不得静默缩小训练规模；读取失败、过长样本替换等现有行为必须记录。

### 2.2 允许的信息与禁止的输入混用

允许使用训练分区的：

- 视频、音频、推理时可得的ASR/英文字幕；
- 原始开放情绪标签及target caption作为监督；
- 由训练target caption/ASR派生的Situation弱标签；
- 有明确来源和数值定义的心理学关联先验，作为可选消融。

明确区分：

- ASR/subtitle：线上query与离线key均可使用的输入；
- target caption/Emotion：训练监督、伪标签来源及合法训练Memory的value；
- 目标benchmark标签：仅按锁定协议最终评分，不用于超参、本体、门控或checkpoint选择。

禁止把包含训练答案的input_ids直接送入Text Evidence Encoder。目标caption不得冒充线上ASR。

### 2.3 开发阶段与最终全量阶段

开发阶段可按重复/同源组，从主清单取约5K做临时开发：

- 约4K fit：训练新增模块、发现本体、建开发Memory；
- 约500 dev：选配置、预算和校准；
- 约500 source holdout：锁定后评估，查看后不继续反复调参。

实际数量随组边界记录，不强行拆组凑整。其余主清单样本保留，开发划分不改变最终31,327条协议。

分组首先使用clip_id及已确认媒体哈希/来源关系；缺乏完整来源时记录已知分组范围，未识别项先按单clip组处理，不擅自把同演员或相似背景认作重复。近重复审计可逐步补充，不以剔除99条或全库审计完毕作为主方案启动条件。分组只服务开发切分、pair采样和训练召回过滤。

默认可复用已有全31K基线。此时dev/holdout只对新增模块与开发Memory保持隔离，**基础AffectGPT已经监督见过这些样本**；结果支持增量模块的受控开发，不能称全模型的严格未见样本验证。若另做从未见该分组的项目SFT分支，应单独标注；该分支不是主方案前置要求。

配置锁定后，所有开发分区回并，最终训练与Memory使用全部31,327条。最终训练预算和取checkpoint规则由开发阶段预定，不能以目标测试分数挑epoch。

### 2.4 OV-MERD+评测与已知重叠披露

OV-MERD+ **仅用于最终评测**，不加入训练、不加入训练Memory、不用于开发调参或checkpoint选择；评测主结果保持 **全部532条**。已接受的99条重叠仍来自MER-Caption+原训练样本，不从目标集额外导入数据。披露：

- 其中99条与当前Caption+视频已确认SHA-256相同，占18.61%；
- 这99条按用户决定保留在最终训练与Memory中；
- 因此532条结果不表述为“所有测试媒体严格未见”。

可附加报告已确认99条与其余433条的分组结果，但不得替代532条主结果、不得用于选择检索策略，也不得将433条宣称为已完成全量近重复审计的“干净测试集”。其他八个目标集的隔离程度按实际证据说明。

实验定位采用“固定训练清单下的跨数据集迁移/检索增强比较”。目标集不参与额外调参，不等同于所有目标媒体从未出现在项目训练中。

## 3. 总体架构与实施顺序

### 3.1 先实现可独立运行的M0

**M0：原AffectGPT → 冻结clip级AV特征精确检索 → 小型Memory Adapter → 固定Memory Tokens → 共享输入组装 → 生成。**

M0不依赖Situation、本体、learned Evidence Queries、HGT、ANN、queue、MMR或复杂辅助loss。它先回答“训练经验是否有新增价值”。

### 3.2 完整研究分支

M0通过开发检验后：

1. S0：构建并审核Situation本体与弱标签。
2. E1：Current Evidence与Dynamic Adapter训练，建立任务梯度闭环。
3. E2：冻结表示链，生成固定Memory snapshot与精确索引。
4. G3：固定检索表示，训练Graph/Readout/Memory Adapter/Gate及预定PEFT。
5. G3B：仅在固定snapshot稳定后，单独研究周期性刷新。

线上完整分支：

输入 → 原encoder与ASR-only Enc_t → Current Evidence + Dynamic Tokens → 同模态检索 → clip重评分/可选MMR → 子图 → HGT → Graph Readout → Memory Gate/显式关闭分支 → AffectGPT。

Dynamic Tokens承载当前Evidence；Graph Tokens承载检索/概念关系。两者分别做消融，避免把当前输入表示改善误归因为Memory。

## 4. Memory节点与数据结构

所有记录携带clip_id、duplicate/source_group_id、split、版本及有效模态标记。

| 节点 | 保存内容 | 图初始特征 |
|---|---|---|
| Current V/A/T Evidence | 当前样本E、slot、modality、valid mask、时间/位置 | 对应E投影 |
| Memory V/A/T Evidence | 冻结E、单位检索key、clip归属、encoder/constructor版本 | 保存的E经类型投影 |
| Clip Memory | 全部Evidence归属、clip摘要、Situation弱标签、Emotion监督、质量标记 | 冻结clip摘要经类型投影 |
| Situation | 名称、定义、正反例、证据规则、本体版本 | E2缓存的定义表示经类型投影 |
| Emotion | 训练来源词项、规范化定义、别名与版本 | E2缓存的定义表示经类型投影 |

所有图初始特征统一到d_g=256；检索key另存d_r=256。图特征投影与检索投影分别命名，不能用Stage 3可变的图特征重新解释冻结索引中的key。

clip摘要由该clip全部有效Evidence作masked pooling后投影；子图中的部分Evidence被截断时，clip摘要仍是其声明版本的全clip摘要，应记录这一差异。

不将latent slot命名为“微笑”“低音量”等人工语义。Emotion监督进入训练Memory是合法信息来源；自检索过滤防止query直接读回自己的答案。

## 5. Evidence Constructor与真实encoder接口

### 5.1 当前AV粒度

当前默认实际输出：

\[
H^v\in\mathbb R^{B\times8\times768},
\qquad H^a\in\mathbb R^{B\times8\times1024}.
\]

视觉是8个CLIP帧级全局向量；音频是8个2秒片段的HuBERT内部时间池化向量，不是patch/原始声学帧序列。

Evidence接encode_*返回的融合前store_hidden_state；另一个返回值是已经投影到LLM空间的模态token。当前store_hidden_state不能默认视为已经带有后续位置编码。

先定义：

\[
\bar H^m=LN(W_mH^m)+P_m(t)+T_m.
\]

其中W_m统一到256维，P_m表示帧/片段真实采样时间或明确的顺序位置，T_m为模态标记。loader需额外返回采样帧时间、音频起止/中心时间和valid mask，不能把两个独立采样序列的同一索引直接当精确同步。

若某版数据只有索引位置，则标注为顺序编码，不能声称提供精确AV时间对齐。

### 5.2 ASR-only文本编码器

原AffectGPT没有独立的文本Evidence encoder；字幕仍由Qwen自己的tokenizer、词嵌入及完整decoder处理。该原生生成路径继续保留，音频编码器暂时继续使用chinese-hubert-large。M0只用冻结AV特征，不调用新增文本组件、不生成Text Evidence。

完整E1分支的首版Enc_t选择 **冻结的BAAI/bge-m3上下文编码器**，服务器权重路径：

`/ai/sjq/AffectGPT-sjq/AffectGPT/models/bge-m3`

独立输入只接受sample原始subtitle字符串，由BGE自己的tokenizer处理；需要数值化字段时另存transcript_ids/transcript_mask。禁止传入已拼target的Qwen input_ids、完整任务prompt、训练caption或Emotion答案。训练/推理使用同一字幕来源规则；两套tokenizer的ID不能共用。

接口和用途分开定义：

- `FrozenBGETextEncoder.forward(subtitles=...)`输出上下文token hidden `[B,L,1024]`、bool attention mask、样本级valid mask及原生L2归一化CLS dense `[B,1024]`。
- Text Evidence使用 `Linear(1024,256) → LayerNorm → learnable Queries cross-attention`，输出首版2个256维Evidence；BGE保留上下文token序列，不把一个句向量复制成多条证据。
- 简单文本检索对照使用完整1024维原生dense向量；不能粗暴截取前256维并称为BGE原生检索。完整Evidence的256维retrieval head属于另行训练的投影。
- `encode_concepts(definitions=...)`使用同一个冻结BGE编码Situation/Emotion的名称及完整定义，输出原生dense；概念空间需经明确的可训练概念投影映射到256维。
- 首版Evidence字幕预算为128个BGE token，记录截断率并做长度消融。原Qwen字幕预算独立，仍遵循共享输入预算。
- 空或纯空白ASR为缺失模态：valid=false，token mask全false，dense和Evidence为零；全空batch/空batch直接跳过encoder和attention，不能让特殊token把空ASR变为有效证据，也不能调用全mask softmax。
- BGE权重始终冻结且eval；父模型调用train()仍保持BGE eval。E1只训练文本投影、Evidence Queries/attention及相关head。
- 权重只从本地路径加载（local_files_only=True、add_pooling_layer=False）；原checkpoint多出的pooler.dense.weight/bias是明确允许的未使用项，其他missing/unexpected/mismatched keys必须报错。

冻结BGE的原生概念dense可按encoder/tokenizer版本预先缓存。E1中的可训练概念投影会更新，不能跨优化步复用旧的投影后原型；E2对最终eval链统一重算并冻结字幕Evidence、检索key与投影后概念。冻结版本记录包括encoder/tokenizer、投影/queries、checkpoint和输入预算；仅BGE冻结不足以保证完整query/key不漂移。

当前新增组件文件为 `amg/text.py`，CPU契约检查为 `amg/tests/test_text.py`，它们尚未接入M0或原生Qwen生成路径。它提供后续E1可复用的表示接口，不代表完整Evidence/Situation训练已经闭环。

原“冻结Qwen词嵌入＋随机初始化2层Transformer contextualizer”保留为可选轻量消融，不能与当前BGE-M3主配置混称。新增文本分支需计入参数/计算，并提供使用相同文本分支、相同Dynamic Adapter而无Memory的对照。

### 5.3 查询聚合

\[
E^m=LN(CrossAttn(Q^m,\bar H^m,\bar H^m)),
\qquad z_{i,k}^m=
\frac{W_r^me_{i,k}^m}{\|W_r^me_{i,k}^m\|_2+\epsilon}.
\]

padding不进入attention或pooling；全缺失模态直接跳过。每模态独立queries，检索不要求不同slot具有固定人工语义。

如果V/A/T全部没有有效输入，不调用全mask的Evidence、Situation或Dynamic attention，不插Dynamic/Memory tokens；记录input_invalid，并按预定读取失败协议处理。训练loader若重采样必须显式记录原ID/替代ID，评测保留失败记录与分母，不静默丢弃或造有效零节点。

## 6. 节点数与collapse诊断

第一版Evidence配置采用Small，Base作为后续增量：

| 配置 | Video | Audio | Text | 总节点 |
|---|---:|---:|---:|---:|
| Small，首版 | 4 | 2 | 2 | 8 |
| Base | 8 | 4 | 4 | 16 |
| Medium | 8 | 6 | 6 | 20 |
| Large | 8 | 8 | 8 | 24 |

当前只有8个视觉输入，不把12/16个Video queries解释为更细视觉证据。表中K为上限；实际valid输入不足时记录有效数量/重复采样，不强制制造独立证据。

默认λ_div=0，先统计：

- 每模态slot输出cosine、attention overlap；
- attention entropy，按有效输入数归一；
- 任务梯度与每slot利用率；
- 不同输入下slot表示是否随内容变化。

删除原AAᵀ≈I的强制目标。逐行softmax下该目标会同时逼近one-hot和互斥；K>N时不可达。

只有确认collapse后，才消融较小权重的归一化attention off-diagonal惩罚、query dropout或输出去相关。不要仅因loss下降认定Evidence更好；关键共享线索允许被多个query共同关注。

## 7. Information Preservation的范围

默认只使用masked全局cosine preservation：

\[
L_{pres}^{cos}=\sum_m
[1-\cos(D_mPool(E^m),stopgrad(Pool(H^m)))].
\]

默认L_pres的求和仅包含V/A，D_v/D_a分别输出回768/1024维；按模态分别归一，再平均有效模态。preservation heads D_m在E1训练，仅服务辅助监督；E2后固定，推理可不部署。BGE-M3原生token/dense是冻结参考，文本投影和Evidence Queries在E1可训练；若另加文本preservation，目标须明确为冻结BGE的原生dense或masked token mean，维度匹配并单列消融，不能把可训练投影的移动输出当固定教师。此目标只约束全局信息，不保证局部表情、短促声学变化或事件顺序。

可选增加：

\[
L_{rec}=\sum_m\|D_mPool(E^m)-stopgrad(Pool(H^m))\|_2^2/d_m.
\]

relation distillation仅比较同批有效样本的归一化相似度矩阵，按有效pair数平均；同源重复不作为独立对照。

默认λ_rec=λ_rel=0，按第33节逐项开启。若要声称局部/时序能力提升，必须另保留时间信息并做片段/顺序干预，不能从全局重构推出。

## 8. E1的任务梯度闭环

原模态路径保留；新分支为：

\[
E\rightarrow DynamicAdapter
\rightarrow Z_D\in\mathbb R^{B\times M_D\times d_{LLM}}
\rightarrow SharedAssembly
\rightarrow LLM
\rightarrow L_{gen}.
\]

M_D初始为4，Dynamic Adapter采用4个learnable queries对有效Current Evidence作cross-attention，再投影到实际LLM隐藏维度（当前Qwen为3584，运行时读取配置）。

E1训练：

- AV输入投影与时间/位置表示、BGE后的文本投影/attention（BGE本体冻结eval）；
- Evidence Queries、retrieval heads；
- Situation Predictor及其概念投影；定义文本的BGE原生表示冻结，投影后原型随E1更新；
- Dynamic Adapter与各模态preservation heads D_m。

E1默认冻结原encoder、原模态投影、LLM和已有LoRA；冻结参数仍需允许L_gen对输入embedding反传，不能用no_grad包住含新tokens的整个LLM前向。可训练PEFT作为后续统一预算分支，不在不同对照间混用。

\[
L_{E1}=L_{gen}
+\lambda_sL_{sit}
+\lambda_rL_{ret}
+\lambda_pL_{pres}.
\]

初始λ_s=0.1、λ_r=0.05、λ_p=0.05；分阶段从L_gen开始加项。数值只是source开发起点，需记录各loss实际量级，不能当作最优结论。

启动正式训练前，单独由L_gen反传检查有效模态的Query梯度非零。仅检查total loss不够，辅助loss可能掩盖生成分支断链。

Dynamic Adapter在G3和推理继续保留。完整模型的Memory-off包含相同Dynamic分支，因此应与Evidence-only对照比较；不能声称它逐logit等同最初AffectGPT。

## 9. Situation弱标签与本体构建

S0只使用当前开发fit分区；最终按锁定流程在全部31,327条上重建最终本体/标签并记录版本，不查看目标结果决定概念。

初始本体控制在约12–32个可观察情境概念，数量在source dev选择；例如Support、Conflict、Achievement、Threat、Separation等均需定义、反例和证据条件，不能只给名称。

teacher输入为训练ASR及可选target caption，输出至少包含：

- concept；
- present / absent / unknown三态；
- 原文evidence span；
- 可得的主体/对象、否定或事件极性；
- self-reported confidence与来源字段。

只有情绪词、没有事件证据时允许unknown。禁止按“sad→Loss”“angry→Conflict”直接补全原因；caption推断出的事件需保留“推断”来源。

规范化过程为候选提取、embedding/聚类、定义、同义合并、人工审核和冻结。聚类/词频/别名不从dev或目标数据发现。最终全量重建是使用既定流程扩展训练信息，不能借此重新用目标结果挑本体。

## 10. 弱标签质量与Situation监督

人工审核200–500条，至少两名标注者独立判断；按常见/稀有、可观察/unknown、情绪冲突等分层。标注者可核对视频、音频和ASR，不能只对同一target caption重复确认。

至少比较：

1. transcript-only；
2. caption-derived；
3. 遮蔽显式情绪词后抽取。

报告Human–Human与LLM–Human的micro/macro F1、precision/recall、Jaccard及unknown覆盖率；一致性指标需明确多标签适配方式。十条示例抽查不能作为全库噪声率。

Situation Predictor输出独立sigmoid：

\[
p_{ij}^s=\sigma(l_{ij}^s).
\]

有明确present/absent依据的标签才进入mask M_ij，unknown或低置信标签不强行当负类：

\[
L_{sit}=
\frac{\sum_{ij}M_{ij}r_{ij}
BCEWithLogits(l_{ij}^s,y_{ij}^s)}
{\sum_{ij}M_{ij}r_{ij}+\epsilon}.
\]

r_ij为按人工开发标注校准后的权重，不把teacher报0.9直接当90%正确率。校准与最终质量审计集分开，ECE/Brier需说明以concept-label还是clip为单位。

## 11. 检索训练：互斥P/N与逐正例目标

### 11.1 关系集合

不同clip先排除同一duplicate/source_group中的近重复pair。设可靠Situation集合的Jaccard为J_s，Emotion兼容度为J_e：

- 跨clip正例：J_s≥t_s^+，且Emotion可靠兼容J_e≥t_e^+；
- 跨clip负例：可靠Situation明显不同J_s≤t_s^-，或Situation高重合但Emotion明确冲突J_e≤t_e^-；
- t_s^-<t_s^+，t_e^-<t_e^+；
- 缺标签、低置信、中间区间、无法判定的多标签关系忽略。

先分配P，再从其余候选分配N；运行时断言P∩N为空。相同Emotion本身不足以成为正例，Emotion不同本身也不自动是负例。

同clip的有效跨模态样本可作为E1的身份对齐正例；这是训练表征的监督，不允许把同clip放入G3的实际自检索结果。真实跨模态情绪冲突不自动当负例。

### 11.2 slot无固定对齐的可计算相似度

对anchor模态m与candidate模态n定义：

\[
s_{i,c}^{m,n}=
\frac1{K_i^m}\sum_k
Top2Mean_{\ell}
[(z_{i,k}^m)^\top z_{c,\ell}^n].
\]

只有一个有效candidate slot时取该项，无有效slot则该模态pair不参与。E1可用同clip跨模态身份正例及可靠跨clip同模态P/N；线上检索只比较同模态。

以candidate clip/modality为单位做逐positive平均：

\[
L_{ret}=
-\frac1{|P(i,m)|}\sum_{p\in P(i,m)}
\log
\frac{\exp(s_{i,p}/\tau)}
{\sum_{c\in P(i,m)\cup N(i,m)}\exp(s_{i,c}/\tau)}.
\]

τ初始0.07；P为空则跳过该anchor。统计有效anchor、正负数量、同clip与跨clip项的比例，避免只有身份对齐却宣称学到了情境检索。

### 11.3 初版不使用queue

先in-batch；必要时使用冻结encoder特征支持更大有效batch，但仍按实际梯度规则记录。batch内B²未必是瓶颈，先测量。

queue、hard-negative mining后置。开启queue时记录key年龄、constructor版本、最大存活步数和漂移；超龄/版本不一致清理。不能因E2将来冻结就认为E1旧key没有漂移。

## 12. 图关系schema与软边权

完整图采用以下有向关系；反向边使用独立relation参数：

| src → dst | 关系 | 反向 | 边权来源 |
|---|---|---|---|
| Current E → Memory E | retrieval，同模态 | 是 | 经source校准的相似度权重 |
| Memory E → Clip | belongs_to | 是 | 1 |
| Memory E → Memory E | similarity，同模态 | 是，单独类型 | mutual-kNN与相似度 |
| Clip → Situation | exhibits_situation | 是 | 校准弱标签置信 |
| Situation → Emotion | associated_with | 是 | 平滑训练统计/可选先验 |
| Current E → Situation | activates | 是 | 冻结Situation预测与slot attention |
| Current E → Current E | 同模态局部/跨模态关联 | 显式双向 | 时间邻近或定义的相似度 |
| 任意节点 → 自身 | self | 不另建 | 1 |

无真实AV时间对齐时，不用相同slot id硬连为同步边。跨模态关系另标为相似/共现，而非精确时间对应。

正边权通过attention logit偏置使用：

\[
a_{uv}^{(r)}=
\frac{(W_Q^{type(v)}h_v)^\top
W_K^rh_u}{\sqrt{d_h}}
+b_r+\log w_{uv}.
\]

w=0直接不建边，正权重裁剪到数值安全范围；不能用epsilon把本应不存在的边全部补出来。边权为关系强度，不自动等于类别概率或因果影响。

Situation–Emotion数据关联按当前训练分区计算。令u_is为可靠present弱标签的校准权重、y_ie为源训练Emotion多热标签、π_e为该分区Emotion频率：

\[
a_{se}=\frac{\sum_i u_{is}y_{ie}+\alpha\pi_e}
{\sum_i u_{is}+\alpha},\qquad \alpha>0.
\]

无可靠Emotion监督的样本不进入该统计，α在source dev锁定。a_se在[0,1]，不同Emotion不要求和为1；它是观察到的源域关联，非普适情绪原因。主版本心理学混合系数为0；将来加入w_psych时须明确来源、尺度与source校准，单独消融，不能直接混合未经定义的数值。

## 13. Emotion信息与检索约束边界

线上主召回路径只使用：

- modality与valid mask；
- input-derived embedding similarity；
- query自身/duplicate group过滤。

Emotion标签不作为预测emotion相等的硬筛选，也不作为线上primary retrieval filter。

Emotion监督可用于：

- E1的正负兼容性；
- 合法训练Memory的value/关联边；
- source分析与对照。

Situation兼容度作为后置软信号，需来自当前输入预测，不能使用query真值。若Emotion值置乱后结果不变，应检查模型是否实际使用该信息；若一律追随Memory标签，应检查错误检索风险。

## 14. 检索流程与训练自检索过滤

### 14.1 M0 clip级精确检索

从冻结eval的原AV隐藏特征masked mean，按模态L2归一。分别计算同模态cosine，再平均双方共同有效模态的分数；视频与音频维度无需强行相同。

默认top-5，α_m为共同有效模态上的等权。保存模态支持数与单模态分数供质量/门控分析。初版不使用Situation或Emotion重排。

### 14.2 完整分支的Evidence召回

每个有效Current Evidence在同模态Memory中取top-k_e，k_e初始5。开发先精确搜索，ANN只有在实测需要时替换。

训练时过滤当前clip的所有模态/slot及同duplicate/source_group候选。可预过滤或overfetch后过滤再补足；候选不足允许少于k或空集，不用自身补齐。

这项过滤不会将99个OV+重叠ID从最终训练或Memory删除。目标测试按完整Memory检索，不为其单独加99条屏蔽规则。

### 14.3 clip级重评分

把Evidence命中聚合为clip候选，读取候选完整slot特征，再按第11节同模态s_{i,c}^{m,m}重评分：

\[
S_{semantic}(i,c)=
\sum_{m\in Valid(i)\cap Valid(c)}
\tilde\alpha_m s_{i,c}^{m,m}.
\]

初版等权，缺失模态重新归一。保留top-10候选，再取top-5进入初始图。记录重评分前候选是否覆盖真正相关clip，区分召回失败和rerank失败。

### 14.4 MMR后置

可选：

\[
S_{MMR}(c)=\lambda S_{rel}(i,c)
-(1-\lambda)\max_{c'\in R}cos(h_c,h_{c'}).
\]

R为空时先取最相关项。λ及Situation软项只在source dev选；初版不强制“同Situation不得超过40–60%”，避免为了多样性塞入无关情境。各score先按source尺度处理再组合。

## 15. 子图大小与截断规则

完整图初始上限：

| 项目 | 初始值 |
|---|---:|
| Current Evidence | Small最多8 |
| Retrieved clip | 5 |
| Memory Evidence | 32 |
| Situation | 8 |
| Emotion | 8 |
| HGT hidden / heads | 256 / 4 |
| HGT layers | 3 |
| Graph Readout Tokens | 8 |

Small最多约61节点；Base的Current Evidence为16时约69节点，不包含batch padding。

按检索分数/关系质量选择Memory Evidence，每个保留clip尽量至少一项；Situation/Emotion按关联激活选取。保留关系的两端节点必须都在图中，截断后重新构建edge index/mask。

没有可用retrieved clip时，主系统走Memory-off，不静默保留Concept-only信息。Concept-only作为独立对照。

仅在初始图有效后，再消融clip数5/10/20、Memory Evidence32/48/64、M_g=4/8/16；不同时做全组合暴力搜索。

## 16. HGT实现契约与传播范围

采用relation-aware HGT，类型投影、反向关系参数、自环、edge weight方式按第4/12节实现。

完整图默认3层，2层为预算消融，4层只在传播/性能诊断需要时测试。三层可覆盖Memory E→Clip→Situation→Emotion三跳，但Current→Memory再接该链是四跳，不能宣称默认覆盖全部路径。

Graph Readout明确读取**全部保留的valid节点**，包含type/memory/valid mask。这样允许直接读取concept节点；输出称关系聚合结果，不能从架构本身推断模型必然沿四级链推理。

必须用以下对照证明结构作用：

- 固定节点/检索内容的无边set attention；
- 同构Transformer；
- typed HGT；
- 类型/度保持的随机置乱边；
- 去Situation、去Emotion或去某类关系。

节点排序置换后结果应在数值误差内一致（若未使用额外顺序标签）。图batch之间不允许串边。

## 17. Current Evidence激活Situation

Situation原型s_j由同一冻结BGE-M3编码概念完整定义，取原生归一化CLS dense后经可训练概念投影得到。E1可缓存同encoder/tokenizer版本的1024维原生dense，每次使用当前概念投影重算256维原型；不得复用旧投影原型。E2按最终eval表示链统一重算并缓存冻结；G3只读同版本snapshot。然后查询有效Current Evidence：

\[
\alpha_{ji}=softmax_i
\left((W_qs_j)^\top W_ke_i/\sqrt{d_g}\right),
\quad
\tilde s_j=\sum_i\alpha_{ji}W_ve_i,
\]

\[
p_j^s=\sigma(f([\tilde s_j;s_j])).
\]

E1按第10节masked BCE训练predictor；E2将predictor及其上游一并冻结。G3默认直接使用冻结预测，不一边冻结一边声称L_sit继续训练它。

Current E→Situation边权由p_j^s与归一化slot attention组合，关系定义随snapshot记录；unknown或低于预定source阈值的概念不强行连边。

G3若另加只服务图消息的edge MLP，需单独列为可训练参数，不能反向更改检索key或Situation监督定义。

## 18. Dynamic/Graph Readout与Memory Gate

### 18.1 Graph Tokens

\[
H_G=HGT(G),\quad
Z_G=LN(MLP(CrossAttn(Q_G,H_G,H_G))),
\]

输出形状[B,M_g,d_LLM]，M_g初始8；有效节点mask必须贯穿readout。

M0用相同接口的小型Memory Adapter读取top-5 clip特征，可采用MLP+4个readout queries，输出4个Memory Tokens。它不声称存在图推理。

### 18.2 gate特征与训练

gate输入可用：

- 各模态top-1、top-k均值、相似度gap；
- softmax(score/τ_c)的检索熵，按logK归一，K=1时定义为0；
- Situation的逐标签Bernoulli熵及有效概念数量；
- 跨模态近邻agreement、模态缺失与支持数；
- 可选source距离诊断。

特征在source开发上固定尺度，缺失值携带missing bit，不能把高熵/模态冲突直接判为无用。

\[
g=\sigma(MLP(c_{ret})),\quad \hat Z_G=gZ_G.
\]

软缩放仅为融合机制，不保证输出影响与g成比例，也不等于严格关闭。可在source dev用Memory-on/off的配对任务loss或指标差值分析/校准有害检索；目标数据不参与校准。

### 18.3 显式Memory-off契约

空检索、训练Memory dropout或预先确定的关闭策略触发时：

**完全不插入Graph/Memory tokens，跳过Graph分支，重新使用同样的原模态/字幕/指令与Dynamic输入组装。**

不保留零Graph token，不只把embedding乘0。Concept-only不混入该分支。

Memory dropout初始p=0.2，作用于整条Memory分支；训练和推理共用同一off路径。gate接近0/1不自动判失败，应结合实际Memory质量判断。

验证同一个训练后模型在eval模式下，Memory-off与直接原输入路径的logits一致。完整Evidence模型的原输入路径包含Z_D；该检查不要求与最初旧checkpoint一致。

## 19. AffectGPT共享输入组装

新增SharedAssembly，训练与推理共用，输出inputs_embeds、attention_mask、position_ids和labels。

保留当前实际原prompt布局与Frame/Face、Audio、Multi占位语义。在原prompt最终任务问题前统一插入Dynamic block和可选Memory/Graph block；实际布局通过同一模板生成，不能训练推理各写一版。

实现约定：

- 新增独立Graph/Dynamic占位符与不冲突的token索引；
- 同一block扩展为相应M_D/M_g个embedding；
- 新增prefix位置的训练labels全部为-100；
- 先完成实际长度展开，再对batch padding、mask和position_ids统一处理；
- 训练先预留target预算，推理预留max_new_tokens；
- 超长时按统一规则截ASR/可截文本，禁止切断模态占位块；
- 空ASR、缺音频、缺视觉、单个Memory、空Memory均有定义；
- 保存抽样的最终有效输入结构和截断率。

默认Prefix方案。残差cross-attention作为后续替代实验，可用h'=h+gF(h,M)定义g=0恒等路径，但不得与prefix结果混称相同模型。

相关现有入口：

- /ai/sjq/AffectGPT-sjq/AffectGPT/my_affectgpt/models/affectgpt.py
- /ai/sjq/AffectGPT-sjq/AffectGPT/my_affectgpt/conversation/conversation_video.py
- /ai/sjq/AffectGPT-sjq/AffectGPT/my_affectgpt/models/tokenizer.py

## 20. 分阶段训练与冻结表

| 阶段 | 使用数据 | 可训练部分 | 固定部分/输出 |
|---|---|---|---|
| M0 | 开发fit；最终全31K | 小Memory Adapter、gate、统一预算PEFT | 原AV key冻结eval；先验证flat retrieval |
| S0 | 开发fit；最终全31K | 非梯度本体/弱标签流程 | 输出版本化定义、标签、审核及校准 |
| E1 | 同上 | 第8节Evidence表示链、retrieval、Situation、Dynamic Adapter | 原AffectGPT路径/LLM默认冻结 |
| E2 | 同上训练分区建库 | 不训练 | 冻结E1完整链，生成snapshot与精确索引 |
| G3 | 同上 | HGT/type projections、Graph Readout/Adapter、gate、预定PEFT | E2表示链、Situation Predictor和Dynamic Adapter冻结 |
| G3B | 单独可选实验 | 明确解冻的表示模块 | 周期性整体刷新，禁止静默使用旧key |

E2冻结完整可变表示链：BGE后的文本投影/attention、AV输入/时间投影、Evidence Queries、retrieval heads、概念投影、Situation Predictor与Dynamic Adapter；BGE本体、原AV encoder及原模态投影也固定eval。调用全模型.train()后需显式保持整条snapshot为eval。同一版本必须覆盖原encoder/tokenizer、所有投影与queries、Situation本体、输入预算、checkpoint及Memory manifest；仅记录BGE版本不能替代完整snapshot版本。

G3可训练的图类型投影不参与ANN/key生成。若实验允许解冻任何检索上游模块，就进入G3B，所有query/key/metadata/version同步处理。

沿用已有权重时固定run/epoch/文件哈希与基座版本。历史checkpoint的video_llama_proj.weight/bias需在形状一致时显式转换到当前affectgpt_proj.weight/bias；本轮新face/frame权重已使用新键，不重复转换。检查所有预期可训练参数的加载覆盖率，打印missing/unexpected keys；冻结基座不在增量checkpoint内是允许的，不能机械要求全部state_dict键存在，也不能让strict=False静默掩盖训练参数漏载。

开发阶段所有策略只查fit Memory。最终按锁定流程在全31,327条重新完成所需阶段；已有全31K baseline可继续作为共同起点，不要求另做排除99条的重训。

训练预算明确记录optimizer更新次数、有效batch、样本曝光及每ID覆盖。当前AffectGPT一个epoch是固定5,000次更新，不能当作全库过一遍；开发到全量的预算换算按预定样本曝光或更新规则执行，并对所有方法一致。最终单一checkpoint由这项规则确定。

## 21. 损失按阶段启用

不再使用一个在全部阶段都恒加的“总loss”。

| 阶段/损失 | 默认 |
|---|---|
| M0：L_gen | 1 |
| E1：L_gen | 1 |
| E1：L_sit | 0.1 |
| E1：L_ret | 0.05 |
| E1：AV全局cosine L_pres | 0.05 |
| diversity / reconstruction / relation distillation | 0，诊断后单项消融 |
| G3：L_gen | 1 |
| G3：L_rank | 0，只有启用可训练reranker才开启 |
| G3：L_graph | 0 |

L_gen使用与baseline相同的标签/描述混合、token-level自回归CE和mask。若改变混合比例、最大长度或描述监督，全部相关对照同步调整。

冻结retriever时不以L_ret声称继续训练它；冻结Situation Predictor时不以L_sit声称继续训练它。输出各active loss及有效样本数量，避免空mask产生NaN或虚假下降。

## 22. 可选Ranking Loss

初版不需要L_rank。

若引入可训练f_θ(i,c)重排序器，它只使用当前输入特征、候选Memory特征和可用相似度统计，不能输入query真值Emotion/Situation：

\[
L_{rank}=\max(0,m-f_\theta(i,c^+)+f_\theta(i,c^-)).
\]

c^+/c^-严格复用第11节互斥P/N定义，训练采样排除自身/同源组。不能重新把所有Situation overlap高的clip扩成positive。

检索候选的离散top-k不假装端到端可导；梯度作用于候选内reranker，固定snapshot不受更新。需单列reranker参数、时间与收益。

## 23. Graph Consistency：主方案关闭，扩展须定义概率

默认λ_graph=0，删除原A_SEᵀp_sit直接当类别概率做KL的写法。Situation为多标签sigmoid，矩阵乘积可能大于1；现有生成CE也没有p_model^emo接口。

将来如确有需要，只作为明确命名的辅助头实验：

1. 在训练来源固定Emotion概念上定义多标签辅助head，p_head,e=σ(l_e)。
2. 仅由prompt端hidden或Current Evidence取特征，不读取gold answer的hidden。
3. 同时用训练Emotion标签监督该head，避免仅自蒸馏错误图先验。
4. 先把a_se定义在[0,1]；可采用假设条件独立的noisy-OR图目标：
   \[
   q_e=1-\prod_s(1-p_s^sa_{se}).
   \]
5. 裁剪到数值安全范围，使用confidence mask，对stopgrad(q_e)作逐类Bernoulli BCE/一致性；不套未经定义的类别KL。
6. 单独报告独立性假设、校准、辅助head指标与对生成的影响。

辅助head不等于自由生成文本的情绪概率。开放文本解码继续保留，不将输出强制限制为有限图本体；本体外情绪需单列分析。

## 24. 检索质量与最终任务评估

Situation检索指标在固定clip候选、同clip去重后计算：

- Concept Coverage@K：top-K并集覆盖query可靠Situation集合的比例；
- Any-hit@K：是否至少命中一个Situation，单独列出，不与coverage混称；
- nDCG@K：预先固定relevance，例如Situation Jaccard；unknown/无相关项query另报覆盖率；
- 人工盲审clip relevance与“是否帮助当前情绪判断”；
- redundancy、有效候选数及各模态支持数。

只由同一teacher弱标签产生的Recall/nDCG属于代理指标，不能单独证明知识正确。随机对照注明库规模、常见Situation频率和K。

任务指标：

- 九基准逐数据集主指标与平均；
- OV-MERD+完整532条主结果；
- 可选已确认99/其余433分组，按第2节边界解释；
- precision/recall、预测标签数、空输出/未映射率；
- source上的配对Memory增益、负增益比例及高置信但有害Memory比例。

所有方法遵循相同选模规则；每个方法只选择一个checkpoint，该方法九个目标集统一使用它。禁止逐目标集取最佳epoch再平均；当前evaluation.py的按测试argmax路径不能用于正式主结果。

最终运行前锁定：生成与抽取模型/权重、prompt、seed、temperature/top_p/beam等解码参数、抽取器版本、情绪归一化/情绪轮版本。相同生成结果在同一资源版本下评分，缓存键包含方法、checkpoint、snapshot和抽取/评分版本，禁止复用不匹配的旧缓存。

情绪资源先在预定规则下审计fear/fearless等反义错连（当前format.csv第490行）。原资源复现版与审计修正版分别命名、分表报告；修正规则不能根据目标分数选择，修正版重新计算全部相关结果。每集同时报告全N、实际映射后分母、未映射率与失败数，不能把空真值过滤后的分母当完整N。HIT、集合F-score与极性F1分别解释，不称统一准确率。

## 25. 延迟与资源评估

必须同时测量新增模块与完整端到端差值：

1. ASR文本分支、Current Evidence与Dynamic Adapter；
2. exact/ANN检索；
3. clip重评分、可选rerank；
4. 子图与CPU/GPU搬运；
5. HGT、Readout、Memory Adapter；
6. 额外tokens导致的LLM prefill/decode变化。

记录warm/cold、batch size、输入/输出长度、精度、CPU/GPU型号、同步计时方法、mean/p50/p95、峰值显存、CPU内存、索引大小。

报告离线伪标注成本、建库/重建时间、缓存大小；这些不混入单次在线延迟，但不能省略。

100–150ms新增overhead仅为工程目标，没有测量前不承诺。Graph Tokens固定数量也不意味着端到端成本恒定。

## 26. 优化顺序

先profile，再按真实瓶颈优化：

1. 批量化特征读取、metadata聚合与子图构建；
2. 减少候选clip、有效图节点或M_g；
3. 对比3层/2层HGT和256维配置；
4. 对精确检索与ANN做召回/延迟对照；
5. 在允许误差内采用压缩索引、CPU/GPU流水和邻居缓存。

不因规模称谓先上HNSW/IVF-PQ。索引压缩需报告相对精确top-k的召回损失及最终情绪指标影响。

所有缓存用snapshot版本寻址；不能只凭clip_id复用旧encoder/旧constructor结果。

## 27. Domain Shift与拒用Memory

定义“无合适Memory”诊断，而非声称熵或相似度天然能检测OOD：

- source标定后的相似度/距离；
- 多模态支持与真实冲突类型；
- unknown Situation比例；
- 相似度与实际配对收益的对应；
- 不同语言/画面质量/场景分组表现。

用source dev确定关闭规则和覆盖率-性能曲线；目标结果只作最终报告。空Memory直接走第18节off路径，不为其编造高置信concept。

训练包含p_drop=0.2的Memory dropout，必要时单列错误Memory注入训练。真实冲突模态不能一律按低质量删除。

Memory-off退化到同权重、同Current Evidence/Dynamic路径，不保证回到最初baseline参数状态。

## 28. 可解释性与干预

可展示：

Current Evidence → retrieved clip → Situation → Emotion。

命名为retrieval/association trace，不称已证实的因果推理链。至少做：

- 等数量top-k与随机Memory删除；
- 保持token数量的Memory内容替换；
- 类似embedding但Situation不同的替换；
- 同Situation、不同Emotion的误导Memory；
- Memory Emotion值置乱；
- 去Situation/Emotion与类型度保持边置乱；
- AV/T模态消融。

删除后下降只证明依赖；输入长度变化、错误依赖和分布变化都可能造成下降。结合正确/错误案例及matched对照解释。

## 29. 失败预案与停止扩展条件

| 现象 | 优先检查 | 后续行动 |
|---|---|---|
| flat Memory不优于随机/无Memory | 数据曝光对照、自检索、key相关性、融合 | 定位后再扩展，不先堆图 |
| Query高度冗余 | 内容梯度、有效输入数、attention | 先少量queries，必要时单项正则 |
| 检索代理指标高但任务不升 | pseudo标签循环、Emotion shortcut、原输入已有信息 | 人工相关性与on/off配对分析 |
| 真HGT与置乱边相同 | 图是否旁路、readout是否只读概念 | 收缩图主张或采用flat模型 |
| gate经常关闭 | 检索是否确实无益 | 不强迫gate打开 |
| 高置信Memory常有负增益 | 校准、源域偏差、模态混淆 | source上修检索/拒用策略 |
| Graph token梯度近零 | assembly/mask/梯度链、模型已足够 | 先排接口问题，再判断是否需要模块 |
| Snapshot更新后性能漂移 | key/query版本和eval状态 | 重建整体索引，隔离旧缓存 |

预研失败不直接证明方向无效，但必须给出可验证原因，再决定扩大数据或模块。

## 30. 5K技术预研与通过条件

按第2节临时分组开发，不改变最终31K协议。先M0，再逐项进入完整分支。

必须回答：

1. 自检索过滤后，真实Memory是否优于随机Memory和相近容量adapter？
2. 新增模块对开发Memory之外query是否有增益，基础模型曝光条件是什么？
3. 图结构是否优于同内容flat/set模型？
4. 错误Memory是否可被识别，off分支是否符合接口契约？

首轮按用户最新决定仅使用单seed=42，记录同seed baseline与增强模型的配对差值，并按当前manifest group重采样报告置信区间。该区间仅反映此seed下的样本不确定性，不代表跨训练seed稳定性；跨seed复验留作后续可选扩展。开发样本量不足时承认不确定性，不把500条留出集当足够的长尾结论。

用dev预定主指标、实际有意义的效果阈值和训练预算；source holdout只按锁定规则查看。通过与否看统计稳定性、实际收益和代价，不要求每个seed或每个数据集必然同向。

“gate不接近0或1”“删除后必然下降”不作为独立通过条件。已有31K基线曝光的开发结果明确称新增模块验证。

## 31. 最终31,327条规模

最终全量，不剔除99条：

| 表示配置 | Evidence/clip | Evidence总数 |
|---|---:|---:|
| Small 4/2/2 | 8 | 250,616 |
| Base 8/4/4 | 16 | 501,232 |
| Medium 8/6/6 | 20 | 626,540 |
| Large 8/8/8 | 24 | 751,848 |

另有31,327个Clip节点及少量concept。缺失模态会减少实际有效Evidence，manifest记录真实数量。

M0只需每clip的AV key/value，不强制建立数十万Evidence节点。“接近百万节点”不是研究目标。

115K MER-Caption扩容另立实验，明确新增样本、噪声、曝光和资源，不混入主协议。

## 32. Memory存储、版本和刷新

256维原始key体积（不含索引副本、metadata、邻接、高维feature）：

| 配置 | fp16十进制MB | fp32十进制MB |
|---|---:|---:|
| 5,000 clip ×16 | 40.96 | 81.92 |
| 31,327 clip ×8 | 128.32 | 256.63 |
| 31,327 clip ×16 | 256.63 | 513.26 |
| 31,327 clip ×24 | 384.95 | 769.89 |

实际按索引实现与副本数计峰值。高维feature可CPU缓存，计入cold读取延迟。训练基座、文本embedding、概念表示和动态图不包含在此表内。

snapshot至少记录：

- 31K/开发分区manifest与重复组版本；
- encoder/constructor/ASR tokenizer及预处理哈希；
- 时间编码、精度、模态valid mask；
- 本体/teacher/prompt/弱标签/情绪规范化版本；
- retrieval head、度量、索引参数；
- 图schema与缓存版本。

G3B每2–5轮刷新只是候选策略。解冻表示链后，query/key存在漂移；应明确刷新间隔内可接受漂移、重建全Memory、原子切换索引并失效旧缓存，单列总成本。默认G3不刷新。

## 33. 分组消融矩阵

不做所有维度的笛卡尔积；每次只改变一个主要变量。

1. **新增信息**：baseline、普通tokens、匹配参数adapter、random Memory、flat retrieval、同权重Memory-off。
2. **Situation监督**：无Situation、相同弱标签的无Memory多任务baseline、Situation增强检索/图。
3. **Evidence学习**：raw clip pooling、Small queries、Base queries；Dynamic-only与Dynamic+Memory分开。
4. **检索目标**：无L_ret、互斥SupCon、可选hard-negative/ranking。
5. **preservation**：无、cosine、+reconstruction、+relation；分别记录量级。
6. **图结构**：相同retrieval内容的set、同构Transformer、HGT、置乱边、去Situation/Emotion。
7. **token/预算**：M_D与M_g、图大小、2/3层，记录参数和时间。
8. **门控/刷新**：无gate、软gate+显式off、source校准关闭；固定snapshot优先。

不同数据量、source曝光、teacher监督或基线checkpoint的结果分表，不混称纯架构消融。

## 34. 必须保留的Baselines

| Baseline | 控制的问题 |
|---|---|
| 原AffectGPT，固定同一31K起点/数据协议 | 基础能力 |
| 相同新增token数量 | 序列容量 |
| 相近可训练参数的无Memory adapter | 参数量 |
| Evidence-only + Dynamic Tokens | 当前输入表示改善 |
| 同Situation弱标签的无Memory多任务模型 | 额外监督 |
| random / label-shuffled Memory | 内容与答案关联 |
| KNN + MLP或普通Memory Attention | flat检索的价值 |
| 固定检索内容的set/Transformer | 关系结构 |
| Concept Graph only | 实例Memory贡献 |
| 同一个训练后模型Memory-off | 实际Memory依赖 |

相同tokens不代表相同参数量；原AffectGPT对照也按相同数据/曝光预算继续训练，不能只与未经相同步数继续训练的旧权重比较。各对照采用一致的冻结encoder/eval策略；额外文本分支、弱标签teacher成本、训练步数和样本曝光都要记录。若不能完全匹配，明确差异并报告受控补充实验。

## 35. 相关工作与创新验证

不将“检索+图编码+固定tokens接LLM”单独作为新颖贡献。

需优先对照的原始工作：

- [G-Retriever](https://arxiv.org/abs/2402.07630)：图检索和soft prompt。
- [RAER](https://aclanthology.org/2025.findings-acl.590/)：复合情绪的检索增强。
- [AffectAgent](https://arxiv.org/abs/2604.12735)：多模态情绪检索、证据处理及MER-UniBench。
- [HyperEmo-RAG](https://arxiv.org/html/2605.18884v1)：情绪层次、证据图、EmotionGraphFormer和固定tokens注入。
- [AffectGPT](https://arxiv.org/abs/2501.16566)：当前基线与数据/评测定义。

方法定位聚焦：

**可观察Situation组织实例经验的独立收益、不同情绪含义的相似表达区分，以及错误Memory条件下的可拒用融合。**

这些是待验证主张。至少证明真实图优于固定内容flat模型、Situation优于额外监督对照、收益在非重复组开发query上可观察，并披露最终99条重叠。不能以模块数量或路径可视化替代证据。

## 36. 方法命名与结论表述

整体暂称：

**Affective Memory Graph Augmented AffectGPT（AMG-AffectGPT）**。

模块：

1. Latent Evidence Constructor；
2. Situation-associated Affective Memory；
3. Memory-aware Graph Token Adapter。

若最终只有flat Memory有效，按实际方法收缩命名和贡献；若只有额外Situation监督有效，不把它写成图推理突破。

实验表述分别说明：

- 模型/模块是否使用同一31K起点；
- 开发query是否只对新增模块未见；
- OV+主测试含99已见媒体；
- 开放词汇生成、本体内辅助头与实际评分映射的区别。

不预先承诺“Universal”“因果”“所有数据集严格zero-shot”或“必然可发表”。

## 37. 两级MVP与实施交付

### 37.1 第一级M0：先验证Memory

- 固定31,327条主manifest与开发分组；
- 共同已有AffectGPT起点、冻结eval的AV clip key；
- 精确cosine top-5；
- 训练query屏蔽自身/同源组；
- 小MLP/attention、4个Memory tokens；
- 共享assembly、显式off、p_drop=0.2；
- 仅L_gen与统一PEFT预算；
- 完成第34节核心容量/随机/flat/Memory-off对照。

### 37.2 第二级完整研究分支

只有M0或对应诊断支持继续后：

- S0可观察Situation本体、证据span与人工质量审计；
- E1 Small 4/2/2 queries、d_g=d_r=256、M_D=4及真实生成CE闭环；
- E2冻结完整表示链与eval snapshot；
- 同模态Evidence检索top-5，clip重评分top-10，取5个clip；
- 九类型图、显式反向边和soft权重；
- 初始3层HGT、M_g=8、scalar gate+显式off；
- 默认L_graph/L_rank/queue/MMR/复杂diversity关闭；
- 固定检索内容的结构消融与错误Memory测试；
- 开发配置锁定后，全部31,327条训练建库，完整532条OV+最终主评测。

首版不加入momentum encoder、复杂互信息估计、token-wise gate、动态query数量、大型LLM reranker或online memory update。

交付物仅在服务器：

- 配置、split/全量manifest与版本；
- 本体/伪标签/人工审核记录；
- snapshot、索引及key/query版本；
- checkpoint、最终输入抽样、生成与抽取缓存；
- 每seed指标、配对差值、分母和资源测量；
- 已知曝光/重叠的实验说明。

## 38. 实施验收与当前实施状态

正式训练前先完成有意义的接口检查：

1. ASR-only字段不包含target；空模态mask有效。
2. L_gen单独反传确实到达Evidence Queries。
3. P/N互斥，重复组过滤与真实top-k不足行为正确。
4. query/key同一snapshot、冻结模块保持eval，加载键无静默漏载。
5. 训练/推理共享assembly；prefix label、padding、截断和位置一致。
6. Memory-off真正不插Graph token，与同权重原路径logits一致。
7. 图不跨batch串边，零权重无边、反向边和readout mask符合schema。
8. 目标评分不按测试挑checkpoint；缓存、词表及有效分母可追溯。

后续实验才回答检索增益、Situation可靠性、图贡献、门控和资源代价。确定的定义问题先修，不把它们都当可自由搜索的超参。

**固定最终决策：保留全部31,327条训练与Memory，保留已确认99条重叠，完整532条OV+仍为主评测；在此协议下进行受控、可追溯的改进。**

当前按M0先行的边界实施，首阶段代码已完成，独立入口为 `amg/build_memory.py`、`amg/train.py`、`amg/infer.py`，使用说明见服务器 `/ai/sjq/AffectGPT-sjq/AffectGPT/amg/README.md`。已实现冻结AV特征精确top-5、query实际身份/同组屏蔽、Memory Adapter与4个tokens、共享输入组装，以及retrieval/random/current/learned/off对照入口；训练记录曝光、失败替换、Memory启用量、AMP溢出/无梯度跳步，并保存版本化增量checkpoint。默认group_id仅为clip ID，尚不声称完成跨clip近重复分组。正式训练的Memory必须来自同一训练manifest；face/frame、采样槽数、编码器实际权重、bank与来源清单哈希均检查。

数据主清单保留全部31,327条及已接受的99段重叠；临时开发清单为4,000/500/500，最终回并全量。另准备了仅供最终评测调用的OV-MERD+ 532条输入清单（不作为训练或建库输入），包含22条空字幕；所有532条Qwen提示词预检和1条真实媒体CPU读取通过，没有读取目标标签或运行目标评测。其余benchmark媒体入口尚未接入。

完整CPU测试套件124项全部通过（Ran 124 tests in 4.832s，OK，TEST_RC=0），日志位于 `amg/artifacts/single_seed42_unit_tests.log`，最新执行状态见第39节。完整fit Memory已提取完成（4,000条、complete=true），内容为冻结CLIP/HuBERT的AV隐藏特征，与基线LoRA独立；沿用同一encoder、预处理和fit清单时可以复用。新共同起点的真实optimizer更新、checkpoint保存重载和生成结果，只按新实验目录的实际记录报告。

`amg/text.py`已提供后续E1可复用的冻结BGE-M3字幕/概念编码和可训练Text Evidence组件；真实BGE CPU中英文＋空字幕小批验证通过，token输出[3,6,1024]、dense输出[3,1024]，只出现明确允许的两个未使用pooler键。此组件没有接入M0。完整Situation/HGT/E1/E2/G3研究分支、全31K特征提取与正式训练、最终目标评测尚未完成；当前4K M0双卡执行见第39节，后续是否进入完整分支按开发检验决定。现有face/frame GPU训练任务、原始CSV与媒体保持不变；独立评估报告此前已删除。本轮产物仅保存在服务器。


## 39. 单 seed M0 开发执行（2026-10-15）

本轮仅使用seed=42，五组共同基线固定为：

`/ai/sjq/AffectGPT-sjq/AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230/checkpoint_000035_loss_0.723.pth`

固定协议位于服务器`/ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-v1/protocol.json`，状态、日志和结果均保存在同一目录。协议锁定共同基线文件SHA-256、fit/dev清单、Memory、配置与评价资源，所有产物仅在服务器。

fit 4,000条用于建库和参数训练，dev 500条用于开发；off/retrieval/learned/current/random均为1,334个梯度累积iteration、batch=1、accum=3，名义曝光4,002次，统一使用最终`checkpoint_001334.pth`，不扫描epoch。holdout与目标集不用于当前配置选择。完整fit Memory已完成，冻结AV内容与共同起点LoRA独立，可在校验版本后复用。

运行入口为`python -m amg.run_experiment --protocol /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-v1/protocol.json --output-dir /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-v1`。本轮已在物理GPU 0先运行off、GPU 1先运行retrieval，空闲卡接续完成learned/current/random；五组前五步的真实更新验收、最终checkpoint保存重载及dev生成均通过。每个槽连续完成本组训练和dev生成，最多两个新增GPU任务并行；dev生成保持双卡调度，配对评分由CPU最多同时两组执行。子进程以`CUDA_VISIBLE_DEVICES`绑定单卡并在进程内使用`cuda:0`。既有face/frame训练任务继续运行。

新增逐microstep曝光审计和逐ID覆盖汇总；共享总长度预算只裁ASR并保护完整target/模态块；source评测入口为amg.evaluate，固定fit词形资源、全样本分母和版本信息。source normalized开放label集合microF1是开发指标，与论文九基准Emotion Wheel指标分别报告。原format.csv不改动，fear/fearless错连另作审计披露。

第35号共同起点的CPU兼容校验与124项完整CPU测试已经通过（日志 `amg/artifacts/single_seed42_unit_tests.log`，TEST_RC=0）。五组1,334步训练、各500条dev生成及7项配对评测于北京时间2026-10-15 22:52:30全部完成，state.json为complete。每组有效optimizer更新1,332次（2次AMP溢出跳过）、实际曝光4,002次、覆盖全部4,000个fit ID，参数有限、完整曝光一致性通过，dev生成零失败。结果已写入SUMMARY.md和summary.json；holdout与目标集仍未评分。单seed结果不支持跨训练seed稳定性的结论。

本轮source dev microF1：off 0.464437，retrieval 0.460784，current 0.459680，learned 0.458374，random 0.457031。retrieval相对off差值为−0.003652（−0.3652个百分点），95%配对bootstrap区间为[−0.016927, 0.008111]，跨0；相对其余三组的区间也均跨0。当前没有支持检索Memory性能收益的证据。该结论仅对应seed42的4K开发实验，不是论文EW或最终目标集成绩。详细结果见`amg/experiments/single-seed42-face-ckpt35-v1/SUMMARY.md`。


同checkpoint推理干预已于北京时间2026-10-16 00:51:16完成：同一份retrieval训练后权重，正常检索46.0784%、关闭Memory46.3749%、随机Memory46.0733% micro-F1；三种设置各500条、零失败，三项配对区间均跨0。正常检索与随机Memory的标签集合491/500一致。报告与112条CPU错例分析位于服务器`/ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-intervention-v1/`，详见`SUMMARY.md`及`INTERPRETATION.md`。这是固定权重的推理干预，与此前五组独立训练对照分开报告；未新增训练、未改标签映射、未运行holdout/目标集，完整图/HGT尚未实现。


已启动真实dev AV/Adapter敏感性诊断，目录为服务器`/ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-sensitivity-v1/`。CPU bank审计已完成：normal/random在498/500条query上top5完全无交集，原始AV向量有较强共同方向；该几何观察不能直接判断Adapter或LLM原因。新增后台任务仅冻结CLIP/HuBERT与已训练Adapter，无Qwen、文本生成或训练；GPU0/1各处理250条，自动聚合真实query、attention、token差异及重放一致性。最新状态见state.json，完成后生成SUMMARY.md和summary.json。按用户要求启动后不全程监测；原源码、权重和评分资源保持锁定，所有产物只在服务器。


Adapter机制CPU审查已完成，报告在服务器`/ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-adapter-audit-v1/FINDINGS.md`。500条真实query显示Value MLP末层公共bias约为Wx信号范数4.46倍，明显降低相对邻居对比度；Q/K跨邻居logit差约2e-5，attention近似均值聚合。FP64与手算已排除显示/softmax维度错误；最终optimizer显示选择性通路任务梯度极弱。公共偏置不消除绝对差值，共同K偏移不直接造成softmax均匀，尚不能反推唯一训练原因。内部去偏置探针不等于任务收益；未改模型、未启动新训练/生成。


## 40. 单偏置有界验证（2026-10-16）

已启动后台流水线，当前进度以服务器 /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-bias-validation-v1/state.json 为准；启动检查为同目录 launch-validation.json。142项CPU测试通过，67项输入/源码/启动器锁通过。原face/frame训练继续运行，所有新产物仅在服务器。

先对原retrieval已训练checkpoint推理：只清零 memory_adapter.value_projection.2.bias，GPU0正常检索、GPU1随机检索各500条，旧正常/随机/关闭预测用当前同一评分器重算后配对。该操作是训练分布之外的机制探针。

随后固定运行一对新的seed42/4K训练，不依据阶段A成绩决定是否跳过。两组共享一份CPU新建Adapter初值，LoRA均严格恢复第35号基线；control保留初值，zero_init只清零value末层偏置，二者偏置都可训练。这不复现旧实验未保存的Adapter初值。其余初值和训练设置一致，每组1334 iteration、batch1、accum3，实际曝光需4002次且覆盖全部4000条；自动比较逐张量初值和完整任务/clip/预算曝光，首五步检查真实更新。

每组训练后分别正常/关闭/随机推理各500条，保留最终学到的偏置。自动运行11项配对评分并汇总最终偏置和标签集合差异。固定探索性实际增益参考为+0.005 microF1，结合配对95%区间和内容对照判断；bootstrap不代表跨训练seed稳定性，多项比较未经族错误校正。完整说明见同目录PROTOCOL.md；完成后生成SUMMARY.md/summary.json，技术失败写FAILURE.txt。不会自动扩展31K、HGT或运行holdout/目标评分。按用户要求，启动验证后结束本轮，不持续监测。


偏置验证续跑记录（2026-10-16）：两组seed42训练均完成，各1334 iteration、1332有效更新、4002实际曝光、覆盖4000条，共同初值审计通过。原流水线因off trace的retrieved_ids为null触发校验迭代错误而停止；模型与推理本身未因此改动。现仅修复这一行校验并新增3项回归，完整145项CPU测试通过。原失败记录、495条control/off不完整输出和全部权重保留。新恢复目录为 /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-bias-validation-v1/recovery-v2/ ，当前状态见该目录state.json。复用完整zero_init/off500及两组retrieval；GPU0补跑control/off再random，GPU1补跑zero_init/random，后续自动完成配对报告，不重新训练。新的121项输入/代码/输出锁已验证。完成报告改为恢复目录的SUMMARY.md、summary.json，父目录state.json保留原失败事实。


偏置验证最终结果（2026-10-16）：恢复流水线于北京时间2026-10-16 11:50:01全部完成，恢复目录state.json为complete。全部12个计分条件（含复用参考）各500条、零错误，11项配对评测完成；两组训练实际4002曝光、覆盖4000条及共同初值审计均通过。报告位于 /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-bias-validation-v1/recovery-v2/SUMMARY.md ，独立完成检查为同目录completion-validation.json。

Stage B普通初始化：正常检索45.9177%、随机46.0183%、关闭46.5298%；零偏置初始化：正常检索46.3550%、随机46.2292%、关闭46.6102%。zero正常减control正常为+0.4373个百分点，95%配对CI[-0.0724,+1.0020]，跨0且未达预设+0.5个百分点参考。zero正常减自身off为-0.2552个百分点，CI[-1.2040,+0.7354]；减自身random为+0.1258个百分点，CI[+0.0145,+0.2993]，是很小的单seed样本信号，不代表总体Memory增益。两组正常/随机标签集合均495/500一致。最终bias范数control0.54759、zero0.00484；初始去偏置保留了很小的可学习bias，但未证明任务性能受益。Stage A推理直接清零相对原正常检索为-0.2111个百分点、CI跨0。

结论：该有界试验未通过预设扩展条件，不据此继续增加图复杂度或全31K训练预算；也不能宣称所有检索方法无效。当前只有seed42，区间仅反映样本不确定性，多项探索比较未做族错误校正，source开发集已被共同基线见过；不能作为正式目标或九benchmark成绩。当前未启动新研究任务，holdout和目标集未评测，原失败及不完整预测仍保留。

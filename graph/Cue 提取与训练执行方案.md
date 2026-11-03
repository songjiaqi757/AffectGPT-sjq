# AffectGPT-AMG Cue 提取与训练执行方案

协议冻结日期：2026-10-19；实施同步日期：2026-10-20（北京时间）。当前标注协议为 `qwen_omni_api`，Teacher 为 `qwen3.8-omni-flash`，本体为 `cue_ontology_v1.2`。本文以服务器实际代码、严格数据包和九组运行配置为依据：第0、5、6、16、17节记录当前实施，第4、8–10节同时说明尚待完成的人工评估、阈值与AMG工作，第12–15节保留明确注明时间和统计总体的标注历史。工程训练已启动，不将训练启动、测试通过或Teacher一致性指标写成人工准确率验收。

全部代码、数据、日志、权重和文档只在服务器 `/ai/sjq/AffectGPT-sjq` 中处理，不下载或留存本地。

## 0. 当前执行状态与数据口径

### 0.1 Teacher 输入与标注结果

- Text Teacher：同一次请求输入 `chinese`、`english` 两个独立字段，不拆成两个文本任务。证据注明ZH/EN，翻译不作为重复陈述；影响判断的实质冲突使用uncertain。
- Audio Teacher：完整连续16 kHz、单声道、PCM16 WAV；不抽稀疏窗口、不拼接、不裁时长，不附转录或数值声学代理量。
- Visual Teacher：完整原视频移除音轨后以 `video_url` 上传；默认Base64 MP4，大小或解析兼容项使用已验证的官方私有临时文件URL。客户端不抽帧、不缩放、不截断；通常复制视频流，兼容项完整H.264 CRF18转码并保留范围。云端内部处理未知，不宣称云端逐帧无损观察。
- 三模态由同一API模型执行三个独立任务，不输入源Emotion或目标description。画面烧录字幕尚未物理遮挡，仅通过Prompt要求忽略，须保留此审计限制。
- 原始成员来自 `dataset/mer2025-dataset/track2_train_mercaptionplus.csv` 的name字段，双语文本来自 `subtitle_chieng.csv`。原始31,327条样本对应93,981个模态任务、1,315,734个Cue位置（15/17/10维）。
- 旧30条试标标签及原始响应已按用户要求删除；`cue_annotation/runs/pilot30/`仅保留输入/媒体，不作为当前可复核标签。全量单独调用API，不复用旧标签；旧本地30B Teacher已删除。

最终队列已结束，无pending/running任务：

| 模态 | 成功任务 | 最终失败任务 |
|---|---:|---:|
| Text | 31,323 | 4 |
| Audio | 31,322 | 5 |
| Visual | 31,258 | 69 |
| 合计 | 93,903 | 78 |

78个失败是模态任务，涉及 **72条不同样本**；其中73项内容审核拒绝、5项视频过短。三模态均成功的样本为31,255条。标注状态为complete_with_failures，不再使用中途快照估算标注剩余时间。

### 0.2 当前生效的整样本排除与划分

执行 `all_modalities_succeeded_v1`：**任意模态标注失败，就整条样本从训练、验证和人工300条中排除**；独立诊断保留集同样只接收三模态均成功样本。72条失败样本的任一模态均不进入当前release。原始成功标注和失败记录保留用于追溯，不等于仍可参与其他模态训练。

| 工程角色 | 样本数 | 用途 |
|---|---:|---|
| pseudo_train | 27,679 | Teacher伪标签训练 |
| pseudo_validation | 3,076 | 早停、开发比较 |
| gold_audit | 300 | 人工盲审保留，人工标签尚未完成 |
| diagnostic_reserved | 200 | 独立诊断保留 |
| 合计 | 31,255 | 全部三模态标注成功 |

训练角色中，某模态所有Cue均为uncertain/unobservable时，该样本不参与该模态优化。这与模态任务失败不同，不取消其已合格的其他模态成员资格：

| 模态 | 实际优化样本 | 无有效监督而跳过 | 验证样本 | 训练有效Cue监督 | 验证有效Cue监督 |
|---|---:|---:|---:|---:|---:|
| Text | 27,673 | 6 | 3,076 | 397,290 | 44,117 |
| Audio | 27,679 | 0 | 3,076 | 331,334 | 36,878 |
| Visual | 27,677 | 2 | 3,076 | 253,399 | 28,164 |

三模态成功的31,255条中，四个角色合计的标签分布如下（单位为Cue位置，**不是仅训练集统计**）：

| 模态 | positive | negative | uncertain | unobservable | unlabeled |
|---|---:|---:|---:|---:|---:|
| Text | 62,015 | 386,584 | 19,157 | 1,069 | 0 |
| Audio | 67,990 | 306,213 | 49,354 | 107,778 | 0 |
| Visual | 66,398 | 219,758 | 22,323 | 4,071 | 0 |

### 0.3 当前发布物、运行目录与状态来源

以下路径均相对 `/ai/sjq/AffectGPT-sjq`：

| 路径 | 作用 |
|---|---|
| `cue_annotation/protocols/qwen_omni_api/` | 冻结本体、配置及三套Prompt |
| `cue_annotation/runs/mercaptionplus/` | 原始样本、标注JSON、原始响应、CSV和SQLite队列 |
| `cue_student/artifacts/release_strict_all_modalities_20261020_163131/` | 当前唯一生效的严格工程数据包 |
| `cue_student/splits/holdout300/` | 修订后固定人工300条名单与指纹 |
| `cue_student/jobs/latest_all_experiments.json` | 五组基线与新增四组的统一索引 |
| `cue_student/jobs/strict_all_modalities_20261020_163131/` | 五组基线的配置、status.json及日志 |
| `cue_student/jobs/full_finetune_20261020_170308/` | 新增四组全量微调的配置、status.json、显存包装入口及日志 |
| `cue_student/output/<job>/<run>/` | 各实验的checkpoint、事件、验证预测和输入观察记录 |

当前release_id：`2019ab786e4e065699a3f980291b1d300a17ee1ec9a18213672f620fd2823ac7`。
当前holdout_id：`8d384d71d1aed030adb5f480f5b28a4379c48ffda9c6bc1be1648f8fc6ca8224`。

原始标注完成状态以SQLite及最终导出共同核对；训练进度以两个job的 `status.json`、各run的 `events.jsonl` 和实际进程为准。`cue_annotation/viewer/`下方旧试标区的“0条标签”不代表全量进度；静态文档也不替代运行状态。

### 0.4 九组实验的当前实施范围

截至本次核对，九组均已启动并发生实际optimizer更新。五组严格基线为Text、Audio mean、Audio temporal、Visual mean、Visual temporal；新增四组为Audio mean/temporal全量微调、Visual mean/temporal全量微调。全部使用同一严格release和固定人工300条，均从对应预训练编码器新建Student，不沿用曾含失败样本的旧Student权重。

- GPU0共六组：`text`、`audio`、`audio_temporal`、`audio_full`、`audio_temporal_full`、`visual_full`。
- GPU1共三组：`visual`、`visual_temporal`、`visual_temporal_full`。
- 九组均使用已实施的输入加载优化；新增四组启用gradient checkpointing和每进程20%的PyTorch CUDA allocator预算，详见第6节。
- 人工300条盲审、60条双标、全面来源/内容近重复核验、人工阈值校准、OOF建库及AMG尚未完成。本轮属于明确披露限制的Teacher伪标签工程实验，不宣称已得到最终人工性能。

## 1. 固定协议、输出层与成本

### 1.1 API与Prompt

接口：`https://maas.qianwenaiapi.com/compatible-mode/v1/chat/completions`；模型：`qwen3.8-omni-flash`。生成参数固定为 `temperature=0`、`reasoning_effort=none`、`response_format={"type":"json_object"}`、`max_tokens=3072`、`stream=false`、`modalities=["text"]`。并发/RPM/TPM属于运行配置，不改变Prompt和Cue定义。

| 模态 | Prompt SHA256 |
|---|---|
| text | `46a44e9c46a2d24a48a916e7a02211a6225caff10d66ab2d8eaad08f09536de6` |
| audio | `cab586cf3804d378916322929e027a59c0a19122e0ac65dbf4d7da545657b500` |
| visual | `9acbba0d5ec71bbf18906c924c1a93198d011646f1dedb48fb566b57589fb4cd` |

每个响应必须含唯一的 `sample_id`、`modality`、`labels`，对应模态的Cue恰好出现一次；每项仅含 `state`、`evidence_note`。状态仅positive/negative/uncertain/unobservable，positive、uncertain、unobservable均须有非空证据。还检查返回模型名称、`finish_reason=stop`与JSON/schema完整性。缺字段、解析失败和输出截断作为任务失败处理，不自动补negative。

```json
{"sample_id":"sample_id","modality":"visual","labels":{"VIS_SMILE_PRESENT":{"state":"negative","evidence_note":""}}}
```

此例仅说明结构；实际视觉响应须包含全部10个视觉Cue，另外两种模态分别为15和17项。本体ID固定为 `cue_ontology_v1.2`。

### 1.2 API原始判断与训练监督层

`teacher_raw/`保存每次API响应/错误及请求哈希；`annotations/`保存通过校验、可能附带明确质量处理的最终模态记录；`inputs/`保存实际输入、媒体和请求哈希。原`media/audio/`、`media/video/`为完整API输入副本，已按第15节清理；原始dataset和历史输入元数据保留，后续输入按需恢复。旧试标的8张浏览缩略图不属于API帧输入。

一般映射：positive→y=1/mask=1；negative→y=0/mask=1；uncertain/unobservable→y空/mask=0。失败/待处理只在导出层使用unlabeled→y空/mask=0，不能将其解释为模型判断“看不见”或“没有”。

`VIS_TEARING_PRESENT`与其他Cue采用相同处理：保留API原始state和evidence_note，positive→y=1/mask=1，negative→y=0/mask=1，uncertain/unobservable→y空/mask=0。按用户2026-10-20最新要求，已取消流泪专用门控，902条原始阳性恢复为positive，不添加逐样本人工确认或批量指定标记。此前200条中途快照和902条全量候选的屏蔽属于历史处理，现已撤销；原始模型响应不变。

### 1.3 已完成标注的用量与训练工期口径

首轮与定向补标均已结束。包括最后5次完整短视频复验，累计94,366次模型HTTP尝试；本地记录usage总计303,109,687 tokens，其中输入265,580,873、输出37,528,814。上传网络失败未计入模型HTTP次数，缺少usage的请求可能无法在本地完整计费，最终实付以平台账单为准。证据见全量运行目录的 `repair_summary.json` 与 `short_video_retry.json`。

历史00:40的费用外推和06:29预计结束时间已失去当前调度意义，不再作为未完成任务或当前价格依据。Student训练不需重新调用Teacher。九组共享GPU后的工期需根据各组近期完整optimizer step耗时、剩余步数、验证/保存/加载开销动态计算，并注明观测时间；早停或其他任务结束释放资源会改变剩余时间，不能把五组独占时期的速度外推到九组。

## 2. Cue 语义与状态规范

### 2.1 样本级语义

每个 Cue 表示：

> 在该样本实际可观察的范围内，是否存在可复核证据支持这个 Cue。

它不表示完整原始视频在所有时刻都不存在该 Cue，也不直接表示人物的 Emotion
或 Appraisal。

-   **positive**：观察视图内至少有一处明确证据。
-   **negative**：观察范围和输入质量足以判断该
    Cue，且没有符合定义的证据。
-   **uncertain**：有相关观察信息，但证据含糊、相互冲突或边界难以稳定判断。
-   **unobservable**：观察条件本身不足以判断该
    Cue，例如无有效语音、画面没有可辨认的人脸、关键区域被遮挡或相对声学基线无法建立。
-   **unlabeled**：Teacher
    尚未成功给出该标签、输出解析失败或调用失败。它是数据流水线状态，不是
    Cue 的语义类别。

训练规则：

  Teacher 状态    是否进入主 BCE 监督  处理方式
  -------------- --------------------- ---------------------------
  positive                是           (y=1, m=1)
  negative                是           (y=0, m=1)
  uncertain               否           (m=0)
  unobservable            否           (m=0)
  unlabeled               否           (m=0)，重试或记录失败原因

不得把"Teacher 没有输出某个 Cue"自动当作 negative。

**标签使用补充：不是只使用positive。** 对同一个Cue，positive是“存在”，negative是“观察充分但不存在”；两者共同训练独立二分类，不能理解为积极/消极情绪。uncertain、unobservable保留状态用于审计和覆盖分析，unlabeled保留失败原因；三者当前都不进入主BCE，不当negative、不设成0.5。主模型不因此自动具备四状态预测能力，详见第7节。

上述为语义状态与原始导出约定；实际训练成员另外执行第5节整样本失败排除。当前release不含任一模态任务失败的样本，不能仅靠该模态mask=0让其他模态继续参与训练。

### 2.2 样本级聚合规则

所有标签都是**样本级存在性/可观察性判断**，不要求输出精确时间戳，但内部可保留证据片段供人工审计。

- **事件型 Cue**（如笑声、哭泣、可见泪水）：在模型实际观察到的任一有效位置发现清晰证据即可为 `positive`。
- **局部状态/韵律 Cue**（如相对语速、相对音高、语调）：完整输入范围内只要有一个可比较片段满足冻结定义，即可为 `positive`；相反 Cue 可以同时为 `positive`，但必须由不同片段或不同语句支持。
- **文本结构 Cue**：只依据本样本实际送入Teacher的中文与英文独立字段，保留语言边界与证据来源，不从音频或视频补推。
- **negative**：只有在相关模态输入完整、相关区域/语音足够可观察、处理过程没有明显截断或覆盖不足时，才表示“观察充分但未发现 Cue”。
- **uncertain**：证据可见但存在真实歧义、强弱处于边界，或采样结果无法支持稳定二分判断。
- **unobservable**：输入损坏/缺失、相关区域或语音不可见/不可听、相对 Cue 缺少可比较基线，或模型实际观察覆盖不足以判断。
- **平台处理边界**：完整视频文件交由API默认处理；无法知道内部帧时间点时不编造逐帧覆盖，也不单凭平台内部过程未知就强制判不可观测。按实际可见性、清晰度和歧义判断四状态。

第一版只训练样本级输出。`support_segments`、原始时间戳、帧索引或分块索引可以作为 Teacher 审计元数据，但不是 Student 的强制监督目标，也不是强制的图节点。

### 2.3 样本级主体约定

第一版采用"样本内任意主体"的语义：

-   视觉 Cue：任意可辨认人物出现符合定义的表现即可。
-   音频 Cue：任意可听到的声音或说话者出现符合定义的声学表现即可。
-   不要求将视觉人物与音频说话者匹配。
-   不把样本级 Cue 解释为特定目标人物的心理状态。
-   对相对音高、相对语速等标签，仍然不能跨说话者直接比较绝对数值；必要的同一说话者参照不足时应标为
    unobservable。

当前采用样本级规则，但尚未对全量完成单人/多人镜头比例审计，不以“基本单人镜头”作为已验证前提。但样本级
Cue
仍不等于严格的人物身份绑定，也不能直接解释为某个指定人物的心理状态。若未来需要主体级情绪解释，应另行升级本体/数据结构。

------------------------------------------------------------------------

### 2.4 正例、反例与不可判定状态：必须统一理解

**正例/Positive 不是"人物情绪积极"，反例/Negative
也不是"人物情绪消极"。** 它们只描述某一个指定 Cue
是否在当前模态的规定观察范围中出现。

-   `positive`：该 Cue 存在明确、可复核的证据，对应训练目标 `y=1`。
-   `negative`：观察充分，但没有符合定义的 Cue 证据，对应训练目标
    `y=0`。
-   `uncertain`：观察到相关现象，但是否满足 Cue 定义仍有歧义。
-   `unobservable`：输入或观察条件不足，无法可靠判断该 Cue。
-   `unlabeled`：标注流程未成功产出标签，例如模型调用失败、JSON
    解析失败或 Cue 遗漏；它不是语义标签。

示例：

  -------------------------------------------------------------------------------------------------------------
  模态 / Cue                   观察内容                             状态           说明
  ---------------------------- ------------------------------------ -------------- ----------------------------
  Text:                        "I am happy."                        positive       出现正向情绪词 `happy`
  `TXT_AFFECT_WORD_POSITIVE`                                                       

  Text:                        "I am tired."                        negative       文本清晰，但没有正向情绪词
  `TXT_AFFECT_WORD_POSITIVE`                                                       

  Text:                        "I am not happy."                    positive       词面 Cue 仍存在；否定由
  `TXT_AFFECT_WORD_POSITIVE`                                                       `TXT_NEGATION_PRESENT`
                                                                                   单独记录

  Audio:                       清楚听到笑声                         positive       声学事件出现
  `AUD_LAUGHTER_PRESENT`                                                           

  Audio:                       音频清晰、观察范围充分，未听到笑声   negative       已观察且不存在该事件
  `AUD_LAUGHTER_PRESENT`                                                           

  Audio:                       语音太短，无法建立相对语速参照       unobservable   不能强行判为 negative
  `AUD_SPEECH_RATE_REL_FAST`                                                       

  Visual: `VIS_SMILE_PRESENT`  完整视频的实际观察范围内至少有一处清楚显示微笑           positive       样本级存在即可

  Visual: `VIS_SMILE_PRESENT`  相关面部区域在实际观察范围内充分可见且没有微笑           negative       观察充分且未发现

  Visual: `VIS_LIPS_PRESSED`   嘴部被遮挡                           unobservable   没有足够信息判断
  -------------------------------------------------------------------------------------------------------------

同一条样本可以对不同 Cue 同时具有不同状态。例如，"I am not happy"
可以同时让
`TXT_AFFECT_WORD_POSITIVE=positive`、`TXT_NEGATION_PRESENT=positive`；这并不矛盾，因为两个
Cue 判断的对象不同。

**禁止的简化规则：** 1. 不得把模型未输出的 Cue 自动填为 negative。 2.
不得把 `uncertain`、`unobservable` 或 `unlabeled` 转成 `y=0`。 3.
不得因为样本整体情绪看起来积极/消极，就推断相应的词语、声学或视觉 Cue
必然存在。 4. 不得把一个 Cue 的存在自动推导成另一个 Cue 的存在。

## 3. 42 个 Core Cue 的操作性示例与边界登记表

本节将 Prompt
中的操作性定义配上简短正例、反例和易混淆边界，供标注培训、审计和 Prompt
版本管理使用。示例是解释规则的合成例子，不是 MER-Caption+
的真实样本，也不是新增标签。`negative`
的含义始终是"观察充分但没有这个具体 Cue"，而不是相反情绪。

如果某条示例与正式 `AMG Cue Ontology v1.2`
定义冲突，应停止新的标注任务并核对本体；若需要改变 Cue
的语义而不只是澄清标注操作，应升级 `cue_ontology_version`。

### 3.1 Text Core Cue（15 类）

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Cue ID                                    正例示例/条件                  反例示例/条件          边界与易混淆项
  ----------------------------------------- ------------------------------ ---------------------- ---------------------------------------------------------------------------
  `TXT_AFFECT_WORD_POSITIVE`                "I feel happy." 中出现         "The train arrives at  只判断词语/短语是否出现；"not happy"仍是正向情绪词出现，同时可标否定结构。
                                            `happy`。                      noon."                 
                                                                           中没有正向情绪词。     

  `TXT_AFFECT_WORD_NEGATIVE`                "I feel miserable."            "The train arrives at  不以整句总体情绪代替词面判断；"not sad"仍出现负向情绪词。
                                            中出现明确负向情绪词。         noon."                 
                                                                           中没有负向情绪词。     

  `TXT_EVALUATION_POSITIVE`                 "That was an excellent         "The result was        评价对象可以是人、事、物或结果；不要把正向情绪词自动当作正向评价。
                                            result." 明确给出正向评价。    announced at noon."    
                                                                           只陈述事实。           

  `TXT_EVALUATION_NEGATIVE`                 "That was a terrible           "The decision was      注意否定作用范围；单纯提到负向词不一定等于整句负向评价。
                                            decision." 明确给出负向评价。  announced yesterday."  
                                                                           只陈述事实。           

  `TXT_NEGATION_PRESENT`                    "I do not agree." 有语义否定。 "I agree with you."    只标真实的否定功能，不把转折或不确定性当成否定。
                                                                           没有否定结构。         

  `TXT_CONTRAST_PRESENT`                    "I wanted to leave, but I      "I wanted to leave and 需要对比/转折关系；仅有两个不同事件不够。
                                            stayed." 有显式转折。          then I stayed."        
                                                                           只是顺序陈述。         

  `TXT_INTENSIFIER_PRESENT`                 "I am extremely tired." 中     "I am tired."          不把普通形容词本身当作强化词；按上下文判断 `so` 等词是否起强化作用。
                                            `extremely` 加强程度。         没有显式程度强化词。   

  `TXT_UNCERTAINTY_HEDGE`                   "Maybe this will work."        "This will work."      "I
                                            显式表达不确定。               直接断言，没有 hedge。 think"仅在语境中确实弱化承诺/表达不确定时才标；不要把所有第一人称观点都算
                                                                                                  hedge。

  `TXT_RHETORICAL_QUESTION`                 在明显反问语境中说 "Who could  "Where is the          仅有问号不够；若功能不清楚，用 uncertain，而不是自动标正例。
                                            believe                        station?"              
                                            that?"，不期待真实信息回答。   主要是在询问信息。     

  `TXT_EXCLAMATION_INTERJECTION`            "Wow, that is amazing!"        "Please close the      标点单独不足以证明 Cue；区分表达性话语标记与普通句子。
                                            中有明确感叹/感叹词。          door." 是普通指令。    

  `TXT_DESIRE_NEED`                         "I hope to see you again."     "I saw you yesterday." 不从行动结果反推欲望；需文本显式表达希望、想要、需要或目标。
                                            明确表达愿望。                 只陈述过去事件。       

  `TXT_EXPLICIT_CAUSAL_ATTRIBUTION_SELF`    "I caused the delay."          "I noticed the delay." 同时提到自己和事件不够；必须有显式因果/责任归因。
                                            明确把延误归因于自己。         只是提及自己与事件。   

  `TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER`   "He caused the delay."         "He was there when the 必须明确另一人物/行动者是原因；主体不清楚时用 uncertain。
                                            明确把延误归因于他人。         delay happened."       
                                                                           只是共现。             

  `TXT_EXPLICIT_SUCCESS_OUTCOME`            "I passed the exam."           "The exam was          正向评价不等于成功结果；需要明确成功、获胜、完成或达成目标。
                                            明确陈述达成结果。             difficult."            
                                                                           没有陈述成功结果。     

  `TXT_EXPLICIT_FAILURE_LOSS_OUTCOME`       "I failed the exam."           "The exam was          负向评价不等于失败结果；需明确失败、失去、被拒绝或未达成目标。
                                            明确陈述失败结果。             difficult."            
                                                                           没有陈述失败结果。     
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Text 通用边界：** 中文和英文为独立字段，只依据各字段实际表达的线索，证据注明ZH/EN；不得从其他模态恢复缺失内容，不把翻译当作重复陈述；影响判断的实质语义冲突使用uncertain。空文本不统一补成negative，短文本按具体Cue是否可判断处理。

### 3.2 Audio Core Cue（17 类）

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Cue ID                           正例示例/条件                                                反例示例/条件                                  边界与易混淆项
  -------------------------------- ------------------------------------------------------------ ---------------------------------------------- ----------------------------------------------------------------------------
  `AUD_SPEECH_RATE_REL_FAST`       同一说话者的有效观察中，有一段清楚比可比的自身基线更快。     有充分可比语音，未发现明显快于基线的片段。     不能跨说话者比较绝对语速；无基线/语音太短为 unobservable，差异模糊为
                                                                                                                                               uncertain。

  `AUD_SPEECH_RATE_REL_SLOW`       同一说话者的有效观察中，有一段清楚比可比的自身基线更慢。     有充分可比语音，未发现明显慢于基线的片段。     `REL_FAST=negative` 不推出 `REL_SLOW=positive`；二者分别判断。

  `AUD_PITCH_LEVEL_REL_HIGH`       同一说话者某段可比较语音的音高明显高于其样本内基线。         基线充分，未发现明显高于基线的片段。           不把天生高音区当成相对高；无基线为 unobservable。

  `AUD_PITCH_LEVEL_REL_LOW`        同一说话者某段可比较语音的音高明显低于其样本内基线。         基线充分，未发现明显低于基线的片段。           不把低音说话者与高音说话者直接比较；与语速 Cue 独立判断。

  `AUD_VOCAL_INTENSITY_REL_HIGH`   录音条件稳定、可比较时，某段人声强度明显高于样本内基线。     可比较且未发现明显高于基线的人声强度。         麦克风距离、增益、背景噪声可能伪造响度差异；条件不可靠时 unobservable。

  `AUD_VOCAL_INTENSITY_REL_LOW`    录音条件可比较时，某段人声强度明显低于样本内基线。           可比较且未发现明显低于基线的人声强度。         不把静音、音轨缺失或远距离录音直接当作低声强。

  `AUD_PITCH_VARIABILITY_HIGH`     一段可辨识的有声语音中出现清楚、幅度较大的音高起伏。         音高轨迹充分可观察且没有明显的大幅起伏。       需要可用有声段；F0 跟踪错误或背景音干扰时不要强行判断。

  `AUD_PITCH_VARIABILITY_LOW`      有足够语音且音高变化持续狭窄、平稳。                         可观察语音中存在清楚且频繁的大幅音高变化。     高/低变化可在不同片段分别出现；同一片段同时判高低须有明确分段证据。

  `AUD_PAUSE_LONG`                 有效窗口内可听到一处明显长停顿，且不是文件缺失或窗口间隔。   有充分语音观察，未出现超过冻结标准的长停顿。   只判断输入窗口内部；非连续窗口之间的空档绝不是停顿。若用
                                                                                                                                               VAD，冻结最小停顿时长。

  `AUD_PAUSE_FREQUENT`             有效窗口内多个停顿反复打断语流，达到冻结的频次标准。         语音足够且停顿未达到冻结频次标准。             不把自然的窗口边界或采样间隔算入；频次阈值需在试标中与人工判断核对并冻结。

  `AUD_INTONATION_RISING`          可听到短语/话语末端或局部语调明确上扬。                      有充分语音观察，未出现明显上扬语调。           不能因为句子是疑问句就自动标上扬；要根据实际声音判断。

  `AUD_INTONATION_FALLING`         可听到短语/话语末端或局部语调明确下降。                      有充分语音观察，未出现明显下降语调。           句法上的陈述句不自动意味着下降；必须有声学证据。

  `AUD_INTONATION_FLAT`            有足够可观察语音，整体语调明显平直、缺少旋律变化。           可观察语音有清楚且有意义的语调起伏。           与低音高变化相关但不完全相同；不能仅凭低音量判断平直语调。

  `AUD_VOICE_TENSE`                能听到明显挤压、紧绷、用力或受压发声。                       声音质量充分可听，未见明显紧绷/受压发声。      大声、愤怒语义或高音本身不足以证明声带紧张。

  `AUD_VOICE_TREMBLING`            声音存在可听辨的不稳定颤动。                                 声音足够清晰且没有明显颤抖。                   普通 F0 起伏、录音抖动或噪声不等于声音颤抖。

  `AUD_LAUGHTER_PRESENT`           任一有效窗口中清楚听到笑声或轻笑。                           所有有效观察充分，均未听到笑声。               不因台词好笑而推断笑声；若音频无效或未包含可判断声音，标 unobservable。

  `AUD_CRYING_SOBBING_PRESENT`     任一有效窗口中清楚听到哭泣、抽泣或可辨识的哭声。             有效音频充分，未听到哭泣/抽泣。                不因台词悲伤或声音低沉而推断哭泣。
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Audio 通用边界：** 对相对快慢、高低和强度，先判断参照是否成立，再判断
Cue。对长停顿/频繁停顿，任何算法阈值都必须在正式审计前冻结；不得把非连续窗口之间的缺失时间当作静音。当前固定协议不向API提交多个分段，整段一次输入；将来若需分块，须另行验证、固定聚合并升级协议。


#### 3.2.0 当前停顿规则与原始标签使用口径

当前Audio Teacher只听完整音频，不接收外部VAD区间、F0、响度、语速代理值或ASR转录。代码没有在本轮执行silero-vad/F0统计流水线；不能把模型证据中的听感描述当作已计算的声学数值。

当前Prompt包含的候选规则为：内部停顿≥0.3秒、长停顿≥1.0秒；频繁停顿为连续10秒范围中至少3个合格内部间隔，且须有至少5秒有效语音。首尾静音、缺失音频、padding或分块边界不算停顿。阈值只是已固定在Prompt中的候选定义，尚未经人工金标准验证；本轮实际提交单个完整音频，不做分块聚合。

**资格偏差诊断。** 00:40历史快照中，短于5秒的频繁停顿二分项有2,600条；全量结束后为11,395条（negative 11,381条、positive 14条）。总时长不足5秒不可能包含至少5秒有效语音，这些模型判断与Prompt资格规则存在冲突；冲突清单只用于记录和后续语义审计，不作为当前标签修改或屏蔽条件。

按用户最新要求，长停顿与频繁停顿均和其他Cue一样直接使用大模型原始state及evidence_note：positive→y=1/mask=1，negative→y=0/mask=1，uncertain/unobservable→y空/mask=0。取消此前方案中按时长资格另外屏蔽二分项的计划；该额外屏蔽此前也未实际应用。11,395条诊断项保留原始二分监督，不新增专用门控、覆盖标记或人工确认要求。冻结Prompt不改、不重新调用API；这不表示上述规则冲突已通过人工语义验证。

如后续引入silero-vad测量，则另行固定VAD版本、阈值、有效语音资格和停顿统计，并作为独立诊断/Student特征消融验证；不得宣称本轮Teacher已经使用了这些数值。

#### 3.2.1 相对声学Cue：当前听觉比较与后续数值对照

六个相对Cue为语速快/慢、音高高/低、强度高/低。当前Prompt要求同一样本、同一可比较声音内至少两个足够的语音片段，且信号质量允许比较；不要求三个固定2秒窗口，两个任意相邻词也不自动形成参照。先判断参照成立，再判断是否存在不能由语音内容、句型、增益/距离等解释的明显偏离：无参照为unobservable，有参照无偏离为negative，边界不清为uncertain。

当前由模型听感执行这一流程，未独立测得F0/RMS/语速baseline，也未自动证明“same speaker”或有效语音资格。高mask比例须在人工审计中解释，不能为了增加正例将unobservable改为negative。

后续HuBERT与声学特征对照可采用冻结的VAD单位、有效F0、响度/能量、语速代理量及稳健median/MAD基线；特征与阈值须在源域开发集验证。它们属于后续研究，不是本轮API输入或已执行的冻结数值标准。若缺少可学的正负例或可靠参照，依据独立审计考虑core_deferred，不因维持42维而强行激活。

### 3.3 Visual Core Cue（10类，按当前执行Prompt澄清边界）

| Cue ID | 直接可见的合格证据与主要排除项 |
|---|---|
| `VIS_BROWS_FURROWED` | 眉部明确向内收紧/聚拢；低眉、阴影或低头本身不够。 |
| `VIS_BROWS_RAISED` | 明显上抬构形或同一人物的可见抬眉；天生拱眉本身不够。 |
| `VIS_EYES_WIDENED` | 明显增大的眼裂；相机距离或天生大眼不等于睁大。 |
| `VIS_EYES_SQUINTED` | 明确眯眼/眼裂缩窄；眨眼、向下看或自然小眼型不够。 |
| `VIS_SMILE_PRESENT` | 嘴角上扬运动或明确的微笑构形；不从字幕/假定快乐推断。 |
| `VIS_MOUTH_CORNERS_DOWN` | 可与透视、惯常面形、普通发音区分的嘴角下垂；张嘴说话不够。 |
| `VIS_LIPS_PRESSED` | 上下唇主动压紧、挤压或变平；普通闭嘴、短暂停顿或双唇发音闭合不够。 |
| `VIS_GRIMACE_PRESENT` | 明显扭曲构形，如鼻部/上唇清楚扭曲；不能由皱眉加闭唇自动推出。 |
| `VIS_TEARING_PRESENT` | 可区分的眼睑/面颊泪滴，或起于眼部的狭窄泪痕；反光、皮肤亮斑、眼袋、妆容、汗液或悲伤表情本身不够。直接采用API原始状态，按第1.2节通用规则映射y/mask。 |
| `VIS_HEAD_LOWERED` | 以可见躯干/姿态为参照的明确低头；静态低头也可成立，不强制要求运动；视线、相机倾斜或裁剪本身不够。 |

任何可辨认人物在片段内一处清晰合格证据可支持样本级positive。关键区域充分可见且未发现合格证据可为negative；模糊、遮挡、分辨率或姿态参照不足分别使用uncertain/unobservable。不因平台内部抽帧过程未知就统一强制unobservable。模型给出的近似时间戳仅供复核，不能当作人工验证的帧级真值。

## 4. 人工金标准与 Teacher 审计

### 4.1 当前阶段与试标记录边界

接口试标、输入/JSON验证、全量伪标注、严格工程release及九组训练启动均已完成。旧30条标签和原始响应已删除，不再作为可复核实验结果。人工盲审及独立双标尚未完成，不能把接口通过、数据发布或训练启动写成Teacher准确率通过。

当前顺序为：冻结API/Prompt → 全量Teacher标注与技术补标 → 整样本失败排除、固定保留名单和工程数据发布 → 九组工程训练；独立人工评估仍待实施。若重新开展30–50条人工校准，应另登记开发角色，标注者只看对应模态，不先看Teacher、Emotion或目标description。若修改协议，须建立新版本并明确受影响重标范围。

### 4.2 正式人工审计：固定300条

同一批300条同时覆盖Text、Audio和Visual。当前所有保留样本都满足三模态标注成功，但尚无人工参考标签，名称 `gold_audit` 表示预留用途。

- 在查看审计答案前冻结本体、模型、Prompt、输入协议、JSON Schema及Student开发选择；不据gold结果反复改架构或原地改伪标签。
- 每条由至少1名标注者盲标；只看对应模态，不先看Teacher、Emotion或description。固定60条由第二人独立盲标，分歧按预登记规则仲裁。
- 300条及其已知同源/字节级重复成员均不进入Student训练、验证、早停或架构选择。即使已有Teacher标签，也不能作为训练样本。
- 若据审计结果修改Teacher或训练方案，该批需按实际用途登记为开发数据，新版本独立评估另行设计；不得继续宣称同批结果独立。

#### 4.2.1 当前名单及299+1修订来源

最初按种子42固定300条，先排除49条工程开发暴露样本及其字节级音视频重复。采用整样本失败排除后，原名单中 `samplenew3_00094241` 因视觉失败移除，其余299条保留；以 `samplenew3_00039200` 补齐。

补充候选来自旧 `diagnostic_reserved` 独立保留集中的三模态成功成员，排除旧训练/验证/开发组与已知音视频字节级重叠，按种子42确定候选顺序，不读取Cue、Emotion或description值。当前名单属于“原299条合格成员＋独立候选补1条”，不能描述为重新在31,255条中均匀随机抽300条。名单修订与候选总体须随评估一并披露。

当前文件：

- `cue_student/splits/holdout300/sample_ids.csv`、`sample_ids.txt`：固定300条ID。
- 同目录 `members.json`：输入及原始媒体指纹。
- 同目录 `manifest.json`：当前holdout_id、旧名单、删除ID、保留299条、补充候选和种子及新ID；当前ID见第0.3节。

prepare与训练再次检查保留名单、eligibility、已知组及媒体重复，checkpoint绑定当前holdout_id。不得静默重抽名单。

原视频来源仍未全面核实，不能从samplenew3_*名称推断独立性；字节级SHA256也不能排除不同编码或剪辑的近重复。后续补充可信 `video_source_id` 或已验证重复簇。若与既往开发成员同源，登记审计独立性问题并阻断未说明的发布；若仅与未开发成员同源，将整组其余成员排除训练/验证，不能暗中替换固定保留ID。

#### 4.2.2 双标名单：60条

当前release manifest的 `split.double_annotation_sample_ids` 已固定60条，种子43，均为当前300条的子集，三模态共用。实际按样本ID抽取；可信来源分组尚未齐备，不能称为已按video_source_id完成分组抽样。60条只是名单，尚未完成第二人标注或一致性评估。若后续发现来源关联，在审计报告中披露并按组分析。

### 4.3 稀有 Cue 补充

对笑声、哭泣、可见泪水等稀有 Cue，若随机 300
条中的正例或负例不足，可定向补充约 50--200 条，或补充到足以分析为止。

- 主审计集使用第4.2.1节当前固定的300条，披露排除开发暴露、三模态成功筛选和299＋1修订来源；不能声称是原始31,327条或当前31,255条的重新均匀随机300条，也不代表稀有Cue定向样本的质量。
- 定向补充集用于稀有Cue诊断；同时覆盖Teacher阳性、阴性及边界样本，不只复核阳性。若定向结果用于改训练策略，应登记独立开发角色，不能混作最终gold。
- 对拟作为独立最终诊断的数据，先预留候选来源组并排除出训练/早停，再定向抽样。已参与训练的同源样本不能事后变成独立测试。
- 两者分开报告；不能直接混合后计算自然分布总体指标。以原始总体历史比例粗估，均匀300条约只有1.9个频繁停顿伪阳性；这是历史预算估计，不是当前修订名单的支持数或人工真阳性数，不保证逐类五折阈值稳定。

### 4.4 必须报告的指标

逐模态、逐 Cue 报告：

-   Precision、Recall、F1。
-   正例数、负例数、uncertain 数、unobservable 数。
-   Teacher 预测为正的数量及 Teacher--Human 混淆矩阵。
-   人工双标一致性。
-   置信区间，尤其是稀有标签的区间。
-   每个 Cue 的覆盖率与可观察性比例。

不要只报告 42 个 Cue 的平均 F1。某些 Cue
可能整体准确率很高，但几乎没有正例，或者 Teacher 对其判断经常不可观察。

------------------------------------------------------------------------

## 5. 数据划分与泄漏控制

### 5.1 先整样本筛选，再分组和分配角色

当前策略 `all_modalities_succeeded_v1` 在划分前检查SQLite中的全部预期三模态任务，要求队列已结算且三模态均成功；对任何失败任务取sample_id并集。78项失败对应72条样本整条剔除，31,255条进入当前工程release。`cue_student/eligibility.py`、prepare和Release加载共同执行白名单与版本检查，不能通过改角色或仅屏蔽失败Cue绕过。

随后按可信来源和原始音/视频SHA256合并已知组，隔离固定300条及诊断角色，再以种子44将其余组分为约90/10的训练/验证；三模态共用同一角色，不能逐模态另抽。全量标签已生成不等于全量都可用于训练，原始失败样本的成功模态记录也只用于追溯。

已完成原始媒体字节级哈希与重复组的工程隔离；原视频来源、不同编码/剪辑的内容近重复及与九个目标数据集的来源重叠仍未全面核实。当前release明确 `scope=engineering` 并记录group_limitations；运行显式使用 `--allow-unverified-groups`，不能据此宣称来源完全独立。后续内容核验不读取目标标签，不根据目标性能调整重复检索规则。

### 5.2 当前角色与独立评估边界

当前样本数和实际模态监督数见第0.2节，角色清单以release的 `members.json` 和manifest为准：

- `pseudo_train`：27,679条候选训练成员；仅使用各模态有效positive/negative。
- `pseudo_validation`：3,076条，用于早停和九组开发比较，不用于拟合训练类权重。
- `gold_audit`：300条固定人工保留，不参与Student参数训练、早停或架构选择。
- `diagnostic_reserved`：200条独立保留；尚非已完成的人工诊断结果，不混入主300条统计。
- `teacher_pilot`：若后续重新设立人工开发校准，单独登记；已删除旧30条标签不作为当前结果。
- `gold_oof_evaluation`：未来人工gold在开发选择冻结后的交叉拟合评估视图，不是额外训练数据，也不是源域Memory折模型训练。

Teacher配置在人工审计前已冻结，盲审后可直接报告Teacher–Human。Student架构、聚合、损失和训练轮数由pseudo-validation开发选择。若利用gold校准每类阈值，预先固定5折分组交叉拟合：只用其他4折选阈值，在留出折评估；同一样本的人工答案不能选择自己的阈值。任一折缺乏正负支持时报告不足，不强行声称阈值稳定。最后用全部gold拟合部署阈值须与此前OOF性能区分；部署阈值在同批gold重算不是独立测试。

### 5.3 九个目标数据集的输入兼容性登记（只看元数据，不看标签）

在最终 zero-shot
评测前，建立一张只记录数据接口和输入可用性的表，至少包含：数据集名称、文本字段与语言、音频是否可用及语言、视频/帧是否可用、时长/分辨率格式、缺失模态比例、对应的预处理器版本。

-   这一步只用于确认输入管线是否能运行，不得查看目标 Emotion
    标签、目标性能或任何标签相关统计。
- Text Student 主模型固定为 `FacebookAI/xlm-roberta-base`（XLM-RoBERTa Base），可接收中文和英文；模型/分词器版本须一并冻结，多语言支持不等于不同语言Cue性能自动一致。
- 源域主协议固定同时读取samples.json的`chinese`和`english`独立字段，与Teacher一致；分别编码后聚合，不采用“原文优先、英文回退”替代双语监督。缺失语言通过language_present屏蔽；原始31,327条总体英文缺失588条（当前训练角色另计）。目标域按预注册字段适配已有双语；仅单语时可使用已支持的缺失字段路径，但单语与双语分别报告，不宣称与源双语性能等价。
- 不得在看到目标标签或性能后临时决定是否翻译、换字段或改预处理。zero-shot评测前登记每个目标域的实际字段、语言、来源、翻译与缺失情况；存在语言不兼容时，预注册保留可用单语、固定版本翻译或文本不可用策略。翻译新增/丢失词面Cue是输入协议差异，单独报告，不能静默适配。
-   任何目标域标签都不得用于 Prompt、Teacher、Student、阈值、Cue 选择或
    AMG 检索策略的调整。

### 5.4 已发布的严格工程数据包与指纹

生效目录、release_id与holdout_id见第0.3节。包内含 `manifest.json`、`members.json`、`labels.npz`、`ontology.json`、`eligibility.json`；全部文件SHA256登记在manifest，保留原31,327条总体与筛后31,255条总体、排除样本、分组限制、支持数和抽样来源。eligibility文件与强制策略一起核验。

本次严格包从此前已核验的发布物派生：核验父manifest及标注来源哈希，检查原媒体大小/mtime仍与原核验记录一致，复用此前完整SHA256核验的媒体身份，筛除72条并重建角色与哈希。没有在这次派生中再次逐字节重哈希全部媒体。保留成员对应93,765份成功模态标注、62,510个原始媒体引用；不把这些数写成原始全量总数。

常规prepare检查CSV重复/缺失/额外键、非法state与y/mask、成功标注JSON一致性及原媒体哈希；运行Dataset继续检查文件大小/mtime，不是每个训练step重复全文件SHA256。原API派生媒体已清理，其历史哈希只作提交证据。缺失/变更或eligibility不匹配应阻断，不能补成negative。

checkpoint绑定release、holdout、Cue顺序、配置、代码及编码器资产指纹；类权重等训练统计仅从pseudo_train计算。当前标签包是伪标签工程发布物，人工gold和全面来源/近重复验收仍未完成。

## 6. 三路 Cue Student 与九组训练实验

### 6.1 已实现入口与独立数据契约

`cue_student/` 已实现eligibility、prepare、固定holdout、data/加载、models、temporal、损失、train/evaluate/predict和输入观察日志。三路分别输出Text15、Audio17、Visual10个独立Cue分数；一组实验只处理对应模态，不使用其他模态预测该模态标签，不使用Emotion或description。九组是候选实验数，最终三路组合仍是42维，不拼成九组输出。

训练为各自独立的单进程单GPU，当前不支持DDP。Teacher证据时间/文本、label_mask不作为推理特征；语言缺失标志、音频有效帧和视频padding mask只由实际输入产生。全量训练读取原始dataset媒体，不依赖已删除的API输入副本。

### 6.2 Text：共享双语XLM-R，全编码器微调

- 编码器 `FacebookAI/xlm-roberta-base`，服务器资产为 `/ai/sjq/AffectGPT-sjq/AffectGPT/models/xlm-roberta-base`；固定revision `e73636d4f797dec63c3081bb6ed5c7b0bb3f2089`。
- 中文、英文分别经过同一个共享编码器，不拆成两条训练样本；保留两种语言的实际可用标志。缺失语言使用mask，不能以另一语言复制填充。
- max_length=128，overflow重叠32；如超长，确定性覆盖所有分块并按token重叠倒数加权，避免静默截断和重叠重复计数。每种语言得到768维表征，双语拼接并加入2维language_present，融合头为1538→256→15，GELU与dropout=0.1。
- 当前Text实验 `encoder_train=full`，**文本编码器没有冻结**；head_lr=1e-4，encoder_lr=2e-5。代码虽支持冻结选项，九组中没有另开的冻结Text实验。
- 旧全量31,327条源数据的英文缺失588条是原始总体统计，不直接替代当前release或训练角色的缺失率。

### 6.3 Audio：完整HuBERT与新增时序对照

编码器资产 `/ai/sjq/AffectGPT/AffectGPT/models/chinese-hubert-large`。完整读取原音频，转单声道16 kHz，并使用do_normalize=true的Wav2Vec2FeatureExtractor；不附转录、VAD、F0或其他数值声学特征，不截短、不自动分块、不启用冻结特征缓存。

HuBERT输出1024维上下文序列，本身已包含时间上下文；mean基线对有效特征帧做masked mean，再经1024→256→17分类头，未额外添加序列模块。

时序对照保留全部HuBERT特征帧：1024→256投影与LayerNorm，加入帧序号和相对秒数的正弦编码（两者各半），接2层pre-norm Transformer，4个attention head、FFN1024、dropout=0.1，最后masked mean与256→256→17分类头。不是只有视频才有额外时序模块。

音频时间基准为卷积窗口中心：步长320采样点（0.02秒）、感受野400采样点，首帧中心199.5/16000秒；相对首中心的坐标为0、0.02……，无额外下采样。日志保存有效特征帧数和时间几何。

冻结组HuBERT保持eval且不更新；全量组编码器参与反向传播。预处理保持apply_spec_augment=false；正式全量训练的HuBERT LayerDrop=0.1可能随机跳过层，不能把单步未激活理解为该层冻结。未使用的masked_spec_embed也不要求每步产生梯度。

### 6.4 Visual：全时段2FPS与实际PTS时序对照

编码器资产 `/ai/sjq/AffectGPT/AffectGPT/models/clip-vit-large-patch14`，使用CLIPVisionModelWithProjection的768维image_embeds，只读取视频，不用音轨。

原始视频在完整时段确定性2FPS采样并保留首、末可解码帧及实际PTS；letterbox至224×224保持完整画面，再执行CLIP归一化，当前不使用center crop。每次前向最多8帧只是编码分块，不是每视频只取8帧；所有选中帧均进入聚合，不裁掉末段。

mean基线为有效帧masked mean与768→256→10分类头。temporal对照为768→256投影、同第6.3节的2层Transformer和256→256→10分类头；位置同时使用帧序号与实际相对PTS，先以float64减去时间原点再转float32，padding不参与注意力或池化。Teacher近似时间戳不作为帧级真值。

当前2FPS/完整画面可能遗漏短暂细节，须由人工审计评估。4FPS、区域特征、GRU和声学辅助量尚未纳入当前九组；已有attention/Top-k选项也不是本轮运行配置。

### 6.5 九组实验、GPU与学习率

| 实验名 | 物理GPU | 编码器训练 | 聚合/附加时序 | head_lr | encoder_lr |
|---|---:|---|---|---:|---:|
| text | 0 | XLM-R全量 | 双语融合 | 1e-4 | 2e-5 |
| audio | 0 | HuBERT冻结 | mean | 1e-3 | 不更新 |
| audio_temporal | 0 | HuBERT冻结 | Transformer＋mean | 1e-3 | 不更新 |
| visual | 1 | CLIP冻结 | mean | 1e-3 | 不更新 |
| visual_temporal | 1 | CLIP冻结 | Transformer＋mean | 1e-4 | 不更新 |
| audio_full | 0 | HuBERT全量 | mean | 1e-3 | 1e-5 |
| audio_temporal_full | 0 | HuBERT全量 | Transformer＋mean | 1e-3 | 1e-5 |
| visual_full | 0 | CLIP全量 | mean | 1e-3 | 1e-5 |
| visual_temporal_full | 1 | CLIP全量 | Transformer＋mean | 1e-4 | 1e-5 |

前五组归属 `strict_all_modalities_20261020_163131`，后四组归属 `full_finetune_20261020_170308`。以job下各自 `configs/<run>.json` 为实际运行参数，不用后来改动的通用模板替代运行快照。冻结编码器虽留有encoder_lr配置值，但无编码器参数更新。

Audio的mean与temporal学习率一致；Visual temporal的head_lr实际低于Visual mean，因此该对照包含架构及head学习率差异，不能把最终差异全部归因于时序模块。比较全量/冻结时使用对应同结构配对；GPU共享程度不同也影响墙钟时间，不能直接当模型固有速度结论。当前每配置只有seed42单次运行，尚无多种子稳定性证据。

### 6.6 当前训练、验证与保存参数

| 模态/组别 | microbatch上限 | grad_accum | 动态时长预算 | epoch上限 | patience | workers | 计划optimizer步上限 |
|---|---:|---:|---|---:|---:|---:|---:|
| Text | 4 | 8 | 无 | 10 | 3 | 0 | 8,650 |
| Audio四组 | 2 | 16 | 每batch时长和20秒 | 20 | 4 | 2 | 每组17,500 |
| Visual四组 | 2 | 16 | 每batch时长和15秒 | 20 | 4 | 4 | 每组17,879 |

`max_batch_units`按样本时长之和控制打包，不是特征帧数；超预算的长单样本仍完整进入。累积样本数上限约32，动态batch可能更小，不能固定称每步32条。步数上限来自实际训练manifest，早停会提前结束。

共同设置：seed42、BF16 autocast、AdamW、weight_decay=0.01（bias和一维参数不衰减）、warmup_fraction=0.1后线性衰减、clip_grad_norm=1、dropout=0.1。九组均使用普通masked BCE，未开启weighted_bce或focal。

每200个完整optimizer step原子保存 `last.pt`；每epoch验证并更新 `last.pt`/`best.pt`。best优先比较验证集固定可评估Cue集合上的macro AP，同分取更低masked BCE；无可评估Cue时退回负masked BCE。patience按epoch计算，不根据人工300条选择checkpoint。epoch事件/计数与训练step不同，不以日志零起始epoch编号直接当已完成轮数。

### 6.7 九组共享的输入速率优化

九组均使用同一已优化加载链路：有序spawn DataLoader，音频每组2个worker、视频每组4个worker，文本实测worker0更快；workers>0时prefetch_factor=2，pin_memory=true，GPU拷贝non_blocking=true。worker的Torch/BLAS为1线程，主进程cpu_threads=8，视频decode_threads=1。

当前persistent_workers=false，训练/验证及新epoch重建加载器，仍有启动开销。冻结组也每轮完整编码，没有启用离线冻结特征缓存；当前未扩大microbatch或裁剪媒体来提速。不能把“已做加载优化”等同于消除CPU解码、I/O、验证和共享GPU竞争。

### 6.8 新增全量微调的显存与启动保护

后四组均启用gradient_checkpointing，以重算换激活显存；每进程 `cuda_memory_fraction=0.20`，在80 GiB GPU上约16 GiB的PyTorch allocator预算。原五组未设置这一进程上限。allocator预算不覆盖所有驱动/CUDA上下文等分配，也不保证nvidia-smi总占用恰好为该值。

新增组由 `cue_student/jobs/full_finetune_20261020_170308/memory_limited_train.py` 在构造模型前应用预算，并以main guard阻止spawn CPU worker重复进入训练或初始化CUDA。直接运行普通train入口不会自动应用此配置项，恢复新增组仍必须经过该包装入口。

启动前依次以真实长训练样本完成四组有界前向、反向及AdamW更新，检查编码器与分类头的实际参数更新和有限梯度；预检峰值reserved约6.2–7.1 GiB，不代表整个训练过程的峰值保证。启动器按“当前占用＋计划新增预算＋8 GiB余量”检查两卡，再逐组等待首个optimizer更新，未停止原五组。

冻结编码器无需保存完整反向图/优化器状态，小microbatch、BF16和编码分块也降低显存；全量训练通常增加反向计算及状态，checkpointing又增加重算。因此显存占用小本身不等于训练快或慢。耗时还取决于有效序列长度、额外时序模块、加载与解码、GPU算力利用率及九组共享；须用近期完整step和验证耗时评估。

## 7. 标签、损失函数与阈值的当前实现

### 7.1 普通masked BCE与整样本筛选分工

九组均使用普通masked BCEWithLogits。positive和negative共同监督，分别表示Cue存在与观察充分但不存在，不表示积极/消极情绪。

| 原始状态 | y | label_mask | 当前用途 |
|---|---:|---:|---|
| positive | 1 | 1 | 阳性监督 |
| negative | 0 | 1 | 阴性监督 |
| uncertain | 有限占位值 | 0 | 保留歧义原因，不参与BCE |
| unobservable | 有限占位值 | 0 | 保留不可观察原因，不当阴性 |
| unlabeled | 空 | 0 | 仅原始失败导出；该样本全部模态从当前release排除 |

第5节先按模态任务是否成功整样本筛选；只有已合格样本才逐Cue屏蔽uncertain/unobservable。部分Cue不可判定时，其余有效Cue仍训练；不能把这种局部mask误用成允许“某模态任务失败但其他模态训练”。

主损失沿用：

$$
\mathcal{L}=\frac{\sum_{i,k}m_{ik}\,\operatorname{BCEWithLogits}(z_{ik},y_{ik})}{\max(1,\sum_{i,k}m_{ik})}.
$$

BCE以float32计算，先用有限值替换无效目标，不能先算NaN再乘0。梯度累积的分母为整个累积组的有效Cue总数，不平均有效标签数不同的microbatch mean。全累积组无监督则跳过optimizer和scheduler并计数。当前单进程单GPU，不宣称已实现DDP全局分母或同步。

### 7.2 类别不平衡与噪声：已实现选项和当前运行分开

普通masked BCE是当前九组共同基线，保留全部有效正负监督。train-only加权BCE选项已经实现，但九份配置均未开启，实际pos_weight全1。其可选规则为每类只从pseudo_train的有效位置统计N+、N-，两者均非零时取 `min(20,max(1,sqrt(N-/N+)))`，缺乏任一类时登记支持不足并保持有限权重；训练manifest保存统计。加权分数不直接作为校准概率。

focal、强过采样、人工可靠性权重尚未纳入当前九组，不将多个策略同时叠加后归因于单一因素。全量原始稀有Cue计数与当前训练支持数不同，以当前release/support和各run的training_manifest为准，不能用含失败样本或保留角色的计数拟合权重。

Teacher自报confidence不当真实概率；不把uncertain设为y=0.5，不按证据文字长度猜权重。停顿/流泪与其他Cue统一保留API原始状态，无专用阳性门控。人工噪声策略若用于开发，使用独立开发角色，不能反复利用最终gold后仍称独立测试。

### 7.3 连续分数、当前0.5与未来人工校准

每类独立sigmoid，当前评估/推理使用固定0.5，明确为未校准工程阈值；无逐类人工阈值结果。训练使用正负监督，AMG未来仅选择部分阳性断言不意味着训练只用positive。低于阈值不是人工确认不存在，输入不可用也不是negative。

仅用pseudo-validation拟合的阈值须称Teacher一致性阈值。人工校准需在开发选择冻结后按第5.2节预登记交叉拟合，首选规则为开发折最大F1、同分取较高阈值；支持不足时保留连续分数和未校准说明。最终部署阈值与交叉拟合性能分开报告。九个目标数据集不参与阈值、Cue激活、checkpoint或预处理选择。

### 7.4 四状态保留与预测任务边界

当前三路分别学习15/17/10个独立存在性二分类，不是四状态分类器；uncertain/unobservable用于审计及覆盖分析，unlabeled是失败登记。接近0.5不代表学会uncertain，低分不代表unobservable。推理输入有效mask不使用Teacher label_mask。

可观察性辅助头、人物绑定与强定位均不是当前九组实现。若以后增设，需单独定义任务、训练和验证，不能默认作为屏蔽原始监督或推理阳性的门控。

## 8. 当前验证结果的含义与人工评估门槛

### 8.1 已实现的Teacher验证与待完成的人工评估

当前训练每epoch计算masked BCE、逐Cue正负support、Precision/Recall/F1和Average Precision（AP），保存连续预测、mask及样本ID；best以验证前固定的两类均有支持的Cue集合计算macro AP，不能为某个模型临时换集合。AP是当前PR性能实现，不混称另一种积分算法。固定0.5的F1仅为未校准参考。

这些指标是Student–Teacher一致性，不能称人工准确率。可选按组bootstrap工具已实现，默认200次；常规epoch验证并不自动产生正式人工置信区间。来源未知时即使有工程group_id，也须披露未建模相关性，不能称已完成可信来源聚类推断。

后续人工评估要求：

- Teacher–Human：盲审后报告四状态覆盖、Teacher可判定子集混淆矩阵，并登记Teacher在人工可判定样本上的uncertain/unobservable/失败，不隐藏拒判。
- Student–Human：以人工参考的可判定状态决定范围，不用Teacher mask二次过滤；报告输入缺失、无输出及逐Cue支持。
- 逐Cue报告Precision、Recall、F1、AP、正负支持、覆盖与区间；macro/micro仅作补充，不把不可评估类静默补零。
- 按语言缺失、时长、多人/遮挡/小脸、原始状态和稀有Cue分层；规则在源域预登记，不按目标性能修改。
- 人工300条按第4节披露299＋1修订及候选总体，稀有Cue定向诊断单独报告，不混成自然分布总体。

### 8.2 Cue激活和时序对照的证据

是否active/deferred需结合定义、人工双标一致性、Teacher–Human差异、独立正负支持、可观察覆盖、Student–Human稳定性和可复现性。大量negative造成的高accuracy、较低训练loss、单次seed或更高显存利用都不足以单独证明效果。

停顿/流泪继续普通监督，不附额外门控；高mask比例不自动表示deferred。若支持不足或人类表现不合格，可保留42维槽位并登记core_deferred。音频/视频时序及全量微调是否优于对应基线尚待训练与评估完成；比较时披露Visual的head_lr差异和GPU资源分配。

### 8.3 进入AMG前仍需冻结的内容

当前已冻结Teacher协议、工程release、角色与运行配置。正式AMG发布前还需完成并冻结选定的三路权重、人工参考与抽样总体、阈值版本及来源、active/deferred、输入与缓存版本、来源/近重复限制和独立评估结果。文件存在或训练启动不替代这些验收。

## 9. 后续 AMG 图构建的接口约定

区分CueType（本体类型）、CueAssertion（样本级预测/存在性断言）、局部证据位置（第一版可选审计属性）。第一版无人物绑定、无经过验证的强定位输出。

当前predict入口一次加载一个模态checkpoint，返回15/17/10维连续分数、输入有效性、本体/资产与架构信息，输入不可用时返回null分数及不可用标记。Teacher监督mask不传给推理器。

后续从九组中选定Text、Audio、Visual各一个checkpoint，再组装42维scores、本体顺序、阈值与active/deferred、modality_present、输入协议和checkpoint版本；三路组合及AMG图尚未接入。图中可按阈值选择positive断言，同时保留连续分数；未选中、不可用和明确不存在分开记录。

### 9.1 OOF建库与阈值交叉拟合是两项任务

- 第5/7节gold的5折主要用于阈值交叉拟合：不要求为每折重新训练一个Student，因为gold本身已排除出Student训练。
- 对Student训练过的源域样本进行OOF预测建Memory，则需额外训练折模型。建议在完成单次三路基线后，按来源组固定5个outer folds；每个样本仅由未用其所属组训练的checkpoint预测。
- 各outer训练部分内部再划分早停/阈值开发角色；不能用outer留出折选epoch或阈值后仍声称该折是严格独立预测。架构候选预冻结，登记原开发数据使用边界；最终gold始终不参与折模型训练/早停。
- 记录每折权重、成员、早停与阈值来源。OOF特征不能仅标成“最终Student”而隐藏生成模型；需要每模态约5套折训练，另有最终部署模型，费用与工期独立估算。
- OOF折模型与最终全量Student权重不同，Memory/Query虽共享本体、结构及预处理，分数分布仍可能不同；仅用源域开发数据比较尺度/阈值兼容性并登记。不得声称严格相同权重，不用目标标签修正。
- Teacher标签只作监督、审计与对照，不是默认Memory表示。若先用单次模型做原型，明确标注in-sample检索的乐观偏差，不能冒称OOF结果。

## 10. 已完成事项、后续顺序与发布门槛

当前已完成：

1. 冻结Teacher协议与42类本体，完成全量标注和技术补标，保留93,903成功/78失败的原始记录。
2. 实施任一模态失败整条排除，剔除72条；修订固定300条为299＋1，发布31,255条严格工程包。
3. 完成三路Student及音频/视频时序模块、监督mask与恢复检查、真实GPU集成验证和加载优化。
4. 原五组因数据策略变化从预训练重新训练；新增四组也从预训练开始。九组按GPU0六组/GPU1三组运行，未复用含失败样本的旧Student结果。
5. 按用户授权删除已作废的旧训练输出、旧发布物和相关测试产物；原始dataset、API响应、标签、队列和协议继续保留。

后续按以下顺序推进，均尚不能写成已完成结果：

1. 保持当前九组配置与数据指纹固定，完成训练并汇总各组best、Teacher验证指标、实际耗时和资源。时序、冻结/全量对照说明学习率与共享资源差异；单次seed结果不代表稳定优势。
2. 完成人工300条三模态盲标、60条双标与仲裁；独立诊断/稀有Cue补充单独报告。继续核验来源及近重复，披露当前抽样修订与独立性限制。
3. 冻结Student开发选择后做人工校准/阈值交叉拟合，评估逐Cue覆盖、支持数和active/deferred，保留42维槽位。
4. 从三路各选定checkpoint，验证15＋17＋10分数接口，再单独实施源域OOF折模型、Memory和AMG。九个目标域不得参与参数/阈值/策略选择。

当前已有严格工程release及正式全量数据训练checkpoint；这些仍为Teacher伪标签工程结果，并未完成独立人工性能或AMG发布验收。本次同步方案无需重启当前九组，不修改其代码、配置或训练进程。

## 11. 标注结束后的失败处理与读取方式

### 11.1 API调度与当前GPU用途

已结束的标注使用32并发、360 RPM、1,600,000 TPM客户端上限；这是历史执行配置，不等于平台吞吐保证。API推理在平台侧，服务器承担完整音视频准备、磁盘及网络；当前两张GPU用于九组Student训练，不决定API请求并发。重新调用相同目录时仍须使用单一调度进程及独占锁。

### 11.2 最终失败分类及训练处理

| 原因 | 模态任务数 | 当前状态 |
|---|---:|---|
| 平台内容审核拒绝 | 73 | 记录原始错误，不通过改写输入规避 |
| 平台认为视频过短 | 5 | 完整视频复验仍失败，不填充或循环延长 |
| 合计 | 78 | 涉及72条样本，整条不进入当前任何工程角色 |

首轮大小/解析失败已定向修复，不再把中途76项、74条样本或首轮345项作为当前失败数量。未成功模态在原始导出中为unlabeled/y空/mask=0；同样本其他模态的原始成功标签保留，但该sample_id整体不进入当前release。

### 11.3 后续补标的版本边界

当前没有待继续的普通标注队列。若以后有明确技术修复，才按失败类别定向重排；成功标签不重跑，不无限清零次数。网络/408/429/5xx或无效输出使用已有有限重试、退避和全局限速；余额/权限、连续失败和磁盘保护保持生效。不得无差别 `--include-permanent` 重排审核拒绝。

补标若使72条中的样本恢复三模态成功，不会自动修改已冻结release、holdout或正在运行的九组。需另行审计并建立新版本；若改变训练成员，checkpoint签名不兼容，不能当作当前运行无差别续训。

### 11.4 只读检查

在项目根目录执行以下命令只读取状态，不启动训练或API：

    cd /ai/sjq/AffectGPT-sjq
    /ai/sjq/miniconda3/envs/vllm/bin/python cue_annotation/annotate_full.py --status
    cat cue_student/jobs/latest_all_experiments.json
    cat cue_student/jobs/strict_all_modalities_20261020_163131/status.json
    cat cue_student/jobs/full_finetune_20261020_170308/status.json
    nvidia-smi

每组日志位于对应job的 `<run>.log`，每组原始事件位于 `cue_student/output/<job>/<run>/events.jsonl`。导出、重排或恢复属于有状态操作，不混在只读检查命令中；运行恢复约束见第17节。

### 11.5 凭据和服务器边界

历史标注曾经由代理/SSH隧道访问API，仅在再次执行该流程时才涉及该依赖。此次文档同步不启动隧道或标注，不处理新凭据；凭据不写入方案、脚本或日志。文档、代码、原始数据、训练缓存和产物均在服务器管理，静态统计以注明时间和总体为准。

## 12. 历史快照：00:40已成功Cue的分布与审计线索

以下是成功任务内当前已落盘的监督层，不包含失败/待处理位置；这是2026-10-20 00:40历史快照，当时计入流泪候选门控；该门控现已取消，当前状态见第14节。频繁停顿额外资格屏蔽从未应用，并已按用户要求取消该计划。它不是自然分布准确率，也不是人工参考标签。由于三个模态完成数略有不同，各行分母不同。

| 模态 | Cue位置数 | positive | negative | uncertain | unobservable | mask=0占比 |
|---|---:|---:|---:|---:|---:|---:|
| 文本 | 105,840 | 14,146 | 87,177 | 4,317 | 200 | 4.27% |
| 音频 | 119,935 | 15,422 | 69,346 | 11,062 | 24,105 | 29.32% |
| 视觉 | 69,760 | 14,468 | 49,269 | 5,157 | 866 | 8.63% |

| 历史复核项 | 当时mask=0比例 | 含义与下一步 |
|---|---:|---|
| `AUD_SPEECH_RATE_REL_SLOW` | 51.14% | 核验同一样本/说话者参照、有效语音与记录条件；不直接补负例 |
| `AUD_PITCH_LEVEL_REL_HIGH` | 66.72% | 核验同一样本/说话者参照、有效语音与记录条件；不直接补负例 |
| `AUD_PITCH_LEVEL_REL_LOW` | 62.96% | 核验同一样本/说话者参照、有效语音与记录条件；不直接补负例 |
| `AUD_VOCAL_INTENSITY_REL_HIGH` | 60.06% | 核验同一样本/说话者参照、有效语音与记录条件；不直接补负例 |
| `AUD_VOCAL_INTENSITY_REL_LOW` | 61.98% | 核验同一样本/说话者参照、有效语音与记录条件；不直接补负例 |
| `AUD_PAUSE_FREQUENT` | 55.65% | 另有短音频资格冲突，仅作审计诊断；当前保持原始标签 |

历史快照中`VIS_TEARING_PRESENT`的200条API阳性曾被屏蔽；目前已取消该处理，原始阳性与其他标签相同使用，当前全量计数见第14节。笑声、哭泣、成功结果、自身原因归因等稀有Cue须在全量结束后统计有效正例支持数，必要时另建与审计集隔离的训练复核集。上述高mask比例只是审计/可学性风险，不自动改变本体ID，也不凭这一部分数据直接判core_deferred。

## 13. 2026-10-20 首轮结束与技术失败补标

本节记录标注阶段的时间顺序及原始31,327条总体，不代表当前训练成员政策。原始成功记录保留；当前训练、验证、人工300条和诊断均按第5节排除全部72条含失败模态的样本。

首轮于06:31结束：成功93,636个模态任务，失败345个；三模态齐全30,988条样本，339条样本存在失败。失败包括完整视频超出Base64预算261项、平台内容审核拒绝72项、URL/文件解析错误7项（视觉6、音频1）、视频过短5项。大小超限发生在客户端准备阶段，未调用模型；不能靠原样重复提交解决。

技术修复使用[千问官方私有临时上传](https://platform.qianwenai.com/docs/api-reference/more/upload-file-get-temporary-url)：同一账号、同一`qwen3.8-omni-flash`模型取得上传策略，上传完整文件，通过`oss://`和`X-DashScope-OssResourceResolve: enable`调用原接口。实测单文件上限1024MB；私有临时文件48小时有效，缓存按47小时处理。上传凭证只保留在内存，不公开媒体，不改动模型、生成参数、Cue本体或冻结Prompt。传输修订及文件哈希登记于实际输入和响应元数据，原始冻结配置保留。

261个大小失败使用完整静音视频流复制；6个视频解析失败使用既有H.264 CRF18兼容转码，均保留时长、分辨率、FPS、客户端帧数。1个音频解析失败仍输入完整连续16kHz PCM16 WAV，仅改变上传传输方式。首个验证视频保留8.08秒、202帧，通过14,327,744字节完整文件上传成功。

文件上传单独限制4路，写入/连接超时120秒、响应读取300秒；模型请求仍保持32并发、360 RPM、160万TPM上限。曾有5个并发上传代理超时，已从断点恢复；上传网络错误可自动重试，不计为模型调用。19项离线测试通过。成功标签不重跑。

本次268个技术失败任务补标恢复267项，另1个上传成功后被平台内容审核拒绝。总成功任务为93,903项，剩余78项：73项内容审核拒绝、5项视频过短。已没有大小、解析或上传网络失败。审核拒绝不改写内容绕过；过短视频不填充、不循环延长；未解决项在原始导出中继续unlabeled/y空/mask=0，同样本其他模态的有效标签仅在原始记录中保留；当前release整条排除，后续人工补标或平台复核另立版本。

证据文件位于`cue_annotation/runs/mercaptionplus/`：`repair_manifest.json`保留原始345项失败及修复决定；`repair_actions.jsonl`记录定向重排；`transport_overrides.json`登记上传兼容项；`repair_summary.json`记录补标完成后的完整输入核验与最终队列统计。`labels.csv`、`failures.csv`须以本次导出完成的版本为准。人工语义质量审计仍未完成；频繁停顿按第14节保留原始标签，资格冲突仅作诊断，技术补标成功不代表已经满足训练发布验收。

补标后最终核验：三模态齐全31,255/31,327条样本（99.77%），72条样本尚有至少一个失败模态。成功补标的266个视觉文件和1个完整音频已逐项通过schema、输入范围与SHA256核验；音频样本`samplenew3_00091781`为完整4.609秒、73,744个16kHz采样点。正式`labels.csv`已重新导出，`failures.csv`与数据库78项一致，无pending/running。补标新增1,820,342 tokens；累计303,109,687 tokens（输入265,580,873、输出37,528,814），共94,361次模型HTTP尝试。上传网络失败未计入模型请求次数。详细证据见`repair_summary.json`。

后续短视频单次复验：按用户要求，将5个0.68–0.84秒完整静音视频改经官方私有临时文件URL各提交一次；SHA256、时长和画面保持原样，5项均再次返回HTTP400 / `The video file is too short`。因此仍保留视觉unlabeled/mask=0，不填充、不循环；原文本/音频有效标签只在原始记录中保留，失败样本不进入当前任何工程角色。证据见`short_video_retry.json`。模型HTTP尝试累计94,366次，成功/失败数量、完整样本数和本地记录token总量均未变化；失败清单已刷新。本次单次请求上限及既有保护的20项离线测试通过。


## 14. 统一采用大模型原始标签

本节计数均为原始31,327条标注总体，保留了失败样本的其他成功模态，仅说明原始标签映射；当前严格release的四状态总数见第0.2节，训练统计按其角色单独计算。

按用户指令“将902条候选都标注为流泪”，并按后续澄清“不用特殊处理，直接改为和原始大模型标注其他标签一样”，已将这902条流泪标签逐项与成功API响应对齐，恢复原始positive及原始evidence_note。当前annotations不附流泪专用quality_review或label_overrides，执行器也不再将流泪阳性改成uncertain；原始模型响应、模型与Prompt均不变。与其他Cue采用相同映射：positive→y=1/mask=1，negative→y=0/mask=1，uncertain/unobservable→y空/mask=0。

原始31,327个流泪Cue位置为：positive902、negative25,518、uncertain1,236、unobservable3,602、unlabeled69。902条均已校验原始响应一致性和CSV的positive/y=1/mask=1，全量CSV仍为1,315,734行。前端显示普通流泪阳性，不再显示待确认或用户批量指定标记。未调用API；20项执行器与上传离线测试通过。核验记录见`runs/mercaptionplus/tearing_label_restoration.json`。


按用户后续要求，停顿也统一为普通大模型标签。已核对31,322条成功音频记录中的62,644个停顿标签，与成功API原始响应及CSV的state、evidence_note和y/mask全部一致；没有需要恢复的覆盖标签，未改写annotations或labels.csv。长停顿positive 3,181条，频繁停顿positive 197条；历史11,395条资格冲突仍保持negative 11,381条和positive 14条，均mask=1。原始uncertain/unobservable和5个音频失败位置仍按统一规则mask=0，不强行改成正负。核验记录为`cue_annotation/reports/pause_label_verification_20261020.json`；诊断清单不参与标签后处理。

## 15. API派生副本清理与目录整理

用户已明确同意“调整引用，再删除副本，然后刚刚整理的清单也可以按你说的做”。原始数据位于`dataset/mer2025-dataset/{audio,video}`；逐项核实62,654个原始文件均存在后，清理全量`runs/mercaptionplus/media/audio/`和`media/video/`，共62,654个API派生副本、61,886,077,531字节（约57.6 GiB）。前端从原始dataset按访问生成完整静音播放缓存；补标按需恢复原记录的完整音视频输入，并验证源文件及历史输入哈希。历史`submitted_*_path`与哈希保留提交事实，不当作当前文件存在性保证。

标注JSON、原始API响应、输入元数据、全量CSV、SQLite队列、失败及质量核验记录保留。原始dataset不在删除范围；旧30条输入及已有浏览缓存因仍有使用而保留。已完成标签不重跑，不触发收费API。

测试移入`cue_annotation/tests/`，运行说明移入`cue_annotation/docs/FULL_RUN.md`，历史预算、清理记录和中途统计移入`cue_annotation/reports/history/`；README按当前状态重写。23项离线测试覆盖执行器、上传、完整输入恢复和源文件变更保护。完整整理及最终结果核验见`cue_annotation/reports/cleanup_20261020.json`。

## 16. 实施验证、版本切换与旧产物处置

当前五组job下 `unit_tests.log` 记录64项测试通过，`integration_report.json`记录严格数据范围内五组真实GPU集成与音频时序恢复验证；`data_audit.json`记录角色隔离与失败样本交集检查。该证据属于计算与数据契约验证，不替代人工Cue语义质量或九组最终指标。

新增全量job下 `preflight_summary.json`、各组 `<run>.preflight.json` 记录四组有界真实GPU预检；`launch_verified.json` 记录九组PID、配置、GPU绑定及严格数据审计，`final_audit.log`记录最终启动核验。新增组预检包含编码器参数实际更新，不能只用requires_grad或进程存在作为已训练的证据。

按先前用户授权，含失败样本旧版本的训练checkpoint/结果、旧release和相关任务/测试产物已清理，当前release及九组产物保留。旧历史文档中出现的旧运行路径不再作为现有证据或续训入口。原始标注、完整源数据、冻结Prompt/本体和失败记录不在清理范围。

当前可复核索引（相对项目根目录）：

| 路径 | 内容 |
|---|---|
| `cue_student/reports/strict_all_modalities_20261020.md`及同名JSON | 严格排除、300条修订与五组重启报告 |
| `cue_student/reports/full_finetune_20261020.md`及同名JSON | 新增四组全量微调报告 |
| `cue_student/jobs/strict_all_modalities_20261020_163131/cleanup_report.json` | 旧产物清理结果 |
| 两个当前job下的配置、status及启动核验文件 | 真实运行参数与启动结果 |
| `cue_student/artifacts/release_strict_all_modalities_20261020_163131/manifest.json` | 当前数据身份、划分、支持数、限制 |
| `cue_student/splits/holdout300/manifest.json` | 当前固定名单、替换来源及指纹 |

## 17. 当前训练维护、恢复与时间估计

### 17.1 恢复条件

运行签名绑定完整配置、代码、release/holdout、编码器资产和Cue顺序。只有相同数据/配置/代码的 `last.pt` 才能在原output目录恢复，保留模型、AdamW、调度器、进度、早停和CPU/CUDA随机数状态。不能将旧含失败样本的checkpoint、不同架构或不同release作为本轮resume。

恢复操作应先确认原进程已经停止，避免重复占GPU或触发runner.lock。原五组使用普通 `python -m cue_student.train`；新增四组必须使用当前job内 `memory_limited_train.py`，携带原command各参数并增加 `--resume <原output>/last.pt`，继续使用原物理GPU UUID映射、原配置、release和output。所有进程内部只看见一张卡，所以内部 `--device cuda:0` 不等于全部在物理GPU0。

`SIGUSR1`/`SIGTERM`支持在完整梯度累积边界保存last并安全停止；若维护需要停止，等待 `graceful_stop` 与进程退出后再恢复。不能用SIGKILL代替正常保存流程。本次仅更新方案，不发送停止信号。

### 17.2 当前九组工期估计方法

用每组近期 `event=train` 的完整optimizer step时间差估算训练速度，并单独计入epoch验证、每200步checkpoint写盘及加载器启动；若直接使用包含这些开销的长期墙钟均速，不再次重复计入。动态时长打包、Transformer序列长度和共享GPU会使短窗口波动，记录窗口和时间。

剩余上限按training_manifest的 `total_planned_steps − global_step` 计算，结合patience和验证趋势给区间；训练结束也不等于人工评估、OOF或AMG完成。新增四组后GPU0六组/GPU1三组共享，旧五组独占阶段或新增前的ETA均已过期；其他实验结束释放资源后再次估计。低显存占用不直接用于推断完成时间。


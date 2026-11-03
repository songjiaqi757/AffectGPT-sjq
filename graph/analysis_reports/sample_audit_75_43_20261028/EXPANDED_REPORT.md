# 扩展166例：新增发现与改进优先级

项目/分析均位于服务器 /ai/sjq/AffectGPT-sjq。本轮新增166条数据集内案例，与上轮72例无相同(dataset,name)，累计238例；新增36条片段各4帧，共144个解码位置全部成功，累计检查52条案例的视频帧。
所有读取、CPU计算、抽帧和产物保存在服务器；未修改预测、评分、数据、训练/推理代码，未启动GPU任务。视频审阅是抽帧，未完整听看音视频，未人工重标真值。

## 1. 选样与对照

每集围绕六类各最多3条：50权重持续零/错、持续满/对、赢家错而其他权重经常对、赢家对而其他权重经常错、相对起点改善、相对起点恶化；另给四个离散集各补2条neutral。组内固定SHA256排序并分散参考类别/极性强度，排除上轮72例。部分层可选样本不足，不补造样本。
新例按dataset/name计数，不视为媒体去重的独立总体。选样为探索性定向阅读，不能用各机制案例数推算总体占比。

每例对照：
1. 当前75.4334%逐集赢家及自身原始起点；
2. 原始face七权重中该数据集最佳；
3. 上轮长证据25权重中该数据集最佳；
4. MER2023/SIMS/OV同名样本补base35、graph40的A-G。
原始/长证据赢家同样来自测试选优，且跨权重/协议并非单因素消融。新增诊断不替换历史官方成绩。

|数据集|新增例数|
|---|---:|
|MER2023|20|
|MER2024|20|
|MELD|20|
|IEMOCAPFour|20|
|CMUMOSI|18|
|CMUMOSEI|18|
|SIMS|18|
|SIMSv2|18|
|OVMERDPlus|14|


## 2. 应修正上轮“失败样本”的解释

原报告的1,754条“赢家零/错”是评分定义，不能统一解释成1,754条语义理解失败。

### OV sample_00000680：语义有重叠，计分却完全零
参考 shy/relaxed/positive/grateful/happy；字幕“Last night, I forgot to properly thank you.”
赢家 gratitude/apology/friendliness/positivity；四个词在五个轮上都无映射，诊断F=0。
逐词探针：
- gratitude：五轮均空；
- grateful：五轮均有映射；
- appreciation：五轮均有映射；
- positivity：五轮均空；positive：四轮有映射。
抽帧中人物低头再抬头、有笑意变化，这不支持把“表达感谢”一律视为完全错误，羞怯等细节仍需语气和上下文确认。

跨实验：graph40 A为gratitude/apology，质量0；base35 E/G仅多了appreciation，诊断F达到0.8。分数大变包含词汇覆盖因素，不能全归于心理理解提高。

### OV samplenew3_00019671：有分数不等于理解更细
参考 joy/humor/happiness/emphasis；赢家 calm/rational。
calm在wheel1/2/4分别映射到happy/happy/joy，逐样本诊断F=0.6；rational没有映射。
这来自轮级粗化，不等于模型明确识别了幽默/喜悦。

扫描全部532条OV赢家：56条有效参考零重叠，其中11条预测无任何轮映射；9条是neutral/空抽取，另外2条为上述gratitude等，以及humor/sarcasm/jest。不能把11条都称为词典错误，更不能靠扩词典替代模型训练。
完整探针和词频见expanded_mapping_audit.json。保持官方历史协议；如建立补充语义映射诊断，应对所有模型冻结同一规则、统一处理，并单列报告。

## 3. 情绪主体与事件时间：比“正负词”更细的缺口

### MELD test_dia12_utt6，GT sadness，50次全零
台词：“I've never seen either of you … as happy as you've been since you've got together.”
赢家happy/excited/enthusiastic；原始集最佳与长证据最佳也都偏正向。
画面有多人，后半聚焦当前说话者；台词中的happy明确描述“你们两个人”，不直接证明说话者当前开心。实际Cue含正情绪/正评价，level3候选joy/appreciated/hopeful。
这是“被谈论者情绪”和“当前说话者情绪”应分开的实例；说话者确切sad仍以参考为准，抽帧不是重标。

### IEMOCAP Ses05M_script02_2_F015，GT sad，50次全零
“Dancing barefoot in the sand, drinking champagne out of the bottle.”
赢家excited/joyful/content/satisfied；长证据最佳仍joy/satisfaction/freedom/happiness。
实际音频Cue是slow/low intensity/low variability/long pause/falling/flat，视觉head lowered，图检索到ashamed/depressed/pity，但当前level2不展示Emotion。
模型可能把回忆/谈论的愉快场景当成此刻情绪。至少在此例，简单增加同类正负词或把责任全放在错误Emotion候选上都不充分。

### SIMS video_0027_0023，GT -1
“这回娘也给你煮了新的饺子，还是20个。”
九集赢家warm/comforting/encouraging；抽帧显示人物低头，不能仅凭“包饺子”断定温暖。
base35 A无图为sadness/longing/nostalgia，B/C/G等也判对；graph40 A无图已变warm/caring/comforting，B-G均未恢复。
原始该集最佳40和长证据该集最佳也能给sadness等。它是权重依赖的判断变化案例，提示单换图提示未必修复。不同权重训练历史不一致，不能单由此把变化归因于图训练。

建议新增结构化证据：情绪主体、事件发生时间、台词描述情绪、当前人物情绪。每项带短语/时间依据与可判定标记，不把参考标签泄露到推理提示。

## 4. 说话行为、立场和感受需要分开

### MOSI cXypl4FnoZo_11，GT +1.4，50次全错
“I would say … go and see it … if you … weren't sure if it would be worth seeing.”
赢家neutral；原始最佳uncertain/hesitant，长证据最佳neutral/hesitant/uncertain。
“你原本不确定”是受建议者状态；“我建议你去看”体现说话者的推荐立场。回答情绪词不能稳定保留整体推荐信息。

### MOSEI 208592_7，GT -1
“The only good thing about this movie are the songs and the dances.”
起点neutral/slightly negative，赢家positive/neutral。Cue仅选TXT_EVALUATION_POSITIVE和intensifier等，未保留only对评价范围的限制。
这里不是一般“是否有否定词”问题；需要表示“仅局部优点，整体贬评”的结构。

### SIMS video_0029_0007，GT +0.2，50次全错
“以后我再也没有机会干这种事了，这牛我得吹一辈子。”
赢家disappointment/despair；原始/长证据最佳及A-G均没修复。英文“I have to blow it all my life”没有表达“吹牛/夸耀”的习惯意义。
画面是消防员自拍场景；情境、危急唤醒、夸耀行为、整体情绪可能不同向，尚需完整音频审阅。不能把“再没机会”直接定为绝望，也不能仅凭参考正向忽视可能混合情绪。

建议给源域/新dev增加：推荐/抱怨/安抚/夸耀/挖苦等行为、被评价对象、范围限定、整体立场与当前感受的区分。与简单42维Cue同权重配对验证，再决定是否训练。

## 5. 有些强证据已经存在，输出仍会加入相反情绪

### MOSI jUzDDGyPkXU_20，GT -2.2
“Everything they say … sounds so … stupid.”
赢家anger/frustration/sadness/happiness/excitement，最终positive；50次49对，只有赢家这次错。
起点、原始该集最佳、长证据该集最佳都给明确负情绪。Cue已经有负情绪词和负评价；实际level2也没有展示正向Emotion候选。
这是新增不支持次要词的直接例子，不能只归为图给错候选。

### MOSI yDtzw_Y-7RU_23，GT +2.2
“I enjoyed myself … you might as well.”
赢家sarcastic/provocative/ironic，最终negative；50次49对1错。原始/长证据最佳均正确。
媒体帧不足以确认有无反讽；应审计为何该权重引入强解释。

### MOSI tmZoasNr4rU_12，GT -2.2，50次均对
“I just couldn't find it funny.”
赢家unable to find humor/dissatisfaction/disappointment；它能正确处理某些否定幽默表达。应拿这种正确样本与相近失败样本做源域对比，保护已有能力，而不是把所有否定模板重新训练成一套硬规则。

建议保留开放次要情绪的表达能力，同时要求依据和主次；在独立源域/dev计算新增纠错、伤害和不支持次要词，加入经审核正确答案的保持约束。不要简单对所有任务强制Top1。

## 6. 微笑/笑声并不充分区分情绪

### OV samplenew3_00098820，GT embarrassment/hesitation，50次全零
台词Good good good；赢家positive/affirmative/excited，Cue含smile/laughter，level3候选joy/hopeful/content。
四帧确实可见笑容，也有视线和头部变化，但这些稀疏帧不能确认是愉悦还是尴尬性微笑。base35/graph40 A-G均零，说明该例不只是某一个提示组合的问题。

### IEMOCAP Ses05F_script01_3_F015，GT happy，50次全零
“I'll never forgive you. Why did you wait so long? …”
赢家anger/frustration/disappointment；Cue同时有负词及smile/laughter，抽帧可见表情变化。
这与上例构成反方向材料：正向参考未必有正向措辞，笑容也不能独立定类。需要语气、时间与前文，而不是规定“有笑就positive”或“有负词就negative”。

建议建立“笑容+尴尬/难过/愉悦”和“负措辞+玩笑/抱怨”等来源分离的对比组。逐条确认笑声属于当前人物还是背景，不假定多个相关Cue就是独立支持。

## 7. 输入质量出现直接可核验的问题

### OV samplenew3_00055533
模型输入字幕仅Red；原视频中间帧清楚显示“黄色的 应该可以”。这是文字内容缺失/错配的直接证据，具体在原始字幕、ASR还是翻译哪一级产生，尚未追溯。
GT serious/deep in thought/slightly nervous；赢家excited/joyful/enthusiastic，50权重以及原始/长证据最佳、A-G都零。
参考中的serious仅在一个轮映射，其他词部分不映射，另有计分覆盖限制。错误不能只归到图。

### 翻译拒答混入Cue输入
MOSEI BRSyH6yfDLk_3的中文字段是“该输入含有不适当的言辞，无法提供翻译。”，英文subtitle仍保留原台词。
影响首先是读取双语的Text Cue分支，不能说AffectGPT英文主提示也读到了拒答。九集按已写明模式扫描仅找到这一条，不能扩成普遍污染结论。
空subtitle：MER2023 18、MER2024 3、OV 22；空字幕可以是真正无台词，不自动判坏数据。

建议先给新dev加输入质量标记，追溯少数明确错配案例；同权重对照核验文本前后变化。原测试输入不在本轮改写。缺失时允许文本分支缺省，仍保留媒体判断。

## 8. 正确样本和neutral对照补充了什么

稳定正确例：
- MER2024 samplenew_00029298，“你原来是应龙夜神”，50次满surprise。
- IEMOCAP Ses05M_impro06_M008，“he's gone now … can't believe it”，50次满sad。
- MELD test_dia216_utt1，“I can't believe you're getting married”，50次满joy。
- OV sample_00002078，明确指责对方先有错，50次诊断F=1。
- OV sample_00000338，手机和钱包在包里，50次诊断F=1，焦虑判断稳定。
相似的“can't believe”可因事件和当前人物表现落在不同情绪；应学习情境区分，不写死词触发。

四个离散集共有1,929条neutral参考，既定HIT不计入。赢家对其中1,794条至少产生某轮可映射类别；这不是官方错误计数，calm等也会映射到happy。
新增8个neutral对照常被回答为担忧/希望/焦虑等。例如MER2023“想让妹妹读完高中考大学”，参考neutral却输出concern/hope/worry/anxiety。
建议补全类别人工诊断和“是否有足够情绪依据”审核，避免仅通过HIT得分理解系统能力；不把上述1,794直接称为人工确认的过度归因。

## 9. 跨集重复和证据限制

SIMS与SIMSv2中的video_0037_0005、video_0045_0040音频SHA256分别完全相同；不把它们当两条独立媒体证据。对应输入/字幕和赢家不同，可作为稳定性对照。
所有“全错”“全对”仍是当前参考和缓存协议定义。跨实验差异不分离训练预算、权重、评分随机性。抽帧能发现文字错配和部分表情/人物变化，不能代替完整音视频盲审。

## 10. 更新后的执行优先级

1. 先给错误诊断分型：媒体/文本错配、情绪主体或时态错误、真实类别混淆、无依据次要词、词汇映射/抽取问题、需复核的参考。先确定能修什么。
2. 在新的独立dev上，优先做核验文本、主体/时态/评价范围等最小证据的同权重配对验证；当前材料不支持继续只改Appraisal措辞。
3. 增加整体立场与人物情绪分开的监督；用清楚的正确样本及相近失败类型做源域对比，并保护正确答案。
4. 微笑、反讽、回忆和多人片段再做完整音视频/上下文审计。缺少这些信息时，不强选Appraisal状态或Emotion候选。
5. 保留官方评分，另设冻结、统一的语义与映射诊断；修字典后只涨分不能宣称模型感知增强。

## 11. 产物

- expanded_cases.json、EXPANDED_CASES.md：166新例的参考、字幕、回答、Cue、实际门控、50权重稳定性、原始/长证据赢家、适用的A-G。
- expanded_selection.json：选样协议、分层数量与旧例重叠0。
- expanded_media_1..3.jpg/.json：36例144帧位置。
- expanded_mapping.py / expanded_mapping_audit.json：OV全量映射覆盖与探针。
- expanded_controls.py / expanded_historical_sources.json：九集历史对照谱系。
- expanded_input_qc.json：输入字段扫描。
- expanded_neutral_audit.json：neutral参考输出诊断。
- EXPANDED_REPORT.md：本报告。

所有文件仅在服务器本目录。

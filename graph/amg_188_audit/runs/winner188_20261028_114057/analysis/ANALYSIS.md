# 第一轮：原188类图九集赢家证据干预结果分析

结论：保留Appraisal作为下一轮候选；优先检查Emotion候选的展示与支持判定；现阶段不重建188类图，也不宣布新统一最优。Cue+Appraisal本轮均值最高，但仅比原完整提示高0.1192个百分点，优势没有在逐集区间中得到确认。更深的主体、时态、评价范围、字幕与输出任务问题仍然存在。

## 1. 完整性与比较口径
本轮于北京时间2026-10-28 15:12:57完成。54个job manifest全部complete、54个score齐全；76,794条逻辑预测，52,718个唯一生成输入，21,466个唯一原始回答。54项主指标从预测重新计算均一致，全部原始回答文件hash与score记录匹配。同prompt/checkpoint/seed/media的回答及抽取一致，未发现例外。
status.json残留53/54推理和部分judge进度计数，是最后一次进度快照未同步；不能据此判为缺少一个实验。evaluation_barrier和全部job/score/最终复核证明已完成。

固定各集历史赢家权重（7个不同checkpoint），比较同一权重下的提示字段；并非一个统一checkpoint在九集的结果。A是关闭在线附加证据，不是重新训练的无图模型，不能把A-P解释为图训练的因果效果。
评分保留原函数/词典/提示和采样温度，但本轮新增按内容固定seed及全局抽取缓存。应与本轮P=75.4293%配对比较；历史拼接75.4334%只作锚点。
九集均值混合HIT/WAF/F_s，只延续原汇总口径；决定采用还要看逐任务指标、伤害与案例。

## 2. 六条件结果
A：无附加证据；B：Cue；C：Cue+Appraisal；D：Cue+Emotion；E：Cue+Appraisal+Emotion、无路径；P：原完整提示、含路径。

|条件|九集均值%|对本轮P差值pp|
|---|---:|---:|
|A|75.0239|-0.4054|
|B|74.5279|-0.9015|
|C|75.5485|+0.1192|
|D|74.3943|-1.0350|
|E|75.2496|-0.1797|
|P|75.4293|+0.0000|

|数据集|A无证据|B Cue|C Cue+App|D Cue+Emo|E无路径|P原完整|C-P pp|
|---|---:|---:|---:|---:|---:|---:|---:|
|MER2023|77.566|76.448|78.768|76.568|78.826|78.823|-0.055|
|MER2024|79.837|78.691|79.744|78.385|79.259|79.808|-0.064|
|MELD|59.676|59.197|58.803|58.974|58.568|58.526|+0.277|
|IEMOCAPFour|61.540|60.070|60.980|60.303|60.093|60.163|+0.817|
|CMUMOSI|82.857|81.661|82.413|82.257|82.263|82.864|-0.450|
|CMUMOSEI|80.106|80.707|80.294|80.725|80.077|80.192|+0.102|
|SIMS|86.409|86.674|89.941|86.162|89.691|89.691|+0.250|
|SIMSv2|85.966|85.518|86.069|84.428|85.963|86.071|-0.001|
|OVMERDPlus|61.258|61.784|62.925|61.747|62.506|62.727|+0.198|

### 2.1 Appraisal有条件增量，不能一刀切删除
C-B平均+1.0206pp，7/9集上升；去掉SIMS后仍+0.7399pp。另一背景E-D平均+0.8553pp，6/9集上升。因此这一prompt块的增量不只来自单个数据集，也不限于没有Emotion时。
最清楚的是SIMS：86.674%→89.941%，14条纠正、1条伤害；按可由名称识别的来源视频聚类，2000次配对bootstrap区间为[+1.283,+5.516]pp。
MER2023的C-B为+2.320pp，样本iid区间[+0.369,+4.409]pp；来源组未确认，证据弱于真实聚类/独立验证。
MELD、MOSEI则分别-0.395、-0.413pp，Appraisal并非通用开关。

这确认的是当前训练权重对该提示块的反应；不能证明每个Appraisal状态都准确。实际提示经常同时列congruent/incongruent、self/other、certain/uncertain，可能包含格式、长度或训练输入分布因素。下一轮应加入格式及长度尽量匹配、状态打乱的内容对照，区分语义信息与提示结构收益。

### 2.2 Emotion候选是优先检查对象，但不是全部错误来源
E-C平均-0.2989pp，8/9集下降。只有4777/12799条真正展示Emotion并改变提示，另8022条未展示时条件相同，回答与抽取也完全一致。全量均值是对实际干预效应的稀释。
IEMOCAP：60.980%→60.093%，27条HIT方向改善、42条变差；对话聚类区间[-1.584,-0.148]pp。本区间未做多重比较调整，也不代表跨说话者泛化。
D-B平均-0.1336pp，4集升5集降，不能说Emotion在任意背景必然有害。并且有些候选方向正确，输出仍退化，不能只以“候选极性是否正确”制定硬门控。

### 2.3 路径整体未显示有害，不能因为追求简短就全删
P-E平均+0.1797pp，6升2降1平；MOSI+0.601，MER2024+0.549pp。逐集区间仍覆盖0，暂不构成稳定收益证明，但不支持“路径普遍是噪声”。
本轮没有Cue+Appraisal+路径且不含Emotion的条件，无法知道删除Emotion后路径是否仍有帮助。C-P同时去掉Emotion和路径，不是单独Emotion因果差值。

### 2.4 无证据在部分集更好，不能全面关闭图
A-P：MELD+1.150pp、IEMOCAP+1.377pp；SIMS却-3.282pp、OV-1.469pp、MER2023-1.257pp。去掉SIMS后A-P均值仅-0.0459pp，说明整体差距部分由SIMS驱动。
MELD和IEMOCAP值得在开发集检查在线证据关闭分支；不应依测试结果直接逐集切换后宣称泛化提升。

### 2.5 C的0.119pp优势需要重复确认
C-P有5集正、4集负；所有9集的配对bootstrap95%区间都覆盖0。例如IEMOCAP+0.817pp区间[-0.169,+1.747]，MOSI-0.450pp区间[-1.916,+0.863]。
因此75.5485%是研究候选，不是已经确认的新最好模型。若在这次测试上再逐集选六条件最大值，会拼到75.8226%，这又增加一次测试后选优，只能作探索性上限。

## 3. 案例如何解释收益和退化

### 3.1 Appraisal能纠正部分表面情绪与立场混淆
SIMS video_0015_0035，参考-0.6：“就算这本日记是真的，你也不能指证我是凶手。”
B：cool/calm/confident/defense/rebuttal，最终positive；
C：defensive/frustrated/angry，最终negative。
与之前“自信/镇定不自动等于正向”的判断一致。

SIMS video_0012_0016，参考+1：“你别难过，馆陶会一直陪着你的。”
B：comfort/encouragement/solitude/distress，最终negative；
C：comfort/encouragement/sympathy，最终positive。
这里减少了把被安慰者的难过混入说话者整体状态的回答，符合安抚行为与当前立场区分的方向，但完整人物情绪仍需音视频审核。

反例SIMS video_0035_0011，参考+1：“白居易，他可狂得很。”
B excited/crazy/positive正确，C加入frustration/sarcasm/mockery后变negative。Appraisal会伤害已有正确回答。

MER2023 sample_00000436，参考sad：“他说我很烦的时候，我就很想哭。”
B annoyance/frustration/dissatisfaction/distress；C frustrated/annoyed/sad。确实补回sad。但相邻样本sample_00000929在没有明确输出anger时HIT仍升，说明部分数值改善来自轮映射，不宜都解释为类别理解变好。

### 3.2 Emotion影响输出，未必表现为直接照抄候选
MOSI jUzDDGyPkXU_6，参考-1.6，批评电影不及《第九区》《黑鹰坠落》。
C disappointment/dissatisfaction/anger/frustration→negative；
E在正确负向候选disappointed/depressed/despair之外，回答反而加入excitement/enthusiasm，最终positive。
候选是负向也不保证回答负向；问题还包括不支持的次要情绪和整体极性裁判对混合词的处理。

IEMOCAP Ses05F_impro03_M001，参考happy。
C excited/happy/enthusiastic，E展示joy/hopeful/content后回答excited/enthusiastic/possibly teasing，HIT从1降0.4。不是候选方向完全错，而是明确类别词丢失、轮映射改变。
因此首要评估应同时看新增词支持度、主次和稳定性，不能只检查候选是否包含参考标签。

SIMSv2 aqgy4_0021_00000，参考-0.6：“我真是随便一说，可你找了那么多借口我才开始好奇的。”
C curious/frustrated/annoyed/teasing/mocking→negative；
E curious/amused/slightly annoyed→positive。候选同时有anger/disappointed/joy，输出被改变但没有新增可核实的情境信息。

### 3.3 不能把路径的单例加分等同于语义修复
MOSI dq3Nf_lMPnE_14，参考-1.8：“除非你的孩子非常想看，否则我会建议你等DVD出来再看。”
C中有mocking→negative；E把它变humorous→positive；P又改teasing→negative。路径内容却为brows raised→joy/hopeful。
这说明分数有变化，但未显式学会“建议等DVD=较负推荐”的评价结构。路径可能改变词汇采样，也可能有局部帮助；不能用这条加分证明路径推理正确。
MER2024 sample_00003004，C和P为tense/anxious，E为warning/caution，路径又把担忧相关输出恢复，也显示不同字段交互。

### 3.4 之前的核心难例仍在
以下样本六条件均为既有指标零/错，不能靠本轮字段删除解决：
- MELD test_dia12_utt6：描述“你们在一起后很幸福”，参考sadness，所有条件仍admiration/happiness等；情绪主体问题未修复。
- IEMOCAP Ses05M_script02_2_F015：沙滩跳舞、喝香槟的回忆，参考sad，六条件均偏happy/excited；事件时间与当前人物情绪未区分。
- MOSI cXypl4FnoZo_11：建议别人去看电影，参考+1.4，六条件全neutral；人物情绪输出缺少整体推荐立场。
- MOSEI 208592_7：only good thing is songs and dances，参考-1，六条件全positive/neutral；评价范围未修复。
- SIMS video_0027_0023：包饺子片段，参考-1，六条件全warm/comforting/encouraging。
- SIMS video_0029_0007：吹牛的习语被译为blow it，参考+0.2，六条件全disappointment/despair。
- OV samplenew3_00055533：字幕Red与既有抽帧发现的“黄色的 应该可以”错配，六条件均零。
- OV sample_00000680：感谢片段六条件均gratitude/apology/friendliness/positivity，既有词典覆盖问题仍使分数为零；不等同语义完全错误。
- OV samplenew3_00098820：笑容/Good good good，参考embarrassment/hesitation，六条件仍偏positive。

新增定向旧例中，九集各3条persistent_error共27条，本轮六条件仍全零/错。不是总体比例估计，但它们对“删掉Emotion就能解决核心错误”给出明确反例。
按当前混合诊断定义，P共有1757条零/错，其中1299条（73.93%）六条件都没有恢复；这包含真实理解、参考/输入问题、抽取与映射问题，不能当作1299条人工确认语义失败。

## 4. 类别与评分诊断
IEMOCAP anger：A HIT61.059%、P54.000%，差7.059pp；happy则A72.896%、P73.484%。无证据分支的总体好处不是各类一致，重点检查怒与其他负类的边界。
MELD disgust在六条件仅10.784%~14.216% HIT，没有靠字段删减修复；fear和surprise也需单列。参考类别没有映射的样本（包括neutral）不在HIT中有效计分，不能把HIT当全类别准确率。

原极性评分去除参考0后使用prediction>0二分类；预测neutral也归非正。SIMS C-B官方纠正14/伤害1，其中2条纠正以neutral结束；另一类negative→neutral的退化被二分类掩盖。
补充将预测neutral对非零参考计错：C-B纠正14/伤害5，准确率84.536%→86.856%，方向仍正，但不是“几乎无伤害”。补充指标不替换官方WAF。
此外MOSI fvVhgmXxadc_9仅给positive/appreciative/metaphorical增加analogy，官方最终极性就改变；这不支持直接说人物情绪识别变好。混合词回答及裁判的不稳定性需要专门审计。
当前固定内容缓存保证相同输入同抽取/极性，但不消除不同措辞的裁判敏感性，也不代替多种子复核。

## 5. 具体下一步
1. 暂时保留188类图及原始基线，C作为首要提示候选；不全面删除Appraisal，不直接按测试集决定数据集分支，不把75.55%宣布为统一新最好。
2. 先补齐开发材料并做来源隔离。现1253条官方val候选在配置和已知实际根目录下的音频/人脸/视频，已在本次分析重新检查；统计见ADDITIONAL_DIAGNOSTICS.json。SIMS/SIMSv2还存在来源视频与测试重叠，不能只补文件就视为独立开发集。
3. 开发集上做小规模单因素验证：原P与C；Cue+Appraisal+路径但不展示Emotion（本轮缺失单元）；原Appraisal与格式/长度匹配的状态打乱对照；主体/时态/评价对象/否定和only范围的有依据语义证据。按阶段开展，不同时改字幕、映射、训练目标。
4. Emotion优先比较不展示与有局部依据、允许缺省的展示方式。不要用现测试真值定阈值；输出主次和新增不支持词需审核。仅凭候选方向正确不足以放行。
5. 对输入确错的字幕先追溯原始转写/翻译链，做独立配对实验；官方原测试不在本报告中改写。映射修正只作统一冻结补充诊断。
6. 若语义证据在隔离开发集、多生成种子、固定研究权重上显示净增益，再做同起点、同数据流、同训练步数的小规模训练对照：普通续训、人物情绪与整体评价极性分离监督、再加入验证有效语义证据。训练需要保护已有正确样本。

## 6. 证据边界与产物
本轮只分析既有预测/抽取/指标与之前审阅的材料，没有新增完整音视频盲审、没有重标参考、没有运行第二轮或训练。置信区间是2000次配对bootstrap；按名称可识别的视频/对话聚类，MER/OV来源不明时用样本iid；不覆盖生成、裁判、训练多种子不确定性，不做多重比较显著性承诺。
分析均在服务器上运行与保存。未修改原始预测、评分、图或训练代码。

- ANALYSIS.md：本报告。
- STATISTICS.md、summary.json：所有54项和主要对照/区间/提示改变样本数。
- all_samples.jsonl：12799条完整六条件回答与诊断。
- CASE_COMPARISONS.md、case_reading_pool.json：175个对照条目，覆盖114条dataset/name案例。
- class_effects.json：四个离散集逐参考类HIT/M。
- prior_case_effects.json：前两轮定向案例在本轮的响应。
- ADDITIONAL_DIAGNOSTICS.json：极性neutral单列、持续零/错、原文件hash及开发媒体当前复核。

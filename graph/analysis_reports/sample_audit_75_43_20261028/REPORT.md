# 75.4334% 九集逐集赢家：样本复核与提升建议

日期：2026-10-28。服务器项目：/ai/sjq/AffectGPT-sjq。
所有读取、计算、抽帧和文件写入均在服务器执行，没有把项目或媒体文件下载到本地。未启动训练、模型推理或新评分；未修改原始代码、权重、预测或评分缓存。

## 核心建议

优先改进“当前说话者对当前事件/对象的判断”，并保护原本正确的输出。提升重点是：否定与转折的作用范围、整体评价极性与自信/唤醒的区分、sad/anger/disgust等近邻类别、证据的人物/时间归属，以及不被支持的次要情绪。

简单软化提示和删除Emotion已在后续A-G实验中检验，未形成统一增益。Appraisal若继续研究，应先验证状态内容是否有当前样本依据，再研究图关系。以下区分直接观测与待验证机制；错误以原参考和评分口径为准，不表示完成了人工重标。

## 1. 范围和诊断口径

- 目标运行：amg_d_multistart10/runs/d_multistart10_20261025_160152，实际为旧188类统计图。
- 九集各从50权重选官方主指标最高者，均值75.4334%；不是一个单一权重。
- 全部50权重逐样本对齐，共639,950条预测、12,799条数据集内记录。不同数据集间可能媒体重叠，未据此称为独立视频数。
- 每集从“起点/赢家均零、均满、改善、恶化”各选2条，共72条。组内固定SHA256排序并分散参考类别；不是误差类型随机抽样，不能把案例频次当总体占比。
- 查看16条视频各四个位置的帧；第一张拼图有一条末帧未解码。未完整听看所有音视频，没有对参考标签重标。
- HIT诊断质量：各有效轮的平均命中。满HIT可同时包含错误次要词；当前neutral参考不进入HIT。
- OV诊断质量：逐样本、逐有效轮P/R调和后的均值，不是官方F_s；不将这些样本差相加解释官方F变化。532条中1条没有任何有效参考轮，诊断排除。
- 极性任务沿既定实现排除GT=0，以positive/非positive二分，neutral/mixed/未知预测落在非positive。因此“判对”可能只是计分边界正确。
- 50权重属于相关训练轨迹；50次错误不表示任何新模型都不可能修复。
- 九个赢家的npz哈希及主指标已独立复核，误差<1e-12，详见verification.json。

## 2. 九集赢家与持续错误

“赢家零”指HIT/OV所有有效轮零重叠，或极性判错；“50次均零”是这50个权重一直如此。各任务口径不同，不混算统一错误率。

|数据集|起点→保存epoch|主指标%|总记录|诊断有效|赢家零|50次均零|
|---|---|---:|---:|---:|---:|---:|
|MER2023|30→39|79.0085|411|323|36|5|
|MER2024|45→54|79.8081|1169|968|94|6|
|MELD|30→39|58.5257|2610|1354|341|58|
|IEMOCAPFour|30→39|60.1167|1241|857|228|37|
|CMUMOSI|50→57|82.8635|686|656|113|24|
|CMUMOSEI|50→55|80.3151|4659|3634|718|159|
|SIMS|35→41|89.4411|457|388|41|9|
|SIMSv2|45→49|86.0707|1034|911|127|23|
|OVMERDPlus|35→40|62.7512|532|531|56|5|

有效诊断记录合计9,622；赢家零1,754；50次均零326。很多赢家错误曾被其他权重救回，但不能逐条读取测试参考选答案来声称可实现这些收益。

## 3. 否定、转折和评价对象：最值得优先处理的语义问题

**CMUMOSI yvsjCA6Y5Fc_8，GT=+0.4。**
“…my expectations were lowered… but I really didn't hate it”。
赢家disappointed/negative/frustrated；50权重39次negative、11次neutral，均未识别正类。
Cue有负词、负评价、否定、转折，图候选为disappointed/anger/despair。二值Cue保留了“有否定”，没有保留否定的对象与转折后结论。画面中的眉眼、口型变化也不能直接等同于对电影的负评价。

**CMUMOSEI 53609_12，GT=-0.3333。**
“…it was going to be bad and it wasn't as bad as I thought…”。
赢家relieved/positive；50次26对、24错。
相对预期改善和整体仍负可以同时存在。不能用固定规则“not bad就正向”修复上一条。

**CMUMOSEI 222247_8，GT=-2。**
“…surprising… really didn't care anymore”。
起点release/indifference/surprise，赢家改为calm/unconcerned/acceptance/let-go/positivity，最后由对变错。
低唤醒、冷漠、接受、正向不是同一维度。

建议在源数据/新dev中增加评价对象、被否定谓词、转折前后评价、整体立场的监督，保留短语依据；将“情绪”和“整体评价极性”作为不同任务验证。不要只扩充情绪候选。

## 4. 自信与决心不能充当正向情绪

**SIMSv2 aqgy5_0013_00019，GT=-1。**
“我警告你，别拿我的容忍，当成你们不要脸的资本。”
起点anger/frustration/dissatisfaction判对，赢家anger/frustration/confidence/determination最终判positive；50次47对3错。
抽帧可见警告、指向对方的动作。该例支持检查“自信/能动性如何混入极性”，不能只把它归为少听了一个负词。

**SIMS video_0008_0011，GT=-0.2。**
中文“花多少钱我都可以的啦”，模型字幕“I can do whatever it takes.”。
赢家positive/determined/willing/capable；50权重全错，后续两权重A-G的14组同样全错。
翻译删去了钱这个对象并强化意志/能力表达；需核验翻译、上下文、媒体融合及参考，不能单凭本例判原标签有错。

低强度极性更难：
|数据集|0<abs(GT)≤0.5，错/总数|错误率|更强极性对照|
|---|---:|---:|---|
|CMUMOSI|30/76|39.47%|abs(GT)>1：45/431=10.44%|
|CMUMOSEI|290/902|32.15%|abs(GT)>1：150/1419=10.57%|
|SIMS|22/110|20.00%|abs(GT)>0.5：19/278=6.83%|
|SIMSv2|80/339|23.60%|abs(GT)>0.5：47/572=8.22%|

以上是GT分析分箱，不是推理可用特征。强负警告例也说明不能只管弱极性。
建议明确学习整体valence，将confidence、determination、arousal作为独立属性；先在独立dev配对检验核验后的原中文/当前翻译。

## 5. 相近类别：需要具体判别依据

- MELD disgust HIT14.22%；68条中56条全轮零，16条50次一直零。
- IEMOCAP sad HIT40.41%；245条中110条全轮零，24条50次一直零。
- MER2023 sad61.20%、surprise41.67%，worried88.77%，能力并不均衡。

**MELD test_dia57_utt5，GT=disgust。**
“But you will always be the guy who peed on me.”
起点/赢家均anger/dissatisfaction，50次全错。Cue包含laughter/smile，实际level3候选joy/disappointed/hopeful。
视频包含多人、镜头变化及片尾字幕。需要核查笑声/笑容归属、愉悦与厌恶的区别；没有听音频标声源，不能断言laughter一定是观众。

**IEMOCAP Ses05F_script03_2_M041，GT=anger。**
“Very music- amusing indeed.”，赢家appreciation/joy，50次全错，Cue也偏正向。
反讽是值得审核的机制，文字和稀疏帧尚不足以确认这条就是反讽。

**MER2023 sample_00000714，GT=sad。**
关于检讨进档案，赢家nervous/concerned/uneasy/worried/anxious，50次47次零。
它识别了负性，但没有区分参考sad与焦虑/担忧。

建议建立sad–worry、anger–disgust、surprise–anxiety、反讽–字面赞美的源域/新dev对比组，标出可区分的语句、语气、面部依据。多标签仍允许共存，但训练主次及不支持的次要情绪，验收同时看HIT/M和类召回。

## 6. 上游证据的人物、时间和原文对齐

代码直接显示：Audio读取完整片段并混合声道；Visual Cue对原video整帧2fps、224尺寸采样；AffectGPT生成端读取face_npy与audio。两个视觉分支观察对象未必一致。来源：cue_student/data.py、amg_inference/model.py。

抽帧中MELD有多人；MER2024 samplenew_00040546最后镜头切换到另一人；部分IEMOCAP人物占画面较小。这支持做speaker/crop/time审计，尚不支持宣布这些问题已解释总体错误。
MER2024 samplenew_00011679字幕“何处？葛？寻？机密，远岭。”不通顺，需核验ASR；GT=sad，赢家tense/anxiety/fear，50次41零。

建议先审核一批独立多人物/切镜材料，配对比较目标人物轨迹、原文和有效说话区间；小规模正向后再扩大。不要直接对全部数据重新预处理并假定有收益。

## 7. 正确样本：保护已有能力

- MER2023 sample_00003944：“他到底在哪里”，GT worried，50次满HIT。
- MER2024 samplenew_00040546：“你想替那几只走狗出头”，GT angry，50次满HIT；赢家anger/frustration。
- CMUMOSI cXypl4FnoZo_29：“I didn't like Peter”，50次极性全对。简单明确否定已有能力，不能概括为所有否定不会处理。
- CMUMOSI zhpQhgha_KU_35：“more positive review… very good”，50次全对。
- OV sample_00000476：“怎么还不回来”，GT anxiety/worry，赢家concern/anxiety，诊断F1；实际level3候选disappointed/anger/bewildered。能拒绝错误候选是一项应保护的能力，候选采纳率不是越高越好。
- IEMOCAP Ses05F_impro05_F018：买票后行李丢失的抱怨，起点/赢家均anger/frustration。具体损失与责任清楚时已有良好判断。

正确还需要区分“真精确”和“命中”：
- MER2023 sample_00003805，GT angry，“你走吧”。赢家增加frustrated/angry，却仍有supportive/encouraging/understanding；HIT从0变1，不等于排他判断精确。
- MER2024 samplenew_00017770，GT sad，赢家把tranquility/contentment/sadness/nostalgia/fear/anxiety/stress都列出；命中中包含扩词因素。
- SIMSv2 video_0040_0046，GT=-0.2，赢家objective/neutral，抽取[]，按非positive算对。不能据此称其理解了负面态度。
- OV sample_00000927，GT excited/joyful/happy，电话画面中可见笑意变化；赢家附加urgent/anxious等，诊断F0.6667→0.5133。开放词任务应控制无依据次要词。

## 8. 其他实验约束了哪些改进方向

固定十类图graph40权重的A-G消融：

|条件|MER HIT|SIMS WAF|OV F_s|
|---|---:|---:|---:|
|B Cue-only|75.453|84.765|59.554|
|E Cue+平铺Appraisal+Emotion|74.281|82.994|60.476|
|G Cue+软Appraisal，无Emotion|75.526|83.017|60.714|

G在OV相对B有局部信号；SIMS删除Emotion后没恢复。base35 G-B三个主指标也没提高。软表达和删Emotion不足以成为通用修复。

同名样本进一步说明：
- sample_00003175，GT happy，“我就不会了”，九集50次全零，base35/graph40 A-G也全零。它需要回到媒体、语气、语境与参考审计。
- sample_00003805，base35 A无证据满HIT、B/C/E/G零；graph40 A-G均满。提示和权重存在相互作用。
- SIMS video_0025_0018，graph40 B对、C/E错、G对。单例软表达有帮助，但整体G-B仍-1.748，不能用好例代替总体结果。
- OV sample_00001097，GT curious，九集赢家anger/dissatisfaction/tension/anxiety、零；base35 B出现curious，E/G诊断F0.6667。证据能救部分个案，仍需净增量。
A-G是十类图、不同权重历史；不能把跨实验个案变化当成188→10类的单因素效果。

各极性赢家相对自身起点的纠错/伤害：
|数据集|纠正|新增错误|净多正确|
|---|---:|---:|---:|
|CMUMOSI|58|28|30|
|CMUMOSEI|274|229|45|
|SIMS|20|9|11|
|SIMSv2|47|30|17|

MOSEI纠错大部分被新增错误抵消。应在经过验证的源域正确样本上增加保持约束/蒸馏，并审核源答案，监测原易样本伤害。

50权重缓存等权多数投票，平票非positive：
|数据集|逐集赢家WAF|多数投票WAF|
|---|---:|---:|
|CMUMOSI|82.864|82.727|
|CMUMOSEI|80.315|80.101|
|SIMS|89.441|88.227|
|SIMSv2|86.071|86.838|

只有SIMSv2超过赢家。复用现有judge缓存且未统一重评分，这只是诊断；“别的权重曾答对”不等于实用集成就能提取全部收益。

## 9. Appraisal内容应如何改

sample_00003805实际关联相对支持：
goal incongruent0.9598/congruent0.0402；uncertain0.9607/certain0.0393；low coping0.8983/high0.1017。
提示平铺后强弱消失。这些数值是关联支持，不是状态概率，也不能证明Top1真实。

G仍平均约10.5个状态，经常将二态维度写全；前次CPU条件概率/严格门控已无明确收益。建议新诊断：
1. 对穷举全部状态的维度预先指定删除消融，允许缺省；
2. 将当前样本可观察性、状态可靠性与统计支持分开；
3. 比较直接多模态/上下文Appraisal预测+validity，与Cue经图重建；
4. 只有超越Cue-only且可复验时保留Appraisal，OV可作研究线索。
直接Appraisal预测也需有效覆盖和Teacher质量审计，不预设换监督就一定改善。

## 10. 可执行路线

### 先做独立开发材料和小规模配对推理
保留预先选定强原始权重（原始40；九集统一基线还应保留原始30）和当前最佳单权重45→54。统一比较，不临时各测试集换赢家。
在新建、未用于这些测试选优的dev上：
- 当前字幕 vs 核验后原文/翻译；
- 无证据 vs Cue-only vs 带评价对象/否定范围/转折结论的最小证据；
- 多人物/切镜子集的人物归属核验。
固定权重、样本随机流、评分，只改变待检验因素；不带测试真值。
原始40已有历史MER75.9198/SIMS88.1624/OV61.2276；与A-G严格配对仍需相同推理条件。

### 再做最小训练对照
固定同起点、同数据流、预算、优化器恢复：
- T0 普通无图继续训练；
- T1 T0+明确整体极性任务，与情绪生成分开；
- T2 T1+验证过的对象/否定/说话者Cue；
- T3 仅在证据显示增量后加validity Appraisal。
旧ovlabel词伪标签和推理不用的辅助头，不等于已经验证T1。新监督应审核。
源域构建相近类别与语义反转对比组，并用经过审核的正确源答案做保持约束。72测试案例用于定义误差类型，不回灌后在原测试声称泛化。
可以预注册较小学习率候选如2e-6与1e-5同预算比较，但当前没有证据说明只改学习率就能解决语义缺口。

### 采用标准
净纠错为正，伤害受控；单列disgust、sad及低强度极性；HIT/M与OV P/R共同报告；多个可行种子与视频/说话者聚类不确定性；固定单模型或dev定义路由后再验九集。
只有OV的Appraisal有效时可保留任务分支，不要求全任务统一使用。不能按测试真值逐条路由。

## 11. 评分误差单列，不替代模型改进

MELD赢家有2例原回答明确含surprised却被抽取删去：test_dia133_utt8、test_dia169_utt0。原回答均excited/surprised/happy，openset只余excited/happy；规模不足以解释其他大量错误。
MOSEI赢家385条正类错误中192条最终judge为neutral。它可反映输出valence不足或评分解释，不能全当感知错。
SIMSv2 aqgy5_0014_00032，起点sadness/appreciation/gratitude判对，赢家gratitude/appreciation/sadness判错，语义集合近似。
保留历史官方分数，另对唯一回答/抽取按内容缓存做一致性诊断；改变评分协议需全对照一致处理并另标结果。

## 12. 产物与来源

本目录：
- audit.py/common.py，statistics.json，九份*_all_samples.jsonl：全50权重对齐。
- extend.py，cross_experiment_statistics.json：A-G交叉对照及补充诊断。
- selected_cases.json / CASES.md：72例字幕、参考、起点/赢家、实际门控、Cue/Appraisal和后续回答。
- media_review_1.jpg / media_review_2.jpg：服务器抽帧。
- verify.py / verification.json：九赢家哈希与主指标复核。

主要来源：
amg_d_multistart10/runs/d_multistart10_20261025_160152/{scores,jobs,plan.json}；
每个score.raw_path及openset/sentiment缓存，包含BCD与D_continue溯源复用；
amg_inference/runs/graph_225_20261022_174537/{inputs,cache}；
amg_prompt_ablation/runs/prompt_ablation_20261027_215553；
amg_prompt_ablation_g/runs/g_soft_appraisal_20261028_002141；
analysis_reports/G_soft_appraisal_detailed_20261028.md、nine_dataset_reanalysis_20261027.md。

复现：项目根目录，CUDA_VISIBLE_DEVICES=''、PYTHONDONTWRITEBYTECODE=1、OPENBLAS_NUM_THREADS=1，用/ai/sjq/miniconda3/envs/vllm/bin/python -B依次执行audit.py、extend.py、verify.py。
audit.py重建案例，extend.py补A-G；本次额外Cue/Appraisal字段从原目标缓存原值补入，不改变预测。

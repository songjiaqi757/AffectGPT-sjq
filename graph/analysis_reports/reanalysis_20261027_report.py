from graph_paths import Path as _GraphPath
import json,pathlib,statistics,math,hashlib
ROOT=_GraphPath('/ai/sjq/AffectGPT-sjq/graph');P=ROOT/'analysis_reports'
def read(n):return json.loads((P/n).read_text())
s=read('reanalysis_20261027_stats.json');a=read('reanalysis_20261027_predictions.json');h=read('reanalysis_20261027_human.json');j=read('reanalysis_20261027_judge_consistency.json')
def clean(v):
 if isinstance(v,float) and not math.isfinite(v):return None
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
 if isinstance(v,list):return [clean(x) for x in v]
 return v
(P/'reanalysis_20261027_predictions.json').write_text(json.dumps(clean(a),ensure_ascii=False,indent=2,allow_nan=False))
lines=['# 九数据集完整评测复盘：2026-10-27',
'',
'项目：服务器 /ai/sjq/AffectGPT-sjq。分析全程在服务器执行，未下载项目、数据或结果到本地。只新增 analysis_reports/reanalysis_20261027* 分析文件；未改训练、推理、评分代码、数据、权重或人工标注库，未启动GPU任务。',
'',
'## 结论',
'',
'本轮有局部提升，但没有得到稳定、累积的整体改善。50个权重九集主指标平均72.5584%，相对各自五个原始起点平均只提高0.3500个百分点。最佳单一权重为45→54，九集均值74.0173%，上一轮长证据方案最佳单一权重35→40为74.0563%；本轮低0.0390个百分点。九集分别挑最优拼出的75.4334%不对应一个可部署权重。',
'',
'证据优先指向：原188类图及其Appraisal表达的问题仍在；Teacher Cue含噪且没有独立目标域校准；辅助极性目标与实际生成评分链不一致；纠错被新增错误抵消；评分链自身存在对完全相同答案的极性翻转。继续增加同类训练和扫描checkpoint不能分别解决这些问题。',
'',
'## 1. 本轮究竟跑了什么',
'',
'- 运行：amg_d_multistart10/runs/d_multistart10_20261025_160152。',
'- 原始30/35/40/45/50起点各续训10个名义epoch，共50权重×9数据集=450项，639,950条样本预测。40个权重新训练，35起点10个权重与其中30项评分按溯源复用。',
'- 实际图release为75d45e203722ce060829e0db17ce7348f24ef44c024f1e99ff310f050194a420，即旧188情绪类图。不是十类重建图，也不是10月26日CPU修复方案。',
'- 当前D：graph-only五折OOF、50%训练图呈现、固定gate、512-token证据上限、最多2条展示路径、极性辅助权重0.1；推理不dropout。',
'- 原监督仍为MERCaptionPlus description / ovlabel随机50/50；batch3，5000steps/epoch，恒定lr1e-5；新极性头基于原ovlabel的Qwen2.5伪标签。推理不加载该分类头。',
'- 单分支十个名义epoch是50,000steps、150,000样本呈现，约4.88遍30,755个源样本。四个新分支均使用相同seed42，读取的样本顺序SHA256相同；这些权重是相关训练轨迹，不是50次独立多种子实验。',
'- 35分支为既有5+5轮，41轮重建过loader；其余四分支连续10轮。不能把所有分支当完全相同的连续训练历史。',
'',
'## 2. 不只看最好值',
'',
'单位：百分数；差值：百分点。原始最佳为face七权重最好，上一轮为长证据25权重最好；候选数量不同，最好值比较有选择偏差。平均配对差为本轮50权重各自减去其原始起点；提高数只是轨迹计数，不能当独立试验成功率。',
'',
'|数据集|原始最佳|上一轮最佳|本轮最佳|本轮平均配对差|提高权重/50|',
'|---|---:|---:|---:|---:|---:|']
for d,r in s['datasets'].items():lines.append(f"|{d}|{r['original_best']:.2f}|{r['long_best']:.2f}|{r['current_best']:.2f}|{r['paired_base_mean']:+.3f}|{r['improved']}|")
lines+=['',
'本轮前四个离散任务平均配对+0.765，后五个极性/开放词汇任务平均仅+0.018。MOSEI的峰值80.32遮盖了平均-0.289和仅13/50个权重改善；OVMERDPlus平均-0.475、仅16/50改善。IEMOCAPFour即使本轮50次挑选，最高60.12仍低于原始61.52。',
'',
'与上一轮长证据方案按同原始起点、同新增第1–5轮匹配，本轮225项平均低0.284个百分点；MER2023 -1.155、IEMOCAP -1.009、OV -0.506、SIMS +0.858。这里同时改变提示、门控、OOF、辅助任务等，因此不是某一单因素的因果效果。',
'',
'|原始起点|起点九集均值|本轮十权重均值|均值变化|本轮最高|',
'|---|---:|---:|---:|---:|']
for b,r in s['base_summaries'].items():lines.append(f"|{b}|{r['original_mean']:.3f}|{r['mean']:.3f}|{r['mean']-r['original_mean']:+.3f}|{r['best']:.3f}|")
lines+=['',
'收益主要来自较弱的35/50起点；原始30/40/45起点的十轮平均均退化。它更像源任务继续适配后部分恢复较弱权重，不能证明图带来了普遍可迁移增益。',
'',
'## 3. 原图与Appraisal表达的缺口没有消失',
'',
'之前的可复核CPU诊断（cpu_four_checks_20261026.md）已经指出：188类图中90类没有可用统计入边；NPMI是关联强度，不是当前样本状态概率；goal relevance的Top1对源Teacher有效参考一致性仅25.28%；14,241个位置输出两个状态，其中3,321个第二状态支持小于第一状态10%。',
'',
'本轮policy.py仍把每维display_candidates直接串成文字，省略强弱分数；只要维度有通过的证据，就可能展示相互竞争的多个状态。emotion gate主要看第一候选间隔和支持者，再一起放行Top3。失败多数回到level2，仍展示Cue和Appraisal，不等于完整回退到原模型。',
'',
'本轮目标样本提示实测：',
'',
'|数据集|样本数|仅Cue+Appraisal(level2)|含Emotion(level3)|平均Appraisal状态数|',
'|---|---:|---:|---:|---:|']
for d,r in a['target_prompt'].items():lines.append(f"|{d}|{r['n']}|{r['levels'].get('2',0)}|{r['levels'].get('3',0)}|{r['totals'].get('appraisals_displayed',0)/r['n']:.2f}|")
lines+=['',
'六个Appraisal维度，平均却写入约10个状态，意味着经常把多个竞争假设交给生成器。全局Emotion置信不足并不会自动移除不可靠Appraisal。来源问题与表达损失仍在；50%训练dropout不能修正有图分支的错误假设。',
'',
'四个新分支各150,000次样本呈现：level0=75,173，level1=39，level2=49,268，level3=25,520。情绪候选只在约17.01%的全部训练呈现中可见；模型主要仍优化原生成任务，并非每次都获得可靠图推理监督。',
'',
'10月26日条件概率/先验校正/逐维门控的CPU修复也不能直接作为答案：十类图源Teacher检索F1从C0的58.094降到C1的56.256、C2的50.536；仅候选门控57.872，没有明确样本F1收益。应保留负结果，避免把未验证修复当已解决。',
'',
'## 4. 新增人工证据：Teacher的不同模态质量不一致',
'',
'以人工库只读快照计算，当前50条submitted，均为positive_confirmation_v1、teacher-visible辅助审阅。使用工作台自身positive_scoring.py的正集合口径；未被人工确认的Teacher positive按集合FP，未把留空写为negative。单标注者、未完成500条，不能当盲审或总体准确率。',
'',
'|来源|Teacher正标签数|人工确认匹配|precision|recall|F1|',
'|---|---:|---:|---:|---:|---:|']
for k,r in h['groups'].items():lines.append(f"|{k}|{r['teacher_positive']}|{r['tp']}|{100*r['precision']:.2f}|{100*r['recall']:.2f}|{100*r['f1']:.2f}|")
lines+=['',
'音频Cue有37个Teacher positive未被人工确认，视觉34个、文本29个。Teacher→Student→图→生成器每一级都继承部分上游误差；Student对Teacher的AP很高也不自动等于对人的准确。',
'',
'但不能据此把所有问题都归为Appraisal Teacher差：这50条Appraisal集合F1为88.48，goal relevance集合F1为98.18，反而比旧图检索goal relevance的一致性强很多。两组样本不同，不能相减当因果差值；它提示“原标注本身”和“Cue经图重建状态”需要分开检查。Appraisal中expectedness F1=56.00、agency precision=60.00，维度间也不应共用一个置信标准。',
'',
'## 5. 极性辅助为什么没有稳定变成WAF收益',
'',
'辅助头已验证对LoRA和head有非零梯度，不是没有训练。四个新分支的极性损失大致从首轮0.256–0.280降到末轮0.041–0.044；但没有独立验证头准确率，不能把低训练CE当泛化证据。',
'',
'辅助标签来自源ovlabel语义，而最终目标来自目标视频sentiment；30688条有效标签中negative19228、positive10306、neutral1154，且全部伪标签、没有人工核验。训练是不加权三分类CE。',
'',
'推理却不用这个三分类头，仍先生成多个开放情绪词，再由另一个Qwen抽取词，再转positive/negative/neutral。约束隐藏表示不保证多情绪生成和最终极性一致，尤其混合情绪、反讽、平静的正情绪。',
'',
'评分实现还删除真值为0的样本，以pred>0判断positive；neutral和mixed/未知输出都进入非正一侧。因而三分类训练目标、开放词生成目标和最终二分类WAF并不相同。这里是原评测协议，本分析没有修改。',
'',
'最佳单权重45→54的极性纠错/伤害：',
'',
'|数据集|原始WAF|当前WAF|纠正|新增错误|',
'|---|---:|---:|---:|---:|']
for d in ['CMUMOSI','CMUMOSEI','SIMS','SIMSv2']:
 r=a['single_comparisons'][d];lines.append(f"|{d}|{r['original']:.2f}|{r['current']:.2f}|{r['corrected']}|{r['harmed']}|")
lines+=['',
'MOSEI原45→续54的positive recall为79.60%，negative recall77.70%；正类错误466条。举例AQ4Pktv4-Gc_4真值+0.333，原输出attentive/concentrated/positive，续训输出neutral；SqofxdeEcjg_1真值+1.333，原relaxed/joking/happy变成calm/serene/indifferent。它们说明输出中性化会通过评分链损失正类，但未观察媒体，不能仅凭字幕断言心理原因。',
'',
'## 6. HIT提升不一定意味着排他判断更准',
'',
'官方HIT不因额外预测多个情绪而直接扣分；M会按候选集合内多报词约束。按本次各数据集最佳权重对其原始起点复算：',
'',
'|数据集|HIT变化|M变化|平均映射后预测词数变化|',
'|---|---:|---:|---:|']
for d in ['MER2023','MER2024','MELD','IEMOCAPFour']:
 r=a['oracle_comparisons'][d];lines.append(f"|{d}|{r['difference']:+.3f}|{r['new_M']-r['old_M']:+.3f}|{r['old_pred_labels']:.3f}→{r['new_pred_labels']:.3f}|")
lines+=['',
'本轮MELD最高58.53对应M37.20，低于原始M37.37；因此HIT的+2.50不能全部解释为判断更准确。IEMOCAP最佳HIT和M都下降。MELD的fear命中54.00→49.20、disgust仍只有14.22；大量候选并未解决弱类。',
'',
'这里的平均预测词数是五个情绪轮映射后、全部样本的均值。原HIT会跳过未映射到情绪轮的GT，本轮四个数据集neutral类在五轮均被跳过。MELD1256/2610条neutral不进入HIT，不能把58.53理解为全类别普通准确率。每轮有效分母也可能不同。',
'',
'最佳单权重45→54在OVMERDPlus上P60.54→59.51、R63.27→63.75，F61.79→61.49。增加输出提高了少量召回，同时降低精度，最终F下降。',
'',
'## 7. 新发现：评分链会让完全相同回答发生正负翻转',
'',
'直接扫描本轮200项极性任务的缓存，把完整模型回答按字符串精确分组。只要同一字符串在不同任务缓存里有positive和非positive两种结果，即计为一个二分类翻转组。没有重新调用评分模型，没有对官方分数作替换。',
'',
'|数据集|总回答次数|出现二分类翻转的完全相同回答类型|这些组的回答次数|偏离组内多数极性的次数|',
'|---|---:|---:|---:|---:|']
for d,r in j.items():
 if isinstance(r,dict):lines.append(f"|{d}|{r['total_predictions']}|{r['binary_flip_types']}|{r['occurrences_in_binary_flip_groups']}|{r['minority_binary_occurrences']}|")
lines+=['',
'两个可直接复核的例子：',
'',
'1. MOSEI c9hE1ghElrM_0：from_50_epoch_53 与 from_50_epoch_55回答完全相同：The character\'s emotional state is neutral, professional, informative. 两次openset也完全相同：[neutral, professional, informative]；前者sentiment=neutral，后者=positive。相同中间输入也在第二阶段翻转。',
'2. MOSI rnaNMUZpvvg_18：from_30_epoch_32 与 from_30_epoch_33原回答同为excited, enthusiastic, tense, anxious；第一阶段一次漏掉tense，最终一次positive、一次negative。',
'',
'原因可定位到原评分链的随机抽取与极性解释：Qwen judge的SamplingParams temperature=0.7/top_p=0.8，未对每条唯一输入绑定独立固定随机流；生成模型自身也使用do_sample=True/temperature=1.0/top_p=0.9。当前生成阶段按样本固定seed能改善配对性，但不能消除judge链的随机性或估计多种子方差。',
'',
'上表不是错误率，不代表多数输出就是真值，也不能直接换算WAF应加减多少。翻转组也不全是真值非零的计分样本。它严格证明评分链不是模型输出的稳定映射。影响规模不能解释全部50权重退化，但小幅榜首差距需要先排除这一噪声。',
'',
'## 8. 不确定性与工程排查',
'',
'选各集赢家后，对赢家和自身原始起点做2000次样本配对bootstrap，seed20261027。区间没有校正从测试集50选1，且按样本而非视频/说话者聚类；只能作探索性描述，不能当选择校正后的显著性或跨种子泛化区间。',
'',
'|数据集|赢家配对变化|探索性95%区间|',
'|---|---:|---|']
for d,r in a['oracle_comparisons'].items():lines.append(f"|{d}|{r['difference']:+.3f}|[{r['paired_bootstrap95'][0]:+.3f}, {r['paired_bootstrap95'][1]:+.3f}]|")
lines+=['',
'工程上暂未发现错checkpoint、未更新、截断或OOM可以解释本轮整体问题：',
'',
'- 已存档final_verification核验450项、50权重、639950预测的谱系与原始hash。本次又核验code_manifest中的61个源码文件均未漂移。',
'- 本次直接从已有评分缓存独立复算“各集赢家/自身起点”和“最佳单权重/自身起点”共18个配对，所有当前与原始主指标都在1e-12内一致；没有加载torch/vLLM。',
'- 四个新训练日志合计200000steps/600000样本呈现，AMP跳步76次(0.038%)，梯度smoke通过，所有训练answer/subtitle截断与预算删除计数为0。',
'- 赢家九集输入中无空回答；仅MOSEI2条字幕触发截断，不能解释全局瓶颈。不存在“因为所有样本都被512-token预算砍掉了”的证据。',
'- 低训练loss与稳定数值更新不等于目标泛化。以45起点为例generation loss首轮0.601→末轮0.514，但epoch54九集74.017→55轮71.780；单条轨迹存在显著波动，尚缺独立干净dev用于早停。',
'',
'## 9. 下一步最值得做的工作及采用标准',
'',
'1. 先固定评分可复现性：保留官方原协议成绩，另外建立诊断链，对唯一完整回答和唯一openset输入按内容hash统一缓存，固定解码/种子/批处理；同一输入的转换一致性必须100%。若改变官方judge解码，则需给所有对照同样重评并另标协议，不能只修新模型。',
'2. 暂停扩大同配置checkpoint扫描。固定有限起点与未参与测试集选优的验证划分，报告轨迹平均、弱类指标和原始强基线。不要把源pseudo_validation重新用于早停，它已参与图选择并进入续训。',
'3. 做同一权重、同一输入、同一生成随机流的推理消融：无证据 / 仅Cue / Cue+Appraisal / Cue+Emotion / 完整。旧图与十类图先在同一权重上比较兼容性。这样能定位证据的净增量；后续若要证明训练机制，还需无图、无辅助、图、图+辅助的同预算训练对照。',
'4. 先按人工标注分模态、分Cue审核和校准；50条只能发现问题，不能用来拟合后再宣布泛化。继续完成审计，并为阈值拟合和最终审计保留不同样本。不要把跨模态支持数当独立证据的概率。',
'5. 优先验证移除不可靠Appraisal的推理消融，保留分数强弱或只给独立有证据的状态；不能直接采纳10月26日已失败的条件概率/严格门控分支，也不能预设十类图必胜。',
'6. 把极性辅助的价值单独验证：独立dev上检查head的类召回、校准和生成极性一致性，再决定是否采用显式极性生成任务或一致性约束。0.1权重及更长训练没有得到足够证据，应保留no-aux对照。',
'',
'上述为后续实验方案；本次没有启动这些训练/推理，也没有改动当前默认系统。',
'',
'## 10. 复现文件',
'',
'- reanalysis_20261027.py / reanalysis_20261027_stats.json：450评分、225历史评分对照与四分支训练日志统计。',
'- reanalysis_20261027_predictions.py / reanalysis_20261027_predictions.json：18组配对、主指标复算、M/precision/recall/错误计数、2000次bootstrap、目标提示统计。',
'- reanalysis_20261027_human.py / reanalysis_20261027_human.json：50条人工只读快照、正集合统计和payload hash。',
'- reanalysis_20261027_judge_consistency.py / reanalysis_20261027_judge_consistency.json：200项极性评分的同文本一致性扫描。',
'- reanalysis_20261027_examples.json：示例原答案、当前答案、抽取结果及参考标签。',
'- 本报告由reanalysis_20261027_report.py生成。所有文件均位于服务器analysis_reports/。',
]
report=P/'nine_dataset_reanalysis_20261027.md';report.write_text('\n'.join(lines)+'\n')
files=sorted(P.glob('reanalysis_20261027*'))+[report]
manifest={str(f.relative_to(ROOT)):dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files if f.is_file()}
(P/'reanalysis_20261027_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(report,'bytes',report.stat().st_size,'files',len(manifest))


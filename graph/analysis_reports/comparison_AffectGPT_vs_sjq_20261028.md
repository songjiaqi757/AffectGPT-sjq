# AffectGPT 与 AffectGPT-sjq：图与实际运行差异
日期：2026-10-28。全部在服务器读取和分析；只在新项目 analysis_reports 保存本报告及证据索引。未修改旧项目、现有模型或实验配置，未进行GPU推理。

## 结论
两套图确实不是同一机制：旧项目实际主线使用固定符号语义关系表；新项目此次使用从源数据统计得到的188类NPMI关联图。图差异是合理的待验证解释，但现有跨项目分数不能单独证明它是性能差距的主因。

更直接的反证边界是：旧项目50条固定权重、固定Cue消融也没有证明旧AEG相对Cue Only有稳定增量。不能因为旧项目部分benchmark更高，就把旧图当作已经验证有效的答案。

## 主线和分支定位
旧主线：
AffectGPT/AffectGPT/inference1.py
→ affect_prompt_integration.py:AffectPromptEnhancer
→ evidence/evidence_infer.py
→ evidence/graph_retriever.py:GraphRetriever
→ evidence/affect_graph.json
→ evidence/prompt_builder.py

旧项目另有graph_prior.py及evidence/graph/affectgpt_appraisal_graph_v2_numeric_gated.json等分支；不能把它们的余弦、fear/surprise gate等计算误写成上述主线。

新项目本轮：
amg_d_multistart10/runs/d_multistart10_20261025_160152/plan.json
→ amg_runtime/releases/p2p3_20261022_111315/inputs_p0.json
→ amg_graph/runs/amg_edges_v2_restore_diagnostic_20261022/graph/graph.json
→ amg_runtime/engine.py:GraphQueryEngine
→ amg_d_multistart10/policy.py

## 图本身
|项目|旧AffectGPT主线|本轮AffectGPT-sjq|
|---|---|---|
|关系来源/表达|固定语义符号表，++/+/~/-/--；不是由当前列联计数拟合|源训练计数、NPMI、bootstrap下界、支持度/FDR等准入|
|Cue空间|11文本+13音频+13视觉=37，含3种no-clear标签|15文本+17音频+10视觉=42|
|Cue语义|如gratitude_respect、blame_critique、loss_damage_separation|如TXT_NEGATION_PRESENT、TXT_CONTRAST_PRESENT、显式成功/失败、音高/音强/可见动作|
|Appraisal|8个节点，主要为连续有符号得分，agency为投票|6维16状态，按各状态正关联支持排序|
|具体维度|relevance,valence,goal_obstruction,coping,norm_violation,agency,certainty,social_support|goal relevance,goal congruence,expectedness,agency,certainty,coping potential|
|Emotion|图文件定义6个基本情绪，无neutral；是否展示由分支开关控制|此次188情绪概念，Top3；十类图存在但本轮未使用|
|推理路径|Cue→Appraisal加权平均/agency投票，按固定情绪profile匹配|Cue→Emotion直连与Cue→Appraisal→Emotion混合，权重0.75/0.25|
|正负关系|用有符号关系提高/降低同一评价维度|当前准入统计边是正关联；不直接编码负关联反证|
|规模|37条Cue规则行及6个情绪profile；不能等同于37条单边|177 CA+670 CE+201 AE=1048条统计边|
|展示|常用每模态2个Cue；主要把阻碍、应对、确定性、归属合成摘要|展示所选Cue和每维display_candidates；九目标集平均约10个Appraisal状态|

旧图可能更容易保留直接的情感方向：positive_alignment→valence++/goal_obstruction-；laugh_smile_voice也有固定的valence++关系。新图改成关联估计后，强度不再表示这种语义方向，也不等于状态后验。稀有状态可能有更高NPMI，正是先前goal relevance错排的机制线索。
但固定关系也会把反讽、礼貌笑等语境映射错；符号规则不是已验证因果关系，旧分数softmax也不是已校准概率。

## 训练及提示的共同变化
旧主线常用的20260723195分支：graphmix30、cue2+appraisal、训练证据不含emotion candidates；lr2e-6、500steps warmup、3个名义epoch；原始父权重为20260311194 epoch30。
新本轮：50%图训练呈现、gate允许时包含情绪Top3、lr1e-5、无新warmup、10个名义epoch，恢复原AdamW状态。
旧训练31327条，当前续训30755条。两套Cue predictor、标签空间、阈值/校准与提示也不同；旧推理还含benchmark-aware问法，不能将差距全归图。
旧训练配置不含emotion candidates，不代表旧固定九集各推理分支均关闭emotion。experiments/fixed_avt_multiseed.json中仅部分条件显式关闭，需按实际运行逐项区分。

已计算两项目原始epoch30的完整文件SHA256，均为：
73fb1c257c0482e792ecad2ca0706ecccce04639e209071793484b65a97df380
即同一原始checkpoint，不能把这个起点的差异解释成原始模型不同。文件名的202603/202610日期不同不代表权重不同；结论仅核验epoch30，不外推全部checkpoint。

## 旧图独立贡献的已完成实验
真实结果目录：
/ai/sjq/AffectGPT/AffectGPT/experiments/aeg_contribution_20261011_epoch3/run_20261011_01/results/86cd93eccb907a3f/evaluation/c27753ec1c7444f7/

固定同一完整epoch3权重、同一批预测Cue，每模态top2；生成seed42/43/44；统一去重抽取后按原EW指标评分：
|条件|三次生成均值F1，%|
|---|---:|
|Base，无证据|67.73|
|Predicted Cue Only|67.29|
|Predicted Cue+AEG|67.28|
|Predicted Cue+Random Appraisal|66.81|
|人工Cue Only|70.26|
|人工Cue+AEG|68.02|

AEG-Cue Only=-0.01个百分点，配对95%区间[-2.29,+2.23]；
AEG-Random=+0.47，区间[-0.34,+1.41]；
人工Cue下AEG-Cue Only=-2.24，区间[-4.80,+0.14]。
不能证明旧图优于Cue Only或随机关系，也不能据此证明所有图都无效。50条与MLLM训练材料全部重叠，人工Cue单标，情绪参考来自已有训练标签；这是源材料探索诊断，不是独立目标测试。
旧主结果77.65%是跨checkpoint/epoch/提示的各集选优拼接；旧固定配置三次生成重复也按数据集选不同checkpoint，不能与新项目单一权重74.02%直接归因比较。

## 应如何检验是不是图的原因
不能直接把旧JSON替换新JSON：Cue词表、Appraisal维度与值域不同，替换会同时改变可用证据及接口语义。
建议分两层：
1. 比较两套完整旧/新链路，作为系统级复现，不声称隔离图。
2. 冻结共同Cue定义和同一批Cue分数，保留语义确实一致的共同子集；在同一Appraisal本体上分别建立固定语义关系版和统计关系版。统一是否展示Emotion、输出摘要、token预算、模型权重、生成随机流与评分缓存。加入Cue-only基线。若有旧/新两种已适配权重，可交叉比较以检查提示适配偏差。

若规则版在这些控制下稳定优于统计版，才能支持“关系建模方式导致差距”；若二者都不胜Cue Only，说明需要优先处理Appraisal的增量价值和接入方式。规则/统计融合仅作为后续待验分支，不能直接许诺提升。
本次只完成对比和证据核验，没有启动上述新实验。

# Reader validation results

All artifacts on server; seed42, fit4000/dev500. Base already saw all source31327.
Sample bootstrap is exploratory; no cross-seed claim. Null prefixes are inference distribution interventions.

|Condition|micro-F1 %|sample macro-F1 %|
|---|---:|---:|
|native-random-off|46.0836|49.2675|
|native-random-random|45.1148|48.0584|
|native-random-retrieval|45.0787|48.0368|
|native-retrieval-off|46.6102|49.7181|
|native-retrieval-random|46.2292|49.2936|
|native-retrieval-retrieval|46.3550|49.3905|
|old-null-bank_mean|45.8920|48.9670|
|old-null-zero|45.6175|48.6973|
|old-ref-normal|46.0784|49.1463|
|old-ref-off|46.3749|49.4842|
|old-ref-random|46.0733|49.0860|
|scaled-random-off|46.7863|49.9493|
|scaled-random-random|46.0488|49.2385|
|scaled-random-retrieval|46.0488|49.2090|
|scaled-retrieval-off|46.5664|49.7752|
|scaled-retrieval-random|45.8374|48.7469|
|scaled-retrieval-retrieval|45.4992|48.5959|
|zero_init-null-bank_mean|46.2394|49.3571|
|zero_init-null-zero|45.8632|49.0023|
|zero_init-ref-normal|46.3550|49.3905|
|zero_init-ref-off|46.6102|49.7181|
|zero_init-ref-random|46.2292|49.2936|

Matched starts/exposures passed. Pairwise exploratory intervals and mechanism audit are in reports/.
Predeclared practical gain threshold: +0.5pp, positive paired interval against native and own off/random.
No automatic full31327, Situation/HGT or target evaluation is authorized by this pipeline.

## 完成后的结果解读

完成时间：2026-10-16 19:55（北京时间）。

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

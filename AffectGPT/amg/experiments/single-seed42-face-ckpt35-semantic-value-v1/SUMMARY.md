# Semantic Memory value results

Seed42; fixed AV candidates, 4000 fit/500 source dev. Base already supervised all source31327.
All arms have identical 2816-dimensional value inputs, 4 tokens and common initialization.

|Condition|micro-F1 %|sample macro-F1 %|
|---|---:|---:|
|av-only-off|46.5359|49.6940|
|av-only-random|46.1990|49.3882|
|av-only-retrieval|46.0986|49.2106|
|caption-off|46.0685|49.1568|
|caption-override-av_only|45.6657|48.6822|
|caption-override-shuffled_caption|45.7721|48.7308|
|caption-override-subtitle|45.5853|48.5784|
|caption-random|45.6564|48.6617|
|caption-retrieval|45.6209|48.6498|
|shuffled-caption-off|46.2141|49.2592|
|shuffled-caption-random|45.9081|48.9479|
|shuffled-caption-retrieval|45.9530|48.9587|
|subtitle-off|46.2492|49.2727|
|subtitle-override-av_only|45.8415|48.9667|
|subtitle-random|45.9327|49.1433|
|subtitle-retrieval|45.9124|49.0862|

Matched initialization, exposure and exact retrieved IDs verified. Bootstrap is exploratory sample uncertainty for one seed.
Practical gate: aligned caption must exceed capacity-matched AV-only, shuffled captions and its own off/random; +0.5pp is predeclared.
No automatic target/holdout, full31327, graph or Situation experiments.

## 完成后的结果解读

完成时间：2026-10-16 21:05（北京时间）。

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

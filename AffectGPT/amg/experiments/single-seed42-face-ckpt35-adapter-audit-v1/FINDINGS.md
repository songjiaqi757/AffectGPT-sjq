# Adapter机制检查结论

本次对500条真实dev query缓存及同一份训练后Adapter做CPU检查，没有调用GPU、加载Qwen、生成文本、修改原模型或训练。逐层重放与原forward最大绝对误差约1.9e-7；独立手算attention与MHA匹配，FP64检查确认近均匀行为真实存在。

## 1. Value MLP末层公共偏置主导表示方向

正常/随机邻居集合均值的平均cosine：原1792维输入0.966772；第二层线性变换未加bias时0.982746；加上公共bias后0.999192。末层bias范数0.538449，而Wx信号范数均值0.120708，约4.46倍。全库末层输出共同均值能量比例0.997440。

偏置相同地加到所有邻居，不会消除绝对差值；它使共同分量和相对尺度占主导，因此不能把该现象表述为信息已不可逆丢失。冻结权重只去掉这一项bias，最终正常/随机token的cosine从0.999237降至0.988222，相对L2差从0.038450升至0.151465，约为原来的3.94倍。这只是内部敏感性探针，没有重新生成或证明F1提高。

## 2. Attention确实近似均值聚合

正常/随机五邻居logits标准差均值分别2.0623e-5和2.8126e-5。FP64重算仍接近每项0.2；原FP32 entropy显示1是极小熵差舍入。mask、softmax轴、head平均及精度误报已核查。用精确均匀平均替代原attention，最终token相对L2差均值仅5.75e-7/8.35e-7。

Q/K每头的有效尺度和邻居间K变化很小，再除sqrt(64)=8，导致可用于选择邻居的logit差极小。公共K偏移对一行增加相同常数，会被softmax抵消，故不能把bias单独说成attention均匀的直接原因。gate在attention之后，也不是权重均匀的原因。

## 3. 参数发生变化不等于内容选择已学好

最终优化器状态显示Query slots、Query MLP、Q/K投影的梯度尺度远低于Adam eps=1e-8；V路径明显高于eps。Q/K权重最终moment对应的数据更新项RMS约4.75e-10/4.32e-10，weight decay项约2.21e-8。该最终状态支持选择性通路任务梯度很弱，但不能反推出唯一学习率、初始值或整个训练历史。Adapter各参数step1321、LoRA1332；整段Memory dropout导致部分iteration没有Adapter梯度属预期。

原训练未保存完整初始Adapter或构造前RNG状态，未用seed42随便新建模型冒充真实初值。原coverage的19个Adapter张量changed，只能证明值发生变化，不能单独证明学到了邻居区分能力。

## 已定位与下一步边界

当前Adapter行为接近带强共同分量的平均聚合器，邻居差异在Value投影后变得相对弱，Query控制的选择性attention几乎没有发挥作用。这与正常/随机邻居替换后491/500输出相同相吻合，但不构成完整生成质量机制的唯一证明。

最小单因素候选优先单独验证Value MLP最后一层bias；attention尺度另列独立对照。不要一次改学习率、gate、检索和归一化，也不要据CPU探针直接扩大到全31K/HGT。任何参数修改或新训练的效果均需同预算任务评测，本轮尚未执行。

详见layer-audit/SUMMARY.md、attention-audit/SUMMARY.md、optimization-audit/OPTIMIZATION_AUDIT.md及各自完整JSON。全部产物仅在服务器。

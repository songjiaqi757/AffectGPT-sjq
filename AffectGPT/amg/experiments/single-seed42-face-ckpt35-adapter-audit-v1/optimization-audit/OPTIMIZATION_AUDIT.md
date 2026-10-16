# Adapter初始化与优化尺度审查

生成：2026-10-15T17:42:03.915439+00:00。仅服务器CPU读取真实trained Adapter、最终optimizer和500条真实dev缓存；未加载Qwen、未调用GPU、未训练或评分。

## 初值边界

没有把manual_seed(42)后随便新建的Adapter当作真实初值。实际Adapter在完整AffectGPT/Qwen/PEFT/AV构造之后初始化，前序消耗RNG；训练未保存构造前RNG或完整初始Adapter。只能精确比较源码明确的常数初值（gate、MHA bias、LayerNorm常数）。

真实coverage记录Adapter全组最大坐标变化0.001992490；19个tensor均变化且有限。这不等于每层平均变化，也不能证明学习率充足或不足。

## 输入与默认初始化尺度

- 1792维输入来自两个单位范数模态，整体范数约√2，分量RMS=0.033407655。
- 默认Linear(1792,256)权重/bias区间±0.023623；理论bias分量RMS=0.013639，Wx分量RMS约0.019288。
- 第二层Linear(256,256)默认bias分量RMS约0.036084。这些是分布公式，不是本轮真实随机初值观测。

## 训练后实际仿射分解

|路径|层|bias L2|mean(Wx) L2|mean(output) L2|平均中心化残差L2|共同均值能量比例|
|---|---|---:|---:|---:|---:|---:|
|value_all_bank|first_affine|0.220987|0.320539|0.392431|0.096303|0.942183|
|value_all_bank|second_affine|0.538449|0.117171|0.553498|0.027750|0.997440|
|query_actual_dev|first_affine|0.218220|0.297370|0.372869|0.096271|0.936417|
|query_actual_dev|second_affine|0.535358|0.107211|0.550483|0.027518|0.997457|

各仿射项可能相关，不能把bias范数当作可相加的因果占比；共同分量还可来自输入的共同方向。

## 实际normal邻居的MHA分数

- 四头、每头64维，分数按QKᵀ/8计算；没有Q/K LayerNorm、L2 normalize或learned temperature。
- Q/K每头分量RMS=0.027147617/0.022869486。
- 每行5邻居logits的标准差均值=2.0622918e-05，range均值=5.70414127e-05。
- float64 softmax最大权重超出0.2的均值=5.75458933e-06；1−归一化entropy均值=1.53477602e-10。

近乎均匀是数值上可确认的现状。float32 entropy舍入到1不等于softmax导数为0；真正影响权重的是同一行跨邻居的logit差。Gate在attention之后，不能造成attention均匀。

## 优化器最终状态

AdamW lr=1e-05，eps=1e-08，weight_decay=0.05；LoRA和Adapter共享一组，统一clip_grad_norm=1；原AMG循环无lr scheduler。成功迭代1332，各参数step计数{1332: 392, 1321: 19}。

|参数|有效state step|sqrt(v̂)中位数|低于eps的比例|最终moments对应Adam数据项RMS|
|---|---:|---:|---:|---:|
|queries|1321|2.45023e-11|1.000000|3.41482e-09|
|query_projection.0.weight|1321|2.60544e-13|1.000000|8.5465e-11|
|query_projection.0.bias|1321|2.03575e-11|1.000000|2.53481e-09|
|query_projection.2.weight|1321|6.23679e-13|1.000000|1.12777e-10|
|query_projection.2.bias|1321|7.0348e-11|1.000000|9.35766e-09|
|value_projection.0.weight|1321|6.1037e-07|0.000000|1.57961e-06|
|value_projection.0.bias|1321|6.05618e-05|0.000000|1.71835e-06|
|value_projection.2.weight|1321|1.77148e-06|0.000000|1.65229e-06|
|value_projection.2.bias|1321|0.00021343|0.000000|1.62478e-06|
|attention.in_proj_weight|1321|4.20543e-12|0.666667|9.91896e-07|
|attention.in_proj_bias|1321|9.92577e-11|0.666667|9.75908e-07|
|attention.out_proj.weight|1321|8.448e-06|0.000000|1.76619e-06|
|attention.out_proj.bias|1321|0.000530562|0.000000|1.73315e-06|
|output_projection.0.weight|1321|5.07846e-06|0.000000|1.76963e-06|
|output_projection.0.bias|1321|7.54878e-06|0.000000|1.77215e-06|
|output_projection.1.weight|1321|2.37616e-06|0.000000|1.84146e-06|
|output_projection.1.bias|1321|3.44927e-06|0.000000|1.82453e-06|
|gate_projection.weight|1321|1.32183e-06|0.000000|1.22914e-06|
|gate_projection.bias|1321|0.000106526|0.000000|1.01013e-06|

这些是最终moments的解析尺度，不是完整更新历史。若sqrt(v̂)经常小于eps，小梯度通路会受eps影响；仅凭最终state仍不能确定是初值、输入几何、监督信号还是学习率造成。

## 判断与限制

训练后的共同仿射分量、小Q/K分量及极小跨邻居logits差可以解释当前近似常量value和近均匀attention的数值机制；不能据此反推唯一训练历史。近似相同的values也会让重分配attention对输出影响很小，进一步减弱Q/K路径的学习信号。

不建议据此直接增加学习率或全量重训。应先以冻结权重做明确、独立的归一化/bias/温度消融，并把参数影响与任务质量分开验证。完整数值、源码初始常数边界和哈希见summary.json及附属JSON。

## 两个机制必须区分

给所有key加同一个偏移c，只会让同一query的所有logits加同一个常数q·c/√d，softmax严格抵消；因此不能把共同bias直接当作attention均匀的原因。共同value偏移则会进入attention输出，使normal/random共同分量变大。给两路value均值加同一b2不改变二者的绝对差，只会改变相对范数和cosine；这不是证明信息被彻底删除。

Q/K/V最终optimizer状态拆分：

|参数块|sqrt(v̂)中位数|低于eps比例|Adam数据项RMS|衰减项RMS|
|---|---:|---:|---:|---:|
|attention.in_proj_weight.Q|3.14512e-12|1.000000|4.74572e-10|2.20697e-08|
|attention.in_proj_weight.K|2.52854e-12|1.000000|4.32107e-10|2.2155e-08|
|attention.in_proj_weight.V|8.1923e-06|0.000000|1.71801e-06|2.20929e-08|
|attention.in_proj_bias.Q|9.92083e-11|1.000000|1.27418e-08|1.89609e-12|
|attention.in_proj_bias.K|3.53386e-14|1.000000|6.3815e-12|6.73029e-16|
|attention.in_proj_bias.V|0.000303921|0.000000|1.69027e-06|1.62152e-10|

“参数变了”并不等于学会使用邻居：AdamW在存在零值grad时也可通过weight decay改变参数。最终moments中Q/query路径的信号小且受eps影响，是当前可测现象，仍不能单凭它确定历史学习率因果。

## 最小单因素优先候选

优先只检查/移除value_projection.2.bias，固定其余参数、Q/K尺度、gate、LR和评分。它直接针对已测到的相对对比稀释，并且不会把“更非均匀attention”误当成任务收益。内部对比扩大不是情绪识别提升；若后续要验证任务效果，应另用固定dev的明确干预。当前审计没有启动任何推理或训练，也不建议同时改bias、归一化、温度和学习率。

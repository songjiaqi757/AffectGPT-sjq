# 本轮原图＋D：50个checkpoint九数据集最优结果

完成时间：2026-10-27 21:07（北京时间）。450项结果、每个数据集50个checkpoint；最终预测数量639950条，完整性核验通过。

下表按原版AffectGPT主指标在50个权重内分别选优；全部值为百分数，原始起点与续训后的epoch共同确定权重。

|数据集|主指标|最好结果|原始checkpoint|续训后epoch|同一最优权重辅助指标|
|---|---|---:|---:|---:|---|
|MER2023|HIT|79.0085|30|39|—|
|MER2024|HIT|79.8081|45|54|—|
|MELD|HIT|58.5257|30|39|—|
|IEMOCAPFour|HIT|60.1167|30|39|—|
|CMUMOSI|WAF|82.8635|50|57|ACC=82.7744%|
|CMUMOSEI|WAF|80.3151|50|55|ACC=80.2422%|
|SIMS|WAF|89.4411|35|41|ACC=89.4330%|
|SIMSv2|WAF|86.0707|45|49|ACC=86.0593%|
|OVMERDPlus|F_s|62.7512|35|40|P_s=61.6748%，R_s=64.0082%|

九数据集分别选优后的均值：75.4334%。这些最优值来自不同权重。
最佳单一权重：原始checkpoint45起点续训至epoch54，九集均值74.0173%。

OVMERDPlus本轮最优62.7512%；此前63.1529%来自不同的完整原图证据训练方案，不属于本轮固定D设置的50权重。

每个最优权重的绝对路径：

MER2023：/ai/sjq/AffectGPT-sjq/amg_d_multistart10/runs/d_multistart10_20261025_160152/from_30/checkpoint_000039_loss_0.684.pth
MER2024：/ai/sjq/AffectGPT-sjq/amg_d_multistart10/runs/d_multistart10_20261025_160152/from_45/checkpoint_000054_loss_0.511.pth
MELD：/ai/sjq/AffectGPT-sjq/amg_d_multistart10/runs/d_multistart10_20261025_160152/from_30/checkpoint_000039_loss_0.684.pth
IEMOCAPFour：/ai/sjq/AffectGPT-sjq/amg_d_multistart10/runs/d_multistart10_20261025_160152/from_30/checkpoint_000039_loss_0.684.pth
CMUMOSI：/ai/sjq/AffectGPT-sjq/amg_d_multistart10/runs/d_multistart10_20261025_160152/from_50/checkpoint_000057_loss_0.474.pth
CMUMOSEI：/ai/sjq/AffectGPT-sjq/amg_d_multistart10/runs/d_multistart10_20261025_160152/from_50/checkpoint_000055_loss_0.499.pth
SIMS：/ai/sjq/AffectGPT-sjq/amg_d_graph_compare/runs/d_compare_20261025_111800/D_continue/checkpoint_000041_loss_0.604.pth
SIMSv2：/ai/sjq/AffectGPT-sjq/amg_d_multistart10/runs/d_multistart10_20261025_160152/from_45/checkpoint_000049_loss_0.595.pth
OVMERDPlus：/ai/sjq/AffectGPT-sjq/amg_bcd_polarity_oof/runs/bcd_polarity_20261025_014715/D/checkpoint_000040_loss_0.669.pth

# AffectGPT论文行的checkpoint溯源

作者结果目录：emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20250110100

|数据集|论文值|作者缓存重算最高值|checkpoint|
|---|---:|---:|---|
|MER2023|78.54|78.538700|checkpoint_000050_loss_0.527|
|MER2024|78.80|78.796984|checkpoint_000045_loss_0.551|
|MELD|55.65|55.649145|checkpoint_000030_loss_0.602|
|IEMOCAPFour|60.54|60.536756|checkpoint_000035_loss_0.597|
|CMUMOSI|81.30|81.301356|checkpoint_000040_loss_0.569|
|CMUMOSEI|80.90|80.899905|checkpoint_000030_loss_0.602|
|SIMS|88.49|88.489744|checkpoint_000030_loss_0.602|
|SIMSv2|86.18|86.184846|checkpoint_000035_loss_0.597|
|OVMERDPlus|62.52|62.522881|checkpoint_000050_loss_0.527|

逐集最高值的均值：74.76892398。

固定checkpoint的均值：
- epoch 30: 73.549111
- epoch 35: 73.963003
- epoch 40: 72.367444
- epoch 45: 73.486316
- epoch 50: 73.422999
- epoch 55: 73.323059
- epoch 60: 71.967770

原始评分入口对每个数据集的whole_score1s取np.argmax，再对九项最佳值求均值。
当前output中20261014训练目录与作者20250110结果属于不同训练轮次，不能以相同epoch视作同一权重。
未在当前output中找到作者20250110100训练轮次的.pth权重；该处有作者的预测与评分缓存。

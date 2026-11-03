# 四组全量微调实验

任务目录：/ai/sjq/AffectGPT-sjq/cue_student/jobs/full_finetune_20261020_170308
正式输出：/ai/sjq/AffectGPT-sjq/cue_student/output/full_finetune_20261020_170308

用户指定新增四组并按GPU0三组、GPU1一组放置：

| 名称 | GPU | 编码器 | 头部 |
|---|---:|---|---|
| audio_full | 0 | HuBERT全量可训练 | mean + MLP |
| audio_temporal_full | 0 | HuBERT全量可训练 | 两层时序Transformer + MLP |
| visual_full | 0 | CLIP全量可训练 | mean + MLP |
| visual_temporal_full | 1 | CLIP全量可训练 | 两层时序Transformer + MLP |

原有五个任务继续训练，全部同源代码、严格排除失败样本的数据包与固定300条人工保留集。
新四组均从预训练编码器及新初始化头开始，不使用旧Student checkpoint。音频315435136、视频303966208个编码器参数全部requires_grad=true。
与对应冻结基线保持head_lr、encoder_lr(1e-5)、batch、grad_accum、训练/验证成员、FPS、标签mask、seed及早停配置一致。
变化为encoder_train=full、gradient_checkpointing=true，并增加cuda_memory_fraction=0.20作为独立进程的PyTorch allocator显存上限。默认HuBERT LayerDrop0.1仍生效，这与冻结或只训练最后几层不同。
音频完整有效帧、视频既定2FPS首尾覆盖、动态时长组批、微批2/累积16保持原设置。

输入管线优化沿用原设置：音频两组worker2，视频两组worker4，prefetch2、pin_memory、non_blocking、worker Torch/BLAS单线程、视频decode_threads1。
每个新增进程在进入训练器前通过memory_limited_train.py限定为一张可见GPU、20%显存allocator预算（80GB卡约16GB）。
启动前检查两卡现有占用 + 所有新增进程最大allocator预算 + 8GiB余量不超过卡容量；逐个启动并等待首次optimizer更新，随后再启动下一组。
四个预检按顺序执行，最多一个预检进程，均受20%上限约束。输入为训练集中最长的两个样本，合并时长超过正式动态组批上限，作为保守显存测试。音频时序预检额外强制所有HuBERT层激活，正式训练仍沿用原始LayerDrop。
预检验证真实bf16前反向、AdamW更新、encoder/head权重变化、所有编码器参数可训练、梯度与loss有限。结果见NAME.preflight.json。

状态status.json、日志NAME.log、配置configs/NAME.json。
source/仅保存完全相同的共享Python源码，用于指纹追溯；实际训练从主项目cue_student导入，不修改正在运行的五组源码。
jobs/latest_full_finetune.json指向本任务，jobs/latest_all_experiments.json汇总原五组与新增四组。
正式启动入口launch.py；恢复时必须使用memory_limited_train.py和原配置/原输出目录，附--resume OUTPUT/last.pt以继续保留显存上限。

并行后GPU0共六组、GPU1共三组，共享计算资源；原五组此前完成时间估算不再适用。这里保证显存预算受限，并不保证新增并行提高每组训练速度。
原标注失败72个样本的排除规则、固定人工300条隔离及模型选择规则保持原状；所有操作/文件只在服务器。

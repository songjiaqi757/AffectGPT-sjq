# Cue Student：五组提取器实验

当前生效的数据政策为 all_modalities_succeeded_v1：
文本、音频或视频任意一个标注任务失败，就排除整个样本。78条失败模态任务去重后为72个样本，均不进入训练、伪标签验证、人工300条或诊断保留集。原始标注记录和媒体不删除。

当前任务目录：
/ai/sjq/AffectGPT-sjq/cue_student/jobs/strict_all_modalities_20261020_163131

数据包：
/ai/sjq/AffectGPT-sjq/cue_student/artifacts/release_strict_all_modalities_20261020_163131

输出目录：
/ai/sjq/AffectGPT-sjq/cue_student/output/strict_all_modalities_20261020_163131

## 五组实验

| 名称 | 编码器 | 头部 | DataLoader workers | GPU |
|---|---|---|---:|---:|
| text | XLM-RoBERTa，全量微调 | 双语言池化 + MLP | 0 | 0 |
| audio | HuBERT，冻结 | 有效帧均值 + MLP | 2 | 0 |
| audio_temporal | HuBERT，冻结 | 全有效帧时序Transformer + MLP | 2 | 0 |
| visual | CLIP，冻结 | 帧特征均值 + MLP | 4 | 1 |
| visual_temporal | CLIP，冻结 | 帧级时序Transformer + MLP | 4 | 1 |

两个时序头均为256维、2层、4头、FFN1024。音频时间步长20ms，保留全部有效HuBERT帧；视频保留既定2FPS及首尾帧。视频时间来自实际PTS。
每组从预训练编码器和新初始化头开始；没有 resume 或 init-from 旧训练结果。
数据划分：pseudo_train 27679、pseudo_validation 3076、gold_audit 300、diagnostic_reserved 200。每模态没有任何可监督cue的样本仍由训练加载器排除；失败样本已在划分之前全局排除。

## 性能设置

五组均使用已验证的有序DataLoader、pin_memory、non_blocking传输。启用worker的任务采用spawn、多进程预处理、prefetch_factor=2，每个worker限制Torch/BLAS线程为1；视频decode_threads=1。文本worker0是先前实测选择。BF16、微批和梯度累积沿用既有设置。上述是输入管线优化，不代表所有微批大小和GPU吞吐已调至最优。

## 数据与人工保留集

eligibility.py从已结束的标注队列生成成功白名单和失败样本并集，prepare.py在划分前过滤。
每个数据包保存eligibility.json，文件摘要纳入release_id；Release加载器强制验证此政策及成员白名单。
固定人工集位于 cue_student/splits/holdout300。保留原299个成功成员，排除samplenew3_00094241，补入samplenew3_00039200。
替补来自旧独立诊断保留集，三模态均成功，并排除旧训练/验证/开发组和已知原始媒体重复；按seed42的无标签值随机顺序选取。当前仍未创建人工gold标签，不能把Teacher伪标签性能当作人工性能。

## 状态、验证和使用

当前任务目录中的 status.json 包含五组状态、PID、配置、数据身份及输入管线设置。每组日志为 NAME.log。data_audit.json记录集合交集审计，unit_tests.log和integration_report.json记录验证。
jobs/latest_full.json、jobs/latest_audio_temporal.json及jobs/latest_strict.json指向当前任务。
统一源码在 cue_student/；当前任务目录/source/留存同版本的可运行源码和测试。
训练命令由 launch.py记录。若以后需要断点恢复，在原配置、代码、release及输出目录不变时使用 --resume 原输出/last.pt；改变数据政策不能沿用旧权重续训。

生成新的数据包（已冻结人工集时）：

    python -m cue_student.prepare --scope engineering --output NEW_ABSOLUTE_DIRECTORY --allow-unverified-groups

推理：

    python -m cue_student.predict --checkpoint BEST_PT --input INPUT_JSON --output OUTPUT_JSON --device cuda:0

五组结束后，任务管理器生成 comparison.json，汇总同一伪标签验证集上的最佳检查点、逐cue指标及音频/视频时序对比。人工300条不参与早停或模型选择。
旧训练结果已作废，并按用户要求清理；当前训练不会读取旧检查点。

本次任务：AffectGPT-RL 与 OPPO，官方推理和测评，仅加入此前的 Cue + Appraisal + 10-emotion 图。

范围：AffectGPT-RL epoch 5/10/.../60 共 12 个 checkpoint，各九数据集；OPPO 官方发布权重各九数据集。每个 checkpoint 12799 条样本，共117项、166387条预测。
图：完全复用 base7_original_plus_graph10_20261031_122105 对应的冻结 graph10 缓存与 D compact+gate 格式，图提示预算512 tokens。
官方推理：原样提取两个项目的样本循环，唯一模型输入变更为追加图提示。RL 保留 1200 new tokens / max_length 2000；OPPO 保留启动脚本默认1024 new tokens、temperature0.9、top_p0.9、do_sample、音频开启。
路径适配：RL 其余八数据集补齐官方读法需要的本机路径，嵌套人脸路径映射到原有相同 NPY；OV-MERD+两目录的1596个媒体文件逐一哈希相同。
官方评分：RL 的 OV-MERD+ 用其 statistic.py；其余八数据集用原始 AffectGPT 的官方 MER-UniBench evaluation.py。OPPO 用自己的 merbench/evaluation.py，full answer、use-answer-openset 开启。只在推理进程退出后启动评分。
运行：Qiii/A800 四个 RL worker；Qiii-A100/A100 一个 OPPO worker。长视频 OPPO 实测峰值显存64.4 GiB，因此保持单路、保留官方处理。三路 RL 加载和全部12 checkpoint恢复均已验证。
后台流水线支持逐样本恢复和有限重试。进度见 pipeline_rl.json、pipeline_oppo.json 和 workers/*.json；日志见 logs/；官方格式输出见 official/。完成后自动写 metrics_all.csv、per_checkpoint_summary.csv/json 和 RESULTS.md。
完整指标尚未生成。启动与首批真实输出已验证，见 validation/production_start_verified.json。所有代码、数据、权重、预测和日志保留在服务器，未下载到本地。

2026-11-02 双节点扩容：OPPO 推理与评分完成后，在 A100 新增四路 AffectGPT-RL（slot 4–7），与 A800 原四路（slot 0–3）共用冻结任务队列，总计八路。A800 四个推理进程原地接管，未重启，保留全部历史预测和原 plan_id。跨节点 flock 排他性已经真实验证。双节点控制器及拓扑见 multinode_control/；只有八个推理 worker 全部退出、两卡显存均释放且108个 RL 任务全部导出后，A800 才启动官方评分。

2026-11-02 优先测评：ckpt10 九数据集官方预测全部导出后，priority_evaluation/ckpt10/watcher.py 自动暂停 A100 四路并释放显存，按官方评分函数仅评 ckpt10；A800 四路持续推理。评分写入全局 scores/ 与 CKPT10_RESULTS.md，随后 A100 自动恢复四路。最终全量评分跳过已完成的 ckpt10，不重复测评。

2026-11-02 自动测评策略更新：本次 ckpt10 推理完成后，同一次释放 A100 测评 ckpt5 和 ckpt10；此后15、20、25、30、35、40、45、50、55、60每个checkpoint九数据集推理完成后都按相同方式自动测评。A800持续推理，A100测评后恢复四路；最终checkpoint完成后不再重启已无任务的worker。最终汇总复用所有已提交评分。策略和进度见 priority_evaluation/automatic/。此更新覆盖此前仅测评ckpt10的一次性策略。


## Qi 七路加入现有八路 — 2026-11-03T18:01:16.314108+08:00

新增 Qi GPU0 三路（slot8–10）、GPU1 四路（slot11–14），与 A800 四路、A100 四路共用原分片队列。Qi 的每个分片由原服务器上的 SSH broker 持有相同 flock；逐样本原子回写并验证 plan/checkpoint/graph cache/official contract。七路均已成功提交结果。官方源文件、生成参数、冻结图缓存及原 plan_id 保持不变。Qi 使用独立 Python3.10 / PyTorch2.7.1+cu128 / CUDA12.8 环境以支持 sm120；BF16、无量化。已核对全部九个数据集的成员、字幕和媒体路径，并验证实际生成、提示词和图证据与原服务器相同。每 ckpt 完成后临时释放 A100 四路做官方测评并恢复的策略继续生效。

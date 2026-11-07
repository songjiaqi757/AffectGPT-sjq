# checkpoint35 → checkpoint36–40：AMG v2.1 Graph-OOF + P4 紧凑证据 + 门控

本任务所有项目文件、数据、日志、缓存、模型都只在服务器上创建或读取。Qiii/A800 训练；Qiii-A100/A100 分担 CPU 图准备；两机共享此目录。

- 原始起点：checkpoint_000035_loss_0.723.pth，SHA256 0d0fa91f579d2540bf321630aeb05b35c2c919bb792800813968fc8352870a4e。
- 新权重：from_35/checkpoint_000036... 至 checkpoint_000040...，共 5 个；每个 5000 iteration，总 25000 iteration。
- batch_size=3，lr=1e-5，weight_decay=.05，fp16，恢复原优化器与 GradScaler；原 hybird(description/ovlabel) 监督和 face/audio/multi 输入。
- 原始 30755 条 AffectGPT 训练成员不变；500 条保留审计样本不进入训练。
- 指定图：amg_v2_1_cue_admission_8a8994fe1e7495f0；对应 P4 输入保留 Cue 描述、source-domain 校准分数和 signed C。沿用此前三数据集推理的 P4 图预算 1000 token、完整 Prompt 最多 800 token。原字幕不截断；若图超预算则按 P4 原有规则删除完整假设块/最低优先 Cue，重新计算覆盖率。
- Graph-OOF 是原历史 D 方法的 graph-only OOF，不是 Student-OOF。冻结原 v2.1 Cue Student，未切换 current_student_oof 图、未重训 Student。
- 5 折将源 group、相同媒体 SHA256 和已有保守长字幕分组保持在同一折。每折排除 held groups 后，重新拟合 G1 CA/CE、关系校准、Cue 校准/双层准入、64 次关系 bootstrap、5 个内折符号稳定性和边删除准入。held groups 不参与这些拟合或准入。沿用 v2.1 的 AE 关闭状态。
- Cue 准入保留原 v2.1 1000 次 group-bootstrap 与阈值稳定性约束。仅略去本次任务不需要的重复内部评估嵌套循环，不改最终校准拟合/阈值规则。
- 历史 D 门控：至少2个 Cue；emotion coverage>=.35、relative gap>=.10、至少2个支持 Cue；混合文本情感削弱至 appraisal；证据不足回退 Cue-only/无图。训练呈现时 20% 完全无图、另20%去掉 emotion。
- P4 默认不输出全局 W，仅输出实际贡献 C；未引入任务特定 prompt 分支。各折权重/校准有意不同于全量发布，runtime 由 Fold G1 与 Fold Cue admission 一同构建。
- 上下文最大2048，prompt<=800，answer<=510，实际训练序列<=1398；保持历史不启用 LLM gradient checkpointing 的执行方式。全量所有样本、原版两套匹配问题/答案、两类监督及三种 dropout 情况在 CPU 做长度/多模态标记验收。
- 训练随机流重新按 seed42 初始化；checkpoint35 的原始 optimizer/scaler 恢复，模型从原始权重继续。
- GPU 实际两次成功优化器更新与 LoRA 权重变化验收计入本次25000步。
- 不覆盖原始图、checkpoint 或其他实验；本次没有请求/启动目标集评测。

监控：pipeline_status.json；folds/*/status.json；folds/*/evidence_progress.json；train.log；from_35/status.json。
进程：service_A800_process.json、service_A100_process.json、coordinator_A800_process.json、training_process.json。
完成清单：from_35/checkpoints.json；最终 pipeline_status.json.state=complete 才代表五个新增 checkpoint 全部完成。

本轮最终输入：原版 description/ovlabel 两套各自匹配的问题和答案，随机各50%；P4 图证据由此前推理同一个 AffectGPTUnifiedBridge.prepare() 生成，保持 native max_length2000/max_new_tokens1200 对应的800 token输入预算。训练答案仍按原续训监督设置；推理的1200不是训练答案长度设置。

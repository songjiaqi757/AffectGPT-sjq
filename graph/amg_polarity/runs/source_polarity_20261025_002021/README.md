# 源域训练集极性伪标注

仅使用当前 30,755 条源域训练样本的 ovlabel，不读取目标测试标签，不使用图证据作为标注输入，排除 500 条人工核验样本。

双卡各一个 Qwen2.5-7B-Instruct 进程，复用原版测评提示词、聊天模板及 temperature=0.7 / top_p=0.8 / repetition_penalty=1.05 / max_tokens=512。每批设置并记录随机种子。相同 ovlabel 字符串只标注一次，映射回全部样本。按输入长度由大到小共享批次队列；逐条原子缓存，可恢复。非法输出重试，绝不自动填 neutral。

类别编号 negative=0、neutral=1、positive=2；符号分别 -1、0、1。结果是伪标签，human_verified=false，未做人工可靠性核验，模型未输出校准置信度。源 ovlabel 已经是 neutral 的样本也使用相同裁判流程，不能据此认定为人工中性标注。

最终输出 polarity_labels.json / .jsonl / .csv 和 summary.json；状态 status.json、gpu_0_status.json、gpu_1_status.json；日志 controller.log、gpu_0.log、gpu_1.log。未启动任何 AffectGPT 新训练。所有文件仅存服务器。

重试三次仍输出 mixed 或其他非法类别时，保留 abstain，polarity_id=-100、valid_for_polarity_loss=false，单独输出 needs_review.json，禁止将其作为 neutral 用于监督。所有样本均有记录，但仅格式有效的三分类标签可用于极性损失。

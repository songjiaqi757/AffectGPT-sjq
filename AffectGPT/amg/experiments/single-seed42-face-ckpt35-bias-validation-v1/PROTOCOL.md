# 单偏置有界验证

这轮只回答 Value MLP 最后一层公共偏置是否影响 Memory 内容的利用，不提前实现完整图。

A：使用原 retrieval 已训练 checkpoint，仅推理时清零 value_projection.2.bias，正常/随机 Memory 各500条双卡并行；与原正常/随机/关闭结果配对。旧预测重新计分，不改旧产物。该操作是训练分布之外的机制探针。

B：随后固定执行一次新的 seed42 训练对照。共享一份CPU seed42新建 Adapter 初值；control完整载入，zero_init只清零该偏置，二者偏置均保持可训练。所有 LoRA 都从第35号基线恢复并逐张量验证。其他参数初值、训练设置、4K曝光和长度预算必须一致。这不声称复现旧训练未保存的初始化。

每组1334 iteration、batch1、accum3，最大4002次实际曝光；只取最终 checkpoint。每组最终权重分别正常/关闭/随机推理各500条，生成后保留学到的偏置，不额外清零。自动检查首五步、实际覆盖、完整曝光一致性和初值差异，再执行配对bootstrap及报告。

预先设定 +0.005 microF1 为探索性的实际增益参考，并查看95%配对区间以及正常相对自身随机/关闭的差异；不据内部token敏感性判断任务改进。单seed、多项探索性比较、baseline已见source等限制保留。不会自动扩展31K/HGT或运行holdout/目标评分。

所有产物只在服务器。本任务启动后用户无需等待持续监测；最新状态见同目录 state.json，完成后 SUMMARY.md / summary.json，技术失败见 FAILURE.txt。

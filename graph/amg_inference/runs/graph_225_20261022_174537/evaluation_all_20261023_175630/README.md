# 全部推理结束后自动双卡测评

25 个续训权重 × 9 个数据集，共 225 项推理；全部完成后才启动测评。

- 推理保留现有双卡各 4 路进程，控制器每 60 秒按未完成样本数更新任务优先级，大任务优先，由 8 路共享队列领取，以缩短末尾等待；不打断已领取的任务。样本长度与生成长度不同，不能保证两卡严格同时结束。
- 全局门槛：225 项推理全部成功完成，停止已登记推理进程组，确认两张 GPU 显存已释放并取得独占资源锁，才启动两个测评进程。
- GPU 0、GPU 1 各一个测评进程，各加载一份原版 Qwen25 裁判；领取互斥的共享测评任务，按历史耗时优先处理大任务，不重复测评。
- 直接复用先前 20 × 3 已完成的 60 项测评（校验分数与原始预测的 SHA256），新增测评 165 项，最终共 225 项。
- 使用仓库原版评测函数和标签映射：MER2023、MER2024、MELD、IEMOCAPFour 汇报 HIT；CMUMOSI、CMUMOSEI、SIMS、SIMSv2 汇报 WAF 与 ACC；OVMERDPlus 汇报 F_s、P_s、R_s。最优权重按各数据集主指标选择，附属指标来自相同权重。
- controller.log 与 status.json 记录自动接续；gpu_0_evaluation.log、gpu_1_evaluation.log 及对应状态文件记录测评。
- metrics_all.csv 为全部指标；per_checkpoint_summary.csv / .json 为每个权重九数据集汇总；全部完成后生成 best_original_reporting.json。
- 启动记录 launch.json；预检记录 preflight.json；实际测评门槛记录 evaluation_start_barrier.json。
- 本次未安排新训练。所有脚本、日志、预测及测评结果均留在服务器。

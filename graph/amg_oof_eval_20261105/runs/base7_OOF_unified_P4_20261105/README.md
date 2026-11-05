# 新 OOF 图 + 统一 P4，原始七个 checkpoint

全部操作、代码、输入、日志和结果保存在服务器。图：amg_v2_oof_d837c39aeb0949ca；Prompt：unified_P4_OOF_4444697a94aeeae9。

MER2023 test1 411 条；SIMS test 457 条；仓库 OV-MERD 评测入口 OVMERDPlus 532 条。七个 epoch 30/35/40/45/50/55/60，共 21 组、9800 条推理。原始模型配置、媒体管线和解码设置保持。仅用新图生成辅助 P4 文本，不重新提取 Student Cue、不训练、不额外试跑。

A800/A100 每卡四路，通过共享分片锁分工；逐样本落盘可恢复。推理全部结束且八个进程退出后，A800、A100 每卡一路自动运行原仓库 evaluation.py，保存 21 份 scores、metrics_all.csv、per_checkpoint_summary.csv 和 RESULTS.md。

进度：pipeline_status.json；workers/*_controller.json；workers/A800_*.json 和 A100_*.json。日志：logs/。

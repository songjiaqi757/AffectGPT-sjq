# G组运行入口

current_run.json 指向当前正式运行。
先每卡4路容量验证与推理，全部退出后每卡1个原统一评分进程。
6项任务，总2800条：1718条F的严格匹配回答复用、1082条新生成。
只新增G，已有A-F结果只读；最终RESULTS.md给出全部对比，final_verification.json记录完整性。
查看运行目录下status.json和inference_gpu_*_slot_*.json获取进度。

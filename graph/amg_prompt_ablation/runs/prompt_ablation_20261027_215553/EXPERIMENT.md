# 三数据集固定权重提示消融

运行目录：`/ai/sjq/AffectGPT-sjq/amg_prompt_ablation/runs/prompt_ablation_20261027_215553`  
启动日期：2026-10-27。只做推理及原流程评分，不更新模型参数。

## 实验矩阵

两个固定权重：原始 epoch35；同一起点的十类图 D_newgraph epoch40。
三个数据集：MER2023 411、SIMS 457、OV-MERD+ 532，共 1,400 条。
六组：A 无证据；B Cue；C Cue+Appraisal；D Cue+情绪候选；E 完整字段、原表达；F 与 E 相同字段、显式备选及不确定性表达。
共 36 个任务、16,800 条生成结果，分为 288 个最多 64 条的分片。

原十类图及原 D 门控先冻结，再做字段消融；不因删除字段重新运行门控。所有组均不展示解释路径，E 不是旧历史含路径结果的直接复用。原门控：level3=541、level2=858、level1=1。各组在没有对应可见字段的样本上可能完全相同，这是本次保留原门控的预期行为。

CPU 检查 8,400 个提示，通过；共同预算没有删除任何样本的证据字段。最大 graph tokens=236，最大 prompt tokens=408。

## 解码与配对

保留历史设置：num_beams=1，do_sample=true，temperature=1.0，top_p=0.9，max_new_tokens=1200，max_length=2736。prompt/graph/subtitle 预算为1536/512/256。
逐样本 seed=(42+int(canonical(sample_id)[:8],16)) % 2**32，在所有条件和权重之间相同。单次配对种子不能替代多种子稳健性实验。
F 不增加新状态、候选、分数或路径，只改写相同字段的表达。

## GPU 并行

两张 A800，各 4 个独立推理进程，共 8 路。共享文件锁队列，大数据集/大分片优先。每卡四路同时使用源域样本完成1536输入+1200输出容量测试，通过才处理目标样本。
每个进程可切换两个固定权重；不固定某个条件独占某张卡，所有分片互斥领取。逐样本结果落盘，worker可恢复同一分片未完成的样本；最多三次失败尝试。
使用既有 `amg_finetune_nogc/gpu_0.lock` 和 `gpu_1.lock`，控制器全程持有。

全部推理完成、8个进程退出并确认两卡显存释放后，再启动两个评分进程，每卡一个 Qwen25 judge。评分共享互斥任务队列，不与生成同卡并行。沿用原 evaluation.py、标签、情绪轮、抽取与采样设置。
MER2023同时保存HIT/M和抽取标签数；SIMS保存WAF/ACC；OV保存F/P/R和抽取标签数。

## 文件

- `status.json`：控制器阶段、PID、任务完成数。
- `inference_gpu_X_slot_Y.json`：每路推理状态。
- `probe_accepted_gpu_X.json`：四路容量验收记录。
- `jobs/`、`shards/`：任务与分片状态。
- `predictions/`：逐样本JSON、完整JSONL和原评分NPZ。
- `evaluation_barrier.json`：全部生成完成且显存释放的验收。
- `scores/`、`metrics_all.csv`、`metrics_all.json`：逐任务指标。
- `paired_deltas.json`：预定条件差值。
- `RESULTS.md`：全部36组完成后的汇总。
- `cpu_preflight.json`、`plan.json`、`code_manifest.json`：预检与配置、源码指纹。

`current_run.json` 指向本运行。控制器已脱离SSH会话运行，日志在 `controller.log`。
全部代码与结果保存在服务器项目目录；没有下载至本地。

## 解释限制

这是目标测试集上的探索性诊断，不用于分别挑选每个数据集的提示或checkpoint。对两个权重分别比较提示差异；二者训练历史不同，不能把跨权重差值全部归为图效果。正式结论还需逐样本纠错/伤害、配对不确定性和后续开发集确认。

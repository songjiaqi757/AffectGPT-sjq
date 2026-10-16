# AffectGPT AMG：M0 实施入口

本目录是独立新增实现，服务器目录为 `/ai/sjq/AffectGPT-sjq/AffectGPT/amg`。原训练、推理源码及既有任务没有改动。当前交付是方案第一级 M0 与可供后续 E1 使用的 BGE 文本组件；完整 Situation、本体弱标签、HGT、E1/E2/G3 尚未完成，也没有性能结论。

## 当前行为

- 原 AffectGPT 没有独立文本编码分支：字幕仍放进 Qwen 提示词；训练答案只进入被监督的生成目标，推理没有答案。
- M0 不调用 BGE。冻结 CLIP-768 / chinese-hubert-large-1024 的原隐藏特征按 clip 全局均值，再按模态 L2 归一，双方共同有效模态的 cosine 等权平均，精确 top-5。
- 原 loader 固定采样 8 槽，短视频沿用重复补齐；当前均值沿用全部原槽位，不声称新增了时间 padding mask。
- Memory value 只有冻结 AV 特征，不含字幕、训练答案、目标标签。Adapter 用 4 个 query 压成 4 个 Memory tokens，放在问题段前。
- 训练排除实际读取的 query 自身与 manifest 同组记录，读取失败后重采样会记录 original/actual ID。分组默认只是 clip ID；尚未建立跨 clip 的近重复/同源标注，不能声称过滤了全部近重复。
- `retrieval`、`random`、`current`、`learned`、`off` 分别提供真实邻居、随机邻居、当前 AV、静态 tokens、无 Memory 对照。各模式可统一启用相同 LoRA；原 AV 编码器和投影冻结、eval。实际参数量会记录，各容量对照并非天然等参数。
- 训练和推理共用 `assembly.py`。off 不占用任何 Memory 位置；EOS=PAD 的原监督规则保留。
- BGE-M3 已在服务器 `models/bge-m3`，`text.py` 接口只接收独立字幕/概念定义；BGE 冻结 eval，原生 dense 1024 维，Evidence 投影 256 维。它尚未连接到 M0。

## 数据协议

`artifacts/manifests/main.jsonl` 保留全部 **31,327** 条；已接受的 99 段 OV-MERD+ 重叠未删除。`fit/dev/holdout` 为固定 seed=42 的 4000/500/500 临时开发清单；最终全部回并使用 main。`version.json` 保存来源与输出 SHA256。开发只允许 fit 建库，最终才用 main 建库和训练。OV-MERD+ 的全部 532 段仅用于最终评测，不加入训练、不加入训练 Memory、不参与开发调参或 checkpoint 选择。已接受的 99 段重叠仍作为 MER-Caption+ 原训练样本保留，不从 OV-MERD+ 额外导入任何样本。

## 运行方式

以下命令均在服务器执行，不下载项目或权重到 Mac：

```bash
cd /ai/sjq/AffectGPT-sjq/AffectGPT
AMG_PY=/ai/sjq/miniconda3/envs/vllm/bin/python
AMG_CFG=train_configs/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz.yaml
AMG_BASE=/ai/sjq/AffectGPT-sjq/AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230/checkpoint_000035_loss_0.723.pth
```

`AMG_BASE` 是显式示例共同起点；不要在测试集上选出最优 checkpoint 后替换它。face 与 frame 的 bank、配置、共同起点分别固定，不能混用。

### 1. 建开发 Memory

建库只加载 CLIP 和 HuBERT，不加载 Qwen；失败立即中止，不隐藏跳过/替换。CPU 命令不占用当前两个 GPU 训练任务。

```bash
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 "$AMG_PY" -m amg.build_memory \
  --config "$AMG_CFG" \
  --manifest amg/artifacts/manifests/fit.jsonl \
  --output amg/artifacts/m0-bank-face-fit.pt --device cpu
```

`--limit 2` 只用于冒烟验证。已生成的 `artifacts/m0-bank-face-smoke2.pt` 明确标记 partial，默认训练/推理拒绝把它当正式库。正式全量阶段把 manifest 换成 main，输出另存 `m0-bank-face-main.pt`。

### 2. 先检查训练配置

```bash
"$AMG_PY" -m amg.train --config "$AMG_CFG" \
  --baseline-checkpoint "$AMG_BASE" \
  --manifest amg/artifacts/manifests/fit.jsonl \
  --memory-bank amg/artifacts/m0-bank-face-fit.pt \
  --output-dir amg/runs/m0-face-ckpt35-fit-retrieval-seed42 \
  --mode retrieval --steps 1334 --batch-size 1 --grad-accum 3 --seed 42 --dry-run
```

检查完成后，删掉 `--dry-run` 才会开始训练。设备默认 `cuda:0`，正式启动由下述双卡实验入口调度。当前固定预算为1,334个梯度累积iteration、batch=1、accum=3，名义曝光4,002次。五组均使用seed=42，保持相同数据、曝光预算与PEFT设置，并使用最终checkpoint。

输出目录必须是新目录，且不能位于原 `AffectGPT/output` 下。每步记录 loss、实际曝光量、Memory 启用量、读取替换、梯度范数；保存 LoRA/Adapter 等实际可训练参数及 optimizer、配置与输入哈希。`--freeze-peft` 时整批 Memory 被丢弃可能没有梯度，此步不执行优化且明确记录 `no_update`。不支持精确中途续训；不会把缺失 sampler/worker 状态的恢复伪称为完全可复现。

### 3. 开发推理

```bash
"$AMG_PY" -m amg.infer --config "$AMG_CFG" \
  --baseline-checkpoint "$AMG_BASE" \
  --amg-checkpoint amg/runs/m0-face-ckpt35-fit-retrieval-seed42/checkpoint_001334.pth \
  --memory-bank amg/artifacts/m0-bank-face-fit.pt \
  --manifest amg/artifacts/manifests/dev.jsonl \
  --output amg/runs/m0-face-ckpt35-fit-retrieval-seed42/dev-predictions.jsonl \
  --device cuda:0 --task ovlabel --dry-run
```

删掉 `--dry-run` 才生成，`--task description` 可生成解释。保存 prediction、retrieval trace 和版本元数据。推理仅读 manifest 的 name/subtitle/group_id，媒体失败记原 clip 并返回失败状态，不换样本。`--memory-mode off` 可在同一个增强 checkpoint 上做推理关库诊断；它不能替代统一预算另行训练的 off 对照。

推理 CLI 支持默认 `--dataset MERCaptionPlus` 与 `--dataset OV-MERD+`；目标媒体路径按原项目映射，OV 人脸使用平铺 `<name>.npy`，source 使用 `<name>/<name>.npy`。仅供评测调用的输入清单为 `artifacts/manifests/ovmerdplus-observed.jsonl`，共 532 条（22 条空字幕），只保存 ID、字幕、group_id；它只作为评测 query 的输入，不作为训练或建库输入，没有读取目标标签。此前仅做了输入格式/媒体路径验证，未用于训练或选择方案。最终评测时用全量训练产生的 checkpoint 和 main Memory，将上面命令的 manifest 换成该观测清单并加 `--dataset OV-MERD+`。完整目标生成与原指标解析评测尚未执行；本轮source五组状态见下文，其他benchmark的媒体入口尚未接入。

## 验证与状态

```bash
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 "$AMG_PY" -m unittest discover -s amg/tests -v
```

完整CPU测试套件 **124 项全部通过**（Ran 124 tests in 4.832s，OK，TEST_RC=0），记录位于 `artifacts/single_seed42_unit_tests.log`。检查覆盖检索过滤、缺失模态、生成损失反传、真正off、EOS/超词表AV占位符、独立字幕、数据对齐、曝光审计、长度预算、评测分母及双卡调度器。

完整fit Memory已经生成：`artifacts/m0-bank-face-fit.pt`，4,000条、`complete=true`。其内容来自冻结CLIP/HuBERT的AV隐藏特征，独立于基线LoRA权重，可复用于当前共同起点。Memory和manifest校验通过后才允许正式实验使用。

第35号共同起点的CPU兼容校验及124项完整测试已经通过。五组真实GPU训练、最终checkpoint保存重载、各500条dev生成及7项配对评测已全部完成，state.json为complete，完成时间为北京时间2026-10-15 22:52:30。每组1,334个iteration、1,332次有效更新（2次AMP溢出跳过），覆盖全部4,000个fit ID、实际曝光4,002次；完整曝光对齐通过，各组dev零失败。完整研究分支、全31K建库/正式训练和最终目标评测尚未完成。现有face/frame训练任务继续运行。源码、权重、清单、日志及测试输出均只保存在服务器。

## 当前单seed执行

当前固定为seed=42，五组均从以下共同起点开始：

`/ai/sjq/AffectGPT-sjq/AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230/checkpoint_000035_loss_0.723.pth`

固定协议：`/ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-v1/protocol.json`；状态：同目录`state.json`；启动日志：`pipeline.log`；已生成`SUMMARY.md`和`summary.json`。协议保存基线SHA-256以及输入、资源和源码版本。全部产物仅在服务器。

```bash
cd /ai/sjq/AffectGPT-sjq/AffectGPT
/ai/sjq/miniconda3/envs/vllm/bin/python -m amg.run_experiment \
  --protocol /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-v1/protocol.json \
  --output-dir /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-v1
```

本轮已由物理GPU 0先运行`off`、GPU 1先运行`retrieval`，空闲卡接续完成`learned/current/random`。每组前五步的真实更新验收均通过，记录在各组`first-five-validation.json`。每组的训练与dev生成占用同一个调度槽，最多两个新增GPU任务并行。dev生成也由两个槽并行推进；全部预测生成后，CPU配对评分最多同时两组。GPU子进程通过`CUDA_VISIBLE_DEVICES`绑定单卡，进程内设备为`cuda:0`。原有face/frame训练继续运行。

五组均为1,334个梯度累积iteration、batch=1、accum=3，名义曝光4,002次；只使用`checkpoint_001334.pth`，不按dev或目标集挑选checkpoint。训练使用fit 4,000条及完整fit Memory；dev 500条用于开发评分，holdout和目标集不参与当前调参。

训练输出`exposure.jsonl`和`coverage.json`，分别记录每microstep实际曝光与逐ID覆盖。共享预算含BOS/EOS、Memory和生成预留，字幕截断量可追踪。source开发评分示例：

```bash
python -m amg.evaluate --manifest amg/artifacts/manifests/dev.jsonl --split dev \
  --predictions RUN/dev.jsonl --output RUN/dev.metrics.json
```

该指标为source normalized开放情绪集合microF1/sample macroF1，与原九基准EW指标分别报告。同seed配对加`--paired-report OFF/dev.metrics.json`，bootstrap仅反映此seed下的样本不确定性，不能估计跨训练seed方差。固定资源在`amg/resources/source_evaluation_v1.json`，仅来自fit标签和明确词形别名。

本轮source dev microF1：off 0.464437，retrieval 0.460784，current 0.459680，learned 0.458374，random 0.457031。retrieval相对off差值为−0.003652（−0.3652个百分点），95%配对bootstrap区间为[−0.016927, 0.008111]，跨0；相对其余三组的区间也均跨0。当前没有支持检索Memory性能收益的证据。该结论仅对应seed42的4K开发实验，不是论文EW或最终目标集成绩。详细结果见`amg/experiments/single-seed42-face-ckpt35-v1/SUMMARY.md`。


同checkpoint推理干预已于北京时间2026-10-16 00:51:16完成：同一份retrieval训练后权重，正常检索46.0784%、关闭Memory46.3749%、随机Memory46.0733% micro-F1；三种设置各500条、零失败，三项配对区间均跨0。正常检索与随机Memory的标签集合491/500一致。报告与112条CPU错例分析位于服务器`/ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-intervention-v1/`，详见`SUMMARY.md`及`INTERPRETATION.md`。这是固定权重的推理干预，与此前五组独立训练对照分开报告；未新增训练、未改标签映射、未运行holdout/目标集，完整图/HGT尚未实现。


已启动真实dev AV/Adapter敏感性诊断，目录为服务器`/ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-sensitivity-v1/`。CPU bank审计已完成：normal/random在498/500条query上top5完全无交集，原始AV向量有较强共同方向；该几何观察不能直接判断Adapter或LLM原因。新增后台任务仅冻结CLIP/HuBERT与已训练Adapter，无Qwen、文本生成或训练；GPU0/1各处理250条，自动聚合真实query、attention、token差异及重放一致性。最新状态见state.json，完成后生成SUMMARY.md和summary.json。按用户要求启动后不全程监测；原源码、权重和评分资源保持锁定，所有产物只在服务器。


Adapter机制CPU审查已完成，报告在服务器`/ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-adapter-audit-v1/FINDINGS.md`。500条真实query显示Value MLP末层公共bias约为Wx信号范数4.46倍，明显降低相对邻居对比度；Q/K跨邻居logit差约2e-5，attention近似均值聚合。FP64与手算已排除显示/softmax维度错误；最终optimizer显示选择性通路任务梯度极弱。公共偏置不消除绝对差值，共同K偏移不直接造成softmax均匀，尚不能反推唯一训练原因。内部去偏置探针不等于任务收益；未改模型、未启动新训练/生成。


## 单偏置有界验证（2026-10-16）

已启动后台流水线，当前进度以服务器 /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-bias-validation-v1/state.json 为准；启动检查为同目录 launch-validation.json。142项CPU测试通过，67项输入/源码/启动器锁通过。原face/frame训练继续运行，所有新产物仅在服务器。

先对原retrieval已训练checkpoint推理：只清零 memory_adapter.value_projection.2.bias，GPU0正常检索、GPU1随机检索各500条，旧正常/随机/关闭预测用当前同一评分器重算后配对。该操作是训练分布之外的机制探针。

随后固定运行一对新的seed42/4K训练，不依据阶段A成绩决定是否跳过。两组共享一份CPU新建Adapter初值，LoRA均严格恢复第35号基线；control保留初值，zero_init只清零value末层偏置，二者偏置都可训练。这不复现旧实验未保存的Adapter初值。其余初值和训练设置一致，每组1334 iteration、batch1、accum3，实际曝光需4002次且覆盖全部4000条；自动比较逐张量初值和完整任务/clip/预算曝光，首五步检查真实更新。

每组训练后分别正常/关闭/随机推理各500条，保留最终学到的偏置。自动运行11项配对评分并汇总最终偏置和标签集合差异。固定探索性实际增益参考为+0.005 microF1，结合配对95%区间和内容对照判断；bootstrap不代表跨训练seed稳定性，多项比较未经族错误校正。完整说明见同目录PROTOCOL.md；完成后生成SUMMARY.md/summary.json，技术失败写FAILURE.txt。不会自动扩展31K、HGT或运行holdout/目标评分。按用户要求，启动验证后结束本轮，不持续监测。


偏置验证续跑记录（2026-10-16）：两组seed42训练均完成，各1334 iteration、1332有效更新、4002实际曝光、覆盖4000条，共同初值审计通过。原流水线因off trace的retrieved_ids为null触发校验迭代错误而停止；模型与推理本身未因此改动。现仅修复这一行校验并新增3项回归，完整145项CPU测试通过。原失败记录、495条control/off不完整输出和全部权重保留。新恢复目录为 /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-bias-validation-v1/recovery-v2/ ，当前状态见该目录state.json。复用完整zero_init/off500及两组retrieval；GPU0补跑control/off再random，GPU1补跑zero_init/random，后续自动完成配对报告，不重新训练。新的121项输入/代码/输出锁已验证。完成报告改为恢复目录的SUMMARY.md、summary.json，父目录state.json保留原失败事实。


偏置验证最终结果（2026-10-16）：恢复流水线于北京时间2026-10-16 11:50:01全部完成，恢复目录state.json为complete。全部12个计分条件（含复用参考）各500条、零错误，11项配对评测完成；两组训练实际4002曝光、覆盖4000条及共同初值审计均通过。报告位于 /ai/sjq/AffectGPT-sjq/AffectGPT/amg/experiments/single-seed42-face-ckpt35-bias-validation-v1/recovery-v2/SUMMARY.md ，独立完成检查为同目录completion-validation.json。

Stage B普通初始化：正常检索45.9177%、随机46.0183%、关闭46.5298%；零偏置初始化：正常检索46.3550%、随机46.2292%、关闭46.6102%。zero正常减control正常为+0.4373个百分点，95%配对CI[-0.0724,+1.0020]，跨0且未达预设+0.5个百分点参考。zero正常减自身off为-0.2552个百分点，CI[-1.2040,+0.7354]；减自身random为+0.1258个百分点，CI[+0.0145,+0.2993]，是很小的单seed样本信号，不代表总体Memory增益。两组正常/随机标签集合均495/500一致。最终bias范数control0.54759、zero0.00484；初始去偏置保留了很小的可学习bias，但未证明任务性能受益。Stage A推理直接清零相对原正常检索为-0.2111个百分点、CI跨0。

结论：该有界试验未通过预设扩展条件，不据此继续增加图复杂度或全31K训练预算；也不能宣称所有检索方法无效。当前只有seed42，区间仅反映样本不确定性，多项探索比较未做族错误校正，source开发集已被共同基线见过；不能作为正式目标或九benchmark成绩。当前未启动新研究任务，holdout和目标集未评测，原失败及不完整预测仍保留。

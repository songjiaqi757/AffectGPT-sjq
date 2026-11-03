# Cue 标注实现与 Student 训练准备审查（2026-10-20）

审查位置：/ai/sjq/AffectGPT-sjq。仅在服务器检查并保存本报告与统计证据；未修改方案.md、标注、Prompt、模型权重或训练代码，未调用收费 API，未启动训练。

结论：已有标注可以作为三路 Student 的伪标签来源，42 维独立输出和 masked BCE 的方向正确，无须因本次训练准备重新全量标注。但现有 AffectGPT 训练入口不是 Cue 分类训练入口，方案仍需补齐执行细节，并修正文内冲突。当前不等于训练数据发布验收完成，也不等于人工语义质量通过。

## 1. 实际实现与验证范围

- annotate_full.py:122–160 从 track2_train_mercaptionplus.csv 只读取成员 name，字幕从 subtitle_chieng.csv 分别读取 chinese/english；同一模型执行 text/audio/visual 三个隔离任务。没有将 openset/reason 加入标注输入。
- annotate_api.py:38–48 校验 sample_id、modality、完整 Cue 集合、四状态及证据字段；65–83 构造完整 16 kHz 单声道 PCM16 WAV；86 起构造完整静音视频，保留范围与历史哈希。Teacher 视频内部抽帧不可见，不构成逐帧人工真值。
- annotate_full.py:158–163 保留模型 annotation；321–337 按本体导出长表，positive/negative 映射为 y=1/0、mask=1，其余为 y 空、mask=0。停顿和流泪统一按原始标签处理。
- 当前全量 CSV 的 1,315,734 个 sample_id/modality/cue_id 键全部唯一且属于预期集合，映射错误为 0；78 个 unlabeled 模态任务与只读数据库查询逐键一致。
- 固定种子 20261020 抽查 30 个样本、90 份成功 JSON，身份及 Cue 集合无错误；这是结构抽查，不是全部 JSON 与原始 Teacher 响应逐项复验，更不是人工语义审计。
- labels.csv、samples.json、ontology.json、protocol.json 的本次 SHA256、逐 Cue 计数、分词及媒体时长统计见同目录 training_readiness_evidence_20261020.json。该文件是审查快照，不冒充正式 release manifest。

| 模态 | 成功任务 / 31,327 | positive | negative | mask=0 位置 | mask=0 比例 |
|---|---:|---:|---:|---:|---:|
| Text | 31,323 | 62,136 | 387,441 | 20,328 | 4.33% |
| Audio | 31,322 | 68,128 | 306,857 | 157,574 | 29.59% |
| Visual | 31,258 | 66,404 | 219,782 | 27,084 | 8.65% |

78 个失败模态分别为 text 4、audio 5、visual 69。失败只屏蔽对应模态/Cue，不删除其他有效模态。

## 2. 训练前必须落实的修改

### 2.1 新增独立 Cue 训练链路，不能只改原 YAML

现有 AffectGPT/my_affectgpt/datasets/datasets/mercaptionplus_dataset.py:37–84 读取 openset、reason 和 english；AffectGPT/my_affectgpt/models/affectgpt.py:720–729 将 token labels 交给语言模型并返回生成损失。现有 train.py / mercaptionplus_frame_gpu1.yaml 没有把 labels.csv 转成 15/17/10 维 y/mask，也没有三路 Cue 分类头。

建议新增 cue_student/（待实现）负责数据验收、划分、三种 Dataset、模型、训练和评估；复用现有编码器权重，而不是照搬 Qwen/LoRA/Q-former 训练框架。训练输入只包含实际文本/媒体，evidence_note、Teacher state/mask、openset、reason 均不得作为预测特征。

数据适配器按 ontology.json 的数组顺序输出 float32 targets 与 bool label_mask，不能按 CSV 偶然行序或字符串排序固定头维度。先将 mask=0 的 y 填成有限占位值，再计算逐元素 BCE 并取有效项；不要对 NaN 先算 BCE 再乘 0。模态缺失和时序 padding 分别使用独立掩码。

### 2.2 修正双语协议冲突，显式处理缺失字段

方案.md:562 的“原文优先、英文回退”与 :580 的“双语分别编码并聚合”不一致。当前 Teacher 明确读取两个字段，且某个词面 Cue 可能只在英文译文出现；仅给 Student 中文会产生输入无法解释的监督。

建议将第 5.3 节源域规则改为：源域始终沿用 samples.json 的 chinese/english 两个独立字段，各自编码后聚合；缺失字段使用 language_present mask。全量中文均非空，英文有 588 条为空，不能把空串当一个有效英语句子参与等权平均。单语输入或固定翻译输入应作为另外登记的推理协议/消融，与主双语协议分别报告。

词面存在性与语义判断的聚合应允许区分：可以从任一语言读取词面证据，但不能把翻译重复累加，也不宜对全部 Cue 无条件取两语言最大值来代替语义冲突处理。先使用共享 mBERT + 语言掩码 + 可学习融合的简单实现。

方案所要求的 text_source/is_translation 等元数据并未全部存在于 samples.json；须从可靠来源补登记，未知项标 unknown，不凭字符串自动编造原始语种或翻译 provenance。

### 2.3 在样本级聚合后监督，不向每帧/每块复制标签

Teacher 给的是“样本内至少出现一次”的弱监督。对整条阳性样本的每帧、每音频块都强制 y=1，会把没有事件的局部内容当成阳性证据。

正确路径是：局部表征 -> 带有效时间掩码的样本级聚合 -> 15/17/10 个 logits -> masked BCE。事件 Cue 可以比较逐 Cue attention / Top-k；保留 mean pooling 基线。需要顺序的语调保留时间顺序或小型时序模块。Teacher 的 evidence_note 及未经人工验证的近似时间戳，不直接转成帧级强监督。

### 2.4 划分和发布适配器必须先落地

现有 samples.json 只有 sample_id、text、audio_path、video_path；已检查的源 CSV 也没有可信 video_source_id。现存 run 目录无正式 split/audit/release 文件。不能直接 random_split 后声称无同源泄漏。

先核实来源组；无法恢复时登记限制，至少进行可复现的媒体重复/近重复检查，得到的是重复簇而非已证实的原视频身份。固定统一的样本/组角色清单，各模态共用角色，再按有效监督使用数据；隔离未来 300 条审计样本及可识别同源组。可在排除审计组后以约 90/10 分组划分伪训练/验证作为起点，记录每类各划分的正负支持数。

重新生成训练发布 manifest，登记本体顺序、文件哈希、标签映射、来源与划分版本，以及已知失败。无需修改或重新标注现有 78 个失败来凑完整数据。没有人工金标准时可以在预留审计角色后做工程基线，但只能报告对 Teacher 伪标签的拟合程度，不能宣称对人类真值的准确率。

### 2.5 训练读取原始媒体，不能依赖已清理副本

原 runs/mercaptionplus/media/audio 和 media/video 已清理，inputs 里的 submitted_*_path 是历史事实，不是当前训练数据路径。Dataset 应从 samples.json 的原始 audio_path/video_path 读取，执行受版本控制的转换。

音频沿用完整 16 kHz/mono，保留真实时长；可以在内存中完成重采样，不必恢复全量 API 副本。视觉只解码视频流，不读取音轨。若保存特征缓存，只保存在服务器，key 包含源文件/编码器/预处理哈希及时间位置，不能只以 sample_id 命名后混用不同版本。

## 3. 根据本次实际数据可简化的设计

### 3.1 Text：首版长度 128 足够覆盖当前源域

用已有 mBERT tokenizer 离线统计（含特殊 token）：
- 中文 median 13、p99 38、max 109；
- 英文 median 14、p99 41、max 101；
- 两种语言均无超过 512 tokens 的样本。

因此首版可采用 max_length=128、动态 padding，减少无效计算；仍检测 overflow 并为后续长输入保留确定性分块回退，不能静默截断。无需首先投入大量工作实现当前源域用不到的文本分块架构。

### 3.2 Audio：完整编码为首选，分块作为回退

31,327 条输入元数据：median 2.761 秒、p95 6.584 秒、p99 10.105 秒、max 26.912 秒，超过 20 秒仅 5 条，总计约 28.91 小时。服务器两张 A800-SXM4-80GB 在检查时均无显存占用。

优先尝试完整音频编码，按总采样点/时长分桶控制 batch，动态 padding 并将有效采样长度转换为编码后有效帧 mask。原 ImageBind/data.py:170–213 的“8 个 2 秒片段 + 短音频补到 2 秒”不应复用。

若微调时确需分块，覆盖完整时间轴，记录起止位置与有效长度，并处理重叠区；不能将补零或块边界计为停顿。当前 HuBERT 特征提取器 do_normalize=true；各块独立归一化可能消除块间相对音量。遵循预训练输入处理，同时从归一化前波形保留完整时间轴的能量/F0/VAD统计作对照，勿声称 HuBERT 表征必然保留全部相对声学证据。多说话者时，全文件 F0 均值不等于同一说话者基线。

### 3.3 Visual：时间覆盖之外，还要验证空间证据

视频 max 26.92 秒、p99 10.095 秒。2 FPS 或 4 FPS 的完整时段确定性采样是可执行的首版候选，需包含首帧/最后可解码帧，去除重复索引，并保存实际 PTS。不要为固定 batch 只保留最前面若干帧；长输入可分批编码后聚合全部帧。

现有 CLIP preprocessor do_center_crop=true、crop_size=224；多数原视频是宽屏，全画面中心裁剪可能丢掉边缘人物。先冻结空间预处理并检查覆盖，比较全画面保比例缩放补边与默认中心裁剪；必要时把面部/上半身多区域作为后续独立消融。样本级“任意主体”语义不能静默变成“中央人物”。低分辨率眼部细节也可能不足，流泪标签继续普通监督，不新增人工阳性门控。

## 4. 损失、验证和 AMG 接口建议补充

- 保留普通 masked BCE 基线。加权实验中 pos_weight 只由 pseudo_train 内有效正负例计算，记录裁剪/平滑规则；正例为 0 时禁止除 0。不要一开始同时叠加强过采样、大正例权重和 focal。
- 不平衡是真实存在的：频繁停顿 positive 197、笑声 378、哭泣 387、相对高音高 411、自身归因 458、成功结果 508、流泪 902。频繁停顿 mask=0 为 56.22%，相对高音高为 67.00%。不据此改标签或直接删除 Cue，但必须逐类报告支持数、PR-AUC、覆盖率和区间。
- checkpoint/早停规则应预先固定，例如固定可评估类集合上的 pseudo-validation macro PR-AUC，masked validation loss 辅助；没有正例的类记为不适用并列出，不能悄悄按不同 checkpoint 改变平均集合。伪验证指标明确标为 Student–Teacher。
- Teacher mask 不是推理输入；它只控制监督。Student–Human 评估依据人工参考的有效状态，不能仅保留 Teacher 有信心的样本而隐藏 Teacher 的不可判定区。
- 推理输出除 score 外，应保存 modality_present、实际预处理版本和输入有效性信息；缺失媒体不能输出伪装成正常预测的全零向量。mask=0 训练项未被要求学成 negative，也不保证分数在不可观察人群上已经校准。
- 多 GPU/DDP 如果使用有效标签数归一化，要核对全局分母；某 rank 全 mask 的 batch 不能单独跳过而让其他 rank 继续同步。本首版可先每个 Student 单 GPU 独立训练，避免过早引入该复杂度。
- 方案第 4.2.1 节按来源组均衡取样，却在第 4.3 节称自然样本分布评估，两者不自动等价。保留组均衡抽样就标明对应评估总体；若要估计样本自然分布，应采用相应抽样或登记纳入概率并加权，置信区间考虑来源组相关。
- 300 条随机审计预计只含约 1.9 个频繁停顿伪阳性，无法支持该类稳定的五折阈值校准；沿用“支持不足则不作稳定结论”及独立稀有 Cue 诊断集。使用 Teacher 状态估计的该数量仅用于预算，不是人工真阳性数。
- 第 9 节源域训练样本 OOF 建库需要额外训练折模型，区别于第 5 节“只对阈值交叉拟合”。先完成三路单次基线，再规划 K 折 OOF。保存各折 checkpoint 与来源关系；最终全量 Student 和 OOF Student 并非同一个权重文件，需比较表示/校准差异并明确建库版本。

## 5. 推荐执行顺序（均为后续，当前未执行）

1. 实现发布验收与 Dataset；冻结角色清单、审计隔离、Cue 顺序及源文件引用。
2. 对三种模态各跑小批次完整 forward/backward 检查：维度、finite loss、mask、变长 padding、缺失英文、部分模态失败、长短边界；确认能在小训练子集降低损失。
3. 第一轮主基线：Text 共享 mBERT 双语融合并微调；Audio/Visual 先冻结 HuBERT/CLIP，训练样本级聚合器与分类头。冻结编码器必须 eval 模式且缓存无随机增强。
4. 以同一 pseudo-validation 比较普通/加权 BCE、mean/事件聚合，再决定是否解冻音视频编码器最后若干层、加入声学特征或视觉区域。学习率、epoch、patience、有效 batch、精度、随机种子须写入真实配置；不能沿用生成式训练的 60 epochs × 5000 iters 而不按实际成员数解释。
5. 完成人工审计和独立阈值评估后，冻结 active/deferred、阈值与模型版本，再做 OOF Memory 和 AMG 接入。

运行环境现有 torch 2.4.0+cu121、transformers 4.49.0，检查了所需模块的可发现性；mBERT tokenizer 已实际离线加载。三个编码器权重目录存在，但本次未完整加载三个模型做 forward/backward，不能据目录存在就声称训练已可运行。

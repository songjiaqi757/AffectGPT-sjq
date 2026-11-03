# Emotion 节点：原版 AffectGPT 映射基线

本次仅在服务器执行，未调用模型、未占用GPU、未更改正在运行的Appraisal进程。

当前生效划分取消了诊断预留，原200条全部并入训练集；历史版本保留以供追溯。
当前数据发布由 cue_student/artifacts/current_release.json 指定，Emotion产物由 runs/current.json 指定。
本次仅重算映射与支持数，没有调用模型或重训Cue checkpoint。

## 原版流程与实际复用

1. 原版 reason_to_openset_qwen() 根据description提取open-set情绪列表；已核查原始prompt，但本次不需要重新提取。
2. 当前官方 track2_train_mercaptionplus.csv 已提供open-set标签，原版MERCaptionPlus_Dataset直接读取该文件。本次与track3描述、Cue全源manifest核对31,327个唯一ID完全一致，再筛选当前严格release的31,255条合格样本。
3. case1使用format.csv归一词形；case2继续通过synonym.xlsx的8轮同义词资源映射到canonical词。
4. case3分别使用wheel1至wheel5的层级映射；原版M-avg默认平均五套level1评测。本次同时保留五套level1/level2结果。
5. 映射函数直接来自原版源码，经AST只加载已核查的纯函数，避免原版模块导入时加载模型或API依赖。未重写原版映射算法，未使用自定义语义别名。

## 字典序与丢弃的含义

原版func_backward_case2先对format候选排序取第一个，再对该分支的synonym候选排序取第一个。这保证重复运行结果一致，不利用当前样本语境选择意义。
真实例子：anxiety的词形候选为anxiety/anxious，先取anxiety，再按资源映射成fear；concern映射为care。pessimism与neutral没有format词条，会从映射输出略过。
丢弃不修改原CSV、不代表neutral，也不代表样本中该情绪不存在。每个词的候选、所选分支和丢弃原因完整保留。
空标签列表仍为空。原数据集训练读取器有空列表补neutral的分支，但原版Wheel映射仍会丢弃不在字典的neutral；本任务直接复用映射函数，不凭空新增neutral节点。

## 本次产物

- 31,255条合格样本全部处理，0次模型调用。
- 只用27,879条pseudo_train发现并冻结188个EmotionConcept，ID按canonical词内容哈希生成。
- pseudo_train中27311条映射非空；568条映射为空。
- pseudo_validation共3,076条，映射非空3,003条，其中2条有训练词表外canonical结果；仅记录OOV，不扩展节点。
- 共111,481次原始标签词出现，16,507次被原映射略过（14.81%）。
- 词形资源7,386个输入形式，同义词资源1,255个输入词，五轮词表联合含253个候选词；正式候选节点不是预填253个，而是训练分区实际出现的188个。
- 标签来源为官方已提供的open-set表；其历史提取模型版本未提供，不能声称这些官方标签由本次Qwen调用产生。

## 图使用边界

本次按对话要求生成完全原版映射的独立基线；它保留字典序消歧及词表外丢弃，区别于图构建.md第3.3节原先建议的语义核验。该差异在protocol.json中明确记录，本次已修订图构建.md中的数据角色；Appraisal冻结文档保持历史快照。
图节点仅由pseudo_train发现；pseudo_validation、gold_audit不能扩展本体或参与正式边统计。
按原版兼容行为，部分词被丢弃但仍有canonical标签的样本保留；全映射为空的样本mask=0。原版未映射不能解释为真实心理负类。
五套Wheel是平行评测视图，不合并为唯一父类。原版直接对raw标签做case3，与先做case2再对canonical做case3通常不等价；两者均保留并统计差异。复现原版Wheel评测时必须使用样本中的raw-label case3结果。
这里只生成节点、标签和映射视图，尚未构建Cue/ Appraisal/ Emotion统计边，不能称为图已完成或证明了情感识别准确率。

## 文件

- runs/affectgpt_original_v1_no_diagnostic/nodes.json、nodes.csv：188个训练集节点及支持数。
- labels.jsonl：每样本raw/case1/case2、五套case3、逐词候选及丢弃轨迹。
- labels.csv：便于对齐Cue和Appraisal的样本级canonical标签与mask。
- mapping_decisions.csv：全部3,345个观测词的原版分支、词频与丢弃原因。
- mercaptionplus-emotion.csv：与当前合格release一一对应的官方原始open-set标签副本。
- validation_oov.json：验证集OOV，未扩展节点。
- source_functions/、resources/、protocol.json：原版代码和资源快照、哈希及版本。
- verification.json：31,255条、62,510个case1/case2输出和312,550个Wheel输出逐项对照原版。
- summary.json：覆盖率、丢弃和各分区计数。

## 重复核验

在服务器项目根目录执行：

    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python emotion_nodes/verify.py
    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m unittest discover -s emotion_nodes/tests -v

不会调用模型。已经存在的冻结run禁止直接覆盖；策略变更应使用新的版本目录。
现有Cue release的原始来源组及近重复隔离限制继续保留。

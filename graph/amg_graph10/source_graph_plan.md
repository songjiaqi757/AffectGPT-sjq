# 十个Emotion节点的独立图版本
按用户确认的十节点方案，只构图和CPU统计验证，不启动训练、模型推理或基准测评。
Emotion先从原始openset标签分别运行AffectGPT原始case3/wheel1..5/level1，再取并集并执行显式同义合并。
固定节点：anger,disgust,fear,joy,sad,surprised,peaceful,powerful,bad,genius。
genius保持原wheel4资源中的原名。此同义合并是图本体附加层，不修改原版测评映射和词表。
逐样本多标签去重，空映射全部Emotion列mask无效，不转换neutral或全负例。
仅使用现有pseudo_train 27679个单例组计算全部边和三元联合支持；pseudo_validation 3076只做结构诊断。
不使用gold_audit/diagnostic_reserved/目标数据集。Cue42与Appraisal16标签、6维mask不变。
固定支持门槛20、三元联合支持5，沿用原图1000次bootstrap、NPMI正CI下界、完整关系族BH q<0.05规则。
不做阈值搜索。图表示标注关联，不作因果解释；原始来源和近重复独立性、人工审核限制沿用。
独立package和current指针保存，旧图和所有训练/推理结果不变。

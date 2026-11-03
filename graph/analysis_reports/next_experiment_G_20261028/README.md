# 下一轮最小实验：G组
状态：仅准备方案与CPU提示预览；未启动GPU、未改历史配置或结果。
服务器：/ai/sjq/AffectGPT-sjq。

## 第一轮只新增G
G=Cue+F风格软表达Appraisal，不含Emotion，不含解释路径。
从已冻结F提示中仅删除Tentative emotion alternatives行；保留Cue、每维原状态及OR、unresolved/tentative、mixed-affect说明和原门控。
不能同时更换图、Cue阈值、TopK、Appraisal状态、解码或评分。

固定base35和graph40，固定MER2023(411)、SIMS(457)、OVMERDPlus(532)，沿用同一样本随机流。
形成6项完整对照、2800条回答。CPU核对859/1400条G/F证据文本相同；逐权重验证完整prompt ID、权重SHA、种子、媒体与生成参数相同后可复用F的1718条回答，仅需新增1082条生成（每权重MER154、SIMS159、OV228）。A/B/C/E/F已有结果引用而非重跑。
评分沿用已统一流程，不列为待修问题。

比较：
G-B为Appraisal是否有净增量；
G-C隔离平铺/软表达；
G-F隔离情绪候选的移除；
G-A为相对无证据的总收益。
MER报告HIT/M及预测集合规模；SIMS报告WAF和正负类召回；OV报告F/P/R。所有比较按样本配对。

## 决策
一次配对流只作机制筛查，不能将偶然小幅提高当采用依据。
若G不胜B，则不增加同类Appraisal训练；Cue-only/无证据保留为候选基线。
若G有正向信号，则预先固定A/B/C/G及参数，用配对生成重复和未参与调参的开发材料确认；查看G-B跨seed方向、配对区间及其他任务的系统退化。
若只有OV受益，应如实限定任务范围，不将三测试集各自最优拼为统一新模型。
如需干净泛化结论，三集已反复检查不能再当未见开发集；应使用新保留材料或重建严格划分。

## 图比较与训练
只有在Appraisal内容显示增量后，再在共同Cue、本体、格式上比较语义规则关系与统计关系。
不要直接替换旧JSON：旧valence与新goal congruence并不同义；共同节点必须逐项确认。
若进入训练，先补同epoch35、同25000步、同样本顺序、同lr1e-5、batch3、同优化器恢复和0.1极性辅助的无图续训。用以分离训练时间与图的贡献。
后续改lr或生成监督均另设对照，避免一次改变多个因素。

plan.json为配置和任务预算；prompt_examples.json为从实际冻结提示构造的G示例。

# 原188类图证据干预

所有操作和文件均在服务器 /ai/sjq/AffectGPT-sjq。
固定75.4334%对应的各集赢家；五组主对照A-E，另加P原始完整提示锚点。只做推理和评分，不训练、不构图。

A：无证据；B：Cue；C：Cue+Appraisal；D：Cue+Emotion；E：两者都有、无路径；P：原完整提示、含原保留路径。
当前测试集已用于分析，本轮仅作机制诊断。研究顺序与开发集准入要求见运行目录中的EXPERIMENT.md、research_program.json。

运行状态：current_run.json指向运行目录，status.json记录阶段；RESULTS.md在完成后生成。
启动控制器使用服务器vllm环境的python -B -m amg_188_audit.controller --run 运行目录。
控制器独占现有两张GPU的项目锁，四进程/GPU先做源样本满窗口容量验证；全部推理退出后才加载评分模型。

评分保留原指标/词典/提示和temperature等，新增按唯一内容固定随机种子和缓存，单列新协议结果；历史原协议锚点保留。

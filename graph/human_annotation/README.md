# AffectGPT 500 样本人工标注工作台

所有代码、原始媒体、人工标注、缓存、导出和测试均在服务器 `/ai/sjq/AffectGPT-sjq/graph/human_annotation` 处理，不将项目或样本留存本地。浏览器不使用 localStorage / IndexedDB；响应为 `Cache-Control: no-store`。

## 当前规则：只确认存在的标签（2026-10-27）

`annotation_policy=positive_confirmation_v1`，取代原先要求补齐 48 个节点及证据的规则。

- 固定 500 条：现有 release 中 300 条 gold_audit + 200 条 diagnostic_reserved，不重新抽样。
- Cue：文本 15、音频 17、视觉 10。人工只勾选 `positive`；不必选择 negative / uncertain / unobservable，不要求逐项填满。
- Appraisal：6 维、16 个状态。只选择能确定的状态，每个维度都可留空，不要求无效原因。
- 证据、模态说明、事件概述与备注均选填；标注人默认 1。
- 可以只确认一个标签就保存或提交，也可提交零个确认项，表示该样本已复核但没有确认的 positive。
- 留空以 `state=null` 保存，Appraisal 同时 `valid=null`，不补成 negative 或 invalid。
- 左栏 Qwen 原始状态及证据继续直接读取 teacher_raw；不覆盖原始模型结果，不修改训练集划分。

停止编辑 1.2 秒后自动保存草稿；切换前等待保存。提交后进入下一条。已提交记录再编辑会保存成草稿。刷新恢复服务器数据。revision 防止并发覆盖，workspace_epoch 防止清零后的旧页面重新写回草稿。清零或规则变化后必须刷新页面。

## 导出和计算

导出按钮仅在服务器 `exports/` 生成文件：

- JSONL：保存人工确认项、留空字段、状态、来源及原始 Qwen 内容，便于追溯。
- CSV：只含人工确认的 positive Cue 和选定的 Appraisal 状态；行上保留 draft / submitted。
- `*.positive_comparison.json`：按已提交样本计算确认标签集合的 precision、recall、F1。草稿和未开始样本不参与计算。

计算实现为 `positive_scoring.py`，口径 `positive_set_comparison_v1`。每个已提交样本分别构造人工 positive 集合 H 和 Qwen positive 集合 T；Appraisal 使用 `维度=状态` 作为一个确认标签。

TP=H∩T，FP=T−H，FN=H−T。Precision=TP/(TP+FP)，Recall=TP/(TP+FN)，F1=2TP/(2TP+FP+FN)。分母为零的指标返回 null。分别输出文本、音频、视觉和 Appraisal 及整体 micro 结果。不计算 true negative 或四态准确率。

未勾选不写为 negative，但在一个已提交样本中，Qwen 多报而人工未选的 positive 仍按集合差计 FP。这样无需逐项选择其他三个状态即可进行正标签集合比较。

模式仍是 `teacher_visible_assisted_review`，不可混称盲审。未自动将结果写回训练集或训练模型。

## 运行和存储

在项目根目录执行 `bash human_annotation/start.sh`，服务监听服务器 `127.0.0.1:8766`。原 Cue / Appraisal 服务 8765 独立运行。

SSH 访问通道：`ssh -N -L 18766:127.0.0.1:8766 Qiii`，打开 `http://127.0.0.1:18766`。通道只转发访问，结果仍写服务器。

正式库是 `annotations.sqlite3`。SQLite 使用兼容网络盘的 DELETE 日志、完整同步事务、关闭 mmap；history 表保存版本历史，settings 表保存 workspace_epoch。清零操作只删除草稿；如某草稿有先前已提交版本，则恢复先前提交。

视频默认有声：在服务器按需将原始 WAV 与完整兼容视频封装成 MP4，缓存位于 `cache/video_audio/`。原始媒体及原 Cue 静音预览不变。两个播放器互斥，避免重复出声；暂停、跳转、倍速由视频播放器统一处理。

## 验证

`reports/positive_review_checks.json` 记录当前规则的隔离 API / 浏览器测试：单个标签保存提交、证据选填、可留空维度、零确认项提交、自动保存刷新恢复、清零版本保护、positive CSV、已提交集合统计、已知 TP/FP/FN 数值与桌面/手机布局。

`reports/media_playback_checks.json` 为有声播放验证；`reports/storage_checks.json` 为并发写入和网络盘事务验证。测试使用隔离数据库与 8767 服务，未写入正式人工标签。

`reports/draft_resets.jsonl` 只记录清零时间和数量，不备份被清除的草稿内容。早期 `browser_check.py` 及其报告对应已被取代的全量必填规则；当前验证脚本是 `positive_review_check.py`，运行时需全新的隔离测试数据库。

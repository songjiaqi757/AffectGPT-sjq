# Appraisal v2.4 全量并行标注

用户已授权将全部合格源域样本的文本、完整音频和完整静音视频发送到原Qwen服务，并行标注。所有代码、数据、结果及截图均保存在服务器，密钥只通过关闭回显的stdin及匿名管道进入进程内存。

## 当前完成状态与划分（2026-10-22）

31,255条已全部成功，0条待处理/运行/失败；187,530个维度位置中58,443个有效、129,087个无效。
原200条已恢复diagnostic_reserved；训练27,679、验证3,076、审计300、独立保留200。
全部Teacher结果与原始响应保留，没有重新请求模型；labels.csv和页面仅同步当前角色，annotation_snapshot_role保留启动角色。
current_split_verification.json记录现行导出；final_verification.json及labels.no_diagnostic_split_20261022.csv保留历史导出校验，供旧图追溯。
下方并发、重试和传输说明记录执行机制；当前任务已结束，未发送新请求。

## 运行协议与文件

- 目录：/ai/sjq/AffectGPT-sjq/appraisal_annotation/runs/mercaptionplus_v2_4/
- 范围：当前冻结Cue release中的31,255条合格样本；原始31,327条中72条因Cue任一模态失败而按严格策略排除。
- 角色沿用：pseudo_train 27,679、pseudo_validation 3,076、gold_audit 300、diagnostic_reserved 200；不重新划分，不使用九个目标评测集。
- 模型及接口：qwen3.8-omni-flash，沿用Cue服务。
- Prompt：appraisal_teacher_v2.4；本体：appraisal_ontology_v2.3；schema：appraisal_annotation_schema_v2.4。
- 每样本一个联合任务，共31,255个请求任务；每次同时输入中英独立字段、完整连续16kHz单声道WAV、完整静音视频。
- 请求并发32；最大360 RPM、1,600,000 TPM；按保守token估计预留并平滑发送，实际速率可能低于上限。
- 遇429遵守Retry-After并全局降速；每轮至多3次，自动补跑可恢复失败一轮，累计至多6次模型请求。
- SQLite持久队列、独占锁、进程重启恢复running到pending；已成功任务不会重复调用模型。
- 鉴权/余额错误、连续36条任务失败、磁盘不足等会停止并保留断点。技术失败与语义弃标分开保存，不能伪造为unknown。
- 正常运行已脱离SSH会话；网络仍使用服务器既有1080代理隧道。
- 本任务只做Teacher标注，不进行图统计、模型训练或人工gold审计。

## 输入及传输

从原始dataset按需恢复Cue当时的完整媒体预处理，沿用Cue历史元数据并逐条核对SHA256。视频不抽帧、不裁时长、不缩放，沿用历史流复制/H.264兼容策略。

普通媒体采用Base64；超大完整文件沿用同一千问服务的官方私有临时上传（48小时有效），请求带X-DashScope-OssResourceResolve: enable。上传只是传输变化，不改变模型、原文prompt或媒体内容，不公开文件。

请求只含原始文本和音视频，绝不输入目标description、Emotion标签、Cue标签或图结果。焦点人物字段已取消；证据不足时state=null、valid=false。

## 已删除试标记录

按用户要求，pilot30与pilot30_v2_4中这30个样本的Appraisal标签、原始API响应、失败记录、标签CSV及截图/浏览器下载副本均已删除，共172个文件。没有备份或复用这些标签。

原始dataset、已有Cue标签、冻结协议、本体、prompt与输入元数据保留；清理清单见 reports/full_v2_4/pilot_cleanup.json。旧试标入口已禁止再次直接运行，使用annotate_full.py操作当前全量任务。

## 页面

原入口：http://127.0.0.1:18765/appraisal（沿用Cue的SSH转发）。
服务器服务仍只监听127.0.0.1:8765。页面显示全量成功/失败/进行中/等待数、并发上限，15秒刷新。

样本按100条分页，支持全库ID/文本/证据搜索、成功/失败/弃标筛选、完整媒体播放、原始JSON及下载。尚未执行的样本播放原始媒体，明确标出模型输入待生成。

运行中下载CSV为当时已成功记录；任务结束后执行器生成包含全31,255条样本（187,530个维度位置）的labels.csv及failures.csv。未成功位置保持request_status=technical_failure/pending且state/valid为空，绝不填成语义弃标或负类。

## 状态与文件

在服务器项目根目录执行：

    /ai/sjq/miniconda3/envs/vllm/bin/python appraisal_annotation/annotate_full.py --status

以上只读状态、不调用模型。运行中查看实时结果使用页面下载；任务已停止后，可用 --export 重建CSV。恢复任务使用 --launch，凭据仅通过无回显stdin输入；只处理pending或中断任务。不要将密钥写入文件。

- tasks.sqlite3：持久任务队列与尝试/token账本。
- runtime_config.json：workers/rpm/tpm，每5秒读取，可在既有允许范围调整。
- runner.pid.json、launch.json：后台进程身份。
- execution.log：任务成功/失败与限流日志。
- status.json、summary.json：每5秒更新的运行状态。
- annotations/、teacher_raw/、failed/：成功标签、每次原始响应、技术失败。
- inputs/、media/：实际输入元数据及完整媒体副本。
- protocol.json、source_document.md、prompts/、ontology.json：冻结依据。
- upload_cache/：私有临时文件引用，密钥与上传凭证不落盘。
- reports/full_v2_4/：清理、19项离线测试、输入预检、页面测试及运行抽核报告。

## 离线测试

    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m unittest discover -s appraisal_annotation/tests -v

不会调用模型。覆盖持久队列、崩溃恢复、成功缓存、最大重试、失败导出、联合媒体与私有上传、v2.4 schema及禁用焦点人物字段。

现有release的原视频来源和近重复隔离仍未全部核验。人工审计必须使用盲审界面，不能先看本页Teacher结果。语义弃标覆盖率不等于心理状态准确率。


## 数据角色恢复（2026-10-22）

原200条恢复为diagnostic_reserved，不并回训练，现行为27679/3076/300/200。当前划分入口见cue_student/artifacts/current_release.json，运行目录effective_data_split.json记录对齐方式。冻结samples/protocol和模型原始返回保留启动时快照；前端及JSON/CSV导出按sample_id显示当前角色，并保留annotation_snapshot_role。Appraisal提示词、实际输入和标签不变；恢复执行时验证冻结source_document.md。

## 全量标注完成（2026-10-22）

当前 mercaptionplus_v2_4 已完成31,255条，pending/running/failed均为0。
共187,530条维度记录通过严格格式校验：58,443条valid=true，129,087条valid=false。
最终CSV使用现行27679/3076/300/200划分，并保留annotation_snapshot_role历史角色。
8条最终响应中无效维度的字符串null按json_null_string_to_null_v1规范化为JSON null；
所有valid判定、证据、unknown_reason和其他字段不变，原始teacher_raw完整保留，无新增模型调用。
format_normalization_audit.json记录修复来源；current_split_verification.json记录当前划分全量核验，final_verification.json保留历史导出核验，
labels.csv为当前角色导出；labels.annotation_snapshot.csv保留原始角色导出。
valid=false维度仍应从相关建图统计中排除，不代表心理状态不存在。
标注目录只负责Teacher结果；统计图已由amg_graph按恢复划分重建，300条人工gold审计仍未完成。


## 媒体副本清理（2026-10-22）

按用户要求，已删除mercaptionplus_v2_4/media中的31,255份WAV与31,255份静音视频，共57.53 GiB。删除前逐一核对62,510个原文件及62,510个副本的SHA256，均与标注时元数据一致。dataset/mer2025-dataset原件、annotations、teacher_raw、inputs及全部CSV/协议保持不变。
页面使用数据集原始音频和按需兼容视频预览，明确区分原件与已清理的模型输入副本；历史输入路径返回410，不伪装为原件。可用冻结预处理代码和输入哈希在服务器按需重建副本，不会重新请求模型。
完整清单及前后核验见data_migrations/appraisal_media_cleanup_20261022。共享Cue预览缓存未清理。

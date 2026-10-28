# MER-Caption+ 全量 API 标注

用户已授权启动31,327条全量标注；93,981个独立模态任务；初始12个并发API请求，按用户后续要求先提升到24，现提升到32个并发API请求。
使用固定三套Prompt：中英独立字段、完整连续16kHz音频、完整静音视频文件。未完成的旧30条标签不复用。

运行目录：`/ai/sjq/AffectGPT-sjq/cue_annotation/runs/mercaptionplus/`。

- `tasks.sqlite3`：持久队列；每个样本/模态独立记录pending、running、succeeded、failed。
- `status.json`：每5秒更新成功/失败/进行中任务数、三模态齐全样本数、重试用量、停止原因。
- `annotations/`：仅保存验证成功的完整模态输出；`teacher_raw/`保留每次响应/错误及请求哈希、实际输入元数据。
- `failed/`：失败原因、是否允许重试、尝试次数；结束后生成`failures.csv`供复查。
- `labels.csv`：本轮结束或显式导出后生成。失败或未完成模态对应全部Cue为unlabeled、y空、mask=0，绝不补成negative。

限流：当前统一32并发、360 RPM（初始12并发、240 RPM）、1,600,000 TPM，平滑发送、按保守输入与最大输出预留token。遇429遵守Retry-After（无则60秒冷却），全局减半RPM；普通“Allocated quota exceeded”按限流重试，不误判为余额耗尽。

失败处理：

1. 网络错误、408/429、服务端5xx、JSON/schema不完整等每轮最多3次，指数退避并加抖动。
2. 首轮处理完后，只对可恢复失败再补跑一轮，总计最多6次HTTP请求/模态，不重复请求已成功任务。
3. 音视频损坏、400参数/输入拒绝、文件超限等保留在失败清单。视频只允许完整文件H.264兼容转码，保留时长/分辨率/FPS/帧数；不裁时长、不抽帧、不缩放来凑成功。
4. 密钥/权限/余额错误全局停止；连续36个任务失败也停止，防止系统故障扩大。未开始/中断的任务保留pending，修复后续跑。
5. 断点重启自动回收running为pending；已落盘且通过schema验证的成功记录直接复用。文件原子写入、独占运行锁避免双进程重复收费。网络超时后平台可能已经完成请求，重试仍可能重复计费。

```bash
cd /ai/sjq/AffectGPT-sjq/cue_annotation
/ai/sjq/miniconda3/envs/vllm/bin/python annotate_full.py --status
# 修复网络/输入问题后，以同一运行目录和密钥恢复；凭据仅通过环境或stdin传入
/ai/sjq/miniconda3/envs/vllm/bin/python annotate_full.py --retry-failed
# 已结束运行中的大小/文件解析失败：审计后定向排队，禁止批量重试审核拒绝
/ai/sjq/miniconda3/envs/vllm/bin/python repair_failed.py
/ai/sjq/miniconda3/envs/vllm/bin/python repair_failed.py --apply
# 再正常启动 annotate_full.py；只处理 pending，已成功结果不重跑
# 运行停止时可单独重新导出，含所有未标注项及失败清单；不调用API
/ai/sjq/miniconda3/envs/vllm/bin/python annotate_full.py --export
```

`--retry-failed`仍遵守单模态累计6次请求上限；超过上限的任务须复核后显式安排新的补标任务，不无限重试。
任务依赖本机网络代理的SSH反向隧道时，本机需保持联网，后台代理连接不能关闭。密钥不写入脚本、运行日志或配置文件。

2026-10-20 上传兼容修复：首轮结束有345个失败模态任务，其中261个完整视频超出Base64编码后10MB限制，7个音视频文件解析失败，72个内容审核拒绝，5个视频过短。前两类可定向使用千问官方私有临时上传：`GET /api/v1/uploads?action=getPolicy&model=qwen3.8-omni-flash`取得内存中的上传凭证，上传原完整静音视频/完整WAV后，携带`X-DashScope-OssResourceResolve: enable`引用`oss://`。官方临时文件48小时有效，缓存按47小时处理，服务实测允许单文件1024MB。上传和模型调用使用同一模型、同一账号。未把文件公开到第三方。

此修复是传输方式变更：模型、生成参数、Cue定义、冻结Prompt和完整时长/分辨率/FPS/客户端帧数要求不变。仅6个视频解析失败项采用既有H.264 CRF18完整转码；大小失败使用完整静音视频流复制。实际传输和文件SHA256记录于`inputs/`、`teacher_raw/`及成功标注meta；`repair_manifest.json`保留原始345项失败及处理决定，`transport_overrides.json`仅含定向修复项，`repair_actions.jsonl`记录排队操作。审核拒绝不自动补发；过短视频不填充、不循环来改变输入。所有未解决项继续unlabeled/mask=0。禁用无差别`--include-permanent`补跑，因为它会把审核拒绝一并重新提交。

官方说明：https://platform.qianwenai.com/docs/api-reference/more/upload-file-get-temporary-url

临时文件上传单独限4路；模型请求仍沿用32并发、360 RPM、160万TPM上限。上传写入/连接超时放宽为120秒、响应读取300秒；每次上传最多3次，网络失败标为可恢复，上传失败不占用模型请求次数。已停止运行时，可用`repair_failed.py --apply --retry-upload-errors`恢复经过审计的上传网络失败，与剩余pending任务一起续跑。该开关仍排除审核拒绝、短视频和已成功任务，不把重复上传当作重复模型标注。

并发和RPM支持运行中调整：执行器每5秒读取`runtime_config.json`的`workers`、`rpm`、`tpm`。workers范围1–64，RPM范围12–1000，TPM不超过1,600,000；越界配置被拒绝，继续使用原配置。提高并发补充工作线程，降低并发则让多余线程完成当前任务后退出。已有429降速按比例保留，不因反复读取配置被清除。配置文件应通过临时文件原子替换。用户停止时保存队列/JSON断点，CSV可通过`--export`单独生成，不阻塞后续续跑。

用户随后明确要求重试5个过短视频：各通过官方私有临时URL提交一次，视频SHA256和原时长0.68–0.84秒均保持不变，5项仍返回HTTP400 / `The video file is too short`。每项累计模型请求2次，本次新增5次HTTP尝试，API未返回新增token用量。证据为`short_video_retry.json`及`teacher_raw/*.visual.attempt2.json`；失败清单已更新，成功标签与CSV标签内容未改变。累计HTTP尝试94,366次，成功/失败仍为93,903/78，三模态齐全仍31,255条。单任务定向调用可设`Runner.task(..., maximum_requests=1)`，避免这类人工单次验证自动多发；完整离线测试现为20项通过。

2026-10-20按用户最新要求，流泪与其他Cue统一采用大模型原始标签：902条原始阳性恢复positive/y=1/mask=1，逐条证据与API响应一致。已移除执行器专用门控及每条记录的quality_review/label_overrides；未改变Prompt或重新调用模型。配置统一为`quality.label_postprocessing=none; preserve_original_model_state_and_evidence_for_all_cues`。CSV及前端同步更新，核验记录为`tearing_label_restoration.json`。

## 输入副本与目录整理（2026-10-20）

原始音视频仍位于项目`dataset/mer2025-dataset/`。全量`runs/mercaptionplus/media/audio/`、`media/video/`是API预处理副本，按用户确认的范围清理。前端读取原始视频，按访问生成完整静音播放缓存；补标按需恢复完整输入，沿用记录的转码策略，并核验源文件及已提交输入哈希。`inputs/`及`teacher_raw/`中的历史提交路径、哈希不因副本删除而改写。已成功任务仍直接复用标签，不调用API。

测试移至`tests/`，命令为`PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m unittest discover -s tests -v`；运行说明现位于`docs/FULL_RUN.md`。历史预算、中途快照和旧清理记录移至`reports/history/`；本次整理核验见`reports/cleanup_20261020.json`。

2026-10-20按用户后续要求，长停顿与频繁停顿也统一使用原始模型标签，不额外按时长资格屏蔽。全量核对31,322条成功音频、62,644个停顿标签，原始API响应、annotations和CSV状态及证据一致，y/mask符合统一映射；此前并无实际额外屏蔽，因此未改写标签文件。长停顿positive 3,181条，频繁停顿positive 197条；历史11,395条资格冲突（negative 11,381、positive 14）均保留原始二分监督。模型原始uncertain/unobservable仍mask=0，5个失败音频位置仍unlabeled/mask=0。方案中原拟增加的专用资格屏蔽已取消；冲突清单只作诊断。核验记录见`reports/pause_label_verification_20261020.json`，未重新调用API。

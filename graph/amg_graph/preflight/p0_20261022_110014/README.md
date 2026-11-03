# P0 运行前核验报告

状态：P0 完成；可进入 P2/P3 工程开发，最终目标集评测仍受后续阶段门槛限制。

完成时间（北京时间）：2026-10-22T11:08:33.570278+08:00
自动检查：305 项通过。
版本锁 ID：76eac932b109b29455aef081a5da79a48f9f1fa3055fef718c0d1b58fa72bebb

## 数据与图

- 数据 release：2019ab786e4e065699a3f980291b1d300a17ee1ec9a18213672f620fd2823ac7
- 图 release：75d45e203722ce060829e0db17ce7348f24ef44c024f1e99ff310f050194a420
- 角色：训练 27,679；验证 3,076；人工审计 300；独立保留 200。
- 252 节点、1,048 统计边、16 层级边、2,595 合格路径。
- 独立复算 11,576 张列联表、完整候选族 FDR、bootstrap 区间和 3,209 条候选路径联合支持。
- 样本 ID、manifest 来源组及已登记媒体 SHA256 在各角色之间无交叉；原视频来源及近重复独立性仍属于 P1。
- 62510 个媒体文件重新核验存在性、字节数与 mtime；本次不重新计算所有媒体内容哈希。
- 66 个原数据/图/Emotion 文件前后指纹一致。

## 已有模型选择的核验与锁定

| 模态 | 已选实验 | Teacher 验证 macro AP | 有监督训练样本 |
|---|---|---:|---:|
| text | text | 0.8632430462 | 27673 |
| audio | audio_full | 0.8037129680 | 27679 |
| visual | visual_full | 0.8129467638 | 27677 |

核验九组 best.pt 的完整文件 SHA256、静态元数据、签名、数据/holdout 身份、Cue 顺序、模型头维度、配置、支持计数、归档训练代码和编码器资产。选择复现已有训练报告的源域验证 macro AP 规则；无新训练和目标集数据使用。

## 已明确记录的差异与后续门槛

- historical_document_revision_is_v28：Live v2.9 hash is separately locked; frozen build plan and old revision record are unchanged.
- cue_code_aggregate_has_added_migration_file：All original training source modules match archived code; added cancel_diagnostic.py changes the aggregate current module hash. Exact live and archive hashes are recorded.
- uncalibrated_thresholds_and_no_active_deferred_freeze：Current fixed 0.5 is an uncalibrated engineering threshold. No human calibration or deployment active/deferred artifact is claimed.
- validation_last_cache_not_bound_to_best：Do not reuse validation.last.npz as best predictions; regenerate from the locked trio and store checkpoint hashes.
- human_and_original_source_audits_pending：Registered group/exact hash isolation is verified; original provenance and near duplicates remain unaudited.
- untracked_implementation：Git commit is recorded; exact source hashes are required because core directories are currently untracked.

## 入口与复现

- preflight_audit.json：逐项检查结果与范围。
- version_lock.json：数据、图、模型、源码、环境、schema 指纹。
- query_engine_inputs.json：后续模块统一输入配置；P4 参数为空，active/deferred 未冻结。
- role_reconciliation.json / .csv：四种角色数量与成员/组 ID 摘要。
- checkpoint_inventory.json：九组权重及现有三路选择证据。
- document_revision_v2_9.json：本次文档修订来源记录，保留旧 v2.8 历史。
- run_preflight.py / checkpoint_metadata.py：服务器上的审计程序。

本次不调用旧验证器的文档修订检查，因为它针对旧 v2.8；统计核验结果重定向到本目录，未覆盖冻结图的历史 verification.json。

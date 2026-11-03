# 严格排除任意模态失败样本：五组全新训练

当前任务：/ai/sjq/AffectGPT-sjq/cue_student/jobs/strict_all_modalities_20261020_163131
政策：all_modalities_succeeded_v1。原始31327个样本的93981个标注任务中78个失败，涉及72个不同样本。所有72个样本均在划分前整体排除。

## 数据审计

保留31255个三模态均标注成功的样本。划分为训练27679、伪标签验证3076、人工保留300、诊断保留200。
失败ID与每种划分以及实际每模态训练/验证成员集合的交集均为空。
人工集保留原299条；视觉标注失败的samplenew3_00094241替换为samplenew3_00039200。
替补通过seed42从旧诊断保留集中的合格候选抽取，排除曾被旧训练/验证/开发使用的已知组及对应音视频SHA256重叠；选择过程不读取cue标签值。
manifest记录替补候选、随机种子、上一版身份和新成员摘要。固定人工集不参与早停/模型选择，目前人工gold标签尚未创建。

原始标注、labels.csv及媒体保持原状；排除清单和成功白名单冻结在release/eligibility.json中，摘要参与release_id。
Release加载器强制拒绝旧政策和不合格成员；prepare在分组划分前过滤；reserve_holdout只从三模态成功样本抽取。

## 从头训练及优化

五组均从原始预训练资产和新随机初始化头开始，optimizer/scheduler/step全部重新初始化；不加载旧Student模型或旧optimizer状态。
文本编码器full；音频、音频时序、普通视频和时序视频编码器frozen。维持既有学习率、BF16、微批、累积、epoch及早停设置。
五组共用经过输入管线优化的loader_for：text worker0、audio/audio_temporal worker2、visual/visual_temporal worker4；pin_memory和non_blocking；多worker任务prefetch_factor2、spawn并固定Torch/BLAS单线程；视频decode_threads1。文本worker0是先前实测选择。
这确认输入加载速率优化生效，不等同于所有batch/GPU吞吐参数都达到最优。

## 验证与结果

64项单元测试通过，新增按单模态失败整条排除、失败任务去重、不完整队列拒绝、加载阶段白名单防护及集合无交集测试。
五种真实编码器训练及音频时序续训测试记录在任务目录integration_report.json；正式启动状态见status.json。
部署时核对主项目和任务source快照的全部Python源码摘要相同。
五组结束后comparison.json对同一伪标签验证集的best checkpoint汇总macro AP、masked BCE和逐cue指标；不作为人工gold性能声明。

旧训练输出、旧数据包、旧任务目录、旧测试checkpoint及旧结果报告已按用户授权清理。保留当前版本数据/源码/测试审计、预训练资产和开发曝光历史，避免丢失人工保留集隔离依据。

## 完成核验

2026-10-20T16:49:10.995932+08:00，五个正式进程均持续更新，旧训练产物目录已全部删除。最新核验及删除清单见当前任务completion.json与cleanup_report.json。

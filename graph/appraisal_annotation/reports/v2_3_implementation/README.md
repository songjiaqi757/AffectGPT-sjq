# Appraisal 三模态联合标注 · 30 条试跑

所有代码、数据、结果、截图及验证工具均保存在服务器 /ai/sjq/AffectGPT-sjq；没有下载到本地文件。API 密钥仅经关闭回显的 SSH 标准输入进入进程内存，未写入配置或日志。

## 本次结果

- 固定样本：复用 cue 旧 pilot30 的相同 30 条 ID。
- 模型：请求与实际返回均为 qwen3.8-omni-flash；接口沿用 cue。
- Prompt：从 图构建.md 的完整英文代码块逐字提取，冻结为 appraisal_teacher_v2.3；本体 appraisal_ontology_v2.3。
- 单条请求同时包含中英文独立文本字段、完整连续 16 kHz 单声道 WAV、完整静音 MP4。
- 媒体通过服务器硬链接复用 cue 当时的真实 API 输入；逐条 SHA256 一致，无截断、抽帧或缩放。视频服务端处理沿用平台默认，不声称验证了平台内部全部帧覆盖。
- 每条实际返回均含非零 text/audio/video token，包括最终 schema 失败的样本，证明接口接收了同次请求中的三种输入。
- 30 条均已测试；29 条通过 schema，1 条技术失败。成功结果共174行维度记录：108行有效，66行 state=null, valid=false。
- 失败样本 samplenew3_00089629：9次尝试仍发生schema错误，主要为把JSON null返回成字符串"null"，部分响应缺少字段。没有做类型强转、补标签或语义后处理。
- 64个请求尝试记录全部保留：29次通过schema、32次schema失败、3次最初直连超时。失败生成也计入 usage_including_failed_generations。
- 没有运行全量标注、图构建或人工金标审计。试跑覆盖率不是心理状态准确率。

## 页面

沿用现有cue回环服务 127.0.0.1:8765，新增 /appraisal；cue首页增加入口。
已有SSH转发入口为 http://127.0.0.1:18765/appraisal。服务器无需公开新端口。

页面支持30条检索、状态筛选、J/K切换、完整音视频同步播放、兼容预览/实际模型视频切换、中英文本、焦点人物、事件情境、六维状态及ID、证据来源、无效原因、技术失败详情、原始响应、CSV/JSON下载。浏览或刷新不会触发模型调用。

## 产物

- annotate.py：协议冻结、预检、联合请求、断点续跑、三并发、每轮最多三次尝试、原始记录与汇总。
- verify.py：离线核验联合输入、哈希、schema、原始响应和CSV；已记录的终态技术失败保持为失败。
- viewer.py、viewer/：挂载到原cue FastAPI服务的只读页面与API。
- runs/pilot30/samples.json：原始字段及来源分区；沿用 source_group_id/role，不重新划分。
- runs/pilot30/prompts/、protocol.json、ontology.json：冻结的prompt和输入协议。
- runs/pilot30/annotations/：29条成功标注。
- runs/pilot30/teacher_raw/：64次尝试的API原始响应或网络错误。
- runs/pilot30/failed/：1条最终技术失败。
- runs/pilot30/inputs/：实际请求元数据、哈希、媒体路径与处理事实。
- runs/pilot30/labels.csv：174行成功维度记录。
- runs/pilot30/summary.json、status.json、verification.json：真实计数和离线核验。
- reports/：原cue文件备份、测试报告、服务器浏览器截图。
- tools/、browser-cache/：项目内的独立页面验证依赖，不安装到训练环境或系统。

## 离线验证

在服务器 /ai/sjq/AffectGPT-sjq 执行：

    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python appraisal_annotation/verify.py
    PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m unittest discover -s appraisal_annotation/tests -v

以上不需要凭据、不调用模型。
annotate.py --preflight 仅构造和核验输入，--summarize 仅重建汇总。
annotate.py 正常执行会补跑未成功样本，调用并消耗模型额度；本次已停止，不会自动重试。
网络需使用现有服务器代理 QWEN_HTTPS_PROXY=socks5h://127.0.0.1:1080。

## 数据角色与审计限制

复用当前严格Cue release release_strict_all_modalities_20261020_163131 的成员、角色和来源组。
30条中包含既有人工保留分区成员；未来独立人工审计须另用盲审界面，人工标注者不能先看本页Teacher输出。
原始视频来源和近重复隔离仍受现有release限制，不声称已经完成来源组独立性核验。

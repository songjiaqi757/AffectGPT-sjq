# MER-Caption+ 完整音视频 API 标注

当前协议：`qwen_omni_api`；模型：`qwen3.8-omni-flash`。全量31,327条样本、93,981个模态任务；已成功93,903项，剩余78项失败，31,255条样本三模态齐全。流泪与其他Cue统一采用大模型原始标签，现有902条流泪positive均为y=1/mask=1。长停顿和频繁停顿同样保留原始模型结果，不额外按时长资格屏蔽；positive分别为3,181条和197条。

## 目录

| 路径 | 用途 |
|---|---|
| `annotate_full.py` | 全量调度、断点续跑、限流与导出 |
| `annotate_api.py` | 输入构造与schema验证，全量执行器依赖；独立入口面向旧30条 |
| `media_upload.py` | 官方私有临时文件上传 |
| `repair_failed.py` | 修复后的技术失败定向补跑 |
| `protocols/qwen_omni_api/` | 42个Cue、本体、模型参数与固定Prompt |
| `runs/mercaptionplus/` | 当前标签、原始API响应、输入元数据、队列及核验清单 |
| `viewer/` | 只读查看器及按访问生成的播放缓存 |
| `tests/` | 不调用模型的执行器、上传和输入恢复测试 |
| `docs/FULL_RUN.md` | 全量运行、失败恢复及处理记录 |
| `reports/history/` | 原预算、历史清理记录与中途快照 |
| `reports/cleanup_20261020.json` | 本次文件整理与副本清理核验记录 |
| `reports/pause_label_verification_20261020.json` | 原始停顿标签与CSV映射全量核验记录 |
| `runs/pilot30/`、`verify_api.py` | 旧30条输入及离线校验，仍被查看器默认首页依赖，无旧试标标签 |

## 数据与缓存

原始音视频唯一保留于`/ai/sjq/AffectGPT-sjq/dataset/mer2025-dataset/{audio,video}/`，样本成员和源路径见`runs/mercaptionplus/samples.json`。

原`runs/mercaptionplus/media/audio/`与`media/video/`为API预处理副本，已在确认原始文件存在、调整引用并验证后清理。输入元数据中的`submitted_*_path`与哈希保留历史提交事实，不保证副本当前仍在磁盘。

流泪页面直接从原始dataset按访问生成完整静音H.264播放缓存，不依赖已删除的API副本。后续补标只为实际请求的样本恢复完整16kHz WAV或完整静音MP4；恢复视频沿用记录的复制/转码方式，并校验源文件与历史输入哈希。不会因浏览或读取状态重新调用模型，也不会批量重建全量副本。

## 常用命令

```bash
cd /ai/sjq/AffectGPT-sjq/cue_annotation
# 读取全量状态，不调用API
/ai/sjq/miniconda3/envs/vllm/bin/python annotate_full.py --status
# 23项离线测试，不调用API
PYTHONDONTWRITEBYTECODE=1 /ai/sjq/miniconda3/envs/vllm/bin/python -m unittest discover -s tests -v
# 启动只监听127.0.0.1的查看器
bash viewer/start.sh
```

本机SSH转发入口：`http://127.0.0.1:18765/tearing`（902条流泪阳性）；`/`仍为旧30条输入浏览与全量进度入口。重跑失败项和导出命令见`docs/FULL_RUN.md`。

环境：`/ai/sjq/miniconda3/envs/vllm/bin/python`；FFmpeg为`/ai/sjq/miniconda3/envs/talkinghead/bin/ffmpeg`。密钥仅通过环境或stdin传入，脚本不保存密钥。训练方案见项目根目录`方案.md`。

所有Cue采用同一映射：positive→y=1/mask=1，negative→y=0/mask=1，uncertain/unobservable及失败unlabeled→y空/mask=0。频繁停顿的历史资格冲突清单仅作诊断，不参与后处理。

# 实体目录整理完成

此记录替代 _organization/20261029 中关于软链接兼容方案的当前状态描述；旧记录保留为操作历史。

- 图相关内容实体目录：/ai/sjq/AffectGPT-sjq/graph。
- 上次创建的 29 个旧入口软链接，以及 graph 下的 AffectGPT、dataset 两个依赖软链接，均已删除。
- 工程根目录、graph 一级目录当前均无软链接。
- 225 项代码、配置、文档文件完成实际路径调整；Python 模块从 graph 目录执行或使用 graph/run.py。
- 原始模型工程和数据仍使用 /ai/sjq/AffectGPT-sjq/AffectGPT、/ai/sjq/AffectGPT-sjq/dataset 的实际地址。
- 冻结实验记录保留原始字节；历史路径由显式读取规则解析到新实体目录。
- 原始 SHA256 函数返回真实当前字节哈希；只有迁移清单精确绑定的改动可以满足旧源代码指纹检查。
- 修改前原文备份在 before/，前后指纹见 source_migration.json。
- A800、A100 各通过 18 项测试、真实冻结图加载、统一启动入口及两个标注启动脚本语法检查。
- 冻结图读取成功：252 节点，1048 边，2595 路径。
- 16 项冻结记录的迁移前后哈希一致；未重训、未改指标。
- 全部修改、备份、测试和报告都在服务器上。

汇总验证：verification.json
分机验证：A800_verification.json、A100_verification.json
路径索引：../../paths.json
使用说明：../../README.md

# 图相关目录整理完成

- 实体目录统一为 /ai/sjq/AffectGPT-sjq/graph。
- 移动 29 项原有目录和文档；更新 7 个当前入口/资源配置。
- 旧路径保留兼容软链接；冻结计划、源代码和历史结果内容不改写。
- 286 个受保护文件的迁移前后 SHA256 相同；推荐 checkpoint 的 inode、大小和修改时间未变。
- A800、A100 分别验证全部 29 个新旧入口指向同一实体，以及当前计划、13 项代码指纹与 4 项输入指纹。
- 13 项现有统计/映射测试通过；真实冻结图加载通过（252 节点，1048 边，2595 路径）。
- 新启动入口和从 graph 直接执行 Python 模块均通过启动检查。
- 全部操作、备份、日志和验证报告在服务器上完成，无本地项目副本。

索引：../../paths.json
说明：../../README.md
迁移清单：plan.json
当前入口变更：navigation_changes.json
原始导航备份：navigation_before/
两台服务器验证：A800_verification.json、A100_verification.json
运行检查：smoke_checks.json
总验证：verification.json

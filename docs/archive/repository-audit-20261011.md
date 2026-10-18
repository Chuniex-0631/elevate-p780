> 2026-10-11 验收历史快照。数量、研究优先级和监测描述不代表现在；最新见 [全库整理验收](../REPOSITORY_AUDIT.md)。

# 2026-10-11 全库结构整理验收

基准提交：`af103577c223c905a26924d623afb220397c34ff`；完整递归树未截断，共 **254 个文件**。本轮是研究档案整理，研究进入待机；未取得 Root、BL 解锁或匹配原厂固件。

## 整理后的入口与层次

[README](../../README.md) → [文档导航](../README.md) → [STATUS](../STATUS.md)/[专题](../research)/[证据](../../evidence)。状态和资产清单保留稳定入口，持续专题位于 research，规范/来源位于 reference，早期阶段验收位于 archive；旧原始报告仍在仓库 archive/。

- 原厂配置从根目录归位 evidence/device，原始 Blob 不变；Tracefs、GhostLock ZIP、APK、Bugreport/日志保留原件。
- 初轮失败布局资料从含混的顶层 builds/ 与 comparison 文件归位 run 38060293186；最终结果仍引用 run 38060518994。所有不同运行上下文保留，LATEST 不能保证最近轮次成功。
- critical-delta.txt 与同轮 critical-delta.md Blob 完全相同；只删除前者，保留 Markdown 正本与历史恢复分支。
- 重写首页、文档/证据/工具导航和待办；补齐 OTA、Journey、布局与本轮时间线；旧验收计数标为历史快照。
- 全量更新相对链接、显式仓库路径及 workflow 输入；候选构建/历史导入改为手动，归档完整性检查继续自动运行。

## 数量与重复项

迁移路径 **44 个**（文档与数据归位），删除 **1 个 / 3,321 B** 的重复阅读格式。整理完成版本为 **258 个受跟踪文件**；后续版本变化以实际 Git tree 为准。

基准树有 **34 组相同 Blob**，包括同源配置、跨运行日志、空输出及不同格式阅读副本。没有把同 SHA 自动等同于“无用”：保留独立运行、ZIP 内部副本和失败证据，仅合并上述一份同轮重复格式。

[结构映射与保留 Blob 身份](../../evidence/analysis/repository-structure-20261011.json) 登记全部迁移、删除及基准重复组；[复核工具](../../tools/verify_repository.py) 验证链接、Python/JSON 格式、Journey 编码 ZIP/阅读视图、方法原始指令哈希及数据迁移 Blob。

## 验证范围

提交前已静态核对全量 Markdown 相对路径链接、Python 语法、workflow YAML 格式，以及迁移计划中的旧/新路径。

实际结构提交 `a5212613d8fb784772095a6c2d03170da0dea9ac` 的 [GitHub 验收 run 38069160978](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38069160978) / job 114262861154 已全部 success：258 文件、48 Markdown、337 个相对路径链接/0 失效、10 个 Python 语法检查、35 个有效 JSON；25 个迁移数据 Blob 身份一致。原配置/GZIP、Tracefs、四版 ZIP 内嵌副本、ADB/Bugreport ZIP、三 APK、UTF-16 快照及 Journey 编码原件/阅读视图均通过检查；54 个配置方法和 6 个性能决策方法的原始指令哈希通过。

验证结果同步写入结构映射 JSON；本记录补记仅更新说明，不改变证据字节。未验证所有网页可达性、Markdown 标题锚点或全历史隐私。

原始 framework 大 ZIP/JAR 尚未入 Git；现有提取与来源 SHA 不冒称原件完整保存。Journey 小配置 ZIP 以 Base64 可还原；敏感日志仍未发布级脱敏。细节见 [资产清单](../EVIDENCE_MANIFEST.md) 和 [SECURITY](../../SECURITY.md)。

## 恢复和今后维护

整理前完整快照：[archive/pre-restructure-20261011](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-restructure-20261011)，较早 pre-cleanup 快照继续保留。移动不改写历史；旧路径可在快照中找到。

每日监测任务保持启用，只有可核验新进展才通知；以当前 GitHub 为基线，有新证据时同步专题、状态、来源与维护说明。无新增不制造提交，主动实机实验暂缓。

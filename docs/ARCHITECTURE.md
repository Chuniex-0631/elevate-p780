# 仓库结构与维护约定

> 2026-10-25 重建。说明本仓库的目录职责、文档命名与更新规则。

## 目录职责

| 路径 | 职责 |
|---|---|
| `README.md` | 入口：项目定位、设备事实、当前状态、导航 |
| `CHANGELOG.md` | 按时间的目标与结果摘要（不是原始日志） |
| `SECURITY.md` | 范围、伦理与联系方式 |
| `docs/` | 全部文档。总览页为 `docs/index.md`（自动生成） |
| `docs/STATUS.md` | 当前结论与证据等级，**唯一权威状态页** |
| `docs/NEXT_STEPS.md` | 下一步计划与验收标准 |
| `docs/HISTORY.md` | 时间线（只记录可被仓库文件或 Actions 证据支持的事件） |
| `docs/research/` | 专题报告，命名 `p780-<主题>-<YYYYMMDD>.md` |
| `docs/reference/` | 方法学：来源、归档规范、证据完整性 |
| `docs/archive/` | 已被取代的阶段性文档，保留原样 |
| `evidence/` | 原始证据（日志、配置、快照）。清单见 `docs/EVIDENCE_MANIFEST.md` |
| `tools/` | 可复跑的分析与探针工具，每个目录自带 README |
| `archive/` | 迁移前的旧研究材料 |

## 文档约定

1. **状态只有一个权威页**：`docs/STATUS.md`。其他页面只写"本页范围"，不另立结论。
2. **每条结论必须能追到证据**：文件、命令输出、Actions 产物或上游链接；没有证据的推断标注为"未验证"。
3. **更新通告**：在页面顶部加 `> YYYY-MM-DD …` 一行，保留历史通告，不删旧行。
4. **不重写历史**：已被取代的专题移入 `docs/archive/`，不删除、不改写。
5. **编码统一 UTF-8**。历史上少量页面因二次编码出现不可逆替换字符（U+FFFD），这类页面在 `docs/index.md` 中标记为"部分损坏"，其结论以 `docs/STATUS.md` 与未损坏专题为准。

## 证据约定

- 原始运行日志、设备配置、OTA 元数据放 `evidence/`，按主题与日期分层。
- 证据文件不做内容编辑；需要脱敏时，另存副本并在对应专题报告里说明变换方式。
- `docs/EVIDENCE_MANIFEST.md` 由脚本从实际文件生成，不手工维护。

## 工具约定

- 每个工具目录含 `README.md`，写明用途、依赖、运行方式与边界。
- 只读工具与会产生设备状态变化的工具必须区分标注。

## 变更流程

1. 新增专题：写 `docs/research/` 报告 → 更新 `docs/STATUS.md` 与 `docs/NEXT_STEPS.md` → 重跑 `docs/EVIDENCE_MANIFEST.md` 与 `docs/index.md` → 更新 `CHANGELOG.md`。
2. 结论变化：先补证据，再改状态；不允许先改结论后找证据。

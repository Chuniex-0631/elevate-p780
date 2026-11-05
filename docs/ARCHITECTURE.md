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
4. **保留历史证据**：原始输出、样本和日志不改写。旧解释可在原段落就地更正并注明日期、依据与范围；大幅重排状态页/计划前保存快照至 `docs/archive/`。历史候选步骤必须标明已被替代，不作为当前执行指令。
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

## 2026-11-05 仓库维护重构

维护流程见 [贡献指南](../CONTRIBUTING.md)。索引与证据清单仅从 Git 跟踪文件生成，使用 `--check` 可只检查、不写入。维护脚本定位仓库根目录，不依赖调用目录；完整性检查在 Python 优化模式下仍生效。

原始证据全目录禁用换行转换，以保持 Windows / Linux 的摘要一致。维护 CI 独立于设备实验及历史内核构建；不自动运行探针或连接设备。

本次重建清单补录 10 个已跟踪文件；271 个既有条目的历史清单摘要与当前 Git 保存字节不符，已按保存字节重新计算。原始证据文件无 Git 差异。此操作更正清单基线，不证明历史设备采集时的字节身份；复核旧摘要时应同时查看 Git 历史中的旧清单。

## v1.1.0 完整目录分工

```text
app/                    应用源码与历史构建说明
release/                已有应用产物（APK 仍为 1.0）
docs/
  research/             专题报告
  reference/            来源、方法与结构迁移表
  archive/              阶段性文档快照
  rom/                  ROM 来源与核验说明
  releases/             按版本记录的发布说明
evidence/               原始材料；路径与字节保持不变
archive/                迁移前研究、历史工具与脚本
tools/
  kernel-config/        内核配置与候选结构工具
  journey/              Journey 框架分析
  ghostlock/            从根目录归入的历史研究骨架
  tests/                维护与结构回归测试
  <专题目录>/           完整分类见 tools/README.md 与 catalog.json
.github/workflows/      维护检查、历史实验构建与标签发布
```

每个工具子目录必须在 `tools/catalog.json` 登记并包含 README；结构测试检查覆盖率，防止新工具再次散落。原根目录 Python 工具保留兼容转发，规范代码只保存在分类目录中。活动工作流已使用规范路径。历史材料和证据中的命令仍保留原貌。

`docs/reference/structure-migration.json` 记录迁移前后路径及迁移前 Git 内容 SHA-256；代码迁移按 Git 字节校验，Markdown 只修复相对链接。原始证据与 `archive/` 未搬迁或改写。`ghostlock/` 不再位于仓库根目录，其研究材料统一归入工具层。

仓库版本由 VERSION 管理，发布流程见 [RELEASING](RELEASING.md)。本地 reports、构建缓存与凭据不属于源码包。

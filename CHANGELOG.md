# 归档维护日志

## 2026-10-10 — 继续研究：配置语义与候选结构布局

- 逐项扫描 24 个消失符号的 Kconfig/C/H/S/Makefile 引用，永久保存原始引用和 provenance。
- 区分 FORTIFY_SOURCE 的 Clang 依赖限制、REFCOUNT_FULL 的实现替换、不可达 NFC 菜单和未被两棵公开树覆盖的配置。
- 增加候选结构探针和 Kbuild 编译参数提取流程；固定两棵源码与 Android Clang11，保存每轮成功或失败工件。
- 首轮 TINNO 构建脚本缺执行权限已记录并修复；探针 TASK_SIZE 名称与内核宏冲突已改名，新增 32 项完整性检查；保留前两轮结果，不冒充完整布局。
- 最终 [#38060518994](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38060518994) 全部通过，两棵固定树各 32 项完整提取、0 项差异；永久保存全部原始工件。
- 专题：[配置与布局研究](docs/2026-10-10-config-layout-research.md)。候选布局不代替原厂二进制，未实现 Root/BL 解锁。

## 2026-10-10 — 新一轮原始设备资料归档与去重

- 新收到 2 套 ADB 审计及各自压缩包、完整 Bugreport、三份 APK、两份 OTA 日志、TEE 白名单与 JNI 受限路径记录、phase3 包清单。
- GitHub Actions 校对证实，`hand5g_debloat_audit.zip` 对应展开的 22 个文件、`hand5g_final_audit.zip` 对应展开的 9 个文件**逐字节相同**；删除 31 个重复展开文件，总计 7,576,640 B，保留两个 ZIP 和完整恢复分支。
- 将原件重新组织为 `evidence/restricted/`、`evidence/apk/`、`evidence/tee/`。含敏感数据风险的系统日志不再堆放根目录；备份分支 [archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010) 保存了清理前所有文件。
- 对照旧文件清单，特别区分历史 1,742 B 和本次 376,662 B 的同名审计 ZIP，避免误认为同一份字节原件。
- 新增 [文件去重报告](docs/NEW_UPLOADS_AND_DEDUP.md)、[TEE/APK 资料](docs/TEE_AND_SYSTEM_APKS.md) 和 [OTA/Bugreport 资料](docs/OTA_LOGS_AND_BUGREPORT.md)，并更新 README、状态表、时间线、固件与应用清理专题。
- 这次整理为只读离线研究档案维护，没有实机 Root/BL 解锁或获取完整 OTA 的新成功证据。

## 2026-10-10 — 最终封存验收（经 GitHub 实际核查）

- 机主新上传的 **4 份 GhostLock 研究 ZIP** 和 **4,096 B 的 Tracefs 原始文件**已经全部入仓，按来源与用途移动至 `evidence/ghostlock/` 和 `evidence/device/`；使用 Git 已有 Blob 保持字节不变。
- 新建 [完整性报告](docs/EVIDENCE_INTEGRITY.md)；Actions [#38055450831](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055450831)、[#38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285) 验证压缩包 CRC、SHA-256、ZIP 内部 `CHECKSUMS.sha256`、四版内嵌设备证据与主原件的字节一致性。
- 四个 ZIP 分别包含 **13 / 16 / 17 / 27** 个文件；v0.4 原始 README 首行错误标成 v0.3，已如实在 [版本索引](docs/GHOSTLOCK_PORT_VERSIONS.md) 标记，不修改原件。
- 消除 README、GhostLock、Next Steps、文件清单、历史时间线与出处文档中“原件仍未上传”的旧描述；重写仓库首页，明确研究结果和未达成事项。
- 当时尚未迁入的材料已在**随后一轮新增上传**中部分补齐（Bugreport、三份 APK、OTA/ADB 日志），其余继续列入清单。新增原件尚未完成发布级脱敏，详见本日志上方的后续整理记录。
- 已发布 [最终验收报告](docs/FINAL_ARCHIVE_REVIEW.md) 与全套双向证据索引；本轮为**资料验收**，没有在实体机运行漏洞、刷入固件、获得 Root 或解锁 Bootloader。

## 2026-10-10 — 首次整库整理

- 从早期 **2026-06-12 EDL / Fastboot 记录**，恢复并归档系统版本、Sahara、Bootloader、A/B 分区及历史失败信息。
- 从 2026-10-03～04 的文件，恢复 **QAS/PFM/Mink/TZAccessService** 完整技术报告与设备清理脚本/摘要。
- 归档旧版 **GhostLock v0.1–v0.4** 的资产清单、实机 Kernel Config、Tracefs 取证结论和只读核对工具；此初期记录在后续“最终封存验收”阶段已补全全部四份 ZIP 原件。
- 保存 **2026-10-10** Qualcomm 5.4.233 候选源码的原生 Kconfig、Android Clang11.0.2/14 编译过程，以及真实的 `rtmutex.o`。
- 将 GitHub Actions 原始工件转为 `evidence/actions/` 下可长久存储的 Git 文件，减少 CI 工件过期导致的资料丢失。
- 生成设备基线、可信度表、时间线、官方 OTA/安全公告、隐私规则、资料清单和当前阻断条件。
- 明确说明：**设备仍 locked，Root/BL 解锁尚未达成**，原厂 `_162` 镜像与实机匹配的 `vmlinux` 未取得。

## 未来每轮维护要求

新实验结束后，同步更新：`docs/STATUS.md` → 对应专题报告 → `docs/EVIDENCE_MANIFEST.md` → 本文件。

未经复核的结果只进入“假设/待验证”，不能更新为“成功”状态；所有 GitHub Actions 编译要保存运行编号、源码 commit、工具链版本和日志，重要工件应归档到 Git 历史。


## 2026-10-10 OTA 与实机 framework 深入审计

补同步 OTA 报告/证据：6 份引擎日志均为启动清理，未得到固件。新增机主 JAR 的 54 个 Journey 方法原始字节、8 类反汇编、17 个外部引用与输入 SHA。定位应用行为 XML → JourneyPerformanceService，未证实 OTA/Root 链；统一修订 README、STATUS、NEXT_STEPS、OTA 与证据索引，记录阶段同步维护约定。原始 18MB framework ZIP/JAR 尚未迁入 Git，保留上传来源。

## 2026-10-10 — Journey 实机配置核对完成

- 校验机主 3,940 B 配置 ZIP，保存可还原全部原始字节的 Base64、输入 SHA、vendor XML/version 与 TCS 阅读视图。
- XML、version.txt、运行版本均 42；39 条 XML 规则按 ALL 假设得到 64 个策略键，与实机 dump 的全部字段完全一致。
- 核实 panda、qqdownloader 重复键覆盖，不把策略条目解释为安装/系统权限；配置来源仍不能排除同内容缓存。
- 统一修订既有 Journey 报告、README、STATUS、NEXT_STEPS 和证据清单；下一阶段转为离线消费者追踪及匹配原厂固件证据，Root/BL 成果不变。

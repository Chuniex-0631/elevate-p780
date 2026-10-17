# 归档维护日志

## 2026-10-18 — P780 实机 AVB Green/Locked 基线与只读研究路径

- 用户提供的 ADB 输出：`green`、`locked`、`flash.locked=1`、活动槽 `_b` 与 VBMeta digest `33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`。此为用户提供实机证据，尚非独立重测或镜像提取。
- 新增 [AVB 基线专题](docs/research/avb-live-baseline-20261018.md) 与 [Windows ADB 只读取证脚本](tools/p780-avb-readonly.ps1)；对照 Android 11 官方 avbtool 的链式 VBMeta digest 定义、NCC Group 测试公钥识别工具，明确只凭 digest 无法反推出签名钥匙。
- 同步 README、STATUS、NEXT_STEPS、专题索引、工具说明与公告专题。仍缺 `_162` 原厂 `vbmeta/boot`、经验证的 locked 写入通道；未执行刷机或 Root。
- 审核时 GitHub API 报告 visibility=public，和既有 Private 文案不符；SECURITY/README 已提示敏感原件风险，需机主确认设置并审查 Git 历史。

## 2026-10-17 — XDA 正文补档与 Recovery 验签边界

- 原样保存用户提供的 XDA 4805241 正文，标注来源链及未独立复核状态；关闭同一正文人工获取提醒，保留既有邮件历史。
- 区分 OTA ZIP 证书与 AVB 测试钥匙；将签名失败限定为该包/该次测试结果，记录 whole-file 签名、包结构、公钥和完整日志缺口。
- 同步 README、STATUS、NEXT_STEPS、证据清单及公告专题；OPG105 仅为未验证别名，fastboot boot 未有成功证据，EDL 并非已证实唯一通道。
- 继续优先原厂镜像与可核验写入通道；未实施实机实验，Root/BL 状态不变。

## 2026-10-15 — JVN/CVE 技术归因入档

- 归档 2026-10-14 发布的 JVN#47427200、JVNDB-2026-000147、CVE-2026-107153 与 Rakuten 原公告：确认 Rakuten Hand 5G 全版本的 AVB 使用已知 AOSP 测试钥匙。
- 对照 JVN 引用的 AVBTestKeyInTheWild 论文，记录修改、重签、重建 vbmeta、设备特定部署四阶段；明确论文演示机型不含 P780，跨机型写入方法不能作为本机证据。
- 同步修订 README、STATUS、NEXT_STEPS、固件/OTA 和独立安全公告专题；把后续关卡收敛为 `_162` 原厂 boot/vbmeta 证据与 P780 锁定态写入通道。
- 本轮只做公开资料核对与文档维护，没有运行漏洞、下载执行不可信程序或刷写设备；本机仍未 Root、未解锁，Firehose 与 `_162` 原厂二进制仍缺。

## 2026-10-11 — 全库结构整理与待机监测

- 完整枚举 main 的 254 个文件，以整理前固定提交为基准，保存恢复分支 archive/pre-restructure-20261011。
- 文档按持续专题/来源规范/阶段历史分层；配置原件归位 evidence/device；初轮失败布局证据归位 run 38060293186，原始 Blob SHA 保持不变。
- 删除仅有扩展名不同且字节相同的 critical-delta.txt，保留 critical-delta.md；其它跨运行重复证据保留来源上下文。
- 重写 README、文档/证据/工具导航与待办，补齐时间线、历史验收上下文和当前原件迁移状态；全量修复相对链接及工作流配置路径。
- 候选构建与历史导入改为手动触发，自动归档检查保留并覆盖 Journey 编码原件。每日新线索监测更新为当前 GitHub 基线，仅有实质新增才通知与同步。
- 实际结构提交的 Actions #38069160978 全部通过：258 文件、48 Markdown、337 个相对路径链接/0 失效、10 Python/35 JSON、25 迁移 Blob 身份及原件/视图/字节哈希检查通过。
- 本轮是档案整理；未获取 Root/解锁/匹配原厂镜像。详见 docs/REPOSITORY_AUDIT.md。

## 2026-10-10 — Journey 消费者与匹配语义核对

- 提取性能服务及内部类 134 个有代码方法、类族之外 79 条引用/25 个调用者方法，保存反汇编、调用上下文、6 个决策方法的原始字节及逐 DEX SHA。
- 定位 OOM/进程清理与保留、Service/Provider 黑名单判定；核实末尾星号前缀匹配与精确键查询不同，RootProcess 为应用主进程概念。
- 大型 DEX 完整对象解析耗时过长，改用原始 DEX 表及指令读取；54 个既有配置方法的偏移/字节交叉核验通过，全部所扫描方法指令长度检查通过。
- 合并更新现有 Journey 专题、首页、STATUS、NEXT_STEPS、证据清单；未做实机行为实验，未发现新的 OTA/Root/解锁入口。暂缓扩大此支线，保留系统配置真实性发现及其限制。


## 2026-10-10 — Journey 实机配置核对完成

- 校验机主 3,940 B 配置 ZIP，保存可还原全部原始字节的 Base64、输入 SHA、vendor XML/version 与 TCS 阅读视图。
- XML、version.txt、运行版本均 42；39 条 XML 规则按 ALL 假设得到 64 个策略键，与实机 dump 的全部字段完全一致。
- 核实 panda、qqdownloader 重复键覆盖，不把策略条目解释为安装/系统权限；配置来源仍不能排除同内容缓存。
- 统一修订既有 Journey 报告、README、STATUS、NEXT_STEPS 和证据清单；下一阶段转为离线消费者追踪及匹配原厂固件证据，Root/BL 成果不变。


## 2026-10-10 OTA 与实机 framework 深入审计

补同步 OTA 报告/证据：6 份引擎日志均为启动清理，未得到固件。新增机主 JAR 的 54 个 Journey 方法原始字节、8 类反汇编、17 个外部引用与输入 SHA。定位应用行为 XML → JourneyPerformanceService，未证实 OTA/Root 链；统一修订 README、STATUS、NEXT_STEPS、OTA 与证据索引，记录阶段同步维护约定。原始 18MB framework ZIP/JAR 尚未迁入 Git，保留上传来源。


## 2026-10-10 — 继续研究：配置语义与候选结构布局

- 逐项扫描 24 个消失符号的 Kconfig/C/H/S/Makefile 引用，永久保存原始引用和 provenance。
- 区分 FORTIFY_SOURCE 的 Clang 依赖限制、REFCOUNT_FULL 的实现替换、不可达 NFC 菜单和未被两棵公开树覆盖的配置。
- 增加候选结构探针和 Kbuild 编译参数提取流程；固定两棵源码与 Android Clang11，保存每轮成功或失败工件。
- 首轮 TINNO 构建脚本缺执行权限已记录并修复；探针 TASK_SIZE 名称与内核宏冲突已改名，新增 32 项完整性检查；保留前两轮结果，不冒充完整布局。
- 最终 [#38060518994](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38060518994) 全部通过，两棵固定树各 32 项完整提取、0 项差异；永久保存全部原始工件。
- 专题：[配置与布局研究](docs/research/config-layout.md)。候选布局不代替原厂二进制，未实现 Root/BL 解锁。


## 2026-10-10 — 新一轮原始设备资料归档与去重

- 新收到 2 套 ADB 审计及各自压缩包、完整 Bugreport、三份 APK、两份 OTA 日志、TEE 白名单与 JNI 受限路径记录、phase3 包清单。
- GitHub Actions 校对证实，`hand5g_debloat_audit.zip` 对应展开的 22 个文件、`hand5g_final_audit.zip` 对应展开的 9 个文件**逐字节相同**；删除 31 个重复展开文件，总计 7,576,640 B，保留两个 ZIP 和完整恢复分支。
- 将原件重新组织为 `evidence/restricted/`、`evidence/apk/`、`evidence/tee/`。含敏感数据风险的系统日志不再堆放根目录；备份分支 [archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010) 保存了清理前所有文件。
- 对照旧文件清单，特别区分历史 1,742 B 和本次 376,662 B 的同名审计 ZIP，避免误认为同一份字节原件。
- 新增 [文件去重报告](docs/archive/20261010-import-dedup.md)、[TEE/APK 资料](docs/research/tee-system-apks.md) 和 [OTA/Bugreport 资料](docs/research/ota-bugreport.md)，并更新 README、状态表、时间线、固件与应用清理专题。
- 这次整理为只读离线研究档案维护，没有实机 Root/BL 解锁或获取完整 OTA 的新成功证据。


## 2026-10-10 — 最终封存验收（经 GitHub 实际核查）

- 机主新上传的 **4 份 GhostLock 研究 ZIP** 和 **4,096 B 的 Tracefs 原始文件**已经全部入仓，按来源与用途移动至 `evidence/ghostlock/` 和 `evidence/device/`；使用 Git 已有 Blob 保持字节不变。
- 新建 [完整性报告](docs/reference/evidence-integrity.md)；Actions [#38055450831](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055450831)、[#38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285) 验证压缩包 CRC、SHA-256、ZIP 内部 `CHECKSUMS.sha256`、四版内嵌设备证据与主原件的字节一致性。
- 四个 ZIP 分别包含 **13 / 16 / 17 / 27** 个文件；v0.4 原始 README 首行错误标成 v0.3，已如实在 [版本索引](docs/archive/ghostlock-package-versions.md) 标记，不修改原件。
- 消除 README、GhostLock、Next Steps、文件清单、历史时间线与出处文档中“原件仍未上传”的旧描述；重写仓库首页，明确研究结果和未达成事项。
- 当时尚未迁入的材料已在**随后一轮新增上传**中部分补齐（Bugreport、三份 APK、OTA/ADB 日志），其余继续列入清单。新增原件尚未完成发布级脱敏，详见本日志上方的后续整理记录。
- 已发布 [最终验收报告](docs/archive/20261010-archive-review.md) 与全套双向证据索引；本轮为**资料验收**，没有在实体机运行漏洞、刷入固件、获得 Root 或解锁 Bootloader。


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



## 2026-10-11 — 官方源码请求

- 向 TINNO 官网公开销售邮箱发送 P780 `_162` / 5.4.233 源码对应关系申请，并要求转交开源合规部门；Rakuten Mobile 暂无可靠公开源码专用邮箱，已备日语官方客服文稿但未提交。见 `docs/official-source-request-log.md`。

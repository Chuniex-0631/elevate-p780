# Rakuten Hand 5G（TINNO P780）长期研究档案

> **项目性质：个人实体机的技术研究与历史证据归档。**  
> 研究时间跨度：**2026 年 6 月—2026 年 10 月 10 日**（基于目前可恢复的资料）。  
> 重要结果：**没有实现 Root，没有解锁 Bootloader，也没有取得完整匹配的原厂 `boot.img` / `vmlinux`。**

本仓库保留对一台真实 **Rakuten Hand 5G（P780）** 长期研究的设备信息、测试记录、失败原因、源码核对、离线研究工具、原始取证样本和可重复的 GitHub Actions 编译结果。它是**技术档案**，不是一键 Root 软件或刷机包。

## 一、研究现状一览

| 研究方向 | 目前可确认的事实 | 结论 |
|---|---|---|
| **实体机系统与硬件** | P780 / Android 11 / `P780AE_11.0_RMN_JP_162` / `5.4.233-qgki-gea5245e94afe-dirty` | **实机确认** |
| **Bootloader / Fastboot** | `unlocked:no`；OEM unlocking 开关灰色；常规解锁命令返回 `unknown command` | **尚未解锁** |
| **EDL / Sahara** | 05C6:9008、Sahara v2、`mannar`、HWID `0x0016f0e100000780` | **已识别，尚无 Firehose 分区读取成功证据** |
| **QAS / Mink / PFM / TZAccess** | 识别 eMBMS 许可调用、XRVD 代理建立、服务端凭据与白名单机制 | **部分运行与静态代码证实；没有 OEM Unlock 调用链证据** |
| **GhostLock CVE-2026-43499** | 旧 TINNO 5.4.61 源码存在相关代码模式；实机配置支持 Futex PI；有 Tracefs 标记样本 | **真实 5.4.233 固件漏洞状态未知，适配仍 `BLOCKED`** |
| **内核源码重建** | Qualcomm/A52s 5.4.233 候选树与匹配的 Android Clang 11.0.2 可完成 `olddefconfig` 和 `rtmutex.o` | **构建实验成功，但不是 P780 原厂镜像** |
| **固件 / OTA** | 官方 `_162` 更新始于 2024-03-21；2026-09-28 官方披露固件验证问题 | **公告有据；仍无完整 OTA 和实机成功写入证据** |
| **Journey 系统配置服务** | vendor 版本 42 / TCS 64 键一致；消费者接入进程管理与 Service/Provider 限制，末尾星号匹配已核实 | **独立配置支线；未证实为 OTA/Root 链** |
| **系统精简 / 应用调查** | 历史 ADB 包清理、包/服务枚举和部分应用静态审查 | **已存档，清理脚本不是只读工具** |

→ [**所有问题的当前状态与证据级别**](docs/STATUS.md)

## 二、按专题阅读全部研究

| 文档 | 包含内容 |
|---|---|
| **[最终验收与覆盖范围](docs/FINAL_ARCHIVE_REVIEW.md)** | 最终审核结论、归档覆盖面、已取得/尚未取得的研究成果 |
| [时间线 HISTORY](docs/HISTORY.md) | 从 2026-06-12 的 EDL 到 QAS、GhostLock 和云端源码编译 |
| [真机与启动链](docs/DEVICE_AND_BOOT.md) | 型号、固件号、AVB / Fastboot、Sahara、A/B 分区、失败命令 |
| [固件、OTA 与官方公告](docs/FIRMWARE_OTA_AND_OFFICIAL.md) | 官方版本发布顺序、OTA 取证现状、2026 年安全提示 |
| [QAS / Mink / PFM / TZAccess](docs/QAS_TZ_PFM.md) | Java/DEX/JNI 的身份与许可调用链，已证实和未知的边界 |
| [GhostLock 主线](docs/GHOSTLOCK.md) | 旧源码 CVE 模式、内核编译配置、Tracefs、未获参数 |
| [v0.1—v0.4 研究包版本对照](docs/GHOSTLOCK_PORT_VERSIONS.md) | 四代 ZIP 原始资料、每版新增文件、v0.4 README 历史瑕疵 |
| [设备应用清理历史](docs/DEBLOAT_AND_APP_TESTS.md) | user 0 包数量变化、去预装脚本、可恢复性限制 |
| [新增原件比对与去重结果](docs/NEW_UPLOADS_AND_DEDUP.md) | 新增原始资料、ZIP/目录一致性、清理前恢复分支 |
| [TrustZone 白名单与 APK 原件](docs/TEE_AND_SYSTEM_APKS.md) | 真机 class-ID 白名单、JNI 受限路径、三份 APK |
| [JourneyConfigService 实机审计](docs/2026-10-10-journey-config-audit.md) | 真实 DEX、64 键实机核对、进程管理消费者与匹配语义 |
| [OTA 日志深入审计](docs/2026-10-10-ota-log-audit.md) | 清理任务、配置检查与固件安装的证据区分 |
| [OTA 日志和 Bugreport 归档](docs/OTA_LOGS_AND_BUGREPORT.md) | 原始系统日志、历史 update_engine 痕迹与隐私限制 |
| [全部历史文件及迁移状态](docs/EVIDENCE_MANIFEST.md) | 至少 57 份相关历史文件记录，逐项区分是否已入 Git |
| [证据 SHA / CRC / 相对链接验收](docs/EVIDENCE_INTEGRITY.md) | 核验原始配置、4KB Tracefs、四个 ZIP 与其内部副本 |
| [原始研究来源与出处](docs/RESEARCH_SOURCES.md) | 公开源码与实机、厂商公告、Actions 工件的来源划分 |
| [24 项配置与候选布局研究](docs/2026-10-10-config-layout-research.md) | 源码引用分类、Kbuild 结构探针与每轮构建证据 |
| [后续研究的真实阻断点](docs/NEXT_STEPS.md) | 仍需的匹配固件证据、未得到的符号和 29 项逐构建信息 |
| [归档/更新约定](docs/ARCHIVE_PROTOCOL.md) | 每轮应保存什么、如何避免证据级别混淆 |

## 三、原始证据和历史成果（均为实际已存在文件）

<details>
<summary><strong>设备原始文件与四代 GhostLock 包</strong></summary>

- [真实设备 `p780-config.gz`](p780-config.gz) — **39,170 B**；Android 内核配置
- [真实设备 `p780-cpu4.raw`](evidence/device/p780-cpu4.raw) — **4,096 B**；Tracefs 记录
- [GhostLock v0.1](evidence/ghostlock/P780-GhostLock-port-v0.1.zip) / [v0.2](evidence/ghostlock/P780-GhostLock-port-v0.2.zip) / [v0.3](evidence/ghostlock/P780-GhostLock-port-v0.3.zip) / [v0.4](evidence/ghostlock/P780-GhostLock-port-v0.4.zip) — 原始离线研究 ZIP
- [SHA-256、ZIP CRC 与内部副本交叉核验](docs/EVIDENCE_INTEGRITY.md) — 四个 ZIP 均通过完整性测试，且内置的两份设备证据与仓库主原件**字节一致**

</details>

<details>
<summary><strong>历史实机观察、报告与脚本</strong></summary>

- [实机内核版本](archive/device/hand5g_kernel.txt)、[分区名称映射](archive/device/hand5g_byname.txt)、[44 个已加载模块名称](archive/device/P780_loaded_module_names.md)、[脱敏版早期 EDL 报告](archive/device/P780_EDL_2026-06-12_sanitized.txt)
- [QAS/PFM 全文](archive/reports/P780_PFM_QAS_2026-10-04.md)、[TZAccessService 全文](archive/reports/P780_TZAccess_2026-10-04.md)、[MinkNative 全文](archive/reports/P780_MinkNative_2026-10-04.md)、[GhostLock 源码核对全文](archive/reports/P780_GhostLock_source_audit_2026-10-10.md)
- [历史检查工具](archive/tools) 与 [历史系统清理脚本](archive/scripts)：清理脚本会**修改 Android 用户 0 的应用包状态**，不可当作只读程序执行

</details>

## 四、可重复的内核编译证据

| 实际 GitHub Actions | 结果 | 已永久保存的原始工件 |
|---|---|---|
| [#38051600739](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38051600739) | 首次原生 ARM64 Kconfig 和 Clang14 锁对象最小构建成功 | 日志保留在 Actions |
| [#38052323798](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38052323798) | Clang14：已有值变化 2、缺失 24、新增 327 | [Clang14 原件](evidence/actions/2026-10-10-clang14) |
| [#38053251640](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053251640) | 明确列出 24 项删除配置以及新启用的 Samsung 功能 | [配置差异文件](evidence/actions/2026-10-10-config-delta) |
| [#38053176845](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053176845) | **匹配 Android Clang 11.0.2 (`r383902b1`)**：已有值变化 0，缺失 24，新增 322，`rtmutex.o` 成功 | [Clang11 原件](evidence/actions/2026-10-10-clang11) |
| [#38054396216](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38054396216) | 以上核心 Actions 工件从短期附件转存 Git 仓库 | [永久构建证据目录](evidence/actions) |

**关键界限：** A52s 的 5.4.233 公开候选内核 != P780 实机 5.4.233 私有内核；编译成功**不能**证明原厂代码一致、漏洞可用、Root 成功或已获得可信内核偏移。

## 五、仍未迁移的原始资料（已索引，不冒充“全量原件入库”）

此次已经补入完整 Bugreport、部分 APK、OTA/Activity 日志及 ADB 审计 ZIP，集中存放于 [新增原件目录与审计说明](docs/NEW_UPLOADS_AND_DEDUP.md)。**这些原件尚未完成隐私脱敏，仓库继续保持 Private。** 历史文件库中仍有其它未入 Git 的 Fastboot/getprop 原始转储、APK 和旧分析 ZIP，详见证据清单。还没有取得匹配 `P780AE_11.0_RMN_JP_162` 的可信原厂 `boot.img`、完整 OTA、`vmlinux` 或 `System.map`。

详细原件清单：[EVIDENCE_MANIFEST](docs/EVIDENCE_MANIFEST.md)。隐私及修改设备的风险：[SECURITY](SECURITY.md)。

## 六、目录导航

```text
docs/                     最新结论、研究时间线、证据目录、官方资料与待解决问题
archive/reports/          从历次研究迁入的完整分析报告
archive/device/           脱敏的旧实机文本记录和模块名称
archive/tools/            旧离线研究脚本
archive/scripts/          改动手机配置的历史应用清理脚本（仅存档）
evidence/device/          实机 Tracefs 二进制原件
evidence/ghostlock/       GhostLock v0.1–v0.4 原始 ZIP
evidence/actions/         Clang11/Clang14 配置、日志及编译对象原件
evidence/apk/             新取得的三份 Android APK 原件
evidence/tee/             TZ 白名单、native 库路径访问记录
evidence/restricted/      未脱敏 ADB 审计 ZIP、OTA 日志和 Bugreport（无目录级 ACL）
.github/workflows/        实际已运行的 Linux 构建与完整性检查
evidence/framework/       实机 JAR 提取身份、反汇编与消费者证据\nevidence/journey/         配置原件的可还原存档、阅读视图与状态核对\ntools/                    当前配置/布局及离线 DEX 复核脚本
```

---

**维护规则：每有新的真实实验或分析，先更新 [STATUS](docs/STATUS.md)，同步专题、[文件清单](docs/EVIDENCE_MANIFEST.md) 与 [CHANGELOG](CHANGELOG.md)。保留失败证据，绝不将候选结论写成实机成功。**


## 持续维护约定

每个可核验阶段同步研究文件、结论与说明，修订过时状态、统一专题索引，必要时去重；明确记录原件字节是否已入 Git，避免只追加报告而保留互相矛盾的旧结论。

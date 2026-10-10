# Rakuten Hand 5G / P780：最终归档验收记录

**验收日期：2026-10-10**  
**验收对象：私有仓库 `Chuniex-0631/p780-kernel-research` 的 `main` 分支。**  
**用途：保存所有目前可回收的历史研究**，不等于已复原完整原厂固件或完成 Root。

## 1. 研究领域覆盖

| 专题 | 长期成果的存放位置 | 状态 |
|---|---|---|
| 型号、Android/内核构建、实际开发选项 | [DEVICE_AND_BOOT](DEVICE_AND_BOOT.md)、[原始配置](../p780-config.gz)、[内核版本](../archive/device/hand5g_kernel.txt) | 有直接设备证据 |
| Fastboot / Bootloader / AVB / UFS A/B / 早期 EDL | [DEVICE_AND_BOOT](DEVICE_AND_BOOT.md)、[旧 EDL 脱敏版](../archive/device/P780_EDL_2026-06-12_sanitized.txt)、[分区表](../archive/device/hand5g_byname.txt) | 包含成功探测及失败命令 |
| OTA/更新服务与官方公告 | [FIRMWARE_OTA_AND_OFFICIAL](FIRMWARE_OTA_AND_OFFICIAL.md) 与 [独立安全公告分析](2026-09-28-rakuten-hand5g-firmware-advisory.md) | 官方信息与实机观察分开；原始 OTA 未取得 |
| QAS、XRVD、Mink/JNI、PFM、TZAccess | [QAS_TZ_PFM](QAS_TZ_PFM.md)、[3 份原始分析报告](../archive/reports) | Java/DEX/JNI 路径有实证，OEM 解锁无已证实连接 |
| ADB 软件包清理、诊断服务 | [DEBLOAT_AND_APP_TESTS](DEBLOAT_AND_APP_TESTS.md)、[历史脚本](../archive/scripts) | 记录状态改变，不把历史脚本当只读 |
| GhostLock/CVE 与实机 Tracefs | [GHOSTLOCK](GHOSTLOCK.md)、[实机 4KB 样本](../evidence/device/p780-cpu4.raw)、[v0.1—v0.4 原件](../evidence/ghostlock) | 历史预检全部 `BLOCKED`，不是 Root payload |
| Linux 5.4.61/5.4.233 版本差异与构建 | [GHOSTLOCK](GHOSTLOCK.md)、[Clang11/14 CI 原件](../evidence/actions) | Kconfig 和锁对象编译成功；不是匹配出厂 `vmlinux` |
| 资料来源、原始文件与遗漏 | [RESEARCH_SOURCES](RESEARCH_SOURCES.md)、[EVIDENCE_MANIFEST](EVIDENCE_MANIFEST.md) | 逐项保留原件与迁移状态，不能无证据补齐历史 |

## 2. 原始文件接收及校验

- `p780-config.gz`：39,170B，GZIP 正常，SHA256 已记入 [完整性报告](EVIDENCE_INTEGRITY.md)。
- `p780-cpu4.raw`：4,096B、标记存在；原件已迁移至 `evidence/device/`。
- GhostLock v0.1–v0.4：**四份 ZIP 全部已迁移** `evidence/ghostlock/`；13/16/17/27 条目，CRC 全部通过。
- 四版内部设备配置与 Tracefs 副本与仓库主证据**一致**，不是四份独立实机采样。
- v0.4 内 README 第一行误标 v0.3，保留历史原件，已在 [版本索引](GHOSTLOCK_PORT_VERSIONS.md) 标注。
- [第一次完整性运行](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055450831) 与 [补充内嵌证据核对](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285) 均成功。

## 3. 真实构建记录已永久入 Git

- **源码**：Qualcomm/Samsung A52s 5.4.233 候选树固定 SHA `1f58b196e0dc8de740eb45b51261ea9c5741a30e`；P780 旧厂商源码 **5.4.61** 仍供比较。
- **原厂匹配编译器**：Google Android Clang **11.0.2 (r383902b1)**，预构建源码固定 SHA `659f7cadd7ec920e470bffbb799b031d4344c8d9`。
- **最可信的候选编译观察**：[Actions #38053176845](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053176845)：`olddefconfig` 通过，`rtmutex.o` 构建通过；5,238 实机配置项中已有值变化 **0**，在候选树上 **24 消失**、**322 新增**。
- [Actions #38054396216](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38054396216) 已将 Clang11、Clang14 和配置差异三套构建产物写入普通 Git 历史。

## 4. 对所有既有目标的结论

**已完成：** 实体机软硬件标识、Fastboot/EDL 初级观测、公开源码与相关 CVE 模式比对、QAS/TZ/PFM 的部分调用链审计、实机内核配置与 Tracefs 采样、历史预检版本保存、云端原生 Kconfig 和单对象编译。

**尚未完成：** Firehose 加载器成功授权与分区读取、匹配 `_162` 的原厂 `boot.img`/完整 OTA/`vmlinux`、原厂二进制的漏洞补丁状态与符号偏移、真实 GhostLock root、任意可复现的 Bootloader 解锁。

## 5. 新增原件再次接收与去重验收

- 本轮收到两个完整 ADB 审计 ZIP、对应 31 个逐字节一致的展开文件、完整 Android Bugreport、一组 phase3 包列表、两个更新日志、两份 TZ/JNI 采集记录和三份 APK。
- 保留原始审计 ZIP，删除相同的 22+9 个展开文件；压缩包 CRC、逐文件 SHA 匹配结果详见 [新增原件审计](NEW_UPLOADS_AND_DEDUP.md)。
- APK/TEE 证据见 [TEE_AND_SYSTEM_APKS](TEE_AND_SYSTEM_APKS.md)，系统更新日志与 Bugreport 见 [OTA_LOGS_AND_BUGREPORT](OTA_LOGS_AND_BUGREPORT.md)。仍无实机 Root、Bootloader 解锁或可信完整原厂 OTA 成功提取。
- 清理前仓库全量 Git 快照保留于 [archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010)。所有 `evidence/restricted/` 文件仍可能含个人数据，Private 不是去身份化保证。

## 6. 完整性的严格定义

- 当前的目录、原始报告和 Git 提交已经覆盖**可取得的主要研究结论与设备证据**。
- 早期文件库中至少 **57 份相关历史文件记录**已经索引。**Bugreport、两套 ADB 审计、三份 APK、两份 OTA 日志和 TEE 采集资料现已进入私有仓库**；其它未上传的 APK、Fastboot/getprop 转储和旧源码研究 ZIP 仍列在证据清单中。新增系统转储尚未脱敏。
- 当前可宣布的是“**核心研究成果、原始内核/Tracefs/GhostLock 证据和本轮接收的主要 ADB/TEE/OTA/APK 资料均已归档**”，**不是**“所有过去出现过的文件都已字节级备份或完成隐私脱敏”。
- 如果未来迁移这些敏感原件，应创建数据来源/哈希记录，避免将私有账号、设备唯一标识或未经过审查的二进制公开。
- 将仓库由 Private 改为 Public 前，必须检查完整提交历史，而不只是当前版本。

## 7. 今后继续研究的固定入口

1. 从 [README](../README.md) 进入。
2. 以 [STATUS](STATUS.md) 为当前事实基准，以 [HISTORY](HISTORY.md) 和专题报告追溯旧结论。
3. 新发现只写入有证据级别的专题、[EVIDENCE_MANIFEST](EVIDENCE_MANIFEST.md) 与 [CHANGELOG](../CHANGELOG.md)，及时保留必要原始文件。
4. 在取得实际匹配固件二进制之前，不改变 GhostLock `BLOCKED` 和“未解锁 Bootloader”的状态。

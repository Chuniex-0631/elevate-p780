# 2026-10-10 新增实体机资料接收、比对与去重报告

> 主要结论：本次导入的 ADB 审计原件已经比对，并按资料类型重新归档；**原始资料与研究结论区分存放**。清理前的完整恢复分支：[archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010)。

## 导入验收与处理原则

在整理前，对仓库全部文件进行了 Git Blob（字节身份）分组，并额外通过 GitHub Actions 运行 `tools/audit_new_uploads.py` 对 ZIP 内容与展开目录的单个文件做 **SHA-256** 核对。这比仅比较同名/大小严格。扫描原始日志只输出文件元数据、出现次数、系统配置名称，不把账号、设备标识原文写入文档。

- `hand5g_debloat_audit.zip`：**376,662 B、22 个 ZIP 条目，全部与同名目录内 22 个文件逐字节一致**。保留完整 ZIP，删除重复展开目录。
- `hand5g_final_audit.zip`：**419,387 B、9 个 ZIP 条目，全部与同名目录内 9 个文件逐字节一致**。保留完整 ZIP，删除重复展开目录。
- 本轮共删除了 **31 个可从完整 ZIP 恢复的重复展开文件，7,576,640 B**，仍可以从 Git 备份分支恢复清理前目录。
- 两份审计 ZIP 内还存在小范围重复：如包列表双份相同，角色查询多个相同返回。这些是**采集时原样封装的历史原件**，不强行修改 ZIP 内部以免破坏出处。
- `hand5g_bugreport.zip`：**5,684,665 B、402 条目**，ZIP 格式和 CRC 通过；它是独立的 Android Bugreport，不等同于其它审计包。
- 三份 APK 均为可解压 Android APK（ZIP/DEX 内容完整），但**不代表 APK 内代码已审计或适合安装**。

## 整理后目录

| 资料类型 | 位置 | 说明 |
|---|---|---|
| 真机内核配置和 Tracefs | [核心证据](../evidence/device) 与 [配置根文件](../p780-config.gz) | 历次研究的重要固定证据 |
| ADB 系统快照（原始） | [审计 ZIP](../evidence/restricted/adb) | 完整压缩采集包，ZIP 内分别 22 和 9 个原始文件 |
| 应用清单第三阶段（原始） | [phase3](../evidence/restricted/adb/phase3) | `installed` 210 行包名、`all` 271 行包名；不同过滤条件，不能视为连续两次应用清理 |
| 完整 Android Bugreport | [受限类别](../evidence/restricted/bugreport) | ZIP 内 402 文件；可能含敏感信息，不推荐公开 |
| OTA / 更新服务日志 | [原始文本](../evidence/restricted/ota) | Windows UTF-16 文本，保留原始字节；未发现单独 `payload.bin` 文件 |
| TrustZone 相关只读采集 | [TEE 观察](../evidence/tee) | 白名单原文与 native API 路径访问失败记录 |
| 三份系统 APK | [APK 原件](../evidence/apk) | `ApeHighLights.apk`、`com.qualcomm.qti.services.secureui.apk`、`com.qualcomm.qti.services.systemhelper.apk` |
| Clang/Kconfig 构建原件 | [Actions evidence](../evidence/actions) | 保留完整各次运行，不删除相同的 provenance 文件 |

**注意**：`evidence/restricted/` 只是资料类别和隐私警告，不是 GitHub 的访问控制功能！仓库必须继续设为 Private；Git 历史和清理前恢复分支中均可能保存设备敏感原文。参阅 [安全说明](../SECURITY.md)。

## 真实内容摘要

### ADB / 系统清理

第一份 ZIP 包含 `00_devices.txt`、`01_getprop_full.txt`、`10_packages_user0.txt`、`11_packages_system.txt`、`12_packages_thirdparty.txt`、`31_meminfo.txt`、`32_services.txt`、`33_dumpsys_package.txt`、`34_running_services.txt` 等，属于清理前/某次状态的综合快照，而非独立刷机固件。

第二份 ZIP 保存另外一轮的 packages、processes、services、meminfo、activity-processes 和 package 全量转储等。两份记录可以用于比较不同时间点的功能变化，但**未做严格相同采样条件控制**，不能据此声称性能改善具有可重复统计显著性。

### TrustZone、PFM、更新服务

- `hand5g_tz_whitelist.txt` 从设备取得 Qualcomm **TrustZoneAccess** 服务的 class-ID 白名单原文；包含 10 个对象，例如 `classId 119`（Platform Feature Management）。它的 permissions 数组为空不等于所有调用者可以绕过 Binder UID、证书或安全世界鉴权。
- `hand5g_native_api_paths.txt` 证明若干 JNI 库路径查询当时收到 `Permission denied` 或 `No such file or directory`。保留阴性结果，避免重复得不到权限的实验。
- `hand5g_update_activity.txt` 与 `hand5g_update_log.txt` 为系统 Activity 和 Logcat 快照，并非本次已经提取 OTA。没有从这两份日志取得 `payload.bin`。
- Bugreport 中有 `FS/data/misc/update_engine_log/` 的历史日志路径（包括 2026-06、08、10 的记录），说明设备保存过更新引擎日志，**不能据此推导已经成功取得可刷写固件包**。

## 保留与清理的最终判断

- **删除**：与两个审计 ZIP 逐字节相同的 31 个展开文件，以及此轮临时扫描工具/工作流（完成审查后）。
- **保留**：两份完整审计 ZIP、Bugreport ZIP、三份 APK、phase3 双清单、OTA 两份 UTF-16 原始日志、TEE 两份调查记录。
- **保留原状**：既有 `evidence/actions/` 构建运行报告，即使个别文件字节相同，也用于证明各自运行的来源与结果。Git 本身已按 Blob 去重。
- **不能宣称为原件恢复**：仅在此前私有文件库中存在、这次未上传的其它旧 ZIP/APK/OTA、早期大小 1,742 B 的同名 `hand5g_debloat_audit.zip`。

完整文件接收状态参见 [EVIDENCE_MANIFEST](EVIDENCE_MANIFEST.md)；所有重大已验证研究事实仍以 [STATUS](STATUS.md) 为准。

## 文件名冲突说明

历史文件库曾登记 `hand5g_debloat_audit.zip` **1,742 B** 与 `hand5g_debloat_audit(1).zip` **376,662 B**。此次 GitHub 上传的原件叫 `hand5g_debloat_audit.zip`，体积 **376,662 B**。因此历史小文件不能凭名字认定已归档；本轮保留大包并明确此差别，待原始小包另行检验再决定是否纯重复。

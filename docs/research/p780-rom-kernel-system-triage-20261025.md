# P780 ROM、内核与权限分层复核（2026-10-25）

> 仅基于仓库中已有的文件清单、Release 元数据、内核验证记录及实机实验报告进行**只读复核**。本轮未直接下载或打开数 GB 的 TAR / Image，未接触设备、未执行任何补丁或提升权限实验。与 ROM 元数据相关的逐项数字另见 [ROM 审计](../rom/AUDIT-20261025.md)。

## 1. 内核：已有可复核的本机匹配基线

- `kernel.Image` Release 资产大小 **41,767,424** 字节、GitHub 记录 SHA-256 `6df574af40d260c670c32bdee9ceaca023739850d62851d55f77234b89d4f373`；与此前的 `image-identity.json`、`verification.json` 所用输入一致。
- 既有独立验证记录：**173,205** 个 kallsyms 名称及静态地址核对一致；`256` 个 token、`677` 个 marker；符号地址不递减。合成分析 ELF 的符号回读及 `readelf` 检查有记录。
- 镜像长度等于验证记录中的 `__bss_start` 偏移；内核头声明映射长度 **43,540,480** 字节，差额 **1,773,056** 字节为 BSS。这不单独说明镜像被截断。
- **不能推断**：这些记录不提供原厂完整 `boot.img`、DWARF、C 结构体布局、实机 KASLR 基址，也不能由符号存在推出漏洞可用或永久 Root。
- 对特定 `remove_waiter` 清理路径，静态报告显示**未观察到**公开修复的对应语义；结论局限于已审代码和直接调用者，不等于全内核缺乏等价缓解，更不等于成功利用。

证据：[符号核验](../../evidence/kernel/20261025-symbol-recovery/verification.json) · [镜像身份](../../evidence/kernel/20261025-symbol-recovery/image-identity.json) · [ELF 核验](../../evidence/kernel/20261025-symbol-recovery/elf-validation.json) · [修复核对](p780-static-patch-review-20261025.md)。

## 2. ROM 清单能支持的系统组件定位

下面只是 **文件路径存在性** 的筛选线索，不包含 APK 反编译、ELF 动态分析、包名或运行时权限判定：

| 内容域 | 代表性清单路径 | 下一步合规只读核验 |
|---|---|---|
| `/system` | `priv-app/R_eCare/R_eCare.apk`、`app/R_Link/R_Link.apk`、`etc/init/journey.init.rc`、`etc/init/init.journey_diag_ext_system.rc` | APK manifest / 签名 / 版本、init 服务声明、系统属性来源 |
| `/product` | `priv-app/GmsCore/GmsCore.apk`、`pre-install/R_RakutenBrowser/R_RakutenBrowser.apk`、`etc/selinux/product_sepolicy.cil` | Google / Rakuten 软件清单、权限映射、与系统层依赖 |
| `/system_ext` | `priv-app/Settings/Settings.apk`、`priv-app/SystemUI/SystemUI.apk`、`lib64/vendor.journey.hardware.display@1.0.so` | framework/API 版本、厂商库依赖、服务声明 |
| `/vendor` | `etc/init/vendor.tinno.hardware.faceunlock@1.0-service.rc`、`etc/init/journey.init.vendor.rc`、`etc/vintf/manifest/vendor.journey.hardware.warehouse@1.0.xml` | HAL XML / init 启动配置 / vendor 策略之间的一致性 |

已存的 [2026-10-24 VINTF 补充采集](p780-supplement-20261024.md) 有 **46** 份 XML 的解析记录（38 manifest、8 compatibility matrix）；这些不等于 46 个活动服务，也不等于完成所有 APEX 合并 VINTF 检查。建议优先基于既有副本做静态差异比较，不重复危险的设备提取。

**重要覆盖缺口**：`vendor.tar` 普通文件清单只有 **780** 项，原采集日志记有 **2,127** 项读取失败。不能把其字节大小占比较高当作完整 vendor 镜像的依据，也不能由未列出某文件推断固件根本不存在该文件。

## 3. Root 能力必须按四层分开叙述

| 维度 | 已有实机记录 | 不应夸大的边界 |
|---|---|---|
| UID / GID | `uid=0(root)`, `gid=0(root)` | UID 0 ≠ 所有 SELinux 权限 |
| SELinux | `u:r:installd:s0`; `Enforcing` | 未获得 unrestricted / permissive 域 |
| 文件操作 | `/data/data` 和 `/data/app` 可列举；`/data/app`、`/data/dalvik-cache` 写入测试有记录 | 不等于允许写 `/system`、`/vendor` 或读取任意块设备 |
| 执行与持续性 | `/system/bin/sh` 运行成功；仓库的守护记录显示在一次启动周期内可反复执行受域约束的命令 | 其他系统可执行文件不保证能运行；重启后不持久；Bootloader 仍 Locked |

来源：[Root Shell 实机报告](p780-installd-root-shell-20261025.md) 和 [守护进程验证](p780-root-daemon-20261025.md)。

**证据分层**：这里的“Root Shell 已取得”严格指上述 `installd` 域中的受限 `uid 0` shell，是一次重大实机成果；不是 Magisk 等效权限、SELinux 策略绕过、解锁状态变化或分区永久写入。

## 4. 下一阶段（保持只读/不影响设备）

1. 在本机下载七个 Release 文件后执行 `tools/rom/verify_release.py`，归档完整日志；尤其验证 `product.tar` 拼接 SHA-256。
2. 对 ROM 副本执行 APK 包元数据、ELF 架构/依赖、SELinux CIL 与 VINTF XML **离线静态解析**，形成文件名→属性→版本→证据的矩阵，不运行 APK 或系统二进制。
3. 将 `MISSING.txt` 的 **32** 项和 vendor 采集失败日志标为明确缺口；可重用仓库既有 VINTF XML 副本，不把目录清单说成全分区镜像。
4. 若未来需要评估设备权限变化，必须另记录 UID、SELinux domain、实际允许/拒绝操作及重启后的状态；不以用户界面文案或单个命令输出替代验证。

本轮不修改 `app/elevate/`、不接入应用自动触发、不编写新的设备利用链。

# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：第十二轮确证 DSU 专用重启、单次返回原厂；先停止无效日志重复与试错

**机主直接实测**：第一次 Android15 GSI 安装后，通知 Restart 引发的每次重启都只发生**一次**，未见中途自动重启，直接进入原厂 Android11。`ro.boot.bootreason` 和 `sys.boot.reason` **均为 `reboot,dynsystem`**。此前 `gsi_tool status=installed/disabled`、原厂 Logcat `DynamicSystemService: isInstalled(): true`。故**DSU 专用重启请求已真实生效**，但并未证实镜像成功映射、AVB验签或进入 Android15。

**日志能力边界**：`adb shell logcat -g` 的 kernel 缓冲区 2MiB、实际消耗 **0B**；过滤 `logcat -b kernel` 无任何行；之前 `/sys/fs/pstore` Permission denied。**无消息是可见性不足，不等于 early init 无故障**。这组命令已完成，**不要再重复**。本轮详细证据与 AOSP 分支见 [第十二轮诊断专题](research/p780-dsu-stock-fallback-20261018.md)。

**最新工作假说**：Android11 [DynamicSystemInstallationService](https://android.googlesource.com/platform/frameworks/base/+/978ecf991a9a/packages/DynamicSystemInstallationService/src/com/android/dynsystem/DynamicSystemInstallationService.java) 在启用 DSU 后调用 `PowerManager.reboot("dynsystem")`，与真实 reboot reason 对应；[AOSP first_stage_mount](https://android.googlesource.com/platform/system/core/+/9583e92257ab85075231b014f0999d5a5dab9910/init/first_stage_mount.cpp) 的 `UseDsuIfPresent` 在 `CanBootIntoGsi`、active slot、`MapAllImages` 或指示文件阶段失败时可直接继续原厂启动，符合“无第二次自动重启”的现象。AOSP one-shot 启动在尝试本次启动时就可能把下一次状态标为 `disabled`，所以不能把事后 disabled 当作通知没有 enable。**仍无早期错误日志，不能确认具体根因，更不能认定 AVB 密钥不匹配。**

下一阶段以**离线源码分析和可恢复性评估**为主。暂缓重复 Restart、`gsi_tool enable`（默认 sticky）、`disable/wipe`、其它 GSI 下载，以及为了这个问题贸然恢复出厂/刷分区。若将来需要一次有诊断价值的复现，应先规划如何获取 first-stage 证据、明确数据/Recovery 风险并取得机主针对该风险的单独确认。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

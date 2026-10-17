# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：准备完毕，等待 Android15 GSI 的真实 AVB 公钥（PC 操作，不刷机）

用户已确认继续研究 Google Android15 **无GMS ARM64** 的真实签名公钥。助手完成 [第十四轮离线取证方案](research/p780-dsu-android15-avb-extraction-plan-20261018.md) 与当前聊天附带的 PowerShell+Python 脚本；**仅通过离线模拟，尚未下载目标 ZIP，也未取得新的实际GSI Key Hash**。

- **已核验来源**： Google官方 `vic` GSI目录 + [Android15官方发布页](https://developer.android.com/topic/generic-system-image/releases) 对应 ZIP：`https://dl.google.com/developers/android/vic/images/gsi/aosp_arm64-exp-BP1A.250405.005.C1-13151952-61d23231.zip`，完整发布 SHA-256 `61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`。
- **Windows执行**：把聊天下载的 `p780_gsi_avb_run.ps1` 与 `p780_gsi_avb_extract.py` 放同一文件夹并保证 PC 空间≥12GiB；`powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\p780_gsi_avb_run.ps1'`。脚本用 `curl.exe`下载/续传，核对整个ZIP SHA256；下载官方AOSP `avbtool.py`，从ZIP只提取 `system.img` 和可能存在的 `vbmeta*.img`，经 `avbtool info_image --output_pubkey` 计算真实 AVB blob SHA1/SHA256。任何错误/无footer须保留原文，不推断是否可信。
- **下一轮需要用户提供**：`p780-gsi15-avb/p780-gsi15-avb-report.txt`、对应的 `*.avb-info.txt`、若存在则 `*.avbpubkey`，以及终端成功/失败消息；不要上传多GB ZIP 或 `system.img`。PC脚本sha/边界详见专项文档。
- **比较边界**：六份现有 q/r/s 普通/Developer GSI 公钥只来自公共AOSP源码，**不等于真实P780 ramdisk keys**；提取目标GSI AVB公钥后仍需可靠 `_162` boot/ramdisk文件确认首阶段信任集。结果不是解锁/Root、也不等价于解决 first-stage映射异常。
- **设备保持不动**：GSI已在P780系统中显示 installed/disabled，曾两次 `reboot,dynsystem` 回原厂。现在不再 Restart/Discard/Sticky enable、不重新下载到手机、不修改 Bootloader/AVB。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

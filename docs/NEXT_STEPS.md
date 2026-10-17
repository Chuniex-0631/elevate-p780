# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：DSU 安装服务 user 0 已卸载，保留原厂 APK（第三轮完成）

本轮机主同时提供截图和 ADB 输出：开发者选项 **DSU Loader 可以显示四个在线 ARM64 GSI/GMS 选项**；`am get-current-user=0`；不带 `-u` 的 `pm list packages` **无 `com.android.dynsystem`**；`pm list packages -f -u` 能找到 `/system/priv-app/DynamicSystemInstallationService/DynamicSystemInstallationService.apk`；`dumpsys` 报告 `User 0 ... installed=false ... enabled=0`。**直接证实对 user 0 卸载且系统 APK 保留。** [全证据及来源](research/p780-dsu-locked-gsi-20261018.md)。

历史 ADB 精简脚本两份均将该包列作卸载候选，机主确认本机做过最深度精简，因此用户级卸载最可能源于此前清理，但**没有历史逐包成功执行日志证明具体原因**。注意 `enabled=0` 在 Android `PackageManager` 中表示 `DEFAULT`，不是禁用；Settings 的目录 UI 来自在线 JSON 描述，和 `com.android.dynsystem` 真正安装服务是两步，**能看到 GSI 列表不能证明能安装 GSI**。

**下一可行行动需要机主确认是否恢复官方系统包**（对 user 0 安装记录有改变、不需 Root、不覆盖系统 APK）：

```powershell
adb shell cmd package install-existing --user 0 com.android.dynsystem
adb shell pm path com.android.dynsystem
adb shell dumpsys package com.android.dynsystem | Select-String -Pattern 'User 0:|installed=|enabled='
```

上述命令**尚未运行**，不得自动执行。用户明确愿意恢复后才执行。成功恢复只完成“安装器本身存在”，**不代表 GSI 能启动**。当前列表的 `BP1A.250405.005.C1` 属 Google Android 15 QPR2 GSI，比本机 Android 11 系统新四代；另一个 `CPI1.251209.009.A1` 在本轮未取得官方版别核验。暂不选择任何 GSI、不同意条款、不下载安装或重启。后续只读检查 `ro.vndk.version` 和 ABI，并核对 GSI 包内容/签名与供应商 HAL 兼容。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

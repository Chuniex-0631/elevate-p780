# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：DSU / GSI 在锁定态下的官方受信任启动支持（第一轮只读已完成）

**判定：第一轮 P780 只读已经完成。** `gsi_tool` 文件存在（47,016B），但 `pm path com.android.dynsystem` 无输出；`ls /system/bin/gsid` 返回 Permission denied，不等于文件不存在；三个 `/avb/*-gsi.avbpubkey` 在当前用户空间未找到，但可能属于启动后释放的 first-stage ramdisk；`init.svc.gsid`、DSU 开关和 `ro.gsid.image_running` 三项属性均为空，不能确认为 false。Android 11 `gsid.rc` 设计为 `disabled/oneshot`，不宜据此排除服务。**目前仅能确定部分底层组件存在、标准 UI 未解析到，完整 DSU 支持尚未证实。** [实机+AOSP 专题](research/p780-dsu-locked-gsi-20261018.md)。既非 Root，也非分区写入通道。

第一轮六条**已运行**，以下保留的是之前命令清单（不要重复）；只有机主愿意进一步判断 DSU 是否仅为 AOSP 底层框架，才执行第二轮四条：

```powershell
adb shell pm path com.android.dynsystem
adb shell ls -l /system/bin/gsi_tool /system/bin/gsid
adb shell getprop init.svc.gsid
adb shell getprop persist.sys.fflag.override.settings_dynamic_system
adb shell getprop ro.gsid.image_running
adb shell ls -l /avb/q-gsi.avbpubkey /avb/r-gsi.avbpubkey /avb/s-gsi.avbpubkey
```

第二轮只读：

```powershell
adb shell pm list packages -u | findstr /I "dynsystem gsi"
adb shell ls -l /system/etc/init/gsid.rc
adb shell ls -ld /metadata/gsi /metadata/gsi/dsu
adb shell getprop | findstr /I "gsid dsu gsi"
```

同时在开发者选项中只**观察**是否出现 `DSU Loader`，不要下载/安装/重启任何 GSI。缺失或 `Permission denied` 是有效观察，不能自动推断功能永久不支持。AOSP 某些版本的 `gsi_tool status` 会按需启动 `gsid` 服务，当前严格只读阶段先不调用；更不要调用 `install/enable/disable/wipe`。若依旧无标准包/入口，则**暂停 DSU 支线**，避免投入过多精力在可能只有模板的功能上。

## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

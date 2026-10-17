# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：优先验证 Locked AVB GSI 公钥信任差异 + first-stage 早退（新增高价值方向）

**机主新问题：** P780 的 BL Locked 会不会阻止 DSU？AOSP [官方 DSU 支持](https://source.android.com/docs/core/ota/dynamic-system-updates#verify-boot) 明确允许在 LOCKED 且 AVB 不关闭的情况下启动**受信任公钥签名**的 Developer GSI，前提是 OEM 在 first-stage ramdisk 预装相应 `developer_gsi_keys.mk` 密钥。因此不是“DSU必须解锁BL”，而是**必须有实际签名与设备可信公钥匹配**。

**新增配置疑点 H1**：机主 P780 Fstab 仅见普通 `q-gsi/r-gsi/s-gsi.avbpubkey`，而 Google 公开 Developer GSI 专用的是 `q/r/s-developer-gsi.avbpubkey`（此前六份公开文件哈希两套均不相同）。Google 2021-12-22 从 AOSP 移除普通 Compliance `gsi_keys.mk` 并声明其公钥只需留在 VTS，突出两者用途不同。**不能**把“fstab有q/r/s”视作“可在locked状态下验签 Google Android15 Developer GSI”。但尚未实际读取 P780 ramdisk 或 Android15 system.img 签名，H1仍是**关键假设，不是实机AVB失败证据**。

**同样不能排除 H2**：早前两次 `reboot,dynsystem` 仅单次正常重启返回原厂，AOSP Android11 的 `UseDsuIfPresent()` 在活动DSU槽、`MapAllImages`、`MarkSystemAsGsi` 等失败可直接退回原厂。可能是在**未进行 AVB 验签前**就退出；我们没有 first-stage pstore/LAST KMSG，不能盲判原因。

**新增工具边界**：AOSP Android11 [`gsi_tool status`](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-cts-11.0_r16/gsi_tool.cpp) 仅 UID 0 才会额外输出已安装镜像的 `AVB public key (sha1)`；P780 普通ADB shell只有 `installed/disabled`，重新运行也不会出现Key。不要以未知方法获取提权或强行访问GSID映像。

**下一项真正可复核的工作（PC离线优先）**：1) 获取可靠且匹配 P780 `_162` 的 boot/ramdisk 和 first-stage fstab 原件，以查找实际 `/avb/*` 是否包含 Developer GSI key；2) 获取 Google Android15 `BP1A.250405.005.C1` 镜像 AVB **真实** signing key（仅JSON无pubkey无法核验）并与实际可信公钥二进制或相同哈希算法直接比对；3) 若两者不匹配，锁定态AVB是确定阻断条件；若匹配，则优先检查GSID DSU active slot / image-map 早退。具体证据权重见 [LOCKED BL 与DSU签名专项](research/p780-dsu-locked-bl-vs-gsi-trust-20261018.md)。

**降低其它假说权重但不排除**：[当前 AOSP GSI release 规则](https://android.googlesource.com/platform/build/+/HEAD/target/product/gsi_release.mk) 显式包含 `PRODUCT_EXTRA_VNDK_VERSIONS := 30 31 32 33 34`，因此 VNDK30 在Google构建路线中受支持；但未实际解包当前目标ZIP，不可绝对保证其有兼容APEX或 HAL。用户数据/安全仍优先：不要重复 Restart、`gsi_tool enable` sticky、取消AVB、刷写任何分区。新的高风险实机试验需额外同意和可恢复方案。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

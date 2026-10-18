# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：自签名 GSI × AOSP AVB 测试根密钥的离线对照实验（第十六轮计划）

用户提出将本机确证的 AOSP RSA4096 AVB 根测试密钥漏洞（[JVN#47427200 / CVE-2026-107153](https://jvn.jp/en/jp/JVN47427200/)）与 **DSU 自编译系统镜像 / DSU Sideloader** 结合，测试Locked P780是否可加载第三方系统。**此方案在技术上值得研究，但现在尚未制作/安装/启动自签名镜像**。详细控制变量设计与结论边界见 [第十六轮专项](research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md)。

**关键不能混同的两层：** 真实P780 TEE认可 Bootloader根公钥 SHA256 `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`（公开AOSP测试RSA4096），但 **standalone GSI** 仍经Android11 first-stage `fs_avb::IsPublicKeyMatching` 对 `fstab.avb_keys` 和预加载公钥进行比对，Locked状态不容许未知公钥。P780现有fstab只证实普通q/r/s GSI的路径，没有确认真实ramdisk bytes或额外keystore；给GSI重新用Bootloader测试根私钥签名**不保证通过第二层**。

**首选纯PC离线控制实验，而非先从零编译ROM：** 固定之前下载且SHA已由机主Windows脚本核验的Android15 GSI `system.img` 的文件系统数据、系统补丁及回滚属性，仅在副本上以公开AOSP `testkey_rsa4096.pem` 重新生成合法的 AVB hashtree/footer；保留原版作为A组基线，产生测试根签名B组。用AOSP `avbtool info_image`、`verify_image` 验证两份镜像，记录公钥bytes SHA1/256、原始系统数据段SHA及总大小。**当前只是拟定，尚未签名或执行脚本，不得记录为成功结果**。

**之后再评估机上安装**：官方 [Android Developers DSU](https://developer.android.com/topic/dsu) 和 [VegaBobo DSU Sideloader](https://github.com/VegaBobo/DSU-Sideloader/blob/master/README.md) 都可在无Root时使用AOSP系统安装入口/ADB mode。Sideloader只是前端，不会绕过Verified Boot；该项目要求通常UNLOCKED，因为Locked只接受受信GSI。不得启用第三方Root/System/Magisk/替换gsid模式；不得执行sticky和修改原厂boot/vbmeta。若PC重签的B组**确实通过离线验证且没有事先明确的不可信公钥阻断证据**，在机主明确同意、备份、Recovery失败方案和原DSU镜像替换退出路线确立后，先只安装并在Restart通知前暂停，再另行确认是否重启。

**结果解读**：若控制变量完全一致且B能启动而原Q Developer签名A不能，才是信任密钥差异的强实证；若B也一次重启回原厂，仍不能区分两把密钥均不信任与更早`MapAllImages`等失败，不得循环重试。AOSP测试根密钥漏洞不自动提供任何原厂分区写入通道或Root。

**当前设备状态不改变：** GSID installed/disabled，Android15官方GSI两次 `reboot,dynsystem`只回原厂，Bootloader LOCKED，原有GSI不Discard/Restart直到下一步备份与实验明确批准。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

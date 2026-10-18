# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：已完成 Windows 真正重签 + 完整 AVB 自检；下一步是 Ramdisk 公钥与受控 DSU 安装决策（第十七轮）

**已完成、无需再重签！** 机主上传 v1.1 真实输出三件文本：`original-avb-info.txt`、`testroot-avb-info.txt`、`P780-DSU-testroot-audit.txt`。报告证实1.9GB Google Android15原始 system.img 和测试根重签副本均通过 AOSP `avbtool verify_image`（VBMeta签名、footer、sha256 verity树），且程序严格核对 **VBMeta 2432B 外前/后两个字节区间SHA256均与原件相同**。本轮助手独立读取三份原始小文件比对28个关键参数/属性，唯一实际身份变化是 AVB 签名公钥；descriptor 顺序改变但仍位于VBMeta内部。完整审计/输入 SHA/数据来源见 [第十七轮真实Windows验证报告](research/p780-dsu-testroot-resign-verified-20261018.md)。

| 实验 | 镜像SHA256（用户PC真正算得） | AVB公钥SHA256 | 本机DSU启动 |
|---|---|---|---|
| A：官方Android15原版 | `27321f9655530f014c884a690f49a53e6f3beeda71f4f27cbc141b17a8e86954` | Q Developer `e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925` | 先前两次 reboot,dynsystem 均单次回原厂 |
| B：测试根重签版 | `fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880` | AOSP RSA4096测试根 `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6` | **未安装、更未启动** |

**核心未解**：P780 Bootloader attested Root testkey 匹配B签名，但 Android11 first-stage standalone GSI仍用 fstab/ramdisk `avb_keys` 白名单验签，**不继承Bootloader Root信任**。现有P780 fstab只引用普通Q/R/S GSI公钥，缺实际 `_162` ramdisk文件，B也可能不受信；因此离线 `verify_image`通过绝不等于 Locked P780 GSI启动成功。

**下一步优先**：继续寻找可信P780 `_162` boot/ramdisk真实key bytes与第一次first-stage映像/活动槽早退证据。如果机主希望开展B组上机试验，要先确认备份、Recovery/factory reset最坏后果、剩余空间及当前原版DSU实例安全 Discard/替换方案，然后使用DSU Sideloader的**非Root ADB或Shizuku**模式安装单独 `.img`。`zip`仅是合法DSU package格式，不要把`system.img`随便压成普通ZIP；不能使用Root/System/Magisk模式或替换GSID。**第一次只检查安装成功/失败并停在Restart通知**，启动实验须单独确认。重复无日志价值的Restart不作为诊断方案。

**当前无任何手机变更**：GSID此前installed/disabled，原厂Android11能启动，Bootloader LOCKED、无Root，B在PC保留，后续不得误刷原厂boot/vbmeta。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

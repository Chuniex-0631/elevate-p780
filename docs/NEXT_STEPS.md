# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：Android15 GSI 真实签名公钥已确认：Q Developer；下一项定位 P780 Ramdisk 信任集（第十五轮）

**已完成PC端真正镜像取证，无需重新下载ZIP。** 机主的官方Android15无GMS ARM64 GSI ZIP下载器报告整包SHA256核对通过：`61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`。上传5件小型结果文件，助手读取**实际原始公钥二进制**独立重算SHA1/SHA256，精确与两份 `avbtool info_image` 一致。[第十五轮详细报告](research/p780-dsu-android15-avb-key-verified-20261018.md)。注意本聊天未取得多GB原始ZIP进行再次整包SHA确认，`info_image`不等价于完整`verify_image`签名/verity验证。

| 实际文件 | SHA1（AVB 1032B 公钥） | SHA256（AVB 1032B 公钥） |
|---|---|---|
| Android15 `system.img` | `1ffb1af796b18ebf40d18faed213f686720f73f2` | `e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925` |
| 同ZIP `vbmeta.img` | `2597c218aae470a130f61162feaae70afd97f011` | `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6` |

**重要真正突破**：Android15 `system.img` 原始公钥SHA256 与此前已从公开AOSP二进制独立核验的 **`q-developer-gsi.avbpubkey`完全一致**；与普通 `q-gsi.avbpubkey`（SHA256 `07b373...`）及另外普通R/S不同。P780实际fstab**只见普通Q/R/S路径**，因此 locked状态 AVB公钥缺少Q Developer成为强配置假说，但**尚无本机ramdisk实体或 early AVB 拒绝日志**，不能把这称为已证实失败根因。

**另一项防误判**：这个ZIP的 `vbmeta.img` 嵌入AOSP RSA4096测试根公钥，SHA256恰好与 P780硬件证书 root of trust key哈希一致，**但其 `Flags=2` 是 VERIFICATION_DISABLED，且内含 chain descriptor 的 `system` 公钥SHA1=`cdbb77177f731920bbe0a0f94f84d9038ae0617d`（AOSP RSA2048 testkey），**并不是当前 `system.img` 的 Q Developer 公钥SHA1=`1ffb1...`**。不能视为该 `vbmeta.img` 能授权这份 `system.img` 或已由P780 DSU安装并装载，更不要刷入设备。

**下一项研究（不触碰手机）**：寻找来源可信且**精确匹配P780 `_162`** 的 Boot/Ramdisk/first-stage `/avb/*` 公钥文件，判断厂商是否包含 Q Developer GSI 公钥或其他允许同一key的机制；对比此前 `fstab avb_keys` 普通Q/R/S。若设备信任集确实不包含 Q Developer，则在需要强制AVB验证该system时该镜像**不可能通过该密钥校验**；若包含/匹配，则转攻 `CanBootIntoGsi/GetActiveDsu/MapAllImages/MarkSystemAsGsi` 等 first-stage 映射问题。

**研究停线**：GSID当前 installed/disabled、两次 `reboot,dynsystem`仅回原厂Android11，无 LAST KMSG；不再重复同一Restart/安装、不开sticky、不试刷带`Flags=2`的generic vbmeta、不提出手动`avbctl disable-verification`。Root/BL解锁仍无新进展。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

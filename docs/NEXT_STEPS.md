# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：六个 Google GSI 子目录已完成；转向签名可信性（第八轮）

机主上传 `p780-dsu-catalog-detail.zip`（**4073B；SHA-256 `ad732d61aa7751aeaa6f2a148e3a1998aeee645beb5fe3f344fff98d9ca74c74`**），经离线复核：6份 Google 原始 GSI JSON SHA-256 与 `report.json` 一致、6×4=24个镜像记录、无错误。完整 SHA 表与四条截图匹配见 [第八轮独立核验](research/p780-dsu-gsi-catalog-verified-20261018.md)。**已经完成**前一阶段的子 JSON 搜集，不要让机主重跑。

机主 P780 开发者选项四项全部精确找到：

| 镜像 | 构建 | DSU JSON 安全补丁 |
|---|---|---|
| Android15 GSI ARM64 / +GMS | `BP1A.250405.005.C1`（两条） | 2025-04-05 |
| Android16 GSI ARM64 / +GMS | `CP11.251209.009.A1`（两条） | 2026-01-05 |

**纠错：** 原工具写作 `CPI1`（字母 I），真实是 `CP11`（两位数字1），导致工具的 `report.matches` 只列 Android15 的匹配；源文件中两条 Android16 ARM64 的确完整存在，已对照机主截图复核。不得因此重复 Google 抓取。

**重要新结论：** 6份原始 JSON 的全部24条记录都**没有 `vndk` 和 `pubkey` 字段**；AOSP `DSULoader.isSupported()` 对缺失的 `vndk` 不进行 VNDK列表检查，缺少 `pubkey` 也仅表示无预检查指纹元数据，绝**不**等于镜像未签名。2020–2023 旧 R/S/T/U 的安全补丁比 P780 2024-02 老而被 AOSP SPL 筛选排除；Android15/16 ARM64 各两条留下，说明为何恰好显示四项。**UI 出现并不证明镜像有 VNDK30、实际签名受信或可以在 Android11 Vendor 上启动。**

下一项高价值工作不再是普通 ADB/Getprop 和重新下载同一 JSON，而是 **PC 离线/公开源码核实 Android15/16 GSI 的 AVB 验签钥匙与 P780 Android11 fstab 声明的 q/r/s-GSI AVB 公钥之间的关系、实际镜像包含的 legacy VNDK30、Vendor HAL 运行前置条件**。没有镜像/可信签名资料时不要擅自做兼容性肯定判断。只有在机主明确提出想尝试 DSU 安装、确认数据备份与失败退出恢复计划后才讨论具体 GSI 的 GB 级下载。当前**不执行 DSU ZIP 下载、设备镜像安装、重启、`gsi_tool enable/wipe` 或其它写入操作**。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

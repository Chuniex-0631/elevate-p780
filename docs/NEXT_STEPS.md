# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：DSU 官方主索引已验证，等待 6 个子 JSON（第七轮）

**此前已完成、无需重复的实机任务**：原厂 DSU 安装器已恢复 `installed=true`；DSU Loader 菜单中确实出现四个 ARM64 GSI/GMS 选项；P780 Android11 的 Treble、`[vendor] namespace.default.isolated=true`、VNDK30、`arm64-v8a` 和 103GB 可用存储报告已取证；尚未下载安装或启动 GSI，Bootloader 仍 LOCKED、无 Root。

**本轮新增独立 PC 工件**：机主从 AOSP 默认目录 `https://dl.google.com/developers/android/gsi/gsi-src.json` 成功下载 **508字节** 的 `p780-dsu-catalog.json` 并上传当前会话；已重新计算 SHA-256 与 PowerShell 输出 **`0A1970ABFCEB6BF3962177881B255E6AF9D4F43903AAC3BA9AEF2C1E5B4A2D09`** 完全一致。文件自身**只有**6项 `include`（`rvc/sc/tm/udc/vic/baklava`），没有任何 `images` 详细字段。未取得六份实际子 JSON，不得宣称截图中 `BP1A.250405.005.C1` / `CPI1.251209.009.A1` 具备 VNDK30 或已通过 DSU AVB 验签。

**下一行动（PC 只读，禁止下载镜像）：** 用户可在与主 JSON 相同的 Windows 文件夹使用本会话附上的 `p780_dsu_catalog_audit.py`。标准库脚本已通过**离线模拟测试**，尚未在真实 Google 子目录联机实测；它会限制 Google HTTPS JSON 的目标域、单项≤1 MiB、最多20项及3层递归，并输出包含真实响应与 SHA-256 的 `p780-dsu-catalog-detail.zip`，只发送此小 ZIP 即可。目标是确定实际 `cpu_abi/os_version/vndk/spl/pubkey/uri` 字段（URI 仅存字符串，不访问 `.zip`）。

```powershell
# 把聊天提供的 p780_dsu_catalog_audit.py 保存到这个已含 p780-dsu-catalog.json 的文件夹后执行：
python .\p780_dsu_catalog_audit.py
# 输出文件：p780-dsu-catalog-detail.zip；上传该 ZIP 和终端摘要
```

**观察限制**：主索引来自机主 PC，而不是 P780 本机抓包；即使 `.list` 属性为空，也不能绝对确定 P780 实际访问目录就是该 URL。官方 [DSU JSON descriptor](https://source.android.com/docs/core/ota/dynamic-system-updates) 允许包含更多目录且 `pubkey`、`vndk` 都为可选字段，不出现某字段不能自行假定验签/兼容通过。研究环境当前无法直接拉取六份子 JSON，不能用其他机型日志代替官方当日原件。[第七轮专项](research/p780-dsu-locked-gsi-20261018.md)。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

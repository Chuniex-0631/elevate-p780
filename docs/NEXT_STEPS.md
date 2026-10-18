# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：PC 自签名 GSI 对照工具 v1 已交付，等待真实 AVB 运行报告

**用户希望立即继续第十六轮AOSP测试根密钥实验。** 本轮交付仅 Windows PC 使用的 ZIP `P780-DSU-testroot-offline-tools-v1.zip`（9769B，SHA256 `189d3a4b6e92eea0cc21e24dfde29950a981b35bef72c6997925bcc26ee4dab6`），含PowerShell引导器、Python脚本、中文说明；链接由**当前聊天附件**提供，不使用自动下载到设备，手机尚未操作。完整设计、各脚本哈希和证据级别见[第十六轮自签名DSU专题](research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md)。

**v1实验方法比原计划更严格**：对前轮 Google 官方Android15 `p780-gsi15-avb/system.img` 保留原始fs、Hashtree、FEC、Footer 和所有offset/size，**只在单独副本中重新生成并替换2432B 嵌入式VBMeta**，密钥采用公开AOSP `test/data/testkey_rsa4096.pem`（公钥SHA256必须等于P780 TEE证实的`7728e30f...6defef6`）。用 `make_vbmeta_image --include_descriptors_from_image` 复用原始verity树描述符与系统属性；运行前后独立 `verify_image`、比较**非VBMeta全部数据字节哈希**、key身份/SPL/rollback/algorithm/flags等严格匹配，任何不符拒绝输出成功报告。使用新AOSP VBMeta并**未关闭AVB**（Flags=0），也不会触碰官方ZIP附带的`Flags=2`通用vbmeta。

**实际运行条件**：Windows Python3.9+、`openssl.exe`在PATH、上一轮 `avbtool.py`、现存经GoogleZIP校验的 `p780-gsi15-avb/system.img`，输出磁盘≥3GiB。解压后PowerShell：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\\p780_dsu_resign_run.ps1"`。PS只在未提供测试Key时从 AOSP Gitiles 官方位置下载公开样例private key，Python再将其公钥与已确认的硬件AVB根公钥SHA256做精确比较。

**下一轮请机主反馈**：只上传 `p780-dsu-testroot-output/P780-DSU-testroot-audit.txt`、`testroot-avb-info.txt` 或运行错误原文。不要上传1.9GB`system.img`；也不要在无单独实验审批下通过DSU Sideloader安装/重启。**此环境测试范围为 Python语法、实际先前system.avb-info元数据校验、模拟avbtool端到端差异验证**；未真正拿到多GB原图/GoogleAOSP原版avbtool执行签名，**尚无真实重签成功实证**。

**真正待证问题不变**：Bootloader Root测试密钥认可不等于first-stage standalone DSU Fstab允许该key。P780 Fstab只见普通q/r/s GSI key路径、原官方Android15 `system.img`用Q Developer key。若控制变量B组离线签名成功，仍需要匹配P780`_162` Ramdisk信任Key集合和恢复/备份风险评估，才能考虑进行新一轮上机实验。不能把AVB自检通过当作Locked DSU会启动。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

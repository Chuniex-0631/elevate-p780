# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：Bugreport 取证完成，停止重复相同的软件日志采集（第十三轮）

**机主真实 Bugreport 已离线读取：** `P780-DSU-Bugreport.zip` ZIP有效，共362成员，SHA-256 `64a097d0911e35675c75dff09d68a7e28b5aa15bd342ed796387d12758d5f141`；主文本19,721,044B / 240,297行。**不将原始敏感档案提交到 GitHub**，只存字段、校验和、结果。[第十三轮独立报告](research/p780-dsu-bugreport-audit-20261018.md)。

**新增四条硬证据：**

1. `persist.sys.boot.reason.history` 中有 `reboot,dynsystem` 两项，分别为UTC+8 **2026-10-18 06:30:31、06:31:30**；是两次真实 DSU 专用重启的持久历史（不是设备自主循环重启）。
2. `gsid.image_installed=1`、`ro.gsid.image_running=0`、`init.svc.gsid=stopped`，原厂 `/dev/block/dm-*` 设备映射表仅见 B 槽 `system/vendor/product` 等分区，无活跃DSU映射；这些只能描述报告采集时原厂运行状态，**不能倒推早期启动的失败点**。
3. `dumpstate` 明确报 `Error dumping /proc/last_kmsg (LAST KMSG): No such file or directory`；`incidentd` 同时打不开 `/sys/fs/pstore/console-ramoops`、`console-ramoops-0` 和 `/proc/last_kmsg`；`logcat -L` 返回退出码1。**上一轮 DSU 的 kernel/last logcat未成功采集**。
4. 当前 `dmesg` 虽有约2635行，最早时间戳已是开机后的 **943秒**，不包含 first-stage 时段，找不到 AVB/DSU/映射错误并不能证明根本不存在这些错误。

**后续现在不要再重复：** `adb bugreport`、`logcat -b kernel`、`logcat -L`、读取 pstore/last_kmsg、普通状态 getprop 或第三次同参数通知 Restart。这些途径已经实际验证信息有限。仍保持 DSU已安装、原厂Android11可启动且未 Root/解锁。

**新的真正优先事项改为离线核对**：寻找**可信且匹配 P780 `_162`** 的 boot/ramdisk、第一阶段fstab和 init 二进制/源码证据，独立获取 Android15 候选GSI的 AVB Signing Key信息，逐项核对AOSP `CanBootIntoGsi/GetActiveDsu/MapAllImages/MarkSystemAsGsi` 失败分支与P780原厂启动配置；不能以未读取的设备公钥作为已确认。若新资料提供了具体根因和可回退的修复变量，再与机主讨论一次**有诊断差异**的复现；之前应确认备份、Recovery最坏结果、得到新的明确同意。

**数据保护**：Bugreport原件和此前4.1MB Logcat可能含账号、序列号、MAC、网络SSID、地理/通讯信息，只保留在机主本地或当前私有会话；仓库仅脱敏索引，不上传原文件。若机主日后决定释放数GB临时GSI空间，可在保存所需证据后再经官方 DSU `Discard`，并非必须永久保留以供取证。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

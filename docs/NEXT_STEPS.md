# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：首次 DSU 下载后重启返回原厂系统——进入非破坏性诊断

**机主在 P780 实际观察：** GSI 下载完成后 Settings/DSU 通知提示重启进入 DSU。至少两次由机主**手动点击 Restart**触发重启，但每次都返回原厂 Android 11，并保留同一提示。**这不是自主连续重启的 bootloop，也不是 Android 15 已启动成功。** 原厂系统现在仍能开机。镜像下载内容的确切 `BP1A` ID 需由通知/日志确认（此前推荐值不能冒充当轮确认）。

**下一步停止线**：立即停止重复重启，不点击 Discard（先保留临时镜像/启动证据），不执行任何 `gsi_tool enable/disable/wipe`、Fastboot/EDL 强制刷写或安装其他镜像。目前已有足够实验现象，但**尚未拿到 DSU backend 状态或早期启动日志**，不可直接将原因判为 GSI AVB 签名、VNDK30或 Vendor HAL 错误。

Windows PowerShell 当前原厂系统状态下先提取日志，再做状态查询：

```powershell
adb logcat -b all -d -v threadtime -t 15000 > ".\p780-dsu-after-reboot.log"
Select-String -Path ".\p780-dsu-after-reboot.log" -Pattern 'dsu|gsid|gsi|DynamicSystem|first_stage_mount|avb|verity|liblp|rollback|ImageManager' | Set-Content ".\p780-dsu-filtered.txt"
adb shell getprop ro.gsid.image_running
adb shell getprop ro.boot.slot_suffix
adb shell ls -l /sys/fs/pstore
adb shell gsi_tool status
```

**隐私和限制**：完整 logcat 可能包含设备标识/隐私，先仅上传 `p780-dsu-filtered.txt` 和最后四条终端输出；避免上传完整证书、bugreport 或没有脱敏的完整日志。重启通常重建 logcat；前次 DSU early init 错误有可能已经不可读。`gsi_tool status` 可按需启动 gsid，所以排在保存日志之后。只读诊断会帮助区分 installed/enabled、installed/disabled、normal、权限错误及从 kernel/pstore 是否存在早期证据。

**AOSP 实现关键路径**：Android11 `gsi_tool.cpp::Status` 查询 `isGsiRunning/isGsiInstalled/isGsiEnabled`；`first_stage_mount.cpp::UseDsuIfPresent()` 若 `CanBootIntoGsi` 条件不足会 “proceeding with normal boot”，映像 MapAllImages 失败也会返回。因此 **DSU 按钮存在与 early boot 能成功切换，是两个独立状态**。后续针对具体日志分析，不为再次试错强制打开 sticky mode。

本轮 [首次返回原厂系统/重复提示诊断专题](research/p780-dsu-stock-fallback-20261018.md) 记录完整分层假说、取证命令与风险边界。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

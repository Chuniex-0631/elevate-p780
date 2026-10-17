# P780 下一步研究计划（2026-10-18）

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 路线 A：DSU 已安装、one-shot 重启后被禁用；下一步只读内核启动缓冲区（第十一轮）

机主完成第一次 Android15 DSU 试验：下载后通知提示 Restart，但人工点击两次均返回原厂系统；本轮进一步证实 `gsi_tool status`→两行 **`installed`/`disabled`**，当前 `ro.boot.slot_suffix=_b`，`ro.gsid.image_running` 为空，`/sys/fs/pstore` 普通 shell Permission denied。**原厂Android11可正常开机，Android15未观察到运行。**

机主上传 `p780-dsu-after-reboot.log`（~4.1 MB UTF-16LE、15455行，SHA256 `955c9775371658b36d59e749c648149193a05746a72d26807f09a3f97de6e970`）与筛选文件（678B/3行，SHA256 `333d7ac1de09d46f4a77a3611842a38d47c0ec14819d2b2b23d6ebfb2a74cf76`）。**Logcat 实际出现** `DynSystemInstallationService onStartCommand NOTIFY_IF_IN_USE`、`DynamicSystemService: isInstalled(): true` 和通知入队，直接支持安装状态存在；未出现能定位早期 AVB/mapping/HAL 错误的日志。完整原日志**不上传GitHub**。[第十一轮日志证据与精确解释](research/p780-dsu-stock-fallback-20261018.md)。

**AOSP 源码决定性的语义校正**：Android11 [libgsi::CanBootIntoGsi](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-platform-11.0.0_r16/libgsi.cpp) 在遇到 one-shot 标志时，**先把安装状态写成disabled（影响下一次引导）然后允许本次启动继续**；Android11 [DynamicSystemInstallationService](https://android.googlesource.com/platform/frameworks/base/+/978ecf991a9a/packages/DynamicSystemInstallationService/src/com/android/dynsystem/DynamicSystemInstallationService.java) 默认 one-shot。故**重启后 status=disabled不能视作通知按钮没启用成功**；它完全符合 first-stage 消费一次启动机会后映像映射/AVB/后续 init 失败并回原系统，但当前没有直接 first-stage 证据，也保留其它状态清除来源可能。

后续若需要，可仅执行以下**无需重启、不修改状态**的查询，失败/权限拒绝原样记录即可：

```powershell
adb shell logcat -g
adb shell logcat -b kernel -d -v threadtime | Select-String -Pattern 'DSU|GSI|first_stage|AVB|verity|mapped|rollback|init'
adb shell getprop ro.boot.bootreason
adb shell getprop sys.boot.reason
```

当前明确**不**建议再次点击Restart、`gsi_tool enable`（默认sticky）、手动编辑 `/metadata/gsi`、`gsi_tool wipe`、安装Android16或重新下载镜像。`/sys/fs/pstore` 已权限拒绝，不能以用户未提供pstore为由要求Root或其他绕权。可能需要额外恢复风险评估后才设计下一次**受控**的启动前后日志采集，不应因单次状态disabled自行断言签名不匹配。
## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

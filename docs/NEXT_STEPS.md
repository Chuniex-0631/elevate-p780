# P780 下一步研究计划（2026-10-18）

> **2026-10-18 batch2：** system/lib64 的514项大小/SHA-256全部匹配PC清单（509 ELF、5 bitcode）。通用 bootloader message 库不等于 Journey builtin，尚未建立调用链或新增Root能力。详见[第二批交叉分析](research/p780-static-batch2-analysis-20261018.md)。

> **2026-10-18 SELinux原件审计：** 已查询ODM预编译策略并复核三组CIL/mapping配套摘要。Journey sys属性映射debug_prop，编译策略允许shell设置；config.write、ODM reset及默认vendor诊断开关没有同等shell allow。root socket的0666不能绕过SELinux，本批未见shell连接许可。仅形成静态候选，未写属性或取得Root。详见[权限边界审计](research/p780-policy-boundary-audit-20261018.md)。

> **2026-10-18 batch1原件分析：** ZIP中742个文件条目已逐条重算大小/SHA256，全部匹配1759项PC清单中的对应内容；提取init service声明与ELF依赖。ST factory链确认属于NFC测试；Journey root诊断socket/属性动作仅为待核验权限边界，尚无可利用证据。下一步补SELinux静态映射，不运行工程动作、不恢复DSU重试。详见[原件验证与交叉分析](research/p780-static-batch1-analysis-20261018.md)。

> **2026-10-18 20:31 更新：DSU 路线已由机主停止。** B已安装并尝试原生启用/重启，最终回到原厂Android11，Locked/green、installed/disabled；并非“B尚未上机”。失败阶段未知，不能认定厂商禁止DSU。恢复出厂后的原生Loader回退为用户报告，镜像身份未核实。最新实机证据、系统数据段哈希、安装器静态审计及新路线见[阶段收束与维护接口审计](research/p780-dsu-closure-maintenance-route-20261018.md)。当前优先审计原厂维修/工厂测试/更新组件的权限与可核验读取入口；不重复DSU测试，Root/解锁仍未取得。下文与此冲突的DSU待测状态为历史记录。

**本文件只保留最新可行动计划，不再把已完成工作列为“待测”。** 过往工作已归档至 [2026-10-18 DSU 之前的历史计划](archive/next-steps-before-dsu-20261018.md)、[研究状态](STATUS.md)、[证据总表](EVIDENCE_MANIFEST.md)及相关专题。设备仍 **Bootloader LOCKED、无 Root**；没有可信 `P780AE_11.0_RMN_JP_162` 分区镜像、可用签名匹配 Firehose 或真实 locked 写入证据。

## 当前确定的事实

1. **AVB 根公钥已经本机核验**：Google 2019 Hardware Key Attestation 签名链/TEE 状态由机主 `.p7b` 与公开 AOSP 默认 `testkey_rsa4096_pub.pem` 1032-byte AVB 表示匹配：`verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` 与既有 ADB `ro.boot.vbmeta.digest` 完全一致。根/中间/叶证书签名验证有效，正式完整在线吊销校验仍缺。[实证](research/avb-attestation-confirmed-20261018.md)。不需要再重复 Key Attestation。
2. **Fstab 两份已读取**：`system/system_ext/product` 使用 `avb=vbmeta_system`；`vendor/odm` 使用默认 `avb`。`system` 额外包含 `/avb/q-gsi.avbpubkey` 等三份 Google 开发 GSI 公钥文件路径候选。[Fstab 实测](research/p780-fstab-avb-20261018.md)。但仍未读取真实 `vbmeta_b`、`vbmeta_system_b` 或 chain descriptors。
3. **已完成但没有结果的尝试**：Fastboot 常见 OEM 解锁指令均为 unknown command；EDL Sahara 可识别但没有兼容且授权的 Firehose；Google OTA Prober 对当前 `264` fingerprint 无 `update_url`。不再重复这些请求；OTA 支线暂缓。对应 [启动/EDL](research/device-and-boot.md)、[OTA](research/google-ota-prober-p780-20261018.md)。

## 当前主线：实机静态样本建库与交叉分析

原厂工程/维护APK已排查无线索，不重复作为独立新路线。机主已完成第一批广覆盖只读提取，本地清单1759项/1131297358字节；已收到并核验 batch1 的742项与 batch2 的514项原件，尚非完整固件。已完成 init 声明、ELF依赖、SELinux映射及编译策略查询。batch2 未建立 Journey builtin 实现链，通用 write_misc_partition 不等于厂商 write_misc。下一步利用已有框架/native样本建立调用者、接口、策略许可和服务端实现的证据表；缺失服务端保留为缺口，不重复受拒绝的文件读取，不设置工程属性、不发送socket命令、不触发擦除或重启。

优先读取电脑已有init配置，再按实际依赖选取native/框架原件。vendor/bin、vendor/lib64采集0文件，部分目录跳过及两个零字节项须区分；不能把完整清单称作完整固件。详见[清单审核和缺口](research/p780-static-corpus-inventory-20261018.md)。

## 主要路线 B：真正阻挡永久 Root / 自定义 Boot 的环节

**B1. 只读离线镜像发现**：仅考虑机型为 P780 且有原始构建编号、文件哈希与可信出处的 `vbmeta[_system]`, `boot`, `vendor_boot`, `dtbo`，包括各官方历史版本，但必须注明与 `_162` 的差异。得到镜像后用 AOSP `avbtool info_image` / `verify_image` 分析主 vbmeta→system chain descriptors、rollback indices、boot 分区是否 AVB hash footer；不能从 fstab 或 `7744` 字节 VBMeta 总大小反推出真实描述符。**暂不继续批量搜/探测 OTA。**
**B2. P780-specific 写入/维修路径证据**：寻找有原始终端日志与设备 firmware/HWID 对照的合法厂商恢复程序、signed Firehose 与受锁定状态限制的写入路径；不以同 Snapdragon 平台的 loader 或其它型号成功日志替代 P780 实测。不在现阶段执行 EDL rawprogram、Fastboot flash、sideload 或改写 AVB/boot。研究重心是证据真实性和恢复可行性。
**B3. 内核动态漏洞路线保留但不抢占主线**：GhostLock 因 `_162` 对应内核 ABI、未剥离符号和偏移信息不足而 BLOCKED；其它候选源码与 A52s 只能作比较，不是可执行 P780 root。[详见主线](research/ghostlock.md)。

## 安全与证据规则

- 不导出原始完整 `.p7b` 到 GitHub；其硬件身份相关证书只留在机主设备和本聊天，研究仓库存脱敏公钥/摘要/验证方式。
- 确认 AOSP **默认 AVB 测试私钥**是启动链信任缺陷证据，**不是**自动赋予 locked Fastboot/EDL 写权限；不能用 `signapk`（OTA ZIP 签名）替代 `avbtool`。
- 不再重复普通 `getprop` 穷举、试猜构建指纹、随机 Firehose、主动催促厂商/JVN 或无原厂可恢复镜像的写入测试。收到主动回信只验证来源、避免泄露设备身份信息。
- 新技术进展到一定阶段才同步 STATUS、相关专项、EVIDENCE_MANIFEST、README、CHANGELOG；没有新设备数据不得标记“本机已证实”。监测自动任务开关需要单独根据实际状态确认，仓库内过去的“已启用”文字不是任务运行证据。

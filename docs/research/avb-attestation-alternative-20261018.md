# P780 AVB 研究：无需原厂镜像的硬件证明替代路径（2026-10-18）

> **新增研究假说，尚无 P780 本机 Attestation 实测。** 先前四轮 ADB 实测与来源见 [AVB 基线](avb-live-baseline-20261018.md)。本专题源于用户要求交叉分析既有证据，并非宣称已经取得 AVB 公钥或 Root。

## 为什么这条路径有价值

已知本机启动基线：`green`、`locked`、`_b`、`ro.boot.vbmeta.digest=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`；根 `vbmeta_b` 和候选链 `vbmeta_system_b` 的块设备是 `root:root 0600`。属性 `ro.boot.vbmeta.public_key_digest` 未暴露。

AOSP [Key/ID Attestation 文档](https://source.android.com/docs/security/features/keystore/attestation) 对 `RootOfTrust` 的定义：

| 字段 | 官方语义 | P780 可否取得 |
|---|---|---|
| `verifiedBootKey` | Verified Boot 根信任公钥的安全哈希，推荐 SHA-256 | **尚未测试**；它不是私钥、也不是原始 `vbmeta.img` |
| `verifiedBootHash` | AVB 参考实现通常为完整 VBMeta Digest | **尚未测试**；若存在可与本机 `33ee…95f2` 对照 |
| `deviceLocked` | Bootloader 是否在证明记录中为锁定 | **尚未测试**；预期与已知 `locked` 相容 |
| `verifiedBootState` | Verified / SelfSigned / Unverified / Failed | **尚未测试**；预期与 `green` 相容 |
| `attestationSecurityLevel` | TEE / StrongBox / Software 等证明来源 | **必须记录并核验** |

[AOSP Keystore CTS 代码](https://android.googlesource.com/platform/cts/+/master/tests/tests/keystore/src/android/keystore/cts/KeyAttestationTest.java) 在 `checkVerifiedBootHash` 中检验 `rootOfTrust.verifiedBootHash` 和 `ro.boot.vbmeta.digest`；新版环境也比对 `verifiedBootKey` 与公开属性，但 **P780 所属 Android 11 设备未必实现较新属性或全部字段**。

关键点：**Keystore 密钥证明是一条普通应用可尝试的公开 API 路径，不需要 `adb pull /dev/block/*`、Root 或解锁**。但请求可能失败、TEE 未提供硬件证明、字段缺失或证书链不可信。任何一种结果都必须保留原样，不能冒称研究成功。

## 建议使用经验证来源的开源应用（可选实机试验）

[KeyAttestation（vvb2060）](https://github.com/vvb2060/KeyAttestation) 是生成、解析、保存和验证 Android Keystore Attestation 证书链的开源应用，GitHub [Releases](https://github.com/vvb2060/KeyAttestation/releases) 提供 APK。2026-10-18 查询的 latest 为 `v1.8.4`，GitHub API 报告发布于 2025-01-16，APK 为 `KeyAttestation-v1.8.4.apk`，约 1.33 MB。源码 `app/build.gradle` 声明 `minSdk=24`；仓库 README 声称无需网络权限，源码 `app/src/main/AndroidManifest.xml` 不请求 `android.permission.INTERNET`。**未独立校验发行 APK 的最终合并 Manifest 或重现构建**，下载仅走官方发布页；不能把此判断解释为任意来源 APK 安全。

普通模式：无需 Root、Shizuku、ID Attestation、StrongBox 强制模式或用户设备唯一身份信息。安装 APK 会正常修改用户应用目录/Keystore 中的测试密钥（**不是无状态操作**），但不改变 bootloader、原厂分区或 COW。若担心第三方 APK，也可选择未来自行审计源码并编译最小示例。

只收集/分享以下**最小必需字段的文本或裁剪截图**：

1. App 生成的 **Attestation Security Level**（TEE/StrongBox/Software）；证书链验证结果（Trusted/Untrusted/Error）；
2. `Root of Trust → verifiedBootKey`（注意它是 bytes，可能显示 Base64 或 Hex，记录原编码）；
3. `Root of Trust → verifiedBootHash`（若有；拿既有 digest 作交叉检验）；
4. `Root of Trust → deviceLocked` / `verifiedBootState`；
5. 任何实际错误信息（`StrongBoxUnavailable`、`KeyStoreException` 等），不尝试绕过限制。

**隐私/可信度**：不要上传原始完整证书链、设备 ID、IMEI/序列号、帐号数据、Keybox 或生成的私钥。证书可能含应用标识、制造商和其他可关联字段。屏幕内容只是初步证据；要声称硬件真实证明，仍需单独验证证书链、正确根证书与吊销状态，并把软件声明与硬件 TEE 字段区分。[Android 官方验证指引](https://developer.android.com/privacy-and-security/security-key-attestation)。

## 与 AOSP 默认 AVB 密钥的联动

[AOSP build/core/Makefile](https://android.googlesource.com/platform/build/+/master/core/Makefile) 指明，未自定义 BOARD_AVB_KEY_PATH 时，默认算法 `SHA256_RSA4096`，示例测试钥匙 `external/avb/test/data/testkey_rsa4096.pem`；[AOSP AVB README](https://android.googlesource.com/platform/external/avb/+/android11-release/README.md) 同样记录这一点。**这只是候选，并不是已确定 P780 实际使用的钥匙**。

离线验证时，可对官方 AOSP 仓库的候选公钥生成 AVB 专用公钥 blob（`avbtool extract_public_key`），计算 SHA-256，并与得到的 `verifiedBootKey` 比较。需要注意 TEE 对根密钥的哈希输入编码可能和 AVB blob 不同；**简单的 SHA256(blob) 不匹配，不能直接证明不是该钥匙**。应注明算法、编码、钥匙来源/源码提交 SHA 和证书可信度；不能将证书链信任根公钥与 AVB 启动信任公钥混为一谈。

若 `verifiedBootHash` 与已有 digest 相同，独立地增强已知启动数据的一致性；**仍不能反推出原始 VBMeta 或 Chain Partition Descriptor**。

## 第二条无需完整镜像的配置交叉线索：fstab

[AOSP 动态分区实施文档](https://source.android.com/docs/core/ota/dynamic_partitions/implement) 说明：fstab 的 `avb=vbmeta_partition_name` 决定 Android first-stage mount 为指定逻辑分区采用哪一组 AVB 元数据。

以 `adb shell ls /vendor/etc/fstab*` 确认实际存在的文件；如果 `/vendor/etc/fstab.qcom` 可读，再执行 `adb shell cat /vendor/etc/fstab.qcom`。可以检索 `avb`、`logical`、`first_stage_mount` 等 flags，判断 system、vendor、product、odm、system_ext 指向哪一份 vbmeta。**fstab 的声明并不等于取得了 root vbmeta 的签名描述符、完整信任链或 AVB 公钥**。如果文件不存在，无需遍历受限目录和尝试越权。

## 路线优先级

1. **P1：Keystore Hardware Key Attestation** —— 最有机会直接获取可独立比对的 AVB 根公钥摘要（条件：P780 TEE 支持且返回可信记录）；不会提供签名私钥/刷写权限。
2. **P2：fstab 静态映射** —— 最有机会补全从 `vbmeta_system_b` 至受保护逻辑分区的配置关系。
3. **P3：公开 AOSP 候选钥匙离线编目** —— 在拿到可核验 `verifiedBootKey` 后做字节级证据对照。
4. **P4：原厂镜像、匹配 EDL Loader、P780 专用 locked 写入成功原始记录** —— 仍是最终 Root/解锁研究的独立阻断；AVB 指纹匹配也不能替代刷写能力。

不要求继续常规 `getprop` 穷举。不自动安装手机应用、执行漏洞、越权读写、发送第三方邮件。

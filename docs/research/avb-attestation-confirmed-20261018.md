# P780 AVB 硬件证明与 AOSP 默认测试公钥匹配（2026-10-18）

> 实机重大阶段结果：P780 `_162` 的可信 TEE 报告的 AVB 根公钥摘要，与 AOSP 默认 RSA4096 测试公钥的 AVB 二进制表示 SHA-256 **完全相同**。不是 Root、解锁或锁定态刷写成功。

## 原始材料与隐私

- 机主正常运行 vvb2060/KeyAttestation 并将 P780-KeyAttestation.p7b 从手机下载后上传本轮私有会话。文件大小为 3475 bytes，PKCS#7 Signed Data，4 张 X.509 证书。
- 原始 p7b 可能关联设备：**未上传 GitHub；本专题只保留公开测试公钥摘要、系统镜像摘要和必要的脱敏验证结果**。不公开设备序列号、IMEI、完整证书、attestation challenge 或应用签名。

## ASN.1 与签名链验证（Python cryptography + 本地 ASN.1 TLV）

- Android Key Attestation 扩展 OID 1.3.6.1.4.1.11129.2.1.17；attestationVersion=3，attestationSecurityLevel=TrustedEnvironment(TEE)，keymasterVersion=4，keymasterSecurityLevel=TrustedEnvironment(TEE)。
- RootOfTrust.deviceLocked=true；verifiedBootState=0 (Verified/GREEN)。
- **verifiedBootKey**: `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6` (32 bytes)。
- **verifiedBootHash**: `33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`，与此前本机 `ro.boot.vbmeta.digest` 完全匹配。
- osVersion=110000、osPatchLevel=202402、vendorPatchLevel=20240201、bootPatchLevel=20240201。
- 根证书与 Google [官方公布的 2019-11-22 Android Hardware Attestation Root](https://developer.android.com/privacy-and-security/security-key-attestation#root_certificates) DER **逐字节相等**，根证书 SHA-256 `1ef1a04b8ba58ab94589ac498c8982a783f24ea7307e0159a0c3a73b377d87cc`，有效期至 2034-11-18。
- 离线完成 Root 自签名、Root→CA1→CA2→Leaf 全部 X.509 签名验证，均有效。Google 的 Attestation CA 根公钥与设备的 AVB Bootloader Root of Trust 公钥是两种不同用途的密钥，不得混淆。
- 查阅了当日 Google 官方 [Attestation status](https://android.googleapis.com/attestation/status)，未在公开列表检索到该根和两个中间证书的序列号；**尚未完成正式的全链在线撤销核验**，不能声明生产级 revocation 100% 通过。

## AOSP 公钥精确比对（本轮最重要发现）

- 候选：AOSP `external/avb/test/data/testkey_rsa4096_pub.pem`。三个公开库（LineageOS/android_external_avb、riscv-android-src/platform-external-avb、nccgroup/test_avb_key）给出的 PEM 内容一致。
- 按官方 [avbtool.py](https://github.com/LineageOS/android_external_avb/blob/lineage-21.0/avbtool.py) 的 RSAKey.encode() 构造 `AvbRsaPublicKey` (1032 bytes)：`uint32_be(4096) || uint32_be(n0inv) || n_big_endian(512) || rr_big_endian(512)`，其中 `n0inv=-(n^-1 mod 2^32) mod 2^32`、`rr=2^8192 mod n`。
- `SHA256(AVB公钥blob) = 7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`，**与可信 TEE 的 verifiedBootKey 精确相等**。
- 排除错误编码：SHA256(SPKI DER) 为 `9841073d16a7abbe21059e026da71976373d8f74fdb91cc46aa0a7d622b925b9`；SHA256(PKCS#1 DER) 为 `560297e002c43cff4ca8604ce494e3eb3af9490764b302d78898b96f1ab816de`；SHA256(原始 RSA modulus) 为 `36949b827927c883836897ab67eb01360795186cb81faca37ef7de583a1b65b1`。这些都不匹配。
- 结论：不再仅凭 JVN 公告推定，全新机上实测证书提供了 P780 `_162` 使用 AOSP **默认 AVB RSA4096 测试根公钥**的独立密码学实证。[JVN#47427200](https://jvn.jp/jp/JVN47427200/) 结论与之相符。

## 未解决事项

- **尚未**取得 vbmeta_b / vbmeta_system_b 的原始内容、具体链式签名描述符、分区 hashtree 描述符及 rollback index。根测试公钥与 vbmeta_system 链上的独立公钥不可混同。
- **尚未**得到 P780 在 locked 状态下可复核的有效分区写入通道，也无 boot.img 原厂 `_162` 原件。公开测试私钥的存在不等于现在能刷写、解锁或获得 Root；设备仍 locked、未 Root。
- 当前阶段研究重点转为：离线确认 AVB 公钥编码和现有 Fstab 两级链组合；在获得可信原厂镜像、真实恢复工具或成功锁定态写入证据后再进一步验证。不得冒险尝试随机 Firehose、Fastboot 或 Recovery 强刷。

## 参考

- [Android AOSP Key Attestation / RootOfTrust](https://source.android.com/docs/security/features/keystore/attestation)
- [Google Attestation Root / CRL](https://developer.android.com/privacy-and-security/security-key-attestation)
- [AOSP AVB 与 avbtool](https://android.googlesource.com/platform/external/avb/)
- [NCC Group 公共测试公钥检测样本](https://github.com/nccgroup/test_avb_key)

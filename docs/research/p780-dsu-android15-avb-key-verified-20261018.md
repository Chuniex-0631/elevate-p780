# P780 DSU 第十五轮：Android15 GSI 内嵌 AVB 公钥已取得，确认 Q Developer GSI，根因仍待 P780 Ramdisk（2026-10-18）

> **历史阶段文档（2026-10-18收束）：DSU已停止。** B组后来已安装并尝试启动、最终回到原厂；本文的“未上机／下一步”限于当时阶段，不是当前指令。最新见[收束报告](p780-dsu-closure-maintenance-route-20261018.md)与[当前状态](../STATUS.md)。

> **结论：** 用户 PC 上按官方发布 SHA-256 校验目标 ZIP 后，从 `system.img` 与 `vbmeta.img` 分别提取原始 1032B AVB RSA4096 公钥。聊天助手在容器中**独立重新计算上传两个公钥二进制 SHA-1 / SHA-256**，与报告完全一致。**Android15 `system.img` 的公钥真实匹配 AOSP Q Developer GSI 公钥**，而非 P780 Fstab 所引用的普通 Q/R/S GSI 三把公钥。`vbmeta.img` 的根公钥哈希则与 P780 硬件证明根公钥一致，但此 `vbmeta.img` 的 `Flags=2`（禁用验证），其链式 `system` 描述符中公钥是**第三把 RSA2048 测试公钥**，且非 `system.img` 的签名公钥。**本轮仍无法证明实际P780 first-stage加载了哪些 GSI钥匙，也没有复现 early AVB 拒绝或启动成功。**

## 原始输入与 SHA256/独立审计

用户上传5个文件：`p780-gsi15-avb-report.txt`、`system.img.avb-info.txt`、`system.img.avbpubkey`、`vbmeta.img.avb-info.txt`、`vbmeta.img.avbpubkey`。Python `pathlib` 从 `/mnt/data/` 实际读取这5件文件，并对原始 bytes独立SHA256/SHA1；**没有从这次会话独立读取多GB完整ZIP或原始system.img**。目标ZIP完整校验是用户Windows脚本报告的结果，并非助手对完整ZIP二次哈希。

| 文件名 | 原始大小 | SHA256（本轮独立重算） |
|---|---:|---|
| `p780-gsi15-avb-report.txt` | 3132B | `44243c4292c5f4e01721be184731960a47d97dc32002bcd6b4de774cd0fc4eeb` |
| `system.img.avb-info.txt` | 1549B | `b7e4890bc061b2228d280bdbdd5a687db51ed9edfba403e10cec62293faa26e1` |
| `system.img.avbpubkey` | 1032B | `e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925` |
| `vbmeta.img.avb-info.txt` | 610B | `ba03528797762802c3935dcc03df30e5ee3769c9a4e611b501a6d62117c72e50` |
| `vbmeta.img.avbpubkey` | 1032B | `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6` |

报告声明 Google 官方ZIP `aosp_arm64-exp-BP1A.250405.005.C1-13151952-61d23231.zip` 已在**用户PC**通过 SHA256 `61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`。报告关联的**实际 system 镜像**标记：`Android/aosp_arm64/generic_arm64:15/BP1A.250405.005.C1/13151952:user/release-keys`，系统安全补丁 `2025-04-05`。

## 第一组：system.img 内嵌签名公钥 —— 确认 Q Developer GSI

```text
Image size:                   1899589632
Original image size:          1869524992
VBMeta offset:                1899151360
VBMeta size:                  2432
AVB algorithm:                SHA256_RSA4096
AVB Footer:                   1.0
Public key (sha1):            1ffb1af796b18ebf40d18faed213f686720f73f2
AVB pubkey bytes:             1032
AVB pubkey SHA256:            e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925
AVB rollback index:           1743811200 (2025-04-05 00:00 UTC)
Rollback index location:      0
Flags:                        0
system os_version:            15
system security_patch:        2025-04-05
```

这份上传的1032B原始 AVB公钥，SHA256与已在 [第九轮](p780-dsu-trust-chain-audit-20261018.md) 从公开Android11源码镜像独立获取的 **`q-developer-gsi.avbpubkey`** 的SHA256 `e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925` **完全一致**。其sha1也与当前 `avbtool info_image` 结果一致。与公知的**普通** `q-gsi.avbpubkey` SHA256 `07b37325316fd483765d474aafcaca908b4de4773e16ed87aed415c15f71fb98` 不同。

**重要身份级别声明：** 上述操作识别的是发布镜像 VBMeta 嵌入的公钥和头部信息。用户提供的是 `info_image` 输出而不是 `verify_image` 的完整密码学签名/verity hash tree 验证结果，不能写成助手已独立验证整个system镜像的签名合法性。官方ZIP SHA256只由机主侧报告通过。

## 第二组：vbmeta.img 根公钥与系统分区链式公钥不是一回事

```text
vbmeta.img Public key sha1:  2597c218aae470a130f61162feaae70afd97f011
vbmeta.img key SHA256:     7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6
vbmeta.img Algorithm:      SHA256_RSA4096
vbmeta.img Rollback Index: 0
vbmeta.img Flags:          2 = AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED
Chain Partition:           system
Chain Rollback Location:   1
Chain public key SHA1:     cdbb77177f731920bbe0a0f94f84d9038ae0617d
```

1. 根公钥SHA256 **确实完全匹配**此前 P780 TEE Hardware Key Attestation已经证实的 **AOSP 默认 RSA4096 测试根公钥**。但这仅是`vbmeta.img`自带的公钥身份，不会使单独用另一把钥匙签名的 `system.img` 自动受信。
2. 根 `vbmeta` **Flags=2** 表示AVB的 `VERIFICATION_DISABLED` 位（**不是**HASHTREE_DISABLED，后者是位1）。详见[AOSP libavb vbmeta flags](https://android.googlesource.com/platform/external/avb/+/master/libavb/avb_vbmeta_image.h) 和 [AVB verification-disabled语义](https://android.googlesource.com/platform/external/avb/+/0922bf8970fd2a61b9053a6fca81d8165cc0af67%5E%21/)。当前P780原厂Locked、green、verity=enforcing，**不能把这个vbmeta.img当作关闭原厂验证的授权或要求刷入手机**。并未证实该文件是设备DSU first-stage实际使用的vbmeta。
3. 链式描述符的 `system` 公钥SHA1 **`cdbb77177f731920bbe0a0f94f84d9038ae0617d`**，可在[AOSP avbtool unittest](https://android.googlesource.com/platform/external/avb/+/master/test/avbtool_unittest.cc) 精确对应 **`testkey_rsa2048.pem`** 的公钥。它与system.img真实公钥SHA1 **`1ffb1af7...`** 显著不匹配。故该`vbmeta.img`不可能直接充当“对这份system.img签名进行信任链认可”的证据；此外DSU第一阶段可能仅使用有AVB footer的临时system映像，不能假定整个发行ZIP中的vbmeta被加载。

## 对 P780 LOCKED DSU 故障假设的实际影响

**H1 / 锁定态公钥信任差异加强：** P780 已取得的原厂fstab文本写 `avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey`，对应公开普通GSI钥匙；我们现在**确证目标 Android15 system.img 用 q-developer-gsi钥匙**。这与“P780 原厂第一阶段没有信任 Google Developer GSI 公钥”高度符合，但没有P780实际 Boot/Ramdisk bytes、仍需排除OEM额外公钥和厂商自定义逻辑。因此 **不能写成 P780 已经证实AVB拒绝**。

**H2 / 提前回原厂仍存在：** 上轮机主 Bugreport 证实两次 `reboot,dynsystem` + GSID installed/disabled + 仅一次重启原厂，未取得LAST KMSG、last logcat 或早期 init日志。first-stage `GetActiveDsu/MapAllImages/MarkSystemAsGsi` 等可能在走到AVB以前就返回原厂，这些仍不能排除。

**H3 / 回滚与数据完整性待验：** `system.img` 的rollback index=1743811200，日期与镜像系统安全补丁一致，当前文档只是提取值，尚未获得P780实际GSI rollback storage位置、可与之安全比较的索引。不能因为P780 SPL=2024-02-01 就机械声称此索引会通过。

## 下一步尽量不再重复耗时实验

- PC侧已确认 `system` 真正使用Q Developer GSI公钥。暂**不需要**重新下载同一个 Android15 ZIP 或再算同一公钥。需要从可信原厂 `_162` Boot/Ramdisk/first-stage载体中核验 q/r/s普通keys的**实际bytes**、是否额外有q-developer及优先加载方式；也可寻找更小/更老的发行GSI使用哪套钥匙供将来**不刷机**比对，但不因为新镜像公钥不同就直接冒险安装。
- 若确证实际可信keys只有普通q/r/s而没有Q Developer，则此 Android15镜像在**走到所述 AVB强制验签步骤时**无法通过该公钥验证（条件性确定阻断），但首次失败是否此前已经在slot/mapping处早退仍需独立日志或匹配固件的第一阶段配置。
- 在明确建立一个可解释失败的修复变量、已有备份与恢复方案且机主重新确认风险之前，不再点击DSU Restart、不运行sticky enable、不修改原厂vbmeta或刷机。无Root/BL解锁新成果。

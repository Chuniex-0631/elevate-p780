# P780 DSU 第九轮 — AVB/GSI 信任链源码审计与公开公钥二进制核对（2026-10-18）

> **历史阶段文档（2026-10-18收束）：DSU已停止。** B组后来已安装并尝试启动、最终回到原厂；本文的“未上机／下一步”限于当时阶段，不是当前指令。最新见[收束报告](p780-dsu-closure-maintenance-route-20261018.md)与[当前状态](../STATUS.md)。

> 本次仅离线研究 AOSP、公开 GSI 发布说明与可核验的公开 AVB 公钥数据。**P780 没有下载 GSI ZIP、没有安装、没有重启 GSI；仍为 Bootloader LOCKED / 未 Root。** 研究结论必须区分三件事：设备根 AVB 公钥、fstab 引用的 GSI 额外信任公钥、Google 当期 GSI 映像实际签名公钥。

## 1. 源码确认的两级筛选，不能混为一谈

1. **Settings 菜单元数据初筛：** `DSULoader.java` 读取远端 JSON 的 ABI/OS/SPL 等以及可选的 `vndk`、`pubkey` 字段。第八轮实测 Google 六子目录共24条均无 `vndk`、`pubkey`；这解释为什么 P780 会显示 Android15、Android16 各2个 ARM64 候选。**显示不等于受信验签、运行/硬件兼容**。
2. **DSU 安装时的镜像 AVB 元数据及可选撤销核查：** [AOSP DSU 文档](https://source.android.com/docs/core/ota/dynamic-system-updates) 规定 DSU 中各分区独立有 AVB 签名，镜像公钥需要与设备第一阶段 ramdisk 已信任的公钥配对，`pubkey` JSON 字段只是**可选的安装前匹配提示**。同文档还给出 `https://dl.google.com/developers/android/gsi/gsi-keyblacklist.json` 作为默认签名钥匙撤销列表地址，撤销项为 **SHA-1(AvbRsaPublicKey blob)**。它与我们比较的 SHA-256 是不同用途，不能互换。
3. **早期启动最终验证：** [AOSP `first_stage_mount.cpp`](https://android.googlesource.com/platform/system/core/+/refs/heads/main/init/first_stage_mount.cpp) 明确在早期启动把 `/avb/*.avbpubkey` 复制到 `/metadata/gsi/dsu/avb/` 供 DSU 安装服务**辅助预检**；复制失败不致命，**实际启动仍会再次核对可信钥匙**。不应以 App 的 JSON 无 `pubkey` 或用户态看不到 `/avb` 就断定启动绕过了 AVB。
4. **AVB 系统补丁回滚比较**：[AOSP DSU 文档](https://source.android.com/docs/core/ota/dynamic-system-updates#rollback-protection) 说明需要比较当前系统与候选系统的 AVB 安全补丁属性，而不只是 Settings JSON 的 `spl` 文本。第八轮只核对公开 JSON，没有取得具体 GSI 的 AVB property descriptor、rollback indices。

## 2. AOSP “普通 GSI” 与 “Developer GSI” 是两套不同公钥

- P780 原厂 fstab.default / fstab.emmc 曾被机主实际读到：`avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey`。
- [AOSP Android 11 `target/product/gsi_keys.mk`](https://android.googlesource.com/platform/build/+/refs/tags/android-11.0.0_r1/target/product/gsi_keys.mk) 包含 **q/r/s-gsi**；[AOSP `developer_gsi_keys.mk`](https://android.googlesource.com/platform/build/+/master/target/product/developer_gsi_keys.mk) 则包含 **q/r/s-developer-gsi**，是额外、不同的文件。
- [AOSP 历史 `rootdir/avb/Android.mk`](https://android.googlesource.com/platform/system/core/+/90947d442cb1ae59474f674ba663d8ba2dfdf554/rootdir/avb/Android.mk) 清晰定义了 q-gsi 与 q-developer-gsi 两个独立预编译文件，r/s 同理。**需要纠正旧阶段把 P780 的 q/r/s 路径直接称为 developer-GSI keys 的简化说法**。P780 fstab 只证实引用了普通 q/r/s-GSI 路径，不能在没有 ramdisk 原件前把 Developer key 当作它的加载公钥。

## 3. 公开六份 AVB 公钥二进制的独立 SHA-256

使用公开 [Android 11 `android_system_core` 镜像](https://github.com/twrp-raspberry/android_system_core/tree/twrp-11/rootdir/avb) 的六个二进制文件，按 GitHub connector 的 `base64` 原样取得，再由纯 JS SHA-256 实现对**解码后的原始字节**计算。SHA-256 算法已用 `abc` 标准向量自检。全部是 `1032B` 的 AVB RSA-4096 公钥二进制格式；下表为这些**公开源码镜像**的值，不是直接从 P780 ramdisk 读取的文件。

| AOSP 公钥文件名 | Git blob SHA-1 | SHA-256（1032B AVB blob） |
|---|---|---|
| `q-gsi.avbpubkey` | `5ed7543ba22c4164b0ab153828a6b3bfe0d1289f` | `07b37325316fd483765d474aafcaca908b4de4773e16ed87aed415c15f71fb98` |
| `r-gsi.avbpubkey` | `2609b3037eac08b7ea9653dabc9e8f6c090b08e0` | `4706b8d2ffd46c5759d9431b8bf95f5c0544f4f6c87bbe35ff591325eb1783f5` |
| `s-gsi.avbpubkey` | `9065fb83ff23ca5a0ab7c238aca0e88257cb8b23` | `ec60e13d92331e2c2d5d1372a5d7f2131861dc602815fd87c0637d14790b4538` |
| `q-developer-gsi.avbpubkey` | `0ace69ddd0e4ba9f2ab31e2d85cf106bd36994ba` | `e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925` |
| `r-developer-gsi.avbpubkey` | `aac39cc867c4890046c65377375ceb936ac12e78` | `771cb4a48c41942fb4c4a98ab56020256e2b8255614d434ef536cd699d5d15d5` |
| `s-developer-gsi.avbpubkey` | `f0a6c11b823a7579cf244582bcf65a08908bf867` | `162e40cf394ab8a192948cdeb295f718f61dc9e73603eccc1e165bdc1836304e` |

六个公开公钥值相互不同，均**不等于**此前真实 P780 TEE Key Attestation 所报告的 AVB 根公钥摘要 `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。**这证明“公开标准 GSI 公钥”和“公开 Developer GSI 公钥”都不是那把已确证的 AOSP 默认 Bootloader 根公钥；不能反向推断实际 P780 ramdisk 的 q/r/s 文件100%与公共源码相同。**

## 4. Google Android15/16 发行版身份与实际缺口

Google 官方发布说明提供与手机菜单相同构建的 ZIP 全文件 SHA-256，可作为**将来如果下载镜像时**对文件完整性进行对照的公开来源：
- [Android15 GSI 发布页](https://developer.android.com/topic/generic-system-image/releases)：`BP1A.250405.005.C1`；ARM64 非 GMS ZIP SHA-256 `61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`，ARM64+GMS ZIP SHA-256 `48d6db2ad0638ff7a23bb1dcb154221ee693afe0f88340b4000bda44940ff885`。
- [Android16 官方 CP11 发布页](https://developer.android.com/about/versions/16/qpr3/gsi-release-notes)：`CP11.251209.009.A1`；ARM64 非 GMS ZIP SHA-256 `59a822d9a4dd09873009f40c4b97003a2f2dab1b284f2c56b0aaa63dde7e19dd`，ARM64+GMS ZIP SHA-256 `89298580dda1280efe32b27d04b9caf5bbe19061c3716635c0d2d11640acf292`。
- 以上是**官方 release notes 发布的目标 ZIP 哈希**，不是对本机已下载 ZIP 的检验；本轮没有下载任何 GB 级镜像，也没有检视 ZIP 内 `system.img` 的 AVB Footer / 公钥。
- 官方 Android15/16 release notes 明确警告部分 GSI **重启失败可能需要进 Recovery 清除 userdata 才能修复**；GMS GSI 可能因默认动态分区大小不足而失败。虽然 DSU 设计降低覆盖原系统的风险，**并不保证零数据丢失**，所以不能把拥有闲置 P780 解释为直接安装的授权。

## 5. 判断与后续工作

**已完成：** AOSP 两种 GSI 公钥包分别存在；六个公开公钥的 1032B 与 SHA-256 独立核对；它们与 P780 的主 AVB Root 公钥是不同密钥；DSU 在 Settings 元数据预筛、安装阶段可选辅助核查、first-stage 最终可信公钥核对三个阶段的职责边界进一步明确；两个 Google 镜像发布包的官方 hash 与恢复警示已查到。

**尚未完成：** P780 当前真正使用的 ramdisk `/avb/q,r,s-gsi.avbpubkey` 字节是否与 AOSP 公共素材一致；Google Android15/16 具体 `system.img` AVB 内嵌签名公钥是否匹配上述三把中的任何一把；P780 的 vendor HAL、DSU early boot、Weaver/Gatekeeper 和数据回退安全性。缺少这些条件，**不能**宣称 locked DSU 能启动，也不能认为已获得永久 `boot`/`vbmeta` 写权限。

**不重复 ADB，不发起下载与安装。** 优先继续公开源码和是否有独立小型签名元数据可对照的研究；若要上机 DSU，必须另行征得用户明确同意、备份重要数据，准备 Recovery/Factory Reset 的失败恢复手段。当前仍未 Root、未解锁，主项目的原厂 vbmeta/boot 和 locked 写入通道仍未突破。


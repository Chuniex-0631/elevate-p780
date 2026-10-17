# P780 DSU 锁定 Bootloader 与 GSI 签名信任机制专项核验（2026-10-18）

> **第十五轮 PC 已取得实际GSI公钥，原专题中“未取得目标GSI实际公钥”的句子仅是当时阶段记录。** Android15 `BP1A.250405.005.C1` 的 `system.img` AVB 1032B公钥SHA256 **`e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925`**，与 AOSP **Q Developer GSI** 完全一致（已从用户上传原始bytes独立计算）；其同ZIP `vbmeta.img` 嵌入的AOSP测试根虽然与P780 hardware attestation root匹配，但 `Flags=2`、链式system公钥为另一 RSA2048测试key，不能据此宣称DSU可以加载。**仍缺P780 `_162` 真实ramdisk允许公钥集合，AVB拒绝/早期映射均未直接证实。** 请见[第十五轮实证](p780-dsu-android15-avb-key-verified-20261018.md)。

> **结论：Bootloader LOCKED 并不自动禁止 DSU，AOSP 官方支持在 LOCKED + AVB 验签开启时启动经设备信任的 GSI。** 但在 P780 上，历史证据只见普通 q/r/s GSI AVB 公钥路径，尚未证明设备的第一阶段 Ramdisk 配备能验证当期 Google **Developer GSI** 的公钥。**锁定状态下密钥不受信是高价值待证假设，不是第十轮“重启一次回原厂”的确证根因。** 该单次正常回退同样符合 first-stage 的活动 slot / ImageManager map 等先于 AVB 的失败。

## 用户提出的问题与具体边界

机主问“是否仍有系统限制导致未解锁 BL 的情况下不能加载 DSU”。已有 P780 Android 11 固件 `_162` 的真机：

- BL LOCKED / Verified Boot green / Root 未取得；P780 Fstab `system` 段的 `avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey` 被机主实际读取。此为**文件名引用**，尚未提取本机真实 ramdisk bytes，不排除 OEM 其他额外公钥配置。
- 官方 DSU Loader 显示并下载安装 Google Android15 `BP1A.250405.005.C1` ARM64 GSI（具体安装的 build ID 按过往菜单选择推定；单次新通知未独立抓取），`gsid.image_installed=1`、`gsi_tool status=installed/disabled`。两次通知 Restart 的 bootreason history 确证 `reboot,dynsystem`，均只经历一次重启而回到原厂 B 槽，`ro.gsid.image_running=0`。
- Bugreport 无 LAST KMSG、pstore console-ramoops、LAST LOGCAT；当前 dmesg 只保留开机943秒后的事件，没有前期任何 AVB/mapping 错误可判。**现有实机没有锁定策略拒绝公钥的原始日志，不能宣称“确认是 BL 没解锁”。**

## AOSP 官方对 LOCKED GSI 的明确规则

1. [AOSP DSU Official Guide](https://source.android.com/docs/core/ota/dynamic-system-updates) 的 Verify Boot 章节明确写：若厂商希望在 **LOCKED**、不关闭 Verified Boot 的状态下运行公开 **Developer GSI**，应在 device.mk 中包含 `$(call inherit-product, $(SRC_TARGET_DIR)/product/developer_gsi_keys.mk)`。第一阶段 ramdisk 要携带相应 GSI AVB 公钥以验证镜像。**说明 Locked+DSU 是设计支持的场景，失败应关注信任链配置，而非把解锁BL当作 DSU 一般先决条件。**
2. [Android 10 AOSP developer_gsi_keys.mk](https://android.googlesource.com/platform/build/+/android-10.0.0_r40/target/product/developer_gsi_keys.mk) 注释直接说明厂商选择性添加 Developer GSI 允许锁定态验证，预装的是 `q-developer-gsi.avbpubkey/r-developer-gsi.avbpubkey/s-developer-gsi.avbpubkey`。这与 P780 fstab 引用的 `q-gsi/r-gsi/s-gsi` **不是同名文件，公开原件二进制 SHA也不同**，详见 [第九轮信任链报告](p780-dsu-trust-chain-audit-20261018.md)。
3. [Android 11 build `gsi_keys.mk`](https://android.googlesource.com/platform/build/+/refs/tags/android-11.0.0_r1/target/product/gsi_keys.mk) 过去为普通 Compliance GSI 安装 q/r/s 公钥，Google [2021-12-22 AOSP 提交 5d2cf578](https://android.googlesource.com/platform/build/+/5d2cf578d6b64e03d0babac436dfbbb4f9886971) 明确将其移除，提交说明是：**Compliance GSI 的公钥不再需要进入设备 Ramdisk，只需在 VTS Test Suite 中做验证**。这一源码演进强化：**普通 Compliance GSI keys 与开发者发布 GSI 受信配置不能混为一谈**。
4. [AOSP `fs_mgr/libfs_avb/fs_avb.cpp`](https://android.googlesource.com/platform/system/core/+/main/fs_mgr/libfs_avb/fs_avb.cpp) 的 `IsAvbPermissive` 在设备 LOCKED 时返回 false；`LoadAndVerifyVbmeta(fstab, preload)` 校验公钥与 ramdisk/fstab 的允许公钥集，若未知会记录 `Found unknown public key` 和 `Unknown public key is not allowed` 并拒绝继续。**Locked 时不能忽略公钥不匹配**；Unlocked 设备可以在特定允许条件下宽松处理。因此 “未解锁的限制”可以具体化为**硬性 AVB 信任关系**。

## 为什么安装器能完成，但 Locked 设备仍可能不启动

- 原 Google DSU 七八轮目录共24条镜像，全部**缺可选 `pubkey` 和 `vndk` JSON 字段**；官方 DSU 文档明确指出可选 pubkey 用于**安装前预匹配**，字段缺失不会自动验证镜像签名与当前设备信任公钥是否相同。因此“下载成功/安装状态已保存/通知出现”不等于 AVB mount 已验签接受。
- [AOSP Android11 DynamicSystemInstallationService](https://android.googlesource.com/platform/frameworks/base/+/978ecf991a9a/packages/DynamicSystemInstallationService/src/com/android/dynsystem/DynamicSystemInstallationService.java) 在 `setEnable(true, oneShot)` 成功后才 `PowerManager.reboot("dynsystem")`，设备两次 bootreason 实际为 `reboot,dynsystem`；故“通知没有真正发起 DSU reboot”这个解释不再主要。
- [AOSP `first_stage_mount.cpp::UseDsuIfPresent`](https://android.googlesource.com/platform/system/core/+/9583e92257ab85075231b014f0999d5a5dab9910/init/first_stage_mount.cpp) 在 `GetActiveDsu`、`MapAllImages`、`MarkSystemAsGsi` 等早期条件不满足时会 **return to normal boot**，而在 mount/AVB 阶段才做实际信任校验。P780 仅一次重启即回原厂是 early bailout 的合理解释，**与真实 AVB 不匹配的错误位置尚未建立直接联系**。

## VNDK30 与硬件兼容（需保留其他解释）

- [AOSP 当前 GSI release makefile](https://android.googlesource.com/platform/build/+/HEAD/target/product/gsi_release.mk) 显式 `PRODUCT_EXTRA_VNDK_VERSIONS := 30 31 32 33 34`，证明 Google GSI 构建路线**有支持 VNDK30 的配置能力**，不能仅因 Android15+ / Android11 Vendor就断言不可用。具体 `BP1A` 发行 ZIP 是否完全包含、设备 HAL/Gatekeeper/Weaver 能否运行**仍需实际镜像校验**。
- Android 11 的 first-stage DSU 状态和镜像映射存在与 BL lock 无直接同义关系的失败途径，例如活跃DSU slot、image backing、metadata、dm-linear映射/SELinux/vendor ramdisk 配置。**不能因为检测到绿色 Verified Boot 就排除这些故障。**

## 新发现：AOSP root-only `gsi_tool status` 可在本机已装 GSI 上列出真实签名钥匙 SHA-1

- [Android 11 `gsi_tool.cpp`](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-cts-11.0_r16/gsi_tool.cpp) 第 388～460 行：调用 `isGsiRunning/isGsiInstalled/isGsiEnabled` 后，若 `getuid()!=0` **直接 return**。**只有 UID 0** 时，它才循环 `getInstalledDsuSlots`、`openImageService`、`getAllBackingImages`、`getAvbPublicKey` 并输出 `AVB public key (sha1): ...`。
- P780 普通 ADB shell 非 root，已实测只输出两行 `installed/disabled`，与源码一致。**无法通过再次普通 shell `gsi_tool status` 读到哈希**。也不应该绕过 `ENFORCE_SYSTEM`/IImageService UID 访问限制。若将来通过合法 OEM debug / 设备已获 root 才可使用此路径；目前不要求该操作。
- 真实 Android15 GSI 的 AVB Signing Key SHA-1 未在 Google JSON 中列出，且未下载 GB级发行镜像，也没有获取 P780 的实际 boot/ramdisk 公钥；因此 **证据尚不足以执行两个公钥 SHA-1/SHA-256 的直接比较**。

## 研究优先级与解除分歧的方法

| 假设 | 新证据 | 剩余证据缺口/下一步 |
|---|---|---|
| **H1：Locked + Developer GSI 未被 P780 信任** | 官方 LOCKED 支持需要 Developer GSI 公钥；P780 fstab 仅引用普通 q/r/s key，普通/Developer公钥真实不同，Android15 JSON无pubkey。**强配置层面疑点；未证明触发失败** | 获取匹配 `_162` 实际 first-stage ramdisk 的允许公钥；取得 Android15真实 `system.img` AVB signing public key；同格式哈希或原始 bytes 比对。若未知公钥确实不匹配，才能认定 locked AVB 层阻止镜像。 |
| **H2：P780 first-stage DSU 映像/metadata/slot 条件早退** | 两次 `reboot,dynsystem`、每次只启动一轮进入原厂；AOSP `GetActiveDsu/MapAllImages` 等直接 return，GSID事后 disabled 符合 one-shot 消耗。**行为吻合，未证明函数点** | 匹配 `_162` first-stage 实现与 ramdisk/metadata 初始化；或未来真正可保存 first-stage 日志的受控实验。 |
| H3：后续 VNDK/HAL/Gatekeeper/AVB rollback/系统兼容 | Treble ABI/VNDK 基础满足；AOSP 当前 GSI构建可打包VNDK30；具体包仍未知 | 具体 GSI ZIP/AVB descriptor 和旧 Vendor HAL/系统补丁对照，不能用单纯换Android16验证。 |

**操作边界：** 当前不要再次点通知 Restart、启用 sticky 的 `gsi_tool enable`、取消AVB检查、刷写boot/vbmeta、尝试不可信 EDLLoader，也不因为看不到ramdisk就建议BL解锁（P780 OEM unlocking目前锁定且无可靠解锁方法）。优先PC离线获取可信公开素材及其SHA；任何新实机操作需与机主明确约定新观测目标、备份及恢复风险。

## 最终回答用户的问题

**有可能是 Bootloader Locked 附带的 AVB 公钥信任限制导致，但不是“只要 BL Locked 就禁止 DSU”。** P780 缺少已证实的 Developer GSI 信任公钥是特别具体、比之前更值得检查的疑点；不过单次直接返回原厂的症状也很符合 DSU 在映射或活动槽阶段早退。应同时验证两者，只有实际公钥/first-stage 证据匹配，才能宣称根因查明。
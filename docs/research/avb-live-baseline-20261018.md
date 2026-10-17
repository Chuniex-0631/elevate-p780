# P780 AVB 实机只读基线（2026-10-18）

**证据等级：用户在聊天中提供的实体机 ADB 原始输出；尚未将日志文件作为原件存入 Git。** 不应把它标记为独立重测或完整分区取证。机型和此前的构建身份按 [设备档案](device-and-boot.md) 为 P780 / Android 11 / `P780AE_11.0_RMN_JP_162`，但这次输出本身没有重新核对固件号。

## 2026-10-18 用户执行的只读命令与观察

| ADB property | 本轮原样值 | 证据边界 |
|---|---|---|
| `ro.boot.verifiedbootstate` | `green` | 启动加载器报告当前验证状态；**不能证明使用了安全且唯一的生产密钥** |
| `ro.boot.vbmeta.device_state` | `locked` | 表示当前 VBMeta 设备状态是锁定 |
| `ro.boot.flash.locked` | `1` | 与锁定状态一致 |
| `ro.boot.slot_suffix` | `_b` | 本次启动位于 B 槽；不能推定之后永远在 B 槽 |
| `ro.boot.vbmeta.digest` | `33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2` | SHA-256 形态的本次 VBMeta digest；不是 AVB 公钥指纹，也不是 boot.img 哈希 |

**解读**：`green + locked` 与 [JVN#47427200](https://jvn.jp/en/jp/JVN47427200/) 证实的 AVB 测试密钥缺陷不矛盾。锁定状态下能够通过验证，仅证明设备信任了本次加载的映像及元数据，并不能证明信任锚的密钥没有泄露或被公开。论文在其他机型上演示修改镜像仍显示 green；没有 P780 本机 PoC。

## 本轮外部核查的新可执行技术方法

1. AOSP 官方 [AVB README（Android 11）](https://android.googlesource.com/platform/external/avb/+/refs/heads/android11-release/README.md) 对 `calculate_vbmeta_digest` 的定义：摘要覆盖主 VBMeta 及**所有链式 VBMeta 结构**（若存在），不能简单把原始 `vbmeta.img` 整个文件做 SHA-256 来比较。
2. 未来取得**同版本、同活动槽位**可信镜像后，先运行 `avbtool info_image --image vbmeta.img` 检查签名算法、公钥和链式分区描述，再结合完整链式镜像执行 `avbtool calculate_vbmeta_digest --hash_algorithm sha256 --image vbmeta.img`，与本页基线核对。文件命名/链式加载应以实际描述符为准，不要凭空假设只需一个文件。
3. NCC Group 的 [test_avb_key](https://github.com/nccgroup/test_avb_key) 可在取得 `vbmeta.img` 后比对已知测试私钥对应的公钥；它**不能只靠 Android getprop digest 判断密钥是哪一把**，其命中也仍需与 AOSP avbtool 独立核验。
4. AOSP [AVB README](https://android.googlesource.com/platform/external/avb/+/refs/heads/android11-release/README.md) 说明 `extract_public_key`、`info_image`、`verify_image` 等供离线验证。AVB 公钥与 Recovery OTA ZIP 签名证书、Qualcomm EDL Firehose 签名属于不同信任域。

## 下一次只读数据采集

现已新增适用于 Windows PowerShell 的 [tools/p780-avb-readonly.ps1](../../tools/p780-avb-readonly.ps1)，只调用已授权的 ADB `getprop` 和 `ls -l /dev/block/by-name`，不读取分区数据，不调用 `su`，也不使用 `dd`、`fastboot flash`、`adb reboot` 或 EDL。

在仓库根目录、已连接一台授权设备时运行：

```powershell
powershell.exe -NoProfile -File .\tools\p780-avb-readonly.ps1
```

脚本会生成 `p780-avb-readonly-YYYYMMDD-HHMMSS.txt` 到运行时目录。它只列举白名单属性与包含 `vbmeta/boot/dtbo/super/metadata` 关键词的设备块链接；部分属性不存在或系统拒绝列目录是允许的负面结果。输出需先核对再分享，不收集序列号、IMEI、MEID、设备账户或完整 `getprop`。

如未克隆仓库，也可手工执行少量只读命令：

```powershell
adb shell getprop ro.boot.vbmeta.hash_alg
adb shell getprop ro.boot.vbmeta.size
adb shell getprop ro.boot.avb_version
adb shell ls -l /dev/block/by-name
```

**不可越界的结论**：尚未获得 `_162` 完整 OTA、`vbmeta_b.img`、`boot_b.img` 等原始镜像；不能以 digest 推断已找到可签名钥匙，也没有已验证的锁定态分区写入通道。P780 仍未 Root/解锁，不进行写入或损坏风险高的实验。

## 源与下一关键问题

- [JVN#47427200 / CVE-2026-107153](https://jvn.jp/en/jp/JVN47427200/)：Rakuten Hand 5G 全版本使用 AOSP AVB 测试密钥，属于已确认受影响范围。
- [AVBTestKeyInTheWild 论文](https://www.android-device-security.org/publications/2025-leierzopf-spices/Leierzopf_2025_SPICES_AVBTestKeyInTheWild.pdf)：跨机型的通用原理及受限定的部署路径，未提供 P780 适配。
- [NCC Group 公开工具说明](https://www.nccgroup.com/research/on-almost-signing-android-builds/)：当实际 VBMeta 镜像到手时如何定位已知测试公钥。
- [AVB 核心文档](https://android.googlesource.com/platform/external/avb/+/refs/heads/android11-release/README.md)：`info_image` / `verify_image` / `calculate_vbmeta_digest` 的真实语义。

下一阶段以取得**可信版本一致的 `_162` AVB 镜像**为第一阻断，以**P780-specific locked 写入机制的成功原始日志**为第二阻断。不能用测试密钥替代 Qualcomm Firehose 授权，也不能把其他机型的攻击链视为 P780 已成功的证据。

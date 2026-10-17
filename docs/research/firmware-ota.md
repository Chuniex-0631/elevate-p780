# P780 固件 / OTA / 官方安全公告资料

## 真实设备固件（用户采集）

```text
Manufacturer/TINNO
Model/P780
Android/11
Build fingerprint/Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys
ro.custom.build.version/P780AE_11.0_RMN_JP_162
ro.internal.build.version/P780AE_11.0_RMN_JP_162_CFC
Android security patch/2024-02-01
Linux/5.4.233-qgki-gea5245e94afe-dirty
```

## 楽天モバイル官方更新历史

[官方 Rakuten Hand 5G 软件更新公告](https://network.mobile.rakuten.co.jp/information/software/rakuten-hand-5g/)：明确列出最新官方 `P780AE_11.0_RMN_JP_162` 的更新开始日期 **2024-03-21**，系统仍为 Android 11。已发布历史中还包括 `_161`（2024-01-23）、`_159`（2023-11-16）、`_157`（2023-08-24）、`_153`（2023-06-14）、`_152`（2023-04-13）、`_151`（2023-02-20）、`_149`（2022-12-21）、`_143`（2022-11-18）、`_140`（2022-08-31）、`_139`（2022-07-11）、`_134`（2022-06-20）。

- **2024-02-20** 是设备镜像与内核编译时间，**2024-03-21** 是官方更新开始发布日；它们不是互相矛盾的日期。
- **2026-10-10** 未能从已经掌握的用户文件中提取有版本校验的完整 OTA ZIP、`payload.bin`、`boot.img` 或 `vendor_boot.img`。
- 历史原件已由机主上传并保留至私有 Git 仓库：[Activity 记录](../../evidence/restricted/ota/hand5g_update_activity.txt)（94,710 B）、[Logcat](../../evidence/restricted/ota/hand5g_update_log.txt)（283,944 B）及 [Bugreport](../../evidence/restricted/bugreport/hand5g_bugreport.zip)（5,684,665 B）。**这些是未脱敏原件**，不应公开，亦未从中取得可直接使用的完整 OTA。
- 更新服务材料的独立审阅见 [OTA 与 Bugreport 归档](ota-bugreport.md)。

## 官方安全公告与 2026-10-14 JVN 技术归因

[Rakuten Hand 5G 设备官方支持页面](https://network.mobile.rakuten.co.jp/product/smartphone/rakuten-hand-5g/support/index.html) 确认：

- 设备维修/支持于 **2025-12-31** 结束。
- **2026-09-28** 时已经确认固件真实性验证机制存在缺陷，修改的固件可能被误认为正版。
- 官方指出具有临时物理访问能力的攻击者可能因此安装修改固件，并导致权限获取/软件执行或设置修改，建议停止继续使用此已退役设备。

2026-10-14 发布的 [JVN#47427200](https://jvn.jp/jp/JVN47427200/) / [JVNDB-2026-000147](https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000147.html) 新增了可核验的技术归因：Rakuten Hand 5G **全部版本**的 AVB 使用已知 AOSP 测试钥匙，编号为 **CVE-2026-107153**。因此本机 `_162` 属公开受影响范围。

**研究判断**：JVN 证实的是 AVB 信任钥匙缺陷；它仍未给出 P780 在 locked 状态下的实际分区写入途径，也没有提供 `_162` 原厂镜像。不得把 JVN、论文中的其它机型演示或公开 AOSP 钥匙等同于 `fastboot flashing unlock`、匹配 EDL loader 或本机 Root 成果。详细条件见 [独立安全公告研究](firmware-advisory-20260928.md)。

## 2026-10-18 动态分区 / 快照与镜像检索现状

- 实机 `ro.boot.dynamic_partitions=true`；先前发现 `system_b-cow` / B 槽 dm-verity 节点；`ro.virtual_ab.enabled` 与 `ro.virtual_ab.compression.enabled` 属性为空，不足以定性是否开启 Virtual A/B 或 OTA merge。
- Android 11 Virtual A/B 使用 kernel COW，压缩快照是后续 Android 12 的功能（[AOSP Virtual A/B](https://source.android.com/docs/core/ota/virtual_ab)）。**COW 设备映射不是可自由写入受 AVB 保护固件的证据。**
- 再次搜索 `P780AE_11.0_RMN_JP_162`、`payload.bin`、`vbmeta.img` 及 P780 stock OTA 组合，**没有取得可独立验证出处和 SHA 的完整镜像**。官方发布页只提供软件版本与更新说明，并非原始固件下载源。
- [XDA 2026-03-15 固件求助帖子](https://xdaforums.com/t/request-rakuten-hand-5g-p780-stock-ota-or-full-firmware.4782235/) 出现在搜索结果，但网页正文因 403 未能核实，只可作为公开用户找固件的线索，不视为固件工件或者可信解锁证据。

## 2026-10-18：Google OTA 发现线索

- 本机完整 fingerprint 已实测：`Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`，其中 `264` 为 Android build incremental，并非厂商 `_162` 版本号。
- [Google OTA Prober 项目审阅](google-ota-prober-p780-20261018.md)：通过 Google Check-in (`fetchSystemUpdates=1`) 请求 Google OTA URL，**是否适用于 P780 尚未验证**。
- 公共 Google OTA 档案对 **Tinno 制造的 Rakuten Mini C330** 有真实增量 OTA URL 与构建区间；P710 只有 fingerprint，无 P780 索引。仅构成同厂商历史旁证，不能把其他机型更新包作为 P780 固件。
- 原始 OTA 仍未取得；如果以后获得 P780 URL，必须先核对 OTA metadata、版本和包类型，在本地分析且不在设备上安装。

## 未解决的 OTA 事项

- 收集官方完整 OTA 的可信来源和具体哈希。
- 核对更新机制日志中的下载 URL 是否可用以及是否带鉴权/过期参数（仓库内不发布带 token URL）。
- 如果未来获取 `_162` 官方固件，优先离线提取 `vbmeta*.img` 的公钥指纹、链式分区描述和回滚索引，并与已知 AOSP 测试钥匙核对；完整备份后再设计任何设备实验。


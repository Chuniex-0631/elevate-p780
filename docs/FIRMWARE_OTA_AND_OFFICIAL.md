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
- 历史原件已由机主上传并保留至私有 Git 仓库：[Activity 记录](../evidence/restricted/ota/hand5g_update_activity.txt)（94,710 B）、[Logcat](../evidence/restricted/ota/hand5g_update_log.txt)（283,944 B）及 [Bugreport](../evidence/restricted/bugreport/hand5g_bugreport.zip)（5,684,665 B）。**这些是未脱敏原件**，不应公开，亦未从中取得可直接使用的完整 OTA。
- 更新服务材料的独立审阅见 [OTA 与 Bugreport 归档](OTA_LOGS_AND_BUGREPORT.md)。

## 官方 2026 年 9 月 28 日安全公告

[Rakuten Hand 5G 设备官方支持页面](https://network.mobile.rakuten.co.jp/product/smartphone/rakuten-hand-5g/support/index.html) 确认：

- 设备维修/支持于 **2025-12-31** 结束。
- **2026-09-28** 时已经确认固件真实性验证机制存在缺陷，修改的固件可能被误认为正版。
- 官方指出具有临时物理访问能力的攻击者可能因此安装修改固件，并导致权限获取/软件执行或设置修改，建议停止继续使用此已退役设备。

**研究判断**：此官方公告不是 `fastboot flashing unlock` 已可用的证据；没有给出此 P780 `_162` 版的签名验证失效阶段、实际安装途径或修复详情。不得自行把它等同于 GhostLock 或可以在锁 BL 状态直接刷写任意 `boot.img`。详细历史记录见 [独立安全公告研究](2026-09-28-rakuten-hand5g-firmware-advisory.md)。

## 未解决的 OTA 事项

- 收集官方完整 OTA 的可信来源和具体哈希。
- 核对更新机制日志中的下载 URL 是否可用以及是否带鉴权/过期参数（仓库内不发布带 token URL）。
- 如果未来获取 `_162` 官方固件，优先完全离线校验数字签名与哈希，完整备份后再设计任何设备实验。

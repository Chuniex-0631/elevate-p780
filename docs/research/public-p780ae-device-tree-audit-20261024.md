# 公开 P780AE 设备树候选审计（2026-10-24）

## 结论

2026-10-24 检索发现公开仓库 [2by2-Project-Devices/android_device_rakuten_p780ae](https://github.com/2by2-Project-Devices/android_device_rakuten_p780ae)。仓库创建于 2026-10-14，默认分支 `lineage-23.2`；截至核验时只有该分支、无 Release、无公开 issue，最新提交为 2026-10-19 的 [`experiment`](https://github.com/2by2-Project-Devices/android_device_rakuten_p780ae/commit/7c749c4f678d97c5f410b420a7decd7d88d3ff01)。

该项目是值得继续观察的**同型号公开线索**，但当前不能作为 P780 可构建设备树、原厂源码、Root、Bootloader 解锁、锁定态刷写或恢复成功的证据。不要据此构建或刷写本机。

## 可核验新增点

提交中出现了一组与本研究基线相符或相近的 P780 专用配置：

- `TARGET_OTA_ASSERT_DEVICE := P780|p780ae`，设备路径改为 `device/rakuten/p780ae`；
- 声明 A/B 分区、`tinno_dynamic_partitions`、boot/dtbo/super/vendor_boot 等分区尺寸；
- 顶层 VBMeta 配置为 AOSP `testkey_rsa4096.pem` / `SHA256_RSA4096`；
- 链式 `vbmeta_system` 配置为 AOSP `testkey_rsa2048.pem` / `SHA256_RSA2048`；
- 注释声称参数来自“supplied slot B / build 264 / 2024-02-01 UTC”，并明确回滚值不是设备中存储值的测量结果。

其中“顶层 AOSP RSA4096 测试钥匙”与本机 2026-10-18 TEE 证明一致；`264` 和 2024-02-01 也与本机指纹增量及安全补丁日期一致。但仓库未附所称 slot B 镜像、AVB 输出、哈希、采集日志或来源链，因此这些配置只能登记为**待验证线索**，不能取代本机原始镜像证据。RSA2048 的链式 `vbmeta_system` 配置也尚未由本机证据确认。

## 反证与不可用性

项目主体仍明显来自 Xiaomi `veux`（POCO X4 Pro / Redmi Note 11 Pro）设备树：

- README 仍列 Snapdragon 695、6/8 GB、5000 mAh、108 MP 相机等 Xiaomi 规格；
- `lineage_p780ae.mk` 仍写 `Redmi` / `Xiaomi` / `2201116SG`、MIUI Android 13 指纹及 Snapdragon 695；
- `proprietary-files.txt` 明示 blob 来自 `V816.0.12.0.TKCMIXM (VEUXGlobal)`；
- 多处仍保留 `VEUX`、`2201116`、`RemovePackagesVeux` 和 Xiaomi overlay；
- proprietary vendor 继承被注释，`TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)-kernel/kernel` 所指 P780 配套仓库/文件不存在；
- 该组织中没有可检索到的 P780 配套 kernel/vendor 仓库，项目也没有构建产物、CI 成功记录、真机启动日志、刷写步骤或恢复案例。

最新提交只改动 32 个文件、合计 161 行新增和 191 行删除，主要是从 `veux/xiaomi` 到 `p780ae/rakuten` 的机械替换和少量参数试填，提交说明本身仅为 `experiment`。

## 证据级别

|项目|级别|说明|
|---|---|---|
|仓库创建时间、分支、提交与文件内容|公开一手资料，可复核|GitHub 仓库/API 与固定 commit|
|P780 分区及 AVB 参数|候选配置／待验证|无对应镜像、哈希或采集日志|
|“supplied slot B”来源|未说明来源的作者注释|不能推出作者持有可信完整固件|
|Root、BL 解锁、锁定态刷写、恢复成功|无证据|没有产物或真机记录|
|厂商 P780 内核源码|无新增|该树不包含 P780 内核源码|

## 与现有缺口的关系及安全下一步

当前结论不变：设备仍 Locked、无 Root、无已验证写入通道；`_162/_162_CFC` 原厂 boot/vbmeta/完整 OTA 与匹配本机 PKHash 的 Firehose 仍缺。

只在项目后续出现以下材料时重新评级：

1. 有来源链和 SHA-256 的 P780 原厂/提取分区镜像或完整 OTA；
2. P780 专用 kernel/vendor 仓库或可重复构建清单；
3. 固定 commit 对应的构建日志、产物哈希及 P780 真机启动/恢复日志；
4. 从原始 `vbmeta*.img` 导出的 `avbtool info_image`、公钥摘要和链式描述符；
5. 与本机 HWID/PKHash 匹配且有完整 Sahara→Firehose 握手记录的 programmer。

在这些条件满足前，仅做公开材料和离线文本核验；不连接手机、不刷写、不执行该项目生成物。

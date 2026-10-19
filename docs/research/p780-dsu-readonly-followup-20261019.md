# DSU-READ-01：恢复出厂后的状态与现有GSI兼容性补证（2026-10-19）

本轮按机主新要求重新开放 **DSU只读取证**，不恢复安装/Restart/改签名试验。新增证据是：当前安装状态已不同于失败现场；实际vendor声明FCM5；PC已有A镜像包含FCM5矩阵，选中的5.4内核配置子集未发现冲突。**仍未确定历史回退根因，也没有启动GSI。**

## 1. 当前状态已不是 installed/disabled 的历史现场

|来源|本轮输出|解释边界|
|---|---|---|
|gsi_tool status|normal|与10月18日installed/disabled不同；只查询状态，未调用enable/disable/remove|
|当前启动限定日志|21:40:55 gsid读取 `/metadata/gsi/dsu/install_status` 报No such file；21:41:17 DynamicSystemService记录isInstalled(): false|日志是本次启动缓冲区事件，不是对10月18日失败启动的捕获|
|gsid.image_installed / ro.gsid.image_running|普通shell均返回空|不把空输出解释成全系统不存在属性或值为0；结合status和日志判断|
|init.svc.gsid|前期查询running，正式快照stopped|查询可能按需启动lazy服务；不能把stopped认定为DSU损坏|
|dumpsys gsiservice / dynamic_system|前者Can't find service，后者无输出|不能取得有效dump；不代表设备未实现DSU。此前service list已经列出两个Binder接口|
|启动原因与历史|当前reboot,userrequested；历史只有两条同原因记录|当前没有保留10月18日dynsystem原因记录；不能由此还原旧失败次数或阶段|
|系统状态|原厂fingerprint / `_b` / locked=1 / green|仍在原厂系统；不是GSI已启动|

这些观察与恢复出厂后安装状态已清除相符；不能据此确定由何步骤、何时清除全部DSU文件。只读查询触发lazy gsid的按需生命周期，不属于重新安装或启用DSU。

原厂安装器APK的现机SHA256为 `3015622f3fadb9575cd8521cf303fd3f304a6f1149d42269333e8b9bf3614260`，匹配旧样本；包版本11/API30、UID1000。shell拥有INSTALL_DYNAMIC_SYSTEM，dynsystem共享UID上下文有MANAGE_DYNAMIC_SYSTEM；这些权限与“能启动受信GSI”不是同一结论。

## 2. 明确的读取边界

本轮首次明确记录 `/metadata/gsi`、`/metadata/gsi/dsu`、`/metadata/gsi/dsu/avb`、`/data/gsi` 的目录元数据读取均Permission denied；不继续尝试子文件或别名。故没有取得first-stage复制出的AVB公钥、活动slot元数据或残留镜像。

未重试此前已经失败的pstore/last_kmsg/last-logcat、gsid原件或块设备读取；没有新早期启动记录。因此AVB信任、映射、挂载、HAL与更早失败仍不可区分。`ro.boot.force_normal_boot=1`是当前启动属性，不能单独作为历史回退根因。

## 3. ADB新取得的vendor/VINTF证据

- 从手机成功导出 `/vendor/etc/vintf/manifest.xml`（24723B）和compatibility_matrix.xml（2528B）。manifest声明 `target-level=5`、kernel target-level=5、sepolicy30.0；不是完整合并后的VINTF视图，未覆盖所有manifest fragment/ODM/APEX。
- `ro.vndk.version=30`、first_api_level=30、Treble=true、dynamic_partitions=true、A/B=true；vendor/system补丁字符串均2024-02-01；ABI包含arm64-v8a。
- `ro.vendor.api_level`为空，不用first_api_level代填它。

## 4. 与已有A镜像的离线交叉

对PC `09/p780-gsi15-avb/system.img` 流式重算整文件SHA256：`27321f9655530f014c884a690f49a53e6f3beeda71f4f27cbc141b17a8e86954`，1899589632B。与收束报告的A一致，**本轮独立补上A整镜像哈希复核**；B整镜像及A/B数据段一致性仍沿用既有PC输出，本轮未独立重算。

用只读、受限的ext4 extent读取器从该镜像提取7份顶层VINTF XML，没有挂载、执行或修改镜像。build.prop选行确认为Android15 `BP1A.250405.005.C1/13151952`、system fingerprint `Android/aosp_arm64/generic_arm64:15/BP1A.250405.005.C1/13151952:user/release-keys`、补丁字符串2025-04-05。

- GSI确实含 `compatibility_matrix.5.xml`（124740B，SHA256 `f2b353792c635abdf807aa795396440ebdfc7303b4f9f578c2a2fa9d1c7d5b69`），以及6/7/8/202404矩阵；不能仅因GSI是Android15就认定它没有FCM5支持。
- FCM5矩阵列出5.4.61内核分支。当前5.4.233仅在版本元组意义上不低于它，不证明具体补丁或厂商修改兼容。
- 按现机config选择5.4分支的条件组，共比较261条config要求，**该子集0差异**。字符串去除Kconfig引号；未出现的tristate项对预期n匹配，依照[AOSP匹配规则](https://source.android.google.cn/docs/core/architecture/vintf/match-rules?hl=en)和[KernelInfo实现](https://android.googlesource.com/platform/system/libvintf/+/master/KernelInfo.cpp)。未支持的值类型直接失败，不默认为通过。

这降低“简单的FCM级别/该内核config子集不匹配”作为候选解释的优先级。**不是完整libvintf/checkvintf通过结果**：没有合并framework/device/APEX fragments、逐HAL版本/实例匹配、VNDK库与sepolicy兼容性验证。原厂vendor仍可能与候选GSI在其它阶段不兼容。

没有检查first-stage真正加载的公钥，没有验证AVB rollback indices通过；build.prop补丁较新不替代实际AVB回滚检查。上述结果不能反推A或B失败一定发生在AVB阶段。

## 5. 已保存证据与下一步

仓库保存[状态快照](../../evidence/dsu/20261019-readonly/state-snapshot.json)、[限定DSU日志](../../evidence/dsu/20261019-readonly/dsu-log.txt)、[采集补充清单](../../evidence/dsu/20261019-readonly/acquisition.json)、vendor两份XML、GSI FCM5/manifest XML及[261项比较](../../evidence/dsu/20261019-readonly/vintf-subset.json)。完整GSI、APK与其余提取XML留机主PC；输入与提取文件哈希可复核，不冒称固件全部入Git。

工具见[DSU离线说明](../../tools/dsu/README.md)。有限ext4读取器未校验全文件系统metadata checksums，也未由另一提取器独立比对；只支持本次普通文件/目录extent路径，不用于通用镜像修复。

有价值的后续是对这些已取原件进行完整合并VINTF离线检查，或取得可信同构建boot/first-stage ramdisk以验证真实公钥和失败位置。当前受限ADB无法恢复已经缺失的旧安装/早期启动现场；没有新修复变量或日志捕获能力前，不重放安装/Restart。

本轮未安装镜像、启用/停用/删除DSU、改签名、设置属性、推送工具、重启或刷写，DSU实机试验继续停止。

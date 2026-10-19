# P780-OEMLOCK-01: OEM Unlock 灰色开关的限制来源
2026-10-19。状态：**第一阶段已实机执行，第二阶段待进行**。不推断 Bootloader 解锁或 Root 已实现。

## 已知实机材料
P780 Android 11 开发者选项的 OEM unlocking 灰色；早期资料记录 `ro.oem_unlock_supported=1`、`sys.oem_unlock_allowed=0`、Fastboot unlock/get_unlock_ability 返回 unknown command、BL locked。不同时间点的属性不混为同一次快照。

## 可证伪的新假说
AOSP Android 11 [Settings OemUnlockPreferenceController](https://github.com/aosp-mirror/platform_packages_apps_settings/blob/android-11.0.0_r48/src/com/android/settings/development/OemUnlockPreferenceController.java) 规定是否可点受 bootloader 状态、`isOemUnlockAllowedByCarrier()`、`DISALLOW_FACTORY_RESET` 及管理策略影响。`ro.oem_unlock_supported=1` 只决定功能可见的条件之一。

[OemLockService](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-11.0.0_r48/services/core/java/com/android/server/oemlock/OemLockService.java) 优先 OEM Lock HAL，否则采用 PersistentDataBlockLock。可分别检查 carrier HAL 存在性、PDB、用户限制以及设备管理策略。但 P780 厂商实现尚未取得，AOSP 不保证完全相同。

已完成的第一阶段实测结果和逐字 AOSP 中文资源对照见[2026-10-19 实机报告](p780-oemlock-first-results-20261019.md)；以下保留原始计划命令供审计，不再作为重复采集要求。

## 第一阶段（只读；原厂 Android + ADB）
Windows PowerShell：
```powershell
adb shell getprop ro.oem_unlock_supported
adb shell getprop sys.oem_unlock_allowed
adb shell getprop ro.boot.flash.locked
adb shell getprop ro.frp.pst
adb shell service list | Select-String 'oem_lock|persistent_data_block'
adb shell lshal | Select-String 'oemlock'
adb shell dumpsys user | Select-String 'no_factory_reset|no_oem_unlock|Base restrictions|Device policy'
adb shell dumpsys device_policy | Select-String 'no_factory_reset|no_oem_unlock|Device Owner|Profile Owner'
```
另记录 OEM unlocking 开关下方的具体提示文字。只分享已过滤的输出；完整 dumpsys 可能包含账户/设备敏感资料。

## 分支和风险边界
- 有 `android.hardware.oemlock@1.0` HAL：下一步离线定位 vendor HAL 实现；出现 HAL 不等于它允许解锁。
- HAL 未见但 PDB 存在：调查 user `no_oem_unlock` 与 PDB 回退；未见 HAL 可能只是读取权限/枚举缺失。
- 用户/管理员 `no_factory_reset`：可解释 Settings 一种灰色分支，但不证明 Fastboot 支持解锁。
- 无上述限制但灰色：仅将 P780 Settings 厂商修改列为后续离线审计方向；不能从缺席信息肯定否定某层。

**禁止本阶段**：`service call oem_lock`、Binder 任意事务、设置解锁标志、改 FRP/持久数据块、重刷、EDL/DSU 重试。尤其 AOSP `isOemUnlockAllowed()` 所谓读接口可能同步写 persistent data block OEM Unlock 标志，因此不能用猜事务号的方法读取。即使判定灰色原因，也不代表 `fastboot flashing unlock` 会由 unknown command 变为支持。

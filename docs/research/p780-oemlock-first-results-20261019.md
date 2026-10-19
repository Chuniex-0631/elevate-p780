# P780 OEMLOCK-01 第一阶段实测结果（2026-10-19）

状态：第一阶段已实测，第二阶段只读分支诊断待进行。没有解除解锁限制、Root或改变设备持久状态。

## 来源事实
- 实机 OEM unlocking 整条灰色，开关关闭；提示精确为：`请连接到互联网或与您的运营商联系`。
- 通过 ADB：`ro.oem_unlock_supported=1`；`sys.oem_unlock_allowed=0`；`ro.boot.flash.locked=1`；`ro.frp.pst=/dev/block/bootdevice/by-name/frp`。
- Framework binder 服务列表同时出现 `oem_lock` 和 `persistent_data_block`；两者共同注册并不能说明实际后端。
- `lshal | Select-String oemlock` 没有匹配，但 lshal 同时打印大量 `cannot be fetched from service manager (null)`，不能据此排除 OEM Lock HAL。
- `dumpsys user` 和 `dumpsys device_policy` 针对 `no_factory_reset` / `no_oem_unlock` 筛选未见命中，仅用户服务打印 `Device policy global/local restrictions` 标题。

## 与 Android 11 AOSP 一致的精确 UI 线索
- AOSP Settings 简体中文资源 `oem_unlock_enable_disabled_summary_connectivity_or_locked` 的翻译与设备 UI 字符串**完全一致**。来源：https://github.com/aosp-mirror/platform_packages_apps_settings/blob/android-11.0.0_r48/res/values-zh-rCN/strings.xml
- Android 11 `OemUnlockPreferenceController` 的此文案与 `!isOemUnlockAllowedByUserAndCarrier()` 分支关联；该函数检查 `isOemUnlockAllowedByCarrier()` 以及没有基础 `DISALLOW_FACTORY_RESET` 限制；SIM locked 分支使用另一提示。来源：https://github.com/aosp-mirror/platform_packages_apps_settings/blob/android-11.0.0_r48/src/com/android/settings/development/OemUnlockPreferenceController.java
- Framework `OemLockService` 优先调用 vendor OEM Lock HAL，否则回退 PersistentDataBlockLock。来源：https://github.com/aosp-mirror/platform_frameworks_base/blob/android-11.0.0_r48/services/core/java/com/android/server/oemlock/OemLockService.java
- **解释限制**：本机还没有取得厂商 Settings 和 OEM Lock HAL 的真实实现，不能证明存在联网授权服务器；`sys.oem_unlock_allowed=0` 不是对 carrier HAL 方法返回值的直接读取。AOSP 的 `isOemUnlockAllowed()` 读接口可能同步修改 FRP 位，不应猜测 Binder transaction。

## 第二阶段最低风险只读命令（Windows PowerShell）
```powershell
adb shell logcat -d -b system -s OemLock:I
adb shell 'grep -R -i oemlock /vendor/etc/vintf /odm/etc/vintf /system/etc/vintf 2>/dev/null'
adb shell dumpsys user | Select-String 'Restrictions:|no_factory_reset|no_oem_unlock'
```

有 `Using vendor lock via the HAL` 则优先离线研究厂商 HAL；有 `Using persistent data block based lock` 则研究 AOSP user restriction/PDB 回退。无日志仅说明缓存中没读到该 tag。所有流程不写 FRP、不设置属性、不进行解锁或 Fastboot/EDL。

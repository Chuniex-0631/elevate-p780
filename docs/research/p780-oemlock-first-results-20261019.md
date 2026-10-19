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


## 第二阶段实机结果：OEM Lock 后端已确定（2026-10-19）

机主又取得一次启动后 System logcat，原文：
```text
I OemLock : OemLock HAL not present on device
I OemLock : Using persistent data block based lock
```
因此，**本次 Android SystemServer OEM Lock Service 初始化实际采用了 `PersistentDataBlockLock`，而非 `VendorLock`**；不再以缺少 `lshal` 输出猜测。VINTF `/system/etc/vintf/compatibility_matrix.{2,3,4,5}.xml` 列出 `android.hardware.oemlock` 为框架兼容性条目，并不是设备实现了 HAL 的 manifest 或运行实例。命令没有显示 ODM/vendor 中的 oemlock 声明。

另次 `dumpsys user | Select-String 'Restrictions:|no_factory_reset|no_oem_unlock'` 只命中 Restrictions/Device policy/Effective restrictions 等标题，**没有**任何 `no_factory_reset`、`no_oem_unlock` 记录。这支持“尚无明显用户基础/设备策略限制”这一观察；不能保证 dumpsys 覆盖了所有厂商定制控制点。

**新的张力/可证伪假说**：Android 11 AOSP `PersistentDataBlockLock.isOemUnlockAllowedByCarrier()` 在 User0 不具有 `DISALLOW_OEM_UNLOCK` 基础限制时应返回 true。AOSP Settings 的 `isOemUnlockAllowedByUserAndCarrier()` 还检查当前用户 `DISALLOW_FACTORY_RESET`；目前这两种字符串都未见命中，但机主的开关仍灰色并显示 AOSP carrier/connectivity 文案。合理下一步是**读取 P780 真正 Settings 实现及当前 user restriction 精确快照**，不能直接推断运营商远程服务器正在拒绝，也不能把 FRP bit=0 当作 carrier gate 的结论。

[PC 静态清单](../../evidence/static/20261018-220912/manifest.csv) 已包含 `files\\system_ext\\priv-app\\Settings\\Settings.apk`，当时记录大小 **65,392,240 bytes**，SHA256 `5E44D4F396B4BE7E061DF6269984CAF15DA2FA2E5CBC662FFC6A150A1B995DF7`。该清单**仅证明曾被登记**，不能确认文件现仍在 PC 或原件已进 Git。优先使用本地原件离线检查 DEX 是否包含目标类，不重复 pull 或上传大文件。

### 第三阶段只读/离线建议

```powershell
adb shell am get-current-user
adb shell pm path com.android.settings
adb shell dumpsys user | Select-String 'Restrictions:|no_factory_reset|no_oem_unlock' -Context 0,2
```

上述不执行 OEM Binder 方法，不设置 OEM Unlock Allowed 位。然后在已有 PC 采集目录查找 `Settings.apk`，按 manifest SHA256 复核原件并枚举 `classes*.dex`。如含目标 dex，离线比对 `OemUnlockPreferenceController` 的 `enableOemUnlockPreference()`、`isOemUnlockAllowedByUserAndCarrier()`、`updateOemUnlockSettingDescription()` 实现。原件若不存在，仅在确有必要时只读 ADB pull。最终任何失配假说都不自动变成 Bootloader 解锁或 Root 能力。

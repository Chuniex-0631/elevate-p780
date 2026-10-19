# OEMLOCK-02：设置调用者与权限边界（2026-10-19）

结论：getter/setter 的 customer 检查差异仍成立，但在本轮现有语料中没有发现普通应用/ADB shell可达的特权设置入口。该候选停止作为上机实验；未解锁、未Root、未改变手机状态。

## 范围与复现

起点 main 228e80a5b27a89a377feee6f4010c7e3eaf9beb9。读取机主PC既有静态目录中的APK/JAR，另包含已导出的Settings/framework/services，按整文件SHA256去重，最终296份：176 APK、120 JAR。完整相对路径、大小、SHA及含目标方法名的DEX见[清单](../../evidence/oemlock/20261019/caller-inventory.json)。

扫描每个classes*.dex中的setOemUnlockAllowedByUser字符串；含该名字的DEX解析全部方法定义，用指令解码识别直接invoke，再完整保存命中方法的字节、SHA、偏移和指令。解码方法的字节长度覆盖检查通过。176 APK的manifest解码无异常。工具为[callers.py](../../tools/oemlock/callers.py)、[manifest_audit.py](../../tools/oemlock/manifest_audit.py)，使用相同dex_tables.py与androguard 4.1.4。

此范围不是完整固件；不覆盖缺失vendor服务、动态下载代码、反射构造方法名、native自行构造Binder事务或全部共享UID授权。未命中直接调用不等于所有间接调用均不存在。

## 直接调用结果

共6个直接调用者方法，见[原始指令证据](../../evidence/oemlock/20261019/callers.json)：

|位置|方法|含义|
|---|---|---|
|Settings控制器|onOemUnlockConfirmed|明确传true；唯一应用层直接启用点|
|Settings控制器|onPreferenceChange|关闭分支传false；开启分支转入确认流程|
|Settings控制器|onActivityResult|相关关闭分支传false；另一分支继续弹出确认，不直接传true|
|framework OemLockManager|setOemUnlockAllowedByUser|转发到IOemLockService|
|framework Stub.Proxy|同名方法|Binder封送|
|framework Stub|onTransact|Binder分派，不是额外权限代理|

确认链：EnableOemUnlockSettingWarningDialog.onClick 仅在按钮编号-1时回调目标Fragment的onOemUnlockDialogConfirmed；DevelopmentSettingsDashboardFragment取得OEM控制器后调用onOemUnlockConfirmed。对话框show设置targetFragment并由FragmentManager展示。相关9个方法的原始指令和哈希见[确认链](../../evidence/oemlock/20261019/confirmation-methods.json)。

Settings manifest中未登记EnableOemUnlockSettingWarningDialog为activity/service/receiver/provider/activity-alias；它是内部DialogFragment。开发者设置入口和SubSettings的声明摘录见[组件证据](../../evidence/oemlock/20261019/component-excerpts.json)。没有把静态enabled=false当作运行时禁用证据，也没有从省略exported属性直接推断所有组件不可导出。SettingsActivity.isValidFragment通过SettingsGateway.ENTRY_FRAGMENTS枚举白名单；本轮没有重建所有Fragment入口/参数流，不能称为完整组件安全审计。

这条确认链仍依赖上一轮已核验的Settings开关许可判断。没有发现启动外部Intent即可直接调用该确认方法的证据。onActivityResult不是外部Intent能够任意携带的调用指令，方法名不能当作导出入口。

## 原厂权限证据

从同批framework-res.apk（SHA256 e92f69027d2be2fc6e3a17886e2b7af5fbe1daf94a319003d911ca9b2307ec9e）manifest取得：

- MANAGE_USER_OEM_UNLOCK_STATE、MANAGE_CARRIER_OEM_UNLOCK_STATE、READ_OEM_UNLOCK_STATE：protectionLevel=0x12，即signature | privileged。
- OEM_UNLOCK_STATE：0x02，即signature。

位定义对照[AOSP Android 11 PermissionInfo](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-11.0.0_r48/core/java/android/content/pm/PermissionInfo.java)：PROTECTION_SIGNATURE=2，PROTECTION_FLAG_PRIVILEGED=0x10。原厂实际权限声明是直接证据，AOSP仅用于解释数值。

176 APK中，Settings声明MANAGE_USER_OEM_UNLOCK_STATE并共享android.uid.system；com.qualcomm.location和com.android.dynsystem声明READ_OEM_UNLOCK_STATE；未见其它APK声明上述管理权限。详见[manifest结果](../../evidence/oemlock/20261019/permission-manifests.json)。声明不等于当前实际授予，未声明也不排除通过共享UID获得权限，不能据此声称只有Settings具备能力。前轮shell前置权限异常仍是ADB直接访问受阻的独立证据。

## 决策与下一可证伪边界

OEMLOCK-01的静态解释继续成立；OEMLOCK-02在已扫描语料内**没有形成可达路径**。停止对这6个调用点重复扫描，不调用setter，不改ro.boot.journey.customer、不写FRP，不把确认对话框当作待尝试的绕过方式。

优先级转回“具体服务实现/权限代理证据是否齐备”，而非上机尝试：只有新增系统组件或服务端原件能够补齐某条明确的调用链，才重开针对该组件的离线审计。可证伪标准是完整的普通调用者→入口→身份/参数检查→目标服务路径，而不是同名字符串或权限声明。

customer属性来自启动只读属性且在类初始化缓存；现有材料不足以证明其启动源可以被普通调用者控制。没有可信原厂boot/vendor_boot/实际启动配置时，不将“修改属性”列为实验，也无需再向机主重复索取已在PC的Settings/framework/services文件。Bootloader是否支持正式解锁继续独立未知。

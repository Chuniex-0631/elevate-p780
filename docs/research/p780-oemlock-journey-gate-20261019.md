# OEMLOCK-01：Journey customer gate 离线定位（2026-10-19）

结论：已定位解释灰色开关的厂商服务端条件。不是联网授权服务器的证据；没有 Root、BL 解锁或可用写入入口。本轮仅读取 PC 已存文件和仓库，未访问手机。

## 输入与核验

仓库起点 main：3918f33bb949da25c23fe04604d7284c1adf10a9。读取最近本机 Codex 聊天“继续研究P780的ADB连接”及其 10-oem-unlock 记录、保存的查询异常。重新计算三个原件 SHA256，见[输入清单](../../evidence/oemlock/20261019/manifest.json)。

- Settings.apk：65,392,240 B，5e44d4f396b4be7e061df6269984caf15da2fa2e5cbc662ffc6a150a1b995df7，与历史 PC manifest 一致。
- framework.jar：30,153,054 B，93944fb3db369e013cd5b744c749567f7e9b691cce226f6e6f1744a04476080c。
- P780-services.jar：15,353,744 B，0d93de73a06fca110c2826a92f243ea4afd7d4bf472f27649e0398995adf7345。
- 后两项与既有 DSU 收束专题登记 SHA 一致；services 是已有样本，本轮没有重新从运行设备读取，不能将磁盘身份等同当前内存代码证明。

用仓库原有 DEX 表解析器与 androguard 指令解码器离线解码，共114个目标方法；每个方法检查指令覆盖长度等于原始 insns 长度。提交15个关键方法的 DEX/类/方法/code_item 偏移、原始指令字节、SHA256和反汇编，见[机器证据](../../evidence/oemlock/20261019/focused-methods.json)。保留全部大 APK/JAR 在机主 PC，不上传含身份的原始日志。

## 从 UI 到厂商 gate 的直接证据

1. Settings classes.dex 的 enableOemUnlockPreference 返回 !isBootloaderUnlocked() && isOemUnlockAllowedByUserAndCarrier()；后者仍为 carrier API && !当前用户基础 no_factory_reset。文案方法仍按 bootloader、SIM、carrier/user 分支选择，与 AOSP Android 11 这些相关分支一致。没有在这些已审方法发现额外联网查询。
2. P780-services.jar classes.dex 的 PersistentDataBlockLock.isOemUnlockAllowedByCarrier 返回 !UserManager.hasUserRestriction("no_oem_unlock", UserHandle.SYSTEM)。其后端逻辑本身可与无用户限制并存。
3. **关键差异在 Binder 服务包装层** OemLockService$2.isOemUnlockAllowedByCarrier：权限检查及 clearCallingIdentity 后，先调用后端；若后端允许，再读取 JourneyDebugFeature.IS_CUSTOMER_VERSION；此字段为 true 时返回 false。归纳为：

```text
服务 carrier 查询 = 后端 carrier 允许 && !IS_CUSTOMER_VERSION
IS_CUSTOMER_VERSION <- isCustomerVersion()  // 类初始化时缓存
isCustomerVersion() = SystemProperties.getBoolean("ro.boot.journey.customer", false)
```

服务方法字节偏移0x26之后为后端 false 分支；0x2a读取字段，0x2e的 if-nez 跳到返回 false，0x32仅非customer返回 true。JourneyDebugFeature 位于 framework.jar classes4.dex，其 <clinit> 0x3c调用 isCustomerVersion，0x44写字段。

4. PC既有两份属性文本分别在 01/hand5g_getprop.txt:334、03/hand5g_debloat_audit/01_getprop_full.txt:331 记录该属性为1；同文件fingerprint均为 Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys。这是历史快照，不能冒称本轮当前读数；只保存脱敏选行，不上传全量getprop。

所以“PDB已启用、无用户限制，却显示carrier/connectivity文案”并不矛盾：UI读到的是被 Journey customer gate 再过滤的服务结果。**OEMLOCK-01 从待定位推进为静态根因已定位、历史属性支持；运行内存/同一时刻复核仍有边界。** 不再建议重复联网、换SIM、重查HAL来解释这个分支。

AOSP 对照：[Settings](https://github.com/aosp-mirror/platform_packages_apps_settings/blob/android-11.0.0_r48/src/com/android/settings/development/OemUnlockPreferenceController.java)、[PDB后端](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-11.0.0_r48/services/core/java/com/android/server/oemlock/PersistentDataBlockLock.java)。厂商新增条件的依据是本机原件，不是AOSP推测。

## 最近一轮 Codex 结果的审计修正

framework Stub 常量确实列出查询1/3/5/6/7、写事务2/4；已保存的carrier/user/综合查询Parcel是权限异常，不能当作false。调用6与仓库旧协议禁止综合查询的约束冲突，不能把整轮一概描述为“严格只读查询”。

离线服务代码显示综合查询首先做权限检查，之后才进入后端与同步函数；本次保存异常与前置权限拒绝吻合。另，本机 setPersistentDataBlockOemUnlockAllowedBit 对 PersistentDataBlockLock 后端会跳过 forceOemUnlockEnabled；因此也不能把 AOSP 的通用风险直接写成“本次已写FRP”。本轮没有重放任何Binder方法，旧查询不再作为待办。

## 下一可证伪点 OEMLOCK-02：服务端 getter/setter 一致性与调用者边界

**直接观察**：同一服务 setOemUnlockAllowedByUser 在权限、管理员、admin许可检查后，调用后端 mOemLock.isOemUnlockAllowedByCarrier，再进入后端设备许可设置；这个方法体没有读取 IS_CUSTOMER_VERSION，而公开 carrier getter 有该检查。综合 getter 也直接读后端，不能将其结果与公开carrier getter简单等同。

**假说**：customer gate 可能主要约束 Settings 所读查询，而非在所有服务操作中统一强制。它只构成实现不一致线索，尚未形成普通调用者可达入口。

已排除的捷径：服务 enforceManageUserOemUnlockPermission 明确要求 android.permission.MANAGE_USER_OEM_UNLOCK_STATE；先前shell异常已证实该权限边界。Settings manifest 请求此权限并声明 android.uid.system，但请求/共享UID声明本身不能证明存在任意调用代理。打开开发者选项页面不等于执行setter。

下一阶段只做已有 APK/JAR 的离线调用图审计：查 setter 的调用者、组件导出、组件权限、参数来源、确认界面及调用UID。若所有路径都要求真实用户确认且灰色gate不可越过，或普通调用者均被权限拦截，则此候选在现有语料内关闭；只有发现可验证的普通调用者→特权组件完整路径，才另行设计不写入的验证。本轮没有验证这种路径，也不建议直接调用setter、修改ro.boot属性、反射改字段、写FRP或测试解锁。

不重开DSU/旧Loader/工程菜单盲扫。Bootloader自身是否支持解锁仍独立未知，服务许可不等于解锁能力。

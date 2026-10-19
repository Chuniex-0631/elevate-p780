# NATIVE-01：P780 运行端点与诊断 JNI 失败链（2026-10-19）

结论：补齐了旧 native 矩阵缺失的诊断 Java 调用方和运行身份。QTIDiagServices 的启动日志显示 JNI 初始化因诊断 HIDL 连接失败而退出；这不是可用的 OEM 管理代理。Journey 两个 root 诊断进程确实运行，保留其厂商实现为下一条件候选，但仍没有普通调用者到 Root/分区写入的完整路径。

## 采集范围与输入身份

经机主授权，通过 ADB 读取限定属性、目标进程/服务、目录元数据、目标包及限定日志；导出三个系统文件。没有设置属性、调用 OEM Binder getter/setter、发送诊断/TEE/socket 命令、安装应用、重启或刷写。lshal 用于服务枚举，发生大量 cannot be fetched 警告，不能把它当完整成功的 HAL 运行清单。

本轮 fingerprint 为 `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`；活动槽 `_b`；`ro.boot.flash.locked=1`、verified boot `green`、SELinux `Enforcing`。`ro.boot.journey.customer=1`，补齐 OEMLOCK-01 的当前属性支持。重新 pull 的 services.jar 与历史字节一致；仍不是当前内存代码 dump。

|本轮导出文件|大小|SHA-256|与历史文件|
|---|---:|---|---|
|QTIDiagServices.apk|12702|131e725841b919a0cb1b452b4a2f8b40a214322d371fea139a13343188c2a3ff|一致|
|libDiagService.so|15960|12a65895ee4e3a689da320579da2a208677b08fa7437674bf4b604e8090ce756|一致|
|services.jar|15353744|0d93de73a06fca110c2826a92f243ea4afd7d4bf472f27649e0398995adf7345|一致|

原件留机主 PC 的 `11-native-live/`，Git 只保存提取证据与工具。见[输入清单](../../evidence/native/20261019/input-manifest.json)和[采集摘要](../../evidence/native/20261019/observations.json)。

## 新增调用链：APK → JNI → 初始化失败

旧[接口矩阵](p780-native-interface-crosscheck-20261018.md)只扫描了73个JAR的相关字符串，没有诊断Java调用方。本轮对已有且重新核验身份的APK解码16个方法体，并列出包含 native 声明的17个方法：

1. `Diag_OnBoot` 的 BOOT_COMPLETED 路径显式启动 `QTIDiagServices`。
2. `onCreate` 创建 Handler 和 `DiagJNIInterface`；后者类初始化调用 `System.loadLibrary("DiagService")`，捕获加载异常后只打印警告。
3. JNI `JNI_OnLoad` 导出是 CFI 跳板 `0x2090 → 0x1460`。从 ELF `.gnu_debugdata` 解出 `JNI_OnLoad.cfi`，结合 `.rela.plt` 核对，`0x16b8` 调 registerNativeMethods，随后 `0x1710` 调 `Diag_LSM_Init`；失败分支在 `0x1744` 取失败文案，跳到 `0x16d0` 记录错误，在 `0x16d8` 令返回值为 -1。成功路径才在 `0x173c` 调 `diagpkt_tbl_reg`。不能把4字节导出跳板误当完整实现。
4. 日志缓冲区中同一进程的 `2026-10-19 21:41:16` 记录依次为：尝试加载库 → `Unable to connect to hidl server` → `Failed to open handle to diag driver, error = 25` → `Diag_LSM_Init call failed` → `WARNING: Could not load libDiagService`。这是保留的启动时失败，不是本轮主动重新初始化；不能据此断言 HIDL 此后一直不可用，也不能将 error 25 当唯一根因。
5. 本轮 `dumpsys activity services` 仍列该应用服务，进程域为 `system_app`、UID 1000。包管理器列 DIAGNOSTIC、REBOOT、MANAGE_USER_OEM_UNLOCK_STATE 已授权（共享UID上下文）；拥有权限不等于提供代理。

## 调用者边界

- manifest 的 Boot receiver 明确 `exported=false`；service 无 intent-filter、无显式 exported。在 targetSdk 30 的默认规则下，该 service 不对外导出。`onBind` 返回 null，`onStart` 空实现，`onCreate` 不解析外部 Intent 参数。
- 唯一 Handler 命令分支为字符串 `reboot`，调用 `PowerManager.reboot(null)`；没有 OEM setter、文件写入或任意命令分支。`getNextCommand()V` 确实是声明的 native 方法，不能因16个有代码的方法不含它就声称缺失。
- 旧[编译策略矩阵](p780-native-interface-crosscheck-20261018.md)对 system_app 未见 diag HIDL find/open allow，与启动连接失败方向一致。但本轮没有得到对应 AVC 命中，不能认定 SELinux 是唯一实际原因。不能凭 HIDL 名称在 lshal 中出现就声称其可访问。

因此此 APK 在已审入口内关闭为普通调用者的 OEM/Root 候选；没有启动它或发送 reboot 消息来验证。

## 运行状态补齐与下一条件候选 NATIVE-02

|运行进程|UID / SELinux 域|本轮新证据|
|---|---|---|
|journey_diag_ext_system|root / vendor_mmi_sys|ps存在，init.svc 属性为 running|
|journey_diag_ext_vendor|root / vendor_mmi|ps存在，init.svc 属性为 running|
|qseecomd|system / tee|ps存在|
|qseecom@1.0-service|system / vendor_hal_qseecom_default|ps存在|
|ssgtzd|system / vendor_ssgtzd|ps存在|
|diag-router|system / vendor_diag-router|ps存在；不能把它自动认定为 Idiag HIDL 服务端|
|warehouse@1.0-service|system / hal_journey_warehouse_default|ps存在|

这纠正“disabled 服务可能完全没运行”的不确定性，但不证明对应 init 属性动作、builtin 或socket协议可用。`diag_ext_socket`、`qwes_ipc`、`ssgtzd` 名字可枚举，元数据为问号，未读到标签/DAC；不能据此确认0666或可连接。`persist.vendor.diag.journey.enabled` 返回空，不解释为0或不存在。

下一条件候选仍是[Journey init/debug_prop边界](p780-policy-boundary-audit-20261018.md)：已知编译策略允许 shell 设置 debug_prop，已有 RC 把部分 sys.journey 属性展开到厂商动作；本轮确认相关 root 进程运行。**仍缺 init builtin 注册、write_misc 参数边界及诊断服务实现**，没有新增任意读取/写入能力。没有触发这些属性；日志无相关错误命中也不能证明注册成功。

新增读取边界：三个 vendor 接口库的 `ls -l` 均 Permission denied；首次尝试导出 `/vendor/bin/diag-router`、`/vendor/bin/ssgtzd` 也在远端 stat 被拒绝。旧的 init/Journey/gsid 拒绝路径未重试。后续不要更换路径绕读或反复 pull；只有可信同构建原厂材料/对应源码/新增合法可读服务端实现，才重开方法级审计。当前该实现取得分支 BLOCKED，不等于整项研究结束。

## 可复核性与限制

[DEX方法](../../evidence/native/20261019/diag-methods.json)、[全部声明](../../evidence/native/20261019/diag-declarations.json)、[manifest](../../evidence/native/20261019/diag-manifest.xml)、[ELF分析](../../evidence/native/20261019/diag-elf.json)、[目标进程启动日志](../../evidence/native/20261019/diag-process-log.txt)、[运行进程](../../evidence/native/20261019/processes.txt)及[服务状态](../../evidence/native/20261019/diag-service.txt)随本轮提交。方法字节SHA和指令覆盖校验通过；native符号同时保留导出跳板与minidebug实现，PLT标签来自重定位表，不是猜测函数名。

工具见 [native/README](../../tools/native/README.md)。仅验证本轮改动的JSON/Python语法、指令SHA和相对路径链接；没有在完整克隆上运行仓库全量历史证据验证器。没有 Root、Bootloader 解锁、FRP 修改或永久分区写入成果。

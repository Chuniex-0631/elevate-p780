# P780 第十轮 DSU 首次试机：下载完成后重启仍返回原厂系统（2026-10-18）

> **直接实机新进展：** 机主操作了 Android 15 DSU Loader，下载显示完成，通知要求重启进入 DSU；机主多次点击通知“重启进入 DSU”，每次设备均重新启动回原厂 Android 11，同一通知仍出现。这是**每次人为点击触发的重复回原系统**，**不是**设备持续自主重启的 bootloop，也不是 Android 15 已成功启动。未丢失原厂开机能力。

## 观察到的动作与结果（机主原话整理）

```text
下载 GSI → 下载完成，提示点击重启进入 DSU
→ 点击重启，系统重启 → 实际进入原系统，仍提示点击重启进入 DSU
→ 再次点击重启，系统重启 → 仍进入原系统，通知保持
→ 重复
```

- 实验选择按上轮建议倾向 Google Android15 QPR2 ARM64 无 GMS `BP1A.250405.005.C1`，但**机主本轮未再次贴出下载通知中的准确镜像详情**，因此具体已装镜像 ID 需要依据日志/通知二次核对；不能仅凭既定方案当成实机精确实录。
- “显示下载完成并出现重启按钮”说明 UI/安装服务认为已有可用于启动的 DSU 任务/镜像；**尚未通过 `gsid` 的 `isGsiInstalled/isGsiEnabled` 单独确认映像安装/启用状态**。没见 Android 15 桌面、开机界面或 `ro.gsid.image_running=true` 的证据。
- P780 仍 Bootloader LOCKED、没有 Root；正常原厂系统成功启动至少两次，说明当前并非原厂系统无法开机，但不能由此保证将来任何镜像测试均无数据丢失风险。

## AOSP 可形成同样表象的不同故障层级（不是已证实根因）

1. **安装器和启用标记不一致**：UI 通知可能延续已安装状态，而 `gsid` 的 `isGsiEnabled`、active DSU slot 或 boot indicator 没有正确设置或在 one-shot 失败后被清除；表现为重启后原厂系统可用。无当前 `gsi_tool status` 和日志，未证实。
2. **first-stage DSU 条件检查失败**：AOSP [first_stage_mount.cpp](https://android.googlesource.com/platform/system/core/+/6ad4d0a601485475645ddd1b23181a4c31754977/init/first_stage_mount.cpp) 在 `UseDsuIfPresent()` 调用 `CanBootIntoGsi()`，不满足时明确写 `DSU ... proceeding with normal boot`；随后读取 active DSU slot、尝试把 backing image 映射成临时逻辑分区。若映射或标志操作失败，可能放弃 DSU。具体 P780 分支与实现未核实。
3. **AVB 额外 GSI 受信密钥不匹配**：P780 fstab 曾引用 q/r/s 普通 GSI `.avbpubkey`，Android15 GSI 的实际 `system.img` AVB Footer signing key 尚未读到；第八轮 24 条 Google JSON 均缺可选 `pubkey`，不等于真实镜像无需验签。此假说合理但**尚未证明**。
4. **后续 init / FBE / Gatekeeper / SELinux / HAL 失败及自动回原系统**：启动到 GSI 极早期失败也可能表现为用户最后只见原厂启动；需要早期启动日志/ pstore / bootreason / service 日志证据，不能靠 UI 断言是哪一层。

## 当前停止线与安全取证（不卸载临时镜像、不重启）

- **不要**继续循环点击通知 Restart；暂不点 Discard，也不执行 `gsi_tool enable/disable/wipe/wipe-data`、`fastboot flash`、`setprop` 或 EDL；保持原厂系统在线以保留可能的有限日志。
- Windows PowerShell 第一阶段先保存当前日志（`logcat -d` **不会清空 buffer**）：

```powershell
adb logcat -b all -d -v threadtime -t 15000 > ".\p780-dsu-after-reboot.log"
Select-String -Path ".\p780-dsu-after-reboot.log" -Pattern 'dsu|gsid|gsi|DynamicSystem|first_stage_mount|avb|verity|liblp|rollback|ImageManager' | Set-Content ".\p780-dsu-filtered.txt"
```

- 第二阶段仅查询如下字段：

```powershell
adb shell getprop ro.gsid.image_running
adb shell getprop ro.boot.slot_suffix
adb shell ls -l /sys/fs/pstore
adb shell gsi_tool status
```

- AOSP [Android11 gsi_tool.cpp](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-cts-11.0_r16/gsi_tool.cpp) 的 `status` 基于 `isGsiRunning` / `isGsiInstalled` / `isGsiEnabled`，典型输出组合如 `installed` 后 `enabled`/`disabled`，或者无GSI时报 `normal`。此查询可能按需启动 `gsid` 守护进程（可能改变进程态），因此**必须在抓日志之后执行**，不可当作绝对零变更。若权限不足需原样记录。
- `/sys/fs/pstore` 是某些 Android 设备保存上次异常启动 Kernel/ramoops 日志的路径；可先 `ls` 判断存在/权限。缺失/权限拒绝或日志仅包含正常启动都不能排除 DSU 早期失败。当前 logcat 也可能在每次重启时重新初始化，不保证保存上次失败的 first-stage 日志。
- **隐私**：完整 `p780-dsu-after-reboot.log` 可能包含设备关联信息、应用活动与网络/个人数据，优先只发送 `p780-dsu-filtered.txt` 与命令文本输出；任何疑似 IMEI/SN/账号 Token 先脱敏，原始系统日志不要直接提交 GitHub。

## 下一步证据分流

| 原始状态返回 | 下一轮优先方向 |
|---|---|
| `installed` + `enabled` | 分析 first-stage `CanBootIntoGsi/MapAllImages`、AVB、公钥、pstore/bootreason；仍**不立即强制重启** |
| `installed` + `disabled` | 对照 one-shot DSU 标记是否在尝试失败后消耗/重置，结合 UI 日志；不立即 `enable` |
| `normal` | 结合动态安装服务缓存与 `gsid` 镜像/slot 真实状态，UI 与 backend 可能不一致 |
| 权限拒绝/空/daemon不可达 | 保存准确原文，使用现存日志和权限允许的只读 ADB 先排查 |

## 状态

**这是一个真实、未成功的 DSU 启动尝试，值得记录，但不应记为“启动 GSI 已成功”或“P780 已证实公钥不匹配”。** 先保留现有原厂可正常开机状态和失败证据，不增加有数据擦除风险的操作。收到机主脱敏诊断记录后再缩窄根因。

## 2026-10-18 第十一轮：实际 GSID 状态和两份日志已获得，AOSP 单次启动行为解释

机主新提交 ADB 终端输出及 `p780-dsu-after-reboot.log`、`p780-dsu-filtered.txt`。研究环境直接读取了上传的实际文件原始字节，不使用外部网页搜索代替设备日志。

### 实机命令结果

```text
$ adb shell getprop ro.gsid.image_running
# 空
$ adb shell getprop ro.boot.slot_suffix
_b
$ adb shell ls -l /sys/fs/pstore
ls: /sys/fs/pstore: Permission denied
$ adb shell gsi_tool status
installed
disabled
```

Android 11 [gsi_tool.cpp::Status](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-cts-11.0_r16/gsi_tool.cpp) 顺次调用 `isGsiRunning()` / `isGsiInstalled()` / `isGsiEnabled()` 并输出 `running/installed/enabled|disabled`。此处仅输出 `installed` 和 `disabled`，是**当前的非运行、已安装且未启用状态**，与现正运行的原厂 Android11 相容。`ro.gsid.image_running` 在此机 shell 查询为空，不能擅自将空值当作布尔 false；由 GSID status 没有 `running` 更直接地支持当前非 GSI。

### 文件完整性、类型和精确日志证据

| 文件 | 原始大小/格式 | SHA-256（原始文件） | 观察 |
|---|---|---|---|
| `p780-dsu-after-reboot.log` | ~4.1MB / UTF-16LE, CRLF / 15455行 | `955c9775371658b36d59e749c648149193a05746a72d26807f09a3f97de6e970` | 10-18 06:31:40.616 至 06:36:36.673；记录的是原厂用户空间日志，并非 first-stage 原始 kmsg |
| `p780-dsu-filtered.txt` | 678B / ASCII/CRLF / 3条 | `333d7ac1de09d46f4a77a3611842a38d47c0ec14819d2b2b23d6ebfb2a74cf76` | 只包含下列3项与 DSU 包/服务相关的筛选结果 |

筛选日志摘录（删去主机用户名等路径；以下为原始设备日志字段）：

```text
10-18 06:31:40.743 I am_proc_start: [0,3755,1000,com.android.dynsystem:dynsystem,service,{com.android.dynsystem/com.android.dynsystem.DynamicSystemInstallationService}]
10-18 06:31:40.743 I ActivityManager: Start proc 3755:com.android.dynsystem:dynsystem/1000 for service {com.android.dynsystem/com.android.dynsystem.DynamicSystemInstallationService}
10-18 06:31:40.852 I DynamicSystemService: isInstalled(): true
```

完整日志第418行还有 `DynSystemInstallationService: onStartCommand(): action=android.os.image.action.NOTIFY_IF_IN_USE`。第442行 `notification_enqueue` 对 `com.android.dynsystem` 产生带两项操作的通知；这与重启后仍看到通知一致。**不是**下载/安装或实际 GSI 启动验证通过的日志。Logcat 另出现大量通知显示/隐藏、系统常规进程/通信日志，未找到带 `DSU`, `GSI`, `first_stage`, `AVB`, `verity`, `liblp`, `rollback` 明确关键词的有效早期失败错误；日志开头就是原厂用户空间正常启动后的事件，并未保留上次启动切换中发生的早期内核 init 过程。不能因为搜索无结果就断言 AVB/MapAllImages 没有失败。

**隐私：** 本研究只把上述3条必要的非唯一日志、文件长度和 SHA256 记录到私有仓库；**不将 4.1MB 原始 Logcat 或完整筛选文件的含 Windows 用户路径复制到 Git，避免应用/网络/设备唯一标识泄露**。

### 改变故障解读的 AOSP Android 11 直接源码证据

1. [Android 11 `libgsi.cpp::CanBootIntoGsi`](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-platform-11.0.0_r16/libgsi.cpp) 第71～117行：`CanBootIntoGsi()` 在验证安装状态/读取 `kDsuInstallStatusFile` 后，若处于 `kDsuOneShotBootFile` **一次性启动模式**，则**先把安装状态写成 `disabled`，仅对之后的启动生效**，再返回 `true` 继续当前引导。因此**回到原厂系统后见 `installed/disabled` 与 first-stage 曾认领一次性启动完全相容，甚至是支持这种过程的间接迹象，但不能作为唯一证据断言已消费**（也可能由别的路径清除/禁用）。
2. [Android 11 DynamicSystemInstallationService](https://android.googlesource.com/platform/frameworks/base/+/978ecf991a9a/packages/DynamicSystemInstallationService/src/com/android/dynsystem/DynamicSystemInstallationService.java) 默认 `mOneShot = intent.getBooleanExtra(KEY_ONE_SHOT, true)`；点击通知的 `Restart` 在调用 `mDynSystem.setEnable(true, mOneShot)` 成功后 `PowerManager.reboot("dynsystem")`，因此**默认单次启动**并非“不小心禁用了 DSU”的充分证明。P780 OEM 固件具体定制仍需通过真实行为和日志辨认。
3. [AOSP `first_stage_mount.cpp::UseDsuIfPresent`](https://android.googlesource.com/platform/system/core/+/9583e92257ab85075231b014f0999d5a5dab9910/init/first_stage_mount.cpp) 后续还需读取 active slot、`ImageManager::MapAllImages`、`TransformFstabForDsu`、实际 AVB 验证及挂载。**即使消费了一次性标记，也未必成功完成任意后续步骤**；日志缺少 first-stage 行，暂时无法判断是否发生映射失败、GSI签名公钥拒绝或后续 HAL/加密故障。

### 后续取证步骤（仍不触发重启/写入）

如果设备 shell 支持内核 logd 缓冲区和上一轮 persistent buffer，可仅作以下有限只读尝试：

```powershell
adb shell logcat -g
adb shell logcat -b kernel -d -v threadtime | Select-String -Pattern 'DSU|GSI|first_stage|AVB|verity|mapped|rollback|init'
adb shell getprop ro.boot.bootreason
adb shell getprop sys.boot.reason
```

用户不一定有读取 kernel buffer/pstore 的权限，上次 `ls /sys/fs/pstore` 已明确 Permission denied，因此可能拿不到早期失败日志；错误/零行输出是有效实验结果。**不再要求重新安装、恢复出厂、向 `/metadata/gsi` 越权读取、启用 sticky 模式或重复点击 Restart**。必要时可在明确告知风险后另行设计**真正新的一次**启动前后日志观察，但当前不得以证据缺失为由贸然重启。

### 本轮结论

已成功确认：**GSID已识别到安装的GSI；当前处于disabled、非GSI运行；原厂系统启动后向通知服务报告isInstalled=true，通知正常生成。** AOSP 11 一次性启动规则为 `disabled` 提供了合理的正常解释，因此 **不能把 `disabled` 直接当作启动器未设置 enable 的错误；也不能认定 AVB 签名不匹配已经证实。** 剩余关键分叉为早期流程是否识别/消费 one-shot、映像映射是否成功、实际 AVB/ramdisk信任公钥、后续GSI/Vendor启动能否成功。

## 2026-10-18 第十二轮：Bootreason 精确为 `reboot,dynsystem`，仅一次启动且内核 logcat 空

机主补充说明：**点击 DSU 通知 Restart 后，仅经历一次正常重启，就进入 Android11 原厂系统；没有观察到 Android15 启动画面，也没有中途自动再重启。** 这是由人手动发起的两次独立重启尝试，不是设备自身连续 bootloop。机主当前正常处于原厂系统，并提供以下实机 ADB 原文：

```text
$ adb shell logcat -g
main: ring buffer is 2 MiB (1 MiB consumed), max entry is 5120 B, max payload is 4068 B
system: ring buffer is 2 MiB (388 KiB consumed), max entry is 5120 B, max payload is 4068 B
crash: ring buffer is 256 KiB (374 B consumed), max entry is 5120 B, max payload is 4068 B
kernel: ring buffer is 2 MiB (0 B consumed), max entry is 5120 B, max payload is 4068 B
$ adb shell logcat -b kernel -d -v threadtime | Select-String -Pattern 'DSU|GSI|first_stage|AVB|verity|mapped|rollback|init'
# 无匹配行
$ adb shell getprop ro.boot.bootreason
reboot,dynsystem
$ adb shell getprop sys.boot.reason
reboot,dynsystem
```

### 从这四项能确认什么

1. **真实重启入口已命中 DSU 流程**：Android11 AOSP [DynamicSystemInstallationService.java `executeRebootToDynSystemCommand`](https://android.googlesource.com/platform/frameworks/base/+/978ecf991a9a/packages/DynamicSystemInstallationService/src/com/android/dynsystem/DynamicSystemInstallationService.java) 在 `mDynSystem.setEnable(true, mOneShot)` 成功后调用 `PowerManager.reboot("dynsystem")`。两个 boot reason 属性均显示 `reboot,dynsystem`，**比普通“用户按了通知”更强：上次重启带有 Android DSU 专用重启原因**。不过它只证明请求/重启原因，**不直接证明 first-stage 最终识别、成功映射或通过 AVB**。
2. **没有额外重启的观察**：机主亲自确认是一轮正常重启直接返回原厂系统。结合 [Android11 `first_stage_mount.cpp::UseDsuIfPresent()`](https://android.googlesource.com/platform/system/core/+/9583e92257ab85075231b014f0999d5a5dab9910/init/first_stage_mount.cpp) 能在 `CanBootIntoGsi`、active DSU slot、`ImageManager::MapAllImages` 或 `MarkSystemAsGsi` 等判断失败时**返回继续原厂 system 启动**，因此“在真正 GSI user-space 出现之前被弃用/回退”值得优先怀疑。**不能**只凭没有肉眼看到第二次重启就完全排除 AVB/挂载、设备定制异常或硬件对某次自动切换不可见。
3. **早期错误日志仍不可获取**：`logcat -g` 显示 `kernel` logd buffer 容量 2MiB但当前实际记录 **0B**，而第一阶段 `init` 的 kmsg/dmesg 记录未必能通过这一 buffer 读取；`logcat -b kernel` 无任何匹配**不能解读为“内核没发生错误”**。上轮 `/sys/fs/pstore` shell 报 `Permission denied`，现阶段仍无可信 first-stage 错误/堆栈。重复取同样内核 logcat没有价值。
4. **与已知 GSID 状态结合**：前轮 `gsi_tool status` 为 `installed`+`disabled`，此前 Logcat `DynamicSystemService: isInstalled(): true`；AOSP 的 one-shot `CanBootIntoGsi` 可在随后挂载之前消耗启用标志，并正常在回原厂后看到 disabled，**因而当前最合理的模型是“请求成功→一次性状态可能被消耗→first-stage 可能提前退回原系统”**。但尚无在重启前采集的 enabled 状态或失败分支原始日志，仍是解释模型而非 Root Cause Confirmed。

### 更新后的优先级（防止无证据地试错）

- **第一优先**：有 first-stage 正常回退路径的「DSU 状态/slot/MapAllImages/MarkSystemAsGsi」候选。AOSP 中 `UseDsuIfPresent` 可以直接返回原厂启动，符合机主单次重启的客观观察。
- **第二优先、仍未证实**：真实 Android15 GSI AVB 签名公钥与 P780 ramdisk 信任公钥不符、rollback/verity/挂载，或启动早期 Vendor/HAL 不兼容。缺少具体 GSI 签名、内核初始日志及设备实际公钥，不应强作等级绝对排序。
- 不需要再采集 `logcat -b kernel` 或普通 `getprop bootreason`，已经完成。**不要**继续重启，或执行 `gsi_tool enable`（默认 sticky）、`disable`、`wipe` 或厂商 fastboot/EDL 写操作；不要现在为了 DSU 工具恢复系统出厂、改写 AVB、刷入不明镜像。当前原厂系统可用且 GSI 安装材料还在，应保留现场。
- 如果决定后续再做**受控一次** DSU 启动实验，应先取得机主对数据丢失、Recovery/清除 userdata 风险的再次确认、明确采集办法与停止条件，而不能期待 Android shell 的事后 logcat 会恢复不可见的 first-stage 日志。可转向 Linux/Android AOSP 离线静态分析 `ImageManager`/fstab 转换，或等待可信原厂 boot ramdisk/DSU 原始签名证据。

### 当前实证上限

**证明成功：DSU 服务安装状态存在、UI发出DSU专用重启、系统按 `reboot,dynsystem` 完成单次重启、返回原厂系统。未证明成功：GSI 运行、分区映射、AVB验证、Root/BL解锁。未证明根因：哪一个 first-stage 条件首先失败。**

# P780 Android 11 DSU / GSI 可信启动支线 — 源码交叉核对（2026-10-18）

> **第八轮（2026-10-18）最新证据：** 用户已上传 PC 获取的完整 DSU 子目录压缩包，6个 Google JSON / 24个候选经 ZIP CRC、SHA-256、JSON 结构复核通过；截图四项分别为 Android15 `BP1A.250405.005.C1` 两项和 Android16 **`CP11.251209.009.A1`** 两项（先前 `CPI1` 为读图/脚本拼写错误）。**24条全部不含 `vndk` 或 `pubkey` 字段**，因此 DSU Loader 菜单并未显式验证 VNDK30 和 GSI 公钥。详情见 [第八轮官方目录独立核验](p780-dsu-gsi-catalog-verified-20261018.md)。**仍未下载安装/启动任何 GSI，BL LOCKED、无 Root。**

> **2026-10-18 最新实机状态：`com.android.dynsystem` 已由机主通过 Android 原生 `install-existing --user 0` 成功恢复，`pm path` 可定位原厂 APK，`dumpsys` 已确认 `installed=true`。开发者选项 DSU Loader 和在线 GSI 选项已见，但尚未执行 GSI 下载、安装、重启或启动验证。** 重点不是刷写原有分区，而是核对是否存在官方提供的、在 LOCKED 状态下临时启动受信任 GSI 的 DSU 通道。不能把它误称为 Root/BL 解锁/AVB 漏洞的现成 PoC。

## 发现源头：实际 Fstab 中的 GSI 公钥

2026-10-18 机主读取并作为会话内容提交 `/vendor/etc/fstab.default`、`/vendor/etc/fstab.emmc`，两者 `system` 行均含：

```text
avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey
```

而 AOSP Android 11 [system/core/fs_mgr/fs_mgr_fstab.cpp](https://android.googlesource.com/platform/system/core/+/ebce675b177f22a3248b1104b21c9c79937b8fda/fs_mgr/fs_mgr_fstab.cpp) 的 `BuildGsiSystemFstabEntry()`，明确包含相同的 q/r/s GSI 公钥路径。AOSP [Dynamic System Updates](https://source.android.com/docs/core/ota/dynamic-system-updates) 说明开发者 GSI 可通过预置开发公钥在 **LOCKED** 状态下验证并临时启动。**这证明所见配置符合标准 DSU/GSI 设计，不足以证明 P780 已实际启用该功能或这三份文件当前可读取/生效。**

## 与 P780 已证实实机信息的条件交叉检查

| AOSP DSU 需要 | 当前 P780 证据 | 判定 |
|---|---|---|
| Android 11+ DSU Loader 用户界面 | Android 11；**机主亲眼确认开发者选项有 DSU Loader** | **入口存在已实机确认**；启动后镜像列表和安装行为尚未验证 |
| Android 动态分区 | `ro.boot.dynamic_partitions=true` | 满足 |
| F2FS 或 ext4 `/data` | 两份 fstab 都声明 `f2fs` | 配置符合 |
| 首阶段 `/metadata` | fstab `/metadata` ext4 `first_stage_mount` | 配置符合；需硬件/运行态佐证 |
| dm-verity、部分 DSU kernel configs | 已观察到五份 dm-verity 设备；kernel 5.4.233 | DM_VERITY 运行迹象强；`CONFIG_DM_VERITY_FEC` 与完整 DSU 依赖尚未直接复核 |
| 能够验开发 GSI 签名的对应公钥 | `avb_keys=/avb/q-gsi...` 等 fstab 声明 | **仅配置候选**；未核对 `/avb/*` 的启动时文件、内容和 DSU 验证结果 |
| System/GSI 与 Vendor HAL 兼容 | P780 Android 11 / arm64 / vendor HAL、Gatekeeper/Weaver 未审计 | 未验证 |
| 空间需求 | AOSP 提示大约 10GB 临时空间 | 未确认可用空间（当前阶段不安装） |

**隔离两种钥匙：**
- Key Attestation 已独立证实 `verifiedBootKey=7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6` 匹配 `testkey_rsa4096_pub.pem` 的根 AVB 公钥二进制 SHA-256。
- `/avb/q-gsi.avbpubkey` / `r-gsi` / `s-gsi` 是另一组由系统启动 ramdisk 配置引用的**开发 GSI 签名公钥候选**，不能当作根 AVB 签名密钥、不能以其中之一的存在直接得出任意 root GSI 会被接受。

## 第一阶段允许的只读验证（Windows PowerShell）

以下只读 Android 属性、列举包/系统可见文件，**不执行** `adb reboot`、`setprop`、`gsi_tool enable/install/wipe`、DSU Loader 下载、EDL、Fastboot 或 `dd`：

```powershell
adb shell pm path com.android.dynsystem
adb shell ls -l /system/bin/gsi_tool /system/bin/gsid
adb shell getprop init.svc.gsid
adb shell getprop persist.sys.fflag.override.settings_dynamic_system
adb shell getprop ro.gsid.image_running
adb shell ls -l /avb/q-gsi.avbpubkey /avb/r-gsi.avbpubkey /avb/s-gsi.avbpubkey
```

需要手动在开发者选项中**只观察** `DSU Loader` 是否存在，不点击镜像或开始安装。应用包存在与服务二进制存在，都不等于功能运行成功。`/avb/*` 路径在启动 ramdisk 内存在但启动后不可见、或 shell 权限不足，都不能单独否定功能。`init.svc.gsid` 为空/`stopped` 也不能证明系统不支持按需启动的服务。

注意：官方 Android 11 [gsi_tool.cpp](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-cts-11.0_r16/gsi_tool.cpp) 虽允许 `gsi_tool status` 作为普通用户查询，但工具会在必要时通过 `ctl.start=gsid` **启动服务**，所以本轮严格只读阶段不将它列为默认操作。禁止执行 `gsi_tool install|enable|disable|wipe`。

## 研究价值与停损

- 如果正常 DSU 组件、前端、GSI 公钥和相容的供应商支持均存在，则考虑单独评估**官方签名的临时 GSI** 能否运行；这是一条不会直接覆盖原厂 boot/system 分区的标准 OS 测试路径，不等于漏洞利用或 Root。
- 如果仅 Fstab 写了 AVB GSI keys，系统却缺少 DSU 组件或强制禁用，则优先判为模板配置/不可用功能，不继续通过 `setprop` 强行开启，也不冒险向 Android 11 的锁定态设备写镜像。
- 不混用本次 DSU 与先前 Google OTA Prober；后者为旧版本 OTA 查询、机主已决定暂缓。
- P780 的真正两个未解决主阻断仍是**匹配 `_162` 的分区原始镜像/签名描述符**与**经证实的 locked 状态分区写入/可信修复能力**。DSU 如果可用也只能作为独立、受限制的实验接口，不能代替后者。

## 2025 SPICES 论文交叉限制

[AVBTestKeyInTheWild 论文摘要](https://research.jku.at/en/publications/workshop-avbtestkeyinthewild-bypassing-android-verified-boot-usin/) 的关键是区分 AVB 加密验签与设备允许的刷写/修复通路。2026-10-14 [JVN#47427200](https://jvn.jp/en/jp/JVN47427200/) 确认 P780 全版本弱密钥和物理接触威胁，但没有发布该机的具体成功写入/恢复过程。若 DSU 受官方内置公钥限制，它不是“借助主 AVB 弱密钥自然获得写入权限”的证明。

## 2026-10-18 P780 实机第一轮 DSU 只读结果（机主 ADB 终端）

以下信息由机主在 Windows PowerShell 执行前文的六组命令后提供；**尚未执行 gsi_tool status/install、没有修改任何设备状态**。

| 原命令 / 目标 | 实机原样结果 | 可靠的判断范围 |
|---|---|---|
| `adb shell pm path com.android.dynsystem` | 空（无 APK 路径） | 当前 PackageManager 未返回标准 DSU Loader 包，可能没有安装/对当前用户不可用；不证明整个 GSID 框架缺失 |
| `adb shell ls -l /system/bin/gsi_tool /system/bin/gsid` | `gsi_tool` 存在，`-rwxr-xr-x 1 root shell 47016`；`/system/bin/gsid: Permission denied` | CLI 工具已编入当前 `/system`；不能把 SELinux/权限拒绝等同于 `gsid` 文件不存在 |
| `adb shell getprop init.svc.gsid` | 空 | 没有解析到服务状态；不能仅从空字符串断言服务未安装、运行中或永远被禁用 |
| `adb shell getprop persist.sys.fflag.override.settings_dynamic_system` | 空 | 没有覆盖功能开关的可见值，不是明确 false |
| `adb shell getprop ro.gsid.image_running` | 空 | 未提供运行 GSI 的正面证据；不能据此作全部状态结论 |
| `adb shell ls -l /avb/{q,r,s}-gsi.avbpubkey` | 三项均 `No such file or directory` | **当前用户空间可见的 `/avb` 不存在这些文件**，但早期 boot ramdisk 文件可能在切换根目录时被释放 |

### 与 AOSP Android 11 原码的关键重新解释

- [AOSP Android 11 gsid.rc](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-11.0.0_r13/gsid.rc) 把 `gsid` 定义为 `/system/bin/gsid`、`interface aidl gsiservice`、`oneshot`、`disabled`。这意味着普通启动下不自动常驻可以是设计要求；`init.svc.gsid` 的空值仍需更多信息才能判断为什么没有状态。
- [AOSP Android 10/11 Ramdisk 布局](https://source.android.com/docs/core/architecture/partitions/ramdisk-partitions) 说明 first-stage ramdisk 可能在切换 root 后释放，且 [AOSP 公钥构建目标](https://android.googlesource.com/platform/system/core.git/+/979f3d0116ee62b1461c94899ad7d82d2c00cd3e/rootdir/avb/Android.mk) 明确将 q-gsi 文件放入 ramdisk 或 first_stage_ramdisk。因此，常规 Android shell `ls /avb` 找不到与启动时 fstab 中的路径**完全不矛盾**。
- [Android 官方 DSU 文档](https://developer.android.com/topic/dsu) 明确把 DSU 功能可用性归于设备厂商集成。**`gsi_tool` 存在和 fstab 模板支持均非完整 DSU 运行能力证明**；`com.android.dynsystem` 的无路径结果是一个对标准 UI 集成不利的证据，但未证明不存在 OEM 替代入口。
- [AOSP gsi_tool.cpp](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-11.0.0_r13/gsi_tool.cpp) 有按需启动 `gsid` 的调用，故此阶段继续避免执行 `gsi_tool status`，其语义不是绝对零状态变更。

### 新证据下的优先级与可选第二轮微型只读审计

该判断已被同日随后采集的新结果修正：**开发者选项确实有 DSU Loader 入口**，且系统安装器包记录可见。请阅读下一节的较新实测，不能继续称“标准前端缺失”。

可在机主愿意时执行如下几条完全只读命令进一步核对是否仅保留底层框架：

```powershell
adb shell pm list packages -u | findstr /I "dynsystem gsi"
adb shell ls -l /system/etc/init/gsid.rc
adb shell ls -ld /metadata/gsi /metadata/gsi/dsu
adb shell getprop | findstr /I "gsid dsu gsi"
```

其中 `/metadata/gsi` 可能因 Android SELinux 正常限制而显示 Permission denied；文件为空/不存在或用户无权限均应原样保留。可另外在开发者选项中**仅观察**是否出现“DSU Loader”，不点击安装、不下载、不重启。无 UI 和无服务证据后应暂缓，不为了实验强行修改系统属性或安装随机的 DynamicSystem APK。

## 2026-10-18 第二轮实机只读结果：DSU Loader 入口存在 + 历史卸载关联

机主明确观察到开发者选项中有 **DSU Loader** 入口，此外在 Windows PowerShell 中执行：

```text
adb shell pm list packages -u | findstr /I "dynsystem gsi"
package:com.android.dynsystem

adb shell ls -l /system/etc/init/gsid.rc
-rw-r--r-- 1 root root 590 2009-01-01 08:00 /system/etc/init/gsid.rc

adb shell ls -ld /metadata/gsi /metadata/gsi/dsu
ls: /metadata/gsi: Permission denied
ls: /metadata/gsi/dsu: Permission denied

adb shell getprop | findstr /I "gsid dsu gsi"
# no matching lines
```

**提高置信度的事实**：开发者选项 UI 入口已被实机确认；Android 11 风格 `gsid.rc` 文件也确实存在。此前的 `gsi_tool` 存在、动态分区、F2FS `/data`、fstab GSI 额外钥匙配置相互支持。`/metadata/gsi` 权限拒绝与 [AOSP Android 11 gsid.rc](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-11.0.0_r13/gsid.rc) 对应：它在 `post-fs` 创建 `/metadata/gsi` 为 root/system 组的 `0771` 目录，不允许普通 `shell` 随意列举。这不意味着目录存在或不存在的状态已被证实。没有读取用户隐私数据。

**关键 PackageManager 语义**：Android 官方 [ADB 文档](https://developer.android.com/tools/adb) 把 `pm list packages -u` 定义为 **also include uninstalled packages**；因此 `com.android.dynsystem` 出现在 `-u` 列表不等于它当前对用户 0 已安装。此前 `pm path com.android.dynsystem` 没有输出，需进一步检查具体用户安装状态，不能将两种结果强行合并为“已安装”。

**新关联：仓库历史 user 0 应用精简**。[旧版精简实验](apps-and-debloat.md) 明确记录机主曾进行 `pm uninstall --user 0` 清理；[彻底精简脚本](../../archive/scripts/hand5g_debloat_p780.ps1) 以及 [日常电话精简脚本](../../archive/scripts/hand5g_debloat_daily_phone.ps1) 都把 `com.android.dynsystem` 加入待卸载包清单。另一方面，历史 phase3 [已安装列表](../../evidence/restricted/adb/phase3/hand5g_packages_installed_phase3.txt) 记录过 `com.android.dynsystem`。脚本中出现只是**计划目标**，历史快照也不是当前状态，尚没有充分记录证明这两个脚本在此包上的卸载命令被成功执行。当前新的、可验证的假说是：**安装器可能在某次精简中被对 user 0 移除，但 Settings 的 DSU Loader 菜单仍保留。**

## 下一轮仅查询 user 0 安装状态（暂不还原或启动安装）

```powershell
adb shell am get-current-user
adb shell pm list packages --user 0 com.android.dynsystem
adb shell pm list packages -d --user 0 com.android.dynsystem
adb shell pm list packages -f -u --user 0 com.android.dynsystem
adb shell dumpsys package com.android.dynsystem | Select-String -Pattern 'codePath=|User 0:|installed=|enabled='
```

- `pm list packages --user 0` 若有包，则证明对 user 0 当前已安装；仅 `-u` 有包而普通查询无包，支持系统包被对 user 0 卸载/未安装；`-d` 可核验是否停用。若缺少全部描述，则需讨论权限/包管理器实现差异。`dumpsys` 中 `User 0: ... installed=false` 是最有区分力的只读字段。
- **不执行** `pm install-existing --user 0 com.android.dynsystem`，除非机主在看到查询证据后明确同意恢复系统包；此命令会更改 user 0 应用安装状态，不是“只读检查”。
- 若确认包已安装/可用，则下一步可只打开开发者选项中的 DSU Loader **查看可选镜像列表**；按照官方 [Android 11 DSU 说明](https://developer.android.com/topic/dsu) 选择镜像并同意条款后才会触发下载安装。研究阶段不得选择镜像/确认条款/开始下载/重启。
- DSU 即便有官方可信 GSI 运行入口也**不等于**原厂 Bootloader 已解锁或能永久写入 `boot`/`vbmeta`；可运行性和 HAL 适配必须单独测试，不能由包记录直接推定。

## 2026-10-18 第三轮实机结论：DSU Installer 对 user 0 确认已卸载，但 Settings 选择列表可正常显示

机主提供带截图的当前 P780 开发者选项实测，以及完整 ADB PackageManager 输出。**此轮不再只是推测：`installed=false` 是当前 user 0 的实测状态。** 机主同时明确说明目前手机进行了最深度精简；历史两份脚本均把 `com.android.dynsystem` 列入 user0 的卸载目标。仍应区分历史脚本出现与实际单条执行日志没有归档：能证实当前卸载状态，不能追溯究竟是哪次命令造成。

### 用户终端关键原始结果

```text
$ adb shell am get-current-user
0
$ adb shell pm list packages --user 0 com.android.dynsystem
# no package returned
$ adb shell pm list packages -d --user 0 com.android.dynsystem
# no package returned
$ adb shell pm list packages -f -u --user 0 com.android.dynsystem
package:/system/priv-app/DynamicSystemInstallationService/DynamicSystemInstallationService.apk=com.android.dynsystem
$ adb shell dumpsys package com.android.dynsystem ...
codePath=/system/priv-app/DynamicSystemInstallationService
User 0: ceDataInode=0 installed=false hidden=false suspended=false distractionFlags=0 stopped=true notLaunched=true enabled=0 instant=false virtual=false
```

**精确解释：** 现行用户是 0；`pm list` 无 `-u` 不含这个包，但带 `-u` 能定位系统原厂 APK，包管理器直接报告 `User 0 ... installed=false`。这是 **user 0 已卸载、APK 仍在只读系统分区**，非 APK 文件被物理删除。注意 `enabled=0` 是 [Android PackageManager 常量 `COMPONENT_ENABLED_STATE_DEFAULT=0`](https://developer.android.com/reference/android/content/pm/PackageManager#COMPONENT_ENABLED_STATE_DEFAULT)，**不是禁用状态**；不要误执行 `pm enable` 作为当前问题的第一步。

### 开发者选项截图（会话图片未上传 Git）

进入 DSU Loader 后出现 `Select DSU Package` 弹窗，可见四项：

- `GSI ARM64`: `arm64-exp-BP1A.250405.005.C1-13151952-61d23231`
- `GSI+GMS ARM64`: `gms_arm64-exp-BP1A.250405.005.C1-13151952-48d6db2a`
- `GSI ARM64`: `arm64-exp-CPI1.251209.009.A1-14840729-59a822d9`
- `GSI+GMS ARM64`: `gms_arm64-exp-CPI1.251209.009.A1-14840729-89298580`

其中 `BP1A.250405.005.C1` 与 [Google 官方 Android 15 QPR2 GSI 清单](https://developer.android.com/topic/generic-system-image/releases) 的前缀/短哈希吻合（用于截图 UI 的列表识别；无整包本地下载哈希）。`CPI1.251209.009.A1` 当前只由截图可见，没有在本轮官方 release index 中核实其确切 Android 版本，不能自行认定所有列表项目均兼容 Android 11 vendor。

Android 官方 [DSU Loader 一键功能说明](https://source.android.com/docs/core/ota/dynamic-system-updates) 明确：**Settings 中的 Loader 从在线 JSON descriptor 下载目录、筛选 CPU ABI 等字段后显示浮层菜单；用户选择镜像后才进入安装/下载工作流**。因此 Settings 选择界面**可以在 `com.android.dynsystem` user 0 未安装时仍正常出现**。它证明当前 Settings/UI 能读到镜像目录，但未证明发起实际安装的服务可被当前用户启动、GSID/GSI 签名验证会通过或系统最终能启动。

### 阶段判定（取代先前 P1/P2 的摇摆）

| 问题 | 判定 |
|---|---|
| DSU Loader 系统 UI 和在线镜像列表 | **实机已确认**；四项 ARM64 选项显示 |
| `com.android.dynsystem` 原厂 APK 的物理文件 | **实机已确认存在** `/system/priv-app/...apk` |
| `com.android.dynsystem` 对用户 0 安装状态 | **实机已确认** `installed=false`（已卸载/未安装） |
| `enabled=0` | **默认组件开关状态**，不是 `disabled` |
| 由 Settings 成功选择并启动实际安装流程 | **没有执行，不得声称成功/失败** |
| Android 15/更新 GSI 与 P780 Android 11 Vendor HAL、Fstab AVB/GSI key 相容 | **未验证**；单靠 UI 目录不够 |
| DSU 获得永久 Root、解锁 BL 或写入原有 boot/vbmeta | **不存在相关实证** |

### 有明确用户授权时的下一步

现在不需要重装系统、第三方 APK、ADB root 或修改只读系统分区。系统原 APK 存在，Android 常规恢复命令为：

```powershell
# 仅在机主明确同意恢复此系统软件包时执行：会更改 user0 的安装状态
adb shell cmd package install-existing --user 0 com.android.dynsystem
# 完成后再次只读核验
adb shell pm path com.android.dynsystem
adb shell dumpsys package com.android.dynsystem | Select-String -Pattern 'codePath=|User 0:|installed=|enabled='
```

预期返回 `Package com.android.dynsystem installed for user: 0` 并将 `installed=false` 改为 `true`；**预期不等于本机实际结果**，当前尚未执行。保留原始终端以检验命令支持和 APK 签名/运行限制；无必要先执行 `pm enable`（`enabled=0` 仅默认）。

**风险边界**：该命令修改 Android 用户级应用安装记录，虽然不刷写系统分区、不改变 Bootloader、无需 Root，但可能恢复通知/服务等应用行为。即使恢复成功，也**暂不选择镜像和同意下载**，因为 Google 官方文档提及 DSU 至少预留约 10 GiB 空间、供应商 HAL/AVB 签名与 VNDK 兼容仍不明。优先先检查 `ro.vndk.version`、`ro.product.cpu.abi` 等只读条件，之后再讨论是否对旧 Android 11 vendor 尝试与之匹配的合适 GSI。不要将这视为 Root 研究的永久启动镜像写入通道。

## 2026-10-18 解释机主困惑：四个 GSI 选项从何而来？需要恢复出厂吗？

机主进一步说明：从未主动安装或配置过任何 GSI，但 Settings DSU Loader 弹出四个 ARM64 候选项；为取得“纯净原厂系统”，愿意在必要时恢复出厂。这是用户表述，不是已经执行重置。

**已由 AOSP 官方文档及源码确定的通用机制：**

- Android 11 DSU Loader 是 Settings 自带前端；当用户点击入口时，它通过 HTTPS 取得远端 **DSU JSON descriptor**，再按 ABI、Android OS 版本、VNDK 版本、SPL 等条件过滤候选，显示列表。此时只是**显示镜像元数据**，不是镜像已经在手机中或被安装过。[AOSP 官方 DSU One-click Loader](https://source.android.com/docs/core/ota/dynamic-system-updates#one-click-dsu-loader)、[Settings DSULoader.java](https://android.googlesource.com/platform/packages/apps/Settings/+/286dce6b6ed/src/com/android/settings/development/DSULoader.java)。
- 在所审 AOSP `DSULoader.java` 中，默认 `DSU_LIST=https://dl.google.com/developers/android/gsi/gsi-src.json`，但如果存在 `persist.sys.fflag.override.settings_dynamic_system.list` 会替换默认 URL，描述符还可以通过 `include` 包含下游列表。所以 **高度可能是标准 Google 官方 GSI 列表，尚未证明此 P780 当前究竟使用哪个 URL**。先前机主检查的 `persist.sys.fflag.override.settings_dynamic_system`（没有 `.list`）只是功能覆盖键，**不是**目录地址覆盖键。下一只读检测应带上精确的 `.list`。
- 弹出的四项呈两组构建，每组 `GSI ARM64` 不含 GMS，`GSI+GMS ARM64` 带 Google Mobile Services。这些是供选择的远端镜像**目录条目**，不是设备本机储存的四份映像。AOSP Settings 会按 CPU/OS/VNDK/SPL 做**元数据级初筛**，不替代真正的 AVB 公钥验签、HAL 兼容、启动测试。
- [Android 官方 DSU 文档](https://developer.android.com/topic/dsu) 说明选项出现后还要用户选择、同意条款，此后才会下载并通过 `DynamicSystemInstallationService` 等组件安装。`com.android.dynsystem` 对 user 0 `installed=false`，与 Settings 前端能显示候选是两个层次，不构成矛盾。

**恢复出厂是过度措施**：当前实机已证明只发生系统预装应用的 `pm uninstall --user 0` 用户级移除，原厂 `DynamicSystemInstallationService.apk` 还在只读 `/system/priv-app`。官方 PackageManager `cmd package install-existing --user 0 com.android.dynsystem` 可在得到机主明确同意后，只恢复这个预装包的 user 0 安装登记；无需恢复出厂、不需 Root、不会覆盖原厂镜像。恢复出厂可能清除用户数据、之前安装的 KeyAttestation、USB debugging 授权和部分研究状态/证据，但不会神奇地导出 vbmeta 或 Bootloader 解锁。若未来因深度精简影响设备其它系统依赖，再规划 **先备份/留存当前对照、之后原厂重置**，不作为本轮前提。

**建议仅做两项无状态取证：**

```powershell
adb shell getprop persist.sys.fflag.override.settings_dynamic_system.list
adb shell getprop ro.vndk.version
```

第一个若为空且 Settings 无其它 OEM 自定义，AOSP 默认目录最有可能是上述 Google `gsi-src.json`；第二个供理解 DSU JSON VNDK 过滤。也可查询 `ro.product.cpu.abi` 与 `ro.system.build.version.release`（已有 ARM64/Android 11 基线，不强制重复）。如无安装计划，则连恢复系统包也不是必须。


## 2026-10-18 第四轮：机主实际成功恢复原厂 DSU 安装服务（直接验证）

本节是**现行最新状态**，覆盖上方历史阶段的 `installed=false`；先前结论在其采集时有效，不应再作为手机当前状态。

机主在 PowerShell 中执行并提供原样成功回显：

```text
PS> adb shell cmd package install-existing --user 0 com.android.dynsystem
Package com.android.dynsystem installed for user: 0
PS> adb shell pm path com.android.dynsystem
package:/system/priv-app/DynamicSystemInstallationService/DynamicSystemInstallationService.apk
PS> adb shell dumpsys package com.android.dynsystem | Select-String -Pattern 'User 0:|installed=|enabled='
    User 0: ceDataInode=19397 installed=true hidden=false suspended=false distractionFlags=0 stopped=false notLaunched=false enabled=0 instant=false virtual=false
    User 0:
    User 0:
    User 0:
```

**强证据：** 软件包在用户 0 的安装状态已经从上轮 `false` 变成 `true`；之前无法返回的 `pm path` 此时返回位于预装系统分区的正式 APK。不存在重新下载 APK、替换 `/system` 文件、解除 Bootloader 锁或恢复出厂操作。之前 Settings 已显示在线 GSI 目录，当前又确认安装器已恢复，消除了**用户级卸载**这个直接障碍。

**边界：** `stopped=false`、`notLaunched=false` 是 PackageManager 标志，不证明 GSI 已被安装或启动，也不能由此认定 `gsid` 已成功执行镜像写入。`enabled=0` 是默认值，非禁用。用户仍在原厂 Android 11 `_162`、Bootloader LOCKED、无 Root。没有取得新的 VBMeta 镜像或物理分区写入通道。

### 继续前仅需最小只读兼容性检查

```powershell
adb shell getprop persist.sys.fflag.override.settings_dynamic_system.list
adb shell getprop ro.vndk.version
adb shell getprop ro.product.cpu.abi
adb shell df -h /data
```

- 首条确认是否有 DSU 在线 JSON 列表 URL 的系统属性覆盖；即使为空也只是提示更可能使用 AOSP 默认 Google 目录，不是网络抓包证明。
- `ro.vndk.version` 与 ABI 用于初步比对 GSI 的架构/VNDK 要求；`df -h /data` 只读查询剩余空间。不需要为此重复 Key Attestation、修改属性、访问受限 `/metadata/gsi` 或再次恢复系统包。
- 官方 [Android DSU](https://developer.android.com/topic/dsu) / [AOSP DSU 设计及内核/分区条件](https://source.android.com/docs/core/ota/dynamic-system-updates)：需要受信任签名、动态分区、dm-verity、vendor HAL 兼容与储存空间；AOSP 建议至少预留约 10GB。即使四个在线 GSI 目录条目可见，旧 Android 11 的厂商组件是否能与 Android 15+ GSI 启动相容还没有实证。
- 当前**不执行**选择镜像、同意安装条款、下载、启用 sticky 模式或重启。若用户明确希望进行 DSU 实机安装测试，需要另做针对该镜像的适配、可靠退出方式、备份与具体风险评估。不能把 DSU 临时系统误当成永久 Root 或 locked fastboot 分区写权限。

## 2026-10-18 第五轮：P780 DSU 只读基础兼容性和空间检查已完成

机主已实际执行第四轮安排的四条无状态查询；下面是**本机原样输出**，不是把 AOSP 通用性质误当作实机结论：

```text
$ adb shell getprop persist.sys.fflag.override.settings_dynamic_system.list
# empty
$ adb shell getprop ro.vndk.version
30
$ adb shell getprop ro.product.cpu.abi
arm64-v8a
$ adb shell df -h /data
Filesystem       Size  Used Avail Use% Mounted on
/dev/block/dm-11 106G  3.2G  103G   4% /storage/emulated/0/Android/obb
```

### 解读与证据等级

- **确定：** `ro.vndk.version=30`，对应 Android 11 的 vendor ABI 接口版本。Android 11 P780 的 `ro.product.cpu.abi=arm64-v8a`，与截图中 ARM64 GSI 条目架构匹配。**尚未证明 Project Treble 的完整隔离实现或 GSI 实际启动成功**。
- **确定：** `df -h /data` 显示设备映射 `/dev/block/dm-11`，容量 `106G`，已用 `3.2G`、报告可用 `103G`（约 4%）；显示的 Mount on 却是 `/storage/emulated/0/Android/obb`，可能由 Android 挂载命名空间 / bind mount 导致，**不得强行解释为独立实体挂载路径，更不得直接认为已分配 DSU 空间**。按报告值，空间明显超过 AOSP 的至少约 `10GB` 基础建议，但 quota、F2FS 特殊限制、实际 DSU 分配尚未测试。
- **确定：** `persist.sys.fflag.override.settings_dynamic_system.list` 返回空；表示本机没有暴露这个属性指定的替换地址，和 [Android AOSP DSU 默认 Google GSI JSON](https://source.android.com/docs/core/ota/dynamic-system-updates#customize-the-one-click-dsu) 设计相容，但未抓取本机实际 HTTPS 流量/编译资源/运营商覆盖，因此不应声称已独立证明其实际 URL。
- **AOSP 有条件的筛选解释：** 官方 Android 11 [DSULoader.java `isSupported()`](https://android.googlesource.com/platform/packages/apps/Settings/+/286dce6b6ed/src/com/android/settings/development/DSULoader.java) 通过必选 `cpu_abi`，以及 JSON **若出现才检查** `os_version`、`vndk` 列表（必须包含设备版本 30）、`spl` 等条目。机主截图四个候选在 UI 中出现，若厂商使用基本相同的 AOSP 筛选实现则说明这些候选已通过 *实际具备的字段* 的客户端检查；但它也可能因 JSON 缺少可选的 VNDK/SPL 字段而跳过相应检查。**没有拿到实际候选 JSON 原件，不能认定四个包都明确包含 VNDK 30，也不能由此证明旧 Vendor 与新 system 完全兼容。**
- **官方跨版本边界：** [Android Developers GSI 兼容检查](https://developer.android.com/topic/generic-system-image#check-device-compliance) 对常规 GSI 强调 `ro.treble.enabled=true` 和动态链接器配置中 `[vendor]` 的 `namespace.default.isolated=true`；后者是判断能否跨 Android OS 版本使用 GSI 的重要前提。原官方 GSI 手工刷机流程要求 Bootloader 解锁，与 DSU 的锁定态受信任临时安装**不是同一通道**；不能把两套前置要求机械等同。

### 第六轮建议：仅只读确认 Treble 与 Vendor linker 隔离

```powershell
adb shell getprop ro.treble.enabled
adb shell ls -l /system/etc/ld.config* /linkerconfig/ld.config.txt
adb shell "grep -n -A 20 '^\[vendor\]' /linkerconfig/ld.config.txt"
```

若 linkerconfig 文件/路径不存在或 shell 无法读取，应按具体 Android 11 文件布局重定向检查，不必引入 Root 或执行 `gsi_tool status`/安装。`[vendor]` 命名和 `namespace.default.isolated` 也可能因版本而不同，不能用命令零输出武断推断“不支持 Treble”。

**阶段结果：** 安装器已恢复、目录 UI 正常、ARM64/VNDK 30 明确、可用存储报告充裕，满足继续离线和只读兼容性分析的条件。仍未取得匹配 JSON、DSU trustkey 实际当前加载情况、HAL/Gatekeeper/Weaver 兼容证据、GSI 安装签名验收和启动日志。因此仍不选择镜像、不下载安装、不重启或尝试 locked 写入原厂分区。


## 2026-10-18 第六轮实机：Treble 和 Vendor 链接器隔离已直接证实

机主提供 Treble Check 应用截图和同轮 Windows PowerShell ADB 输出（仅私人会话、未提交原始截图至 Git）。截图可见 Project Treble **支持**（VNDK 30.0）、无缝系统更新 **支持**（有 A/B 分区）、64-bit ARM、System-as-root **支持**。此处主要以以下原始 ADB 结果作为可复核证据；第三方应用 UI 只作旁证，不代替系统输出：

```text
$ adb shell getprop ro.treble.enabled
true
$ adb shell ls -l /system/etc/ld.config* /linkerconfig/ld.config.txt
ls: /system/etc/ld.config*: No such file or directory
-rw-r--r-- 1 root root 90115 1971-04-25 17:45 /linkerconfig/ld.config.txt
$ adb shell "grep -n -A 20 '^\[vendor\]' /linkerconfig/ld.config.txt"
368:[vendor]
369-additional.namespaces = com_android_adbd,com_android_art,com_android_neuralnetworks,com_android_runtime,system,vndk
370-namespace.default.isolated = true
371-namespace.default.visible = true
372-namespace.default.search.paths = /odm/${LIB}
373-namespace.default.search.paths += /vendor/${LIB}
374-namespace.default.search.paths += /vendor/${LIB}/hw
375-namespace.default.search.paths += /vendor/${LIB}/egl
376-namespace.default.permitted.paths = /odm
377-namespace.default.permitted.paths += /vendor
378-namespace.default.permitted.paths += /system/vendor
```

### AOSP 合规性交叉确认

- **直接实机已证实：** `ro.treble.enabled=true`，实际 `/linkerconfig/ld.config.txt` 中 `[vendor] namespace.default.isolated=true`。前一轮已确认 `ro.vndk.version=30`、`ro.product.cpu.abi=arm64-v8a`。这正是 [Android 官方 GSI 设备兼容性检查](https://developer.android.com/topic/generic-system-image#check-device-compliance) 列出的 Treble、跨 Android 版本 VNDK 隔离、ABI 检查。`/system/etc/ld.config*` 不存在与 Android 11 生成的 linkerconfig 路径不同有关，**真实 `/linkerconfig/ld.config.txt` 已直接读取成功，不算失败**。
- **AOSP 官方含义：** 若 Vendor `namespace.default.isolated=true`，官方将该设备描述为可支持**高于原厂 Android 版本**的 GSI 操作系统。它是重要的框架/供应商链接器兼容前提，**不是**所有 Android 15/16 具体 GSI 的安装签名、HAL、设备驱动、Keymaster/Gatekeeper/Weaver 或安全补丁回滚检查已经通过的实机证明。
- **重要版本提醒：** [AOSP VNDK 现状](https://source.android.com/docs/core/architecture/vndk) 指明自 Android 15 开始弃用 VNDK，但**旧 VNDK 版本 14 及以前的 APEX 继续保留**以服务既有 Vendor；因此“Android 15 GSI 一定不含 Android 11 VNDK30”以及“Android 15 一定能兼容”均属于未证实的过度推断。具体镜像仍需检查 JSON 条目与包内 APEX、AVB GSI 签名。
- **DSU 与常规手工刷写必须分开：** 官方 GSI [手工 flashing](https://developer.android.com/topic/generic-system-image) 的 `unlocked` 要求不等于 [官方 DSU](https://source.android.com/docs/core/ota/dynamic-system-updates) 经厂商内置受信任开发 GSI keys 允许的 LOCKED 临时安装路线。此前实机 Fstab 确含 q/r/s GSI keys 配置，但未直接取得当前 boot ramdisk 中公钥或确认它们信任截图中 2025/2026 新版本 GSI。
- **截图证据边界：** Treble Check 报告无缝更新/A-B 和 System-as-root，与既有 by-name A/B 和 fstab 相容，但不能仅凭第三方应用证明 DSU 已完成实际启动或某个 GSI 的签名/硬件适配。

### 第七轮方向：从“抽象兼容性”转为“具体镜像元数据”，不再重复 ADB

目前原生 DSU 安装服务已恢复，Treble/VNDK/ARM64/存储均已有**本机可复核**数据。下一关应该拿到截图中 GSI 候选条目的真实 DSU JSON 元数据，对照 `cpu_abi`, `os_version`, `vndk`, `spl`, `pubkey`, `uri` 和是否存在嵌套 `include`。优先在**Windows PC 上**只读下载官方公共 JSON，不在设备上选镜像/下载巨大的 ZIP；解析公网 JSON 时应保留来源、时间以及服务端格式变化，不执行 JSON 中引用的任意脚本或未知 URL。

- AOSP 默认地址为 `https://dl.google.com/developers/android/gsi/gsi-src.json`，P780 的 `.list` 属性为空；仍不能因此断言已捕获实际设备请求。该 Google URL 当前在研究环境的网页检索接口里不能直接读取 JSON，**尚未取得当前目录原始 JSON 或截图所列两组构建的完整字段**。
- 下载/解析只读元数据的意义：确认是否明确包含 VNDK30、所列 GSI 的发行系统版本、签名公钥指纹/黑名单和真正分发 URL。**它仍不证明动态启动可以成功**，但能在不修改 P780 的情况下有效减少选择风险。

## 最新阶段判定

**Treble 支持、Vendor linker namespace isolation、VNDK30 和 ARM64 已实机确认；DSU 原厂安装器已恢复；GSI 下载、安装、签名和启动仍未执行**。本次研究没有修改 boot/vbmeta 分区、没有 Root 或 BL 解锁、没有完成锁定态永久写入。


## 2026-10-18 第七轮：机主取得 Google DSU 主索引，508 B 字节级核验

机主在 Windows PowerShell 运行 `Invoke-WebRequest -UseBasicParsing -Uri https://dl.google.com/developers/android/gsi/gsi-src.json -OutFile .\p780-dsu-catalog.json`；返回主文件长度 **508 bytes**，`Get-FileHash -Algorithm SHA256` 为 **`0A1970ABFCEB6BF3962177881B255E6AF9D4F43903AAC3BA9AEF2C1E5B4A2D09`**。其后机主在本轮聊天上传该 JSON，助手在只读工作环境重新解析原始 508 字节并独立计算 SHA-256，**字节长度与 SHA-256 完全一致**。当前文件是机主 PC 自行获取的公开 Google 索引，不是 P780 本机 HTTPS 抓包；不代表设备实际使用的 URL 已被捕获。

### 主索引实际内容：只有 `include`，不含镜像声明

```json
{
  "include": [
    "https://dl.google.com/developers/android/rvc/images/gsi/gsi-dsc.json",
    "https://dl.google.com/developers/android/sc/images/gsi/gsi-dsc.json",
    "https://dl.google.com/developers/android/tm/images/gsi/gsi-dsc.json",
    "https://dl.google.com/developers/android/udc/images/gsi/gsi-dsc.json",
    "https://dl.google.com/developers/android/vic/images/gsi/gsi-dsc.json",
    "https://dl.google.com/developers/android/baklava/images/gsi/gsi-dsc.json"
  ]
}
```

- `rvc`=Android 11、`sc`=Android 12、`tm`=Android 13、`udc`=Android 14、`vic`=Android 15、`baklava`=Android 16；这只是索引分支身份，不表示这 6 份镜像已经安装。最相关的是用户手机 DSU 界面截图里的 `BP1A.250405.005.C1`（`vic`）及 `CPI1.251209.009.A1`（待核 `baklava` 子目录的实际记录）。
- 因为主文件**没有** `images`，它自己无法回答具体 GSI 的 `cpu_abi`、`vndk`、`pubkey`、`spl`、`uri` 或 `os_version`。在子目录正式下载核验前**不能**宣称 `vndk` 显式包含 30，不能声称签名是否匹配 P780 GSI 信任公钥；也不能把目录中的 ZIP URL 当作已经下载的镜像。
- [AOSP 官方 DSU JSON descriptor](https://source.android.com/docs/core/ota/dynamic-system-updates) 公开解释 `include` 递归、`images` 结构及 **可选** `vndk`、`pubkey` 字段；若某项没有 `vndk`，仅说明目录没有指定该字段，不等于镜像已确认兼容 VNDK30。
- 本轮研究环境网络检索接口无法直接读取 `dl.google.com/developers/android/*/images/gsi/gsi-dsc.json` 的原始 JSON（返回资源不可访问），并且隔离的运行环境无可用网络解析，**所以六个子 JSON 尚未取得、未冒用网上缓存/他人日志作为当前官方原件**。机主当前 Windows 已证明可访问主目录，下一步在 Windows PC 仅读取上述6个已声明的 Google HTTPS JSON；每个只限制1MiB，只保存原始字节/Hash/字段，**不得跟随 `uri` 下载数GB GSI ZIP**。

### 下一轮可复核的数据采集工具

本轮助手生成并离线模拟测试了标准库 Python 脚本 `p780_dsu_catalog_audit.py`（用户可从当前聊天下载；**当前还未在机主 Windows 上运行**）：从同一目录读取 `p780-dsu-catalog.json`、仅允许 Google 域名 `/developers/android/*.json` 小文件、最多20条包含链/3层/单项1MiB、拒绝外站重定向；将各子 JSON 原始字节、SHA-256 及匹配 `BP1A.250405.005.C1` / `CPI1.251209.009.A1` 的字段放入 `p780-dsu-catalog-detail.zip`。它不请求/下载 ZIP，不运行 ADB，不修改设备。获得并核对实际返回后再考虑将脚本归档入 `tools/`；未经真实网络测试的脚本不可声称在线已验证。

### 结论

**已核验 Google 主索引内容与哈希；6个子索引 URL 和目录结构已确认；两个目标 GSI 的实际签名及 VNDK 字段仍未知。** 保持 P780 Bootloader LOCKED、无 Root、无 GSI 安装/重启。下一步等待 Windows 只读获取子 JSON 原件，或由机主传回工具生成的含原文与 SHA 的小型 ZIP。


## 第八轮摘要（新结论覆盖第七轮“尚未取得子 JSON”）

[第八轮官方目录独立核验](p780-dsu-gsi-catalog-verified-20261018.md) 已核对根索引 508B 及子索引 six-way bundle `p780-dsu-catalog-detail.zip`（4073B，SHA256 `ad732d61aa7751aeaa6f2a148e3a1998aeee645beb5fe3f344fff98d9ca74c74`），六个子目录全部加载，无网络请求错误，24个镜像记录；仅 Android15 与16 ARM64 目录中的4个符合 P780 补丁时间和 ABI 初筛。六份 Google 子 JSON 中**每份4条**，均**没有 `vndk` 或 `pubkey` 字段**；旧 R/S/T/U 安全补丁比设备 2024-02 旧，因此无菜单选项。原审计工具误把 Android16 `CP11` 输入为 `CPI1`，所以 `report.matches` 自动报告漏掉 Android16，本轮已从原始 JSON 与历史截图独立纠正。当前不会因为缺少 JSON 公钥而断言镜像无签名或启动链已接受。后续优先核对 GSI 官方签名信任链以及 Android11 P780 boot ramdisk 中实际 GSI 公钥兼容性；**没有下载镜像或更改分区**。

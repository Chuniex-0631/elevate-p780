# P780 已定位研究文件总清单

## 2026-10-18 第十三轮：完整 Bugreport 成功读取，但 LAST KMSG / 持久化内核日志不可用

- 机主上传 `P780-DSU-Bugreport.zip`；Python zipfile 全部 CRC通过，ZIP成员 **362**；原档 SHA256 `64a097d0911e35675c75dff09d68a7e28b5aa15bd342ed796387d12758d5f141`。主TXT **19,721,044B** / 约240,297行，SHA256 `8767fb7c186050240f3203fd65a82ab73b95dbbeeec338654ba439580f984836`。**原 ZIP 与TXT不上传Git，因包含设备/网络/用户隐私**。
- 系统属性 `persist.sys.boot.reason.history` 明确有两条 `reboot,dynsystem` 对应UTC+08的 **2026-10-18 06:30:31、06:31:30**；`gsid.image_installed=1`、`ro.gsid.image_running=0`、`init.svc.gsid=stopped`、`ro.boot.slot_suffix=_b`。`gsid dump-device-mapper` 只反映报告采集时原厂 `system_b/vendor_b/product_b` 及dm-verity映射，不能判断早期 DSU 映射曾经失败。
- `LAST KMSG` 明确失败：`Error dumping /proc/last_kmsg: No such file or directory`；incidentd 无法打开 `/sys/fs/pstore/console-ramoops`、`console-ramoops-0`、`/proc/last_kmsg`；`LAST LOGCAT` (`logcat -L`)退出码1。当前启动的 `dmesg` 有约2635行，但最早为开机后 **943秒**，未保留 first-stage DSU 时间窗口，故无法确认DSU切换具体失败原因。
- [第十三轮去身份分析报告](research/p780-dsu-bugreport-audit-20261018.md) 详细记录精确来源位置、证据级别与后续离线研究路线。当前 **没有 AVB签名拒绝/MapAllImages失败的直接证据，没有GSI成功启动或Root/解锁**。原件仅留在机主本地及当前对话，不把原始系统隐私数据作为普通commit附件。

## 2026-10-18 第十二轮：仅一次重启与 `reboot,dynsystem` 两处启动原因证明

- 机主亲自观察：点击通知「重启进入DSU」后是**一次正常重启直接进入原厂 Android11**，没有 Android15 GSI 桌面，也没有自动重启第二次；不同于设备无限 bootloop。
- ADB `ro.boot.bootreason` 与 `sys.boot.reason` 均完整输出 `reboot,dynsystem`。在 AOSP Android11 `DynamicSystemInstallationService.executeRebootToDynSystemCommand()` 中调用 `PowerManager.reboot("dynsystem")`，故此输入强力支持真正 DSU 重启请求已传入系统（并非普通重启），**不能因此宣称 first-stage 实际挂载了 GSI**。
- `logcat -g`：main 2MiB(已用1MiB)、system 2MiB(已用388KiB)、crash 256KiB(已用374B)、**kernel 2MiB(已用0B)**。`adb shell logcat -b kernel -d ...` 加过滤词**无输出**；加上前次 `/sys/fs/pstore` Permission denied，说明本机当前 shell 无法从该路径获得上次 first-stage/内核原始故障日志，不能错误写成「内核没有报错」。
- [第十二轮专题](research/p780-dsu-stock-fallback-20261018.md) 联合前次 `gsi_tool installed/disabled`、one-shot 状态会提前消费和 AOSP `UseDsuIfPresent` 失败分支：**first-stage 提前返回原系统是有依据的优先假说，但没有直接日志证明是分区映射/AVB/其它环节之一**。此轮没有刷写/重启新尝试、没有Root。

## 2026-10-18 第十一轮：GSI installed/disabled、私有原始日志 SHA 和 one-shot 源码机制

- 用户终端直接实测：`gsi_tool status` 两行 `installed` / `disabled`；`ro.gsid.image_running` 空、当前槽 `_b`；`/sys/fs/pstore` Permission denied。Android 11 `gsi_tool.cpp::Status` 的 `installed/disabled` 分别来自GSID的已安装/当前启用查询，当前原厂系统启动未发现`running`。
- 两个本轮实上传日志已通过本地程序读文件并计算 SHA：完整 `p780-dsu-after-reboot.log` UTF-16LE/CRLF、15455行、SHA256 `955c9775371658b36d59e749c648149193a05746a72d26807f09a3f97de6e970`；`p780-dsu-filtered.txt` 678B、3条、SHA256 `333d7ac1de09d46f4a77a3611842a38d47c0ec14819d2b2b23d6ebfb2a74cf76`。原件保留用户PC和当前聊天，**不提交4.1MB未脱敏Logcat或Windows个人路径**。
- 真正相关日志：06:31:40.743 DSU应用进程启动；06:31:40.850 `DynSystemInstallationService: onStartCommand(): action=android.os.image.action.NOTIFY_IF_IN_USE`；06:31:40.852 `DynamicSystemService: isInstalled(): true`，随后创建含2个action的通知。文件时间范围06:31:40.616～06:36:36.673，仅有当前原厂用户空间记录，无可判定 first-stage 映射、AVB/受信密钥或后续init是否失败的原始日志。
- [AOSP Android11 libgsi.cpp](https://android.googlesource.com/platform/system/gsid/+/refs/tags/android-platform-11.0.0_r16/libgsi.cpp) 在 `CanBootIntoGsi` one-shot 路径下**先将后续启动状态写disabled但允许当前尝试继续**，所以重启后 `installed/disabled` 与“已经消费一次性DSU启动机会”相符，**不是必然等于点击前未启用，也不能由此证明具体失败原因为AVB**。详见 [DSU第十一轮证据与诊断](research/p780-dsu-stock-fallback-20261018.md)。

## 2026-10-18 第十轮：GSI 下载完成提示后两次重启仍回原厂系统

- 机主直接观察：下载GSI→完成、提示进入DSU→点击重启→返回原厂系统、通知继续提示进入DSU→再点击重启→仍然原厂。**并非设备自主无限 Bootloop，而是用户每次点击导致相同的启动回退。** 原厂可开机，Android15 GSI未观察到真正运行。
- 当前仅有用户文字实验报告；**还没有 GSID status、原始安装通知截图、early init/pstore/logcat、真实安装的 GSI build ID**。此时不能把故障定为 q/r/s AVB 公钥不匹配，也不能认定 DSU已完成所有安装和映像验签。
- 基于 AOSP Android11 first_stage_mount 的 `CanBootIntoGsi`、MapAllImages、MarkSystemAsGsi 等失败分支，可能有启动指示/one-shot、映射、AVB以及后续HAL init等不同因素。用户已被建议停止重复重启、不Discard、先抓 logcat（可能仅当前启动）及 `gsi_tool status`（可能按需启动守护进程）。**还没有新诊断结果，不做推定。**
- [实机失败记录和只读排查](research/p780-dsu-stock-fallback-20261018.md)。原始手机日志如涉及IMEI/账号，应先脱敏，完整日志不直接上传GitHub。

## 2026-10-18 DSU 首次实机实验：用户同意尝试，尚未执行

- 用户在对话中明确表示：“我觉得可以继续研究DSU，并且既然是DSU，我觉得可以进行一波尝试，毕竟DSU并不会破坏原系统”。现阶段视为**研究意愿和实验授权**，不是 DSU 已安装、已进入 GSI 或数据已备份的结果。
- 官方 [AOSP DSU](https://source.android.com/docs/core/ota/dynamic-system-updates) 设计将临时 GSI 置于动态逻辑分区，保存独立的 GSI userdata，确实旨在避免损坏原厂 system/boot；但仍在主机 `/data` 上分配资源，也有 Vendor HAL/AVB 启动边界。Google [Android15 GSI 发布说明](https://developer.android.com/topic/generic-system-image/releases) 明示部分重启失败可能要 Recovery factory reset，**不能写成无损保证**。
- [首次试验协议](research/p780-dsu-first-trial-protocol-20261018.md) 确定 Android15 `BP1A.250405.005.C1` ARM64 **无 GMS** 为相对保守候选，Google 官方 ZIP SHA256 `61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`，尚非机主下载后的实测 SHA。
- 计划按备份→Settings DSU Loader 官方下载/安装→**首次停在 Restart/Discard** 收集结果→独立同意后再考虑真正 GSI 启动，记录用户区修改、潜在数据损失和返回原系统风险。当前没有新手机日志、镜像 ZIP、Root 或 Bootloader 解锁。

## 2026-10-18 第九轮：公开 AOSP 六把 GSI 公钥 SHA-256 与可信链修正

- 新的 [DSU 公钥信任链源码审计](research/p780-dsu-trust-chain-audit-20261018.md) 对 AOSP Android11 `gsi_keys.mk`、`developer_gsi_keys.mk` 与 `rootdir/avb/Android.mk` 交叉核对：普通 q/r/s GSI 公钥与 q/r/s **Developer GSI** 公钥是两套不同文件；机主 P780 fstab 的 `avb_keys=` 仅引用普通 `q/r/s-gsi.avbpubkey`。
- 通过公共 Android11 GitHub 源码镜像读取全部6份原始 AVB RSA4096 公钥二进制（**1032 字节/份**），纯 JavaScript 实现 SHA256 在 `abc` 标准测试向量自检通过。普通 q-gsi/r-gsi/s-gsi 的 SHA256 分别是 `07b37325316fd483765d474aafcaca908b4de4773e16ed87aed415c15f71fb98`、`4706b8d2ffd46c5759d9431b8bf95f5c0544f4f6c87bbe35ff591325eb1783f5`、`ec60e13d92331e2c2d5d1372a5d7f2131861dc602815fd87c0637d14790b4538`；三份 Developer 公钥哈希也在专项逐一保存。**六份均不等于 P780 TEE AVB 根公钥摘要 `7728e30f...`，但本机 ramdisk 密钥实体未直接采集。**
- AOSP first-stage init 的 `CopyDsuAvbKeys` 和 DSU 设计说明确认：`/avb` 启动钥匙可复制到 `/metadata/gsi/dsu/avb` 用于安装辅助验收（普通 shell 受限），即便辅助复制失败也会在下一次 DSU 启动时做真实钥匙核对。Google DSU JSON 缺少 `pubkey` 不意味着 AVB 验签跳过。
- Google 官方 Android15/16 对应版本发布说明有四个目标ZIP的官方SHA，可用于未来离线校验；并有 GSI 重启失败需 Recovery/清除 userdata 的风险说明。没有下载ZIP，也没有设备新的ADB采集/刷写/重启/Root。源码和风险资料按链接保存于专项。

## 2026-10-18 DSU 第八轮：6个子目录与24项 GSI 数据核验完成

- 机主上传的 `p780-dsu-catalog-detail.zip` 为 **4073B**，SHA-256 `ad732d61aa7751aeaa6f2a148e3a1998aeee645beb5fe3f344fff98d9ca74c74`；本地使用 Python 对 ZIP 8 项路径/大小/CRC 均通过、6个子目录的 raw bytes / SHA-256 对照 report.json **6/6一致**；根索引508B仍与原先SHA一致。该ZIP保存在本轮私有会话与机主电脑，仓库存**可复核哈希和研究结论**，未宣称 P780 上实际执行过 HTTPS 抓包。
- `rvc/sc/tm/udc/vic/baklava` 每目录4条，合计 **24个公开镜像条目**；全部有 cpu_abi/os_version/spl/uri，**没有一条包含 vndk 或 pubkey 字段**。这意味着 Android11 Settings 的目录筛选没有实际验证某个镜像的 VNDK30 清单或 GSI AVB 信任公钥。
- 真机截图四项分别是 `vic` Android15 的 `BP1A.250405.005.C1` ARM64+GMS/non-GMS 两条，以及 `baklava` Android16 的 `CP11.251209.009.A1` ARM64+GMS/non-GMS 两条。**前版助手和脚本目标误写为 `CPI1`（字母I），实际 `CP11`（数字1+数字1）**；原报告 matches 漏两条Android16 ARM64，但**原始 baklava JSON 正常完整**。旧 Android11～14目录的安全补丁 2020～2023 早于P780 2024-02设备，按AOSP SPL检查会排除，恰好只显示上述4项。
- 校验和、完整镜像详情、源码依据、证据等级和下一步见 [DSU GSI JSON 独立核验](research/p780-dsu-gsi-catalog-verified-20261018.md)。**无 GSI 镜像 ZIP 下载、DSU 安装、BL 解锁或 Root 成果**。

## 2026-10-18 DSU 第七轮：Google 508B 主索引已完成字节级验证

- 机主 Windows PowerShell 通过 `Invoke-WebRequest` 从 `https://dl.google.com/developers/android/gsi/gsi-src.json` 取得 `p780-dsu-catalog.json`，`Get-Item` 为 **508 bytes**，`Get-FileHash -Algorithm SHA256` 为 `0A1970ABFCEB6BF3962177881B255E6AF9D4F43903AAC3BA9AEF2C1E5B4A2D09`；本聊天实际上传了 508B 文件，助手在运行环境重新读取、解析原始 bytes，并独立 SHA-256 完全一致。主文件**不是本机 P780 HTTP 抓包**。
- JSON 只有6条 Google `include`：`rvc/sc/tm/udc/vic/baklava` 下各自 `gsi-dsc.json`。主文件不含 `images`，因此无法由此确定截图里两组 GSI 的实际 `vndk`、`pubkey`、`os_version` 或下载 URI。原件当前在用户本机与本聊天附件，**Git 中仅记录 SHA 和公开 URL**，没有保存可能关联设备的日志。
- 当前工具环境无法直接从 Google 下载六份子目录 JSON，故用户可用当前聊天提供的标准库 Python 脚本在 Windows 上获取**仅公开小 JSON 元数据**；脚本仅通过离线模拟测试，尚未上机联机验证，输出预期为 `p780-dsu-catalog-detail.zip`，不请求实际 GSI ZIP，也不调用 ADB。待用户上传真实元数据后再进一步核验。专题：[DSU 第七轮](research/p780-dsu-locked-gsi-20261018.md)。

## 2026-10-18 DSU 第六轮：Treble 和 Vendor linker 隔离的直接实机证据

- 机主第三方 Treble Check **截图**显示 Project Treble 支持、VNDK 30、A/B 无缝更新、64-bit ARM、System-as-root。截图只在当前对话内查看，**未保存入 Git 或当作底层源码证据**。
- 同次原始 ADB：`getprop ro.treble.enabled`→`true`；`ls /system/etc/ld.config*`→文件不存在，`ls /linkerconfig/ld.config.txt`→文件存在、90115B（系统给出的时间戳 1971 并非固件构建日期）。
- **关键实证**：`grep -n -A 20 '^\[vendor\]' /linkerconfig/ld.config.txt` 从第368行找到 `[vendor]`，第369行列出额外 namespaces，第370行明确 `namespace.default.isolated = true`，后续 Search Paths 指向 `/odm/${LIB}`、`/vendor/${LIB}`、`/vendor/${LIB}/hw` 等。Vendor isolation 的断言来自本机系统动态生成的真实链接器配置，而非第三方检测软件推论。
- [官方 Google GSI 兼容性标准](https://developer.android.com/topic/generic-system-image#check-device-compliance) 的 `ro.treble.enabled`、Vendor namespace 隔离和 CPU ABI 已结合之前 `ro.vndk.version=30`、`arm64-v8a` 实机结果确认，**基础兼容性达标**。并非特定新版 GSI `vndk`/签名公钥或最终启动验证；AOSP 从 Android15 开始弃用新 VNDK、保留旧版（≤14）APEX 兼容包，详见 [专项](research/p780-dsu-locked-gsi-20261018.md)。
- 当前阶段没有新 GSI 下载/安装、没有获取原始 VBMeta/Boot 镜像、没有获得 Root 或解锁。下一步获取 Google DSU JSON 具体字段，原始镜像 ZIP 仍不下载。

## 2026-10-18 DSU 第五轮：VNDK / ARM64 / 空间与目录来源查询

- 机主真实执行 `adb shell getprop persist.sys.fflag.override.settings_dynamic_system.list`→空；`adb shell getprop ro.vndk.version`→`30`；`adb shell getprop ro.product.cpu.abi`→`arm64-v8a`。
- `adb shell df -h /data` 返回 `/dev/block/dm-11 106G 3.2G 103G 4% /storage/emulated/0/Android/obb`。按输出当前可用空间为 103G；最后一列不是 `/data` 但可能是 Android namespace/bind 的显示，不能由此断言真实 DSU 镜像临时分配或挂载状态。
- AOSP `DSULoader.java` 使用 `cpu_abi` 强制架构匹配，`os_version/vndk/spl` 可选字段若存在则筛选，故先前四个在线 GSI 项出现是**基础客户端筛选**结果，未取得 JSON 原件，不能确认 vndk 数组确实包含 30。仍需 Treble 支持和 linkerconfig 隔离只读确认。
- 结果已经加入 [DSU 第五轮实证专题](research/p780-dsu-locked-gsi-20261018.md)。本轮未下载安装、启用 GSI 或重启，更未获得 Root/BL 解锁。原始 ADB 输出来自本轮会话，尚无独立可哈希 TXT 原件。

## 2026-10-18 DSU 第四轮：原厂安装服务由机主恢复成功（当前状态）

- 用户在 Windows PowerShell 实际执行 `adb shell cmd package install-existing --user 0 com.android.dynsystem`，stdout：`Package com.android.dynsystem installed for user: 0`。
- `adb shell pm path com.android.dynsystem` 返回 `package:/system/priv-app/DynamicSystemInstallationService/DynamicSystemInstallationService.apk`。
- `adb shell dumpsys package com.android.dynsystem | Select-String -Pattern 'User 0:|installed=|enabled='` 显示 `User 0: ceDataInode=19397 installed=true hidden=false suspended=false distractionFlags=0 stopped=false notLaunched=false enabled=0 instant=false virtual=false`；这与先前 `installed=false` 的历史快照构成相同设备本轮操作前后闭环，证实用户级恢复成功。
- 命令没有闪存写入、Root、BL 解锁或出厂重置；**没有下载、安装、启动任何 GSI**。仅表示恢复 DynamicSystemInstallationService APK 对 user0 的安装登记，尚未测试实际 GSID/AVB/GSI 配合。
- 现行状态由 [DSU 第四轮专题](research/p780-dsu-locked-gsi-20261018.md) 和 [STATUS](STATUS.md) 决定；前面第二、三轮的 `installed=false` 必须当作**恢复前的历史结果**，不得再当作手机当前状态。

## 2026-10-18 DSU 第三轮：安装器 user 0 已卸载（直接实机证据）

- 机主确认自己已对现用 P780 做最深度 ADB 精简；开发者选项截图中「Select DSU Package」能显示两组 Google ARM64 GSI/GSI+GMS（`BP1A.250405.005.C1` 与 `CPI1.251209.009.A1`）；**截图只在本聊天出现、未提交 GitHub**。在线列表可见不等于选择后可以成功下载、验签、安装或启动。
- `adb shell am get-current-user`→`0`，不带 `-u` 的 `pm list packages --user 0 com.android.dynsystem` 空，而 `pm list packages -f -u --user 0`→`package:/system/priv-app/DynamicSystemInstallationService/DynamicSystemInstallationService.apk=com.android.dynsystem`；`dumpsys package com.android.dynsystem`→`User 0: ... installed=false ... enabled=0`。直接证明系统原厂 APK 仍在，但用户 0 的安装状态是 false。`enabled=0` 是 PackageManager DEFAULT，不是 DISABLED。
- 原仓库两份历史精简脚本均将 `com.android.dynsystem` 列入 `pm uninstall --user 0` 候选，且机主确认曾进行深度精简：合理解释当前卸载状态，但不冒称已找到具体执行成功记录。
- [详尽取证和官方 AOSP/Google 来源](research/p780-dsu-locked-gsi-20261018.md)。**尚未执行** `cmd package install-existing`、下载、安装或启动 GSI，不更改设备当前状态；如需恢复系统内置安装器，只在机主同意后进行。

## 2026-10-18 DSU 第二轮实机证据 + 历史 debloat 交叉线索

- 机主确认 **开发者选项中有 DSU Loader**，之前“系统 UI 未找到”的说法已被实机证据纠正。`pm list packages -u | findstr /I "dynsystem gsi"` 得到 `package:com.android.dynsystem`；`/system/etc/init/gsid.rc` 为 `-rw-r--r-- root root`，590 字节；`/metadata/gsi` 和 `/metadata/gsi/dsu` 均报 Permission denied；`getprop | findstr /I "gsid dsu gsi"` 无匹配。
- Android 官方文档明确 `pm list packages -u` 会同时列举 **uninstalled packages**；因此上述包记录与以前 `pm path com.android.dynsystem` 返回空不矛盾，本机 user0 安装状态仍待检查。AOSP Android 11 `gsid.rc` 为 root/system `0771` 创建 `/metadata/gsi` 目录，拒绝普通 shell 访问属于权限预期，不能由此证明目录内容。
- [历史应用精简档案](research/apps-and-debloat.md) 证实机主此前做过 `pm uninstall --user 0`；[完整精简脚本](../archive/scripts/hand5g_debloat_p780.ps1) 和 [日用精简脚本](../archive/scripts/hand5g_debloat_daily_phone.ps1) 均把 `com.android.dynsystem` 列为**拟卸载目标**；[phase3 已安装名单](../evidence/restricted/adb/phase3/hand5g_packages_installed_phase3.txt) 又含该包。脚本出现并不是确切执行日志，故只能评估为“可能曾被卸载”；未改变设备，也未将包恢复。新专题 [DSU 证据与核查](research/p780-dsu-locked-gsi-20261018.md)。

## 2026-10-18 DSU 第一轮六项实机只读取证

- 机主在本聊天提交 PowerShell 原始输出（无独立 TXT 附件）：`pm path com.android.dynsystem` 空；`/system/bin/gsi_tool` 存在 47,016B、权限 `-rwxr-xr-x root shell`；`/system/bin/gsid` 访问 `Permission denied`；`init.svc.gsid`、`persist.sys.fflag.override.settings_dynamic_system`、`ro.gsid.image_running` 均为空；`/avb/q-gsi.avbpubkey`、`r-gsi`、`s-gsi` 在当前文件系统均不可见（No such file）。
- 2026-10-18 仅采集只读信息，**未执行** `gsi_tool status`（其某些 AOSP 版本会按需启动服务）、安装、启用或重启 DSU/GSI。文件及权限结果不能单独判断启用情况。
- AOSP Android 11 `gsid.rc` 是 disabled/oneshot 按需服务；GSI 公钥可能在 first-stage ramdisk，启动切根后正常不可见。**只有 `gsi_tool` 存在和标准 DSU PackageManager 路径无返回得到直接实机支持，不能宣称 P780 确实可运行 GSI 或根本不支持。** [对应研究及来源](research/p780-dsu-locked-gsi-20261018.md)。

## 2026-10-18 Key Attestation 本机证实（脱敏档案）

- 用户上传 `P780-KeyAttestation.p7b`（PKCS#7，3475 bytes，含 4 张证书），目前**仅在当前私有会话和用户设备/电脑中保留原件，Git 中没有复制或完整证书链**。
- 本地解析 Android Key Attestation 扩展、TrustedEnvironment 级别与 RootOfTrust；根证书 DER 与 Google 公布的 2019 硬件证明根证书完全一致，4 张证书自签/级联签名均有效；`deviceLocked=true`、`Verified`、补丁 `2024-02`。
- `verifiedBootKey` 完整为 `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`，等于 SHA256(AOSP RSA4096 testkey 的 1032B AVB public-key blob)；`verifiedBootHash=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`，与旧本机 ADB digest 完全一致。
- **证据边界**：签名链和可信根已离线核验，但正式在线吊销完整核验尚未完成；未获得 vbmeta 分区原件、链式描述符、Root、解锁或锁定态写入渠道。分析过程和公开参考见 [脱敏专项](research/avb-attestation-confirmed-20261018.md)。不公开个人证书主体、设备标识或 challenge。

## 2026-10-18 第五轮实机与公共 OTA 索引交叉线索（会话原文，未上传原始 TXT）

- 用户提供 `ro.build.fingerprint=Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`；随后通过附在聊天中的终端文本**实际读取了** `/vendor/etc/fstab.default` 与 `/vendor/etc/fstab.emmc`，`fstab.qcom` 不存在。两份文件的 AVB 挂载分组和 GSI 额外公钥路径已逐项核对并保存 [技术摘录](research/p780-fstab-avb-20261018.md)；**未将原始两个 fstab 文件作为独立的字节级原件上传 Git**，聊天附件也不是手机原始文件 SHA。
- 已通过 GitHub 工具读取 [google-ota-prober](https://github.com/tangalbert919/google-ota-prober) 源码、[Rakuten C330 官方 Google OTA 历史索引](https://github.com/mouseos/ota-archive/blob/main/OTA/Google/rakuten/c330/index.json)、[Tinno P710 构建指纹索引](https://github.com/mouseos/ota-archive/blob/main/OTA/Google/tinno/p710/index.json)。**这些是第三方公共 metadata，不是取得 P780 OTA 原件或完成本机在线探测**，技术细节见 [专题](research/google-ota-prober-p780-20261018.md)。

- 用户运行 `google-ota-prober` 的 P780 CLI 查询，得到 `No OTA URL found for your build`（无下载链接）；是**机主 PC 实测终端输出**，不是 Google 接口状态码，也不是明确的固件服务器不支持结论。详见 [Google OTA 专题](research/google-ota-prober-p780-20261018.md)。

## 2026-10-18 AVB 实机取证（聊天原文，未上传附件）

- 用户在本次对话中提交 2 轮 ADB 原始终端输出；已摘录到 [AVB 专题](research/avb-live-baseline-20261018.md)，包括 `green`、`locked`、`_b`、完整 VBMeta digest、`sha256`、`7744`、AVB `1.1` 和 A/B 分区软链接。
- **保存状态：仅文档转录，未提供独立 TXT 原件**；未来若需逐字节存证，应由用户自行导出并检查潜在隐私再上传。不可冒称是已取得 `vbmeta_b.img` / `vbmeta_system_b.img`。
- `vbmeta.size` 为本次加载 VBMeta 总大小，候选链式 `vbmeta_system_b` 未经签名描述符读取验证。未来原厂镜像采集状态依然为**未取得**。
- 同日第四轮会话终端输出：`ro.boot.dynamic_partitions=true`；`ro.virtual_ab.enabled`、`ro.virtual_ab.compression.enabled`、`ro.boot.vbmeta.device` 为空。以上为用户转述原样输出，已登记于 [AVB 基线专题](research/avb-live-baseline-20261018.md)；仍未获取镜像、OTA 或操作快照。
- 同日第三轮会话终端输出：`vbmeta.public_key_digest` 空、Bootloader/Android libavb `1.0/1.1`、`veritymode=enforcing`、VBMeta 对应设备节点 `0600 root:root`、动态分区 dm-verity 映射及 `system_b-cow`；**同样仅专题转录、未上传日志原件、未获取块设备原始字节**。

2026-10-10 从历史文件库实际枚举。**已登记不代表原件已经 GitHub 归档**；文件名与大小来源于文件库。文本报告已有用户设备实测背景；研究工具有不同的只读与会修改设备类别。

| 研究原件 | 字节数 | 保存状态 |
|---|---:|---|
| `hand5g_debloat_audit.zip`（新上传） | 376662 | [22 项原件 ZIP，已做字节匹配](../evidence/restricted/adb/hand5g_debloat_audit.zip) |
| `ApeHighLights.apk`（新上传） | 1704633 | [原始 APK](../evidence/apk/ApeHighLights.apk) |
| `com.qualcomm.qti.services.secureui.apk`（新上传） | 24990 | [原始 APK](../evidence/apk/com.qualcomm.qti.services.secureui.apk) |
| `com.qualcomm.qti.services.systemhelper.apk`（新上传） | 16798 | [原始 APK](../evidence/apk/com.qualcomm.qti.services.systemhelper.apk) |
| `hand5g_packages_all_phase3.txt`（新上传） | 22482 | [原始 UTF-16 清单](../evidence/restricted/adb/phase3/hand5g_packages_all_phase3.txt) |
| `hand5g_packages_installed_phase3.txt`（新上传） | 17724 | [原始 UTF-16 清单](../evidence/restricted/adb/phase3/hand5g_packages_installed_phase3.txt) |
| `Rakuten_Hand_5G_P780_EDL_重要数据.txt`（2026-06-12 更早文件，单独检索） | 2554 | [已存 GitHub：脱敏版](../archive/device/P780_EDL_2026-06-12_sanitized.txt) |
| `p780-config(1).gz` | 39170 | 另有 evidence/device 主原件（未复核本副本 SHA） |
| `P780-master.zip` | 242946767 | **原文件库保留，未入 Git 仓库** |
| `P780-ARM64-Kconfig-reachability-20261010.zip` | 3519382 | **原文件库保留，未入 Git 仓库** |
| `P780-5.4.233-source-bridge-20261010.zip` | 48277 | **原文件库保留，未入 Git 仓库** |
| `P780-Kconfig-analysis-20261010.zip` | 3458052 | **原文件库保留，未入 Git 仓库** |
| `P780-Kconfig-source-bundle.zip` | 4077134 | **原文件库保留，未入 Git 仓库** |
| `P780-offline-kernel-study-20261010.zip` | 52078 | **原文件库保留，未入 Git 仓库** |
| `P780-WSL-source-prep(1).sh` | 4543 | **原文件库保留，未入 Git 仓库** |
| `P780-WSL-source-prep.sh` | 4543 | [已存 GitHub](../archive/tools/P780-WSL-source-prep.sh) |
| `P780-module-inventory.txt` | 8560 | [已转存 44 个模块名的脱敏结果](../archive/device/P780_loaded_module_names.md)；原始 UTF-16 未迁入 |
| `p780_module_audit(1).py` | 6988 | **原文件库保留，未入 Git 仓库** |
| `p780_module_audit.py` | 6988 | [已存 GitHub](../archive/tools/p780_module_audit.py) |
| `P780-GhostLock-port-v0.4.zip` | 99662 | [已存 GitHub：原始字节已校验](../evidence/ghostlock/P780-GhostLock-port-v0.4.zip) |
| `P780-GhostLock-port-v0.3.zip` | 67667 | [已存 GitHub：原始字节已校验](../evidence/ghostlock/P780-GhostLock-port-v0.3.zip) |
| `P780-GhostLock-port-v0.2.zip` | 72599 | [已存 GitHub：原始字节已校验](../evidence/ghostlock/P780-GhostLock-port-v0.2.zip) |
| `P780-GhostLock-port-v0.1.zip` | 57818 | [已存 GitHub：原始字节已校验](../evidence/ghostlock/P780-GhostLock-port-v0.1.zip) |
| `p780_ghostlock_audit(1).py` | 5471 | **原文件库保留，未入 Git 仓库** |
| `p780_ghostlock_audit.py` | 5471 | [已存 GitHub](../archive/tools/p780_ghostlock_audit.py) |
| `P780_GhostLock_源码核对报告_2026-10-10.md` | 8090 | [已存 GitHub](../archive/reports/P780_GhostLock_source_audit_2026-10-10.md) |
| `p780-cpu4.raw` | 4096 | [已存 GitHub：原始字节已校验](../evidence/device/p780-cpu4.raw) |
| `p780-config.gz` | 39170 | [已存 GitHub](../evidence/device/p780-config.gz) |
| `hand5g_debloat_daily_phone.ps1` | 13721 | [已存 GitHub](../archive/scripts/hand5g_debloat_daily_phone.ps1) |
| `hand5g_debloat_p780.ps1` | 14373 | [已存 GitHub](../archive/scripts/hand5g_debloat_p780.ps1) |
| `hand5g_final_audit.zip` | 419387 | [原始 ZIP 已入私库](../evidence/restricted/adb/hand5g_final_audit.zip) |
| `hand5g_debloat_audit(1).zip` | 376662 | 与新上传 ZIP 大小相同，原件独立 SHA 尚未比对 |
| `hand5g_debloat_audit.zip`（旧 1742B 小包） | 1742 | **仍在历史文件库，非这次完整审计包** |
| `hand5g_bugreport.zip` | 5684665 | [已入私库：含敏感数据风险](../evidence/restricted/bugreport/hand5g_bugreport.zip) |
| `hand5g_update_log.txt` | 283944 | [已入私库：原始 UTF-16 日志](../evidence/restricted/ota/hand5g_update_log.txt) |
| `hand5g_update_activity.txt` | 94710 | [已入私库：原始 UTF-16 日志](../evidence/restricted/ota/hand5g_update_activity.txt) |
| `hand5g_native_api_paths.txt` | 1174 | [已入私库：访问失败证据](../evidence/tee/hand5g_native_api_paths.txt) |
| `hand5g_tz_whitelist.txt` | 3148 | [已入私库：TEE 白名单原文](../evidence/tee/hand5g_tz_whitelist.txt) |
| `Hand5G_P780_TZAccess_20261004.md` | 4016 | [已存 GitHub](../archive/reports/P780_TZAccess_2026-10-04.md) |
| `hand5g_TZAccessService.apk` | 49566 | **原文件库保留，未入 Git 仓库** |
| `Hand5G_P780_MinkNative_20261004.md` | 4915 | [已存 GitHub](../archive/reports/P780_MinkNative_2026-10-04.md) |
| `hand5g_pfm_detail.txt` | 1080 | **原文件库保留，未入 Git 仓库** |
| `hand5g_mink_log.txt` | 2286 | **原文件库保留，未入 Git 仓库** |
| `hand5g_mink_runtime.txt` | 4914 | **原文件库保留，未入 Git 仓库** |
| `hand5g_mink_files.txt` | 2002 | **原文件库保留，未入 Git 仓库** |
| `Hand5G_P780_PFM_QAS_20261004.md` | 20487 | [已存 GitHub](../archive/reports/P780_PFM_QAS_2026-10-04.md) |
| `hand5g_qas_dvc_msp.txt` | 10018 | **原文件库保留，未入 Git 仓库** |
| `QAS_DVC_MSP.apk` | 2706410 | **原文件库保留，未入 Git 仓库** |
| `hand5g_qcom_auth_candidates.txt` | 25856 | **原文件库保留，未入 Git 仓库** |
| `hand5g_uid1000_candidates.txt` | 363930 | **原文件库保留，未入 Git 仓库** |
| `hand5g_ape_test_log.txt` | 6756 | **原文件库保留，未入 Git 仓库** |
| `hand5g_ape_components.txt` | 63898 | **原文件库保留，未入 Git 仓库** |
| `hand5g_settings_package.txt` | 307386 | **原文件库保留，未入 Git 仓库** |
| `hand5g_ape_package.txt` | 103284 | **原文件库保留，未入 Git 仓库** |
| `hand5g_user.txt` | 12762 | **原文件库保留，未入 Git 仓库** |
| `hand5g_lshal.txt` | 112768 | **原文件库保留，未入 Git 仓库** |
| `hand5g_packages.txt` | 56924 | **原文件库保留，未入 Git 仓库** |
| `hand5g_fastboot_all.txt` | 16790 | **原文件库保留，未入 Git 仓库** |
| `hand5g_mount.txt` | 26898 | **原文件库保留，未入 Git 仓库** |
| `hand5g_kernel.txt` | 966 | [已存 GitHub](../archive/device/hand5g_kernel.txt) |
| `hand5g_getprop.txt` | 54618 | **原文件库保留，未入 Git 仓库** |
| `hand5g_df.txt` | 4658 | [已存 GitHub](../archive/device/hand5g_df.txt) |
| `hand5g_byname.txt` | 12182 | [已存 GitHub](../archive/device/hand5g_byname.txt) |

## 另外的云端构建原件

- [Clang 11 #38053176845](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053176845)；[Clang 14 #38052323798](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38052323798)；[Config delta #38053251640](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053251640)。GitHub Actions Artifact 会过期；**[永久归档运行 #38054396216](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38054396216) 已成功**，原始构建工件保存在仓库 `evidence/actions/` 下。

## 已补全原件与仍未迁入的历史证据

- `p780-cpu4.raw` **已完整入仓**：[原始二进制](../evidence/device/p780-cpu4.raw)，4,096 字节，含实验追踪标记；此前的遗留“等待上传”状态已关闭。
- `hand5g_getprop.txt` 与 `hand5g_fastboot_all.txt` 的历史独立原件未入仓。Bugreport 和 OTA/Activity 日志**已经进入私库**的 `evidence/restricted/`；它们仍可能含敏感数据，**未脱敏，不适合公开**。
- GhostLock v0.1–v0.4 的**四份原始 ZIP 已完整入仓并通过 CRC/SHA 检验**；见 [版本与内容索引](archive/ghostlock-package-versions.md)。
- 大型 `P780-master.zip`、`linux-android-samsung-a52sxq-droidian.zip` 可从上游仓库按指定 commit 再取得，避免将整份第三方源码提交为冗余仓库附件。

## 最新整理与原件去重

- 2026-10-10 新增 3 份 APK、2 份 TEE 记录、2 份 OTA 日志、1 份 Bugreport，以及两套 ADB 审计 ZIP。新文件另见 [导入与去重报告](archive/20261010-import-dedup.md)。
- `hand5g_debloat_audit/` 22 个文件与完整 ZIP 内字节相同，`hand5g_final_audit/` 9 个文件亦如此；`main` 已保留两个原始 ZIP、删除 31 个重复展开文件。
- 清理前完整状态备份于 [archive/pre-cleanup-20261010](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010)。

## 完整性原则

原始 Tracefs 与 GhostLock 四代 ZIP 已经入仓，其字节级和内部哈希核对见 [证据完整性](reference/evidence-integrity.md)。其它只有文件清单和分析结论的项目不能标为原始文件已入仓；UTF-16/乱码或无可读内容的文件也不作伪造转写。设备唯一标识、IMEI、带密码与登录凭据的记录不应进入可公开仓库，私库也尽可能脱敏。

_早前至少 57 条历史文件记录已保留；本轮新增文件按原始名称另行登记。文件清单中的同名/同大小资料不自动表示 SHA 相同。_


## 2026-10-10 配置引用与候选布局实验

- [24 项配置与候选布局研究](research/config-layout.md)：24 项配置的逐项源级判断。
- `evidence/actions/2026-10-10-layout-audit/source-audit/`：两棵固定树扫描得到的原始引用 JSON/Markdown 和实际计算的 provenance 哈希。
- `evidence/actions/2026-10-10-layout-audit/`：每轮 Actions 原始/求解配置、Kbuild 命令、日志、汇编及候选结构测量 JSON；首轮失败资料亦保留。
- `tools/audit_missing_config.py`、`tools/derive_candidate_layout.py`、`tools/p780-layout-probe.c`、`tools/compare_candidate_layouts.py` 与 `.github/workflows/p780-layout-audit.yml`：离线研究流程，不连接手机。

## 当前 framework 输入与提取证据

- p780-framework-audit.zip：机主上传 18,141,023 B，CRC 通过；含 services.jar/framework.jar 与五份文本。原始 ZIP/JAR 仍保留在上传文件，未将原始字节迁入 Git。
- [输入 SHA/原件存放状态](../evidence/framework/2026-10-10/input-manifest.json)；[目标方法原始字节](../evidence/framework/2026-10-10/journey-bytecode.json)、反汇编、调用点 JSON、五份 UTF-8 清单已入 Git。反汇编和阅读视图不冒充原始 JAR/UTF-16 原件。
- [Journey 实机代码专题](research/journey-config.md) 与 [OTA 日志深入审计](research/ota-log-audit.md) 已补齐，旧“下一阶段审阅引擎日志”的说明已修订。

## Journey 配置与运行状态（已完成核对）

机主 p780-journey-config.zip 共 3,940 B、3 条目、CRC 通过；[完整原始字节的 Base64 存档](../evidence/journey/2026-10-10/p780-journey-config.zip.b64) 与 [SHA/还原说明](../evidence/journey/2026-10-10/input-manifest.json) 已入仓。vendor XML/version 提供原件文本，TCS 提供 UTF-8 阅读视图；UTF-16 原始字节包含在编码 ZIP 中，避免重复归档。

[64 键对照](../evidence/journey/2026-10-10/comparison.json) 与 [复核工具](../tools/compare_journey_config.py) 已保存；专题、README、STATUS、NEXT_STEPS 同步修订，关闭上一轮等待采集项。原始 framework ZIP/JAR 的未迁入状态仍保持明确。

## Journey 性能策略消费者（静态核对完成）

同一批 framework 输入复用，不重复上传原始 JAR。新增 [134 方法反汇编](../evidence/framework/2026-10-10/performance-disassembly.txt)、[79 条外部引用](../evidence/framework/2026-10-10/performance-callsites.json)、[6 个决策方法原始指令与解析](../evidence/framework/2026-10-10/performance-decision-methods.json)、逐 DEX SHA 和验证摘要；[提取脚本](../tools/read_performance_dex.py) 直接读取原始表，无 DEX 修补。54 个此前配置方法偏移/字节交叉核验通过。覆盖与运行时限制见既有 [Journey 专题](research/journey-config.md)，关闭消费者/星号待研究项。


## 2026-10-17：XDA 4805241 用户提供正文

- [英文粘贴正文](../evidence/web/2026-10-17/xda-4805241-user-provided.txt)：按用户提供的文本归档，不冒称原网页 HTML；作者、发表时间及是否独立于机主研究未核实。
- [线索状态/去重记录](../evidence/web/2026-10-17/xda-4805241-pending.json)：保留原始获取失败和邮件通知历史，追加正文已收到/获取请求关闭。未取得实验 ZIP、完整命令、证书或 Recovery 原始日志。
- 技术边界与下一步见 [专题补充](research/firmware-advisory-20260928.md)；第三方设备报告不替代本机 `_162` 证据。

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
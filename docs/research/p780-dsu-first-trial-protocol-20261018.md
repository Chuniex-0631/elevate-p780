# P780 DSU 首次实机试验协议（2026-10-18）

> **状态：机主已表示愿意开展分阶段 DSU 实验，但截至本记录尚未下载、安装、启动 GSI。** Bootloader 仍 LOCKED，未 Root。DSU 设计避免覆盖原厂 system/boot 镜像，**不保证 userdata 零风险、不会 bootloop 或无需 Recovery 清空数据**。

## 为什么值得测试

已有本机证据：Android 11 P780、ARM64、VNDK 30、Treble、`[vendor] namespace.default.isolated=true`、A/B 动态分区、F2FS、存储可用约103GB、官方 `com.android.dynsystem` user0 已恢复为 `installed=true`、DSU Loader 可以列出四条 Google ARM64 GSI。主索引及6个子目录/24条 GSI JSON 已核对；记录全缺 `vndk/pubkey` 可选字段，**菜单可见不代表具体镜像签名公钥已可信或实际能启动**。公开标准 q/r/s GSI AVB 公钥与设备主 AVB 测试根公钥不同，设备 ramdisk 内 q/r/s 的真实文件尚未导出。

## 第一测试镜像与理由

- 首选 DSU Loader 第一项 **GSI ARM64**，Android 15 QPR2 `arm64-exp-BP1A.250405.005.C1-13151952-61d23231`，**不选 GSI+GMS**、不选 Android16 `CP11`；不用通过 Fastboot 下载/刷入。
- [Google Android15 官方 GSI release](https://developer.android.com/topic/generic-system-image/releases) 列此 ARM64 无 GMS ZIP 的发布 SHA256 为 `61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`；此 SHA 是官方公布的**期望值**，并未下载 ZIP 验证。
- 选择 Android15/无 GMS 是为了少一个大版本、通常更小且减少 GMS 依赖，不保证 P780 Android11 Vendor/Gatekeeper/Weaver/HAL 或 DSU AVB 接受它。
- 同一 Google 页面明示：Android15 GSI 某些设备重启失败，恢复可能须进入 Recovery **清空用户数据、恢复出厂**；部分 GMS 镜像过大。故本机的可恢复性高于静态取证风险。

## 阶段 0：备份与可接受后果

机主确认无不可丢失的重要数据，或先复制研究文件、照片和需要的私人文件至电脑。可选 PowerShell：

```powershell
New-Item -ItemType Directory -Path ".\P780-DSU-Backup" -Force | Out-Null
adb pull /sdcard/ ".\P780-DSU-Backup\SharedStorage"
```

注意上述备份只能复制共享存储，不包括 `/data/data` 私有应用数据、加密密钥、Keystore、系统分区和所有账号信息；不能视为完整备份。建议电量充足、稳定 Wi-Fi、连接充电，保留原始 `P780-KeyAttestation.p7b` 在电脑私有路径。若任何数据不能丢失，且 Recovery 恢复入口没有把握，则应停止首次重启测试。

## 阶段 A：仅先测试下载/安装，暂停在重启之前

1. 手机“设置 → 开发者选项 → DSU Loader”，选择第一项 `GSI ARM64`，核对版本字符串 `BP1A.250405.005.C1`。
2. 阅读并确认系统警告/条款之后才会开始真正下载、创建独立 DSU 临时分区和分配 `/data`；这一步会修改设备用户区，**不是只读操作**。
3. 保持充电和网络，观察进度及错误。若下载/安装失败，保存通知或屏幕错误；不要依次尝试其它镜像、关闭签名校验、执行 fastboot/EDL/手动分区写入。
4. 若通知显示 **Restart** 和 **Discard**，**先不要点击 Restart**；保存截图并报告阶段 A 是否成功。官方 [DSU 教程](https://developer.android.com/topic/dsu) 中 Restart 是真正启动临时系统；Discard 是删除已下载 DSU 文件的官方选项。
5. 当前不运行 `gsi_tool enable`（会涉及持久/非单次启动选择）、`gsi_tool wipe`、`setprop`，也不要拔掉关键供电强制中止尚在安装的过程。

## 阶段 B：备份、安装结果核验后再尝试实际 GSI 启动

机主另行确认愿意承担重启失败/可能清除 userdata 的风险后，才按 DSU 通知的 Restart。成功进入 GSI 时只做系统版本、支持功能和只读日志检查；使用 GSI 的 DSU 通知 Restart 返回原厂。失败时**不要无休止重启或刷入随机镜像**：先尝试受支持的正常冷重启；如果无法恢复，可能需要 Recovery 和恢复出厂。**尚未取得 P780 上可保证不清数据的失败恢复操作实测，不能承诺按一次电源键就能安全回退。**

## 需要记录的结果

- 首次安装用的确切 GSI 条目。
- 下载/安装有无启动、通知进度及错误提示。
- 是否已到达 **Restart / Discard** 通知；到达时先暂停并上传截图。
- 是否完成个人数据备份/确认用户数据可丢弃。

官方原理：[AOSP DSU](https://source.android.com/docs/core/ota/dynamic-system-updates)、[Android Developers DSU](https://developer.android.com/topic/dsu)、[Android15 GSI 已知风险](https://developer.android.com/topic/generic-system-image/releases)。**当前没有成功安装或启动 P780 GSI 的证据**，本文件为待执行实验方案，不是试验成功报告。

## 首次实际执行结果更新（2026-10-18）：安装完成提示出现，但启动未进入 DSU

机主随后报告：GSI 下载显示完成，DSU 通知要求 Restart；点击重启后回到原厂 Android 11，并再次提示 Restart，第二次点击仍重复回原系统。**首次试验的第二阶段已经由机主实际触发，但并未进入 GSI**，此前本文件“尚未安装/重启”的说明属于事前协议快照，不再代表现状。具体镜像 ID 仍待日志/通知确认；GSID installed/enabled 状态也未读取。不是设备自发持续重启的 bootloop。请以 [启动返回原系统诊断专题](p780-dsu-stock-fallback-20261018.md) 和 [当前计划](../NEXT_STEPS.md) 为准，勿重复 Restart、enable 或 wipe。

# P780 第十三轮：首次 DSU 失败后的 Android Bugreport 全量离线审计（2026-10-18）

> 本报告仅针对用户上传的真实 `P780-DSU-Bugreport.zip` 进行**本地只读分析**。提取必要的、已去标识化技术字段，**不上传完整 ZIP / 19.7 MB Bugreport / MAC / IMEI / 账号 / 网络数据到 GitHub**。手机仍原厂 Android 11，Bootloader LOCKED、未 Root，未启动 GSI。

## 输入文件与完整性

- 用户从 P780 在原厂系统中运行 `adb bugreport` 导出 `P780-DSU-Bugreport.zip` 并上传本轮对话。Python `zipfile.ZipFile.testzip()` 全部通过，无损坏。
- ZIP 原始大小约 2.9 MB；精确 SHA-256：`64a097d0911e35675c75dff09d68a7e28b5aa15bd342ed796387d12758d5f141`；ZIP 内共 **362 个成员**（包含 FS/mountinfo、incident/lshal、日志和 `bugreport-P780-RKQ1.210715.001-2026-10-18-07-10-54.txt`）。
- 主 Bugreport TXT 原始长度 **19,721,044 bytes**，约 240,297 行，SHA-256 `8767fb7c186050240f3203fd65a82ab73b95dbbeeec338654ba439580f984836`。收集于约 2026-10-18 07:10～07:12（设备本地时间）。

## 直接证据 A：设备持久保存了连续两次 DSU 专用重启原因

**主报告系统属性区约第 108039～108041 行**，原文（只含一般启动标记）：

```text
[persist.sys.boot.reason.history]: [reboot,dynsystem,1792276290
reboot,dynsystem,1792276231
reboot,shell,1791140253]
```

前两项 Unix 时间戳换算为 UTC+08:00 分别为 **2026-10-18 06:31:30** 与 **06:30:31**。这独立印证机主进行了**两次分别由 DSU 提示触发的重启**，而非手机自主不断 bootloop。第 108167 行 `[ro.boot.bootreason]: [reboot,dynsystem]`；第 108725～108726 行 `[sys.boot.reason]` 和 `[sys.boot.reason.last]` 亦均为 `reboot,dynsystem`。来源是持久启动原因数据，**不等于已进入 GSI first-stage 挂载成功**。

## 直接证据 B：已安装 GSI，收集报告时未运行

**同一份 Bugreport 系统属性区**：

```text
[gsid.image_installed]: [1]      # 约第 107607 行
[ro.gsid.image_running]: [0]     # 约第 108448 行
[init.svc.gsid]: [stopped]       # 约第 107650 行
[ro.boot.slot_suffix]: [_b]      # 约第 108183 行
[persist.sys.fflag.override.settings_dynamic_system]: [1] # 第 108045 行
```

这与上轮机主 `gsi_tool status` 输出 `installed / disabled` 和 `DynamicSystemService: isInstalled(): true` 相互支持。上轮普通 `adb shell getprop ro.gsid.image_running` 为空，Bugreport 记录为 `0`；这是**不同访问上下文/采集方式**的可见性差异，不再误判属性全机不存在。

**主报告约第 42498～42532 行**记录了 `DEVICE-MAPPER (gsid dump-device-mapper)`：可见 `system_b`、`vendor_b`、`product_b`、`system_ext_b`、`odm_b` 及 `*-verity` 等原厂动态映射，没有看到以 DSU 命名的活跃临时映射。该表反映**报告采集时处于原厂 B 槽的正常运行环境**，**不能**证明上一次 DSU 重启中的临时镜像曾经映射失败，因为重启回原厂后映射状态本就可能消失。

## 直接证据 C：LAST KMSG / persistent boot 日志确实没有取得

- **第 103264 行**由 dumpstate 明确报告：

```text
*** Error dumping /proc/last_kmsg (LAST KMSG): No such file or directory
```

- **约第 239905～239911 行** incidentd 依次尝试

```text
/sys/fs/pstore/console-ramoops
/sys/fs/pstore/console-ramoops-0
/proc/last_kmsg
```

  均报告 `GZipSection failed to open file`，随后 `can't open all the files`。这是设备当前没有通过这些路径提供可采集内核持久日志的**正面失败证据**，不能再提议重复同样的 `adb bugreport`、pstore shell、或内核缓冲区命令。
- **第 41774～41776 行**：`LAST LOGCAT (logcat -L -b all ...)` 执行失败，退出码1，因此上次启动的持久化 logcat 亦未取得。
- **第 55699 行**当前启动的 `KERNEL LOG (dmesg)` 确实存在，但第一条时间戳已经是内核开机后的 **[943.330607] 秒**，整个约 2635 行片段无 `DSU/GSI/AVB/first_stage/verity` 相关记录；说明这份当次内核环形缓冲区内容**无法覆盖早期引导**，不能写成“内核未发生错误”。

## 其它客观发现（并非根因）

- 06:31:40.850 的 `DynSystemInstallationService onStartCommand(): action=NOTIFY_IF_IN_USE` 和 06:31:40.852 `DynamicSystemService: isInstalled(): true`（前轮原始 Logcat 已验证）与本 Bugreport 中的安装状态相符。
- 当前 `gsiservice` AIDL 有 lazy service 按需启动/客户端断开记录，例如 06:37:10～06:37:13、07:11:17～07:11:19；这是符合 AOSP GSID 非常驻的现象，不是 DSU 启动失败的直接报错。
- 后续出现第三方 `vegabobo.dsusideloader` 应用桌面图标/普通 Dex2OAT hidden API 告警，但**没有日志证明它参与了这次通过系统自带 DSU Loader 发起的启动**，不能因此归因为第三方 DSU Sideloader 干扰，不把其存在列为本次推测 root cause。

## 阶段判断与下一步

**证实：** 真实两次 `reboot,dynsystem`、Android DSU/GSID 已安装、bugreport 收集时 `ro.gsid.image_running=0`，设备回到原厂 B 槽，`LAST KMSG` 和 `LAST LOGCAT` 采集失败；当前可获取 `dmesg` 仅保留开机 943 秒后的片段。

**没有证明：** 哪一处 Android11 `CanBootIntoGsi/GetActiveDsu/MapAllImages/MarkSystemAsGsi/TransformFstabForDsu` 或后续 AVB/first-stage mount/HAL 环节失败。并没有实际 GSI 镜像公钥、P780 当前 boot ramdisk 内的 key bytes 或真实出错代码；**一切“公钥不匹配”与“映射失败”都仍是假说**。不能把事后 installed/disabled 简单视为没有启用 GSI，Android11 one-shot 有启动前消耗 enabled 的设计。

**研究建议：** 当前系统可正常进入原厂 Android，不应第三次同参数 Restart、不应开启默认 sticky、换 Android16、清空 userdata 或强刷。短期软件无 Root 事后取证途径已经用尽；优先离线从可信 P780 `_162` boot/ramdisk/first-stage init 和 Google GSI AVB 签名渠道寻找额外证据。若未来准备一次真正有诊断收益的复现，须事先能捕获早期引导（或有可复核的具体修复变量），做好数据备份、恢复方案并征求机主新的明确同意。

## 对照原始来源

- [此前第十二轮 DSU stock-fallback 时间线](p780-dsu-stock-fallback-20261018.md)
- [AOSP Android11 DynamicSystemInstallationService](https://android.googlesource.com/platform/frameworks/base/+/978ecf991a9a/packages/DynamicSystemInstallationService/src/com/android/dynsystem/DynamicSystemInstallationService.java)
- [AOSP Android11 first_stage_mount.cpp](https://android.googlesource.com/platform/system/core/+/9583e92257ab85075231b014f0999d5a5dab9910/init/first_stage_mount.cpp)
- [DSU 公钥信任链核验](p780-dsu-trust-chain-audit-20261018.md)
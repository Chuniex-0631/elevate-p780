# P780 ADB 应用清理与设备维护实验（历史）

2026-10-04，用户在已恢复出厂的实验用 P780 上执行一系列 **ADB user 0 应用清理** 和系统包信息收集；其目标之一是减少后台组件并保留可测试的基础 Android 功能。

## 历史实测数字

- 第一轮实际包数：**302 → 242**，该次约移除 60 个 user 0 包；可用内存历史记录从约 **1.55 GiB** 至 **1.90 GiB**，不同快照不能充当严格可重复的性能基准。
- 随后另一次壁纸、屏保和其他类别的清理与重启复核：**157 个 user 0 包**。查询 `wallpaper|dreams` 无命中。后续蓝牙清理有用户确认，但当前缺少完整最终命令输出。
- 已记录默认 HOME：`com.android.launcher3/...SearchLauncher`；早期 WebView：`com.google.android.webview` 93.0.4577.62。
- 这些包数反映不同时间点的**系统状态**，并不证明清理过程没有功能回归，也不能直接作为 GhostLock/bootloader 实验的前提。

## 新归档的实机审计原件

- [首次审计原件](../evidence/restricted/adb/hand5g_debloat_audit.zip)：376,662 B，22 个原始文件；包含当次 `getprop`、302 行 user0 包清单、服务、存储、内存、完整 `dumpsys package`。
- [后续综合审计原件](../evidence/restricted/adb/hand5g_final_audit.zip)：419,387 B，9 个文件，涉及包/进程/内存/服务；其中有 UTF-16 记录。
- 两套 ZIP 内文件与机主额外上传的两个同名展开目录**逐字节相同**；仓库只保留压缩版，删除共 31 个重复展开文件，参见 [去重报告](NEW_UPLOADS_AND_DEDUP.md)。
- [phase3 已安装包清单](../evidence/restricted/adb/phase3/hand5g_packages_installed_phase3.txt)（210 个包名）与 [phase3 全清单](../evidence/restricted/adb/phase3/hand5g_packages_all_phase3.txt)（271 个包名）采用**不同筛选范围**。不能凭 271→210 推断发生了 61 次卸载，也不能将其强行并入较早的 302→242→157 时间线。

这些原始系统快照可能含敏感信息，仍是**未脱敏历史材料**；完整内容保留在 Private 仓库，不应直接公开。

## 历史脚本

- [hand5g_debloat_p780.ps1](../archive/scripts/hand5g_debloat_p780.ps1)：为彻底精简制定的旧脚本，含 `adb shell pm uninstall --user 0`，会变更手机状态。
- [hand5g_debloat_daily_phone.ps1](../archive/scripts/hand5g_debloat_daily_phone.ps1)：后来设计的“日常电话仍可用”方案，强调保留电话、SIM、Google Play、NFC/FeliCa、Bluetooth 等核心服务；但只是**脚本设计**，不能仅凭存在脚本断言完整方案曾经成功跑通。
- 已归档两个脚本仅为**历史研究资料**；不要对新装系统盲目运行，更不要把两者全部串行执行。

## 与 OEM 解锁研究的关系

高权限包、诊断服务和 Qualcomm middleware 的列举有助于查找 QAS/TZ/更新服务组件，但简单移除预装软件、修改用户 0 包集或恢复出厂状态，并没有为设备提供已验证的 Bootloader 解锁通路。

其它包清单、`lshal` 及大量 dumpsys 文件仍仅保存在历史文件库，因为可能包含系统级日志、PID、服务记录、账号或电话号码；优先在本仓库保存脱敏后的技术结论与可复核脚本。

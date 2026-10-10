# 研究时间线（据可复查材料重建）

> 此时间线只记录能从已保存报告、文件元数据、终端片段或 GitHub Actions 回溯的事项。若仅有摘要而无原始日志，会明确写“历史记录”。日期统一按相关报告日期，不杜撰精确小时。

| 日期 | 阶段与资料 | 实际结果 |
|---|---|---|
| **2026-06-12** | 最早保存的 P780 EDL / Sahara / Fastboot 资料；`Rakuten_Hand_5G_P780_EDL_重要数据.txt` | 提取固件号、fastboot locked、unlock 指令返回 unknown command、EDL 05C6:9008 / Sahara v2 / HWID；Firehose 不通 |
| **2026-10-03 ～ 10-04** | ADB `getprop`、`fastboot getvar all`、`by-name`、`mount`、`df`、`lshal`、包清单；未联网/恢复出厂环境下的部分清理 | OEM unlocking 灰色；固件 264 / 安全补丁 2024-02-01；A/B UFS 分区事实归档 |
| **2026-10-04** | 系统应用与去预装实验；`hand5g_debloat_p780.ps1` 和保留基础电话功能的 `hand5g_debloat_daily_phone.ps1` | 历史记录：第一轮安装包 `302→242`，后来壁纸/屏保与其他清理后复查 `157` 包。数字为不同时间点快照，不能串成单次自动结果 |
| **2026-10-04** | `QAS_DVC_MSP.apk`、`xrvdservice.apk`、PFM/Mink/TZService APK 和 JNI 库静态分析、相关运行日志 | 识别 eMBMS PFM class 119/feature 700、XRVD 2100；XRVD 创建 IPFM 代理；没有发现 OEM Unlock 路径 |
| **2026-10-04** | `hand5g_update_activity.txt`、`hand5g_update_log.txt`、`hand5g_bugreport.zip` | OTA/更新服务检查材料已保留在文件库；本归档尚未逐字复核它们；**不声称获取到 OTA 包** |
| **2026-10-10** | 实机 `p780-config.gz`、`p780-cpu4.raw`、Tracefs 原始事件与模块读取测试；GhostLock v0.1–v0.4 工作包 | 配置满足 Futex PI/RT Mutex；追踪见候选地址；`/vendor/lib/modules` 可列但 SELinux 下无法读模块内容；GhostLock 未执行成功 |
| **2026-10-10** | TINNO P780 5.4.61 旧源码；Qualcomm A52s 5.4.233 候选源码；Kconfig 文件比对 | 旧源码存在 CVE 类似代理锁清理模式；不能推出运行中 5.4.233 有漏洞。候选源码含更多 HOLI/BLAIR 平台配置 |
| **2026-10-10** | GitHub Actions [首次](../.github/workflows/p780-kernel-audit.yml) 编译（#38051600739） | 拉取 Qualcomm 候选、Kconfig 通过、Ubuntu Clang 14 编译 `rtmutex.o` |
| **2026-10-10** | Actions #38052323798、#38053251640 | 配置差异与 compiler drift 复核；确认候选引入非原厂功能 |
| **2026-10-10** | Actions [Android Clang11 审计](../.github/workflows/p780-clang11-audit.yml) #38053176845 | **首次使用匹配原厂 Clang 11.0.2** 编译 `rtmutex.o` 成功；原有配置值变化 0，消失24、新增322；仍非原厂 `vmlinux` |
| **2026-10-10** | 新建本私有仓库，保存所有可归档研究产物 | 从易丢失的聊天记录迁移到可追踪的 Git 历史 |
| **2026-10-10** | [Actions #38054396216](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38054396216) 将编译资料永久入 Git | Clang11、Clang14 配置、日志、对象与差异报告均已保存于 `evidence/actions/` |
| **2026-10-10** | 机主补传 GhostLock v0.1—v0.4 和 Tracefs 原件 | 4 个 ZIP 与 4KB `p780-cpu4.raw` 全部保存；[验收 #38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285) 检查 CRC、SHA、内嵌证据的字节一致性 |
| **2026-10-10** | 最终文件与文档收敛 | 整理 `evidence/`、修复早期“待上传”状态、记录 v0.4 README 仍误标 v0.3 的原件瑕疵；Root / BL 解锁仍未达成 |

## 重要警告

- “2026-10-04 去预装实验”会改变 Android 用户 0 的包状态；恢复出厂后数值可能改变。不要将不同日期观察的包数认为同一时间。
- “源码已包含旧错误模式”和“实机成功 Root”没有逻辑等价关系。
- “EDL 已识别”不等于 Firehose Loader 已通过鉴权；“源码已编译”不等于固件镜像已匹配。

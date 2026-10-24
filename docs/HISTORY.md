# 研究时间线（据可复查材料重建）

> 此时间线只记录能从已保存报告、文件元数据、终端片段或 GitHub Actions 回溯的事项。若仅有摘要而无原始日志，会明确写“历史记录”。日期统一按相关报告日期，不杜撰精确小时。

| 日期 | 阶段与资料 | 实际结果 |
| **2026-10-24** | IPsec diagnostics v0.3.0 file-backed sendfile 预检 | native probe 与 APK CI 构建 success；尚未在设备运行，不能作为实机 PASS。见 [v0.3 报告](research/p780-dirtyfrag-v03-sendfile-probe-20261024.md)。 |
| **2026-10-24** | IPsec diagnostics v0.2.0 实机回环 | 普通 UDP 与一个 UDP-encapsulated ESP transport 数据报均在 127.0.0.1 PASS；测试后 dumpsys ipsec 相关资源计数为 0。仅证明正常 API 回环，不证明 DirtyFrag；见 [实机报告](research/p780-ipsec-v0.2-live-loopback-20261024.md) 与 [路径覆盖分析](research/p780-dirtyfrag-v02-path-interpretation-20261024.md)。 |
|---|---|---|
| **2026-06-12** | 最早保存的 P780 EDL / Sahara / Fastboot 资料；`Rakuten_Hand_5G_P780_EDL_重要数据.txt` | 提取固件号、fastboot locked、unlock 指令返回 unknown command、EDL 05C6:9008 / Sahara v2 / HWID；Firehose 不通 |
| **2026-10-03 ～ 10-04** | ADB `getprop`、`fastboot getvar all`、`by-name`、`mount`、`df`、`lshal`、包清单；未联网/恢复出厂环境下的部分清理 | OEM unlocking 灰色；固件 264 / 安全补丁 2024-02-01；A/B UFS 分区事实归档 |
| **2026-10-04** | 系统应用与去预装实验；`hand5g_debloat_p780.ps1` 和保留基础电话功能的 `hand5g_debloat_daily_phone.ps1` | 历史记录：第一轮安装包 `302→242`，后来壁纸/屏保与其他清理后复查 `157` 包。数字为不同时间点快照，不能串成单次自动结果 |
| **2026-10-04** | `QAS_DVC_MSP.apk`、`xrvdservice.apk`、PFM/Mink/TZService APK 和 JNI 库静态分析、相关运行日志 | 识别 eMBMS PFM class 119/feature 700、XRVD 2100；XRVD 创建 IPFM 代理；没有发现 OEM Unlock 路径 |
| **2026-10-04** | `hand5g_update_activity.txt`、`hand5g_update_log.txt`、`hand5g_bugreport.zip` | 历史采集材料现已入 Git；2026-10-10 后续审计见下方时间线；**不声称获取到 OTA 包** |
| **2026-10-10** | 实机 `p780-config.gz`、`p780-cpu4.raw`、Tracefs 原始事件与模块读取测试；GhostLock v0.1–v0.4 工作包 | 配置满足 Futex PI/RT Mutex；追踪见候选地址；`/vendor/lib/modules` 可列但 SELinux 下无法读模块内容；GhostLock 未执行成功 |
| **2026-10-10** | TINNO P780 5.4.61 旧源码；Qualcomm A52s 5.4.233 候选源码；Kconfig 文件比对 | 旧源码存在 CVE 类似代理锁清理模式；不能推出运行中 5.4.233 有漏洞。候选源码含更多 HOLI/BLAIR 平台配置 |
| **2026-10-10** | GitHub Actions [首次](../.github/workflows/p780-kernel-audit.yml) 编译（#38051600739） | 拉取 Qualcomm 候选、Kconfig 通过、Ubuntu Clang 14 编译 `rtmutex.o` |
| **2026-10-10** | Actions #38052323798、#38053251640 | 配置差异与 compiler drift 复核；确认候选引入非原厂功能 |
| **2026-10-10** | Actions [Android Clang11 审计](../.github/workflows/p780-clang11-audit.yml) #38053176845 | **首次使用匹配原厂 Clang 11.0.2** 编译 `rtmutex.o` 成功；原有配置值变化 0，消失24、新增322；仍非原厂 `vmlinux` |
| **2026-10-10** | 新建本私有仓库，保存所有可归档研究产物 | 从易丢失的聊天记录迁移到可追踪的 Git 历史 |
| **2026-10-10** | [Actions #38054396216](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38054396216) 将编译资料永久入 Git | Clang11、Clang14 配置、日志、对象与差异报告均已保存于 `evidence/actions/` |
| **2026-10-10** | 机主补传 GhostLock v0.1—v0.4 和 Tracefs 原件 | 4 个 ZIP 与 4KB `p780-cpu4.raw` 全部保存；[验收 #38055530285](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38055530285) 检查 CRC、SHA、内嵌证据的字节一致性 |
| **2026-10-10** | 最终文件与文档收敛 | 整理 `evidence/`、修复早期“待上传”状态、记录 v0.4 README 仍误标 v0.3 的原件瑕疵；Root / BL 解锁仍未达成 |
| **2026-10-10** | 机主追加上传早期 Android/ADB 研究资料 | 收到审计 ZIP、Bugreport、OTA/TEE 日志和三份 APK；完整比对 22+9 个展开文件与原 ZIP 的内容，发现逐文件相同、移除重复副本；保留 [清理前备份分支](https://github.com/Chuniex-0631/p780-kernel-research/tree/archive/pre-cleanup-20261010) |
| **2026-10-10** | 新证据专题与安全审阅 | [新增资料审计](archive/20261010-import-dedup.md)、[TEE/APK](research/tee-system-apks.md)、[OTA/Bugreport](research/ota-bugreport.md) 分别记录，有敏感风险的原件分类归档，未据此宣称 Root 或固件获取成功 |
| **2026-10-10** | 候选配置/布局最终 run 38060518994 | 两棵固定树各 32 项、0 差异，实机适配仍 BLOCKED |
| **2026-10-10** | OTA 与 Bugreport 深入审计、实机 framework 采集 | 6 份历史引擎日志只见启动清理；Journey HTTP/XML 应用策略链定位 |
| **2026-10-10** | vendor 配置与无参数 TCS 状态核对 | 三处版本 42；64 个策略键按 ALL 假设完整匹配，0 差异 |
| **2026-10-11** | Journey 性能消费者静态核对 | 134 方法、79 条外部引用/25 个调用者方法；进程管理/Service/Provider 策略，无新 Root/OTA 链 |
| **2026-10-11** | 全库结构整理与研究待机 | 主题/参考/历史分层，证据归位、链接更新；当时记录监测已启用；当前任务运行状态须另查 |
| **2026-10-14～17** | AVB公告归因与XDA正文补档 | 官方测试钥匙问题与第三方Recovery失败记录分开，不据此宣称P780写入可行 |
| **2026-10-18** | AVB基线、fstab与Key Attestation | TEE公钥摘要匹配AOSP默认测试根；fstab已读；真实vbmeta/boot原件仍缺 |
| **2026-10-18** | Google OTA Prober | 正确264 fingerprint单次查询无URL；暂停重复探测 |
| **2026-10-18** | GSI A/B Windows离线实验 | 原始A保留，测试根B验签通过；数据段一致性来自机主PC输出 |
| **2026-10-18** | B安装/启用/重启后回退 | 最终原厂Android11、Locked/green、installed/disabled；失败阶段未知 |
| **2026-10-18** | 恢复出厂后原生Loader回退；机主停止DSU | 后一次为用户观察，镜像身份未核实；不作为严格A组复测 |
| **2026-10-18** | 广覆盖静态采集与策略分析 | 1759项清单；batch1 742项、batch2 514项匹配；55份策略设备文件及日志，shell debug_prop静态候选 |
| **2026-10-18** | native接口交叉与全库整理 | 区分客户端/服务端；36项策略查询；重写当前入口、归档逐轮账本、标识DSU历史；无新增Root/解锁能力 |
| **2026-10-19** | Windows EDL通信复测；bkerler/edl v3.62 COM模式无初始HELLO，局部串口补丁仍失败 | QDL v2.8 QUD/COM6 成功查询 Sahara v2 芯片身份；后续候选 A 四次 READ64 请求后通信失败，未见 DONE/Firehose。见[专题](research/p780-qdl-qud-sahara-20261019.md) |

| **2026-10-19** | Mannar A–E 共5文件离线证书矩阵完成 | B–E 在独立脚本副本中禁用去重后得到完整解析；A/B/C 为 d935 根，D为4352根，E为a51a根，全部与本机c19a根不符。B–E 未实机测试。见[专题](research/p780-qdl-qud-sahara-20261019.md) |

## 重要警告

- “2026-10-04 去预装实验”会改变 Android 用户 0 的包状态；恢复出厂后数值可能改变。不要将不同日期观察的包数认为同一时间。
- “源码已包含旧错误模式”和“实机成功 Root”没有逻辑等价关系。
- “EDL 已识别”不等于 Firehose Loader 已通过鉴权；“源码已编译”不等于固件镜像已匹配。



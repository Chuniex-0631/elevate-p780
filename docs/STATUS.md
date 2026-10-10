# 研究状态总表（更新：2026-10-10）

本仓库存档长期围绕 **Rakuten Hand 5G / TINNO P780** 进行的个人设备实验。证据有明确等级：**实机已证实 / 离线源码或文件已证实 / 其他设备参考 / 未验证假设**。不同等级不能互相替代。

| 目标 | 结果 | 依据及边界 |
|---|---|---|
| 确认型号、固件、内核版本 | **实机已证实** | Android 11; `P780AE_11.0_RMN_JP_162`; Linux `5.4.233-qgki-gea5245e94afe-dirty` |
| 获取 ADB Shell / 原厂配置 | **实机已证实** | 非 root shell; 39,170 B `p780-config.gz` 在仓库根目录 |
| Fastboot OEM 解锁 | **未成功** | Unlock 标志 no；标准 unlock 命令返回 unknown command；灰色 OEM 开关 |
| EDL / Sahara 识别 | **实机已证实** | 05C6:9008; Sahara v2; `mannar` / HWID `0x0016f0e100000780` |
| Firehose 握手、分区备份/读写 | **尚无成功证据** | 已识别 loader 匹配需求，不代表已找到可用签名 Loader |
| 以 EDL 获得 `boot.img` | **未取得** | 从未将未知 loader/跨设备镜像作为成功证据 |
| QAS → Mink → PFM | **静态 + 部分实机运行已证实** | eMBMS `open(119)`, `CheckInstalledLicense(700)`；XRVD 代理创建日志；没有 OEM Unlock 连接证据 |
| TZAccessService 白名单/凭据 | **APK 静态已证实** | 调用 Binder UID/PID；白名单 `/vendor/etc/ssg/tz_whitelist.json`；native/backend 未完整审计 |
| TINNO 5.4.61 `rtmutex` CVE 调用链 | **公开旧源码已证实** | **不等于**设备运行中的 5.4.233 已证实存在漏洞 |
| Futex PI、RT Mutex、LTO、CFI 等 | **实机配置已证实** | `CONFIG_FUTEX_PI=y`, `CONFIG_RT_MUTEXES=y` |
| Tracefs 原始数据可读和标记 | **实机已证实 / 原件已归档** | [原件](../evidence/device/p780-cpu4.raw) 4,096 B，已核验标记与 SHA；候选地址不等于 `_text` |
| GhostLock v0.1—v0.4 工作包归档 | **原始 ZIP 已校验** | [四个 ZIP](../evidence/ghostlock) 的 CRC 均通过；版本报告、检查工具与同源内嵌证据已存档 |
| P780 专用 GhostLock 可执行链 | **BLOCKED** | 缺原厂二进制/逐构建结构及符号偏移；未实现 Root |
| Qualcomm 5.4.233 候选源码原生 Kconfig | **云端构建成功** | GitHub Actions 2026-10-10 的 5.4.233 *A52s* 源码、非 P780 固件 |
| Android Clang 11.0.2 `rtmutex.o` | **云端编译成功** | 已匹配实机编译器，非完整 `vmlinux`，非可刷写内核 |
| 还原与出厂 `vmlinux` 一致的内核 | **未完成** | 原厂私有代码与构建身份未满足 |
| JourneyConfigService | **静态与运行状态核对已完成** | vendor/XML/TCS 版本均 42；64 键一致；消费者静态定位进程管理与 Service/Provider 限制；未发现 OTA/Root 链 |
| Root / Bootloader 解锁 / 刷机 | **均未达成** | 任何适配包不得宣称 Root 成功 |

## 新增历史原件（2026-10-10）

- 新上传两份 ADB 审计 ZIP（22 和 9 条目），与其展开目录逐字节相同；删除 31 个冗余展开副本，保留原始 ZIP 与清理前备份分支。
- 新增三份 APK、TEE 白名单和 JNI 访问失败记录、两份 OTA 系统日志及完整 Android Bugreport ZIP。
- `hand5g_tz_whitelist.txt` 实测含 class-ID 119（Platform Feature Management）；不意味着允许绕过其它身份/签名检查。
- OTA 日志和 Bugreport 是**原始取证材料**，目前尚未确认下载到完整 OTA / `payload.bin`；原件可能带隐私信息。
- 这些新增证据和实际移动/去重明细见 [NEW_UPLOADS_AND_DEDUP](NEW_UPLOADS_AND_DEDUP.md)。

## 最新可靠数字

- 设备真实 `config.gz` 解析：**5,238** 个状态明确的配置项，源文件 6,576 行。
- Qualcomm 5.4.233 候选 + **匹配的 Android Clang 11.0.2** 的原生 Kconfig：原有值变化 **0**；消失 **24**；新增 **322**。`rtmutex.o` 成功编译；没有完整内核链接。
- 上述被删除的 24 项里包含 **15 项原本启用**的驱动/防护选项（已逐项扫描两棵固定源码，见本轮配置/布局专题）。
- 旧 TINNO 5.4.61 源码包对照的 45 项缺失只是**不同源码树的静态比较**，不可与 Clang11 的 24 项混为一谈。

## 认识论规则

- 现场软件状态来自具体采集时间；去预装、重启、切槽后不得自动延用以前记录。
- **能 `adb shell` 查看文件名，不代表可 `adb pull` 读取内容。**
- **构建成功不等于原厂固件、没有证据的 kernel 地址不能进入真实设备写入操作。**
- 本库已有 `docs/2026-09-28-rakuten-hand5g-firmware-advisory.md`，该官方安全提示涉及固件真实性验证，独立于 GhostLock；公开提示不等于已发现或验证 Bootloader 解锁途径。
- 重要的 Clang11、Clang14 和配置差异产物现已保存在仓库 [evidence/actions](../evidence/actions)，不再只依赖短期 Actions Artifact；哈希与原始研究包校验见 [完整性报告](EVIDENCE_INTEGRITY.md)。

## 归档范围

- 2026-10-10 最终核查：**四份原始 GhostLock ZIP + 一份原始 Tracefs 数据**已在 `evidence/` 保存，SHA-256/CRC 全部校验通过；工作包的内置配置和 Tracefs 与主原件逐字节一致。
- 此后的新增上传已使 **Bugreport、三份 APK、两轮 ADB 审计 ZIP、OTA 日志和 TEE 文件**进入 GitHub 私有仓库。它们仍是未经发布级隐私审查的原始记录，按 [导入报告](NEW_UPLOADS_AND_DEDUP.md) 分组；另有部分历史文件仍仅在个人文件库。


这里汇总了**已能从历次对话、历史文件库和 GitHub 中重新取得的资料**。并不假装取得所有过去的原始终端输出、未上传的 `boot.img` 或缺失的编译产物。细节参见 [证据索引](EVIDENCE_MANIFEST.md)。


## 2026-10-10：配置语义与布局继续研究

- [24 项配置与候选布局研究](2026-10-10-config-layout-research.md)：24 项完成源码引用核对，15 项原本启用。
- 5 项在两棵公开源码均未命中（4 项实机启用）；5 项仍有候选 Kconfig 定义；14 项候选无同名定义。
- FORTIFY_SOURCE 属 Clang 依赖限制；REFCOUNT_FULL 无开关不代表饱和保护消失。
- 最终 Actions #38060518994 全部通过：两棵固定树分别提取 32 项布局事实，32 项全部一致，prepare 配置漂移 0。TINNO 原生求解消失 46 / 新增 14；A52s 消失 24 / 新增 322。
- 原始日志、编译命令、配置和候选 JSON 已永久入 evidence/actions/2026-10-10-layout-audit。仅为候选源码 ABI 采样；Root/BL 状态不变，GhostLock 仍 BLOCKED。

## 当前系统配置支线

[Journey 实机 JAR 审计](2026-10-10-journey-config-audit.md)：54 个目标方法原始指令、8 类反汇编、6 DEX 的 17 个外部引用已保存。新增消费者 134 方法、79 条外部引用（25 个调用者方法），核实末尾星号前缀匹配与精确键查询的差别；优化开关是否启用未实测。HTTP 配置在所审查路径未见密码学验签，仅见主机/版本检查；静态发现不能宣布权限获取。vendor 默认 XML 与无参数 TCS dump 已核对：三处版本均 42，64 个映射键按 ALL 假设完全一致；重复键为覆盖而非行为合并。完整原始配置 ZIP 以可还原 Base64 文本及 SHA 入仓，详见专题。

[OTA 原件深入审计](2026-10-10-ota-log-audit.md)：全部 6 份历史引擎日志仅为启动清理，无固件 URL/payload；此前的配置成功、INSTALL_UPDATE 事件不作 OTA 安装成功。原始新上传 18MB framework ZIP/JAR 仍在机主上传文件，本仓库保存来源 SHA 与提取证据，未冒称原件已入 Git。

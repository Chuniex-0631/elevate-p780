# 研究状态总表（更新：2026-10-18）

2026-10-18 取得本机 P780 Key Attestation：**TEE / Google 根证书签名链核验通过，证实 AVB 默认测试公钥身份**，不再等待原厂镜像才能确认根钥匙。已开展 P780 实机 DSU/GSI 支线：**开发者选项中 DSU Loader 入口已确认存在**，`gsi_tool`、`gsid.rc` 均存在，`pm list packages -u` 可以找到 `com.android.dynsystem` 包记录；曾实测 user0 `installed=false`；**随后机主通过 `install-existing --user 0` 恢复成功，现已验证 `installed=true` 且 `pm path` 找到原厂 APK**；最新第五轮实机确认 VNDK30、ARM64 和用户数据存储报告可用 103G；**第六轮又实测 `ro.treble.enabled=true`、`[vendor] namespace.default.isolated=true`**，故官方 Treble/VNDK 跨版本前置检查已满足；具体 GSI 公钥和真正启动仍未知。[源码交叉报告](research/p780-dsu-locked-gsi-20261018.md)。当前研究进入 AVB 只读取证阶段，保留公开新线索监测；不涉及刷机、Root 或更改 Bootloader。读取入口见 [文档导航](README.md)，结构验收见 [全库整理](REPOSITORY_AUDIT.md)。

本仓库存档长期围绕 **Rakuten Hand 5G / TINNO P780** 进行的个人设备实验。证据有明确等级：**实机已证实 / 离线源码或文件已证实 / 其他设备参考 / 未验证假设**。不同等级不能互相替代。

| 目标 | 结果 | 依据及边界 |
|---|---|---|
| 确认型号、固件、内核版本 | **实机已证实** | Android 11; `P780AE_11.0_RMN_JP_162`; Linux `5.4.233-qgki-gea5245e94afe-dirty` |
| 获取 ADB Shell / 原厂配置 | **实机已证实** | 非 root shell; 39,170 B `p780-config.gz` 在 evidence/device/ |
| Fastboot OEM 解锁 | **未成功** | Unlock 标志 no；标准 unlock 命令返回 unknown command；灰色 OEM 开关 |
| EDL / Sahara 识别 | **实机已证实** | 05C6:9008; Sahara v2; `mannar` / HWID `0x0016f0e100000780` |
| 固件真实性 / AVB 测试钥匙 | **官方公告 + P780 `_162` 可信 TEE 独立密码学验证成功** | [JVN#47427200](https://jvn.jp/jp/JVN47427200/) / CVE-2026-107153；本机 Google 硬件证明 `verifiedBootKey` 精确匹配 AOSP 默认 AVB RSA4096 测试公钥 SHA256(1032B AVB blob)，`verifiedBootHash` 精确匹配旧 ADB VBMeta Digest。仍无 locked 写入通道，未 Root/解锁；[实证报告](research/avb-attestation-confirmed-20261018.md) |
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
| DSU/GSI 临时系统（LOCKED） | **两次 DSU 专用重启已由系统历史证实；GSI 已安装未运行；Bugreport 无 LAST KMSG；根因仍未查明** | 用户上传完整有效Bugreport ZIP 362成员/主TXT约19.7MB；`persist.sys.boot.reason.history`两项 `reboot,dynsystem` 对应UTC+8 06:30:31/06:31:30；`gsid.image_installed=1`、`ro.gsid.image_running=0`，原厂B槽dm映射。`dumpstate` `/proc/last_kmsg` 不存在、incidentd pstore两路径与last_kmsg均打不开、LAST LOGCAT失败；当前dmesg首记录开机943秒后，不能还原first-stage DSU失败。停止重复重启与无效日志采集；转向 `_162` boot ramdisk/DSU公钥离线证据，**并未证明AVB不匹配、也没成功启动 GSI/获得 Root/解锁**。[第十三轮审计](research/p780-dsu-bugreport-audit-20261018.md) |
| Root / Bootloader 解锁 / 刷机 | **均未达成** | 任何适配包不得宣称 Root 成功 |

## 2026-10-18：AVB 锁定状态下的实机基线（用户提供）

- `ro.boot.verifiedbootstate=green`；`ro.boot.vbmeta.device_state=locked`；`ro.boot.flash.locked=1`；活动槽为 `_b`。
- `ro.boot.vbmeta.digest=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`。这是包括链式 VBMeta 的校验基线，**不是**测试公钥的指纹；只据此不能确定具体 AVB 测试密钥。
- 新增 [AVB 实机取证与离线校验专题](research/avb-live-baseline-20261018.md) 与 [PowerShell ADB 只读采集脚本](../tools/p780-avb-readonly.ps1)。尚未获得 `vbmeta_b` 原始镜像，locked 写入通道仍未知，Root/BL 状态不变。

## 2026-10-18：AVB 第二轮只读实测

- 用户提供 `ro.boot.vbmeta.hash_alg=sha256`、`ro.boot.vbmeta.size=7744` 字节、`ro.boot.avb_version=1.1`。AOSP libavb 代码核实 7744 是**本次加载的 VBMeta 结构总长度**，不是单个分区大小。
- 当前槽 B 的软链接：`vbmeta_b→sde31`、`vbmeta_system_b→sda11`、`boot_b→sde28`、`vendor_boot_b→sde36`、`dtbo_b→sde32`、`super→sda9`；完整双槽名称对应记录在 [AVB 基线专题](research/avb-live-baseline-20261018.md)。
- `vbmeta_system_b` 为 **候选链式 VBMeta**，尚未获得真实分区内容/签名描述符。两级链关系、AVB 公钥指纹、rollback index 和锁定态写入路径仍待证实。
- GitHub API 已再次确认项目 `visibility=private`；继续按 [SECURITY](../SECURITY.md) 约束未脱敏系统日志。

## 2026-10-18：AVB 第三轮只读实测

- 公钥摘要属性为空（**不代表没有公钥**）；`ro.boot.vbmeta.avb_version=1.0` 对应 Bootloader libavb，上轮 `ro.boot.avb_version=1.1` 对应 Android 侧 libavb；AOSP 已解释二者并不矛盾。
- `ro.boot.veritymode=enforcing`；`vbmeta_b` 与 `vbmeta_system_b` 对应目标块设备分别为 `/dev/block/sde31` 和 `/dev/block/sda11`，权限均为 `brw------- root:root`，当前非 root ADB Shell 无法直接读取这些镜像。
- `system_b/system_ext_b/product_b/vendor_b/odm_b` 分别映射 dm-0 至 dm-4；`system_b-cow→dm-5`；五个 `*-verity` 分别 dm-6 至 dm-10。COW 线索不等于正在 OTA 或发现绕过途径。
- 进一步证据边界与下轮查询见 [AVB 专题](research/avb-live-baseline-20261018.md)。`_162` 镜像、公钥指纹和锁定态写入入口仍未取得；Root/BL 状态未变。

## 2026-10-18：AVB 第四轮属性核查与取证收束

- 用户实机 `ro.boot.dynamic_partitions=true`：明确确认动态分区；`ro.virtual_ab.enabled`、`ro.virtual_ab.compression.enabled`、`ro.boot.vbmeta.device` 均为空。**空属性不能视为否定 Virtual A/B 或 VBMeta 的证据**。
- 根据 AOSP，Android 11 Virtual A/B 使用 kernel COW，压缩快照支持出现于 Android 12；`system_b-cow` 与此前观察相符，但**只记录为候选线索，不写成已证明正在 OTA、快照合并或写入漏洞**。
- 本阶段结束常规 getprop 再采集，后续优先查找可信匹配 `_162` 的 OTA/分区镜像和 P780-specific locked 写入通道。见 [AVB 实机专题](research/avb-live-baseline-20261018.md)。

## 2026-10-18：跨线索研究发现（未实机验证）

- 从 AOSP [Keystore attestation](https://source.android.com/docs/security/features/keystore/attestation) 与 Android CTS 交叉发现：硬件 RootOfTrust 可能含 `verifiedBootKey` 公钥哈希与 `verifiedBootHash` VBMeta 摘要，普通 Android 应用可请求。**用户当前只运行过 getprop、ls；从未获得该 Attestation，不能记为成功。**
- 从 [AOSP 动态分区规则](https://source.android.com/docs/core/ota/dynamic_partitions/implement) 得知，fstab 的 `avb=<partition>` 可提供系统逻辑分区所使用 VBMeta 的挂载配置线索，未能替代原始签名描述符。
- 研究方法、可选应用、隐私和强制可信链验证见 [新专项](research/avb-attestation-alternative-20261018.md)。**本机 Root/BL/镜像/匹配 EDL Loader 均无新成功证据**。

## 2026-10-18：Google OTA Prober 交叉验证线索

- 用户实机：`ro.build.fingerprint=Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`；`/vendor/etc/fstab.default` 与 `fstab.emmc` 存在，`fstab.qcom` 不存在。前两份配置内容尚未读取。
- 审阅 [google-ota-prober](https://github.com/tangalbert919/google-ota-prober) `probe.py`：向 Google Check-in 请求 `update_url`。该项目没有 Universal OEM OTA 能力；本机是否采用此 OTA 服务器未知。
- 公开 archive 中发现 Tinno 制造的 Rakuten Mini C330 两条真实 Google OTA 元数据与 Tinno/Rakuten P710 fingerprint（该型号未归档 OTA），**未找到 P780 OTA 索引**。详见 [专题分析](research/google-ota-prober-p780-20261018.md)。没有实际对 P780 发送 Check-in、没有取得固件或 root。

## 2026-10-18：Fstab 内容解析 + Google OTA CLI 第一次负面结果

- **实机已观察**：`fstab.default`、`fstab.emmc` 均对 `system/system_ext/product` 使用 `avb=vbmeta_system`，而 `vendor/odm` 使用普通 `avb`；`system` 行列出 `q-gsi/r-gsi/s-gsi.avbpubkey` 供 GSI 验证。与之前发现的 B 槽 `vbmeta_system_b` 和 dm-verity 映射一致，但无法由 fstab 单独证明 Bootloader 的链式签名 descriptor 或 AVB 生产根密钥；GSI 公钥不得混同。两份文件区别在 userdata 加密配置，实际被 first-stage mount 采用哪份尚未证明。
- **实机附属电脑已执行**：在 `google-ota-prober` CLI 传入正确 `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`、`--model P780`，返回 `No OTA URL found for your build`。**只有这一查询没返回 URL**，无法区分当前最终版无更新/Google 服务不认机型/其它服务端限制；无 HTTP 状态与 P780 镜像。无需重复同一查询。
- 见 [AVB Fstab 专题](research/p780-fstab-avb-20261018.md)、[Google OTA Prober 专题](research/google-ota-prober-p780-20261018.md)。下一实质无原厂镜像的验证项仍是 Key Attestation；设备保持 locked、未 Root。

## 新增历史原件（2026-10-10）

- 新上传两份 ADB 审计 ZIP（22 和 9 条目），与其展开目录逐字节相同；删除 31 个冗余展开副本，保留原始 ZIP 与清理前备份分支。
- 新增三份 APK、TEE 白名单和 JNI 访问失败记录、两份 OTA 系统日志及完整 Android Bugreport ZIP。
- `hand5g_tz_whitelist.txt` 实测含 class-ID 119（Platform Feature Management）；不意味着允许绕过其它身份/签名检查。
- OTA 日志和 Bugreport 是**原始取证材料**，目前尚未确认下载到完整 OTA / `payload.bin`；原件可能带隐私信息。
- 这些新增证据和实际移动/去重明细见 [NEW_UPLOADS_AND_DEDUP](archive/20261010-import-dedup.md)。

## 最新可靠数字

- 设备真实 `config.gz` 解析：**5,238** 个状态明确的配置项，源文件 6,576 行。
- Qualcomm 5.4.233 候选 + **匹配的 Android Clang 11.0.2** 的原生 Kconfig：原有值变化 **0**；消失 **24**；新增 **322**。`rtmutex.o` 成功编译；没有完整内核链接。
- 上述被删除的 24 项里包含 **15 项原本启用**的驱动/防护选项（已逐项扫描两棵固定源码，见本轮配置/布局专题）。
- 旧 TINNO 5.4.61 源码包对照的 45 项缺失只是**不同源码树的静态比较**，不可与 Clang11 的 24 项混为一谈。

## 认识论规则

- 现场软件状态来自具体采集时间；去预装、重启、切槽后不得自动延用以前记录。
- **能 `adb shell` 查看文件名，不代表可 `adb pull` 读取内容。**
- **构建成功不等于原厂固件、没有证据的 kernel 地址不能进入真实设备写入操作。**
- [固件真实性专题](research/firmware-advisory-20260928.md) 已纳入 2026-10-14 发布的 JVN#47427200 / CVE-2026-107153：Hand 5G 全版本的 AVB 使用已知 AOSP 测试钥匙。该结论独立于 GhostLock；JVN 明确的是信任钥匙缺陷，不是 P780 专用刷写入口或 Bootloader 解锁成果。
- 重要的 Clang11、Clang14 和配置差异产物现已保存在仓库 [evidence/actions](../evidence/actions)，不再只依赖短期 Actions Artifact；哈希与原始研究包校验见 [完整性报告](reference/evidence-integrity.md)。

## 归档范围

- 2026-10-10 最终核查：**四份原始 GhostLock ZIP + 一份原始 Tracefs 数据**已在 `evidence/` 保存，SHA-256/CRC 全部校验通过；工作包的内置配置和 Tracefs 与主原件逐字节一致。
- 此后的新增上传已使 **Bugreport、三份 APK、两轮 ADB 审计 ZIP、OTA 日志和 TEE 文件**进入 GitHub 私有仓库。它们仍是未经发布级隐私审查的原始记录，按 [导入报告](archive/20261010-import-dedup.md) 分组；另有部分历史文件仍仅在个人文件库。


这里汇总了**已能从历次对话、历史文件库和 GitHub 中重新取得的资料**。并不假装取得所有过去的原始终端输出、未上传的 `boot.img` 或缺失的编译产物。细节参见 [证据索引](EVIDENCE_MANIFEST.md)。


## 2026-10-10：配置语义与布局继续研究

- [24 项配置与候选布局研究](research/config-layout.md)：24 项完成源码引用核对，15 项原本启用。
- 5 项在两棵公开源码均未命中（4 项实机启用）；5 项仍有候选 Kconfig 定义；14 项候选无同名定义。
- FORTIFY_SOURCE 属 Clang 依赖限制；REFCOUNT_FULL 无开关不代表饱和保护消失。
- 最终 Actions #38060518994 全部通过：两棵固定树分别提取 32 项布局事实，32 项全部一致，prepare 配置漂移 0。TINNO 原生求解消失 46 / 新增 14；A52s 消失 24 / 新增 322。
- 原始日志、编译命令、配置和候选 JSON 已永久入 evidence/actions/2026-10-10-layout-audit。仅为候选源码 ABI 采样；Root/BL 状态不变，GhostLock 仍 BLOCKED。

## 当前系统配置支线

[Journey 实机 JAR 审计](research/journey-config.md)：54 个目标方法原始指令、8 类反汇编、6 DEX 的 17 个外部引用已保存。新增消费者 134 方法、79 条外部引用（25 个调用者方法），核实末尾星号前缀匹配与精确键查询的差别；优化开关是否启用未实测。HTTP 配置在所审查路径未见密码学验签，仅见主机/版本检查；静态发现不能宣布权限获取。vendor 默认 XML 与无参数 TCS dump 已核对：三处版本均 42，64 个映射键按 ALL 假设完全一致；重复键为覆盖而非行为合并。完整原始配置 ZIP 以可还原 Base64 文本及 SHA 入仓，详见专题。

[OTA 原件深入审计](research/ota-log-audit.md)：全部 6 份历史引擎日志仅为启动清理，无固件 URL/payload；此前的配置成功、INSTALL_UPDATE 事件不作 OTA 安装成功。原始新上传 18MB framework ZIP/JAR 仍在机主上传文件，本仓库保存来源 SHA 与提取证据，未冒称原件已入 Git。


## 2026-10-11 官方源码申请进展

已向 TINNO `Sales@tinno.com` 发送与 P780 `_162` 固件对应的 GPL kernel 源码请求，要求转交工程/合规团队；Gmail 返回 SENT，待回复。Rakuten 尚未联系成功，因未验证到专用公开邮箱，日文客服转交请求见 [联络记录](official-source-request-log.md)。


## 2026-10-14：JVN / CVE 技术归因

- JVN 与 JVN iPedia 将此前 Rakuten 的“固件真实性验证缺陷”具体化为：AVB 使用已知 AOSP 测试钥匙，影响 **Rakuten Hand 5G 全部版本**；编号为 **JVN#47427200 / JVNDB-2026-000147 / CVE-2026-107153 / CWE-1391**。
- JVN 评分为 CVSS v4 7.0、v3 6.6，攻击向量为物理访问、低权限、无需用户交互；厂商没有修补方案，建议停用并更换后续产品。
- JVN 引用的 2025 年论文说明通用链路：取得原厂镜像、修改并用公开测试钥匙重签、重建 vbmeta、再通过设备特定通道写入。论文的实机演示机型不是 P780，并明确写入路径依设备而异、公开可用者只占少数。
- 因此本机状态仍是 **locked / 未 Root**。要把该缺陷转化为 P780 可复核成果，仍至少缺 `_162` 的 boot/vbmeta 等原厂镜像及一个经验证的锁定态写入通道；现有 Fastboot 命令失败、匹配 Firehose 未取得。

## 2026-10-17：XDA 正文补档

用户提供 XDA 4805241 正文；已关闭同一正文获取提醒。作者报告 EDL 可达、Recovery ADB 受限和测试 ZIP 验签失败，均属未独立复核的第三方叙述；无构建号及测试原件，不能登记为本机 `_162` 实测。OTA 证书 testkey 与 AVB 测试钥匙不得混同；失败只支持该包未通过该次验签。原件、签名方式及 Recovery 信任钥匙仍缺，详见 [专题](research/firmware-advisory-20260928.md)。原厂镜像/匹配 Loader/锁定态通道仍为优先缺口，未 Root、未解锁。

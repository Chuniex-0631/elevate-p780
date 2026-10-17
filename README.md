# Rakuten Hand 5G / TINNO P780 研究档案

**2026-10-18 DSU 第九轮：** 已对 Google 六份 DSU 目录24项镜像完成独立核验，全部缺可选 `vndk/pubkey` 元数据；新从公开 AOSP Android11 源码分别获取并计算**普通 GSI q/r/s 与 Developer GSI q/r/s 六把 AVB RSA4096 公钥**（1032B）的 SHA-256，六者互异且均非 P780 已证实的 AVB 测试根公钥。P780 fstab 指向**普通 q/r/s GSI** 路径，而非 Developer-GSI。AOSP 源码确认 JSON 筛选与 first-stage **真实验签**分离；**设备 Ramdisk 原始公钥、Android15/16 镜像实际签名仍缺**。鉴于 Google 公布 GSI 启动失败可能需要擦除 userdata，目前不建议下载/安装。Bootloader 仍 LOCKED、无 Root。[第九轮信任链报告](docs/research/p780-dsu-trust-chain-audit-20261018.md) · [研究计划](docs/NEXT_STEPS.md)。

**2026-10-18 重大实机验证：P780 `_162` 的 Android Key Attestation 由 Google 官方硬件证明根签署，TEE 证明已核验；`verifiedBootKey` 精确匹配 AOSP `testkey_rsa4096_pub.pem` 经 AVB 专用编码得到的 SHA-256。`verifiedBootHash` 同样精确匹配既有本机 VBMeta Digest。** 这将官方已公布的默认测试钥匙漏洞升级为对本机公钥身份的独立密码学证明，但**尚无 Root、Bootloader 解锁或 locked 写入通道**。[脱敏验证与证据](docs/research/avb-attestation-confirmed-20261018.md)。原始 `.p7b` 未上传仓库。

**官方源码请求（2026-10-11）：** 已向 TINNO 官网页面列出的海外销售邮箱发送 P780 `_162` 对应 GPL 源码申请并要求转交专业团队；Rakuten Mobile 的日文请求稿待通过官网客服渠道提交。详见 [联络记录](docs/official-source-request-log.md)。

截至 **2026-10-18**：已进入 AVB 只读取证，持续监测公开新线索。**未取得 Root、未解锁 Bootloader；匹配原厂 `_162` 的完整 OTA、boot.img、vmlinux 仍未取得。**

**2026-10-14 新增官方漏洞编号：** JVN 确认 Rakuten Hand 5G **全部版本**的 AVB 使用已知 AOSP 测试钥匙，登记为 [JVN#47427200](https://jvn.jp/jp/JVN47427200/) / [CVE-2026-107153](https://www.cve.org/CVERecord?id=CVE-2026-107153)。这是固件信任链的实证，但公开资料仍未给出 P780 在锁定状态下的具体写入通道，不能改写为已 Root/已解锁。

**2026-10-18 新增实机 AVB 基线：** 用户 ADB 确认 `green / locked / _b`、`sha256`、VBMeta 总长度 `7744`、AVB `1.1` 以及 `vbmeta_b` / `vbmeta_system_b` 的双槽分区；[只读记录与离线核验方案](docs/research/avb-live-baseline-20261018.md) 已更新，新增 [Windows 只读采集工具](tools/p780-avb-readonly.ps1)，未改变 Root/BL 状态。

**2026-10-18 AVB 第三轮只读进展：** ADB 确认 Bootloader/Android 侧 libavb `1.0 / 1.1`、`veritymode=enforcing`、主/系统 VBMeta 目标块设备为 `root:root 0600`、五个 dm-verity 映射和 `system_b-cow` COW 候选节点；仍未取得镜像或可验证写入通道。详见 [AVB 专题](docs/research/avb-live-baseline-20261018.md)。

**2026-10-18 第四轮 AVB 取证收束：** `ro.boot.dynamic_partitions=true`；Virtual A/B、压缩快照与 `ro.boot.vbmeta.device` 属性均为空，不能凭空值否定 AVB/Virtual A/B。暂停继续收集普通 getprop，聚焦匹配 `_162` 原厂镜像及有原始日志的 P780 锁定态写入途径。[专项证据与后续计划](docs/research/avb-live-baseline-20261018.md)。

**2026-10-17 XDA 正文补档：** 作者报告测试 ZIP 的 Recovery 验签失败；缺少原始包、签名命令和日志，不能确定信任钥匙或推翻 AVB 公告。已关闭正文获取提醒，见 [专题补充](docs/research/firmware-advisory-20260928.md)。

这是机主实体机取证、公开源码实验与历史资料的长期档案，不是刷机包或一键 Root 工具。设备基线：Android 11 / `P780AE_11.0_RMN_JP_162` / `5.4.233-qgki-gea5245e94afe-dirty`。

**2026-10-18 新的 AVB 取证方向：** 从 AOSP Keystore/CTS 发现普通应用可请求 `verifiedBootKey`（AVB 根公钥哈希）及可选 `verifiedBootHash`（可与已知 digest 核对），不必预先获得 `vbmeta_b.img`；另外可只读审计 fstab 的 `avb=vbmeta_system` 等挂载规则。这些只是**有官方依据但 P780 尚未实测的新路径**，不是已经 Root 或突破刷写权限。[交叉研究方案](docs/research/avb-attestation-alternative-20261018.md)。

**2026-10-18 OTA 新线索：** 已审阅 [Google OTA Prober](https://github.com/tangalbert919/google-ota-prober) 的真实 Check-in 逻辑；发现同 TINNO OEM 的 Rakuten Mini C330 在公开 OTA 索引中存在经记录的 Google OTA 增量包、P710 有指纹记录。**P780 尚未证实使用该服务，也尚未运行实测或取得镜像。** 用户提供当前 P780 指纹 `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`，且只找到 `fstab.default` / `fstab.emmc` 而非 `fstab.qcom`。[专题](docs/research/google-ota-prober-p780-20261018.md)。

**2026-10-18 Google OTA + Fstab 实机结果：** P780 当前 build fingerprint 首次通过 [Google OTA Prober](https://github.com/tangalbert919/google-ota-prober) 模拟 Check-in，**未返回任何 OTA URL**，不能据此证明服务器从未分发 P780 固件。用户实机已读取 `fstab.default` / `fstab.emmc`，均将 `system/system_ext/product` 指向 `avb=vbmeta_system`，`vendor/odm` 采用默认 `avb`，其中 GSI 附加公钥**并非已验证的生产根公钥**。[Fstab 专题](docs/research/p780-fstab-avb-20261018.md)；[Google OTA 专题](docs/research/google-ota-prober-p780-20261018.md)。不再要求重复执行相同指纹查询。

## 从哪里开始

1. [当前状态](docs/STATUS.md)：已证实、候选结果与阻断点。
2. [文档导航](docs/README.md)：按研究问题阅读专题。
3. [研究时间线](docs/HISTORY.md)：从 2026-06-12 到本轮整理。
4. [后续关卡与待机监测](docs/NEXT_STEPS.md)：出现什么新证据才值得重启研究。
5. [证据资产清单](docs/EVIDENCE_MANIFEST.md)：哪些原件已入 Git、哪些仍仅在上传文件中。
6. [本轮全库整理验收](docs/REPOSITORY_AUDIT.md)：目录变化、去重、恢复快照及验证范围。

## 已完成的研究

| 方向 | 当前结果 | 专题 |
|---|---|---|
| 实机与启动链 | Fastboot locked、OEM 开关灰色；Sahara/EDL 已识别，Firehose 分区读取无成功证据 | [设备与启动](docs/research/device-and-boot.md) |
| QAS / Mink / PFM / TEE | 部分许可与凭据调用链已定位，未连接到 OEM Unlock | [QAS/TEE/PFM](docs/research/qas-tee-pfm.md)、[系统 APK](docs/research/tee-system-apks.md) |
| GhostLock | 旧源码模式与实机配置已核对；运行中漏洞状态未知，适配 BLOCKED | [GhostLock](docs/research/ghostlock.md) |
| 内核候选构建 | 匹配 Clang11 可编译锁对象；两棵候选树 32 项采样布局一致，不能代替原厂 ABI | [配置与布局](docs/research/config-layout.md) |
| 固件与 OTA | JVN 已确认全版本 AVB 使用 AOSP 测试钥匙；仍缺 P780 专用写入路径与 `_162` 原厂镜像，6 份历史日志未取得 payload | [安全公告](docs/research/firmware-advisory-20260928.md)、[固件](docs/research/firmware-ota.md)、[OTA 日志审计](docs/research/ota-log-audit.md)、[Attestation/fstab 新线索](docs/research/avb-attestation-alternative-20261018.md)、[Google OTA Prober 交叉评估](docs/research/google-ota-prober-p780-20261018.md) |
| Journey 配置 | 版本 42 / 64 个策略键核对一致；静态消费者接入进程管理及 Service/Provider 限制，未发现 Root/OTA 链 | [Journey 审计](docs/research/journey-config.md) |
| 应用清理 | 历史操作和不同日期包状态已归档，去预装脚本会修改设备 | [应用实验](docs/research/apps-and-debloat.md) |

## 目录结构

| 目录 | 用途 |
|---|---|
| [docs/](docs) | 状态、时间线、证据清单与阅读入口 |
| [docs/research/](docs/research) | 持续维护的研究专题 |
| [docs/reference/](docs/reference) | 来源、归档规范与原件完整性记录 |
| [docs/archive/](docs/archive) | 早期阶段验收、导入去重与版本历史 |
| [evidence/](evidence) | 原件、阅读视图、提取证据和逐运行构建资料 |
| [archive/](archive) | 旧设备摘要、原始技术报告与历史脚本 |
| [tools/](tools) | 当前离线分析工具；使用方式见工具索引 |
| [.github/workflows/](.github/workflows) | 自动归档检查；候选构建与历史迁移工作流改为手动运行 |

原厂配置归位到 [evidence/device/p780-config.gz](evidence/device/p780-config.gz)，Tracefs 与四代 GhostLock 原件仍保留原始字节。构建资料按运行编号存放；最终布局结果引用 [run 38060518994](evidence/actions/2026-10-10-layout-audit/runs/38060518994)，不使用早期 31 项中间结果代替最终结论。

## 完整性与维护

本仓库保存了可回收的核心研究证据，**未声称所有历史文件均已迁入**。原始 framework ZIP/JAR 仍未入 Git；仓库有其 SHA、方法字节和提取分析。Journey 小配置 ZIP 已以可还原的 Base64 保存。详见 [资产清单](docs/EVIDENCE_MANIFEST.md)。

**仓库可见性：2026-10-18 机主已改回 Private，GitHub API 再次确认 `visibility=private`。此前 Public 状态期间的潜在访问无法撤回，须继续审阅 Git 历史/所有 refs 和未经脱敏的系统日志。** [隐私与安全说明](SECURITY.md)：restricted 是分类标签，不能提供目录级访问控制；原始系统日志和 Git 历史尚未完成发布级脱敏。

每个可核验阶段同步专题、状态、证据、说明和 [维护日志](CHANGELOG.md)，修订过时结论、统一索引，必要时归位与去重。例行监测无实质新增时不制造提交。出现有效新线索时通知机主并同步经核验的来源与结论。

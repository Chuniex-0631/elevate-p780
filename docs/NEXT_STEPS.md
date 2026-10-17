# 后续关卡与待机监测

更新：2026-10-18。**常规 AVB ADB 属性取证已经完成，暂停继续向机主索取重复 getprop 输出**；继续固件/签名/写入通道的公开资料及离线研究，不涉及刷机或 Bootloader 状态修改。

## 本轮立即可用的只读任务（2026-10-18）

- 用户实机确认 `green / locked / flash.locked=1 / _b`、`sha256`、`7744` 字节 VBMeta 总长度和 AVB `1.1`。B 槽 `vbmeta_b`→`sde31`、`vbmeta_system_b`→`sda11`；**链式描述符未经镜像核验**，细节见 [AVB 基线专题](research/avb-live-baseline-20261018.md)。
- Windows 用户可以运行 [只读 AVB ADB 采集脚本](../tools/p780-avb-readonly.ps1) 补齐可见的公钥摘要属性、分区软链接、块设备权限及动态分区映射；结果先检查是否有敏感信息再分享。该脚本不会读取 `/dev/block` 内容。
- 未来获得同版本镜像后，使用 AOSP `avbtool info_image`、`calculate_vbmeta_digest` 校验与实机 digest 是否匹配，并以 NCC Group `test_avb_key` 辅助识别已知测试公钥。**无原始 VBMeta 时不要凭 digest 反推密钥或试刷。**

## 最新只读取证阶段（2026-10-18 第三轮）

- `vbmeta.public_key_digest` 空；`vbmeta.avb_version=1.0`（Bootloader）与 `avb_version=1.1`（Android）来自不同组件；`veritymode=enforcing`。
- `vbmeta_b` 和 `vbmeta_system_b` 原始块设备权限为 `root:root 0600`，当前非 root Shell 无法直接提取；不尝试越权取镜像。
- B 槽逻辑分区以及五份 dm-verity 映射已经观察到，`system_b-cow` 是 OTA/COW 候选线索，**不要推断更新仍在进行或 AVB 可被绕过**。
- **第四轮已核对** `ro.boot.dynamic_partitions=true`；`ro.virtual_ab.enabled`、`ro.virtual_ab.compression.enabled`、`ro.boot.vbmeta.device` 均为空。已确认动态分区，但不能由空值否定 Virtual A/B；`system_b-cow` 仍只是候选快照节点。停止重复属性采集，转入[原厂镜像与写入通道](research/avb-live-baseline-20261018.md)专题。
- **仍最优先取得匹配 `_162` 的可信原厂 VBMeta/OTA**；此类现场映射不是原厂签名与链式描述符的替代品。

## 2026-10-18：新的不依赖原厂镜像的实机取证路径（待用户可选验证）

经 AOSP 官方 Keystore/CTS 与动态分区文档交叉核对，找到之前未测试的两条只读逻辑线索，详细见 [Key Attestation 与 Fstab 专题](research/avb-attestation-alternative-20261018.md)。

- **新 P1：Android Keystore Hardware Key Attestation**。普通应用可以在设备支持时取得 `RootOfTrust.verifiedBootKey`（AVB 信任公钥哈希）及可选 `verifiedBootHash`（有机会与已有 `33ee…95f2` 一致），以及 `deviceLocked`/`verifiedBootState`。不需要 Root/原厂镜像。**P780 本机尚未验证能否获得硬件证明**；需要检查证书链来源、TEE 安全级别和隐私，不能把软件自报的哈希当作可信硬件证明。官方 APK 工具来源：开源 [vvb2060/KeyAttestation](https://github.com/vvb2060/KeyAttestation/releases)，使用普通 Keystore，无需 Shizuku。
- **新 P2：fstab `avb=vbmeta_system` 配置**。可在存在且可读时检查 `/vendor/etc/fstab*`，确认各逻辑分区声明的 AVB 挂载目标。此举不会泄露签名密钥，也不能证明 bootloader chain descriptors。
- **新 P3：AOSP 默认测试公钥的离线候选哈希**。AOSP build 系统默认采用 RSA4096 测试钥匙；必须先核对 Attestation 指纹的真实性与哈希输入编码才能对比，不能猜测 P780 确定使用这把钥匙。
- 不需重复穷举普通 `getprop`、执行 EDL、获取 Root 或刷写。用户可选择是否安装第三方开源测试应用；尚未执行安装或采集。

## 2026-10-18：原厂完整 OTA 稀缺情况下的研究路线调整

**避免把完整 `_162` OTA 当成所有 AVB 工作的唯一前置条件。** 改为两层目标：
1. **探索性离线密钥识别**：接受任意有可追溯出处的 **P780** 版本 `vbmeta*.img`、`avbtool info_image` 输出、chain descriptors、AVB 公钥指纹/原始测试记录；固件版本必须标注，不能用 Rakuten Hand（非 5G）、其他 Snapdragon 480/同 OEM 机型的镜像代替。JVN 确认受影响范围为 Hand 5G 全版本，**不保证不同版本使用同一把密钥**。
2. **本机匹配与实证**：要核对 `P780AE_11.0_RMN_JP_162` 的 `sha256` digest / VBMeta `7744` 字节总量、启动内核等，仍需要 `_162` 同源镜像或有充分构建身份、签名链的工件；写入验证还额外需要 P780 专用、可恢复的 locked 写入通道。

可追踪线索与联系：
- [JVN#47427200](https://jvn.jp/jp/JVN47427200/) 于 2026-10-14 公布并署名报告者 **松原正佳**；尚未发现公开发表的 P780 vbmeta 原件、对应密钥指纹或复现实验详细日志。**不要因署名而断定报告者持有可分享的所有固件/PoC**。
- [JVN 官方联系页](https://jvn.jp/contact/) 仅作历史上可考虑的公开咨询渠道。**机主已明确倾向暂停主动发信/追问**，既有 TINNO 请求尚未取得有效答复，后续不自动联系 JVN、报告人、Rakuten、TINNO。已有原邮件只保持被动监测；若对方主动提供实质资料，另行核验。
- **主要主动路径**：公开漏洞技术补充、开发社区已发表的 P780 镜像/公钥证据、有出处的其它 P780 固件版本 VBMeta、小型只读的签名描述符结果、可信公开 OTA delta；需要记录来源与哈希，谨防维修包或跨机型伪装。完整固件、匹配 Firehose 与 locked 写入通道仍然是最终实机工作的缺口。
- 2026-10-18 针对 `P780AE_11.0_RMN_JP_162` / AVB / 公钥 / Firehose 的公开检索未找到可校验完整镜像。日本楽天社区能确认有升级到 `_162` 的实机用户，但这不等于存在公开镜像下载：[官方升级页](https://network.mobile.rakuten.co.jp/information/software/rakuten-hand-5g/)；[楽天社群用户反馈](https://community.mobile.rakuten.net/questions/p2kmixnvb71rgs7u)。

## 第四轮之后的主动优先级

- 第一：继续寻找来源明确的 `P780AE_11.0_RMN_JP_162` 原厂 OTA / `vbmeta_b`、`vbmeta_system_b`，保证固件身份、哈希和离线验证方式。
- 第二：验证实际的 AVB 公钥、Chain Partition Descriptor、`7744` 字节合计及现有 `sha256` digest；没有镜像就不声称能判断具体密钥。
- 第三：只接受附 P780 构建身份、完整原始记录与恢复条件的锁定态写入入口成果；同 SoC EDL loader 不可当作可信匹配。
- 第四：Virtual A/B / kernel COW 维持固件更新架构线索等级，不进行 OTA/COW 有状态操作。

## 值得重启研究的新证据

| 新证据 | 先做什么 | 仍需注意的边界 |
|---|---|---|
| 可信完整 `_162` OTA / boot.img / Image / vmlinux | 核对来源、构建身份与原件哈希，离线提取内核与更新元数据 | 跨机型镜像不能当成本机原厂输入 |
| P780 专用的锁定态写入通道或 `_162` AVB 布局/签名证据 | 与 [JVN/CVE 专题](research/firmware-advisory-20260928.md) 对照，离线核对 boot/vbmeta 链和钥匙身份 | JVN 已确认 AOSP 测试钥匙，但未公开 P780 的安装路径；信任缺陷不等于可写分区 |
| 本机签名/HWID 匹配的 EDL Loader 证据 | 先核对原件身份与实际握手记录 | 同 SoC 不代表签名兼容；EDL 识别不等于分区读取成功 |
| 可复核的 P780 Root / BL 解锁新成果 | 核对型号、版本、前置状态、原始记录与可重复性 | 传闻、演示名称、其它机型成果不能改写本机状态 |
| 原厂内核实现、类型或符号证据 | 核对逐构建身份后再评估 GhostLock 阻断项 | 候选树的 32 项一致不能代替实机 ABI/栈帧/符号 |

## 已关闭的本轮待办

- OTA/Activity 与 Bugreport 内 6 份历史引擎日志已审计：所见为启动清理，未取得固件 URL/payload。
- 两份实机 JAR 已读取；JourneyConfigService 的 54 方法、8 类和 17 个直接外部引用已存档。
- vendor XML/version 与 TCS 状态均为 42；64 键按 ALL 区域假设完全一致。
- JourneyPerformanceService 消费者与末尾星号匹配已核对：134 方法、79 条外部引用/25 个调用者方法，接入应用策略；开关当前是否启用未动态验证。
- 两棵候选内核最终 run 38060518994 各 32 项提取成功、0 差异；结论仍只适用于被测候选采样。
- 2026-10-14 的 JVN#47427200 / CVE-2026-107153 已归档：确认 Hand 5G 全版本 AVB 使用已知 AOSP 测试钥匙；未把论文中的跨机型通用流程写成本机 Root 成果。

详见 [状态](STATUS.md)、[Journey](research/journey-config.md)、[配置/布局](research/config-layout.md)。以上事项不再重复要求机主采集。

## 监测和维护约定

现有每日监测任务保持启用，仅在出现实质新增时用中文通知，并附原始来源、新增点与本机适配条件。读取仓库当前状态及上次检查为基线；页面无法访问或搜索未命中不等于没有线索。

出现可核验进展时更新对应专题、STATUS、证据来源与 CHANGELOG，修订过时内容并保持结构一致；没有新增不制造例行提交。不自动运行漏洞或刷写手机。

## 持续阻断与资料缺口

原厂 `_162` 完整 OTA/boot.img/vbmeta/vmlinux 未取得；JVN 已确认 AVB 测试钥匙问题，但 P780 锁定态写入通道仍未知；GhostLock 仍 BLOCKED；Firehose 分区读取、Root 和 BL 解锁均无成功证据。部分历史 APK/getprop/Fastboot 原件和新上传 framework 原始 ZIP/JAR 未迁入 Git，逐项见 [资产清单](EVIDENCE_MANIFEST.md)。敏感转储仍按 [SECURITY](../SECURITY.md) 管理。

## XDA 4805241 后续分流（2026-10-17）

- **已完成**：用户提供正文，原样归档；关闭 `xda-4805241-manual-capture` 正文提醒，不重复索取同一正文。未声称获得回复、附件或原始网页。
- **继续推进**：可信 `_162` 镜像、Recovery/OTA 公钥及 AVB 公钥的离线核对，匹配 Loader 和 P780 locked 通道的原始成功日志。
- **有工件再核验**：测试 ZIP/哈希、signapk 版本与完整命令（包括 whole-file 签名方式）、证书指纹、Recovery 完整日志、测试设备构建号。未取得这些资料前不重复要求机主运行测试。
- **暂缓**：以包证书 testkey 直接 sideload 的捷径；`fastboot boot` 仅为作者求助设想，无成功证据；`OPG105` 仅作待验证检索词，不使用其镜像。
- TINNO 源码申请继续等待原线程回复；本篇未改变厂商联络安排。详见 [归因专题](research/firmware-advisory-20260928.md)。

# 后续关卡与待机监测

更新：2026-10-18。继续公开线索监测；可自愿开展无写入的 AVB 信息采集，禁止将只读步骤升级为刷机或 Bootloader 状态修改。

## 本轮立即可用的只读任务（2026-10-18）

- 用户实机确认 `green / locked / flash.locked=1 / _b`、`sha256`、`7744` 字节 VBMeta 总长度和 AVB `1.1`。B 槽 `vbmeta_b`→`sde31`、`vbmeta_system_b`→`sda11`；**链式描述符未经镜像核验**，细节见 [AVB 基线专题](research/avb-live-baseline-20261018.md)。
- Windows 用户可以运行 [只读 AVB ADB 采集脚本](../tools/p780-avb-readonly.ps1) 补齐可见的公钥摘要属性、分区软链接、块设备权限及动态分区映射；结果先检查是否有敏感信息再分享。该脚本不会读取 `/dev/block` 内容。
- 未来获得同版本镜像后，使用 AOSP `avbtool info_image`、`calculate_vbmeta_digest` 校验与实机 digest 是否匹配，并以 NCC Group `test_avb_key` 辅助识别已知测试公钥。**无原始 VBMeta 时不要凭 digest 反推密钥或试刷。**

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

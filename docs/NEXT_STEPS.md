# 后续关卡与待机监测

更新：2026-10-11。当前暂停主动设备实验，保留公开线索监测。机主暂时无需操作手机。

## 值得重启研究的新证据

| 新证据 | 先做什么 | 仍需注意的边界 |
|---|---|---|
| 可信完整 `_162` OTA / boot.img / Image / vmlinux | 核对来源、构建身份与原件哈希，离线提取内核与更新元数据 | 跨机型镜像不能当成本机原厂输入 |
| 官方固件认证问题的技术说明、JVN/CVE 或研究文章 | 与 [官方公告专题](research/firmware-advisory-20260928.md) 对照，定位具体触发环节 | 公告、明文配置服务与 GhostLock 三者不能自动关联 |
| 本机签名/HWID 匹配的 EDL Loader 证据 | 先核对原件身份与实际握手记录 | 同 SoC 不代表签名兼容；EDL 识别不等于分区读取成功 |
| 可复核的 P780 Root / BL 解锁新成果 | 核对型号、版本、前置状态、原始记录与可重复性 | 传闻、演示名称、其它机型成果不能改写本机状态 |
| 原厂内核实现、类型或符号证据 | 核对逐构建身份后再评估 GhostLock 阻断项 | 候选树的 32 项一致不能代替实机 ABI/栈帧/符号 |

## 已关闭的本轮待办

- OTA/Activity 与 Bugreport 内 6 份历史引擎日志已审计：所见为启动清理，未取得固件 URL/payload。
- 两份实机 JAR 已读取；JourneyConfigService 的 54 方法、8 类和 17 个直接外部引用已存档。
- vendor XML/version 与 TCS 状态均为 42；64 键按 ALL 区域假设完全一致。
- JourneyPerformanceService 消费者与末尾星号匹配已核对：134 方法、79 条外部引用/25 个调用者方法，接入应用策略；开关当前是否启用未动态验证。
- 两棵候选内核最终 run 38060518994 各 32 项提取成功、0 差异；结论仍只适用于被测候选采样。

详见 [状态](STATUS.md)、[Journey](research/journey-config.md)、[配置/布局](research/config-layout.md)。以上事项不再重复要求机主采集。

## 监测和维护约定

现有每日监测任务保持启用，仅在出现实质新增时用中文通知，并附原始来源、新增点与本机适配条件。读取仓库当前状态及上次检查为基线；页面无法访问或搜索未命中不等于没有线索。

出现可核验进展时更新对应专题、STATUS、证据来源与 CHANGELOG，修订过时内容并保持结构一致；没有新增不制造例行提交。不自动运行漏洞或刷写手机。

## 持续阻断与资料缺口

原厂 `_162` 完整 OTA/boot.img/vmlinux 未取得；GhostLock 仍 BLOCKED；Firehose 分区读取、Root 和 BL 解锁均无成功证据。部分历史 APK/getprop/Fastboot 原件和新上传 framework 原始 ZIP/JAR 未迁入 Git，逐项见 [资产清单](EVIDENCE_MANIFEST.md)。敏感转储仍按 [SECURITY](../SECURITY.md) 管理。

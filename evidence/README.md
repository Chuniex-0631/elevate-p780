# 证据目录

原件、转换视图与分析产物分别标识；目录位置不代表权限、真实性或实机成功。完整来源/迁移状态见 [资产清单](../docs/EVIDENCE_MANIFEST.md)。

| 目录 | 内容 | 证据边界 |
|---|---|---|
| [device/](device) | 原厂配置 gzip、4KB Tracefs 原始字节 | 配置与采样，不是内核镜像或基址 |
| [ghostlock/](ghostlock) | v0.1–v0.4 四份原始 ZIP | 不重打包；预检不是 Root 成果 |
| [actions/](actions) | 逐运行配置、日志、对象与候选结构采样 | [布局运行索引](actions/2026-10-10-layout-audit/README.md)；独立运行相同 SHA 保留 |
| [framework/](framework) | 实机 JAR 来源 SHA、DEX 方法字节、反汇编、调用点与文本阅读视图 | 原始 JAR/大 ZIP 尚未入 Git |
| [journey/](journey) | vendor XML/version、TCS 阅读视图、对照与可还原原始 ZIP | 配置策略表不等于安装/权限表 |
| [analysis/](analysis) | OTA 审计结构化摘要 | 分析结论，非固件原件 |
| [apk/](apk) | 三份实机来源 APK | 离线归档，不主动安装 |
| [tee/](tee) | 白名单与 native-api 访问证据 | 不等于任意 TEE 权限 |
| [restricted/](restricted) | 原始 Bugreport、ADB ZIP、OTA 日志和包清单 | 分类标签，无目录级 ACL，尚未发布级脱敏 |

[归档规范](../docs/reference/archive-protocol.md)、[原件完整性](../docs/reference/evidence-integrity.md)、[本轮整理](../docs/REPOSITORY_AUDIT.md)。

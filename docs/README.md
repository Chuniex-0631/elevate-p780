# 文档导航

当前结论以 [STATUS](STATUS.md) 为准；早期验收和原始报告用于追溯，不覆盖当前状态。目前正推进 DSU/GSI 可信启动与 AVB 签名证据核对；Root/BL 解锁未达成。

## 核心入口

- [当前状态](STATUS.md)、[后续关卡](NEXT_STEPS.md)、[研究时间线](HISTORY.md)。
- [文件资产与迁移状态](EVIDENCE_MANIFEST.md)、[全库整理验收](REPOSITORY_AUDIT.md)。

## 持续研究专题

| 问题 | 文档 |
|---|---|
| 手机、启动链、EDL/Fastboot | [设备与启动](research/device-and-boot.md)、[DSU/GSI 主专题](research/p780-dsu-locked-gsi-20261018.md)、[Google 24 条 GSI JSON 核验](research/p780-dsu-gsi-catalog-verified-20261018.md)、[第九轮 AVB 公钥信任链与风险](research/p780-dsu-trust-chain-audit-20261018.md) |
| 官方固件、OTA 与认证公告 | [固件](research/firmware-ota.md)、[2026-09-28 公告](research/firmware-advisory-20260928.md)、[2026-10-18 AVB 实机基线](research/avb-live-baseline-20261018.md)、[Google OTA Prober 评估](research/google-ota-prober-p780-20261018.md)、[本机 AVB 测试公钥 TEE 实证](research/avb-attestation-confirmed-20261018.md)、[P780 Fstab 与 AVB 挂载实测](research/p780-fstab-avb-20261018.md) |
| 更新日志到底证明什么 | [OTA 日志审计](research/ota-log-audit.md)、[原始 Bugreport 索引](research/ota-bugreport.md) |
| QAS、Mink、PFM、TZAccess | [调用链](research/qas-tee-pfm.md)、[TEE 与系统 APK](research/tee-system-apks.md) |
| GhostLock 是否可适配 | [主线](research/ghostlock.md)、[候选配置/布局](research/config-layout.md) |
| Journey 网络配置与进程策略 | [实机配置、消费者与匹配规则](research/journey-config.md) |
| 过去的软件包清理 | [应用实验](research/apps-and-debloat.md) |

## 参考与历史

- [来源与可重复性](reference/sources.md)、[归档规范](reference/archive-protocol.md)、[原件完整性](reference/evidence-integrity.md)。
- [2026-10-10 阶段验收](archive/20261010-archive-review.md)、[原件导入与去重](archive/20261010-import-dedup.md)、[GhostLock 四代包索引](archive/ghostlock-package-versions.md)。
- [旧完整技术报告](../archive/reports)、[原件与提取证据](../evidence)、[离线工具索引](../tools/README.md)。

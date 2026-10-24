# 文档导航

当前主线包含已有静态样本交叉分析及单独重启的 EDL 通信/候选 Loader 受控实验。DSU停止，Root/BL解锁未达成。状态以[STATUS](STATUS.md)为准，任务以[NEXT_STEPS](NEXT_STEPS.md)为准。

## 当前入口

[当前状态](STATUS.md) · [下一步](NEXT_STEPS.md) · [时间线](HISTORY.md) · [证据索引](EVIDENCE_MANIFEST.md) · [整理验收](REPOSITORY_AUDIT.md)

## 按研究问题阅读

|问题|文档|
|---|---|
|采集覆盖与实现缺口|[清单审核](research/p780-static-corpus-inventory-20261018.md)、[batch1](research/p780-static-batch1-analysis-20261018.md)、[batch2](research/p780-static-batch2-analysis-20261018.md)|
|接口、调用者与权限|[native交叉矩阵](research/p780-native-interface-crosscheck-20261018.md)、[SELinux审计](research/p780-policy-boundary-audit-20261018.md)|
|OEM Unlock 灰色新假说|[OEMLOCK-01：HAL/PDB/策略只读实验](research/p780-oemlock-gate-probe-20261019.md)（尚未实机执行）|
|硬件与启动状态|[设备/Fastboot/EDL](research/device-and-boot.md)、[QDL QUD/Sahara 实机握手](research/p780-qdl-qud-sahara-20261019.md)、[AVB基线](research/avb-live-baseline-20261018.md)|
|AVB信任钥匙|[本机硬件证明](research/avb-attestation-confirmed-20261018.md)、[fstab](research/p780-fstab-avb-20261018.md)、[官方公告与第三方报告](research/firmware-advisory-20260928.md)、[早期Attestation方案（已完成）](research/avb-attestation-alternative-20261018.md)|
|DSU为何停止|[最终收束](research/p780-dsu-closure-maintenance-route-20261018.md)、[全部历史阶段索引](archive/dsu-index-20261018.md)|
|固件/OTA证据|[固件概况](research/firmware-ota.md)、[2026-10-24 原厂工件检索复核](research/p780-source-availability-followup-20261024.md)、[Google Prober负面结果](research/google-ota-prober-p780-20261018.md)、[OTA日志分析](research/ota-log-audit.md)、[Bugreport来源](research/ota-bugreport.md)|
|QAS/Mink/PFM/TEE|[调用链](research/qas-tee-pfm.md)、[系统APK与白名单](research/tee-system-apks.md)|
|运行内核与候选源码|[GhostLock阻断项](research/ghostlock.md)、[Kconfig与布局](research/config-layout.md)、[官方源码联络](official-source-request-log.md)、[公开同名设备树候选审计](research/public-p780ae-device-tree-audit-20261024.md)|
|Journey应用策略|[配置与消费者审计](research/journey-config.md)；与Journey init诊断命令区分|
|历史精简操作|[应用实验](research/apps-and-debloat.md)；不是当前实验环境基线|

## 参考、历史与工具

- [来源](reference/sources.md)、[归档规范](reference/archive-protocol.md)、[完整性](reference/evidence-integrity.md)。
- [2026-10-10验收](archive/20261010-archive-review.md)、[导入去重](archive/20261010-import-dedup.md)、[2026-10-11结构验收](archive/repository-audit-20261011.md)。
- [GhostLock版本](archive/ghostlock-package-versions.md)、[旧计划](archive/next-steps-before-dsu-20261018.md)、[旧逐轮证据账本](archive/evidence-ledger-before-consolidation-20261018.md)。
- [旧技术报告](../archive/reports)、[证据目录](../evidence/README.md)、[工具](../tools/README.md)、[隐私说明](../SECURITY.md)。

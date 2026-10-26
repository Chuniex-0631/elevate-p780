# 文档索引

> 由 `tools/build_research_index.py` 生成（2026-10-26），含全部目录 Markdown。
> 当前结论优先阅读 STATUS 与最新审计专题；历史报告保留阶段性假设。

## app（1）

| 文档 | 标题 |
|---|---|
| [app/elevate/README.md](../app/elevate/README.md) | Elevate：P780 临时 root 控制台 |

## archive（6）

| 文档 | 标题 |
|---|---|
| [archive/device/P780_loaded_module_names.md](../archive/device/P780_loaded_module_names.md) | P780 2026-10-10 实机模块观察（按原文件保留名称） |
| [archive/README.md](../archive/README.md) | 旧研究成果归档 |
| [archive/reports/P780_GhostLock_source_audit_2026-10-10.md](../archive/reports/P780_GhostLock_source_audit_2026-10-10.md) | Rakuten Hand 5G (P780) / GhostLock 源码核对报告 |
| [archive/reports/P780_MinkNative_2026-10-04.md](../archive/reports/P780_MinkNative_2026-10-04.md) | P780：Mink 原生层与 PFM 运行证据 |
| [archive/reports/P780_PFM_QAS_2026-10-04.md](../archive/reports/P780_PFM_QAS_2026-10-04.md) | Rakuten Hand 5G P780：QAS → Mink → PFM 研究检查点 |
| [archive/reports/P780_TZAccess_2026-10-04.md](../archive/reports/P780_TZAccess_2026-10-04.md) | P780：TZAccessService 服务端 Java 授权链 |

## docs（103）

| 文档 | 标题 |
|---|---|
| [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) | 仓库结构与维护约定 |
| [docs/archive/20261010-archive-review.md](../docs/archive/20261010-archive-review.md) | Rakuten Hand 5G / P780：2026-10-10 阶段归档验收 |
| [docs/archive/20261010-import-dedup.md](../docs/archive/20261010-import-dedup.md) | 2026-10-10 新增实体机资料接收、比对与去重报告 |
| [docs/archive/dsu-index-20261018.md](../docs/archive/dsu-index-20261018.md) | DSU历史专题索引 |
| [docs/archive/evidence-ledger-before-consolidation-20261018.md](../docs/archive/evidence-ledger-before-consolidation-20261018.md) | P780 已定位研究文件总清单 |
| [docs/archive/ghostlock-package-versions.md](../docs/archive/ghostlock-package-versions.md) | GhostLock P780 离线研究包：v0.1—v0.4 |
| [docs/archive/next-steps-before-dsu-20261018.md](../docs/archive/next-steps-before-dsu-20261018.md) | 历史研究计划快照（2026-10-18 DSU 研究之前） |
| [docs/archive/repository-audit-20261011.md](../docs/archive/repository-audit-20261011.md) | 2026-10-11 全库结构整理验收 |
| [docs/EVIDENCE_MANIFEST.md](../docs/EVIDENCE_MANIFEST.md) | 证据清单 |
| [docs/HISTORY.md](../docs/HISTORY.md) | 研究时间线 |
| [docs/NEXT_STEPS.md](../docs/NEXT_STEPS.md) | 下一步计划 |
| [docs/official-source-request-log.md](../docs/official-source-request-log.md) | Rakuten Hand 5G / TINNO P780 官方源码请求联络 |
| [docs/README.md](../docs/README.md) | 文档导航 |
| [docs/reference/archive-protocol.md](../docs/reference/archive-protocol.md) | P780 证据归档规范 |
| [docs/reference/evidence-integrity.md](../docs/reference/evidence-integrity.md) | P780 核心证据完整性校验（2026-10-10） |
| [docs/reference/sources.md](../docs/reference/sources.md) | 来源、引用和可重复性 |
| [docs/REPOSITORY_AUDIT.md](../docs/REPOSITORY_AUDIT.md) | 2026-10-18 全库总结与整理验收 |
| [docs/research/apps-and-debloat.md](../docs/research/apps-and-debloat.md) | P780 ADB 应用清理与设备维护实验（历史） |
| [docs/research/avb-attestation-alternative-20261018.md](../docs/research/avb-attestation-alternative-20261018.md) | P780 AVB 研究：无需原厂镜像的硬件证明替代路径（2026-10-18） |
| [docs/research/avb-attestation-confirmed-20261018.md](../docs/research/avb-attestation-confirmed-20261018.md) | P780 AVB 硬件证明与 AOSP 默认测试公钥匹配（2026-10-18） |
| [docs/research/avb-live-baseline-20261018.md](../docs/research/avb-live-baseline-20261018.md) | P780 AVB 实机只读基线（2026-10-18） |
| [docs/research/config-layout.md](../docs/research/config-layout.md) | P780：24 项配置缺失与候选结构布局研究 |
| [docs/research/device-and-boot.md](../docs/research/device-and-boot.md) | 实机硬件、系统、Bootloader、Fastboot、EDL 档案 |
| [docs/research/firmware-advisory-20260928.md](../docs/research/firmware-advisory-20260928.md) | Rakuten Hand 5G 固件真实性漏洞：JVN#47427200 / CVE-2026-107153 |
| [docs/research/firmware-ota.md](../docs/research/firmware-ota.md) | P780 固件 / OTA / 官方安全公告资料 |
| [docs/research/ghostlock.md](../docs/research/ghostlock.md) | GhostLock (CVE-2026-43499) / P780 适配调查 |
| [docs/research/google-ota-prober-p780-20261018.md](../docs/research/google-ota-prober-p780-20261018.md) | Google OTA Prober × Rakuten Hand 5G (P780) \| 2026-10-18 |
| [docs/research/journey-config.md](../docs/research/journey-config.md) | P780 JourneyConfigService 实机 JAR 审计 |
| [docs/research/ota-bugreport.md](../docs/research/ota-bugreport.md) | P780 更新服务日志与 Android Bugreport 原始证据 |
| [docs/research/ota-log-audit.md](../docs/research/ota-log-audit.md) | P780 OTA 日志与 Journey 配置服务核对 |
| [docs/research/p780-abl-avb-gsi-20261026.md](../docs/research/p780-abl-avb-gsi-20261026.md) | AVB 链重审：根/系统链都是公开测试密钥（2026-10-26） |
| [docs/research/p780-afunix-cve-2024-26923-20261026.md](../docs/research/p780-afunix-cve-2024-26923-20261026.md) | CVE-2024-26923：AF_UNIX GC vs connect() 触发（2026-10-26） |
| [docs/research/p780-artifact-scan-20261025.md](../docs/research/p780-artifact-scan-20261025.md) | 全量系统文件扫描：密钥、凭据与有用信息（2026-10-25） |
| [docs/research/p780-boot-edl-audit-20261026.md](../docs/research/p780-boot-edl-audit-20261026.md) | P780 ABL / EDL 只读复核（2026-10-26） |
| [docs/research/p780-candidate-layout-20261025.md](../docs/research/p780-candidate-layout-20261025.md) | 候选构建的结构布局与验证（2026-10-25） |
| [docs/research/p780-dirtyfrag-live-exploit-20261025.md](../docs/research/p780-dirtyfrag-live-exploit-20261025.md) | P780 DirtyFrag 实机利用链（2026-10-25） |
| [docs/research/p780-dirtyfrag-tinno-5.4.61-source-audit-20261024.md](../docs/research/p780-dirtyfrag-tinno-5.4.61-source-audit-20261024.md) | TINNO P780 Linux 5.4.61：DirtyFrag 相关 UDP sendpage / ESP 源码审计 |
| [docs/research/p780-dirtyfrag-udp-esp-source-audit-20261024.md](../docs/research/p780-dirtyfrag-udp-esp-source-audit-20261024.md) | P780 DirtyFrag / CVE-2026-43284：UDP sendpage 与 ESP 静态源码核对 |
| [docs/research/p780-dirtyfrag-v02-path-interpretation-20261024.md](../docs/research/p780-dirtyfrag-v02-path-interpretation-20261024.md) | P780 DirtyFrag：v0.2 回环证据的含义与下一道安全门 |
| [docs/research/p780-dirtyfrag-v03-sendfile-probe-20261024.md](../docs/research/p780-dirtyfrag-v03-sendfile-probe-20261024.md) | P780 DirtyFrag：v0.3.0 文件支持 UDP sendfile 预检 |
| [docs/research/p780-dsu-android15-avb-extraction-plan-20261018.md](../docs/research/p780-dsu-android15-avb-extraction-plan-20261018.md) | P780 第十四轮：Android 15 GSI AVB 签名公钥 PC 离线提取方案（2026-10-18） |
| [docs/research/p780-dsu-android15-avb-key-verified-20261018.md](../docs/research/p780-dsu-android15-avb-key-verified-20261018.md) | P780 DSU 第十五轮：Android15 GSI 内嵌 AVB 公钥已取得，确认 Q Developer GSI，根因仍待 P780 Ramdisk（2026-10-18） |
| [docs/research/p780-dsu-bugreport-audit-20261018.md](../docs/research/p780-dsu-bugreport-audit-20261018.md) | P780 第十三轮：首次 DSU 失败后的 Android Bugreport 全量离线审计（2026-10-18） |
| [docs/research/p780-dsu-closure-maintenance-route-20261018.md](../docs/research/p780-dsu-closure-maintenance-route-20261018.md) | P780 DSU 实机阶段收束与原厂维护接口路线（2026-10-18） |
| [docs/research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md](../docs/research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md) | P780 DSU 第十六轮：CVE-2026-107153 公共 AVB 测试根密钥 × 自签名 GSI × DSU Sideloader 可行性（2026-10-18） |
| [docs/research/p780-dsu-first-trial-protocol-20261018.md](../docs/research/p780-dsu-first-trial-protocol-20261018.md) | P780 DSU 首次实机试验协议（2026-10-18） |
| [docs/research/p780-dsu-gsi-catalog-verified-20261018.md](../docs/research/p780-dsu-gsi-catalog-verified-20261018.md) | P780 DSU 第八轮：Google 六个子目录原始 JSON 完整验证（2026-10-18） |
| [docs/research/p780-dsu-locked-bl-vs-gsi-trust-20261018.md](../docs/research/p780-dsu-locked-bl-vs-gsi-trust-20261018.md) | P780 DSU 锁定 Bootloader 与 GSI 签名信任机制专项核验（2026-10-18） |
| [docs/research/p780-dsu-locked-gsi-20261018.md](../docs/research/p780-dsu-locked-gsi-20261018.md) | P780 Android 11 DSU / GSI 可信启动支线 — 源码交叉核对（2026-10-18） |
| [docs/research/p780-dsu-readonly-followup-20261019.md](../docs/research/p780-dsu-readonly-followup-20261019.md) | DSU-READ-01：恢复出厂后的状态与现有GSI兼容性补证（2026-10-19） |
| [docs/research/p780-dsu-stock-fallback-20261018.md](../docs/research/p780-dsu-stock-fallback-20261018.md) | P780 第十轮 DSU 首次试机：下载完成后重启仍返回原厂系统（2026-10-18） |
| [docs/research/p780-dsu-testroot-resign-verified-20261018.md](../docs/research/p780-dsu-testroot-resign-verified-20261018.md) | P780 DSU 第十七轮：真实 Android 15 GSI 使用 AOSP 测试根密钥离线重签并通过 AVB 验证（2026-10-18） |
| [docs/research/p780-dsu-trust-chain-audit-20261018.md](../docs/research/p780-dsu-trust-chain-audit-20261018.md) | P780 DSU 第九轮 — AVB/GSI 信任链源码审计与公开公钥二进制核对（2026-10-18） |
| [docs/research/p780-edl-programmer-20261026.md](../docs/research/p780-edl-programmer-20261026.md) | EDL programmer 公开渠道搜索结论（2026-10-26） |
| [docs/research/p780-escalation-and-integration-20261025.md](../docs/research/p780-escalation-and-integration-20261025.md) | 从 installd root 继续提权与平台联动（2026-10-25） |
| [docs/research/p780-evidence-gap-audit-20261019.md](../docs/research/p780-evidence-gap-audit-20261019.md) | GAP-01�����в��ԡ��ں�֤������ļ���ʵ��2026-10-19��（部分损坏） |
| [docs/research/p780-firehose-screening-20261026.md](../docs/research/p780-firehose-screening-20261026.md) | Firehose 候选与商业 EDL 读取核对（2026-10-26） |
| [docs/research/p780-fstab-avb-20261018.md](../docs/research/p780-fstab-avb-20261018.md) | P780 fstab AVB 挂载配置实机取证（2026-10-18） |
| [docs/research/p780-ghostlock-5.4-20261026.md](../docs/research/p780-ghostlock-5.4-20261026.md) | GhostLock 5.4.233 可行性评估（2026-10-26） |
| [docs/research/p780-ghostlock-bug-shape-20261025.md](../docs/research/p780-ghostlock-bug-shape-20261025.md) | GhostLock 缺陷形态确认（2026-10-25） |
| [docs/research/p780-ghostlock-profile-draft-20261025.md](../docs/research/p780-ghostlock-profile-draft-20261025.md) | P780 GhostLock profile 草案（5.4.233，静态部分） |
| [docs/research/p780-init-capability-20261025.md](../docs/research/p780-init-capability-20261025.md) | init 域能力盘点（2026-10-25） |
| [docs/research/p780-installd-root-shell-20261025.md](../docs/research/p780-installd-root-shell-20261025.md) | P780 实机取得 uid 0 root shell（2026-10-25） |
| [docs/research/p780-ipsec-preflight-live-and-localversion-20261024.md](../docs/research/p780-ipsec-preflight-live-and-localversion-20261024.md) | P780 IPsec Preflight 实机结果与内核版本后缀来源核验 |
| [docs/research/p780-ipsec-v0.2-api-cts-design-20261024.md](../docs/research/p780-ipsec-v0.2-api-cts-design-20261024.md) | P780 IPsec diagnostics 0.2.0: Android 11 API/CTS basis and safety boundary |
| [docs/research/p780-ipsec-v0.2-live-loopback-20261024.md](../docs/research/p780-ipsec-v0.2-live-loopback-20261024.md) | P780 IPsec diagnostics 0.2.0 实机 UDP/ESP 回环结果 |
| [docs/research/p780-kernel-image-extraction-20261025.md](../docs/research/p780-kernel-image-extraction-20261025.md) | P780 内核镜像实机提取（2026-10-25） |
| [docs/research/p780-kernel-symbol-recovery-20261025.md](../docs/research/p780-kernel-symbol-recovery-20261025.md) | P780 内核符号恢复与独立核验（2026-10-25） |
| [docs/research/p780-kgsl-cve-2024-23373-20261026.md](../docs/research/p780-kgsl-cve-2024-23373-20261026.md) | 新内核 CVE 方向筛选（2026-10-26） |
| [docs/research/p780-native-interface-crosscheck-20261018.md](../docs/research/p780-native-interface-crosscheck-20261018.md) | P780 native接口、JAR与SELinux交叉核对 |
| [docs/research/p780-native-live-endpoints-20261019.md](../docs/research/p780-native-live-endpoints-20261019.md) | NATIVE-01：P780 运行端点与诊断 JNI 失败链（2026-10-19） |
| [docs/research/p780-next-research-20261025.md](../docs/research/p780-next-research-20261025.md) | 下一阶段研究选择（2026-10-25） |
| [docs/research/p780-oem-unlock-final-20261025.md](../docs/research/p780-oem-unlock-final-20261025.md) | OEM Unlock 终结性判定（2026-10-25） |
| [docs/research/p780-oemlock-caller-boundary-20261019.md](../docs/research/p780-oemlock-caller-boundary-20261019.md) | OEMLOCK-02：设置调用者与权限边界（2026-10-19） |
| [docs/research/p780-oemlock-first-results-20261019.md](../docs/research/p780-oemlock-first-results-20261019.md) | P780 OEMLOCK-01 第一阶段实测结果（2026-10-19） |
| [docs/research/p780-oemlock-gate-probe-20261019.md](../docs/research/p780-oemlock-gate-probe-20261019.md) | P780-OEMLOCK-01: OEM Unlock 灰色开关的限制来源 |
| [docs/research/p780-oemlock-journey-gate-20261019.md](../docs/research/p780-oemlock-journey-gate-20261019.md) | OEMLOCK-01：Journey customer gate 离线定位（2026-10-19） |
| [docs/research/p780-partition-content-extract-20261025.md](../docs/research/p780-partition-content-extract-20261025.md) | 系统分区内容整体提取（2026-10-25） |
| [docs/research/p780-partition-reextract-20261026.md](../docs/research/p780-partition-reextract-20261026.md) | 分区证据再提取：vendor_boot_a/b、dtbo_a（2026-10-26） |
| [docs/research/p780-perf-permission-probe-20261025.md](../docs/research/p780-perf-permission-probe-20261025.md) | P780 perf permission v0.1.0（2026-10-25） |
| [docs/research/p780-perf-v010-live-result-20261025.md](../docs/research/p780-perf-v010-live-result-20261025.md) | P780 perf v0.1.0 实机结果（2026-10-25） |
| [docs/research/p780-phase-3-closure-20261025.md](../docs/research/p780-phase-3-closure-20261025.md) | 阶段收尾：GhostLock 判负、域能力边界、只读榨取与解锁线关闭（2026-10-25） |
| [docs/research/p780-policy-boundary-audit-20261018.md](../docs/research/p780-policy-boundary-audit-20261018.md) | P780 SELinux ԭ����ƣ�Journey ���������socket��2026-10-18��（部分损坏） |
| [docs/research/p780-policy-header-verification-20261020.md](../docs/research/p780-policy-header-verification-20261020.md) | GAP-01 header 原件复核（2026-10-20） |
| [docs/research/p780-qdl-qud-sahara-20261019.md](../docs/research/p780-qdl-qud-sahara-20261019.md) | P780 EDL / QDL QUD 通信突破与 Mannar Loader 待测（2026-10-19） |
| [docs/research/p780-rom-kernel-system-triage-20261025.md](../docs/research/p780-rom-kernel-system-triage-20261025.md) | P780 ROM、内核与权限分层复核（2026-10-25） |
| [docs/research/p780-root-daemon-20261025.md](../docs/research/p780-root-daemon-20261025.md) | Root 守护进程载荷（2026-10-25） |
| [docs/research/p780-source-availability-followup-20261024.md](../docs/research/p780-source-availability-followup-20261024.md) | P780 _162 原厂内核源码与固件工件可得性复核 |
| [docs/research/p780-static-batch1-analysis-20261018.md](../docs/research/p780-static-batch1-analysis-20261018.md) | P780 静态样本 batch1 原件验证与交叉分析（2026-10-18） |
| [docs/research/p780-static-batch2-analysis-20261018.md](../docs/research/p780-static-batch2-analysis-20261018.md) | P780 system/lib64 第二批静态分析（2026-10-18） |
| [docs/research/p780-static-corpus-inventory-20261018.md](../docs/research/p780-static-corpus-inventory-20261018.md) | P780 ʵ����̬������һ���嵥��ˣ�2026-10-18��（部分损坏） |
| [docs/research/p780-static-patch-review-20261025.md](../docs/research/p780-static-patch-review-20261025.md) | P780 静态修复核对与 Magic3 文章参考（2026-10-25） |
| [docs/research/p780-supplement-20261024.md](../docs/research/p780-supplement-20261024.md) | P780 补充情报整理：2026-10-24 |
| [docs/research/p780-system-file-extraction-20261025.md](../docs/research/p780-system-file-extraction-20261025.md) | 从 /system 提取整文件（2026-10-25） |
| [docs/research/p780-uring-cve-2023-6931-20261025.md](../docs/research/p780-uring-cve-2023-6931-20261025.md) | io_uring CVE 选型：CVE-2023-52654 在本机成立（2026-10-25） |
| [docs/research/p780-vendor-service-audit-20261025.md](../docs/research/p780-vendor-service-audit-20261025.md) | 厂商预置服务审计（第一轮）：Journey 根服务与属性触发的 init 原语（2026-10-25） |
| [docs/research/p780-vuln-surface-analysis-20261025.md](../docs/research/p780-vuln-surface-analysis-20261025.md) | 新资产 × 已知漏洞：还有哪里有搞头（2026-10-25 评估） |
| [docs/research/public-p780ae-device-tree-audit-20261024.md](../docs/research/public-p780ae-device-tree-audit-20261024.md) | 公开 P780AE 设备树候选审计（2026-10-24） |
| [docs/research/qas-tee-pfm.md](../docs/research/qas-tee-pfm.md) | QAS → Mink → PFM → TZAccessService：已知事实索引 |
| [docs/research/tee-system-apks.md](../docs/research/tee-system-apks.md) | P780 TrustZone 白名单、JNI 访问记录及系统 APK 原件 |
| [docs/rom/AUDIT-20261025.md](../docs/rom/AUDIT-20261025.md) | P780 ROM Release 元数据与清单审计（2026-10-25） |
| [docs/rom/README.md](../docs/rom/README.md) | P780 ROM 内容提取包 |
| [docs/STATUS.md](../docs/STATUS.md) | 当前研究状态 |

## evidence（29）

| 文档 | 标题 |
|---|---|
| [evidence/20261026/abl/README.md](../evidence/20261026/abl/README.md) | ABL / XBL |
| [evidence/20261026/afunix/README.md](../evidence/20261026/afunix/README.md) | CVE-2024-26923 触发 |
| [evidence/20261026/artifact-scan/README.md](../evidence/20261026/artifact-scan/README.md) | 49 号 artifact 扫描 |
| [evidence/20261026/ghostlock/README.md](../evidence/20261026/ghostlock/README.md) | GhostLock 5.4 反汇编 |
| [evidence/20261026/gsi/README.md](../evidence/20261026/gsi/README.md) | GSI 验签 |
| [evidence/20261026/init/final-report-20261025.md](../evidence/20261026/init/final-report-20261025.md) | init 域能力与只读榨取：收尾报告（2026-10-25） |
| [evidence/20261026/init/README.md](../evidence/20261026/init/README.md) | init 域 |
| [evidence/20261026/kernel/README.md](../evidence/20261026/kernel/README.md) | 内核 / boot |
| [evidence/20261026/oem/README.md](../evidence/20261026/oem/README.md) | OEM unlock final |
| [evidence/20261026/partitions/README.md](../evidence/20261026/partitions/README.md) | 分区快照 |
| [evidence/20261026/README.md](../evidence/20261026/README.md) | 2026-10-26 证据 |
| [evidence/20261026/vuln-surface/README.md](../evidence/20261026/vuln-surface/README.md) | 52 号攻击面 |
| [evidence/actions/2026-10-10-clang11/config-summary.md](../evidence/actions/2026-10-10-clang11/config-summary.md) | P780 kernel config audit |
| [evidence/actions/2026-10-10-clang14/config-summary.md](../evidence/actions/2026-10-10-clang14/config-summary.md) | P780 kernel config audit |
| [evidence/actions/2026-10-10-config-delta/critical-delta.md](../evidence/actions/2026-10-10-config-delta/critical-delta.md) | P780 source-vs-device configuration drift |
| [evidence/actions/2026-10-10-layout-audit/README.md](../evidence/actions/2026-10-10-layout-audit/README.md) | 候选布局实验：按运行编号阅读 |
| [evidence/actions/2026-10-10-layout-audit/runs/38060293186/builds/p780-layout-a52s-5.4.233/config-summary.md](../evidence/actions/2026-10-10-layout-audit/runs/38060293186/builds/p780-layout-a52s-5.4.233/config-summary.md) | P780 kernel config audit |
| [evidence/actions/2026-10-10-layout-audit/runs/38060293186/layout-comparison.md](../evidence/actions/2026-10-10-layout-audit/runs/38060293186/layout-comparison.md) | Candidate source layout comparison |
| [evidence/actions/2026-10-10-layout-audit/runs/38060466663/builds/p780-layout-a52s-5.4.233/config-summary.md](../evidence/actions/2026-10-10-layout-audit/runs/38060466663/builds/p780-layout-a52s-5.4.233/config-summary.md) | P780 kernel config audit |
| [evidence/actions/2026-10-10-layout-audit/runs/38060466663/builds/p780-layout-tinno-5.4.61/config-summary.md](../evidence/actions/2026-10-10-layout-audit/runs/38060466663/builds/p780-layout-tinno-5.4.61/config-summary.md) | P780 kernel config audit |
| [evidence/actions/2026-10-10-layout-audit/runs/38060466663/layout-comparison.md](../evidence/actions/2026-10-10-layout-audit/runs/38060466663/layout-comparison.md) | Candidate source layout comparison |
| [evidence/actions/2026-10-10-layout-audit/runs/38060518994/builds/p780-layout-a52s-5.4.233/config-summary.md](../evidence/actions/2026-10-10-layout-audit/runs/38060518994/builds/p780-layout-a52s-5.4.233/config-summary.md) | P780 kernel config audit |
| [evidence/actions/2026-10-10-layout-audit/runs/38060518994/builds/p780-layout-tinno-5.4.61/config-summary.md](../evidence/actions/2026-10-10-layout-audit/runs/38060518994/builds/p780-layout-tinno-5.4.61/config-summary.md) | P780 kernel config audit |
| [evidence/actions/2026-10-10-layout-audit/runs/38060518994/layout-comparison.md](../evidence/actions/2026-10-10-layout-audit/runs/38060518994/layout-comparison.md) | Candidate source layout comparison |
| [evidence/actions/2026-10-10-layout-audit/source-audit/missing-config-references.md](../evidence/actions/2026-10-10-layout-audit/source-audit/missing-config-references.md) | Removed symbols: actual source references |
| [evidence/analysis/boot-edl-20261026/README.md](../evidence/analysis/boot-edl-20261026/README.md) | 2026-10-26 离线复核产物 |
| [evidence/README.md](../evidence/README.md) | 证据目录 |
| [evidence/restricted/README.md](../evidence/restricted/README.md) | 未脱敏的 P780 实机材料（需谨慎访问） |
| [evidence/supplement/20261024/README.md](../evidence/supplement/20261024/README.md) | P780 supplemental acquisition, 2026-10-24 |

## ghostlock（2）

| 文档 | 标题 |
|---|---|
| [ghostlock/M1.md](../ghostlock/M1.md) | M1：PI 链构造探针 |
| [ghostlock/README.md](../ghostlock/README.md) | GhostLock 移植骨架（2026-10-25） |

## tools（21）

| 文档 | 标题 |
|---|---|
| [tools/abl/README.md](../tools/abl/README.md) | ABL / boot 解析 |
| [tools/afunix/README.md](../tools/afunix/README.md) | CVE-2024-26923 触发 harness |
| [tools/artifact-scan/README.md](../tools/artifact-scan/README.md) | 49 号 artifact 扫描 |
| [tools/dirtyfrag-probe/README.md](../tools/dirtyfrag-probe/README.md) | DirtyFrag 探针工具（P780） |
| [tools/dsu/README.md](../tools/dsu/README.md) | DSU read-only follow-up tools |
| [tools/gaps/README.md](../tools/gaps/README.md) | Evidence gap tools |
| [tools/gsi/README.md](../tools/gsi/README.md) | 官方 GSI 下载/验签辅助 |
| [tools/ipsec-preflight-android/README.md](../tools/ipsec-preflight-android/README.md) | P780 / Android 11 IPsec and UDP diagnostics (non-exploit) |
| [tools/kallsyms/README.md](../tools/kallsyms/README.md) | kallsyms 提取 |
| [tools/kernel-symbol-recovery/README.md](../tools/kernel-symbol-recovery/README.md) | P780 内核符号恢复与独立核验（2026-10-25） |
| [tools/kgsl/README.md](../tools/kgsl/README.md) | kgsl 反汇编辅助 |
| [tools/native/README.md](../tools/native/README.md) | P780 diagnostic offline audit |
| [tools/oemlock/README.md](../tools/oemlock/README.md) | OEM Lock offline audit |
| [tools/partitions/README.md](../tools/partitions/README.md) | init 域分区 dumper |
| [tools/perf-permission/README.md](../tools/perf-permission/README.md) | P780 perf 最小权限探测 v0.1.0 |
| [tools/README.md](../tools/README.md) | 工具 |
| [tools/rom/README.md](../tools/rom/README.md) | P780 ROM Release 离线核验 |
| [tools/supplement/README.md](../tools/supplement/README.md) | P780 supplemental evidence tools |
| [tools/uring/analysis/DATA-CHAIN-20261026.md](../tools/uring/analysis/DATA-CHAIN-20261026.md) | 6931 新数据链设计：fake skb 双写（2026-10-26，离线） |
| [tools/uring/README.md](../tools/uring/README.md) | CVE-2023-6931 研究工具 |
| [tools/vuln-surface/README.md](../tools/vuln-surface/README.md) | 52 号攻击面解析 |

## 根目录（3）

| 文档 | 标题 |
|---|---|
| [CHANGELOG.md](../CHANGELOG.md) | 变更记录 |
| [README.md](../README.md) | Rakuten Hand 5G / TINNO P780 研究档案 |
| [SECURITY.md](../SECURITY.md) | 私人设备研究资料的隐私与安全 |


# 文档索引

> 由 `23-repo-rebuild/build_index.py` 生成于 2026-10-25。
> 列出仓库中全部 Markdown 文档，按目录分组，附标题与首句。

## 根目录（3）

| 文档 | 标题 | 备注 |
|---|---|---|
| [`CHANGELOG.md`](../CHANGELOG.md) | 变更记录 | - 确认 CVE-2026-43284 页缓存写入原语在 P780（5.4.233）成立：有效 ESP 报文被接受并覆盖 splice 进来的文件页。 |
| [`README.md`](../README.md) | Rakuten Hand 5G / TINNO P780 研究档案 | 设备：Qualcomm 平台（holi / mannar），Android 11，内部固件 P780AE11.0RMNJP162，系统指纹末段 264:user/release-keys，内核 5.4.233-qgki-gea5245e94 |
| [`SECURITY.md`](../SECURITY.md) | 私人设备研究资料的隐私与安全 | 本仓库记录用户本人持有的 Rakuten Hand 5G P780。2026-10-18 曾由 GitHub API 检测到 visibility=public；机主随后已改回 Private，经 GitHub API 再次确认。此前的公开 |

## docs 总览（9）

| 文档 | 标题 | 备注 |
|---|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | 仓库结构与维护约定 | 1. 状态只有一个权威页：docs/STATUS.md。其他页面只写"本页范围"，不另立结论。 |
| [`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md) | 证据清单 | 共 297 个文件，合计 18.9 MB。 |
| [`HISTORY.md`](HISTORY.md) | 研究时间线（据可复查材料重建） | - “2026-10-04 去预装实验”会改变 Android 用户 0 的包状态；恢复出厂后数值可能改变。不要将不同日期观察的包数认为同一时间。 |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | 下一步计划 | - DSU / GSI 启动实验：已安装、已回原厂，失败阶段未知。 |
| [`README.md`](README.md) | 文档导航 | - research/：按主题与日期的专题报告（p780-<主题>-<日期>.md） |
| [`REPOSITORY_AUDIT.md`](REPOSITORY_AUDIT.md) | 2026-10-18 全库总结与整理验收 | 基准提交：cc92c49c397dd01e9aecc002a7ca60b63aea500a。完整递归树未截断，整理前289个文件；逐项树清单记录路径、大小、模式和Git blob SHA。当前研究仍Locked/未Root，DSU停止。 |
| [`STATUS.md`](STATUS.md) | 当前研究状态 | 1. DirtyFrag 的原语与"拿到 root"是两件事。原语已确认；root 受 SELinux 域策略限制，逐项否定见 |
| [`index.md`](index.md) | 文档索引 |  ⚠️ 部分损坏 |
| [`official-source-request-log.md`](official-source-request-log.md) | Rakuten Hand 5G / TINNO P780 官方源码请求联络 | - 收件方：Sales@tinno.com（TINNO 官网公开的海外销售邮箱，不是已验证的开源源码专用邮箱）。 |

## docs/research（55）

| 文档 | 标题 | 备注 |
|---|---|---|
| [`apps-and-debloat.md`](research/apps-and-debloat.md) | P780 ADB 应用清理与设备维护实验（历史） | 2026-10-04，用户在已恢复出厂的实验用 P780 上执行一系列 ADB user 0 应用清理 和系统包信息收集；其目标之一是减少后台组件并保留可测试的基础 Android 功能。 |
| [`avb-attestation-alternative-20261018.md`](research/avb-attestation-alternative-20261018.md) | P780 AVB 研究：无需原厂镜像的硬件证明替代路径（2026-10-18） | 已知本机启动基线：green、locked、b、ro.boot.vbmeta.digest=33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2；根 vbmetab |
| [`avb-attestation-confirmed-20261018.md`](research/avb-attestation-confirmed-20261018.md) | P780 AVB 硬件证明与 AOSP 默认测试公钥匹配（2026-10-18） | - 机主正常运行 vvb2060/KeyAttestation 并将 P780-KeyAttestation.p7b 从手机下载后上传本轮私有会话。文件大小为 3475 bytes，PKCS#7 Signed Data，4 张 X.509  |
| [`avb-live-baseline-20261018.md`](research/avb-live-baseline-20261018.md) | P780 AVB 实机只读基线（2026-10-18） | 证据等级：用户在聊天中提供的实体机 ADB 原始输出；尚未将日志文件作为原件存入 Git。 不应把它标记为独立重测或完整分区取证。机型和此前的构建身份按 设备档案 为 P780 / Android 11 / P780AE11.0RMNJP1 |
| [`config-layout.md`](research/config-layout.md) | P780：24 项配置缺失与候选结构布局研究 | 日期：2026-10-10。研究对象为机主 P780 162 / 5.4.233-qgki-gea5245e94afe-dirty 的已归档配置；本轮仅做离线源码核对和 GitHub Actions 编译，不连接或修改手机。 |
| [`device-and-boot.md`](research/device-and-boot.md) | 实机硬件、系统、Bootloader、Fastboot、EDL 档案 | 来源：2026-06-12 EDL/fastboot 实验记录、2026-10-03 至 10-10 ADB 采集记录、hand5gkernel.txt、hand5gfastbootall.txt 和已保存 p780-config.gz。型 |
| [`firmware-advisory-20260928.md`](research/firmware-advisory-20260928.md) | Rakuten Hand 5G 固件真实性漏洞：JVN#47427200 / CVE-2026-107153 | 2026-10-14，Japan Vulnerability Notes 公布 JVN#47427200，把 Rakuten Mobile 早先只描述为“固件真实性确认机制缺陷”的问题具体归因为： |
| [`firmware-ota.md`](research/firmware-ota.md) | P780 固件 / OTA / 官方安全公告资料 | text |
| [`ghostlock.md`](research/ghostlock.md) | GhostLock (CVE-2026-43499) / P780 适配调查 | 详情请查看 2026-10-10 源码核对报告。 |
| [`google-ota-prober-p780-20261018.md`](research/google-ota-prober-p780-20261018.md) | Google OTA Prober × Rakuten Hand 5G (P780) \| 2026-10-18 | - ro.build.fingerprint=Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys. |
| [`journey-config.md`](research/journey-config.md) | P780 JourneyConfigService 实机 JAR 审计 | 日期：2026-10-10。输入为机主新采集的 services.jar、framework.jar、目录清单及 vendor 配置/TCS 无参数 dump；纯离线 DEX 反汇编及调用点扫描，没有执行网络替换、服务更新、Root 或固件 |
| [`ota-bugreport.md`](research/ota-bugreport.md) | P780 更新服务日志与 Android Bugreport 原始证据 | - hand5gupdateactivity.txt 是 Activity/系统状态记录，其中可见 SystemUpdate 相关组件名，但没有直接可复用的完整 OTA 文件。 |
| [`ota-log-audit.md`](research/ota-log-audit.md) | P780 OTA 日志与 Journey 配置服务核对 | 日期：2026-10-10。只读取已归档材料，并对日志中的无鉴权公共配置地址执行 HTTP/HTTPS GET；没有连接、修改手机或重放设备鉴权请求。 |
| [`p780-dirtyfrag-live-exploit-20261025.md`](research/p780-dirtyfrag-live-exploit-20261025.md) | P780 DirtyFrag 实机利用链（2026-10-25） | 设备基线（全部来自实机）： |
| [`p780-dirtyfrag-tinno-5.4.61-source-audit-20261024.md`](research/p780-dirtyfrag-tinno-5.4.61-source-audit-20261024.md) | TINNO P780 Linux 5.4.61：DirtyFrag 相关 UDP sendpage / ESP 源码审计 | 日期：2026-10-24（Asia/Shanghai） |
| [`p780-dirtyfrag-udp-esp-source-audit-20261024.md`](research/p780-dirtyfrag-udp-esp-source-audit-20261024.md) | P780 DirtyFrag / CVE-2026-43284：UDP sendpage 与 ESP 静态源码核对 | 日期：2026-10-24（Asia/Shanghai） |
| [`p780-dirtyfrag-v02-path-interpretation-20261024.md`](research/p780-dirtyfrag-v02-path-interpretation-20261024.md) | P780 DirtyFrag：v0.2 回环证据的含义与下一道安全门 | 日期：2026-10-24（Asia/Shanghai） |
| [`p780-dirtyfrag-v03-sendfile-probe-20261024.md`](research/p780-dirtyfrag-v03-sendfile-probe-20261024.md) | P780 DirtyFrag：v0.3.0 文件支持 UDP sendfile 预检 | 日期：2026-10-24（Asia/Shanghai） |
| [`p780-dsu-android15-avb-extraction-plan-20261018.md`](research/p780-dsu-android15-avb-extraction-plan-20261018.md) | P780 第十四轮：Android 15 GSI AVB 签名公钥 PC 离线提取方案（2026-10-18） | - 用户 PC 已实际获取、上传并由助手验证 SHA256 的 Google DSU 根索引与 vic 子目录 JSON，目标精确匹配P780菜单的 Android15 非GMS ARM64记录：arm64-exp-BP1A.250405. |
| [`p780-dsu-android15-avb-key-verified-20261018.md`](research/p780-dsu-android15-avb-key-verified-20261018.md) | P780 DSU 第十五轮：Android15 GSI 内嵌 AVB 公钥已取得，确认 Q Developer GSI，根因仍待 P780 Ramdisk（2026-10-18） | 用户上传5个文件：p780-gsi15-avb-report.txt、system.img.avb-info.txt、system.img.avbpubkey、vbmeta.img.avb-info.txt、vbmeta.img.avbpu |
| [`p780-dsu-bugreport-audit-20261018.md`](research/p780-dsu-bugreport-audit-20261018.md) | P780 第十三轮：首次 DSU 失败后的 Android Bugreport 全量离线审计（2026-10-18） | - 用户从 P780 在原厂系统中运行 adb bugreport 导出 P780-DSU-Bugreport.zip 并上传本轮对话。Python zipfile.ZipFile.testzip() 全部通过，无损坏。 |
| [`p780-dsu-closure-maintenance-route-20261018.md`](research/p780-dsu-closure-maintenance-route-20261018.md) | P780 DSU 实机阶段收束与原厂维护接口路线（2026-10-18） | 2026-10-18 20:31（Asia/Shanghai），机主明确停止 DSU 路线，转向其它研究。停止重复安装、Restart、改签名和 DSU 参数试验。不能把“回原厂”写成“已证实厂商禁止 DSU”。 |
| [`p780-dsu-custom-testkey-gsi-hypothesis-20261018.md`](research/p780-dsu-custom-testkey-gsi-hypothesis-20261018.md) | P780 DSU 第十六轮：CVE-2026-107153 公共 AVB 测试根密钥 × 自签名 GSI × DSU Sideloader 可行性（2026-10-18） | 1. JVN#47427200 / CVE-2026-107153 于2026-10-14确认 Rakuten Hand5G 全版本在Android Verified Boot使用AOSP已知测试密钥，风险为有物理访问时可能安装经特殊构造的 |
| [`p780-dsu-first-trial-protocol-20261018.md`](research/p780-dsu-first-trial-protocol-20261018.md) | P780 DSU 首次实机试验协议（2026-10-18） | 已有本机证据：Android 11 P780、ARM64、VNDK 30、Treble、[vendor] namespace.default.isolated=true、A/B 动态分区、F2FS、存储可用约103GB、官方 com.and |
| [`p780-dsu-gsi-catalog-verified-20261018.md`](research/p780-dsu-gsi-catalog-verified-20261018.md) | P780 DSU 第八轮：Google 六个子目录原始 JSON 完整验证（2026-10-18） | - 机主 Windows Python 审计脚本产生的 p780-dsu-catalog-detail.zip（本聊天附件），4073 字节，SHA-256 ad732d61aa7751aeaa6f2a148e3a1998aeee645be |
| [`p780-dsu-locked-bl-vs-gsi-trust-20261018.md`](research/p780-dsu-locked-bl-vs-gsi-trust-20261018.md) | P780 DSU 锁定 Bootloader 与 GSI 签名信任机制专项核验（2026-10-18） | 机主问“是否仍有系统限制导致未解锁 BL 的情况下不能加载 DSU”。已有 P780 Android 11 固件 162 的真机： |
| [`p780-dsu-locked-gsi-20261018.md`](research/p780-dsu-locked-gsi-20261018.md) | P780 Android 11 DSU / GSI 可信启动支线 — 源码交叉核对（2026-10-18） | 2026-10-18 机主读取并作为会话内容提交 /vendor/etc/fstab.default、/vendor/etc/fstab.emmc，两者 system 行均含： |
| [`p780-dsu-readonly-followup-20261019.md`](research/p780-dsu-readonly-followup-20261019.md) | DSU-READ-01：恢复出厂后的状态与现有GSI兼容性补证（2026-10-19） | 本轮按机主新要求重新开放 DSU只读取证，不恢复安装/Restart/改签名试验。新增证据是：当前安装状态已不同于失败现场；实际vendor声明FCM5；PC已有A镜像包含FCM5矩阵，选中的5.4内核配置子集未发现冲突。仍未确定历史回退根 |
| [`p780-dsu-stock-fallback-20261018.md`](research/p780-dsu-stock-fallback-20261018.md) | P780 第十轮 DSU 首次试机：下载完成后重启仍返回原厂系统（2026-10-18） | text |
| [`p780-dsu-testroot-resign-verified-20261018.md`](research/p780-dsu-testroot-resign-verified-20261018.md) | P780 DSU 第十七轮：真实 Android 15 GSI 使用 AOSP 测试根密钥离线重签并通过 AVB 验证（2026-10-18） | 真实报告中的输入 system.img SHA256：27321f9655530f014c884a690f49a53e6f3beeda71f4f27cbc141b17a8e86954。 |
| [`p780-dsu-trust-chain-audit-20261018.md`](research/p780-dsu-trust-chain-audit-20261018.md) | P780 DSU 第九轮 — AVB/GSI 信任链源码审计与公开公钥二进制核对（2026-10-18） | 1. Settings 菜单元数据初筛： DSULoader.java 读取远端 JSON 的 ABI/OS/SPL 等以及可选的 vndk、pubkey 字段。第八轮实测 Google 六子目录共24条均无 vndk、pubkey；这解释 |
| [`p780-evidence-gap-audit-20261019.md`](research/p780-evidence-gap-audit-20261019.md) | GAP-01�����в��ԡ��ں�֤������ļ���ʵ��2026-10-19�� | ���ֲ��������ȱ�ڣ��ɹ�ȡ�������� SELinux policy ԭ�����ֻ��ں�������10��10���������ֽ�һ�£�journey.factory.rc ȷΪ���ֽ��ļ��� δ�õ��µ ⚠️ 部分损坏 |
| [`p780-fstab-avb-20261018.md`](research/p780-fstab-avb-20261018.md) | P780 fstab AVB 挂载配置实机取证（2026-10-18） | 证据类型：用户通过普通 ADB shell 提供的两个文件文本（会话附件），已核对 5 行 AVB 挂载声明。并非原始 fstab 文件字节哈希或实际 Bootloader vbmeta.img 的签名描述符。 |
| [`p780-ipsec-preflight-live-and-localversion-20261024.md`](research/p780-ipsec-preflight-live-and-localversion-20261024.md) | P780 IPsec Preflight 实机结果与内核版本后缀来源核验 | 日期：2026-10-24（Asia/Shanghai） |
| [`p780-ipsec-v0.2-api-cts-design-20261024.md`](research/p780-ipsec-v0.2-api-cts-design-20261024.md) | P780 IPsec diagnostics 0.2.0: Android 11 API/CTS basis and safety boundary | Date: 2026-10-24 (Asia/Shanghai) |
| [`p780-ipsec-v0.2-live-loopback-20261024.md`](research/p780-ipsec-v0.2-live-loopback-20261024.md) | P780 IPsec diagnostics 0.2.0 实机 UDP/ESP 回环结果 | 日期：2026-10-24（Asia/Shanghai） |
| [`p780-native-interface-crosscheck-20261018.md`](research/p780-native-interface-crosscheck-20261018.md) | P780 native接口、JAR与SELinux交叉核对 | 2026-10-18，纯PC静态分析；没有运行手机二进制、Binder/HIDL请求、socket连接、属性修改或分区操作。 |
| [`p780-native-live-endpoints-20261019.md`](research/p780-native-live-endpoints-20261019.md) | NATIVE-01：P780 运行端点与诊断 JNI 失败链（2026-10-19） | 结论：补齐了旧 native 矩阵缺失的诊断 Java 调用方和运行身份。QTIDiagServices 的启动日志显示 JNI 初始化因诊断 HIDL 连接失败而退出；这不是可用的 OEM 管理代理。Journey 两个 root 诊断进 |
| [`p780-oemlock-caller-boundary-20261019.md`](research/p780-oemlock-caller-boundary-20261019.md) | OEMLOCK-02：设置调用者与权限边界（2026-10-19） | 结论：getter/setter 的 customer 检查差异仍成立，但在本轮现有语料中没有发现普通应用/ADB shell可达的特权设置入口。该候选停止作为上机实验；未解锁、未Root、未改变手机状态。 |
| [`p780-oemlock-first-results-20261019.md`](research/p780-oemlock-first-results-20261019.md) | P780 OEMLOCK-01 第一阶段实测结果（2026-10-19） | 状态：第一阶段已实测，第二阶段只读分支诊断待进行。没有解除解锁限制、Root或改变设备持久状态。 |
| [`p780-oemlock-gate-probe-20261019.md`](research/p780-oemlock-gate-probe-20261019.md) | P780-OEMLOCK-01: OEM Unlock 灰色开关的限制来源 | 2026-10-19。状态：第一、第二阶段已实机执行；第三阶段进入现有 Settings APK 离线审计。不推断 Bootloader 解锁或 Root 已实现。 |
| [`p780-oemlock-journey-gate-20261019.md`](research/p780-oemlock-journey-gate-20261019.md) | OEMLOCK-01：Journey customer gate 离线定位（2026-10-19） | 结论：已定位解释灰色开关的厂商服务端条件。不是联网授权服务器的证据；没有 Root、BL 解锁或可用写入入口。本轮仅读取 PC 已存文件和仓库，未访问手机。 |
| [`p780-perf-permission-probe-20261025.md`](research/p780-perf-permission-probe-20261025.md) | P780 perf permission v0.1.0（2026-10-25） | 状态更新：机主已提供 P780 v0.1.0 用户态计数实机 PASS 日志，见结果报告。下文保留工具交付阶段的范围和验证记录；内核/寄存器采样仍未测试。 |
| [`p780-perf-v010-live-result-20261025.md`](research/p780-perf-v010-live-result-20261025.md) | P780 perf v0.1.0 实机结果（2026-10-25） | 结论：普通 ADB shell 下，自身线程用户态软件 CPU-clock 计数链 PASS。 不是 kernel/register sampling PASS，更不是 GhostLock 可用或 Root 成功。 |
| [`p780-policy-boundary-audit-20261018.md`](research/p780-policy-boundary-audit-20261018.md) | P780 SELinux ԭ����ƣ�Journey ���������socket��2026-10-18�� | P780-policy-20261018-222940.zip��SHA256 85f6d86d7d3d33ba940afacca6350527848ce07e29961ab92129ffcdb70a82a1��CRCͨ����55���豸 ⚠️ 部分损坏 |
| [`p780-policy-header-verification-20261020.md`](research/p780-policy-header-verification-20261020.md) | GAP-01 header 原件复核（2026-10-20） | 结论：两份 PC 原件哈希与 10/19 归档一致；旧专题把 header config 的两端写反，现已纠正。独立 SETools 语义比较仍为 BLOCKEDTOOLING，不升级为运行策略完全等价。 |
| [`p780-qdl-qud-sahara-20261019.md`](research/p780-qdl-qud-sahara-20261019.md) | P780 EDL / QDL QUD 通信突破与 Mannar Loader 待测（2026-10-19） | 2026-10-19，机主在 Windows x64 上用 linux-msm/qdl v2.8 官方 Release 的 Windows x64 二进制执行 qdl list 和 qdl chipinfo --backend=qud -- |
| [`p780-source-availability-followup-20261024.md`](research/p780-source-availability-followup-20261024.md) | P780 _162 原厂内核源码与固件工件可得性复核 | 日期：2026-10-24（Asia/Shanghai） |
| [`p780-static-batch1-analysis-20261018.md`](research/p780-static-batch1-analysis-20261018.md) | P780 静态样本 batch1 原件验证与交叉分析（2026-10-18） | 收到P780-static-analysis-batch1.zip，CRC全包通过，SHA256 340765c47e7a9bc8d96b6eb368902117ce631d84a3d34ca0ae1d0eff2e92ca3b。743个ZI |
| [`p780-static-batch2-analysis-20261018.md`](research/p780-static-batch2-analysis-20261018.md) | P780 system/lib64 第二批静态分析（2026-10-18） | 本次只在电脑读取上传文件，未在手机执行二进制、设置属性、连接诊断 socket、写分区或重启。设备仍无已证实的 Root/解锁能力，DSU 路线保持停止。 |
| [`p780-static-corpus-inventory-20261018.md`](research/p780-static-corpus-inventory-20261018.md) | P780 ʵ����̬������һ���嵥��ˣ�2026-10-18�� | ����ָ��ԭ������/ά��APK��ǰ���Ų��������������ܽ��ظ�APK���ð����·�ߡ����׶�תΪ�㸲�Ǿ�̬�������⡢init����ܡ�native���ü��汾���������DSUֹͣ ⚠️ 部分损坏 |
| [`p780-supplement-20261024.md`](research/p780-supplement-20261024.md) | P780 补充情报整理：2026-10-24 | 新增价值集中在 VINTF分片与OTA验证证书，没有发现可确认的解锁、Root或固件写入通道。全程仅ADB读取与PC离线解析，没有设置属性、安装、DSU切换或重启。 |
| [`public-p780ae-device-tree-audit-20261024.md`](research/public-p780ae-device-tree-audit-20261024.md) | 公开 P780AE 设备树候选审计（2026-10-24） | 2026-10-24 检索发现公开仓库 2by2-Project-Devices/androiddevicerakutenp780ae。仓库创建于 2026-10-14，默认分支 lineage-23.2；截至核验时只有该分支、无 Rele |
| [`qas-tee-pfm.md`](research/qas-tee-pfm.md) | QAS → Mink → PFM → TZAccessService：已知事实索引 | 2026-10-04 对真实 P780 提取的应用、库与日志进行静态分析，详细原始报告已永久提交至： |
| [`tee-system-apks.md`](research/tee-system-apks.md) | P780 TrustZone 白名单、JNI 访问记录及系统 APK 原件 | 本章节根据机主上传到 GitHub 的真实文件编写，并与 2026-10-04 QAS/Mink/PFM 分析 对照。静态内容与实时鉴权的成功与否必须分开看。 |

## docs/reference（3）

| 文档 | 标题 | 备注 |
|---|---|---|
| [`archive-protocol.md`](reference/archive-protocol.md) | P780 证据归档规范 | 本仓库用于长期交接与跨对话续接。所有研究条目最少应说明： |
| [`evidence-integrity.md`](reference/evidence-integrity.md) | P780 核心证据完整性校验（2026-10-10） | 这是 GitHub Actions Linux Runner 对已上传 Git 仓库版本的原始文件进行的 SHA-256、GZIP/ZIP 解码与 ZIP CRC 检查。由流水线自动打印完整结果，本文为持续保存的审计摘要。 |
| [`sources.md`](reference/sources.md) | 来源、引用和可重复性 | 仓库主来源：实际持有的 TINNO P780，从 2026-06-12 至 2026-10-10 各阶段采集的 ADB、Fastboot、Sahara 和应用/内核证据。 |

## docs/archive（7）

| 文档 | 标题 | 备注 |
|---|---|---|
| [`20261010-archive-review.md`](archive/20261010-archive-review.md) | Rakuten Hand 5G / P780：2026-10-10 阶段归档验收 | 验收日期：2026-10-10 |
| [`20261010-import-dedup.md`](archive/20261010-import-dedup.md) | 2026-10-10 新增实体机资料接收、比对与去重报告 | 在整理前，对仓库全部文件进行了 Git Blob（字节身份）分组，并额外通过 GitHub Actions 运行 tools/auditnewuploads.py 对 ZIP 内容与展开目录的单个文件做 SHA-256 核对。这比仅比较同名 |
| [`dsu-index-20261018.md`](archive/dsu-index-20261018.md) | DSU历史专题索引 | 2026-10-18机主已停止DSU路线。先读阶段收束：B已安装并尝试启动、最终回原厂，失败阶段未知；没有GSI启动、Root或解锁成功。下列文档保留当时方案、观察、源码依据和中间假设，不是当前操作清单。 |
| [`evidence-ledger-before-consolidation-20261018.md`](archive/evidence-ledger-before-consolidation-20261018.md) | P780 已定位研究文件总清单 | - 收到机主当前会话三份原始审计小文件：original-avb-info.txt 1549B SHA256 b7e4890bc061b2228d280bdbdd5a687db51ed9edfba403e10cec62293faa26e1； |
| [`ghostlock-package-versions.md`](archive/ghostlock-package-versions.md) | GhostLock P780 离线研究包：v0.1—v0.4 | 关于 v0.4 的原件内部不一致：压缩包外层目录与文件名标注为 v0.4，但其内部 README.md 首行仍写“适配工程 v0.3”。这属于保留的历史打包瑕疵，不能因此将 ZIP 误认作另一个 v0.3，也不应篡改历史 ZIP 原件。区分 |
| [`next-steps-before-dsu-20261018.md`](archive/next-steps-before-dsu-20261018.md) | 历史研究计划快照（2026-10-18 DSU 研究之前） | - 已完成：机主上传本机 KeyAttestation PKCS#7；Google 官方 2019 硬件证明根证书 DER 一致、4 张证书签名全有效，TEE/Keymaster 均 TrustedEnvironment，deviceLoc |
| [`repository-audit-20261011.md`](archive/repository-audit-20261011.md) | 2026-10-11 全库结构整理验收 | 基准提交：af103577c223c905a26924d623afb220397c34ff；完整递归树未截断，共 254 个文件。本轮是研究档案整理，研究进入待机；未取得 Root、BL 解锁或匹配原厂固件。 |

## tools（9）

| 文档 | 标题 | 备注 |
|---|---|---|
| [`README.md`](../tools/README.md) | 工具 | 历史脚本见 ../archive/scripts。 |
| [`README.md`](../tools/dirtyfrag-probe/README.md) | DirtyFrag 探针工具（P780） | 本目录收录 2026-10-25 实机专题用到的全部离线工具与载荷源码，配套报告见 |
| [`README.md`](../tools/dsu/README.md) | DSU read-only follow-up tools | Python standard-library tools for exported P780 files and the existing raw ext4 Android15 A image. No image download, mo |
| [`README.md`](../tools/gaps/README.md) | Evidence gap tools | comparepolicyrecords.py and verifypolicycomparator.py are offline Python-standard-library tools. They read original PC p |
| [`README.md`](../tools/ipsec-preflight-android/README.md) | P780 / Android 11 IPsec and UDP diagnostics (non-exploit) | Version: 0.3.0 |
| [`README.md`](../tools/native/README.md) | P780 diagnostic offline audit | These tools read exported files on the PC. They do not connect to or execute code on the phone. |
| [`README.md`](../tools/oemlock/README.md) | OEM Lock offline audit | Requires Python and androguard 4.1.4. Based on the repository's readperformancedex.py table reader. No device or network |
| [`README.md`](../tools/perf-permission/README.md) | P780 perf 最小权限探测 v0.1.0 | 目标：仅验证 Android ADB shell（UID 2000）能否创建、启用、读取并关闭自身线程的用户态 perf 软件计数事件。 |
| [`README.md`](../tools/supplement/README.md) | P780 supplemental evidence tools | The fixed ADB collector exports selected VINTF directories, the public OTA certificate archive, and a small baseline/boo |

## archive（旧仓库）（6）

| 文档 | 标题 | 备注 |
|---|---|---|
| [`README.md`](../archive/README.md) | 旧研究成果归档 | reports/ 保存完整 Markdown 技术报告，包括 QAS/ PFМ /Mink /TZ、GhostLock 源码核对。 |
| [`P780_loaded_module_names.md`](../archive/device/P780_loaded_module_names.md) | P780 2026-10-10 实机模块观察（按原文件保留名称） | 来源：先前保存的 P780-module-inventory.txt（UTF-16）中 === Loaded kernel modules === 部分。此处仅列出已成功恢复的模块名称；故意不推断所有 .ko 文件均可读取，也没有复制内核地 |
| [`P780_GhostLock_source_audit_2026-10-10.md`](../archive/reports/P780_GhostLock_source_audit_2026-10-10.md) | Rakuten Hand 5G (P780) / GhostLock 源码核对报告 | <!-- Historical research report, preserved from an earlier user-provided artifact. Not a fresh assertion; see docs/STATU |
| [`P780_MinkNative_2026-10-04.md`](../archive/reports/P780_MinkNative_2026-10-04.md) | P780：Mink 原生层与 PFM 运行证据 | <!-- Historical research report, preserved from an earlier user-provided artifact. Not a fresh assertion; see docs/STATU |
| [`P780_PFM_QAS_2026-10-04.md`](../archive/reports/P780_PFM_QAS_2026-10-04.md) | Rakuten Hand 5G P780：QAS → Mink → PFM 研究检查点 | <!-- Historical research report, preserved from an earlier user-provided artifact. Not a fresh assertion; see docs/STATU |
| [`P780_TZAccess_2026-10-04.md`](../archive/reports/P780_TZAccess_2026-10-04.md) | P780：TZAccessService 服务端 Java 授权链 | <!-- Historical research report, preserved from an earlier user-provided artifact. Not a fresh assertion; see docs/STATU |


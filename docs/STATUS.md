# 当前研究状态

更新：2026-10-19（Asia/Shanghai）。这是当前结论的统一入口；逐轮细节见 [时间线](HISTORY.md) 和专题。**Locked / 未 Root / 未取得已验证的永久分区写入能力。DSU 已停止。**

## 设备与版本基线

|字段|已记录值|边界|
|---|---|---|
|设备|Rakuten Hand 5G / TINNO P780；Qualcomm holi / mannar|不是联发科平台|
|固件|Android 11；`P780AE_11.0_RMN_JP_162` / `_162_CFC`|内部构建与 fingerprint 编号不同|
|Fingerprint|`Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`|不可用 162 替换其中 264|
|内核|`5.4.233-qgki-gea5245e94afe-dirty`；Android Clang 11.0.2 r383902b1|候选源码不是出厂二进制|
|启动状态|`flash.locked=1`，verified boot `green`；历史活动槽 `_b`|每次采集的快照，不保证以后不变|

来源：[设备](research/device-and-boot.md)、[AVB 基线](research/avb-live-baseline-20261018.md)、[回退后状态](research/p780-dsu-closure-maintenance-route-20261018.md)。恢复出厂后的包状态不得沿用先前精简快照。

## 路线与结果

|路线|已证实或已完成|剩余缺口 / 决策|
|---|---|---|
|AVB 公钥身份|本机硬件证明证书签名链及 Google 根匹配；`verifiedBootKey` 匹配 AOSP AVB RSA4096 默认测试公钥；`verifiedBootHash` 匹配本机 digest|在线吊销完整校验未完成；真实 VBMeta chain descriptors、rollback index 及原厂镜像仍缺。见[确认报告](research/avb-attestation-confirmed-20261018.md)|
|Fstab / 动态分区|两份 fstab 已读；system/system_ext/product 使用 `avb=vbmeta_system`，vendor/odm 默认 avb；system 列 q/r/s-GSI key 路径|配置不能替代真实描述符和 first-stage 实际公钥。见[fstab](research/p780-fstab-avb-20261018.md)|
|DSU A/B|Windows A/B 均通过 AVB 验证；B 已由原生安装器安装并触发 dynsystem 重启，最终回到原厂，installed/disabled|**停止**。未启动 GSI；失败阶段未知。恢复出厂后原生 Loader 回退是机主观察，镜像身份未核实。见[收束](research/p780-dsu-closure-maintenance-route-20261018.md)|
|OEM Unlock 灰色开关|原件离线定位服务端 carrier getter 额外要求 !JourneyDebugFeature.IS_CUSTOMER_VERSION；framework初始化读取 ro.boot.journey.customer；两份历史同fingerprint快照为1；本轮ADB再次读到customer=1，解释PDB/无用户限制仍灰色|静态根因已定位；2026-10-19重新pull的services.jar SHA匹配历史，未复核当前内存。OEMLOCK-02已扫描296份APK/JAR，仅6个直接调用点；确认链及signature/privileged权限已核验，现有语料未找到可达写入入口。见[OEMLOCK-02调用者边界](research/p780-oemlock-caller-boundary-20261019.md)及[Journey gate](research/p780-oemlock-journey-gate-20261019.md)|
|native运行端点 / 诊断JNI|QTIDiagServices、libDiagService、services三份现机原件SHA匹配历史；补齐16个DEX方法体和JNI CFI实现；启动日志定位Diag_LSM_Init连接HIDL失败；两项Journey root诊断服务正在运行|诊断APK在已审入口内没有OEM代理；HIDL失败最终原因未定。vendor服务端读取被拒绝，Journey init builtin实现仍缺。见[运行交叉报告](research/p780-native-live-endpoints-20261019.md)|
|Fastboot / EDL|常见 unlock 命令 unknown command；2026-10-19 QDL v2.8 使用 Windows QUD/COM6 读到 Sahara v2/HWID/PKHash，与早期实测吻合|已验证 Sahara command-mode，**A 曾进行早期 READ64，B–E 仅离线分析；A–E 共3组签名根均与本机 PKHash 不符，未成功运行 Firehose**；未取得可用签名 Loader 或原厂 boot/vbmeta。见[实测报告](research/p780-qdl-qud-sahara-20261019.md)|
|OTA|6 份历史引擎日志没有 payload；正确 fingerprint 的 Google OTA Prober 查询未返回 URL|**暂缓重复探测**。不证明所有厂商渠道均无包。见[OTA 审计](research/ota-log-audit.md)、[查询](research/google-ota-prober-p780-20261018.md)|
|源码与内核构建|真实 config.gz 5238 个明确配置项；匹配 Clang11 编译 rtmutex.o；A52s 候选配置值变化0、消失24、新增322；两棵候选树32项布局采样一致|不是原厂 vmlinux/ABI。TINNO 旧5.4.61原生求解消失46、新增14；不同实验数字不可混用。见[布局](research/config-layout.md)|
|GhostLock|旧源码模式、配置、Tracefs 与四代工作包归档|**BLOCKED**：缺运行内核漏洞确认、二进制/符号/逐构建偏移。见[专题](research/ghostlock.md)|
|Journey 应用配置|TCS/vendor XML 版本42、64键按 ALL 假设一致；消费者定位到进程与 Service/Provider 策略|已审查路径未见密码学验签，但无 OTA/Root 链；不重复作为新工程入口。见[专题](research/journey-config.md)|
|QAS / Mink / PFM|class119、eMBMS feature700、XR feature2100及部分代理日志；UID/PID和凭据路径已有分析|代理创建不等于授权成功；未连接 OEM Unlock。见[专题](research/qas-tee-pfm.md)|
|静态样本|1759项PC清单；batch1 742项、batch2 514项逐项匹配；政策包55设备文件+日志|清单不是完整固件，ZIP未全量入Git；vendor/bin和vendor/lib64尚无采集内容。见[证据索引](EVIDENCE_MANIFEST.md)|
|Journey init / SELinux|编译策略允许 shell 设置 debug_prop，覆盖部分 sys.journey 属性；config.write、ODM reset及默认vendor开关无同等allow|只有静态候选；init注册/参数限制/运行标签/服务实现缺失；四个可执行文件元数据查询 Permission denied，不重复尝试。见[策略](research/p780-policy-boundary-audit-20261018.md)|
|native 接口交叉|Diag JNI→diag库→HIDL依赖、QSEE HIDL封装、Mink JNI→传输库已区分；6个所选域的36项策略查询未见allow|尚无可直接调用的提权入口；服务端和具体方法鉴权未齐。见[交叉报告](research/p780-native-interface-crosscheck-20261018.md)|
|官方源码申请|已向 TINNO 发送请求；既有2026-10-18检索未发现厂商回复|本轮未重新检索邮箱；发送日期有10/10与10/11记录差异，待邮件头核对。Rakuten暂不联系。见[联络记录](official-source-request-log.md)|

## 核心摘要及解释边界

- AVB 公钥 SHA-256（1032字节 AVB 表示）：`7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6`。
- 本机 VBMeta digest：`33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`；加载 VBMeta 总长度7744字节，不是单分区长度。
- B整镜像 SHA-256：`fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880`。此值及A/B数据段一致性来自机主PC输出，助手没有完整1.9GB镜像独立重算。
- 通用 `write_misc_partition` 不等于厂商 `write_misc` builtin；DT_NEEDED/符号名不是完整调用图；未命中字符串不证明实现不存在。
- 磁盘预编译 SELinux 策略与配套摘要吻合，不是运行内核策略 dump；单个 allow、root UID、socket 0666 均不能单独证明端到端操作成功。

证据分为：实机原始输出/机主观察、原件静态分析、公开源码或第三方参考、未验证假设。每项注明来源，不将不同等级互相替代。下一步统一见 [行动清单](NEXT_STEPS.md)。

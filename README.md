# Rakuten Hand 5G / TINNO P780 研究档案

更新：2026-10-19（Asia/Shanghai）。记录机主实机取证、离线样本分析与候选源码实验。**Bootloader 仍 Locked，未取得 Root；没有已验证的锁定态永久分区写入通道。**

设备：Qualcomm 平台（holi / mannar），Android 11，内部固件 `P780AE_11.0_RMN_JP_162`，系统指纹末段 `264:user/release-keys`，内核 `5.4.233-qgki-gea5245e94afe-dirty`。`_162` 与指纹中的 `264` 是不同版本字段。

## 当前结论

|方向|已取得的证据|当前状态|
|---|---|---|
|AVB 测试根密钥|本机 TEE 硬件证明中的公钥摘要匹配 AOSP 默认 RSA4096 AVB 测试公钥；VBMeta digest 同时吻合|公钥身份已核验；不等于可写入或解锁|
|DSU / GSI|A/B 在 Windows 验签通过；B 已安装并尝试启动，最终回原厂；恢复出厂后原生 Loader 也由机主报告回退|**路线已停止**；失败阶段未知，不能认定厂商禁止 DSU|
|静态样本与权限|PC 清单 1759 项；batch1 742 项、batch2 514 项匹配清单；另有 SELinux 配套文件与编译策略|当前主线：调用关系、权限边界与缺失实现交叉分析|
|Journey / Qualcomm 接口|Journey debug 属性存在 shell 静态 allow；取得部分 JNI/HIDL 客户端库|未形成任意读写或提权链；关键 init/vendor 服务原件缺失|
|原厂固件、EDL、源码|2026-10-19：QDL v2.8 经 QUD/COM6 成功查询 Sahara v2/HWID/PKHash；TINNO 旧源码及候选构建已归档|尚未上传/认证 Firehose Loader；仍缺匹配原厂镜像和运行内核身份|
|GhostLock|配置、旧源码模式及候选布局已有分析|**BLOCKED**；不得把候选偏移当本机参数|

## 阅读入口

- [当前状态与证据边界](docs/STATUS.md)：全路线结果、尚不能推出的结论。
- [下一步](docs/NEXT_STEPS.md)：只保留尚未完成、满足条件才推进的任务。
- [文档导航](docs/README.md)：按问题索引所有专题，DSU 历史单独归类。
- [证据资产清单](docs/EVIDENCE_MANIFEST.md)：区分 Git 原件、提取摘要、机主 PC 与会话材料。
- [时间线](docs/HISTORY.md) · [本轮整理验收](docs/REPOSITORY_AUDIT.md) · [更新日志](CHANGELOG.md)。

最新实机进展：[QDL QUD/Sahara 握手成功](docs/research/p780-qdl-qud-sahara-20261019.md)。最新分析：[native 接口交叉核对](docs/research/p780-native-interface-crosscheck-20261018.md)、[SELinux 边界](docs/research/p780-policy-boundary-audit-20261018.md)、[batch2](docs/research/p780-static-batch2-analysis-20261018.md)。核心证据：[AVB 硬件证明](docs/research/avb-attestation-confirmed-20261018.md)、[DSU 阶段收束](docs/research/p780-dsu-closure-maintenance-route-20261018.md)。

## 仓库结构与维护

|目录|职责|
|---|---|
|[docs/](docs)|当前状态、行动清单、证据索引与时间线|
|[docs/research/](docs/research)|专题；历史试验页在页首标记状态|
|[docs/reference/](docs/reference)|来源、归档规范与完整性记录|
|[docs/archive/](docs/archive)|冻结的阶段账本与结构验收|
|[evidence/](evidence)|原件、提取证据、逐运行构建产物；保存范围见索引|
|[archive/](archive)|旧报告、设备摘要与历史脚本|
|[tools/](tools)|分析与验证工具，依赖和设备影响见工具说明|
|[.github/workflows/](.github/workflows)|归档完整性检查；候选构建与历史迁移为手动工作流|

当前结论只在 STATUS 汇总；专题保存证据细节，HISTORY/CHANGELOG 保存时间顺序。每阶段修订正文与索引，不再向所有入口重复追加同一通知。例行查询无新证据时不制造研究成果。

仓库含未经发布级脱敏的历史资料；`restricted` 只是分类，不能提供目录级访问控制。原始硬件证明证书不入仓。可见性及历史风险见 [SECURITY](SECURITY.md)。自动监测是否运行须查实际任务状态，文档中的历史“已启用”不是当前运行凭据。

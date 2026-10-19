# 证据资产与保存状态

更新：2026-10-19。此页按资产组织，不再将每轮“待测”计划当资产重复追加。当前技术结论见 [STATUS](STATUS.md)；完整旧文件名、来源大小及阶段摘要保存在[冻结的历史账本](archive/evidence-ledger-before-consolidation-20261018.md)。

## 保存等级

|等级|含义|
|---|---|
|Git原件|仓库保存可重新读取的原始字节；可逆Base64另行标注|
|Git提取证据|只存哈希/清单/符号/反汇编/分析；不能据此宣称整个输入已入仓|
|机主PC/会话原件|已用于分析或由机主报告，但未将原件放入Git|
|未取得|没有可信原件；文件名、路径、错误日志不代替内容|

## OEMLOCK-01 新增离线证据（2026-10-19）

Settings/framework/services三个PC原件重新计算SHA，Settings匹配旧manifest，后两者匹配DSU专题；大原件留PC。[输入清单](../evidence/oemlock/20261019/manifest.json)、[15方法原始指令/反汇编](../evidence/oemlock/20261019/focused-methods.json)、[历史属性脱敏选行](../evidence/oemlock/20261019/property-excerpts.json)进入Git。全量目标解码114方法，仅提交关键15方法；长度覆盖检查通过，不等于完整调用图或运行内存验证。见[Journey gate离线定位](research/p780-oemlock-journey-gate-20261019.md)。

## 当前静态样本

|资产|核验结果|Git保存范围|
|---|---|---|
|PC采集manifest|1759项，1131297358字节；覆盖并不完整|[manifest.csv](../evidence/static/20261018-220912/manifest.csv)；[采集范围和缺口](research/p780-static-corpus-inventory-20261018.md)|
|batch1 ZIP|742个文件条目全部匹配PC清单；194 RC、285 service声明、381 ELF条目（含编译产物）|[验证/索引JSON](../evidence/static/20261018-220912/batch1-verified-analysis.json)、[报告](research/p780-static-batch1-analysis-20261018.md)；ZIP/全部原件未入Git|
|batch2 ZIP|514项全部匹配；279493296字节；509 ELF+5 bitcode|[摘要JSON](../evidence/static/20261018-220912/batch2-verified-analysis.json)、[报告](research/p780-static-batch2-analysis-20261018.md)；完整逐项哈希由PC manifest覆盖；ZIP未入Git|
|policy ZIP|55份设备文件+pull.log；CRC通过；ODM预编译策略881104字节；3组CIL/mapping摘要匹配|[逐文件哈希和查询](../evidence/static/20261018-222940/policy-audit.json)、[报告](research/p780-policy-boundary-audit-20261018.md)；策略二进制未入Git|
|native接口交叉|6个库的依赖/相关动态符号，36项策略查询；73 JAR/DEX定向字符串扫描|[机器证据](../evidence/static/20261018-220912/native-interface-crosscheck.json)、[报告](research/p780-native-interface-crosscheck-20261018.md)|

三个ZIP SHA-256：

- batch1：`340765c47e7a9bc8d96b6eb368902117ce631d84a3d34ca0ae1d0eff2e92ca3b`
- batch2：`31aa1878b46a71fd960b7bdc5044e1a5421a2f8e6400bf919873e1efa62e5ce2`
- policy：`85f6d86d7d3d33ba940afacca6350527848ce07e29961ab92129ffcdb70a82a1`

批次计数是文件条目数，不保证路径或内容互斥，不能相加称为去重后的完整固件。0文件的vendor/bin/vendor/lib64采集结果和空journey.factory.rc均不能用于不存在/无功能结论。

## 2026-10-19 EDL 通信实测

|资产|保存状态与边界|
|---|---|
|QDL v2.8 Windows x64 `list` / `chipinfo`|机主PC及当前会话日志；已核对 Sahara v2/HWID/PKHash 与 2026-06-12 记录一致；原始串号与完整 PKHash 未入Git。见[专题](research/p780-qdl-qud-sahara-20261019.md)|
|bkerler/edl v3.62 COM6 NOP 失败日志|机主PC/会话终端文本，报告仅存脱敏阶段判断；`END_TRANSFER status 1` 后旧式 Streaming 卡住，不代表 Loader 签名拒绝|
|Mannar 通用 Firehose 候选 A|第三方 GitHub 源码仓中的候选文件，匹配 MSM 但 model/PKHash 前缀不同；实机已请求4段 Sahara READ64 后通信失败，未完成认证或 Firehose 启动；原始日志只在机主PC/会话，二进制未入仓；同日离线解析获得 Qualcomm/MODEL=0000/HWID=全零/VAR=MannarPkgLAB，根证书 PKHash=`d9357db8…`（与本机不符），详见专题|

|B–E 批量签名离线解析|原始批次因现有 Loaders 去重跳过3文件，临时副本关闭去重后两份日志均列出 B–E。A–E 共5文件、3组根摘要 d935/4352/a51a，均与本机 c19a 不符；原始终端日志和二进制不入仓，见[矩阵](research/p780-qdl-qud-sahara-20261019.md)|

## AVB与已停止DSU实验

|资产|保存状态与边界|
|---|---|
|硬件证明.p7b|不入Git；[脱敏报告](research/avb-attestation-confirmed-20261018.md)保存根/公钥摘要和验证方法；在线吊销校验不完整|
|AVB/fstab终端输出|专题引用机主原始输出；不是原厂vbmeta/boot镜像。[基线](research/avb-live-baseline-20261018.md)、[fstab](research/p780-fstab-avb-20261018.md)|
|Google GSI A/B整镜像|保留机主PC；仓库只保存报告/摘要；助手未拿到整镜像独立重算。[重签报告](research/p780-dsu-testroot-resign-verified-20261018.md)|
|B启动前后日志/bugreport、原厂安装器APK/framework/services JAR|已用于会话分析；未将本轮含身份信息原件全量提交Git。[收束与输入SHA](research/p780-dsu-closure-maintenance-route-20261018.md)|
|离线签名/提取工具交付包|历史账本登记版本与来源，不能冒称仓库tools目录已包含这些包|

B已安装并尝试启动后回原厂；历史账本的“尚未制作/安装/启动”只对应早期阶段。完整历史页见[DSU索引](archive/dsu-index-20261018.md)。

## 既有核心原件与提取证据

|类别|保存路径|边界|
|---|---|---|
|内核配置与Tracefs|[device](../evidence/device)：39170B config.gz、4096B trace raw|非内核镜像/确定基址|
|GhostLock工作包|[ghostlock](../evidence/ghostlock)：v0.1至v0.4原ZIP|保留版本瑕疵；CRC/SHA及内嵌副本曾核验，不是提权成果|
|候选构建|[actions](../evidence/actions)：Clang11/14、配置delta、布局多轮原件|最终布局引用run38060518994；其他运行保留上下文|
|Journey框架|[framework](../evidence/framework)：输入SHA、方法字节、反汇编、调用点|原始大JAR/ZIP未入Git|
|Journey配置|[journey](../evidence/journey)：XML/version、TCS阅读视图、可逆Base64 ZIP|64键按ALL假设匹配；非固件/权限表|
|系统APK|[apk](../evidence/apk)：ApeHighLights、SecureUI、SystemHelper|实机来源归档，不代表导出接口可越权|
|TEE记录|[tee](../evidence/tee)：白名单、读取失败记录|不等于所有TEE调用已授权|
|旧ADB/OTA/Bugreport|[restricted](../evidence/restricted)：原ZIP、UTF-16日志及包清单|部分未经发布级脱敏；目录没有单独ACL|
|公开资料快照|[web](../evidence/web)：XDA用户提供正文与来源记录|第三方报告，不能冒充本机复测|
|旧报告/工具|[archive](../archive)|历史技术依据，不自动成为当前执行计划|

历史账本里的字节数有原始UTF-16、转换UTF-8和旧命名副本之别；当前Git对象身份以[整理前树清单](../evidence/analysis/repository-inventory-20261018.json)为准，Git blob SHA与SHA-256不混称。同名/同大小不等于内容相同。

## 明确未取得

匹配 `_162` 的可信完整OTA、boot/vendor_boot/vbmeta/vbmeta_system镜像、运行内核vmlinux/System.map及可用签名Firehose；init/Journey诊断/gsid关键可执行文件内容；失败DSU启动的有效pstore/ramoops。编译成功、接口名字或权限拒绝均不能补齐这些空缺。

完整性标准见[证据规范](reference/evidence-integrity.md)，原件隐私边界见[SECURITY](../SECURITY.md)。本轮整理保持已有证据原件字节不变；验证范围见[验收](REPOSITORY_AUDIT.md)。

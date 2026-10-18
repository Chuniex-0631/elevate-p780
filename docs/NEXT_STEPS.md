# 下一步研究计划

更新：2026-10-19。只保留当前任务；事实与完成项见 [STATUS](STATUS.md)。DSU停止，Root/BL解锁未达成。2026-10-19 已按机主新要求重启独立的 EDL 兼容性实验；实验须逐阶段限制为最小操作。

|优先级|任务|进入条件与交付物|完成或停止条件|
|---|---|---|---|
|1|已有样本的调用者与服务端交叉核对|基于[native矩阵](research/p780-native-interface-crosscheck-20261018.md)，逐项区分JNI、传输库、HIDL接口与服务实现；记录样本SHA、引用符号、策略规则、缺失端点|形成有来源的调用链或明确排除理由；只剩缺失二进制时标BLOCKED，不反复扫同名字符串|
|2|核对尚未取得原件的价值|先核对PC现有清单和已上传范围；只有明确能补齐具体调用链时再提最小增量材料|不重复要求已被Permission denied拒绝的init/Journey/gsid文件；不把未取得内容判为不存在|
|3|可信同型号固件或源码新证据|新原厂材料需型号、构建、来源、哈希；源码回复需对应 `_162` 与5.4.233说明|能验证来源才离线检查boot/vbmeta/内核；不以A52s或旧TINNO树替代本机|
|EDL受控实验|QDL v2.8 已在 QUD/COM6 成功返回 Sahara v2 身份信息；下一阶段仅在机主继续实际操作及备份/可恢复条件满足时，验证 Mannar 候选 A 的 Sahara 传输与 Firehose configure/reset；签名 PKHash 前缀不匹配，成功预期极低。见[实测与实验边界](research/p780-qdl-qud-sahara-20261019.md)|保存错误码/阶段/日志并停止该候选；不得用握手成功推断 Root/解锁/写权限。|
|条件分支|GhostLock恢复研究|取得运行内核修补状态、可信二进制/符号/类型布局，能核验本机构建身份|当前BLOCKED；不运行跨机型payload，不用候选布局估算偏移|

## 已结束或暂缓，不重复列为待办

- Attestation公钥身份、fstab读取、Google OTA同指纹查询、A/B离线验签、B上机回退和SELinux配套摘要核对均已完成相应阶段。
- DSU：按机主决策停止安装、Restart、改签名和参数试错。仅保留[收束与证据](research/p780-dsu-closure-maintenance-route-20261018.md)。回退根因未知。
- 工程APK/菜单、Journey网络配置与应用保活消费者已审查，无新证据不重开同一路线。
- 不重新穷举getprop、猜OTA指纹或无记录地随机Firehose；不催发厂商邮件、不主动联系Rakuten。
- 当前所选shell/普通应用域未见diag/QSEE发现权限及目标设备节点/ssgtzd权限，先保留权限矩阵，不尝试直接服务请求。

## 推进标准

新结论必须包含输入身份、直接观察、分析推断、反证与缺口。只有拿到具体实现和权限证据，才设计下一阶段最小验证；现阶段不设置工程属性、不发诊断socket命令、不写misc/boot/vbmeta；单独 EDL 测试可能涉及重启，须明确设备风险。

每个实质阶段同步专题、STATUS、EVIDENCE_MANIFEST与CHANGELOG；README只保留摘要。自动监测/邮件任务状态须单独核对，仓库文字不替代运行状态。旧计划见[历史计划](archive/next-steps-before-dsu-20261018.md)与[DSU历史索引](archive/dsu-index-20261018.md)。

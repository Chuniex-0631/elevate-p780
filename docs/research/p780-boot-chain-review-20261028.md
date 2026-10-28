# P780 启动链复核：Boot HAL、GPT 与切槽证据（2026-10-28）

> 基线：94c9112644f40a5a1895f8a5ae075e2e4f4a7c1b。只读仓库保存文件和上游源码；未连接手机、未运行更新、未写分区、未切槽。当前 Root 仍为临时 installd UID0；永久 Root、BL 解锁、完整 EDL 均未证实。

## 1. 本轮结论

**切槽路线不能继续按“仅有 1.1，故 1.0 客户端必然失败”判死。** 本机保存 RC 同时声明两版接口；已有静态策略也将 update_engine 列为 boot HAL 客户端。另一方面，没有完整 HAL 返回值和重启前后槽状态，仍不能宣布切槽可用。

**优先研究 GPT 属性及 HAL 的真实存储后端，不再预设槽元数据必在 misc。** P780 ABL 字符串与 Qualcomm 上游 GPT 方案相符，但尚未恢复本机实际可达控制流或解析本机 GPT，故只是有依据的候选。

可复跑摘要：[离线复核 JSON](../../evidence/analysis/boot-chain-20261028/report.json)；工具：[audit.py](../../tools/boot-chain-audit/audit.py)。输入为连接器 UTF-8 视图；JSON 的 local_sha256 不冒充原始设备字节摘要。

## 2. 本机材料中的直接发现

| 保存文件 | 位置/观察 | 可支持的范围 |
|---|---|---|
| [Boot HAL RC](../../evidence/20261027/vendor-config/init/android.hardware.boot@1.1-service.rc) | L1 服务名 vendor.boot-hal-1-1；L2/L3 分别声明 @1.0 和 @1.1 的 IBootControl/default | 双版本配置已记录；不证明运行时两版都成功注册 |
| [VINTF fragment](../../evidence/20261027/vendor-config/vintf/manifest/android.hardware.boot@1.1.xml) | 声明 hwbinder 与 @1.1::IBootControl/default | fragment 的单个 fqname 不能覆盖 RC 或反证父接口不存在 |
| [平台版本化策略](../../evidence/20261027/vendor-config/selinux/plat_pub_versioned.cil) | L223：hal_bootctl_client 包含 update_engine_30_0、update_verifier_30_0、vold_30_0；L6545/6551：binder call/transfer 与 hwservice find | 静态允许 update_engine 客户端路径；shell 的失败不能直接外推到该域；不是最终加载策略的运行时复验 |
| [vendor 策略](../../evidence/20261027/vendor-config/selinux/vendor_sepolicy.cil) | L3606：hal_bootctl 对 vendor_gpt_block_device 可写；L3618/3619：sg/bsg 权限；另有 misc 权限 | GPT/UFS 后端值得查；allow 不证明 API 调用成功或实际使用这些设备 |
| [ABL 字符串](../../evidence/20261026/abl/abl_lzma.bin.strings.txt) | L1503 Updating GPT partition；L1508 Slot suffix / Part Attr；L1510–1532 SetActiveSlot、FindBootableSlot、retry | 提供定位字符串交叉引用的入口；不能把字符串当成已经恢复的调用链或位布局 |
| [历史 fastboot 输出](../../evidence/20261026/oem/fastboot-getvar-all.txt) | L177–185：当前 B；A/B 的 retry=6、unbootable=no、successful=yes | 仅是早期快照；不能拿来证明 10-27 更新之后的状态 |
| [boot 块探针源码](../../tools/update-engine-probe/mkpayload_boot.py) | L52–58：4096 B、0xAA、extent 从块 0 开始、partition=boot | 当前源码构造的是测试块，不是可启动 boot；不能仅凭生成器证明某次会话实际用了相同文件 |

## 3. 上游控制流核对

### 3.1 HIDL 版本与日志

[IBootControl 1.1 定义](https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/master/boot/1.1/IBootControl.hal) 继承 1.0。所读 blob 为 939dfb3d7480a02850c0592506d8d04a30b0a7fa；这解释版本关系，不证明本机实现等同上游。

[Android 11 分支 BootControlAndroid](https://android.googlesource.com/platform/system/update_engine/+/refs/heads/android11-d2-release/boot_control_android.cc) 的 Init 取得 1.0 接口，失败返回 false；SetActiveBootSlot 在 transport 或 CommandResult 失败时记录错误，成功路径没有必然的同名成功日志。所读 blob 为 ec2ca0f88146938049a9944ddcbd32a43dbbe0b2。故“没看到 SetActiveBootSlot 字样”不足以证明没有调用；shell bootctl 获取失败也不能证明 update_engine 已初始化的接口为空。

### 3.2 更新收尾与 postinstall

[固定提交的 PostinstallRunnerAction](https://android.googlesource.com/platform/system/update_engine/+/8bdae7ff4a9eb1dcdab7ddac5b82668c3ecac65d/payload_consumer/postinstall_runner_action.cc) 中，无分区需要 postinstall 也可直接进入 CompletePostinstall；没有子进程不证明整个 Action 为 no-op。该实现先看成功状态和 switch_slot_on_reboot，再执行 FinishUpdate，成功后才调 SetActiveBootSlot；失败返回 kPostinstallRunnerError，开关为 false 则返回 kUpdatedButNotActive。

这是另一份上游版本的候选控制流，不冒充 Android 11/P780 二进制。应以本机日志、二进制分支与返回值核验，而不是把上游条件直接当成设备现场。

### 3.3 Qualcomm GPT 后端

[Qualcomm bootctrl 固定提交](https://android.googlesource.com/platform/hardware/qcom/bootctrl/+/1afac11f51b27e99f31ff8c8ad7cde2ffb285631/boot_control.cpp) 从 GPT entry attribute 读取槽状态；设置 active 涉及主/备 GPT、CRC 和分区映射；UFS 路径还涉及 XBL boot LUN 选择。不能简化为“改 misc 一个字节”或“找到可写 misc 即切槽”。

此源码只提供同平台实现线索，尚未建立 P780 Boot HAL 的构建身份。**本轮不提供 GPT/LUN 写入命令，也不建议直接改 GPT。**

## 4. 历史判定需要撤回到未知的位置

| 旧判断 | 本轮替代判断 | 仍缺什么 |
|---|---|---|
| 只注册 1.1，缺 1.0，所以 update_engine 切槽必然 no-op | 配置同时声明两版；运行时注册/调用待核对 | 同次启动的服务注册与调用者身份、transport 结果、CommandResult |
| 没有 SetActiveBootSlot 日志，所以没切槽 | 所读上游成功路径不必打印该日志 | 精确 InstallPlan、最终错误码及重启前活动槽证据 |
| 重启后 _b，证明 A 从未 active | 未切槽、HAL 失败、ABL 回退均未排除 | 重启前后元数据、启动阶段/回退记录；current 与 active 分开 |
| RUN_POST_INSTALL=1 没子进程，整个 Action 无效 | 分区级 postinstall 条目可能为空；Action 的收尾逻辑另行存在 | payload manifest 的条目与本机 Action 分支 |
| A boot 写入成功，A 不能启动就是切槽失败 | 0xAA 小块本身不可启动；该次 payload 身份和后续恢复过程须独立确认 | 完整 boot 读回、配套 vbmeta/vendor_boot/dtbo、A/B 构建关系 |

## 5. 证据缺口与下一项工作

本轮未取得 10-27 完整原始更新会话及本机 Boot HAL/update_engine 二进制；已有专题摘录不足以完成原因归属。树中未见独立 GPT dump；misc 的二进制读取经当前连接器未返回可分析内容，因此未对其布局作新解码结论。旧 bugreport/10-10 OTA 审计早于这些实验，不能填补时序缺口。

登记本轮摘要时还发现，旧证据清单的 679 个路径都在基线 Git 树，但 271 项登记字节数与 blob 大小不同；原因未经核实，不直接判为内容损坏。本轮保留旧值并标明未全量重哈希，不能以既有清单冒充全库字节完整性复验。

下一项具体工作是**取得本机 Boot HAL 后端身份与一次历史会话的完整证据链**，先不重跑 applyPayload：

1. 保存并按 boot/时间划分已有 update_engine log，核对 InstallPlan、payload 身份、source/target slot、switch 开关、最终错误码；禁止拼接多次实验凑出成功链。
2. 核对本机服务实际注册链、调用者 SELinux 域及 HAL 查询返回；shell 被拒与 update_engine 失败分别记录。只查询，不调用 setActive/markSuccessful 等写状态方法。
3. 对已有 ABL 原件定位上述字符串交叉引用，确认读取 GPT 属性的函数、位含义与回退条件；有本机 GPT 保存样本后再离线验证主/备 CRC、所属 UFS LUN 及属性一致性。
4. 核对目标槽 boot/vbmeta/vendor_boot/dtbo 等完整镜像及 build 配套；签名通过、切槽成功、镜像启动与永久 Root 四项分别验收。

前两项若能定位真实失败分支，才评估后续受控启动实验。没有可靠恢复条件，不用已知不可启动测试块反复切槽；静态复核继续进行，设备写入仍暂停。

## 6. 验证

离线工具在 7 份保存文本视图上运行；5 项测试覆盖双版本配置与运行时结论分离、多会话不合并、缺失日志不判 no-op、输入不变和本地字节哈希。没有声称完整 Root 或永久 Root 已取得。

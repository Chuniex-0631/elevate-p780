# 当前研究状态

> 2026-10-28 文档复核（Asia/Shanghai）。本页为唯一权威状态页。
> 本轮仅核对仓库保存记录，未连接设备、未新增设备实测。历史快照见 [整理前状态页](archive/STATUS-before-status-review-20261028.md)。

## 当前结论

**已记录临时、受 SELinux 限制的 UID0 shell；永久 Root、Bootloader 解锁及完整 EDL 均未证实。**
已测试候选路线尚未形成完整提权或持久启动链，设备实验保持暂停；这不是对所有软件路径的穷尽性否定。

| 项目 | 已记录证据 | 结论与边界 |
|---|---|---|
| 临时 UID0 | daemon / Elevate 保存 `uid=0(root)`、`u:r:installd:s0`、Enforcing 输出 | 临时受限 shell；重启后需重新触发，不等于永久 Root |
| Bootloader | `flash.locked=1`、verified boot green；本 ABL 注册路径未见 unlock；历史 unlock 命令为 unknown command | 已记录状态仍为 Locked；不能外推所有固件永远无法解锁 |
| EDL | QDL 到达 Sahara v2 | Firehose、经完整验证的 programmer、存储读写均未证实 |
| AVB | 本机保存公钥与 AOSP 测试公钥的身份核验及离线验签记录 | 不提供写入通道，不证明设备端接受修改后镜像 |
| misc 固定字段写入 | Journey builtin 历史样本仅十进制 73–84 改变；恢复样本与原件相等 | 仅证明固定文本字段写入，不证明 BCB command、slot 元数据或任意偏移可写 |
| update_engine 有限块写 | 后续专题记载 boot_a 的一条 4096 B REPLACE 操作完成、对应哈希校验成功 | 仓库记录支持该次有限写入；不称“任意块写”，不证明任意分区/偏移可写 |
| 切槽与修改后启动 | 后续记录未见 SetActiveBootSlot，bootctl v1.0 获取失败；一直从 B 槽运行 | 未证实 A 槽被设为 active；不能据回 B 判定修改后的 A 镜像已接受启动验证 |
| 永久 Root | 尚无跨重启自动恢复权限且成功启动的闭合证据 | 未证实；运行时权限扩大也须另验持久性 |

后续实验文档报告 B 槽 stock、SELinux Enforcing。本页不将历史现场描述冒充 2026-10-28 的实时设备检查。

## 设备与版本事实

| 字段 | 已记录值 | 边界 |
|---|---|---|
| 设备 | Rakuten Hand 5G / TINNO P780，Qualcomm holi / SD480 | 工具平台别名不能单独裁决 programmer 兼容性 |
| 固件 | Android 11，P780AE_11.0_RMN_JP_162 / _162_CFC | 指纹构建字段为 264，含义不同 |
| 内核 | 5.4.233-qgki-gea5245e94afe-dirty，Clang 11.0.2，2024-02-20 构建 | 候选源码不等于运行内核源码 |
| SPL | 2024-02-01 | 日期本身不能证明某漏洞可利用 |
| 普通 adb shell | UID 2000 | 与另行触发的 installd UID0 shell 区分 |

## 证据与能力边界

1. **UID0 与 Root**：[daemon](research/p780-root-daemon-20261025.md) 和 [Elevate](../app/elevate/README.md) 保存后续成功记录。[installd 专题](research/p780-installd-root-shell-20261025.md) 为分阶段实验；[init 能力专题](research/p780-init-capability-20261025.md) 的负例只约束具体载荷、域与操作。目录枚举不证明能读取全部应用文件，部分路径写入不证明整个 /data 可任意读写。sh 成功不推出 toybox、su、域切换或 selinuxfs 可写。
2. **Bootloader 与 ABL**：[离线审计](research/p780-boot-edl-audit-20261026.md) 核实 14 项注册循环与分派。download 存在不证明可启动或写盘。FRP 读取成立，但到 Unlock 菜单显示/隐藏的消费链未闭合；FFBM/QMMI 回 Android 不证明缺少工厂镜像。
3. **EDL 与 programmer**：[筛查报告](research/p780-firehose-screening-20261026.md) 仅对五份候选做来源核验、DER 初筛及存储字符串检查。扫描到的根 DER SHA-256/SHA-384 未见目标摘要前缀；没有把完整本机 PKHash 提供给本轮筛查工具。完整签名、平台/授权条件、设备接受与 UFS 均未验证。未找到不等于不存在；AVB 与 PBL programmer 签名是不同信任链。读通过也不推出可写。
4. **有限写入与刷写链**：[update_engine 专题 §4.2.3](research/p780-full-root-routes-20261027.md) 与 [工具说明](../tools/update-engine-probe/README.md) 保存 boot_a 写入日志摘录。本轮未独立复验完整原始设备会话。misc 的固定字段原语与 update_engine 写 misc 失败可同时成立；后者不证明全设备不存在 misc 写接口。
5. **testkey 与持久性**：离线 avbtool 验签成功不等于设备启动成功。需要分别验证目标槽 boot/vbmeta 写入、读回、slot 元数据、设备端 AVB 接受和修改后镜像启动；“可写 boot 即可永久 Root”不成立。

## 已测试候选路线

| 路线 | 已记录阻塞 | 当前决定 |
|---|---|---|
| update_engine | 记录了 metadata 验签通过及有限 boot_a 写入；所需切槽未实现，misc 请求失败 | 暂停；不称可靠刷写或永久 Root |
| CVE-2023-6931 | 泄漏、回绕及校准有记录；values 放置不稳定，曾卡死/重启；函数指针链受 CFI 限制 | 暂停 heap groom；原语不等于完整提权 |
| KGSL | 无 VBO/sparse，公开 VBO 触发不适用；非 VBO 短 unmap 触发未闭合 | 暂停；不将“公开触发不适用”写成所有可能路径已证伪 |
| FastRPC | map 前置条件有记录；已测 handle 不可用，未到 put_args 触发点；async 能力检查阻断另一候选 | 当前已测接口未形成触发链 |
| DSU/GSI | ramdisk GSI 公钥与已核对的公开 Developer GSI 不匹配 | 停止现有候选；不外推所有固件/GSI |
| EDL | 截至记录中的检索，未获得可验证匹配 programmer | 仅补离线来源与兼容性证据 |

详见 [6931](research/p780-uring-cve-2023-6931-20261025.md)、[FastRPC](research/p780-fastrpc-20261027.md)、[路线复审](research/p780-full-root-routes-20261027.md) 和 [下一步计划](NEXT_STEPS.md)。专题中的旧优先级与建议须服从本页暂停结论。

## 公开资料与维护

本仓库文档记录 2026-10-26 visibility=public；本轮未更改或重新核验可见性。restricted 目录名不提供访问隔离，全面脱敏未完成，见 [SECURITY](../SECURITY.md)。
公开摘要应使用脱敏输出与样本身份/哈希，不新增个人数据原件来证明权限。

证据索引：[EVIDENCE_MANIFEST](EVIDENCE_MANIFEST.md)；文档索引：[index](index.md)。原始证据不因文字整理而编辑。

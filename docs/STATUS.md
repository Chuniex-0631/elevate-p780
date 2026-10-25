> 2026-10-25 ROM Release 七个资产已经上传；GitHub size / digest 与文本清单一致，**未完成真实 TAR 的逐字节与目录核验**。[审计边界](rom/AUDIT-20261025.md) · [离线复核工具](../tools/rom/verify_release.py)。

> 2026-10-25 静态核对：相关清理路径仍呈现current语义，未观察到上游3bfdc63936dd修复语义；范围仅限已审函数及直接调用者，不等于完整可利用性结论。Magic3文章纳入方法参考，不能套用其参数。 [报告](research/p780-static-patch-review-20261025.md)。

> 2026-10-25 离线更新：Image恢复173,205个符号，全部名称/静态地址经独立解码核对；文件末端与BSS起点自洽。[报告](research/p780-kernel-symbol-recovery-20261025.md)。不等于实时地址、结构体布局或Root能力。

> 2026-10-25 突破：已在锁定、无 root 状态下从 init 域提取完整内核 `Image`（41,767,424 字节，SHA-256 `6df574af…`）。镜像未入库，方法见 [提取报告](research/p780-kernel-image-extraction-20261025.md)。

# 当前研究状态

> 2026-10-25 重建。本页是唯一权威状态页；其余页面的结论只在"本页范围"内有效。
> 历史正文中因二次编码损坏的段落不再引用（见 `docs/index.md` 的"部分损坏"标记）。

## 设备与版本事实

| 字段 | 已记录值 | 边界 |
|---|---|---|
| 设备 | Rakuten Hand 5G / TINNO P780，Qualcomm holi / mannar | 平台名称层级不同，非矛盾 |
| 固件 | Android 11，`P780AE_11.0_RMN_JP_162` / `_162_CFC` | 内部构建号与指纹字段 `264` 不同 |
| 指纹 | `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys` | — |
| 内核 | `5.4.233-qgki-gea5245e94afe-dirty`，Clang 11.0.2 r383902b1 | 候选源码不等于 running source |
| 启动状态 | `flash.locked=1`，verified boot green，槽 `_b` | 每次采集的快照 |
| SELinux | Enforcing；shell 为 UID 2000 | — |
| Root | 已实机记录受限 `installd` 域 `uid=0` shell；SELinux 仍 Enforcing | 非完整权限、非持久 Root |

## 结论总表

| 方向 | 已取得的证据 | 状态 |
|---|---|---|
| DirtyFrag 页缓存写入 | 有效 ESP 报文被内核接受，文件页被原地解密覆盖；`/proc/net/xfrm_stat` 计数吻合 | **已确认** |
| 只读系统库写入 | `libc++.so` `.rodata` 填充区被改写，另一进程可读；写回零后恢复 | **已确认** |
| init 域代码执行 | `sentry` 入口 trampoline + 桩；孤儿回收触发；标记落地 | **已确认** |
| installd 域代码执行 | `libbase` `LogMessage` 入口改写；275 个调用点；标记落地、`exec` 失败标记出现 | **已确认** |
| 受限 Root Shell | `installd` 域已成功执行 `/system/bin/sh`；`uid=0(root)`；可以列举 `/data/data`，并有 `/data/app`、dalvik-cache 写入记录 | **已实机验证；受 SELinux 域限制且重启失效** |
| AVB 测试根密钥 | TEE 公钥摘要 = AOSP 默认 RSA4096 AVB 测试公钥；vbmeta digest 吻合 | 身份已核验，不等于可写 |
| DSU / GSI | A/B 离线验签通过、B 安装完成、重启回原厂 | **停止** |
| OEM Unlock | Journey gate 静态根因 + fastboot 解锁命令全 `unknown command` | **关闭** |
| Fastboot / EDL | unlock 全 unknown command；Sahara v2 可达，Firehose 未通 | 阻塞 |
| GhostLock（CVE-2026-43499） | M1/M2 实机成立；M3 卡在 6 秒窗口的 prio 门与单次读，9 种尝试均无效 | **判负**（本机不可利用） |
| 内核镜像与符号 | `boot_b` 提取 41,767,424 B Image，恢复 173,205 符号；旧偏移表错位已修正 | **已恢复**；仍缺完整源码/DWARF |
| init / installd 域 | 两域均取得代码执行；init 可读 kmsg/块设备、写 `/metadata`；installd 触发可靠 | **能力已探明** |
| 运行时 Permissive | `security:setenforce` 无任何 allow，avc 证实 write 被拒 | **不可行**；tracefs/kprobe 关闭 |
| 只读榨取 | 9 类分区已提取；AVB 根信任 = AOSP testkey；B 槽 vendor_boot 与运行内核同源 | **完成** |
| 厂商预置服务 | Journey diag socket 三域 EACCES；`sys.journey.diag.write_misc` shell 可写 → init 写 misc | **新原语** |
| io_uring | shell/installd 可 io_uring；CVE-2023-52654（SCM_RIGHTS）未修复 | **候选主战线** |

## 关键边界

1. **DirtyFrag 的原语、UID 0 与完整 root 是不同层级**。现已在 `installd` 域得到受限 UID 0 shell，但其权限与持续性仍有严格边界；早期否定实验属于旧阶段，见
   [`research/p780-dirtyfrag-live-exploit-20261025.md`](research/p780-dirtyfrag-live-exploit-20261025.md) 第 5 节。
2. **所有页缓存改写都是易失的**：不改磁盘、重启还原；改动前备份原始字节、可逐字节回滚。
3. **候选源码与在线二进制不能混用**：TINNO 5.4.61、A52s 5.4.233 都不是本机 running source。
4. **历史编码损坏**：少量早期页面正文含不可逆替换字符，结论不再引用；以本页与未损坏专题为准。

## 2026-10-25 同步复核

- ROM 元数据与普通文件清单审计：[rom/AUDIT-20261025.md](rom/AUDIT-20261025.md)，二进制未下载验证。
- 内核 / 分区组件 / 权限分层复核：[research/p780-rom-kernel-system-triage-20261025.md](research/p780-rom-kernel-system-triage-20261025.md)。
- 受限 UID 0 shell 原始实机记录：[research/p780-installd-root-shell-20261025.md](research/p780-installd-root-shell-20261025.md)；[守护进程验证](research/p780-root-daemon-20261025.md)。本轮未开展任何设备实验。

## 证据

- 证据清单：[`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md)（由脚本从 `evidence/` 生成）
- 证据规范：[`reference/evidence-integrity.md`](reference/evidence-integrity.md)、[`reference/archive-protocol.md`](reference/archive-protocol.md)

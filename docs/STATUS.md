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
| Root | 未取得 | — |

## 结论总表

| 方向 | 已取得的证据 | 状态 |
|---|---|---|
| DirtyFrag 页缓存写入 | 有效 ESP 报文被内核接受，文件页被原地解密覆盖；`/proc/net/xfrm_stat` 计数吻合 | **已确认** |
| 只读系统库写入 | `libc++.so` `.rodata` 填充区被改写，另一进程可读；写回零后恢复 | **已确认** |
| init 域代码执行 | `sentry` 入口 trampoline + 桩；孤儿回收触发；标记落地 | **已确认** |
| installd 域代码执行 | `libbase` `LogMessage` 入口改写；275 个调用点；标记落地、`exec` 失败标记出现 | **已确认** |
| 交互式 root shell | 两个域 `exec` 被拒、`/data/local/tmp` 写入被拒、`/sys/fs/selinux/enforce` 打开即拒 | **未取得** |
| AVB 测试根密钥 | TEE 公钥摘要 = AOSP 默认 RSA4096 AVB 测试公钥；vbmeta digest 吻合 | 身份已核验，不等于可写 |
| DSU / GSI | A/B 离线验签通过、B 安装完成、重启回原厂 | **停止** |
| OEM Unlock 灰化 | Journey gate 静态根因已定位，无可用的普通调用者 | 阻塞 |
| Fastboot / EDL | unlock 全 unknown command；Sahara v2 可达，Firehose 未通 | 阻塞 |
| GhostLock | 已有身份匹配Image；本轮恢复173,205个符号并独立核对 | 二进制/符号缺口已补；修复状态、布局及适用性仍未定 |
| 内核源码身份 | 本机来源Image的版本/构建/config匹配，符号已恢复 | 仍缺对应完整源码、原始debug vmlinux/DWARF |

## 关键边界

1. **DirtyFrag 的原语与"拿到 root"是两件事**。原语已确认；root 受 SELinux 域策略限制，逐项否定见
   [`research/p780-dirtyfrag-live-exploit-20261025.md`](research/p780-dirtyfrag-live-exploit-20261025.md) 第 5 节。
2. **所有页缓存改写都是易失的**：不改磁盘、重启还原；改动前备份原始字节、可逐字节回滚。
3. **候选源码与在线二进制不能混用**：TINNO 5.4.61、A52s 5.4.233 都不是本机 running source。
4. **历史编码损坏**：少量早期页面正文含不可逆替换字符，结论不再引用；以本页与未损坏专题为准。

## 证据

- 证据清单：[`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md)（由脚本从 `evidence/` 生成）
- 证据规范：[`reference/evidence-integrity.md`](reference/evidence-integrity.md)、[`reference/archive-protocol.md`](reference/archive-protocol.md)

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
| init / installd 域 | 两域均取得代码执行；init 可读 kmsg/块设备、写 `/metadata`；installd 触发可靠 | **能力已探明** |
| 运行时 Permissive | `security:setenforce` 无任何 allow，avc 证实 write 被拒 | **不可行**；tracefs/kprobe 一并关闭 |
| OEM Unlock | `oem device-info` 可执行，解锁命令全 `unknown`；`ro.oem_unlock_supported=1` 是 vendor 属性 | **关闭** |
| 只读榨取 | 9 类分区已提取；AVB 根信任 = AOSP testkey；B 槽 vendor_boot 与运行内核同源 | **完成** |
| 厂商预置服务 | Journey diag 服务以 uid 0 常驻；diag socket 对 app/shell 均 EACCES；`sys.journey.diag.write_misc` shell 可写 → init 写 misc 分区 | **新原语（shell→init 写 misc）** |

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
| GhostLock（CVE-2026-43499） | M1/M2 实机成立；M3 卡在 6 秒窗口的 prio 门与单次读限制，9 种尝试全部无效 | **判负**（本机不可利用） |
| 内核镜像与符号 | `boot_b` 提取 arm64 Image（41,767,424 B，SHA-256 `6df574af…4f373`），恢复 173,205 个符号 | **已恢复**；旧偏移表错位一个符号已修正 |

## 关键边界

1. **DirtyFrag 的原语与"拿到 root"是两件事**。原语已确认；root 受 SELinux 域策略限制，逐项否定见
   [`research/p780-dirtyfrag-live-exploit-20261025.md`](research/p780-dirtyfrag-live-exploit-20261025.md) 第 5 节。
2. **所有页缓存改写都是易失的**：不改磁盘、重启还原；改动前备份原始字节、可逐字节回滚。
3. **候选源码与在线二进制不能混用**：TINNO 5.4.61、A52s 5.4.233 都不是本机 running source。
4. **历史编码损坏**：少量早期页面正文含不可逆替换字符，结论不再引用；以本页与未损坏专题为准。

## 证据

- 证据清单：[`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md)（由脚本从 `evidence/` 生成）
- 证据规范：[`reference/evidence-integrity.md`](reference/evidence-integrity.md)、[`reference/archive-protocol.md`](reference/archive-protocol.md)

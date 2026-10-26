# 当前研究状态

> 2026-10-26 更新。本页是唯一权威状态页；其余页面的结论只在"本页范围"内有效。
> 历史正文中因二次编码损坏的段落不再引用（见 `docs/index.md` 的"部分损坏"标记）。

## 设备与版本事实

| 字段 | 已记录值 | 边界 |
|---|---|---|
| 设备 | Rakuten Hand 5G / TINNO P780，Qualcomm holi / SD480 | 平台名称层级不同，非矛盾 |
| 固件 | Android 11，`P780AE_11.0_RMN_JP_162` / `_162_CFC` | 内部构建号与指纹字段 `264` 不同 |
| 指纹 | `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys` | — |
| 内核 | `5.4.233-qgki-gea5245e94afe-dirty`，Clang 11.0.2 r383902b1 | 候选源码不等于 running source |
| SPL | `2024-02-01` | CVE-2024-23373 的修复在 2024-07 之后 |
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
| ABL 工厂菜单 | Vol Up + Power：START / Restart bootloader / Recovery mode / Power off / Boot to FFBM / Boot to QMMI；**无 Unlock**；FFBM/QMMI 均回 Android | **路线关闭** |
| Fastboot / EDL | unlock 全 unknown command；Sahara v2 可达，Firehose 未通 | 阻塞 |
| GhostLock 5.4 | 5.4.233 `remove_waiter` 漏洞确认；pselect/mcast/tcp/sigreturn/process_vm/bpf 公开车辆在 P780 上全部判负；AArch64 Path B data-only 可用但无完整车辆 | **无可用车辆** |
| EDL programmer | SD480/Holi；五份候选根均不匹配 `c19a5029…`；公开仓库无 TINNO loader | **缺签名 loader** |
| CVE-2024-23373 | NVD 明确含 SD480；`kgsl_mmu_put_gpuaddr` 的 unmap 失败→释放 DMA/anon 页模式成立；但 P780 kgsl 无 VBO、无 sparse，GPUAF 的 VBO 触发不适用 | **待触发** |
| CVE-2024-26923 | 5.4.233 < 5.4.275；`unix_gc` 未修复；触发 PoC 两轮 30s 未赢 | **未触发** |
| 内核源码身份 | 实机 config 5238 项、候选编译与结构测量 | 缺原厂 Image/vmlinux |

## 关键边界

1. **DirtyFrag 的原语与"拿到 root"是两件事**。原语已确认；root 受 SELinux 域策略限制，逐项否定见
   [`research/p780-installd-root-shell-20261025.md`](research/p780-installd-root-shell-20261025.md) 与
   [`research/p780-init-capability-20261025.md`](research/p780-init-capability-20261025.md)。
2. **GhostLock 的公开车辆是 build-specific 的**：A52s 5.4 QGKI 的 pselect 帧、6.x 的 tcp/sigreturn/pipe 结构，
   都不能直接套到 P780 的 5.4.233（Qualcomm/holi）上；自研第 7 条车辆工程量大、概率低。
3. **EDL 可达不等于能写**：P780 的 PBL 只认 TINNO OEM key（PKHash `c19a5029…`）签名的 programmer；
   五份公开候选的根都不匹配，不能靠"再搜几个仓库"解决。
4. **CVE-2024-23373 的漏洞模式成立，但触发未解决**：P780 kgsl 没有 VBO、也没有 sparse；
   GPUAF 的 VBO race 不适用，需要另找让 `iommu_unmap` 返回 `< size` 的路径（`kgsl_mmu_unmap` /
   `qcom_io_pgtable` / `tblcnt`）。
5. **CVE-2024-26923 仍未触发**：两轮 30s 未赢竞态；需要内核可见的 `BUG_ON` 判据和更细的时序调参。
6. **不入仓的内容**：个人分区（`persist`/`modemst`/`fsg`/`fsc`）、第三方 exploit（`pipa/`）、
   47 号事故记录、1.6 GB GSI zip、1.9 GB system dump、NDK、`xbl_b.00.bin` 全文（API 401；strings/scan 已入仓）；`boot_b_full.img` 与 `P780-kernel-symbol-recovery-20261025.zip` 已入仓；其余只在 `docs/EVIDENCE_MANIFEST.md`
   或对应 README 登记来源/哈希。

## 证据

- 证据清单：[`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md)（由脚本从 `evidence/` 生成）
- 证据规范：[`reference/evidence-integrity.md`](reference/evidence-integrity.md)、[`reference/archive-protocol.md`](reference/archive-protocol.md)



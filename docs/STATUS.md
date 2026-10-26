# 当前研究状态

> 2026-10-27 更新。本页是唯一权威状态页；其余页面的结论只在"本页范围"内有效。
> 历史正文中因二次编码损坏的段落不再引用（见 `docs/index.md` 的"部分损坏"标记）。

## 2026-10-27 收口结论

**完整 root 尝试停止。** 从 `shell` 可达的软件路径已全部证伪：

- update_engine：验签绕过 + 任意块写成立，但切槽是 no-op（仅 boot@1.1，
  update_engine 请求 v1.0），A 槽从未 active；misc 无写入接口；
- 6931 perf：values 槽位不可控，geo-direct/交替关闭全部失败；
- KGSL：驱动无 VBO，CVE-2024-23380/23373 不适用；CVE-2025-21479 仅 A7xx；
- FastRPC：CVE-2024-21455 被 `ASYNC_FASTRPC_CAP=0` 挡住；
  CVE-2024-43047 的 map collision 前置条件可达，但没有有效 DSP handle，
  `put_args` 触发点不可达；
- EDL：入口可达，但无 TINNO/holi 签名 Firehose loader。

设备当前：B 槽 stock、Enforcing、数据完好。保留的能力只有 uid0 shell
（Elevate，installd 域）作为**部分 root**；完整 root 需要 EDL loader、
可写 misc/slot 的服务/工厂工具，或新的零权限驱动漏洞。

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
| Root | 历史 daemon / Elevate 记录已取得临时 UID0 shell | `u:r:installd:s0`，Enforcing；本轮未上机复现，非永久 root |

## 结论总表

| 方向 | 已取得的证据 | 状态 |
|---|---|---|
| DirtyFrag 页缓存写入 | 有效 ESP 报文被内核接受，文件页被原地解密覆盖；`/proc/net/xfrm_stat` 计数吻合 | **已确认** |
| 只读系统库写入 | `libc++.so` `.rodata` 填充区被改写，另一进程可读；写回零后恢复 | **已确认** |
| init 域代码执行 | `sentry` 入口 trampoline + 桩；孤儿回收触发；标记落地 | **已确认** |
| installd 域代码执行 | `libbase` `LogMessage` 入口改写；275 个调用点；标记落地、`exec` 失败标记出现 | **已确认** |
| 受限 root shell | 后续 daemon 与 Elevate 保存 UID0 / installd 域成功记录；早期失败仅限其测试上下文 | **临时受限 shell 已记录**；完整能力未取得 |
| AVB 测试根密钥 | TEE 公钥摘要 = AOSP 默认 RSA4096 AVB 测试公钥；vbmeta digest 吻合 | 身份已核验，不等于可写 |
| DSU / GSI | A/B 离线验签通过、B 安装完成、重启回原厂 | **停止** |
| OEM Unlock 灰化 | Journey gate 静态根因已定位，无可用的普通调用者 | 阻塞 |
| ABL 工厂菜单 | Vol Up + Power：START / Restart bootloader / Recovery mode / Power off / Boot to FFBM / Boot to QMMI；**无 Unlock**；FFBM/QMMI 均回 Android | 历史菜单观察；隐藏原因与工厂镜像是否缺失未证实 |
| Fastboot / EDL | unlock 全 unknown command；Sahara v2 可达，Firehose 未通 | 阻塞 |
| GhostLock 5.4 | 5.4.233 `remove_waiter` 漏洞确认；pselect/mcast/tcp/sigreturn/process_vm/bpf 公开车辆在 P780 上全部判负；AArch64 Path B data-only 可用但无完整车辆 | **无可用车辆** |
| CVE-2023-6931 perf 数据链 | u16 回绕、8446 sibling、delta 校准（1888/5984/10080/14176/22368 全部一次命中）、sock/cred/KASLR 泄漏、`x19` 可观测 | **原语全通；V 放置未解；暂停设备实验** |
| observed-V | `__perf_read_group_add` 采 `x19` 可拿到 values；校准会移动 X；双组 8446 规模在真机卡死，小观察组采样为 0 | **暂停** |
| EDL programmer | SD480/Holi；五份候选根均不匹配 `c19a5029…`；本轮未找到可验证匹配样本；摘要算法及多根详见新复核 | **缺签名 loader** |
| CVE-2024-23373 | NVD 明确含 SD480；`kgsl_mmu_put_gpuaddr` 的 unmap 失败→释放 DMA/anon 页模式成立；但 P780 kgsl 无 VBO、无 sparse，GPUAF 的 VBO 触发不适用 | **待触发** |
| CVE-2024-26923 | 5.4.233 < 5.4.275；`unix_gc` 未修复；触发 PoC 两轮 30s 未赢 | **未触发** |
| 内核源码身份 | 实机 config 5238 项、候选编译与结构测量 | 缺原厂 Image/vmlinux |

## 关键边界

1. **临时 UID0 已有后续成功记录**，见 [root daemon](research/p780-root-daemon-20261025.md) 与 [Elevate](../app/elevate/README.md)。仍受 SELinux 域限制；下面两页记录的是早期失败上下文，不能作为“从未取得 shell”的总判定：
   [`research/p780-installd-root-shell-20261025.md`](research/p780-installd-root-shell-20261025.md) 与
   [`research/p780-init-capability-20261025.md`](research/p780-init-capability-20261025.md)。
2. **GhostLock 的公开车辆是 build-specific 的**：A52s 5.4 QGKI 的 pselect 帧、6.x 的 tcp/sigreturn/pipe 结构，
   都不能直接套到 P780 的 5.4.233（Qualcomm/holi）上；自研第 7 条车辆工程量大、概率低。
3. **EDL 可达不等于能读写**。五份候选本轮未见目标根摘要前缀，且存在 SHA-256/SHA-384 与多证书链差异；完整本机 PKHash、签名头、平台、授权与 UFS 仍须逐项核对。不能从厂商名推断唯一可接受根，不能从检索未命中断言公开样本不存在。见 [筛查报告](research/p780-firehose-screening-20261026.md)。
4. **CVE-2024-23373 的漏洞模式成立，但触发未解决**：P780 kgsl 没有 VBO、也没有 sparse；
   GPUAF 的 VBO race 不适用，需要另找让 `iommu_unmap` 返回 `< size` 的路径（`kgsl_mmu_unmap` /
   `qcom_io_pgtable` / `tblcnt`）。
5. **CVE-2024-26923 仍未触发**：两轮 30s 未赢竞态；需要内核可见的 `BUG_ON` 判据和更细的时序调参。
6. **不入仓的内容**：个人分区（`persist`/`modemst`/`fsg`/`fsc`）、第三方 exploit（`pipa/`）、
   47 号事故记录、1.6 GB GSI zip、1.9 GB system dump、NDK、`xbl_b.00.bin` 全文（API 401；strings/scan 已入仓）；`boot_b_full.img` 与 `P780-kernel-symbol-recovery-20261025.zip` 已入仓；其余只在 `docs/EVIDENCE_MANIFEST.md`
   或对应 README 登记来源/哈希。`vendor_boot_a/b`、`dtbo_a` 及其解包内容已按 manifest 哈希复核并入仓（2026-10-26，见 [再提取记录](research/p780-partition-reextract-20261026.md)）。

## 本轮优先复核（2026-10-27）

- **6931 暂停设备实验**：原语层全部打通（泄漏、回绕、delta、observability），
  但"两次 read 之间不能有分配"与校准冲突；双组 8446 规模会卡死，小观察组采样为 0。
  详见 [`OBSERVED-V-20261027.md`](../tools/uring/analysis/OBSERVED-V-20261027.md)。
- **6931 观测点已修正**：x19 位于 IRQ 关闭的 `__perf_read_group_add` 循环里，
  PMU 采样会被推迟，之前的 X 多为噪声；改采 `perf_read` 中 kzalloc 之后一直
  保持 values 的 **x24**，众数信号干净（单值 >95%）。文件页缺页校准在
  `MADV_DONTNEED` 后 X 不变，但 fault-around 会让计数只有 1/16，需要 16 页步长
  或 `vm.fault_around_bytes=0`。
- **X 槽位问题（新阻塞）**：多轮 read0 显示 values 常落在 slab 顶部（slot 13）；
  喷 512 个 sock 仍只填 X 下方，`X+0x800` 跨页后没有活 sock；UDP skb 占 X 失败。
  一次 32-sock 分配/关闭循环还导致设备重启（B 槽 stock 恢复，无 OOB）。
  "S 在 X 上方"命中率低，继续高 churn groom 风险高。
- **下一步改为直接 OOB 到 cred 的可行性评估**：不经过 victim sock/fake skb，
  直接检查已知 cred 是否落在 `X..X+67KB` 内；若命中，`values[index] += delta`
  可直接改 `cred->cap_effective`。这只依赖 X 与 cred 的距离，不要求 X 上方有 sock。
- **顶部槽位策略也失败**：read0 后先分配 4 个 sock 占住 X 及相邻槽，再 read0，
  values 没有落到下一槽，而是跳到 57 槽外的另一页（`X1-X0 = -0x1c800`）；
  S/F 都不在已分配 sock 中。说明 SLUB 当前页 freelist 并不能按“向下连续”控制。
  结论：继续用 sock churn 控制 values 槽位，成功率和稳定性都不够，暂停这一方向。
- **geo-direct 交替关闭也失败**：喷 2000 sock，关闭末尾交替 17 个，等 2s 后
  read0 三次，X 分别是 `0xffffff80cae24800`、`0xffffff80cae26000`、
  `0xffffff802d219000`，**都不是被关闭的槽**（关闭槽是 `...cae22800` /
  `...cae25000` 等）；X 落在同一页的另一个空闲槽，随后又跳页。
  命中 0/3。说明 5.4 的 SLUB/RCU 行为与 PIPA 的 4.19 不同，
  “关闭交替槽 → values 复用”这个假设不成立。
- **完整 root 结论（2026-10-27）**：在现有可达接口下，刷机路线卡在 v1.0 bootctl，
  6931 路线卡在 values 槽位不可控；PIPA 的函数指针链又受本机 CFI 限制。
  **暂停完整 root 尝试**，保留已实现的 uid0 shell（Elevate）作为部分 root。
- **JVN#47427200 / AVB testkey（2026-10-14）**：JPCERT/CC 与 IPA 确认 Rakuten
  Mini/Hand/Hand 5G/BIG s 的 AVB 使用 AOSP 测试键，全部停止支持且不会修复。
  这只确认了 bootloader AVB 的 testkey，不提供新的写入/切槽路径。
- **DSU 路线也被证伪**：P780 boot ramdisk 的 `first_stage_ramdisk/avb/` 只带
  `q-gsi` / `r-gsi` / `s-gsi` 三个 GSI 公钥；官方 Developer GSI
  `aosp_arm64-exp-RP1A.200720.009` 的 AVB 公钥是 `1ffb1af7…`，而 `r-gsi` 是
  `501ff342…`，不匹配。AOSP 的 `developer_gsi_keys.mk` 说明公开 Developer GSI
  用的是 `*-developer-gsi` 键，本机没有。用 testkey 重签也不能过 DSU。
  **DSU 需要 r-gsi 私钥签名的 release GSI，公开不可得。**
- **新攻击面：FastRPC（2026-10-27 晚）**：`/dev/adsprpc-smd` 为 `crw-rw-r--`，
  shell 可 O_RDONLY 打开，未知 ioctl 返回 `ENOTTY`（已进入驱动）。
  内核 2024-02 / SPL 2024-02，而 CVE-2024-43047（ITW map collision UAF）与
  CVE-2024-21455（compat `is_compat` 指针混淆）均在 2024 下半年修复。
  CVE-2024-21455 只读探针已跑：32 位子进程可设置 is_compat，但 baseline 与 compat 的 invoke2 都返回 EPROTONOSUPPORT，async 能力检查在拷贝前就失败，**21455 在本机不可达**。
  但 **43047 的前置条件已打通**：`INIT_ATTACH=0` 成功、ION system heap fd 可用、两个 `vaddrin=0` 的重叠 FastRPC map 都创建成功（`va=0xe18bc000` / `0xe18b8000`）。
  然而 **UAF 触发点不可达**：shell 没有有效 DSP handle；`INVOKE(handle=0)` 与静态 handle 3..6 都是 ENOSUCH，7..20 是 EPERM；`put_args` 只在一次真正完成的 invoke 后调用。
  FastRPC 路线降为不可达。
  详见 [`p780-fastrpc-20261027.md`](research/p780-fastrpc-20261027.md)。
- **KGSL 复核**：`/dev/kgsl-3d0` 可打开，但内核无 VBO 符号，
  CVE-2024-23380/23373 不适用；CVE-2025-21479 仅 A7xx，本机 A619。
- **EDL 无新候选**：公开仓库仍无 TINNO/holi 签名 loader；同 SoC 样本使用不同 OEM key。
- **完整 root 路线复审**（新）：`system_app` 可直接调用 update_engine（实测 `--cancel`
  返回服务错误而非权限拒绝）；update_engine 是唯一可写 boot **和** vbmeta 的可达域；
  OTA 证书是 RSA-2048 releasekey，不是 testkey。详见
  [`p780-full-root-routes-20261027.md`](research/p780-full-root-routes-20261027.md)。
- **update_engine 基线已打通**：确认它每次 apply 重读 `otacerts.zip`；最小 payload
  已生成并通过本地签名校验；system_app + 本地 HTTP 触发成功，错误精确停在
  `kDownloadMetadataSignatureMismatch`（证书门）。工具在
  [`tools/update-engine-probe/`](../tools/update-engine-probe/)。
- **证书页替换 + 签名门绕过已实测**：自建小 APK（`tools/update-engine-probe/app/`）
  把 1135 B 的 `otacerts_ours.zip` 写进页缓存（`match=true`），紧接着触发
  update_engine，日志出现
  `Verified correct signature 1 out of 1 signatures.` 与
  `Metadata hash signature matches value in Omaha response.`。
- **新阻塞**：空分区 manifest 会让 `DeltaPerformer::Write` SIGSEGV；需要带
  `partitions` + `REPLACE` operation 的合法 payload。另：page cache 会被回收，
  写完必须立刻触发 update。
- **块写路径已完整打通**：`mkpayload_boot.py` 的 `partition=boot` + `REPLACE`
  payload 被 update_engine 接受，
  `Opening /dev/block/bootdevice/by-name/boot_a` → `Applying 1 operations` →
  `Completed 1/1` → `FilesystemVerifierAction ... kSuccess`。
  结束码 `kUpdatedButNotActive` 只因 `SWITCH_SLOT_ON_REBOOT=0`。
- **A 槽启动仍失败**：原厂 `vbmeta_a.00.bin` 的 boot 描述符对应 build **263**，
  当前 B 是 **264**；A/B boot 镜像不同。已用原厂 vbmeta_a 只替换 boot 描述符
  并重签（`avbtool verify_image` 通过），以及尝试 B 的 vbmeta/boot，A 仍回到 B。
  随后 update_engine 拒绝写 `misc`（`kInstallDeviceOpenError`），fastboot 无
  `set_active`/`flash`/`erase`，`bootctl` 不可用 —— **slot 元数据无法清除**。
- **关键更正：update_engine 根本没有切槽**。重新跑 `SWITCH_SLOT_ON_REBOOT=1`
  的 payload，日志只有：
  `UpdateBootFlagsAction` → `Marking booted slot as good`
  → `Marking new slot as unbootable` → apply → `Update successfully applied`；
  **没有 `SetActiveBootSlot` / “marking new slot as active”**。
  原因：设备只注册了 `android.hardware.boot@1.1::IBootControl/default`
  （PID 645，`hal_bootctl_default`），而 update_engine 和 `/system/bin/bootctl`
  都请求 **v1.0**；v1.0 service 不存在，bootctl 报
  `Error getting bootctrl v1.0 module`，SELinux 也拒绝 shell 的
  `find hal_bootctl_hwservice`。因此 `switch_slot_on_reboot=1` 是**静默 no-op**，
  A 槽从未被真正设为 active；B 一直 active。
- **misc 写入域**：policy 允许 `init`、`vendor_init`、`vold`、`uncrypt`、
  `update_engine`、`hal_bootctl_default/server`、`vendor_misc_writer` 写
  `misc_block_device`；但设备上没有 `/vendor/bin/vendor_misc_writer`，
  只有 bootctl HAL。能 `find hal_bootctl_hwservice` 的域只有
  `update_engine`、`update_verifier`、`vold`（`hal_bootctl_client`）。
- **postinstall 也是 no-op**：`RUN_POST_INSTALL=1` 时
  `PostinstallRunnerAction` 只打印 `All post-install commands succeeded`，
  没有执行任何子进程；本地 update_engine_client 的 install plan 没有
  postinstall 路径，无法借此进入 update_engine 域。
- **刷机路线的实际结论**：update_engine 能写块、能过验签，但**不能切槽**；
  没有 v1.0 bootctl、没有可写的 misc 接口、没有 EDL loader。
  “刷机 → permissive boot → 完整 root”目前被 slot 切换卡死，而不是被写入能力卡死。
- **OTA 情报收集**：A=263、B=264；`/data/ota_package` 与 `/data/misc/update_engine`
  对 shell/system_app 均拒绝；`/system/etc`、`/vendor/etc`、props 中没有 OTA URL；
  没有 OTA/FOTA/SystemUpdate 应用；Rakuten 官方页只给操作说明。详见
  [`p780-ota-recon-20261027.md`](research/p780-ota-recon-20261027.md)。
  **OTA 包路线不可行**。
- **主线切回 6931 target A（selinux_state）**：不依赖 A 槽启动，成功后用现有
  uid0 shell 即完整 root。update_engine 的块写/验签绕过保留为已备能力。
- **下一步**：生成合法 partition/operation payload（先写可回滚的 `vbmeta_b`），
  6931 保持 fallback；信息层清单已基本收口。

旧复核记录：[ABL / EDL 审计](research/p780-boot-edl-audit-20261026.md) 核实了 14 项注册循环、
FRP 缓冲区末字节读取与 misc 恢复样本相等。FRP 位到菜单隐藏的完整链未闭合。
Chimera 精确机型页仅列 Get Info；商业 EDL 读分区未证实。当前仓库公开且仍有原始敏感材料，
见 [SECURITY](../SECURITY.md)。

## 证据

- 证据清单：[`EVIDENCE_MANIFEST.md`](EVIDENCE_MANIFEST.md)（由脚本从 `evidence/` 生成）
- 证据规范：[`reference/evidence-integrity.md`](reference/evidence-integrity.md)、[`reference/archive-protocol.md`](reference/archive-protocol.md)



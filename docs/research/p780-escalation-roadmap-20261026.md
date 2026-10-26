# P780 提权与刷机路线图（2026-10-26）

> 本文把"提权 → 更多文件 → 解锁 BL / EDL → 刷机"拆成可分别验证的层次，结合仓库现有结论与
> 2026 年公开的临时 root 生态，给出优先级、最小验证实验与停止条件。
> 只针对机主自有设备；不写分区、不加载模块、不改 SELinux 状态之前，都要先有离线证据。

## 0. 结论先行

1. **不要再把"解锁 BL"当作刷机的前提**。本机 ABL 的 14 个 fastboot 命令里没有
   `flashing unlock` / `oem unlock`（[ABL 复核](p780-boot-edl-audit-20261026.md)），
   而 AVB 根信任是 **AOSP testkey**（[JVN#47427200](https://jvn.jp/en/jp/JVN47427200/)、
   [CVE-2026-107153](https://www.cve.org/CVERecord?id=CVE-2026-107153)，仓库也已逐位核对）。
   testkey 的私钥是公开的 AOSP 测试密钥，意味着**只要能写 boot 分区，就能刷入自签的
   boot + vbmeta 并通过 AVB**；顶层 vbmeta 还可以带 `disable-verification` 标志，
   让 system/vendor 的 dm-verity/AVB 一起失效。
2. 因此真正的瓶颈是 **"任意块写"或"内核 root"**，不是 fastboot 的解锁命令。
   拿到块写之后：`dd` 写 `boot_b` + 自签 `vbmeta_b` → 重启 → 持久 root；
   BL 仍然是 locked，`fastboot flash` 仍然会被拒，但设备已经按我们的镜像启动。
3. 当前最接近"块写"的三条路：
   - **内核 LPE**（仓库里的 CVE-2023-6931 数据链、新的 CVE-2025-38352）；
   - **页缓存 → 内核模块**（DFRoot 思路；本机 `CONFIG_MODULE_SIG` 未开，是少见的有利条件）；
   - **劫持本来就有 boot 分区写权限的服务**（`update_engine`、`hal_bootctl`）。
4. 纯信息层（更多文件/应用数据）不必等内核 root：init 8 MiB 分块 dumper 已经可用，
   加上 Zygote 的 CVE-2024-31317（本机 SPL 2024-02-01，低于修复线 2024-06），
   可以先拿到应用私有数据。

---

## 1. 已确认的底牌（本轮复核，2026-10-26）

| 项 | 值 | 意义 |
|---|---|---|
| 内核 | `5.4.233-qgki-gea5245e94afe-dirty`，2024-02-20 构建 | 大量 2024-2026 的 5.4 CVE 未回补 |
| SPL | `2024-02-01` | Zygote CVE-2024-31317（修复线 2024-06）等仍可利用 |
| 启动 | `flash.locked=1`、verified boot `green`、`ro.debuggable=0` | BL 锁定，但 AVB 用 testkey |
| SELinux | Enforcing；无任何域可 `setenforce`；`init` 也无 `sys_module` | "permissive 后门"不存在，必须换域或换内核 |
| 模块 | `CONFIG_MODULE_SIG` **未设置**；`MODVERSIONS=y`；`MODULE_UNLOAD=y` | 未签名模块可加载，但必须过 vermagic + 符号 CRC |
| 内核硬化 | `CFI_CLANG=y`、`SHADOW_CALL_STACK=y`、`ARM64_PTR_AUTH=y`、`INIT_ON_ALLOC=y`、`SLAB_FREELIST_RANDOM/HARDENED=y`、`KASAN=n` | 控制流劫持基本被 CFI 掐死，只剩 data-only |
| 攻击面开关 | `IO_URING=y`、`KPROBES=y`、`FUSER`/`ASHMEM`/`ION`/`KGSL` 在；`USER_NS=n`、`NF_TABLES=n`、`VSOCKETS=n`、`DEBUG_FS=n` | 排除 userns / nftables / vsock 一大票公开链；io_uring、perf、kgsl 仍是主面 |
| perf | `perf_event_paranoid=-1`（实测） | shell 无 seccomp，可建 perf 组；仓库已实测 u16 回绕 |
| 块写域（SELinux 实测） | `update_engine`：boot/system/super/misc/xbl/uefi；`hal_bootctl`：boot/xbl/gpt/misc/root；`vold`：misc/userdata/dm；`init`：misc/metadata/loop/dm | 找到这些域之一的代码执行 = 直接刷 boot |
| 模块加载域 | 只有 `ueventd`/`vendor_modprobe`/`vendor_init` 可 `module_load` `vendor_file`；`init`/`installd` 都没有 `sys_module` | 模块路线必须先解决"谁加载、加载谁" |
| 供应商文件 | `untrusted_app` **完全不能读** `/vendor`；`crash_dump` 可读 `vendor_file`；`vendor_qti_init_shell` 可写 `mnt_vendor_file` | 页缓存改 `/vendor` 必须换域 |
| ABL | 14 条命令；无 unlock、无 `oem ramdump`；有 `download:`/`getvar:` | 公开的 Qualcomm "oem ramdump 栈溢出" 在本机不适用 |
| EDL | `adb reboot edl` 可达；Sahara v2；缺 OEM 签名 Firehose（PKHash `c19a5029…`） | 只能做只读探测，不能刷 |

---

## 2. 2026 年临时 root 生态对 P780 的启示

### 2.1 DirtyFrag 已经形成完整工具链

公开的 [DFRoot](https://github.com/diabl0w/DFRoot) 与
[DirtyFrag-Android-Root-Jailbreak](https://github.com/ankitrawatgit/DirtyFrag-Android-Root-Jailbreak)
把 CVE-2026-43284 从"页缓存写"推进到"**载入自定义内核模块 → KernelSU late-load**"：

- 第一阶段把 helper 注入 `crash_dump64` 的页缓存；
- 第二阶段把 `.ko` 塞进一个 `/vendor` 库文件的页缓存，再用 libc++ 钩子把它 `finit_module`；
- 已知支持 `android12-5.10` 到 `android17-6.18` 的 KMI，**没有 5.4**。

对本机：漏洞原语我们已经有了（init 域 dumper 就是同一套），缺的是"模块加载"这一环。
本机 `CONFIG_MODULE_SIG=n` 是 DFRoot 路线里最难得的前提，值得单独评估（见 §3.4）。

### 2.2 GPUAF 仍是 Qualcomm 的主线，但本机被 VBO 卡住

GPUAF（CVE-2024-23380 的 VBO race + CVE-2024-23373 的 unmap 失败 UAF + 页表提前销毁）
有两条利用路径：页表操纵（改 `selinux_state`）与 pipe_buffer（`PIPE_BUF_FLAG_CAN_MERGE`）。
公开材料见 [UZCERT 的综述](https://uzcert.uz/en/new-gpuaf-method-discovered-for-complete-takeover-of-android-phones/)。

仓库的结论仍然成立：P780 的 kgsl **没有 VBO、没有 sparse**，GPUAF 的 VBO 触发不适用；
要复活这条线，得找到**非 VBO 的 `iommu_unmap < size`** 路径（§3.3）。

### 2.3 新的 5.4 内核候选：CVE-2025-38352

[posix-cpu-timers 的 UAF](https://ubuntu.com/security/CVE-2025-38352)：非自动回收的退出任务
在 `exit_notify()` 之后仍可能被 `handle_posix_cpu_timers()` 命中，与 `posix_cpu_timer_del()`
竞争，导致 `k_itimer` 被释放后仍挂在 timerqueue 上。

- Ubuntu 20.04 的 **5.4 分支确认受影响**（修复于 5.4.0-223.243），本机 5.4.233 早于修复；
- 已有公开触发 PoC（[longwasu/CVE-2025-38352-PoC](https://github.com/longwasu/CVE-2025-38352-PoC)）
  和面向 5.10 x86_64 的完整利用（[chronomaly](https://github.com/farazsth98/chronomaly)）；
- 对本机：**arm64 5.4 的结构/布局要重做**，但这是 2025 年少数确认覆盖 5.4 的 UAF，
  且 timer 对象是 data-only 友好的目标，优先级应高于继续硬啃 GhostLock。

（对照：CVE-2026-64560 虽然同属 posix-cpu-timers，Ubuntu 标注 5.4 **不受影响**；
CVE-2024-50264 的 vsock 本机未编译；CVE-2024-1086 的 nf_tables 本机未编译——都可以划掉。）

### 2.4 Zygote CVE-2024-31317：先拿应用数据

Android 9-14、SPL ≤2024-06-01 的 Zygote 命令注入，公开工具
[vnescape/zygote-CVE-2024-31317](https://github.com/vnescape/zygote-CVE-2024-31317)
可以"用任意 App 的 UID 起 shell / 导出应用私有目录"。本机 SPL 2024-02-01，**在影响区间内**。
它不提供 root，但能在不碰内核的情况下把 `/data/data/*` 拿出来，正好补上"更多文件"这一层。

### 2.5 Qualcomm 的"解锁 0-day"与本机关系

2026 年初公开的 Qualcomm fastboot 链（`oem ramdump` 超长参数栈溢出、
`oem set-gpu-preemption` 注入 `androidboot.selinux=permissive`、
Snapdragon 8 Gen 5 的 `efisp`/GBL 无签名校验）见
[XDA 汇总帖](https://xdaforums.com/t/qualcomm-there-seems-to-be-a-0-day-vulnerability-that-can-be-used-to-unlock-the-bootloader.4776970/)。

本机 ABL **没有** `oem ramdump`、`set-gpu-preemption`、`set-hw-fence-value` 这些命令，
平台也没有 `efisp`/GBL，因此不能直接套用。可迁移的只有方法论：
**ABL 的 fastboot 参数解析仍是可审计的内存破坏面**（§3.6）。

---

## 3. 七条路线（按"离刷机还有多远"排序）

### 3.1 A：把 CVE-2023-6931 的数据链做完（仓库已有最深积累）

- **已有**：本机确认 `perf_event_validate_size` 修复不完整、u16 回绕真实发生；
  pipa 的完整链（自增 → `netlink_sock_destruct_work` → fake sock → ROP）已移植出
  dry-run（KASLR 泄漏 26/26 命中），并已定位 CFI 阻断点。
- **新思路（仓库 2026-10-26 晚）**：放弃 ROP，改用 fake `sk_buff` 的双写原语，
  把 `current->cred` 写成 payload 里的 fake cred；或 `sk_security` 大位偏移 + `selinux_sk_free_security`
  做一次 arbitrary kfree。
- **阻塞**：`task_struct` 地址泄漏、fake skb 布局、计数校准到 ±1、`recvmsg` 不崩。
- **最小验证**：离线 QEMU/内核重放把"fake skb 双写 → cred 覆盖"跑通，再上设备；
  上设备一次 boot 只跑一次。
- **停止条件**：三条 CFI 合法目标都拿不到"写权限/写 SELinux"原语，则关闭。

### 3.2 B：CVE-2025-38352 的 5.4 arm64 移植（新）

- **为什么值得**：确认覆盖 5.4；UAF 在 `k_itimer`/timerqueue，属于 data-only 友好对象；
  公开触发代码可复用；本机 shell 无 seccomp，`perf_event_paranoid=-1` 也方便做时序。
- **要补的未知量**：5.4.233 的 `posix_cpu_timer_del`/`handle_posix_cpu_timers` 是否含修复；
  `k_itimer` 在 5.4 的 cache/布局；非 leader `exec()` 触发窗口在 arm64 的时序。
- **最小验证**：先只做"触发 UAF + 内核 oops 判据"（用 init 域 kmsg dump，不追求 root），
  确认 5.4.233 真的可触发；再做对象重占与数据改写。
- **停止条件**：连续 3 个触发变体都打不出 UAF，或修复已被 vendor 回补。

### 3.3 C：GPUAF 的非 VBO 路径（老线复活）

- **已有**：CVE-2024-23373 的 unmap 失败模式成立；本机无 VBO/sparse。
- **要做**：读 5.4 kgsl 的 `kgsl_iommu_unmap`、`qcom_io_pgtable` 的 `tblcnt/ptep`，
  找**不依赖 VBO** 就能让 `iommu_unmap` 返回 `< size` 的入口（如 `map_user_mem`、
  `GPUOBJ` import、`IOMMU_TLB` 错误注入）。
- **最小验证**：只读源码 + 在设备上让某个 ioctl 返回短 unmap（用 fault injection 或
  非法 sg），观察是否进入 free 路径；不接 cred。
- **停止条件**：三条候选路径都不可达，记录负结论。

### 3.4 D：页缓存 → 内核模块（DFRoot 思路，本机最有"捷径感"）

- **有利条件**：`CONFIG_MODULE_SIG=n`；DirtyFrag 原语已在手；init 域能读块设备、写 `/metadata`。
- **硬约束（已实测）**：
  - 只有 `ueventd`/`vendor_modprobe` 能 `module_load` `vendor_file`；`init`/`installd` 没有 `sys_module`；
  - `untrusted_app` 读不了 `/vendor`，`crash_dump` 能读 `vendor_file`；
  - `init` 不能 `relabelto vendor_file`，所以"把 /metadata 里的 .ko 改成 vendor_file"走不通。
- **可行形态（待验证）**：改一个**已存在的** `/vendor/lib/modules/*.ko` 的页缓存（保留它正确的
  `__versions`/vermagic），再触发 `request_module()` 让 `vendor_modprobe` 加载它。
  这样绕开"自己编模块要匹配 CRC"的难题；payload 只需替换模块 `.text` 的一小段。
- **谁来做页缓存写**：需要能读 vendor 文件的域（`crash_dump`）加上 DirtyFrag 的 socket 能力；
  或找到 `vendor_modprobe` 自身的可触发钩子。要先用 policy + 小实验确认。
- **停止条件**：没有"能读 vendor 文件 + 能执行 DirtyFrag"的域，或目标模块已被加载/无法触发。

### 3.5 E：直接劫持"有块写权限"的服务（最短刷机路径）

- **已确认**：`update_engine` 可写 `boot_block_device`/`system_block_device`/`super`/`misc`；
  `hal_bootctl` 可写 `boot`/`xbl`/`gpt`/`misc`/`root`。
- **触发面**：`update_engine` 有 `update_engine_client`，shell 可调用（`--follow/--reset_status`），
  日志路径会走 libc++；`hal_bootctl` 的 HIDL 接口从 shell 不可达（`bootctl` 报
  "Error getting bootctrl v1.0 module"）。
- **缺的是数据源**：`update_engine` 只能读 `ota_package_file`（`/data/ota_package`，shell/installd 写不了），
  没有 inet 权限；`hal_bootctl` 只能读块设备。
- **可能的解法**：让 payload 起一个 **本地 TCP 服务**（需该域有 inet，`update_engine` 目前看没有），
  或先让 `system_server` 把镜像写进 `/data/ota_package`（system_server 有该权限），
  再由 `update_engine` 的 payload 读文件 → 写 boot。
- **最小验证**：先只验证"能否触发 `update_engine` 的 libc++ 钩子"（用 marker payload，
  不写块设备），确认触发链；再解决数据源。
- **收益**：不需要内核 LPE 就能刷 boot/vbmeta，风险比内核 exploit 低。
- **停止条件**：payload 无法获得数据源，或目标域没有可用的 libc++ 日志路径。

### 3.6 F：ABL / fastboot 漏洞（真正"解锁 BL"）

- **现状**：本机 ABL 只有 14 条命令，没有 unlock；`oem ramdump` 等公开入口不存在；
  但 `download:`、`getvar:`、`oem select-display-panel` 仍有参数解析代码。
- **可做**：用已有的 ABL 反汇编/控制流工具，审计这 14 个 handler 的缓冲区、
  长度与格式串，重点找**可被普通 fastboot 客户端触发的栈/堆溢出**；
  若有，再评估 canary/PAC 与可利用性（公开的 Qualcomm 0-day 也是从这条路来的）。
- **最小验证**：离线静态审计 + 在 QEMU 里跑 ABL 的 fastboot 解析（如果能搭）；
  没有内存破坏证据就不上真机（ABL 崩溃可能变砖）。
- **停止条件**：14 个 handler 都没有长度/边界问题，或需要物理拆机/写保护才能利用。

### 3.7 G：EDL 签名 loader（刷机/救砖的"保险"）

- **现状**：EDL 可达，但 PBL 只接受 OEM 根 `c19a5029…` 签名的 Firehose；
  公开五份候选都不匹配（[Firehose 筛查](p780-firehose-screening-20261026.md)）。
- **可做**：继续在 TINNO/OPPO/Rakuten 系固件、维修论坛、付费工具样本里找
  **同 PKHash** 的 `prog_firehose_*.elf`；关注 `P780AE_11.0_RMN_JP_162` 的 OTA/工厂包。
- **价值**：一旦有了 loader，即使刷坏也能救回；也能在 EDL 下直接读写分区（不再依赖内核）。
- **停止条件**：检索不到匹配根，或不值得为单台设备付费。

---

## 4. 立即可做（信息层，低风险）

1. **继续用 init 8 MiB dumper**：`/vendor`（含 49 个 DLKM `.ko`）、`/data/misc`、
   `/data/tombstones`、`/data/system` 里可读的部分；每块仍落 `/metadata/cur.bin`，拉走即回滚。
   这一步能把"原厂 .ko / 私有配置"补齐，给后续模块路线提供素材。
2. **Zygote CVE-2024-31317**：先跑 `--check-vuln`，再选一个自己安装的 App 做一次
   `-E` 导出，确认工具链在本机可用；注意 payload 留在设置里可能导致开机循环，跑完用 `--recover`。
3. **vold 写 `/data/media`**：vold 有 `media_rw_data_file` 写权限，若能触发它的 libc++ 钩子，
   就能把分区直接 dump 到 `/sdcard`（不再受 8 MiB 限制）；先测 `sm` 命令能否让 vold 记日志。
4. **确认 testkey 私钥可用**：从 AOSP `build/target/product/security/testkey.pk8` 取私钥，
   离线生成一份 `vbmeta_b` + 修改过的 `boot_b`，用 `avbtool verify_image` 自检；
   等块写通道到位即可直接刷。

---

## 5. 推荐顺序（按投入产出）

| 周 | 工作 | 产出 |
|---|---|---|
| 第 1 周 | §4.2 Zygote 导出 + §4.1 `/vendor` dump + §4.3 vold 触发测试 | 应用数据、原厂 `.ko`、vold 钩子可行性 |
| 第 2 周 | §3.5 update_engine 触发 + marker payload（不写块） | "有块写域能否被劫持"的 yes/no |
| 第 3-4 周 | §3.2 CVE-2025-38352 只读审计 + 触发判据 | 5.4.233 是否真可触发 UAF |
| 第 5-6 周 | §3.1 6931 数据链离线跑通；§3.4 模块路线 policy/载体验证 | 一条可上设备的候选链 |
| 并行 | §3.7 loader 检索、§3.6 ABL 审计 | 长期保险/解锁可能性 |

**不建议**再投入的方向：GhostLock 公开车辆移植（已判负）、OEM Unlock 静态扫描、
DSU/GSI、无 loader 的 EDL 盲试、以及任何"先上设备再想原语"的内核实验。

---

## 6. 风险与边界

- 内核 exploit 失败可能 panic/重启；所有设备实验前先备份可写分区（misc/frp/devinfo 已入仓），
  并确认能通过 `adb reboot edl` 回到 EDL（但没有 loader 时 EDL 只能看不能救）。
- 页缓存写与 `/metadata` 写都可回滚，但仍建议一次只改一个目标、改完立即 unpatch。
- 刷 boot/vbmeta 前先用 `avbtool` 离线验证签名链；BL 锁定下刷错 boot 可能无法开机，
  且没有 EDL loader 时无法自救。
- Zygote 注入会留下 `hidden_api_blacklist_exemptions`，可能导致开机循环；必须准备 `--recover`。
- 以上都是 N-day/自研研究，不针对他人设备；公开的 exploit 代码只作为方法论参考，
  不直接运行未适配的载荷。

## 7. 2026-10-26 晚实测补记

当晚按上面的顺序做了三件不写分区的事，结果修正了路线图里的两处判断：

1. **Zygote CVE-2024-31317 在本机可用**（`--check-vuln`：`VULNERABLE (pre-12)`）。
   - 用 `platform:targetSdkVersion=30:complete` 作为 `--seinfo` 对 `com.android.settings`
     注入成功，拿到 `uid=1000(system) context=u:r:system_app:s0` 的 bind shell；
   - 工具默认的 `default:targetSdkVersion=…` 对系统应用会触发
     `selinux_android_setcontext(...) failed`，Zygote 直接 abort；**系统应用必须显式给
     `platform`**，这是本次唯一改动的参数；
   - system_app 的边界比预期窄：`/data/system`、`/data/misc`、`/data/local/tmp`、
     `/data/data` 全部 `Permission denied`，目前只确认 `/data/tombstones` 可读。
     它能读的是目标应用自己的数据目录（本次 settings 的目录为空），所以它的定位仍是
     "按 App 导出私有数据"，不是通用文件读取。
2. **`update_engine_client` 从 shell 调用被 SELinux 拒绝**
   （`Status(-129, EX_TRANSACTION_FAILED)`），路线 E 的"shell 触发 update_engine"不成立；
   要触发只能借 system_server/系统权限的调用者，成本更高。
3. **`/vendor` 不是独立分区**：挂载点是 `/dev/block/dm-9`，734 MiB（`/vendor/lib/modules`
   在同一个 ext4 里）。整段 dump 约 92 个 8 MiB chunk，代价过高；更合理的是文件级提取
   （crash_dump 域可读 `vendor_file`，但写通道只有 tombstone 追加）。
4. **CVE-2025-38352 的修复状态已离线确认**：
   - Linux 5.4.233 的 `run_posix_cpu_timers()` 没有 `if (tsk->exit_state) return;`；
     5.4.295 才加入（本次直接 diff 了两版源码）；
   - 本机 `kernel.symbolized.elf` 里 `run_posix_cpu_timers`（`0xffffffc0103832a4`）
     入口直接进入 `fastpath_timer_check` 的内联序列（`[x19,#0x7d8/0x7f0/0x808]`），
     同样没有 `exit_state` 检查 —— 与 5.4.233 源码一致，**修复不存在**。
   - 结论从"按构建日期推断"升级为"源码 + 二进制双重确认；可达性仍待触发实验"。

工具链方面：JDK 17 与 platform-30 已重新下载（`work/toolchain`），build-tools 的旧直链
已 404，若还要重建 Elevate APK 需改用 sdkmanager 或换版本；内核 PoC 准备用 zig
（`aarch64-linux-musl` 静态）编译，不依赖 NDK。

## 8. 2026-10-26 深夜：CVE-2025-38352 首次触发实验（负结果）

把公开 PoC（longwasu/CVE-2025-38352-PoC）移植到本机后跑了 1,101 次：

| 项目 | 结果 |
|---|---|
| 编译 | zig `aarch64-linux-musl` 静态，1,109,688 B；musl 下 `struct sigevent._tid` 需按内核 UAPI 的 offset 16 手写 |
| 单次 | 正常退出，`uptime`/`boot_id` 不变 |
| 100 次默认 10 ms | 正常退出，无 panic |
| 1,000 次、timer 1–20 ms 扫描 | 正常退出，`boot_id` 仍为 `2eba953a-…` |

**为什么 0 命中（静态判断）**：PoC 用的是 `CLOCK_THREAD_CPUTIME_ID`，而 timer 线程创建完
timer 后立刻 `SYS_exit`；线程的 `sum_exec_runtime` 在退出后不再增长，10 ms 的 CPU-time
timer 很可能根本没有到期，自然没有 `handle_posix_cpu_timers` 的竞态窗口。公开复现是在
QEMU + GDB 里用断点把四个 vCPU 精确停在 `exit_notify`/`wait4`/`timer_delete`/
`handle_posix_cpu_timers`，不是单进程自然跑出来的。

**结论**：触发"未命中"不等于"漏洞不存在"——源码与二进制都已确认修复缺失；缺的是一个
适合真机的时序 harness。下一步应改成"进程 CPU 时钟 + 忙等消耗 + 多 racer 并发 + 可调
delete 延迟"，而不是继续加大同一 PoC 的循环次数。

## 9. 参考

- 仓库内：[STATUS](../STATUS.md)、[NEXT_STEPS](../NEXT_STEPS.md)、
  [ABL/EDL 复核](p780-boot-edl-audit-20261026.md)、[Firehose 筛查](p780-firehose-screening-20261026.md)、
  [GhostLock 5.4](p780-ghostlock-5.4-20261026.md)、[kgsl CVE-2024-23373](p780-kgsl-cve-2024-23373-20261026.md)、
  [io_uring/perf CVE-2023-6931](p780-uring-cve-2023-6931-20261025.md)。
- 外部：
  [JVN#47427200](https://jvn.jp/en/jp/JVN47427200/)、
  [AVBTestKeyInTheWild](https://www.android-device-security.org/publications/)、
  [DFRoot](https://github.com/diabl0w/DFRoot)、
  [DirtyFrag-Android-Root-Jailbreak](https://github.com/ankitrawatgit/DirtyFrag-Android-Root-Jailbreak)、
  [GPUAF 综述](https://uzcert.uz/en/new-gpuaf-method-discovered-for-complete-takeover-of-android-phones/)、
  [CVE-2025-38352 (Ubuntu)](https://ubuntu.com/security/CVE-2025-38352)、
  [chronomaly](https://github.com/farazsth98/chronomaly)、
  [CVE-2025-38352 PoC](https://github.com/longwasu/CVE-2025-38352-PoC)、
  [Zygote CVE-2024-31317](https://github.com/vnescape/zygote-CVE-2024-31317)、
  [Zygote 公开利用简报](https://feed.craftedsignal.io/briefs/2026-08-cve-2024-31317-android-zygote/)、
  [Qualcomm fastboot 0-day 汇总](https://xdaforums.com/t/qualcomm-there-seems-to-be-a-0-day-vulnerability-that-can-be-used-to-unlock-the-bootloader.4776970/)、
  [P780 XDA 帖](https://xdaforums.com/t/p780-rakuten-hand-5g-looking-for-stock-firmware-firehose-loader-edl-reachable-ota-sideload-not-using-aosp-test-key.4805241/)、
  [rootWithoutUnlockBootloaderList](https://github.com/lokey0905/rootWithoutUnlockBootloaderList)。

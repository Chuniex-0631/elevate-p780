# 新资产 × 已知漏洞：还有哪里有搞头（2026-10-25 评估）

> 输入：本轮拿到的内核 Image + 173,205 符号、设备实际 `config.gz`（6,577 项）、
> SELinux 策略与域权限实测、DirtyFrag 页缓存写原语、AVB testkey、shell→init 的 misc 写原语。
> 目的：在"已有 uid 0 代码执行、但出不了 SELinux 域"的前提下，判断下一步该往哪打。

## 1. 一句话结论

**瓶颈已经不是 uid 0，而是 SELinux 域逃逸。** 因此：

- 普通"内核 LPE 拿 root"价值有限（我们已经有 root 域的代码执行）；
- 真正有价值的是 **内核任意读写 → 改 `selinux_state.enforcing` / 目标任务 SID**，
  一次绕过整个策略；
- 其次才是"属性/服务"层面的域跳板（低风险、可静态做）。

## 2. 新资产与约束（实测）

| 资产 | 内容 | 影响 |
|---|---|---|
| 内核镜像 | 41,767,424 B arm64 Image，SHA-256 `6df574af…4f373` | 可反汇编、可定位任意函数 |
| 符号 | vmlinux-to-elf 恢复 **173,205** 个，旧偏移表错位已修正 | 内核路线可精确到函数/结构偏移 |
| 内核版本 | `5.4.233-qgki-gea5245e94afe-dirty`，Android 补丁级 2024-02，构建 2024-02-20 | 2024 年后披露的漏洞是主要候选 |
| 内核配置（实机 `config.gz`） | 见 §3 | 决定哪些利用链可用 |
| 域权限 | init：全 caps、Seccomp 0、可读 kmsg/块设备；installd：全 caps、Seccomp 0、可读写 /data | 载荷执行不是问题 |
| SELinux | `security:setenforce`/`load_policy` 无 allow；installd 无网络 socket、无块设备读写；app 更严 | 域逃逸是唯一缺口 |
| DirtyFrag | 只读系统库页缓存写（重启即失效） | 不能改内核内存，只能改文件页 |
| AVB | 根信任 = AOSP testkey | 只在"有写通道"时有意义 |
| misc 写原语 | shell 可写属性 → init 写 misc 文本标记 | boot-mode 级，不是内核 |

## 3. 内核配置决定的"可用/不可用"（实机 `config.gz`）

**可用（攻击面存在）**：

```
CONFIG_QCOM_KGSL=y          GPU 驱动（app 可达）
CONFIG_ION=y / ASHMEM=y     ION/ashmem（app 可达）
CONFIG_ANDROID_BINDER_IPC=y binder（app 可达）
CONFIG_IO_URING=y           io_uring
CONFIG_PERF_EVENTS=y        且 perf_event_paranoid = -1（实测）
CONFIG_BPF_SYSCALL=y / BPF_JIT=y
CONFIG_IP_NF_IPTABLES=y / NETFILTER_XTABLES=y / NF_CONNTRACK=y   旧版 iptables
CONFIG_NET_SCHED=y / PACKET=y / TUN=y
CONFIG_NFC=y / BT_HCIUART=y / CFG80211=y / MAC80211=y
CONFIG_KPROBES=y / FTRACE=y / KALLSYMS=y
```

**不可用（直接砍掉一批利用链）**：

```
CONFIG_USER_NS        未开    → nftables/overlayfs 类、需要 userns 的链全部不可用
CONFIG_NF_TABLES      未开    → 2022-2024 的 nft 系列（CVE-2022-32250/2023-32233/2024-1086 等）不可用
CONFIG_USERFAULTFD    未开
CONFIG_KCMP           未开
```

**加固（提高利用难度）**：

```
CONFIG_RANDOMIZE_BASE=y             KASLR
CONFIG_STRICT_KERNEL_RWX=y
CONFIG_HARDENED_USERCOPY=y
CONFIG_SLAB_FREELIST_HARDENED=y
CONFIG_STATIC_USERMODEHELPER=y
CONFIG_SECCOMP=y / SECCOMP_FILTER=y
```

**权限侧**（实测）：

- `perf_event_paranoid = -1`（shell 可读）→ perf 子系统对普通进程开放，
  但 app 的 SELinux/seccomp 是否放行 `perf_event_open` 需探针确认；
- installd 策略里**没有**网络 socket/netlink/packet 的 allow（grep 无命中），
  所以"CAP_NET_ADMIN + iptables/tc"这条从 installd 走大概率被策略挡住；
- installd 只允许 `block_device` 的 dir search——块设备读写不可用。

## 4. 候选路线（按"价值/成本"排序）

### A. KGSL / GPU 驱动（app 可达，闭源复杂，历史 CVE 多）

- 为什么：`CONFIG_QCOM_KGSL=y`，app 通过 `/dev/kgsl-3d0` 可直接访问；闭源驱动历史漏洞密集；
  一旦拿到内核读写，就能改 `selinux_state.enforcing`。
- 难点：5.4.233 已带高通 2024-02 补丁级；需要找**补丁级之后**的 KGSL 漏洞，且要用 Image 反汇编核对。
- 第一步：从 Image 枚举 KGSL ioctl 处理函数与 copy_from_user 路径，和已知高通公告逐条比对。

### B. AF_UNIX GC UAF（CVE-2024-26923 一类）

- 为什么：unix socket 从 app 域可用（socketpair/AF_UNIX），无需 CAP；补丁级 2024-02，
  该修复在 2024 年 4 月之后才进 stable，5.4.233 大概率未覆盖（**需核对 fix 版本**）。
- 难点：UAF 触发窗口窄，需要堆布局；KASLR + SLAB_FREELIST_HARDENED。
- 第一步：用 app 载荷写一个最小触发，先确认"能崩/能触发"再谈利用。

### C. io_uring（installd 侧最现实）

- 为什么：`CONFIG_IO_URING=y`；installd 载荷 **Seccomp=0、全 caps**，只要 SELinux 不拦
  `io_uring_setup` 就能用；5.4.233 有多个 2024 年 io_uring UAF（如 CVE-2024-0582 一类，**需核对**）。
- 难点：SELinux 是否给 io_uring 单独权限（Android 11 策略里可能没有该 class，默认放行）；
  需要先做 syscall 可达性探针。
- 第一步：installd 载荷调 `io_uring_setup/enter/register`，记录返回值与 errno。

### D. perf_event（paranoid=-1）

- 为什么：`perf_event_paranoid=-1` 实测，perf 子系统 2023-2024 有多个 UAF（如 CVE-2023-6931 一类）。
- 难点：SELinux `perf_event` class 可能拒绝；app 的 seccomp 可能过滤 `perf_event_open`。
- 第一步：同 C，探针测 `perf_event_open` 从 app / installd 两个域的返回值。

### E. 属性 → init 动作的横向枚举（零风险、可立刻做）

- 已知：`sys.journey.diag.write_misc`、`sys.journey.restorecon` 都是 shell 可写、init 执行；
- 还没系统扫过：**所有 rc 里的 `on property:` 动作**（exec/start/write/chmod/mount/restorecon），
  与 property_contexts 的"shell 可写"求交集；
- 如果存在 `exec`/`start` 类动作，可能直接拿到更强的域跳板；
- 第一步：解析 `/system/etc/init/*.rc`、`/vendor/etc/init/*.rc` + property_contexts，产出候选表。

### F. 供应商服务 / HIDL（静态，零风险）

- `QAS_DVC_MSP`（TEE/工厂服务）、`vendor.journey.hardware.warehouse`（system，late_start）、
  `qttestservice`（root，属性触发）、`poweropt-service`（root，常驻）；
- 第一步：从已有 `/system`、`/vendor` 解包中静态审协议与权限检查；先用 tar 里的文件，不碰设备。

### G. EDL / Firehose、OTA/固件（需要外部材料）

- Sahara v2 已通，缺匹配签名的 programmer；OTA 需要 TINNO 签名包；
- 一旦拿到工厂包：整片读写 + ABL 分析，直接绕过所有软件层。

### H. misc boot-mode 标记（需要 BL 逻辑）

- 已确认 shell 可写 `recovery.<value>`；若 BL 认可某个工厂/FTM 模式，可能换启动模式；
- 缺 ABL/Recovery 镜像，暂无法枚举有效值。

## 5. 具体 CVE 候选（需逐条核对 fix 版本与可达性）

| CVE | 子系统 | 可达性 | 备注 |
|---|---|---|---|
| CVE-2024-26923 | AF_UNIX GC | app（unix socket） | 2024-04 修复，5.4.233 大概率未覆盖（需核对） |
| CVE-2024-0582 | io_uring | installd（Seccomp 0） | 需确认 SELinux 不拦 io_uring |
| CVE-2023-6931 | perf_event | app/installd（paranoid=-1） | 需确认 SELinux perf_event class |
| Qualcomm KGSL 2023–2024 系列 | GPU | app | 需按 2024-02 补丁级筛选 |
| binder 2024 系列 | binder | app | 需按补丁级筛选 |

> 表中除"可达性"列外均为候选，未在本机验证；下一步先做可达性探针，再谈具体利用。

## 6. 建议的下一步（两条线并行）

1. **零风险静态线（先做）**：属性→init 动作枚举 + 供应商服务静态审；
2. **低风险探针线**：installd 载荷一次测 `io_uring_setup` / `perf_event_open` /
   `socket(AF_NETLINK)` / `socket(AF_PACKET)`，app 侧测 unix socket 与 KGSL open，
   把"哪些内核面真的可达"钉死。

之后才值得投入 KGSL 反汇编或 AF_UNIX 触发这类重活。

## 7. 属性 → init 动作枚举（已完成，2026-10-25）

工具：[`analyze_props.py`](../../tools/vuln-surface/analyze_props.py)；输出：[`props_report.txt`](../../evidence/20261026/vuln-surface/props_report.txt)。
扫描 `system/etc/init`、`vendor/etc/init`、`odm/product/system_ext` 下全部 rc，
共得到 **94 个"属性触发 + 有实际动作"的组合**，按可写域排序。

### 7.1 结论

| 类别 | 例子 | shell 可写？ | 价值 |
|---|---|---|---|
| **Journey 原语** | `sys.journey.diag.write_misc` → init 写 misc；`sys.journey.restorecon` → init `restorecon_recursive` | ✅（实测） | 已确认，本轮最大收获 |
| tracing/perfetto 开关 | `persist.traced.enable`、`persist.traced_perf.enable`、`persist.heapprofd.enable`、`debug.atrace.user_initiated` | ✅（策略允许） | 只能 start/stop tracing 守护进程，低 |
| 内核模块加载 | `persist.vendor.data.{shs,perf,offload}_ko_load` → `exec u:r:vendor_modprobe`；`vendor.wigig.driver` → `modprobe wil6210` | ❌（实测 setprop 失败） | 即使可写，命令是固定的、只能加载已签名模块 |
| 启动完成类 | `sys.boot_completed` → bootstat/wifi tracing/cpuset | ❌（system_app only） | 无 |
| 其它 | `sys.trace.trace_end_signal` → notify_traceur.sh | ❌（traced only） | 无 |

### 7.2 判断

- **属性路线基本榨干**：94 对里，shell 可写的只有 tracing 类和 Journey 两条；
  真正有价值的 `exec`/`modprobe` 动作用的是 vendor 域专属属性，shell/installd 都写不了；
- 唯一还没测的是 **installd 域**对个别属性的可写性（property_service 按域判定，
  uid 0 不等于可写）；但即使可写，固定命令也只给"加载已有模块"，拿不到代码执行；
- 因此下一阶段的重点应转向 **内核可达性探针**（io_uring / perf_event / netlink / packet）
  与 **KGSL 反汇编**，而不是继续在属性上挖。

## 8. 内核可达性探针（已完成，2026-10-25）

用 installd 域载荷（uid 0、CapEff 全开、Seccomp 0，`adb install` 触发）直接调 raw syscall，
结果写入 `/data/local/tmp/kprobe.txt`（10 × int64，已清理），解析脚本
[`parse_kprobe.py`](../../tools/vuln-surface/parse_kprobe.py)：

| # | 接口 | 结果 | 解读 |
|---|---|---|---|
| 1 | `socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE)` | -13 EACCES | 策略拒绝 |
| 2 | `socket(AF_PACKET, SOCK_RAW)` | -13 EACCES | 策略拒绝 |
| 3 | `socket(AF_INET, SOCK_RAW, ICMP)` | -13 EACCES | 策略拒绝 |
| 4 | **`io_uring_setup(8)`** | **8（fd）** | **可达！** |
| 5 | `perf_event_open` | -13 EACCES | 策略拒绝（尽管 `perf_event_paranoid=-1`） |
| 6 | `bpf(BPF_MAP_CREATE)` | -13 EACCES | 策略拒绝 |
| 7 | `open("/dev/kgsl-3d0")` | -13 EACCES | installd 打不开 GPU |
| 8 | `open("/dev/ion")` | -13 EACCES | 策略拒绝 |
| 9 | `open("/dev/binder")` | 8（fd） | 预期可达 |
| 10 | `open("/dev/dma_heap/system")` | -2 ENOENT | 节点名不同，待重试 |

### 8.1 结论：io_uring 是当前唯一"高价值且可达"的内核面

- installd 域（Seccomp 0、全 caps）可以 `io_uring_setup` 成功，说明 io_uring 子系统完全开放；
- netlink/packet/raw socket、perf、bpf 全被 SELinux 挡住；
- app 域打不开 GPU（installd 也打不开），KGSL 只能从 **app** 侧再确认（下一步）。

### 8.2 下一步

1. 用同样的 installd 载荷验证 `io_uring_enter` / `IORING_REGISTER_BUFFERS` / `IORING_REGISTER_FILES`
   都能用（不只是 setup）；
2. 对照 5.4.233 的 io_uring 修复历史，挑一个 2024 年之后修复的 UAF（如 CVE-2024-0582 一类），
   先做"能触发/能崩"的最小复现，再谈利用；
3. app 侧补一个 KGSL `open` 探针（JNI），确认 GPU 面是否只剩 app 可达。

### 8.3 io_uring 可用性验证（已完成）

同一 installd 载荷继续测完整调用链，结果写入 `/data/local/tmp/uring.txt`
（[`parse_uring.py`](../../tools/vuln-surface/parse_uring.py) 解析）：

| 调用 | 结果 | 解读 |
|---|---|---|
| `io_uring_setup(8)` | `8`（fd） | 实例创建成功 |
| `io_uring_enter(fd,0,0,0,0,0)` | `0` | 进入路径可用 |
| `io_uring_register(fd, REGISTER_BUFFERS, iov, 1)` | `0` | 缓冲区注册成功（pinning 路径可用） |
| `io_uring_register(fd, REGISTER_FILES, fds, 1)` | `-22` EINVAL | 参数问题，非权限问题（可再调） |

**结论：io_uring 从 installd 域是"完整可用"的**——setup / enter / register_buffers 全部成功，
不是只能建实例。剩下的就是选一个 5.4.233 尚未修复的 io_uring 漏洞做最小触发。

### 8.4 app 域 io_uring：被 seccomp 直接杀进程（负）

JNI 探针（`am start -e probe uring`）在 untrusted_app 中调 `io_uring_setup`：

```
Fatal signal 31 (SIGSYS), code 1 (SYS_SECCOMP)
Cause: seccomp prevented call to disallowed arm64 system call 425
```

- app 的 seccomp 策略**直接拒绝** `io_uring_setup`（不是返回 EPERM，而是 SIGSYS 杀进程）；
- 所以 io_uring 相关的工作**只能在 installd 域（Seccomp=0）用 raw asm 做**；
- 这也确认了：app 侧能用的内核面只剩 binder / unix socket / GPU（GPU 还要另测）。

### 8.5 对开发路径的影响

| 路径 | 可行性 | 成本 |
|---|---|---|
| app 内 C 写 io_uring 利用 | ❌ seccomp 杀 | — |
| installd asm 直接做 io_uring 提交 | ✅ | 高（要手写 mmap 环 + SQE） |
| installd mmap 一段 app 写好的 PIC shellcode 再跳 | 待验证（需 `execmem`/`file execute` 权限） | 中 |

### 8.6 shellcode 路径验证：execmem 被拒（负）

installd 载荷实测（早期 fchmod 保证崩溃也能读结果）：

```
mmap(NULL,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0) -> 0x759a4c5000
mprotect(addr,4096,PROT_READ|PROT_EXEC)                            -> -13 EACCES
```

- **installd 没有 `execmem` 权限**，匿名 RW → RX 被拒绝；
- 静态核对 `plat_sepolicy.cil` / `vendor_sepolicy.cil`：没有
  `(allow installd self (process (execmem)))`，也没有对 app/shell/system/vendor 文件的 `execute` allow；
- 因此"app 写 C 编译的 PIC shellcode → installd mmap 执行"这条路**关闭**。

**结论：io_uring 相关开发只能在 installd 的 asm 载荷里纯手写**（mmap 环 + SQE + 触发逻辑），
这是目前唯一可行的技术路线，成本高但没有替代。

## 9. asm 版 io_uring 提交：跑通（2026-10-25）

在 installd 载荷里用纯 asm 完成了一次完整的 io_uring 提交（`stub.S`，848 B）：

```
setup(8) -> mmap SQ ring -> mmap CQ ring -> mmap SQEs
        -> 填 SQE(IORING_OP_NOP, user_data=0x1234)
        -> io_uring_enter(1,1,GETEVENTS) -> 读 CQE
```

实测结果（`/data/local/tmp/uring2.txt`，[`parse_uring2.py`](../../tools/vuln-surface/parse_uring2.py)）：

| 项 | 结果 |
|---|---|
| setup fd | 17 |
| SQ / CQ / SQEs mmap | 全部成功 |
| `io_uring_enter(1,1,GETEVENTS)` | 1（提交 1 个 SQE） |
| CQE `user_data` | 4660 (0x1234) ✓ |
| CQE `res` | 0（NOP 完成） |

### 9.1 过程中的坑（供后续 asm 开发参考）

| 坑 | 现象 | 修法 |
|---|---|---|
| CQ 环 mmap 长度用了 `sq_entries` | `-EINVAL` | 必须用 `cq_entries`（params+4） |
| SQEs mmap 长度用 `entries*64` 且不足一页 | `-EINVAL` | 直接映射 4096 字节 |
| 用 `w10` 存 ring_mask | 覆盖了 x10（输出 fd），后续 emit 写到错误 fd，文件"停更" | 换 `w12`；asm 里 x10 是 out fd，不能借用 |
| `add w1, w12, lsl #6` | 汇编报错 | 应为 `lsl w1, w12, #6` |
| 结果文件 0600 读不出来 | 崩溃/跳转时 fchmod 未执行 | fchmod 放在 open 之后立刻做 |

### 9.2 现状

- 已具备"从 installd 用 asm 提交任意 io_uring 操作"的能力；
- 下一步：选定一个 5.4.233 尚未修复的 io_uring 漏洞（2024 年修复），
  用这套骨架构造对应 SQE 序列，先验证"能触发/能崩"，再谈利用。







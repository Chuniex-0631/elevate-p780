# GhostLock 5.4.233 可行性评估（2026-10-26）

> 只做离线评估，不跑设备。结论：**bug 已确认存在；ARM32 栈 shellcode 路线不适用，
> 但公开的 AArch64 reference 有 data-only Path B，可以绕开 P780 的 CFI/PAN/PXN。**
> 这不是“马上能跑”的 exploit，而是一个可做的移植工程。

## 1. Bug 存在性：已确认

P780 5.4.233 `remove_waiter`（`0xffffffc010342cd8`）反汇编：

```
0x...2d10:  mrs  x20, sp_el0          ; current
0x...2d14:  add  x21, x20, #0x90c     ; &current->pi_lock
0x...2d58:  str  xzr, [x20, #0x930]   ; current->pi_blocked_on = NULL
```

`task_struct.pi_blocked_on = 0x930`；这里清的是 **current**，不是
`waiter->task->pi_blocked_on`。`rt_mutex_start_proxy_lock`（`0x...2c40`）失败路径
`bl remove_waiter`。即 **CVE-2026-43499 在本机成立**。

## 2. 两条公开实现

| 实现 | 目标 | 最终提权 | 对 P780 的适用性 |
|---|---|---|---|
| gitchw `exploit/ghostlock_arm32.c` | 5.4.210 ARM32 手表 | 栈上 shellcode → `commit_creds` | ❌ P780 是 arm64，栈不可执行 + CFI |
| gitchw `references/ref_oneplus_aarch64` | 6.6/6.12 OnePlus/OPPO | **Path B：纯数据 PI write** | ✅ 思路可用，需适配 5.4.233 |

AArch64 reference 的 Path B（README 原文）：

```
Write 1 (mode=1) → selinux_state.enforcing = 0
                    (low byte of kernel ptr = 0x00, 8-byte write)
Write 2 (mode=2) → task->cred = init_cred
                    (uid=0, all capabilities)
```

两步都是 **data-only**：不覆盖 `fops->unlocked_ioctl`，不跳 shellcode，
**CFI/PXN 不参与**。这是 P780 最有希望的点。

## 3. P780 已有的静态资产

来自 28 号 profile（已由镜像/反汇编确认）：

```
task_struct.cred          = 0x838
task_struct.pi_lock       = 0x90c
task_struct.pi_waiters    = 0x918
task_struct.pi_blocked_on = 0x930
cred size                 = 0xa8
cred.caps_offset          = 0x38
init_task                 = 0x262d280
init_cred                 = 0x2639be8
selinux_state             = 0x27d6000  (enforcing = +0, initialized = +3)
```

## 4. 5.4.233 仍需补的未知量

| 项 | 说明 | 获取方式 |
|---|---|---|
| **pselect 栈几何 / `PSELECT_SHIFT`** | `NFDS=320` 时 `core_sys_select` 的 256B `stack_fds`；waiter word 必须 ≤3 | 反汇编 P780 `core_sys_select`/`do_select`，或 kprobe 量 |
| **`rt_mutex_waiter` 布局** | `task`/`lock`/`prio` 在 waiter 内的偏移 | 5.4.233 Image + BTF/结构反汇编 |
| **`kernel_phys_load`** | PI write 走 linear-map alias；P780 的物理加载地址 | init 域读 `/proc/iomem` 的 `Kernel code`，或 boot header |
| **KASLR slide** | `selinux_state`/`init_cred` 的运行时地址 | 53 号的 perf KASLR leak（需确认 2MB 精确度） |
| **current task 地址** | `task->cred` 写目标 | AArch64 reference 的 `kernelsnitch`/`pipe physrw`；或在 SELinux 关掉后读 per-cpu `current_task` |
| **pipe physrw 前置** | configfs/ashmem/pipe_buffer | P780 `CONFIG_ASHMEM=y`；需确认 C ashmem、configfs |
| **5.4 `core_sys_select` 差异** | 6.6/6.12 的 pselect 栈布局不能直接套 5.4 | 以 P780 Image 为准 |

## 5. 判断

- **Bug**：确认。
- **最终提权**：data-only Path B 绕开 CFI/PXN，是 P780 目前最可行的内核路线。
- **主要风险**：pselect 栈 overlay 在 5.4.233 上是否成立（waiter word ≤3）；
  如果 `core_sys_select` 的栈帧布局把 waiter 放在不可控区，这条也会像 OnePlus
  不可行机型一样失败。这个必须先用 **Image 反汇编/kprobe** 判定，不能盲跑。
- **工作量**：聚焦移植（offsets + pselect 几何 + task leak + physrw），
  不是“一周内一键 root”；但比继续 6931/26923 的竞态更有确定性。

## 6. 下一步（离线）

1. 拉 AArch64 reference 的 `src/core/{main,fops,slide,root,pipe_physrw}.c`，
   对照 P780 5.4.233 的 `core_sys_select`/`do_select`/`futex_wait_requeue_pi`；
2. 从 P780 Image 反汇编计算 `stack_fds` 相对 `sp` 的偏移、waiter word、
   `PSELECT_SHIFT` 候选；
3. 用 init 域读 `/proc/iomem`（或 boot header）确定 `kernel_phys_load`；
4. 检查 `CONFIG_CONFIGFS_FS`/`ASHMEM`/`pipe_buffer` 路径；
5. 只有 1–4 都成立，才设计最小触发 PoC；否则这条线也应判负。

## 7. 来源

- [gitchw/ghostlock-cve-2026-43499](https://github.com/gitchw/ghostlock-cve-2026-43499)
- AArch64 reference README: `references/ref_oneplus_aarch64/README.md`
- CVE-2026-43499 / P780 5.4.233 `remove_waiter` 反汇编（本机 Image）
- 28 号 P780 GhostLock profile 草案

## 8. pselect 几何：判负（2026-10-26）

从 P780 5.4.233 Image 反汇编：

```
core_sys_select  0xffffffc010504040
  sub sp, sp, #0x1c0
  fdsin = 函数入口 - 0x170        (sp_after_sub + 0x50)

do_futex         0xffffffc01038b9c8
  stp x29,x30,[sp,#-0x60]!
  mov x29, sp
  sub sp, sp, #0x1b0
  rt_waiter = x29 - 0xc8 = 函数入口 - 0x128

__arm64_sys_pselect6 0xffffffc010504be0
  stp x29,x30,[sp,#-0x10]! -> 0x505668 (frame 0x90) -> core_sys_select
__arm64_sys_futex    0xffffffc01038ea9c
  sub sp, sp, #0x70 -> do_futex
```

以同一 syscall 入口 S0 计：

```
fdsin   = S0 - 0xa0 - 0x170 = S0 - 0x210
waiter  = S0 - 0x70 - 0x128 = S0 - 0x198
waiter - fdsin = 0x78 = 15 words
```

- P780 的 `rt_mutex_waiter` 是 5.4 plain 布局：`task=+0x30`（word 6）、
  `lock=+0x38`（word 7）；
- waiter 的 task/lock 在 **word 21/22**；
- pselect 的用户可控区是 `stack_fds` 的 in/out/ex，**word 0–14**；
- waiter 落在 `res_in`（内核清零区），**不在用户可控区**；
- max feasible waiter word = 14 - 7 = **7**；实际 **15**（再加 +0x30 入口差，更差）；
- `PSELECT_SHIFT = 15 - 2 = 13`，远超可调范围。

**结论：P780 5.4.233 的 pselect 栈 overlay 不可行，gitchw 的 AArch64
`PSELECT_SHIFT` 路线不能直接移植。** 这条判负。

剩余 GhostLock 变体是 28 号 profile 里的 **heap-based 路线**：
`multicast_waiter`（`compact_waiter`/`waiter_off`/`buffer_size`）和
`tcp_zerocopy`（`compact_waiter`）。它们不依赖 pselect 栈帧，可能更适合 P780；
但 P780 的 route 几何仍全是 `null`，需要从 JingMatrix 5.4 A52s profile /
P780 structs 重新算。

## 9. multicast_waiter：源码级判负（2026-10-26）

JingMatrix `fops_mcast.c` 的机制：

```c
setsockopt(fd, IPPROTO_IP, MCAST_JOIN_SOURCE_GROUP, greqs, 264);
```

`do_ip_setsockopt()` 把 264B 的 `struct group_source_req` 复制到自己的内核栈；
`MCAST_WAITER_OFF` 必须落在 `[0, 264 - FAKE_WAITER_LAYOUT_SIZE]`（约 `[0,176]`），
才能让 forged waiter 的 task/lock 覆盖 freed futex waiter。但文件头明确写：

> This vehicle is REFUSE-gated on every target measured so far, so it never fires here.
> the copy lives on the stack only briefly, and the pi-chain walk can outlive it.

即：

- **所有已测目标都被 `mcast_gate_check()` 拒绝**，从未成功；
- 即使 off 落在窗口内，`setsockopt` 在校验失败后立即返回，copy 的栈寿命太短，
  pi-chain 走不完（同 `process_vm` 记录的失败模式）；
- 它没有 `pselect` 的阻塞窗口，也没有 `tcp_zerocopy` 的 punch-thread 窗口。

**结论：multicast_waiter 判负，不再投入 P780 off 计算。** 下一个候选是
`tcp_zerocopy`（`fops_tcp.c`，有 punch-thread 窗口）或 sigreturn/clone3/process_vm。

## 10. tcp_zerocopy：5.4 不适用（2026-10-26）

`fops_tcp.c` 用的不是 `MSG_ZEROCOPY` 发送，而是
**`getsockopt(TCP_ZEROCOPY_RECEIVE)`**：

```c
getsockopt(client_fd, IPPROTO_TCP, TCP_ZEROCOPY_RECEIVE, zc, &len);
```

它依赖 **5.14** 的 `struct tcp_zerocopy_receive` 新增 `msg_control/msg_controllen`
（`zc+0x28/0x30` 用来写 waiter->task/lock）。P780 是 5.4.233，结构只有：

```c
struct tcp_zerocopy_receive {  // 16 bytes
    __u64 address;
    __u32 length;
    __u32 recv_skip_hint;
};
```

- `getsockopt` 只 copy **16 字节**；`fops_tcp.c` 写的 `zc+0x18/0x20/0x28/0x30`
  **不在内核 copy 内**，task/lock 不会被放到栈上；
- `tcp_gate_check()` 对 `<5.14` 只返回 `WARN`（“proceeding -- the run's own
  outcome decides”），但结构决定它不会成功；
- A52s 5.4 QGKI 实际 work 的是 **pselect**（stage `pselect_map`），不是 tcp。

**结论：tcp_zerocopy 对 P780 判负。** 剩余可选车辆：

| 车辆 | P780 5.4 情况 |
|---|---|
| `sigreturn` | `rt_sigreturn` 帧，版本无关；最有希望 |
| `clone3` | 5.4 有 clone3；`struct clone_args` copy；shell 无 seccomp |
| `sockopt` | `fops_sockopt.c` 的窄车辆，待看 |
| `process_vm` | 源码已记录瞬时失败（同 mcast），大概率负 |
| `bpf` | P780 shell `bpf` EACCES，SELinux 挡，负 |

## 11. sigreturn：判负（2026-10-26）

P780 5.4.233 反汇编：

```
restore_fpsimd_context  0xffffffc01029e3d4
  sub sp, sp, #0x230
  ...
  0xffffffc01029e5f4:  add x0, sp, #0x10
                       mov w2, #0x200
                       bl  __arch_copy_from_user   ; vregs 512B
```

以同一 syscall 入口 S0：

```
__arm64_sys_rt_sigreturn    stp x29,x30,[sp,#-0x30]!
restore_sigframe            sub sp, sp, #0x60
restore_fpsimd_context      sub sp, sp, #0x230

vregs (sp+0x10) = S0 - 0x30 - 0x60 - 0x230 + 0x10 = S0 - 0x2b0
do_futex rt_waiter                          = S0 - 0x198

SIGRETURN_WAITER_OFF = -0x118
窗口 = [0, SIGRETURN_VREGS_BYTES - FAKE_WAITER_LAYOUT_SIZE] = [0, 424]
```

`vregs` 在 futex waiter **下面 0x118 字节**，负偏移，`sigreturn_gate_check()`
直接 `REFUSE`。**sigreturn 判负。**

## 12. GhostLock 5.4 车辆总结

| 车辆 | P780 结果 |
|---|---|
| pselect | ❌ waiter word 15 > max 7 |
| multicast | ❌ REFUSE-gated + copy 瞬时 |
| tcp_zerocopy | ❌ 5.4 struct 16B < 5.14 |
| sigreturn | ❌ off = -0x118，负偏移 |
| process_vm | ❌ 源码记录瞬时失败 |
| bpf | ❌ SELinux 挡 |
| clone3 / sockopt | 未测；5.4 帧/结构同样强依赖 build，希望低 |

A52s 5.4 QGKI 能 root 走的是 **pselect**（Samsung 的 5.4 帧），P780 的 5.4.233
（Qualcomm/holi）pselect/tcp/sigreturn 帧全部不同。**公开 GhostLock 车辆无法直接
移植到 P780；要 root 需要为 P780 专门设计/测量第 7 条车辆，工程量高、概率低。**

**结论：GhostLock 5.4 在 P780 上实质关闭。** 剩余通往 root/写通道的只有
EDL 签名 programmer（XBL 已确认 EDL 可达）或另一个新内核 CVE。

# 候选构建的结构布局与验证（2026-10-25）

> 目的：GhostLock profile 缺的是结构体成员偏移，而镜像里没有 BTF、`.data` 又受
> `CONFIG_RELOCATABLE` 重定位影响。本页记录"用候选构建出 DWARF"这条路的实际结果与验证边界。

## 1. 流水线

新增工作流 [`.github/workflows/p780-pahole.yml`](../../.github/workflows/p780-pahole.yml)：

- 工具链：AOSP `clang-r383902b1`（11.0.2，与设备构建一致）；
- 源码：[`arminask/linux-android-samsung-a52sxq`](https://github.com/arminask/linux-android-samsung-a52sxq) `droidian` 分支，`5.4.233`；
- 配置：设备 `evidence/device/p780-config.gz`，`olddefconfig` 后只编 `kernel/fork.o`、`kernel/cred.o`、
  `kernel/locking/rtmutex.o`、`security/selinux/hooks.o`、`fs/exec.o`、`kernel/sys.o`；
- 产出：`pahole` 结构布局 + `llvm-objdump` 反汇编。

过程中解决三个问题：

| 问题 | 现象 | 处理 |
|---|---|---|
| genksyms 崩溃 | `LLVM ERROR: IO failure on output stream: Broken pipe` | 关掉 `CONFIG_MODVERSIONS` |
| ThinLTO 产物是位码 | `pahole: Invalid argument` | 关掉 `LTO_CLANG` / `CFI_CLANG` / `SHADOW_CALL_STACK` |
| 产物下载 404 | 重定向把 `Authorization` 带到了 blob 存储 | 手动跟随 302，去掉鉴权头 |

## 2. 候选布局（5.4.233 + 设备 config）

### task_struct

| 成员 | 偏移 |
|---|---|
| `prio` | `116` (0x74) |
| `mm` | `1488` |
| `tasks` | `1408` |
| `thread_pid` | `1768` |
| `real_cred` | `2096` (0x830) |
| `cred` | `2104` (0x838) |
| `comm[16]` | `2120` |
| `nsproxy` | `2160` |
| `seccomp` | `2280` |
| `pi_lock` | `2316` |
| `pi_waiters` | `2328` |
| `pi_blocked_on` | `2352` |

### cred（size 168）

| 成员 | 偏移 |
|---|---|
| `usage` | `0` |
| `uid` / `gid` | `4` / `8` |
| `securebits` | `36` |
| `cap_inheritable` | `40` |
| `cap_permitted` | `48` |
| `cap_effective` | `56` |
| `cap_bset` | `64` |
| `cap_ambient` | `72` |
| `security` | `120` |

即 `caps_offset = 40`、`caps_count = 5`、`copy_size = 168`。

### rt_mutex_waiter（size 80）

`tree_entry` 0、`pi_tree_entry` 24、`task` 48、`lock` 56、`prio` 64、`deadline` 72。

### selinux_state（size 32）

`disabled` 0、**`enforcing` 1**、`checkreqprot` 2、`initialized` 3、`policycap[6]` 4、
`android_netlink_route` 10、`android_netlink_getneigh` 11、`avc` 16、`ss` 24。

### uts_namespace（size 440）

`kref` 0、`name` 4、`user_ns` 400、`ucounts` 408、`ns` 416。

## 3. 与运行镜像的交叉验证

| 项 | 候选 | 运行镜像 | 结论 |
|---|---|---|---|
| `task_struct.real_cred` | 2096 (0x830) | `get_task_cred` 首条取数指令为 `ldr x0,[x0,#0x830]` | **一致** |
| `uts_namespace.name` | 4 | `init_uts_ns` 处 `Linux` 在 +0x14 | **不一致（差 16 字节）** |

`cred` 的验证是硬证据：运行内核的 `get_task_cred`（`0x275ba4`）确实从 `task+0x830` 取 cred，
而 0x830 正是候选给出的 `real_cred`。

`uts_namespace` 的 16 字节差有两种解释：

1. TINNO 在 5.4.233 上改过该结构（例如加了 `ucounts` 或 Android 补丁字段）；
2. 我们的 `init_uts_ns` 符号偏移本身偏了 16 字节。

无论哪种，都说明**不能整体照搬候选布局**，必须逐字段用镜像验证。已确认可用的只有
`real_cred`；`prio`、`pi_lock`、`pi_waiters`、`pi_blocked_on`、`cred`、`seccomp` 尚未验证。

## 4. 下一步

1. 用 `remove_waiter` / `task_blocks_on_rt_mutex` 的反汇编验证 `pi_lock`、`pi_waiters`、`pi_blocked_on`；
2. 用 `__schedule` 或 `set_user_nice` 验证 `prio`；
3. 解决 `uts_namespace` 的 16 字节差（若为厂商改动，则说明 TINNO 确实动过结构，验证必须全部做完）；
4. 全部字段验证通过后，才把这些偏移写进 GhostLock profile。


---

## 5. 更正与实机验证（2026-10-25，基于独立符号恢复包）

机主提供了独立恢复包（`vmlinux-to-elf 1.4.0` + 自带验证器），含 173,205 条**带静态地址**的
`kernel.kallsyms` 与可反汇编的 `kernel.symbolized.elf`。地址约定：

```
image_offset = symbol_addr - 0xffffffc010080000
```

### 5.1 此前那份符号表有系统性偏差

用权威表重算后，此前 `symbols_full.txt` 里的偏移**偏低且幅度不一**，原因是我们用
`/proc/kallsyms` 的行序去配 `kallsyms_offsets` 数组——同名同地址的符号在两侧顺序不同，
导致逐步漂移。**教训：偏移必须从表里直接取，不能按行序配对。**

权威值（镜像相对偏移）：

| 符号 | 权威偏移 | 此前错误值 |
|---|---|---|
| `init_task` | `0x262d280` | `0x262d238` |
| `init_cred` | `0x2639be8` | `0x2639be0` |
| `modprobe_path` | `0x263a1a8` | `0x2639f28` |
| `core_pattern` | `0x2669e5c` | `0x2669950` |
| `remove_waiter` | `0x2c2cd8` | `0x2c2c40` |
| `esp_input$…` | `0x11f8a4c` | `0x11f8a24` |
| `selinux_state` | `0x27d6000` | `0x27d5200` |

### 5.2 `uts_namespace` 的 16 字节差已澄清

用权威地址读 `init_uts_ns`（`0x262d008`）：`kref = 2` 在偏移 0，`Linux` 在 **+4**——
与候选布局**完全一致**。此前的 16 字节差是我们的偏移错误，**不是厂商改结构**。

### 5.3 用运行镜像的反汇编逐字段验证

| 字段 | 候选 | 运行镜像 | 依据 | 结论 |
|---|---|---|---|---|
| `task_struct.real_cred` | 2096 (0x830) | **0x830** | `get_task_cred` 中 `ldr x20,[x19,#0x830]` | 一致 |
| `task_struct.pi_waiters` | 2328 (0x918) | **0x918** | `remove_waiter` 中 8 处 `#0x918` | 一致 |
| `task_struct.pi_blocked_on` | 2352 (0x930) | **0x930** | `remove_waiter` 中 `str xzr,[x20,#0x930]` | 一致 |
| `task_struct.prio` | 116 (0x74) | **124 (0x7c)** | `task_prio`：`ldr w8,[x0,#0x7c]; sub w0,w8,#0x64`；rtmutex 链 5 处一致 | **不一致** |
| `cred.usage` | 0 | 0 | `get_task_cred` 中 `ldr w8,[x20]` | 一致 |

`prio` 的差异说明：TINNO 的 `task_struct` 与 A52s 候选**在 `prio` 附近确实不同**（差 8 字节），
但 `pi_waiters`/`pi_blocked_on`/`real_cred` 又对得上。这验证了此前的判断——**不能整体照搬候选布局**，
必须逐字段以镜像为准。

### 5.4 当前可用值（P780 专用）

```hocon
# 已用运行镜像验证
task_struct.cred_real_off = 0x830
task_struct.prio_off      = 0x7c
task_struct.pi_waiters_off= 0x918
task_struct.pi_blocked_on = 0x930
cred.usage_off            = 0
```

尚未验证：`pi_lock`、`comm`、`seccomp`、`cred` 的能力位布局、`rt_mutex_waiter` 的成员偏移。

### 5.5 下一步

1. 用 `remove_waiter`/`rt_mutex_lock` 的 `ldxr/stxr` 序列定位 `pi_lock`；
2. 用 `commit_creds`/`prepare_kernel_cred` 验证 `cred` 的 `copy_size`、能力位偏移；
3. 用 `remove_waiter` 中对 `waiter` 的访问验证 `rt_mutex_waiter` 布局；
4. 全部验证完再生成 profile。


---

## 6. 逐字段验证结果（2026-10-25 继续）

全部依据运行镜像的反汇编或立即数，不是候选推断。

### 6.1 task_struct

| 字段 | 运行镜像值 | 证据 |
|---|---|---|
| `real_cred` | `0x830` | `get_task_cred`: `ldr x20,[x19,#0x830]` |
| `pi_lock` | `0x90c` | `task_blocks_on_rt_mutex`: `add x24,x2,#0x90c` → `_raw_spin_lock` |
| `pi_waiters` | `0x918` | 同一函数 8 处 `#0x918` / `#0x920` |
| `pi_blocked_on` | `0x930` | `str xzr,[x20,#0x930]`，`str x22,[x20,#0x930]` |
| `prio` | `0x7c` | `task_prio`: `ldr w8,[x0,#0x7c]; sub w0,w8,#0x64`；rtmutex 链 5 处一致 |

`prio` 与候选的 `0x74` 不同，其余四个与候选一致。这坐实了"TINNO 在 `prio` 附近改过布局、
但 `pi_*` 区段又与主线一致"的判断，也说明逐字段验证是唯一可靠做法。

### 6.2 cred

| 项 | 运行镜像值 | 证据 |
|---|---|---|
| `usage` | `0` | `get_task_cred`: `ldr w8,[x20]` |
| `cap_permitted` | `0x30` | `commit_creds`: `ldr x8,[x20,#0x30]` |
| `cap_effective` | `0x38` | `cap_capable`: `ldr w8,[x8,#0x38]`，按 `cap>>5` 索引 |
| `sizeof(cred)` | `168` (0xa8) | `cred_init`: `kmem_cache_create_usercopy(..., 0xa8, ...)` |

能力位按 `cap>>5` 索引 4 字节字、每套 8 字节（两个 u32），与候选的 `caps_offset=40`、5 套布局吻合。

### 6.3 rt_mutex_waiter

| 字段 | 运行镜像值 | 证据 |
|---|---|---|
| `task` | `0x30` (48) | `task_blocks_on_rt_mutex`: `stp x20,x19,[x22,#0x30]` |
| `lock` | `0x38` (56) | 同上（成对存储） |
| `prio` | `0x40` (64) | `str w8,[x22,#0x40]` |
| `deadline` | `0x48` (72) | `str x10,[x22,#0x48]` |

与候选完全一致。

### 6.4 仍未验证

- `task_struct.comm`（2120）：`__set_task_comm` 走 helper，需要更完整的反汇编；
- `task_struct.seccomp`（2280）：未找到直接访问点；
- `selinux_state.enforcing`（候选 +1）：`.bss` 无内容，需从读取它的代码确认。

## 7. 汇总：当前可用的 P780 值

```hocon
task_struct { prio = 0x7c, real_cred = 0x830, pi_lock = 0x90c,
              pi_waiters = 0x918, pi_blocked_on = 0x930 }
cred        { size = 168, usage = 0, caps_offset = 40, caps_count = 5,
              cap_permitted = 0x30, cap_effective = 0x38 }
waiter      { task = 0x30, lock = 0x38, prio = 0x40, deadline = 0x48 }
symbols     { init_task = 0x262d280, init_cred = 0x2639be8,
              root_task_group = 0x27e91b8, selinux_state = 0x27d6000,
              empty_zero_page = 0x27d7000 }
```

这些值已经足以开始拼装 profile 的静态部分；剩下的 `comm`/`seccomp`/`enforcing` 属于补全项，
而 `route.*.waiter_shift` 之类必须实测的字段仍然缺。


---

## 8. 补全：comm 与 seccomp（2026-10-25 继续）

### 8.1 先纠正一处误判

`__set_task_comm` / `__get_task_comm` 里的 `add x?, x?, #0x908` 一开始被我当成 `comm`，
但与 `pi_lock = 0x90c` 冲突。核对调用顺序后确认：`0x908` 是 `task_lock()` 用的
**`alloc_lock`**，不是 comm。于是：

- `alloc_lock = 0x908`（4 字节）
- `pi_lock = 0x90c`（4 字节）
- 中间 8 字节对齐填充，`pi_waiters = 0x918`

三者自洽，`pi_lock = 0x90c` 的结论不变。

### 8.2 comm = 0x848

| 证据 | 指令 |
|---|---|
| `__set_task_comm` | `add x23, x20, #0x848` |
| `__get_task_comm` | `add x8, x22, #0x848` |

与候选的 `2120 (0x848)` 一致。

### 8.3 seccomp = 0x8e8

`prctl_get_seccomp`：

```
mrs  x8, SP_EL0          ; current
ldrsw x0, [x8, #0x8e8]   ; current->seccomp.mode
```

与候选的 `2280 (0x8e8)` 一致。

### 8.4 selinux_state.enforcing：仍未实机验证

`enforcing_setup` 写的是 `selinux_enforcing_boot`（启动用的静态变量），不是
`selinux_state.enforcing`；AVC 路径的 `avc_has_perm` 反汇编里也没有 `ldrb`。
因此 `enforcing = selinux_state + 1` 目前只有候选依据（结构体稳定，风险低），**标记为待验证**。

## 9. 字段状态总表

| schema 字段 | 值 | 状态 |
|---|---|---|
| `offset.init_task` | `0x262d280` | 权威符号表 |
| `offset.init_cred` | `0x2639be8` | 权威符号表 |
| `offset.root_task_group` | `0x27e91b8` | 权威符号表 |
| `offset.selinux_enforcing` | `selinux_state + 1` | **待验证** |
| `offset.empty_zero_page` | `0x27d7000` | 权威符号表 |
| `task_struct.cred` | `0x830` | 反汇编确认 |
| `task_struct.comm` | `0x848` | 反汇编确认 |
| `task_struct.seccomp` | `0x8e8` | 反汇编确认 |
| `task_struct.prio` | `0x7c` | 反汇编确认（**非候选值**） |
| `task_struct.pi_lock` | `0x90c` | 反汇编确认 |
| `task_struct.pi_waiters` | `0x918` | 反汇编确认 |
| `task_struct.pi_blocked_on` | `0x930` | 反汇编确认 |
| `cred.copy_size` | `168` | `cred_init` 立即数 |
| `cred.usage_offset` | `0` | 反汇编确认 |
| `cred.caps_offset` | `40` | `cap_capable` / `commit_creds` |
| `cred.caps_count` | `5` | 由 `cap>>5` 索引方式推得 |
| `waiter.task` | `0x30` | 反汇编确认 |
| `waiter.lock` | `0x38` | 反汇编确认 |
| `waiter.prio` | `0x40` | 反汇编确认 |
| `waiter.deadline` | `0x48` | 反汇编确认 |
| `route.*.waiter_shift` 等几何 | — | **必须实测** |
| `cred.ref_count` / 能力位初值 | — | 需按 schema 语义再定 |
| KASLR 锚点 `nfulnl_logger` | `0x25ba9e0` | 权威符号表 |
| KASLR 锚点 `loggers` | `0x25c3000` | 权威符号表 |

到此为止，**profile 的静态部分已基本完整**；剩余缺口是 `enforcing` 一项待验证，
以及所有需要真正运行 exploit 才能得到的路线几何。


---

## 10. 收尾两项（2026-10-25）

### 10.1 `selinux_state.enforcing = +1`：间接确认

在 SELinux 代码区（`0x106c0000..0x10700000`）找到对 `selinux_state` 的直接引用：

```
ffffffc0106d314c: adrp x8, 0xffffffc012856000 <selinux_state>
ffffffc0106d3150: ldrb w8, [x8, #0x3]        ; initialized
```

代码用 **`+3` 读 `initialized`**，与候选的字段顺序完全吻合：

```
disabled 0 | enforcing 1 | checkreqprot 2 | initialized 3 | policycap[6] 4 ... 11
```

`initialized` 在 +3 成立，则 `enforcing` 在 +1 成立（同一组连续 `bool`）。标为**间接验证**。

### 10.2 `task_struct.cred = 0x838`

`commit_creds` 同时读取两个相邻指针：

```
ffffffc0102f6258: ldr x19, [x21, #0x830]   ; real_cred
ffffffc0102f625c: ldr x8,  [x21, #0x838]   ; cred
```

与候选的 `real_cred 2096 / cred 2104` 一致。此前验证的 `0x830` 是 `real_cred`，
schema 的 `task_struct.cred` 应填 **`0x838`**。

### 10.3 关于 `prio` 的补充说明

运行镜像里所有 `task->prio` 访问都落在 `0x7c`（`task_prio`、`rt_mutex_adjust_prio_chain`
5 处、`task_blocks_on_rt_mutex` 各一处）。候选布局是 `prio 0x74 / static_prio 0x78 / normal_prio 0x7c`，
因此有两种可能：

1. TINNO 在 `prio` 之前多了一个 8 字节字段 → 真实布局是 `prio 0x7c / static_prio 0x80 / normal_prio 0x84`；
2. 该内核的 `task_prio` 语义与主线不同。

无论哪种，**exploit 用到的 `prio` 就是 `0x7c`**；`normal_prio` 暂标 TBD。

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

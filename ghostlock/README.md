# GhostLock 移植骨架（2026-10-25）

> 目标：在本机（5.4.233-qgki）打通 CVE-2026-43499，从应用域拿到内核写，
> 最终 `commit_creds(&init_cred)` 得到完整 root。
> 静态证据已确认缺陷形态与释放点，见
> [`p780-ghostlock-bug-shape-20261025.md`](../docs/research/p780-ghostlock-bug-shape-20261025.md)。

## 已知条件

| 项 | 值 |
|---|---|
| `remove_waiter` | `0xffffffc010342cd8` |
| `rt_mutex_adjust_prio_chain` | `0xffffffc010341df4` |
| 释放点 | `+0x180`：`refcount_dec_and_test(&task->usage)` → `__put_task_struct` |
| `task_struct.pi_lock` | `0x90c` |
| `task_struct.pi_waiters` | `0x918` |
| `task_struct.pi_blocked_on` | `0x930` |
| `task_struct.usage` | `0x38`（本机构建） |
| `rt_mutex_waiter.task` | `0x30` |
| `rt_mutex_waiter.lock` | `0x38` |
| `rt_mutex_waiter.prio` | `0x40` |
| `init_cred` | `0x2639be8` |
| `commit_creds` / `prepare_kernel_cred` | `0x276240` / `0x276670` |

## 攻击链（待实现）

```text
1. 构造 PI 链：两个线程对同一 rt_mutex 做 lock，制造 waiter
2. 触发 remove_waiter 的清理路径（timeout / 信号中断）
3. 因 current 误用，adjust_prio_chain 对错误 task 减引用
4. task refcount 归零 → __put_task_struct → task_struct 被释放
5. 在同一地址窗口重新分配（spray）可控内容
6. 借由仍持有的指针写入 init_cred 相关字段，或直接改 cred 指针
7. commit_creds(&init_cred) / 或改 selinux_state.enforcing
```

## 里程碑

| # | 里程碑 | 判据 |
|---|---|---|
| M1 | 能在本机构造并观察 PI 链 | 读到 `pi_blocked_on` 非零、`pi_waiters` 树上出现节点 |
| M2 | 能稳定触发清理路径 | 无崩溃地走完 `remove_waiter` |
| M3 | 观察到释放 | 释放后再读该 task 触发 UAF（受控崩溃） |
| M4 | 可控重分配 | 同一 slab 上拿回该地址 |
| M5 | 提权 | `commit_creds(&init_cred)` 后 `id` 显示 uid 0 且域变化 |

## 调试通道（复用现有能力）

- 运行域：`u:r:installd:s0`（uid 0），可用 `sh` 与文件读写；
- 日志：写到 App 私有目录，再 adb 拉回；
- 回滚：清理机制已具备，无需重启；
- 崩溃观测：`/data/tombstones` 可读（uid 0）。

## 待解决

1. 本机 futex PI 路径是否与公开 PoC 一致（5.4 vs 6.x 差异）；
2. `CONFIG_PANIC_ON_OOPS=y`：M3 的"受控崩溃"会直接重启，需要改成观测侧信道；
3. `kernelsnitch` 常量缺失，`mm_struct_sz` 影响 heap 布局。

## 下一步

M1 优先：写一个最小程序，两个线程争同一 futex，读 `/proc/<pid>/task/*/stat` 或
`/proc/<pid>/stack` 观察 `pi_blocked_on`，确认链能构造出来。

# GhostLock 缺陷形态确认（2026-10-25）

> 结论：`remove_waiter` 在 PI 清理路径上把 `current` 当作 task 传给了
> `rt_mutex_adjust_prio_chain`，与 CVE-2026-43499 的修复点一致。
> 这是**逐指令确认**，不再是时间线推断。

## 环境

- 内核 `5.4.233-qgki-gea5245e94afe-dirty`（2024-02-20 构建，早于 2026-04 的修复）
- 符号来自独立恢复包：`remove_waiter = 0xffffffc010342cd8`
- `rt_mutex_adjust_prio_chain = 0xffffffc010341df4`

## 反汇编证据

```text
ffffffc010342d00: ldr  x8,  [x22, #0x38]      ; waiter->lock
ffffffc010342d04: cmp  x8,  x19               ; 与 lock 比较
ffffffc010342d08: b.ne 0xffffffc010342ef0     ; 不等则走另一支
ffffffc010342d0c: ldr  x24, [x19, #0x18]      ; lock->owner
ffffffc010342d10: mrs  x20, SP_EL0            ; ★ current
ffffffc010342d14: add  x21, x20, #0x90c       ; &current->pi_lock
ffffffc010342d18: mov  x0,  x21
ffffffc010342d1c: bl   _raw_spin_lock
...
ffffffc010342ebc: mov  x5,  x20               ; ★ 第 5 参数 = current
ffffffc010342ec0: bl   rt_mutex_adjust_prio_chain
```

对照：

| 位置 | 用的是 | 应该是 |
|---|---|---|
| `pi_lock` | `current + 0x90c` | `waiter->task + 0x90c` |
| `adjust_prio_chain` 的 task 参数 | `current`（x20） | `waiter->task`（`+0x30`） |

`waiter->task` 在 `+0x30`，函数里确实读过该字段（`ldr x14,[x9,#0x30]`），
说明两个 task 在同一函数内并存——正是混淆的条件。

## 已验证的相关偏移

| 字段 | 值 | 来源 |
|---|---|---|
| `task_struct.pi_lock` | `0x90c` | 本条反汇编 `add x21, x20, #0x90c` |
| `task_struct.pi_waiters` | `0x918` | `remove_waiter` 8 处 |
| `task_struct.pi_blocked_on` | `0x930` | `str xzr,[x20,#0x930]` |
| `rt_mutex_waiter.task` | `0x30` | `task_blocks_on_rt_mutex` 的 `stp x20,x19,[x22,#0x30]` |
| `rt_mutex_waiter.lock` | `0x38` | 同上（成对存储） |
| `rt_mutex_waiter.prio` | `0x40` | `str w8,[x22,#0x40]` |

## 仍未完成

1. 把 `rt_mutex_adjust_prio_chain` 内部的清理路径读完，确认 UAF 的释放点；
2. exploit 的路线几何（`waiter_shift` 等）需要运行才能测量；
3. `kernelsnitch` 常量（`mm_struct_sz`、collisions）在 5.x 无公开值。

## 结论

漏洞形态成立。接下来是 exploit 侧的工作，不再是"漏洞是否存在"的问题。

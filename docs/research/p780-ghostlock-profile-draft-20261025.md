# P780 GhostLock profile 草案（5.4.233，静态部分）

> **不可直接执行。** 这里只填了能从运行镜像静态验证的字段；
> 所有需要实测的路线几何留 `null`，schema 校验会把它们标记为无效。
> 字段语义依据 `ghostlock-app` 的 `docs/kernel_profiles/PROFILE_SCHEMA.md`。

## HOCON 草案

```hocon
release        = "5.4.233-qgki-gea5245e94afe-dirty"
schema_version = 1
kernel_major   = 5

route {
  # 三条路线都需要实测几何，暂不选择
  select_stack     { waiter_shift = null }
  tcp_zerocopy     { compact_waiter = null }
  multicast_waiter {
    compact_waiter = null
    waiter_off     = null
    buffer_size    = null
    task_offset    = null
    lock_offset    = null
  }
}
fallback { to = "none" }

kernelsnitch {
  # 5.x 无公开默认值，未测
  collisions   = null
  mm_struct_sz = null
}

task_struct {
  prio          = 124   # 0x7c，反汇编确认（候选为 116，不同）
  cred          = 2104  # 0x838，commit_creds 确认
  pi_lock       = 2316  # 0x90c，task_blocks_on_rt_mutex 确认
  pi_waiters    = 2328  # 0x918，同上
  pi_blocked_on = 2352  # 0x930，同上
  seccomp       = 2280  # 0x8e8，prctl_get_seccomp 确认
}

cred {
  copy_size   = 168     # cred_init: kmem_cache_create_usercopy(..., 0xa8, ...)
  usage_offset = 0      # get_task_cred: ldr w8,[x20]
  caps_offset  = 40     # cap_capable: [x8,#0x38] 索引 + commit_creds [x20,#0x30]
  caps_count   = 5
  # ref_count 与 refN_* 需要按实例语义取数，未测
  ref_count    = null
}

offset {
  init_task        = 0x262d280
  init_cred        = 0x2639be8
  root_task_group  = 0x27e91b8
  empty_zero_page  = 0x27d7000
  selinux_enforcing = 0x27d6001   # selinux_state + 1（间接验证）
  slide_nfulnl_logger = 0x25ba9e0
  slide_loggers       = 0x25c3000
}
```

## 已验证 / 未验证

| 类别 | 状态 |
|---|---|
| 符号偏移（`init_task` 等） | 已由独立恢复包与镜像一致确认 |
| `task_struct` 六个字段 | 全部由反汇编确认 |
| `cred` 大小/usage/caps | 由 `cred_init`、`get_task_cred`、`cap_capable` 确认 |
| `selinux_enforcing` | 由 `initialized=+3` 间接确认 |
| `kernelsnitch.*` | **未测**（5.x 无公开值） |
| `cred.ref_count` / `refN_*` | **未测**（依赖运行时实例） |
| `route.*` 全部几何 | **未测**（必须运行 exploit 才有数据） |

## 结论

profile 的静态骨架已经完整，但**没有任何一条路线能通过 schema 校验**——缺的全是几何。
要让它可用，只能回到设备上实际跑 GhostLock，边跑边量 `waiter_shift` / `compact_waiter`
这类依赖栈布局的参数。

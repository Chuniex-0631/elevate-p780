# 6931 新数据链设计：fake skb 双写（2026-10-26，离线）

> 目标：在 ROP 被 CFI 挡死之后，用同一个 OOB 加原语做一条**纯数据、CFI 无关**的利用链。
> 本文只做离线设计与证据核对；**未上设备**。所有偏移都来自本机
> `kernel.symbolized.elf` 反汇编（`analysis/kdis.py`），不是 pipa(4.19) 的假设。
>
> **代码状态（2026-10-26 晚）**：`pipa/exploit_p780.c` 已加入
> `--data-sl-off`（完整链）、`--data-geo-only`（只做地址泄漏 + slab 配对，
> 不触发 OOB）、`--slab-shift N`（默认 15）。已用 NDK r26d 编译通过，
> 产物 `pipa/exploit_p780_new`（1,166,256 B，
> sha256 `2f54b23458f753edeec97b75c9fca55e658c2935e12b319dd2b005e1771b6c7d`）。
> **尚未上设备**。

## 0. 一句话

用 OOB 加原语把 victim netlink_sock 的 `sk_receive_queue.next` 指向**上方相邻槽**里
我们喷的 fake `sk_buff`；`recv()` 时 `skb_dequeue()` 的两次指针写
`next->prev = prev; prev->next = next` 就是任意 8 字节指针写。
第一次写目标选 `selinux_state`（已知全局，不需要任何泄漏）即可关 SELinux；
选 `cred->cap_effective`（需要 cred 泄漏）即可拿 uid 0；
选 `current->cred`（需要 task_struct 泄漏）即可整块 fake cred。

## 1. 原语与 CFI 边界（已定）

- `values[n] += perf_event_count(sub)`，8 字节加；sibling s 落点 `values+8*(s+1)`。
- `NR_SIBLINGS=8446` → `read_size=67584` → u16 2048 → 下一槽 = `values+2048`。
- `__sk_destruct` 的 `sk_destruct` 调用只接受 86 项 CFI stub 表
  （`0xffffffc0114dea48`），`netlink_sock_destruct_work`/pivot 不在表内 → pipa 的
  fake sock 路径不可用（README §19.4.2）。
- 本链**不调用任何被 OOB 改写的函数指针**，只利用 `skb_dequeue()` 里的两次普通
  store，因此不受 CFI 影响。

## 2. 双写原语（本机 skb_dequeue，0xffffffc011160de4）

```
0x11160df8  add  x19, x0, #0x14        ; &list->lock
0x11160e00  bl   _raw_spin_lock_irqsave
0x11160e08  ldr  x8,  [x21]            ; x8 = list->next
0x11160e0c  cmp  x8,  x21              ; empty?
0x11160e14  csel x20, xzr, x8, eq      ; skb = list->next
0x11160e28  ldp  x8, x9, [x20]         ; x8 = skb->next, x9 = skb->prev
0x11160e2c  stp  xzr, xzr, [x20]       ; skb->next = skb->prev = NULL
0x11160e30  str  x9, [x8, #8]          ; *(next + 8) = prev
0x11160e34  str  x8, [x9]              ; *(prev)     = next
```

注意：
- `list->prev` 不参与 unlink；只要求 `list->next` 指向 fake skb。
- `list->qlen`（sk+0xe0）会被减 1；空队列变成 -1，但后续 `skb_queue_empty()` 看的是
  `next == list`，不看 qlen。
- 两次写是**指针值**，不是任意值；所以目标地址和写入值必须设计成“值即地址”。

## 3. 5.4 结构偏移（反汇编证据）

| 字段 | 偏移 | 证据 |
|---|---|---|
| `sk_receive_queue`（`sk_buff_head`） | **0xd0** | `netlink_sock_destruct` `add x0,x19,#0xd0; bl skb_queue_purge`；`__skb_try_recv_datagram` `add x25,sk,#0xd0` |
| `sk_receive_queue.qlen` | 0xe0 | `skb_dequeue` 里 `[x21,#0x10]`，x21 = sk+0xd0 |
| `sk_receive_queue.lock` | 0xe4 | `skb_dequeue` `add x19,x0,#0x14` |
| `sk_buff.next` | 0x00 | `ldp x8,x9,[x20]` |
| `sk_buff.prev` | 0x08 | 同上 |
| `sk_buff.len` | 0x70 | `skb_copy_bits` `ldr w8,[skb,#0x70]`；`netlink_recvmsg` `[x25,#0x70]` |
| `sk_buff.data_len` | 0x74 | `skb_copy_bits` `ldr w9,[skb,#0x74]` |
| `sk_buff.end` | 0xcc | `skb_release_data`/`skb_copy_bits` `ldr w9,[skb,#0xcc]` |
| `sk_buff.head` | 0xd0 | `skb_release_data` `ldr x9,[skb,#0xd0]`；`head+end = skb_shinfo` |
| `sk_buff.data` | 0xd8 | `skb_copy_bits` `ldr x9,[skb,#0xd8]` |
| `sk_buff.users` | 0xe4 | `consume_skb` `ldr w8,[skb,#0xe4]!` |
| `nlk->portid` | 0x348 | `netlink_getname` `ldr w8,[x21,#0x348]` |
| `selinux_state` | `kbase+0x27d6000` | 0xffffffc012856000 - KBASE |

## 4. 布局与常量

```
slab 基址 B（默认 32KB/16 槽；用 --slab-shift 按 slabinfo 调）
  B+0x000  slot0 = V = perf values buffer （read 时分配，read 后 kfree）
  B+0x800  slot1 = S = victim netlink_sock
  B+0x1000 slot2 = fake skb 的 skb data buffer
```

- values buffer 落 V，OOB 目标 S；fake skb 在 slot2。
- UDP payload 在 skb data buffer 内的偏移 = `P_OFF`。**离线推导为 44**：
  loopback 的 `LL_RESERVED_SPACE` = `HH_DATA_MOD` = 16，IPv4 头 20 + UDP 头 8，
  16+20+8 = 44，与 pipa 的 4.19 经验值一致。仍需一次设备校准确认
  （若 5.4 的 `needed_headroom`/IP options 不同，delta 会偏）。
- fake sk_buff 地址必须 **8 字节对齐**（`skb_dequeue` 用 `ldp/stp`，未对齐会 fault）。
  payload 起点是 `B+0x1000+P_OFF`，所以取
  `F = B + 0x1000 + P_OFF_ALIGN`，`P_OFF_ALIGN = (P_OFF + 7) & ~7`；
  若 `P_OFF=44`，`F = B+0x1030`（payload 前 4 字节为 pad）。
- victim `sk_receive_queue.next` 初值 = `S + 0xd0 = B + 0x8d0`。
- OOB 加数：

```
delta = F - (S+0xd0) = 0x1000 + P_OFF_ALIGN - 0x8d0 = 0x730 + P_OFF_ALIGN
```

  若 `P_OFF_ALIGN=48`，`delta=0x760=1888`（page-fault 计数即可，远小于
  CPU_CLOCK 4.3s 的 2^32）。
- OOB sibling 下标：

```
s = (2048 + 0xd0)/8 - 1 = 281
```

  即 sibling 281 的计数设为 `delta`；其余 sibling 计数为 0（加 0 不改内存）。

## 5. 目标 A：`selinux_state`（推荐先做，零泄漏）

一次 unlink 的两次写：

```
fake->next = A - 8          // A = selinux_state
fake->prev = C              // C = V（slot0；64KB 对齐时 byte0=byte1=0）
=> *(A)     = C             // selinux_state[0..7] = C 的 8 字节
=> *(C)     = A - 8         // 落在 V+0（dummy skb data buffer 的 headroom），无害
```

注意第二次写的地址是 `prev`（C）本身，不是 C+8。

要求 `C = V` 是 **64KB 对齐**的槽（这样 `C & 0xffff == 0`）：

- `selinux_state.disabled      = C[0] = 0`
- `selinux_state.enforcing     = C[1] = 0`  ← 关 SELinux
- `selinux_state.checkreqprot  = C[2] = 0`
- `selinux_state.initialized   = C[3] = B 的 bit24..31`（通常非 0；为 0 也只是 hook 早退）
- `selinux_state.policycap[0..3] = C[4..7] = 0xc0,0xff,0xff,0xff`（全开）
- `avc`(+16)/`ss`(+24) 不被这 8 字节覆盖。

`C=V` 的可行性：32KB slab 的基址 mod 64KB 只有 0 或 0x8000；选基址 mod 64KB = 0 的
slab 即可（泄漏 sock 地址后按 `addr & 0x7fff` 分组，再看 `(base & 0xffff)==0`）。

优点：不需要 cred/current/task 泄漏，不需要 P_OFF 以外的未知量。
缺点：只关 SELinux，不给 uid 0（DAC/能力还在）。

## 6. 目标 B：`cred->cap_effective`（拿 uid 0；需要 cred 泄漏）

- `cred->cap_effective` 偏移 **0x38**（pahole：cap_permitted +48，cap_effective +56）。
- 写 `C = V + off` 到 `cred+0x38`：
  - `fake->next = C`、`fake->prev = A`（A = cred+0x38）：
    `*(C+8)=A`（payload scratch）、`*(A)=C`（cap_effective）。
  - 低 32 位 = `V+off`。V 2048 对齐，`off` 低 11 位可控。
    **优先选 8 字节对齐的 C**（`off` 为 8 的倍数），例如 `off=0x3c0`：
    bits6..9 置位 → CAP_SETGID(6)、CAP_SETUID(7)、CAP_SETPCAP(8)、
    CAP_LINUX_IMMUTABLE(9)；低 3 位为 0，所以 **没有** CAP_DAC_OVERRIDE(1)/
    CAP_DAC_READ_SEARCH(2)。拿到 uid 0 后，root-owned 文件按 owner 匹配即可访问。
    （若坚持要 CAP_DAC_OVERRIDE，需要 `off` 低 3 位非 0，`*(C+8)` 变成未对齐
    `STR`；arm64 普通内存支持未对齐单寄存器 store，但不如 8 对齐稳妥。）
  - 高 32 位 `0xffffffc0` → cap 32..63 全开（含 CAP_MAC_ADMIN=33）。
  - 所以 `cap_effective` 写完后 `setuid(0)` 的 `capable(CAP_SETUID)` 通过。
- **cred 指针怎么来**：`__arm64_sys_getuid`（`kbase+0x261e88`）：
  ```
  mrs x8, sp_el0          ; current
  ldr x8, [x8, #0x838]    ; x8 = current->cred
  ...
  ldr w8, [x8, #4]        ; uid
  ```
  用现有 `PERF_SAMPLE_IP|PERF_SAMPLE_REGS_INTR` 采样器，在
  `IP ∈ [getuid+8, getuid+0x10)` 时取 **x8**，就是 cred 指针（IP 过滤消除歧义）。
  - 采样器已是 task-attached、period=4、33 个 regs；复用 `samp_begin/end` 与 ring 解析。
  - 需要新函数 `cred_addr_of()`：循环 `syscall(SYS_getuid)`，按 IP 过滤，x8 取众数。
  - 校验：`(cred & 0x3f)==0`、线性映射、跨多次采样稳定。
- 第二次写 `*(C+8)=A`（payload scratch，值是指针 A），无害。
- 注意：`setuid(0)` 后 `cap_emulate_setxuid` 可能把 effective 重置；但 uid 0 已经拿到，
  DAC 上 root 拥有 root-owned 文件；后续 SELinux 仍受 shell 域限制。

## 7. 目标 C：`current->cred`（整块 fake cred；需要 task_struct 泄漏）

- `current->cred` 偏移 **0x838**（`prepare_creds` `ldr x21,[sp_el0,#0x838]`；real_cred 0x830）。
- 写 `C = fake_cred 地址` 到 `current->cred`：
  - `fake->next = C`（fake cred）、`fake->prev = A`（A = current->cred）：
    `*(C+8)=A`（会覆盖 fake cred 的 gid/suid，见下）、`*(A)=C`。
  - fake cred 在 slot0 的 payload 里：usage=1、uid/euid/fsuid=0、caps 全 1、
    user_ns=init_user_ns、user=root_user、group_info=init_groups、security=假 LSM blob（sid=1）。
  - 第一次写会把 `&current->cred` 这个指针写到 fake cred 的 +8（gid/suid），
    所以 gid/suid 会是垃圾；uid/euid/fsuid 仍是 0，cap 与 security 不受影响。
    另一方向（`next=A-8, prev=C`）会覆盖 fake cred 的 usage/uid，更糟，不采用。
  - 需要 `current` 泄漏：`__arm64_sys_getuid` 的 `mrs x8,sp_el0` 之后、
    `ldr x8,[x8,#0x838]` 之前，x8 = current；用 IP 精确过滤（+0/+4）取 x8。
  - 该路径最强大（uid0 + caps + kernel SID 一次到位），但 IP 窗口更窄、风险更高。
- 若 cred 泄漏（目标 B）已拿到，可以从 cred 反推 current 吗？不能（cred 里没有
  指回 task_struct 的字段）。所以 C 需要单独的 current 泄漏。

## 8. 堆布局步骤（目标 A）

1. pin CPU；喷 `NL_SPRAY=6000` 个 netlink sock（`socket(PF_NETLINK, SOCK_RAW, NETLINK_ROUTE)`）。
2. 用现有 perf-regs 采样泄漏每个 sock 的地址（`sock_addr_of`/`sock_addr_map`）。
3. 按 slab 分组（`--slab-shift`，默认 15）；找**当前 slab**（最后分配 sock 的 slab）：
   - `base & 0xffff == 0`（目标 A 需要 C=V 64KB 对齐；因此 victim 必须是 slot1，
     hole 是 slot0/slot2）；
   - slot0/1/2 都是泄漏到的 live sock（地址 `base`、`base+0x800`、`base+0x1000`）；
   - 不要求整个 slab 满：只要 slot0/1/2 活，其余空闲槽不影响（free 后 freelist 是
     slot0 → slot2 → 其它）。
   - 当前 slab 不满足时，逐个补分配 sock（泄漏地址后检查），直到满足；最多 256 个。
4. 先 `close(slot2)`，再 `close(slot0)`；等 RCU（`--rcu-ms`）让两个 kfree 落到
   per-cpu freelist，顺序为 **slot0 → slot2**。
5. 设 sibling 281 计数 = `delta = 0x730 + P_OFF_ALIGN`（P_OFF_ALIGN=48 → 0x760）；
   其余 sibling 计数 0（数据链模式不要同时设 portid mark，避免额外改 victim 的 0x348 字段）。
6. `read(sib_fds[0], ...)`：
   - kzalloc(2048) 取 slot0（V），OOB 把 `S+0xd0` 写成 `F`；
   - read 返回时 kfree(V)，freelist 头 = V → slot2。
7. 立刻喷两个 UDP payload（`PAYLOAD_LEN=1640`）：
   - 第一个落 V（dummy；`C=V` 的第二次写 `*(V)=A-8` 落在它的 headroom V+0，
     内核不读这段，安全）；
   - 第二个落 slot2（fake skb）。
   注意：如果第一个 payload 没落 V，V+0 可能还是 freelist 指针，第二次写会破坏
   freelist；所以“第一个 payload 落 V”也是本链成立的前提之一。
8. `recv(victim_fd, ...)`：`skb_dequeue` 取 `list->next = F`，两次写完成
   `selinux_state = V`；fake skb 的 len=0、users=2，`consume_skb` 不释放。
9. 读 `/sys/fs/selinux/enforce` 验证 `0`。

fake payload 需要设置的字节（`F = slot2 + P_OFF_ALIGN`；payload 从 slot2+P_OFF 开始，
所以 fake skb 的字段写在 payload 偏移 `P_OFF_ALIGN - P_OFF` 起；P_OFF=44、ALIGN=48 时
payload 前 4 字节是 pad）：

| F+ | 值 |
|---|---|
| 0x000 | `A-8` = `selinux_state-8` |
| 0x008 | `C` = `V` |
| 0x070 | 0 (len) |
| 0x074 | 0 (data_len) |
| 0x0cc | 0 (end) |
| 0x0d0 | `F+0x100` (head) |
| 0x0d8 | `F+0x100` (data) |
| 0x0e4 | 2 (users) |
| 0x108 | 0 (`skb_shinfo` 的 +8；`head+end=F+0x100` 处) |

## 9. 未解决/需设备校准

1. **P_OFF**：离线推导为 44（`HH_DATA_MOD 16 + IPv4 20 + UDP 8`），与 pipa 经验值
   一致；但 5.4 的 `LL_RESERVED_SPACE`/`needed_headroom` 若有差异，delta 会偏。
   仍建议一次 `--skbgeo` 风格的校准（单次 OOB read）确认。
2. **槽位回收顺序**：close 的 kfree 是 RCU 延迟；要求两次 free 都落在 c->page，
   且顺序 slot0 → slot2。需要在设备上验证（geo-only + portid probe + 读回）。
3. **post-read payload 落点**：两个 send 的 2048 分配必须按 V、slot2 顺序落到
   per-cpu freelist 头；send 路径里若有其它 2048 分配会打乱。需要 prefill/最小化。
4. **recv 生存**：fake skb 的 len/users/head/end 布局已按反汇编设计，但
   `skb_copy_datagram_msg(0)` 与 `skb_free_datagram` 的真实行为需实测。
5. **kmalloc-2048 的 order/objs_per_slab**：按 8 CPU、slub_min_objects 默认推是
   order 3/16 槽；需 `/proc/slabinfo` 的 `kmalloc-2k` 行确认（`--slab-shift`）。
6. **目标 B/C 的泄漏**：getuid x8 采样需要新代码与实测；IP 窗口窄，需要环大小/采样率调参。

## 10. 最小设备实验（每次 boot 只做一步）

1. **修常量后的 portid probe**（1 次 OOB read）：确认 values buffer 落在某个 live
   netlink sock 的下方槽（`scan_portid_mark()` HIT）。
2. **`--data-geo-only`（不触发 OOB）**：验证 6000 sock 地址泄漏、slab 分组、
   slot0/1/2 配对；打印 `base/V/S/F/fds`；不对内核写。用来确认 `--slab-shift`
   与 `/proc/slabinfo` 一致。
3. **P_OFF/槽位校准**（1 次 OOB read）：`--skbgeo` 风格，在 +1 槽打一条 mark 带，
   recv 回 payload 看哪个 offset 被改；得到 P_OFF 与 2048/4096 粒度。
4. **目标 A 全链**（1 次 OOB read）：`--data-sl-off`，按 §8 执行，读 enforce 验证。
5. 目标 B/C 在 A 稳定后再做。

## 11. 与 pipa 的差异

- pipa 的 `sk_destruct → netlink_sock_destruct_work` 依赖 CFI 类型哈希相同；本机是
  86 项 stub 表，`_work` 不在表内 → 不可用。
- pipa 用 `skb` 载荷 + pivot + ROP；本链完全不用 ROP，不用 fake sock
  `container_of`，只用 `skb_dequeue` 的两次 store。
- pipa 的 cg/regular 两 cache 邻接不适用；本链在单一 kmalloc-2048 内做槽位配对。

## 12. 代码入口（已编译，未上设备）

| flag | 行为 |
|---|---|
| `--data-geo-only` | pin cpu0 → samp_init(64 pages) → 喷 6000 sock → 泄漏地址 → 找 64KB slab 的 slot0/1/2 → 打印并停（**无 OOB**） |
| `--data-sl-off` | 同上，然后 close slot2/slot0 → 等 RCU → 单次 OOB read → 发 dummy/fake → recv 触发 → 读 enforce |
| `--slab-shift N` | slab order，默认 15（32KB/16 槽）；按 `/proc/slabinfo` 调整 |
| `--rcu-ms N` | close 后的 RCU 等待，默认 3000 |

代码位置：`pipa/exploit_p780.c` 的 `data_sloff_flow()` / `build_data_fake_skb()`；
`setup_group()` 在 `--data-sl-off` 下设 `no_calib=1`，只保留 sibling 281 非零。


# 6931 observed-V 设计：先看 values 地址，再做 OOB（2026-10-27，离线）

> 目标：把 6931 数据链从"猜 V"改成"看 V"。只用于机主自有 P780；
> 本文是流程与常量设计，不含可直接运行的载荷。**未上设备。**

## 0. 为什么换目标

两次 OOB 都因为 `values` 没有落在预期的 V 槽位而 panic。根因是：

- netlink sock 的释放是 `sk_free → call_rcu → __sk_destruct → kfree`，异步；
- SLUB 的下一次分配取当前 CPU 的 `c->freelist`，释放对象若不在当前 slab，
  或 RCU 还没跑，就会被别的分配抢走。

另外，之前的目标 B/C（`cred->cap_effective` / `current->cred`）**只改 uid，
不改 SELinux 域**：利用进程仍在 `shell` 域，uid 0 也写不了 boot 分区。
真正有价值的是 **target A：把 V 写进 `selinux_state`**，让 SELinux 变 permissive；
之后用现有的 installd uid0 shell（Elevate）直接 `dd` boot/vbmeta。

所以本设计只做 target A，并且 V 必须是**观测到的**，不是假设的。

## 1. 观测点：`__perf_read_group_add` 的 x19

本机 `kernel.symbolized.elf` 反汇编（静态地址）：

```
0xffffffc01044a96c  __perf_read_group_add
0xffffffc01044a98c  mov  x19, x2        ; x19 = values
...
0xffffffc01044aa74  ...                 ; for_each_sibling 循环
0xffffffc01044aa84  ldr  x10, [x9, #0xa0]
...
0xffffffc01044aac8  b    #0xffffffc01044aa74
0xffffffc01044aa60  ldp  x20, x19, ...  ; 恢复 x19
```

- `x19` 在整个循环里始终是 `values`（kzalloc 返回值）；
- 循环遍历 8446 个 sibling，时间窗口很长，PMU 采样很容易命中；
- 采样 `x19`，目标 IP 取 `0xffffffc01044aa84`（窗口 `aa74..aac8`），
  slide 加上即可。

采样器就是现有的 `netlink_addr_leak.c` 逻辑：`PERF_TYPE_HARDWARE/CPU_CYCLES`，
`PERF_SAMPLE_IP|PERF_SAMPLE_REGS_INTR`，只采 `x19`，这次把目标 IP 换成上面的地址。

## 2. 流程

常量：`V = slot v` 的地址，`S = V + 0x800`（victim），`F = slot f + 0x30`（fake skb）。

1. **建组**：leader `PERF_FORMAT_GROUP` enabled；8446 个 sibling（DUMMY disabled），
   其中 **sibling 280 = PAGE_FAULTS，初始 disabled**（read0 时计数 0）。
2. **选址**：喷 sock、泄漏，选同一 slab 里相邻的 `v, s=v+1`，再选一个 `f>s`；
   记 `V/S/F` 的 socket fd。
3. **释放**：`close(f)`、`close(v)`，等 RCU（2 s）；不做 probe 假设。
4. **read0（safe）**：`read(leader, buf, 2048)`，目标 sibling 计数为 0；
   同时 PMU 采样 x19。读返回 2048；从采样里取 `x19` 的众数 = **X**。
   - 这一步 OOB 走查是"读改写同值"，已验证不会崩。
5. **判定**：如果 `X != V` → **abort，不做 OOB**，换一轮再来。
   如果 `X == V`：
   - 读返回时 `kfree(values)` 已把 V 放回 `c->freelist` 头；
   - 立刻校准 sibling 280 到 `delta = F - (S + 0xd0)`（页错误法，见 §3）；
   - **紧接着** read1：values 复用 V，OOB 把 `S+0xd0` 改成 F。
6. **payload**：`send` dummy（占 V）→ `send` fake（占 f）；`recv(victim)` 触发
   `skb_dequeue` 双写，把 `selinux_state` 写成 V。
7. **验证**：`getenforce` 应为 Permissive；随后用 Elevate 的 uid0 shell `dd`
   testkey 签名的 boot_b / vbmeta_b。

## 3. read0 与 read1 之间的校准

- 校准必须在 read0 之后、read1 之前完成，且尽量不产生 kmalloc-2k 分配；
- 页错误校准只在用户页上触发缺页：分配页表页、anon_vma 等，通常不是 2k；
- 步骤：`mmap` 预触 → `MADV_DONTNEED` → `ioctl(leader, ENABLE)` →
  `ioctl(target, RESET)` → 触 `delta` 页 → `ioctl(leader, DISABLE)` → `read(target)` 校验；
- 若校准后 `read(target) != delta`，abort（read1 不能跑）。

## 4. target A 的写入数学

- `selinux_state` 静态地址：`0xffffffc012856000`（= `_text` + `0x27d6000`），
  运行时 `A = 0xffffffc012856000 + slide`；
- fake skb 在 F：`next = A - 8`，`prev = V`；
- `skb_dequeue` 的两次写：
  - `*(next + 8) = prev` → `*(A) = V`：`selinux_state` 首字节变成 V 的低字节，
    V 是 `0x800` 对齐 → 低字节 0 → enforcing=0；
  - `*(prev) = next` → `*(V) = A - 8`：落在 dummy payload 里，无害。
- delta 仍按 `F - (S + 0xd0)` 计算，由 sibling 280 的页错误计数提供；
- 下标固定：`(S + 0xd0 - V) / 8 = 0x8d0/8 = 282` → sibling 280。

## 5. 失败门与安全点

| 门 | 判据 | 动作 |
|---|---|---|
| read0 采样 | 没有 X，或 X 不稳定 | abort，不 OOB |
| X != V | — | abort，不 OOB（read0 安全） |
| 校准后计数 != delta | — | abort |
| read1 后 `recv` 返回 EAGAIN | V 又被抢 | 已 OOB，可能 panic；记录后重启 |
| `getenforce` 仍 Enforcing | 写入没命中 | 重启，重新来 |

只有 X==V 且校准精确时才进入 read1；这是本设计相对前两次的核心改进。

## 6. 后续：permissive 之后怎么刷

1. 用 `release/Elevate-1.0.apk` 起 uid0 installd shell（permissive 下 SELinux 不再拦块设备）；
2. 预先在 PC 上用 AOSP testkey 生成：
   - Magisk/KernelSU 处理过的 `boot_b`；
   - `avbtool make_vbmeta_image --key testkey_rsa4096.pem` 的 `vbmeta_b`（含 boot 描述符）；
3. `adb push` 到 `/data/local/tmp`，在 Elevate shell 里
   `dd if=... of=/dev/block/by-name/boot_b`、`vbmeta_b`；
4. 重启，验证 root 与 AVB（testkey 应通过）。

## 7. 还没解决/需要实测的量

- read0 采样能否稳定拿到 x19（窗口很大，预计可以）；
- read0 的 X 是否经常等于 V（取决于 free/RCU 时序；不等就 abort 重试）；
- 校准阶段是否会把 V 抢走（页表分配 vs kmalloc-2k）；
- fake skb 的 `head/end/users/shinfo` 是否能活过 `consume_skb`（target A 仍需 recv 路径）。

建议第一次实现只做 **步骤 1–5**（read0 + 采样 + X 判定），不接 payload；
确认"X==V"能稳定出现后，再加 read1 和 target A。

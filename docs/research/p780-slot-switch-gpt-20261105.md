# A 槽写入成功与切槽失败：GPT 层分析（2026-11-05）

## 1. 已完成的写入

用自建 otacerts 证书页 + 自签多分区 payload，update_engine 在 B 槽运行时向 **A 槽**写入：

```
InstallPlan: source_slot: B, target_slot: A, switch_slot_on_reboot: true
PartitionInfo new boot        size 51408896
PartitionInfo new vendor_boot size 1359872
PartitionInfo new vbmeta      size 65536
Applying 1 operations to partition "boot"
Applying 1 operations to partition "vendor_boot"
Applying 1 operations to partition "vbmeta"
Completed 3/3 operations (100%)
PostinstallRunnerAction ... kSuccess
Update successfully applied, waiting to reboot.
```

payload：`evidence/20261105/payload_a_full.bin`（52,835,192 B，
sha256 `078b95ad…c1`），内部 vbmeta 为 `vbmeta_a_test.img`
（sha256 `e2e2120f…7d`），boot/vendor_boot 描述符已替换为 B 镜像，
dtbo/system/vendor/chain 保留 A 原值。

## 2. 结果：重启仍进 B

```
ro.boot.slot_suffix = _b
sys.boot_completed = 1
```

即 `SetActiveBootSlot(A)` 没有改变 ABL 的选择。

## 3. GPT 实际布局

整盘 LUN 为 `/dev/block/sde`，**逻辑扇区 4096 B**：

| 项 | 值 |
| --- | --- |
| GPT header | 偏移 0x1000（LBA1），`EFI PART` |
| entries | LBA2，偏移 0x2000，64 项 × 128 B |
| entries CRC | `0xde6fe889`（与 header 一致） |

关键 entry（相对 dump 起点）：

| 分区 | entry 偏移 | attributes |
| --- | --- | --- |
| boot_a | 0x2400 | `0x00b2_0000_0000_0000` |
| vbmeta_a | 0x2580 | `0x103b_0000_0000_0000` |
| vendor_boot_a | 0x2900 | `0x0400_0000_0000_0000` |
| boot_b | 0x2d80 | `0x007f_0000_0000_0000` |
| vbmeta_b | 0x2f00 | `0x107f_0000_0000_0000` |
| vendor_boot_b | 0x3180 | `0x0400_0000_0000_0000` |

按 Android bootloader 常见编码（bits 48–51 priority，52–55 retries，56 successful）：

- `boot_b`：priority `0xf`，retries `0x7` → ABL 选 B；
- `boot_a`：priority `0x2`，retries `0xb` → 优先级低，不被选。

**结论：A 槽数据没问题，差的是 GPT 的 priority 位。**

## 4. 为什么 update_engine 没改 GPT

`vendor_gpt_block_device` 的写权限只给了 `hal_bootctl`：

```
(allow hal_bootctl vendor_gpt_block_device (blk_file (... write ...)))
```

- `init` 只有 `relabelto misc/metadata` 和写 `misc/metadata`，没有 `relabelfrom vendor_gpt`，不能改 GPT；
- `system_app`/shell 执行 `bootctl set-active-boot-slot a` 均返回
  `Error getting bootctrl v1.0 module`（不是 HAL 客户端）；
- 唯一 HAL 客户端是 `update_engine` / `update_verifier` / `vold`，而
  update_engine 的 `SetActiveBootSlot(A)` 没有产生 GPT 变更（HAL 1.0/1.1
  后端问题，仓库历史也记录切槽未生效）。

## 5. 下一步

只有两条现实路线：

1. **在 hal_bootctl 进程里执行代码**：
   - 目标进程 `android.hardware.boot@1.1-service`，pid 641，
     `u:r:hal_bootctl_default:s0`；
   - 它拥有 `vendor_gpt_block_device` 写权限；
   - 可仿照 init 的 libc++ 页缓存劫持，把 stub 写进该进程加载的
     `/vendor/lib64/libc++.so`（或 HAL 自身二进制），
   - 再让 update_engine 调一次 HAL（`getCurrentSlot`/`setActiveBootSlot`）触发 stub；
   - stub 直接 `pwrite` boot_a/boot_b 的 GPT attributes，并重算 entries CRC
     与 header CRC（主 GPT；备份 GPT 可后补）。

2. **找另一个能写 GPT 的域**：`hal_bootctl_server` 只有 misc；
   `sgdisk` 只有 `vold_device`；没有现成入口。

## 6. 设备状态

- 当前正常启动 B 槽；
- A 槽已写入 B 的 boot/vendor_boot + testkey vbmeta；
- GPT 未被修改，主 GPT 与备份 GPT 仍然一致；
- 没有做任何回滚或擦除。

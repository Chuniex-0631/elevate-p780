# 切槽路线 A：misc bootloader_control 实测与结论（2026-11-05）

## 1. 做了什么

用 writer App + `spawnOrphan` 把一段 init stub 写进
`/system/lib64/libc++.so` 的 0x790b0，并把 0x62fb4 的 sentry 改成跳转；
stub 在 init 域执行后：

- `openat("/dev/block/by-name/misc", O_WRONLY)` 返回 **fd=23**（成功）；
- `pwrite64` 写入 32 字节 `bootloader_control`：
  - `slot_suffix = "_b"`
  - `magic = 0x42414342`（"BCAB"）
  - `version = 1`
  - `slot_info[0] = 0x6f`（A：priority 0xf）
  - `slot_info[1] = 0x0e`（B：priority 0xe）
  - `crc32` 覆盖前 28 字节，写偏移 0x1c（标准 zlib CRC32）

## 2. 结果

重启后仍然：

```
ro.boot.slot_suffix = _b
```

## 3. 结论

**ABL 不读 misc 的 bootloader_control，或者至少不把它作为主判据。**

GPT 里的 attributes 才是实际生效的：

```
boot_a  0x00b2000000000000  priority=2
boot_b  0x007f000000000000  priority=15
```

`libboot_control_qti.so` 的 `SetActiveBootSlot` 写 misc，只是兼容路径；
真正决定槽位的是 GPT。

## 4. 权限边界（实测）

| 域 | 读/写 GPT LUN `/dev/block/sde` |
| --- | --- |
| init | open O_WRONLY 返回 **-13 EACCES** |
| untrusted_app | 不能读 vendor 库（EACCES） |
| hal_bootctl | 唯一有 `vendor_gpt_block_device` 读写权限 |

## 5. 新增能力

writer App + `spawnOrphan()` 可以：

1. 任意写 `/system/lib64/libc++.so` 的页缓存；
2. 把 0x62fb4 改成跳转；
3. 触发 init 域执行自建 stub；
4. stub 可通过 `/metadata` 回传结果。

这条链已经能稳定执行 init 代码（fd 回传、EACCES 回传都验证过）。

## 6. 下一步唯一可行方向

在 **hal_bootctl** 进程里执行代码：

- `/system/lib64/libc++.so` 是 app 可读可页写的；
- HAL 进程也加载这个 libc++；
- 在 libc++ 里选一个 HAL 调用 `SetActiveBootSlot` 时会经过的函数做 detour；
- stub 先尝试 `openat("/dev/block/sde", O_WRONLY)`：
  - init/app 会 EACCES；
  - 只有 hal_bootctl 成功，然后写 `boot_a=0x6f`、`boot_b=0x0e`
    和 entries/header CRC；
- 再让 update_engine 调一次 HAL 触发。

难点是选一个“每次 SetActiveBootSlot 必走、又不会破坏原语义”的 libc++ 函数；
备选是 `_Znwm`（operator new）做 inline hook，代价是全局开销。

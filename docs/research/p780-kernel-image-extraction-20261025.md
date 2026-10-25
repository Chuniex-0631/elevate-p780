# P780 内核镜像实机提取（2026-10-25）

> 2026-10-25 实机结果：在 **Bootloader 锁定、无 root、SELinux Enforcing** 的状态下，
> 用 DirtyFrag 页缓存写入改写 `libc++.so` 的 `sentry` 入口，让 **init 域**把
> `/dev/block/by-name/boot_b` 的前 41,767,424 字节（完整内核 `Image`）分块搬到 `/metadata`，
> 再由普通 shell 拉出。这是本仓库此前一直缺的那件东西。

## 1. 结果

| 项 | 值 |
|---|---|
| 提取对象 | `/dev/block/by-name/boot_b`（A/B 槽中的 `_b`） |
| boot 头 | `ANDROID!`，header v3，`kernel_size = 41,767,424`，`ramdisk_size = 9,630,085` |
| 内核格式 | 未压缩 arm64 `Image`（起始 `4d 5a 00 91`，PE/EFI stub） |
| 产物大小 | 41,767,424 字节 |
| SHA-256 | `6df574af40d260c670c32bdee9ceaca023739850d62851d55f77234b89d4f373` |
| 内核版本字符串 | `Linux version 5.4.233-qgki-gea5245e94afe-dirty (android@HTSVR18) (Android (6877366 based on r383902b1) clang version 11…` |
| 与设备 `uname` 一致性 | **逐字一致**（含 `-dirty` 与编译器版本） |

附带取得：`/proc/kallsyms` 前 264,892 字节，**符号名完整、地址全部为 0**（`kptr_restrict=2` 的表现）。

镜像未提交入库（42 MB）；仓库只记录大小、哈希与提取方法。

## 2. 方法

1. 用本仓库既有的 libc++ `sentry` hook（[利用链报告](p780-dirtyfrag-live-exploit-20261025.md)）在 init 域执行载荷；
2. 载荷先 `unlinkat` 掉 `/metadata` 里的旧文件腾空间，再 `lseek` 到指定偏移、以 4 KiB 循环读块设备、写 `/metadata/cur.bin`；
3. 每块 8 MiB，shell `adb pull` 后由下一轮载荷覆盖；
4. 五块拼接成 41,767,424 字节的 `Image`，用 boot 头里的 `kernel_size` 截断。

## 3. 过程中确认的设备约束

| 约束 | 观测 |
|---|---|
| `/metadata` 容量 | 11 MB（`/dev/block/sda14`），只够一块 8 MiB |
| shell 能否删除 `/metadata` 文件 | **不能**（`rm: Permission denied`），必须由 init 自己 `unlinkat` |
| init 能否读块设备 | **能**（`boot_b` 打开与读取均成功） |
| init 能否读 `/proc/kallsyms` | 能，但地址被 `kptr_restrict=2` 置零 |
| init 能否读 `/sys/kernel/notes` | 不能（EACCES） |
| init 能否读 `/proc/kcore` | 不存在（ENOENT） |

## 4. 为什么这一步重要

此前三条主线都卡在"没有镜像"：

- **GhostLock**：需要逐构建的内核符号与结构偏移来生成 profile；
- **`esp_input` 判定**：需要确认本机实现是否真的走 `skip_cow` 分支、是否回移了共享页检查；
- **源码身份**：TINNO 公开的 5.4.61 与运行中的 5.4.233 不同源，镜像到手后才能做二进制级比对。

现在这三条的共同前置已经具备。

## 5. 下一步

1. **离线提取符号表**：从 `Image` 中定位 `kallsyms` 表（`kallsyms_names` / `token_table` / `token_index` / `offsets`）或 BTF，还原符号地址；
2. 用符号地址核对 `esp_input`、`remove_waiter`、`init_cred` 等关键对象是否存在、形态是否与公开源码一致；
3. 依据符号与结构偏移生成 5.4.233 的 GhostLock profile，评估其所需字段能否全部从本镜像得到；
4. 若镜像内符号不可恢复，退回"特征码定位"（用公开 5.4 源码编译同配置的候选，做函数级指纹匹配）。

## 6. 边界

- 提取过程只读块设备，未写入任何分区；页缓存改动已回滚，`libc++.so` 入口与牺牲函数均恢复原始字节。
- 设备 uptime 连续，SELinux 仍 Enforcing。
- `/metadata/cur.bin` 残留在设备上（shell 无权限删除），重启即清空。

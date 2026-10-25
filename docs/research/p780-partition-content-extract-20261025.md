# 系统分区内容整体提取（2026-10-25）

> 目标：官方已停止更新，本机就是最终 ROM。先把能读到的系统内容全部取出来，后续慢慢研究。
> 结论：**已提取 5.66 GB，覆盖 `/system`、`/product`、`/system_ext` 与大部分 `/vendor`。**
> 关键发现：这一步**不需要任何漏洞**——普通 adb shell 就能读 `system_file` 类内容并写 `/data/local/tmp`。

## 1. 方法（比预想简单得多）

之前一直以为需要靠 exploit，是因为 `/system/build.prop` 报 `Permission denied`。但那只是
**该文件有独立标签**（`build_prop`）。`system_file` 类的内容 shell 是可以读的。

于是最直接的办法就是：

```sh
adb shell "cd /system && tar -cf /data/local/tmp/system.tar ."
adb pull /data/local/tmp/system.tar
```

`/product`、`/system_ext`、`/vendor` 同理。

## 2. 实际产出

| 分区 | 大小 | tar 条目 | 读取失败 |
|---|---|---|---|
| `/system` | 1,810,707,456 B (1.81 GB) | 2,966 | 95 |
| `/product` | 3,258,192,896 B (3.26 GB) | 681 | 5 |
| `/system_ext` | 361,280,512 B (0.36 GB) | 1,298 | 15 |
| `/vendor` | 233,448,960 B (0.23 GB) | 1,185 | 2,127 报错 |
| **合计** | **5,663,757,909 B (5.66 GB)** | | |

设备端 `du`：`/system/bin` 14 MB、`/vendor` 224 MB。
`vendor.tar` 223 MB ≈ `du` 的 224 MB，说明**字节层面基本已覆盖**，报错多来自
`vendor_file` 标签下的单个文件读取被拒。

## 3. 缺口与原因

| 缺口 | 数量 | 原因 |
|---|---|---|
| `/system/bin/*` 可执行文件 | 88 | 这些是 `*_exec` 标签（如 `apexd_exec`、`audioserver_exec`），shell 无 read |
| `/system/etc` 少量配置 | 4 | 独立标签（`prop.default`、`selinux` 策略相关） |
| `/system/build.prop` | 1 | `build_prop` 标签 |
| `/system/lib{,64}/bootstrap` | 2 | 特殊标签 |
| `/vendor` 部分文件 | 2,127 报错 | `vendor_file` 标签 |

策略查询结果：`*_exec` 与 `vendor_file` **只有 `init` 和 `crash_dump` 能读**，
而这两个域都**没有可写的大容量通道**（init 只能写 11 MB 的 `/metadata`，
`crash_dump` 连 `/data/local/tmp` 都写不了）。这就是缺口的根因。

## 4. 复现

```sh
# 每个分区
adb shell "cd /system && tar -cf /data/local/tmp/system.tar . 2>/data/local/tmp/err.txt"
adb pull /data/local/tmp/system.tar .
adb shell "rm -f /data/local/tmp/system.tar"
```

无需 root、无需 exploit、无需改任何系统状态。

## 5. 后续可选的补洞方式

1. **88 个 `*_exec` 二进制**（约 10 MB）：用 init 域按文件搬运（`/metadata` 8 MB/轮），
   预计 2–3 轮可完成；
2. **`/vendor` 剩余文件**：同 init 域，但体积可能上百 MB、轮次多；
3. **原始镜像**：仍不可行（无域同时具备"读块设备 + 写大空间"），除非有 EDL programmer。

## 6. 产物位置

- `33-full-extract-20261025/system.tar`（1.81 GB）
- `33-full-extract-20261025/product.tar`（3.26 GB）
- `33-full-extract-20261025/system_ext.tar`（361 MB）
- `33-full-extract-20261025/vendor.tar`（233 MB）
- 对应 `*_err.txt` 为各分区读取失败清单

这些是**运行状态**下的内容（已应用全部 OTA），不是出厂镜像。

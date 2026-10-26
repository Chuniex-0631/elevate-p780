# 分区证据再提取：vendor_boot_a/b、dtbo_a（2026-10-26）

> 背景：2026-10-25 的 `48-init-capability-20261025/partitions/` 目录（16 个分区块 + 三个解包目录）
> 一直没有入仓，本地副本在整理时丢失；仓库里只剩
> [`evidence/partitions/manifest-20261025.json`](../../evidence/partitions/manifest-20261025.json)
> 的 459 条路径、字节数与 SHA-256。
> 本篇记录按 2026-10-25 的同一方法（DirtyFrag 页缓存写 + init 域载荷）在机主自有的同一台 P780 上
> 重新提取，并用 manifest 逐文件核验的结果。

## 1. 结论

三个分区块都逐字节复现了 2026-10-25 的产物，SHA-256 与 manifest 完全一致：

| 文件 | 字节 | SHA-256 | 与 manifest |
|---|---:|---|---|
| `vendor_boot_b.00.bin` | 8,388,608 | `226b58c386e6d34d90847f94c4ea779fda7edd0e9b0cced6bae74e32d495e384` | 一致 |
| `vendor_boot_a.00.bin` | 8,388,608 | `d61a895649c123f01dffa66e1eded0e6fc57f7b4b32003c41a62387d3c0e9ce5` | 一致 |
| `dtbo_a.00.bin` | 8,388,608 | `e03beb3a7f8be87c44cfb62cd635cc717677330b932e644f146357e97552dfa1` | 一致 |

解包内容同样全部通过哈希核验：

| 解包产物 | 文件数 | 结果 |
|---|---:|---|
| `vendor_boot_b_ramdisk/` | 51 | 51/51 一致（45 个 first-stage `.ko` + `modules.alias/.dep/.load/.softdep` + 2 个 fstab） |
| `vendor_boot_a_ramdisk/` | 51 | 51/51 一致 |
| `dtbo_a_entries/` | 22 | 22/22 一致 |

`tools/partitions/verify_manifest.py` 的当前结果是 **ok=133、mismatch=0**；
缺的 326 条全部是 `persist` / `persist_tree` / `modemst1/2` / `fsg` / `fsc`，按仓库政策
（个人/IMEI 数据不入仓）本就不在公开树里，manifest 只保留其哈希。

## 2. 方法（与 2026-10-25 相同）

### 2.1 设备状态

- P780，`ro.boot.slot_suffix=_b`，指纹 `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`；
- 先重启一次，使 libc++ 的页缓存回到磁盘上的原始内容（上一轮实验留下的补丁不跨重启）；
- `adb shell` 仍是 `uid=2000(shell)`、`u:r:shell:s0`，SELinux Enforcing。

### 2.2 钩子与载荷

沿用 Elevate APK（`release/Elevate-1.0.apk`）的 `patchProbe()`：

1. 用 DirtyFrag（CVE-2026-43284）按 16 字节块把载荷写进 `/system/lib64/libc++.so`
   的页缓存：入口 `0x62fb4`（`__sentry` 构造）改成 `adrp/add/br` 跳板，载荷落在
   `0x790b0` 的零引用函数里；
2. 载荷长度必须与 APK 内 `PatchData.STUB_HEX` 完全一致（本次为 **816 字节**），
   否则要重建整个 DEX；因此本次只替换了 `classes.dex` 里的十六进制字符串常量
   （等长替换），重算 DEX 头的 adler32/SHA-1 后重新签名安装；
3. 新载荷的门控从“installd”改为 **`gettid()==1 && getpid()==1 && uid==0`**
   （init 主线程），动作是：取一次性锁 `/dev/p780_vbN_lock` → 删旧
   `/metadata/cur.bin` → 打开 `/dev/block/by-name/<分区>` → `mmap` 8 MiB →
   循环 `read` 到 8 MiB → `write` 到 `/metadata/cur.bin` → 关闭 fd →
   重放被覆盖的 4 条 sentry 序言 → 跳回 `0x62fc4`。

载荷源码见 [`tools/partitions/init_dump_stub.S`](../../tools/partitions/init_dump_stub.S)。

### 2.3 触发

`patchProbe()` 写完块后会 `spawnOrphan()`：制造一个被 init 回收的孤儿进程，
让 init 主线程走 libc++ 日志路径，从而命中 `__sentry` 钩子。命中率不是 100%，
所以本次在等待 `/metadata/cur.bin` 达到 8 MiB 期间，额外从 `adb shell` 反复制造
短命孤儿（`(sleep 1) &` 之类在 shell 退出后被 reparent 到 init，再由 init 回收），
把“一次 patch 只能触发一次”的窗口放大成可重试的触发序列。

### 2.4 拉取、核验、回滚

```text
patch → 等 /metadata/cur.bin == 8,388,608 B → adb pull → 与 manifest SHA-256 比对
      → am force-stop；am start … -e probe unpatch → 拉 /system/lib64/libc++.so 复核
```

`unpatch` 把入口 16 字节和 816 字节载荷区写回原始内容；复核点是
`0x62fb4 = fd7bbea9f30b00f9fd0300911f000039`（原始序言）与 `0x790b0` 恢复为原函数体。
全程没有写任何分区，SELinux 保持 Enforcing，也不需要重启。

### 2.5 离线解包

- **vendor_boot**：v3 头（`VNDRBOOT`，page 4096），vendor ramdisk 在 `0x1000`，
  gzip + newc cpio。B 槽 ramdisk `700,473` B、A 槽 `700,501` B，解包后各 51 个普通文件；
- **dtbo**：头部是**大端**存储（`d7 b7 ab 1e` 而不是常见的 `1e ab b7 d7`），
  `total_size=3,296,351`、22 个 entry、page 4096；每个 entry 的 `dt_offset` 直接指向
  FDT blob（同样大端）。旧页面只记了 magic/entry 数/page size，没有记字节序，本次补上。

## 3. 与 2026-10-25 记录的差异

| 项 | 旧记录 | 本次实测 |
|---|---|---|
| vendor_boot dtb | “dtb 256 B” | 头部 `dtb_size = 647,364`（632 KiB）；ramdisk 之后的确有大段 dtb |
| dtbo 字节序 | 未记 | 整个 dtbo 镜像按大端解析；按小端读会得到 `magic=0x1eabb7d7` 的假值 |
| APK 载荷长度 | 仓库 `PatchData.java` 为 784 B | 已安装/Release APK 内实际是 **816 B**，以 APK 内 DEX 为准 |
| vendor ramdisk | 700,501 / 700,473 B | 完全一致 |

## 4. 未恢复 / 不在本次范围

- `persist.00..03.bin`、`persist_tree/`（318 个文件）、`modemst1/2`、`fsg`、`fsc`：
  个人分区与 modem NV，按仓库政策不入仓（manifest 保留哈希，便于机主本地自检）；
- `xbl_b.00.bin`：2026-10-25 上传时 GitHub 返回 401（疑似内容扫描拒收），本地曾保留；
  本次没有重取——ABL 分析用的是已入仓的 `xbl_b.00.bin.strings.txt`；
- `vbmeta_*`、`abl_b`、`devcfg_b`、`misc*`、`frp`、`devinfo`、`xbl_config_b`：仓库原本就有，
  本次一并按 manifest 复核，全部一致。

## 5. 复现

- 载荷源码：[`tools/partitions/init_dump_stub.S`](../../tools/partitions/init_dump_stub.S)
- 清单核验：[`tools/partitions/verify_manifest.py`](../../tools/partitions/verify_manifest.py)

```powershell
python tools/partitions/verify_manifest.py
# manifest entries: 459  ok=133  mismatch=0  missing=326  extras=0
```

提取本身依赖已取得临时 UID0 的设备与 DirtyFrag 原语；步骤、门控与回滚方式见 §2。
只对机主自有设备使用，不写分区、不加载模块、不改 SELinux 状态。

## 6. 产物路径

```text
evidence/20261026/partitions/
├── vendor_boot_a.00.bin        8 MiB
├── vendor_boot_b.00.bin        8 MiB  (B 槽，vermagic 与运行内核同源)
├── dtbo_a.00.bin               8 MiB  (镜像 3,296,351 B)
├── vendor_boot_a_ramdisk/      45 个 .ko + modules.* + first_stage_ramdisk/fstab.*
├── vendor_boot_b_ramdisk/      同上
└── dtbo_a_entries/             22 个 overlay .dtb
```

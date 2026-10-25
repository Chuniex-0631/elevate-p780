# P780 ROM 内容提取包

> 2026-10-25。官方已停止更新，本机即为最终 ROM 状态。
> 本页是仓库内的索引；大文件放在 GitHub Release `p780-rom-20261025`。

## 1. 这是什么 / 不是什么

**是**：设备运行状态下 `/system`、`/product`、`/system_ext`、`/vendor` 的完整文件内容（tar 归档）、
`/system/bin` 下大部分 `*_exec` 二进制、以及运行中的内核镜像 `Image`。

**不是**：可刷写的 `system.img` / `super.img` 原始分区镜像。原始镜像不可得——

| 域 | 读块设备 | 写大容量用户可读空间 |
|---|---|---|
| `init` | 是 | 否（仅 11 MB `/metadata`） |
| `vold` | 是 | 否 |
| `installd` | 否 | 是（`/data/local/tmp`） |

没有域同时具备两者；用 init 经 `/metadata` 中转，3 GB 分区需 300+ 轮，不现实。

## 2. Release 资产

| 文件 | 字节数 | SHA-256（前 16 位） |
|---|---|---|
| `system.tar` | 1,810,707,456 | `dc0c4671b466b6bb` |
| `product.tar.part1` | 1,700,000,000 | `1c331db13f073482` |
| `product.tar.part2` | 1,558,192,896 | `836bcd5044a1bb23` |
| `system_ext.tar` | 361,280,512 | `e7335396d1a1708b` |
| `vendor.tar` | 233,448,960 | `bf3ae9a3bf56faf9` |
| `meta1.tar` | 10,715,136 | `5bc6dbb79a7a0586` |
| `kernel.Image` | 41,767,424 | `6df574af40d260c6` |

完整的 SHA-256 见 [`release-assets.json`](release-assets.json)。

`product.tar` 因为超过 GitHub 单文件 2 GB 限制，拆成 `part1` + `part2`，合并还原：

```bash
cat product.tar.part1 product.tar.part2 > product.tar
```

## 3. 上传清单（人工上传用）

Release 地址：`https://github.com/Chuniex-0631/p780-kernel-research/releases/tag/p780-rom-20261025`

已上传：`meta1.tar`。其余六个需要手动拖拽上传（网页版 Release 编辑页支持拖拽，单文件 <2 GB）：

| 顺序 | 文件名 | 大小 |
|---|---|---|
| 1 | `kernel.Image` | 41.8 MB |
| 2 | `vendor.tar` | 233 MB |
| 3 | `system_ext.tar` | 361 MB |
| 4 | `system.tar` | 1.81 GB |
| 5 | `product.tar.part1` | 1.70 GB |
| 6 | `product.tar.part2` | 1.56 GB |

上传后本地校验（PowerShell）：

```powershell
Get-FileHash .\system.tar -Algorithm SHA256
# 对比 release-assets.json 里的值
```

## 4. 内容覆盖

| 分区 | tar 条目 | 打包时读取失败 |
|---|---|---|
| `/system` | 2,966 | 95 |
| `/product` | 681 | 5 |
| `/system_ext` | 1,298 | 15 |
| `/vendor` | 1,185 | 2,127 报错 |

完整文件清单见 [`file-manifest.txt`](file-manifest.txt)（4,799 行，含每个文件的大小）。

## 5. 已知缺口

见 [`MISSING.txt`](MISSING.txt)。主要缺 32 个 `*_exec` 文件，例如：

```
dex2oat  surfaceflinger  storaged  traced  traced_perf  traced_probes
tombstoned  update_engine  update_verifier  vdc  watchdogd  wificond
tcpdump  pppd  dnsmasq  sgdisk  tune2fs  sdcard  usbd  ...
```

原因：这些只有 `init` / `crash_dump` 域可读，两个域都没有大容量写通道；
用 init 域搬运会触发 init 崩溃重启，因此停止。

已取到的关键守护进程：`init`、`vold`、`netd`、`installd`、`apexd`、`servicemanager`、
`keystore`、`hwservicemanager`、`logd`、`mdnsd`、`lmkd`、`gatekeeperd`、`credstore` 等。

## 6. 提取方法（可复现）

1. `system` / `product` / `system_ext` / `vendor`：普通 adb shell 直接 `tar`
   （`shell` 对 `system_file` 有 read；只有 `build_prop`、`*_exec`、`vendor_file` 等标签被拒）；
2. `*_exec` 二进制：DirtyFrag 页缓存写原语 → init 域载荷 → 分块搬 `/metadata` → `adb pull`；
3. 内核镜像：同 init 域载荷读取 `/dev/block/by-name/boot_b`。

全程可回滚，SELinux 保持 Enforcing，未修改任何分区。

## 7. 研究提示

- 内核 `Image` 已带完整符号表（173,205 条内置符号），见
  [`docs/research/p780-kernel-image-extraction-20261025.md`](../research/p780-kernel-image-extraction-20261025.md)；
- `/system` 内的 TINNO 定制组件（`com.tinno.*`、`journey_diag`）与 AOSP 的差异，可基于
  `system.tar` 做比对；
- `vendor.tar` 覆盖约 223 MB，接近 `du` 报告的全部字节，但报错较多，分析时注意缺项。

## 8. 隐私提示

仓库为 Private 时，Release 资产同样需要登录才能下载；若要让外部模型直接读取，
需要先下载到本地再提供，或临时公开仓库。

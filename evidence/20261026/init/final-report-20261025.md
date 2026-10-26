# init 域能力与只读榨取：收尾报告（2026-10-25）

> 本专题是 GhostLock 判负后的转向：不再依赖内核日志，先把"手上到底还有什么能力"量清楚，
> 再把 init/installd 域能读的东西尽量搬出来做静态分析。
> 结论先行：**能力边界已探明（无运行时 Permissive、pstore 空、kmsg 仅 init），
> 只读资产已基本榨干（9 类分区 + 3 个解包目录），AVB 根信任是 AOSP testkey。**

## 1. 能力盘点（实测）

### 1.1 installd 域（可靠）

用 `21-dirtyfrag-probe` 的 libc++ `sentry` 钩子 + `uid==0 && cmdline 含 "inst"` 门控，
`adb install` 即可稳定触发：

```
Uid: 0
CapEff: 0000003fffffffff      # 38 个 capability 全开（含 CAP_MAC_ADMIN/CAP_SYSLOG/CAP_SYS_RAWIO）
Seccomp: 0
context=u:r:installd:s0
```

- 可读写 `/data`（app 私有目录、`/data/app`、`/data/local/tmp`）；
- 不能 exec `/data/local/tmp` 下的二进制（`shell_data_file` 无 execute）；
- **不能**写 `selinuxfs`（`security:setenforce` 被拒，见 §2）。

### 1.2 init 域（capability 更全，但触发是竞态的）

同一套钩子换成 `gettid()==1 && getpid()==1` 门控，在 init 主线程执行：

| 能力 | 结果 |
|---|---|
| `CapEff` | `0x3fffffffff`（全开） |
| `Seccomp` | 0 |
| 读 `/dev/kmsg` | ✅ 一次性 dump 出 268 KB 当前 boot 日志 |
| 写 `/metadata` | ✅ 唯一可靠的"外带"通道（11 MiB，需注意容量） |
| 读块设备 | ✅ 本报告所有分区镜像都靠它 |
| 触发可靠性 | ❌ 只有 App `patchProbe()` 触发的孤儿回收能命中，且时灵时不灵 |

## 2. SELinux：运行时 Permissive 不可行（有 avc 证据）

installd 载荷尝试 `open("/sys/fs/selinux/enforce", O_WRONLY)` + `write "0"`：

```
open  -> 8          (成功)
write -> -13 EACCES
readback -> '1'     (仍是 Enforcing)
```

init 域 kmsg dump 里抓到的审计记录（[avc-enforce.txt](avc-enforce.txt)）：

```
avc: denied { setenforce } for pid=14510 comm="sh"
  scontext=u:r:installd:s0 tcontext=u:object_r:kernel:s0 tclass=security permissive=0
```

对设备上四份策略文件全量搜索，**没有任何 `(allow ... (security (setenforce)))`**，
只有类定义、`neverallow`、`dontaudit`。结论：

- 运行时切 Permissive **不可行**（连 init 也不行）；
- 由此 `mount tracefs` / kprobe 观测路线一起关闭；
- `security:load_policy` 同样没有 allow。

## 3. 只读资产清单

| 分区 | 大小 | 结论 |
|---|---|---|
| `boot_b` → kernel `Image` | 41,767,424 B | 173,205 符号已恢复（25/27 号专题） |
| `vendor_boot_a` / `_b` | 各 ~704 KB 镜像 | 45 个 first-stage `.ko` + `fstab`；**B 槽 vermagic 与运行内核同源**（`gea5245e94afe`），A 槽是另一套构建（`g2570b53dcf94`） |
| `dtbo_a` | 3,296,351 B / 22 entries | 平台 `blair`/`holi`、电池 `ATL436186_020H_3780mAh`、相机 actuator、ADC 等 |
| `vbmeta_a/b`、`vbmeta_system_a/b` | 各 64 KiB | **RSA4096 公钥与 AOSP `testkey_rsa4096.pem` 逐位相同**；system 用 RSA2048、两槽同钥 |
| `persist` | 32 MiB ext4 | 278 个传感器标定（`icm4x6xa`/`tmd2725`/`icp101xx`/`bu52053nvx`）、Keymaster store、coresight 脚本 |
| `modemst1/2` | 各 3 MiB | modem NV 数据 |
| `fsg` / `fsc` | 3 MiB / 128 KiB | EFS 黄金副本（`IMGEFS` 签名）/ 空缓存 |
| `devinfo` | 4 KiB | 全零（未解锁、未篡改） |
| `frp` | 512 KiB | 仅开头 114 字节非零，无明文状态 |

### 3.1 两个有价值的发现

1. **AVB 根信任是 AOSP 测试密钥**：`vbmeta_a/b` 的 RSA4096 模数 == `09/testkey_rsa4096.pem`。
   含义：签名层面不构成障碍；真正的障碍仍是 Bootloader 锁定（`fastboot flashing unlock`
   返回 `unknown command`）。将来若有任意分区写通道，AVB 一关天然通过。
2. **B 槽 vendor_boot 与运行内核同源**：B 槽 first-stage 模块 vermagic 为
   `5.4.233-gea5245e94afe-dirty`，与 `uname -r` 的 `gea5245e94afe` 一致；A 槽是别的构建。

## 4. 工具与产物

### 4.1 工具

- [`dump_partition.py`](../../../tools/partitions/dump_partition.py)：通用分区 chunk 拉取器（渲染模板 → 构建 → patch →
  触发 → pull → 回滚），支持起始偏移；
- [`cleanup_template.S`](../../../tools/partitions/cleanup_template.S) + `gen_clean.py`：`/metadata` 清理载荷生成器；
- 通用 dump 模板：`25-kernel-dump-20261025/stub_template.S`；
- 其它一次性载荷（kmsg dump、enforce 开关、权限探测、status dump）的 asm 逻辑记录在本目录
  [README.md](README.md) §6–§11。

### 4.2 产物

```
48-init-capability-20261025/
├── README.md                     # 全过程记录（§1–§22）
├── avc-enforce.txt               # setenforce 被拒的 avc 证据
├── init_status.txt               # init 域 /proc/self/status
├── kmsg2.bin / kmsg_boot.log     # 当前 boot 的 kmsg dump
├── dump_partition.py
├── cleanup_template.S / gen_clean.py
└── partitions/                   # 16 个分区文件 ≈ 65 MB
    ├── vendor_boot_{a,b}.00.bin  dtbo_a.00.bin
    ├── vbmeta_{a,b}.00.bin       vbmeta_system_{a,b}.00.bin
    ├── persist.00..03.bin        modemst{1,2}.00.bin
    ├── fsg.00.bin  fsc.00.bin  devinfo.00.bin  frp.00.bin
    ├── vendor_boot_{a,b}_ramdisk/   # 各 45 个 .ko + fstab
    ├── dtbo_a_entries/              # 22 个 .dtb
    └── persist_tree/                # 318 个文件（传感器标定/Keymaster/coresight）
```

## 5. 边界与教训

- **没有写任何分区**；所有改动都在页缓存（重启即恢复），SELinux 始终 Enforcing；
- 19:43 曾因 init 域 fork 载荷导致设备失联约 15 分钟（`事故记录`（47 号本地事故记录，未入仓））；
  之后所有载荷都改为"无 fork、只读、限时"；
- `/metadata` 只有 11 MiB，chunk 写满会被静默截断（size 文件仍写应读字节数），
  必须先清理；`adb pull` 失败时本地旧文件会被误当新 chunk（已在工具里修掉）；
- 分区设备 0600 root、sysfs `size` 被 SELinux 拒，分区大小只能靠"短 chunk"判断；
- PowerShell 的 `Set-Content/Add-Content` 会写坏中文（U+FFFD 或 GBK 乱码），
  带中文的文件一律用 UTF-8 工具读写。

## 6. 未做/暂缓

| 项 | 原因 |
|---|---|
| `/vendor/lib/modules` 50 个 DLKM 模块 | shell 无读权限，要 root 载荷逐个搬；已记录，需要时再做 |
| `mount tracefs` + kprobe | 依赖 Permissive，已确认不可行 |
| pstore（panic 记录） | 目录空/不可访问，`dmesg` 亦无通道（installd 无 `kmsg_device` 读权限） |
| `super` 动态分区整段 dump | 体积过大，且 system/vendor 已挂载可读 |

## 7. 结论

本专题把"GhostLock 判负之后还能做什么"问到了底：

- **能做的**：installd 域可靠 root 通道、init 域只读代码执行（kmsg / 块设备 / `/metadata`）、
  9 类分区的完整提取与静态分析；
- **不能做的**：运行时 Permissive、tracefs/kprobe、panic 取证；
- **最有价值的两条结论**：AVB 根信任是 AOSP testkey；B 槽 vendor_boot 与运行内核同源。

后续若还有新目标，建议直接复用 `dump_partition.py` + `stub_template.S` 这套管线，
不要再为"观测"去碰 init 域的 fork。


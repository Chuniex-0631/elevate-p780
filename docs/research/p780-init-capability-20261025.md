# init 域能力盘点（2026-10-25）

> **状态：已收尾**。能力边界、SELinux 结论、只读资产清单均已固化，
> 集中版见 [final-report-20261025.md](../../evidence/20261026/init/final-report-20261025.md)；
> 本篇保留全过程记录（§1–§22）。

> 新方向：GhostLock 收尾后，以 **DirtyFrag 页缓存写 + init 域代码执行**为基础做能力建设。
> 本篇只做只读盘点，不改任何系统状态。

## 1. 运行环境的实测数据

`21-dirtyfrag-probe` 的 libc++ `sentry` 钩子、门控 `gettid()==1 && getuid()==0 && getpid()==1`，
把 `/proc/self/status` 拷到 `/metadata/init_status.txt`（见 [init_status.txt](../../evidence/20261026/init/init_status.txt)）：

```
Name:	init
Tgid:	1
Uid:	0	0	0	0
Gid:	0	0	0	0
CapInh:	0000000000000000
CapPrm:	0000003fffffffff
CapEff:	0000003fffffffff      <-- 38 个 capability 全开
CapBnd:	0000003fffffffff
NoNewPrivs:	0
Seccomp:	0                 <-- 没有 seccomp 过滤
```

要点：

- **完整 capability 集**：含 `CAP_SYS_ADMIN`、`CAP_SYSLOG`、`CAP_MAC_ADMIN`、
  `CAP_DAC_OVERRIDE`、`CAP_SYS_RAWIO` 等；
- **无 seccomp**：系统调用不受 App 那套过滤；
- 唯一的约束是 SELinux 的 `init` 域策略。

## 2. SELinux 策略里 init 的权限（静态核对）

从设备自带的 `plat_sepolicy.cil` 直接 grep：

```
(allow init selinuxfs (file (write lock append map open)))
(allow init shell_data_file (dir (read create getattr setattr open search)))
(allow init shell_data_file (file (getattr)))
(allow init system_data_file (file (read getattr)))
(allow init rootfs (dir (mounton)))
```

含义：

| 权限 | 结论 |
|---|---|
| 写 `selinuxfs` 文件 | **允许** → 理论上可以把 `/sys/fs/selinux/enforce` 写成 `0`（进入 Permissive） |
| 读 `system_data_file` | 允许读（`/data/system` 一类） |
| `/data/local/tmp`（`shell_data_file`） | 目录可 create，但**文件只有 getattr**，不能读写已有文件 |
| 挂载点 | 只对 `rootfs` 有 `mounton`，没有对 `debugfs`/`tracefs` 的挂载许可（permissive 下另说） |

## 3. 由此得到的路线

1. **Permissive 开关**：init 载荷写 `enforce=0` → SELinux 进入 Permissive（重启自动恢复 Enforcing，
   不落盘）。Permissive 下：
   - init 载荷可以 `mount("debugfs"/"tracefs", ...)` 拿到 **ftrace/kprobe** 通道，
     这才是真正能替代内核日志的观测手段（可以在 M3 复现时挂 kprobe 看
     `rt_mutex_adjust_prio_chain`/`remove_waiter` 的实际走向）；
   - 现有的 installd root shell 可以 exec `/data/local/tmp` 下的自制二进制，
     把"受限 root"变成"完整 root"（至少到重启为止）。
2. **不碰 SELinux 的只读路线**：init 载荷已经有完整 capability，可以继续 dump 文件、读块设备；
   但受 `init` 域策略限制，写路径很少。

## 4. 风险与回滚

- 写 `enforce=0` 是**运行时状态，不持久**：重启即回到 Enforcing；
- 若 Permissive 期间出现异常，长按电源重启即可；
- 所有操作仍不写任何分区，DirtyFrag 补丁可 `-e probe unpatch` 回滚。

## 5. 下一步（待确认）

在 init 载荷里加"写 enforce=0 → 读回 → 可选恢复"的最小逻辑，
先验证能否真的切到 Permissive；确认后再试 `mount tracefs` + kprobe。

## 6. 2026-10-25 20:28 实测：没切成功

**载荷 v1**（open enforce O_WRONLY → write "0" → 读回 → 记结果）：

- init 门控**命中**（`/dev/p780_enf` 锁存在），说明 init 载荷确实执行了；
- 但 `/metadata/enf_result.txt` 是 **0 字节**，`getenforce` 仍是 `Enforcing`；
- v1 没有记录 open 的错误码，最可能是 `open(O_WRONLY)` 被拒（EACCES），
  也就是静态策略里的那行 `(allow init selinuxfs (file (write ...)))` 没覆盖到实际打开路径。

**载荷 v2**（先把 open 的返回值写出来再判断，锁换成 `enf2`）：

- 连续 6+ 次触发（unpatch/patch、force-stop/start 循环）**一次都没命中门控**，
  `/metadata/enf_result.txt` 一直是旧的 0 字节文件；
- 所以拿不到错误码，无法确认是 SELinux 拒绝还是路径/参数问题。

## 7. 瓶颈：init 触发是竞态的

- 钩子只在 **init 主线程（tid 1）** 调 libc++ `sentry` 时生效；
- 目前唯一用过的触发是 App `patchProbe()` 末尾的孤儿进程回收（init `SIGCHLD` 路径），
  命中率不稳定（19:38–20:22 成功过 3 次，之后 6+ 次全部失败）；
- init 的 `set property` 日志确实在写 kmsg，但那是 property service 线程，`tid != 1`，门控会拒绝。

## 8. 下一步候选

1. 换更可靠的 tid-1 触发：框架重启（`stop`/`start`）、服务 start/stop 事件等；
2. 或者放弃"一次性载荷"，改为**在 init 域里 fork 一个子进程**（已试过，风险高、上次把设备弄挂过）；
3. 或者回到只读能力：init 域已有完整 capability，继续做文件/块设备层面的收集。

现场：libc++ 已回滚（`ROLLBACK COMPLETE`、`0x62fb4` 处 prologue 已恢复原值），
`getenforce` 仍为 `Enforcing`，设备未重启。

## 9. 2026-10-25 20:39 再试：installd 域载荷（触发可靠，但写被拒）

init 门控太难命中，于是改成 **installd 门控**（`uid==0 && cmdline 含 "inst"`），
用 `adb install` 触发——这条触发是可靠的。

实测（载荷把每一步返回值写成 8 字节记录到 `/data/local/tmp/enf2.txt`）：

```
open("/sys/fs/selinux/enforce", O_WRONLY) -> 8        (成功，fd=8)
write(8, "0", 1)                          -> -13      (EACCES)
open(... O_RDONLY)                        -> 8
read(8, buf, 1)                           -> 1
readback byte                             -> '1'      (仍然是 Enforcing)
```

另外实测 installd 的运行环境（`/proc/1287/status`）：

```
Uid: 0
CapEff: 0000003fffffffff     (完整 capability 集，含 CAP_MAC_ADMIN / CAP_SYSLOG)
Seccomp: 0
u:r:installd:s0
selinuxfs on /sys/fs/selinux (rw)
/sys/fs/selinux/enforce  root:root 0644 u:object_r:selinuxfs:s0
```

**结论**：`open` 成功、`write` 返回 `EACCES`。虽然 `plat_sepolicy.cil` 里有
`(allow installd selinuxfs (file (write ...)))`，实际加载的策略仍然拒绝了写——
需要 avc 日志才能确认是哪条规则/哪个类被拒。

## 10. 下一步

1. **取 avc**：init 域是唯一能读 `/dev/kmsg` 的域（策略里 `(allow init kmsg_device (chr_file (read open)))`，
   installd 没有这条），但 init 门控是竞态的；可以多试几次拿到写 enforce 时刻的 kmsg，
   grep `avc` / `enforce`。
2. 或者换写入路径：`selinuxfs` 下还有 `checkreqprot`、`policy` 等文件；
   若写 `policy`（加载自定义策略）也被拒，则说明是更上层的限制。
3. 或者接受：本机 SELinux 策略下，运行时切 Permissive 不可行，permissive/tracefs 路线关闭。

## 11. 2026-10-25 20:42 结论：Permissive 路线关闭（有 avc 证据）

用 init 域的 `/dev/kmsg` dump 拿到了写 enforce 那一刻的审计记录
（[avc-enforce.txt](../../evidence/20261026/init/avc-enforce.txt)）：

```
avc: denied { setenforce } for pid=14510 comm="sh"
  scontext=u:r:installd:s0 tcontext=u:object_r:kernel:s0
  tclass=security permissive=0
```

注意拒绝的不是 `file:write`，而是 **`security:setenforce`**——这是 selinuxfs 写 enforce
时的专用检查。再对设备上四份策略文件做全量搜索：

```
(class security (... setenforce ...))                 仅类定义
(neverallow base_typeattr_182 kernel (security (setenforce)))
(neverallow base_typeattr_179_30_0 kernel_30_0 (security (setenforce)))
(dontaudit kernel self (security (setenforce)))
```

**没有任何 `(allow ... (security (setenforce)))`**。也就是说本机构建上
**没有任何域被允许在运行时切换 SELinux 模式**（连 init 也不例外）。

由此：

| 路线 | 结论 |
|---|---|
| installd 载荷写 `enforce=0` | ❌ `security:setenforce` 被拒（EACCES） |
| init 载荷写 `enforce=0` | ❌ 同一检查；且 init 门控本身是竞态的 |
| Permissive → `mount tracefs` → kprobe | ❌ 随 Permissive 一起关闭 |
| 加载自定义 policy | ❌ `security:load_policy` 同样没有 allow |

剩下的可用能力就回到"只读"：init 域读 `/dev/kmsg`（一次性）、写 `/metadata`、
读块设备；installd 域 root shell（uid 0、完整 capability、无 seccomp，但被 SELinux 域限制）。

现场：libc++ 已回滚（`ROLLBACK COMPLETE`），`getenforce=Enforcing`，设备 uptime 连续。

## 12. 只读榨取：分区镜像（2026-10-25 20:50）

### 12.1 先解决 /metadata 满的问题

`/metadata` 只有 11 MiB，之前的内核 dump 残留把 82 个普通文件堆到 100% 满，
8 MiB 的 chunk 写到 225,280 字节就 ENOSPC（而 size 文件仍记 8 MiB）。
写了一个"清理载荷"（init 门控，逐个 `unlink` 那 82 个残留）跑一次后：

```
/dev/block/sda14  11M  180K  11M  2%  /metadata
```

### 12.2 vendor_boot（a/b 两个槽）

用 `dump_partition.py`（本目录，按 chunk 渲染 `25-kernel-dump` 的模板、patch、触发、pull、回滚）
把两个槽都拉下来了：

| 槽 | 镜像大小 | vendor ramdisk | dtb | 解包后 |
|---|---|---|---|---|
| `vendor_boot_a` | 8 MiB chunk（镜像 ~704 KB） | 700,501 B | 256 B | 51 个文件，3,175,168 B |
| `vendor_boot_b` | 同上 | 700,473 B | 256 B | 51 个文件，3,175,168 B |

ramdisk 内容（cpio.gz）：

- `first_stage_ramdisk/fstab.default`、`fstab.emmc`；
- `lib/modules/5.4-gki/` 下 **45 个 .ko**（`_qcom_scm.ko`、`clk-qcom.ko`、`qcom-arm-smmu-mod.ko`、
  `ufs-qcom.ko`、`sdhci-msm.ko` 等），外加 `modules.alias/.dep/.load/.softdep`。

**关键发现（vermagic）**：

| 槽 | `_qcom_scm.ko` 的 vermagic |
|---|---|
| `vendor_boot_a` | `5.4.233-g2570b53dcf94-dirty` |
| `vendor_boot_b` | `5.4.233-gea5245e94afe-dirty` |

跑着的内核是 `5.4.233-qgki-gea5245e94afe-dirty` —— **B 槽的 vendor_boot 与运行内核同源**
（`gea5245e94afe`），A 槽是另一套构建（`g2570b53dcf94`）。这解释了之前"B 槽是活动槽"的推断，
也给 `CONFIG_MODVERSIONS=y` 下"自建模块"的不可行性再添一条：没有匹配的 `Module.symvers`。

### 12.3 dtbo（a 槽）

`dtbo_a` 头：`magic=0xd7b7ab1e`、`total_size=3,296,351`、22 个 entry、page=4096。
已把 22 个 overlay 全部拆出来（`dtbo_a_entries/`），可见的板级信息包括：

- `qcom,blair` / `qcom,holi`、`qcom,board-id`、`qcom,msm-id`（平台与板型）；
- 电池模型 `qcom,ATL436186_020H_3780mAh`、`qcom,ATL466271_3300mAh`；
- 相机 `qcom,actuator0/1`、`qcom,adc-tm5/7` 等外设节点。

### 12.4 产物

```
48-init-capability-20261025/
├── dump_partition.py              # 通用分区 chunk 拉取器
├── cleanup_template.S / gen_clean.py
└── partitions/
    ├── vendor_boot_a.00.bin       # 8 MiB（镜像在前 ~704 KB）
    ├── vendor_boot_b.00.bin
    ├── dtbo_a.00.bin              # 8 MiB（镜像 3.3 MB）
    ├── vendor_boot_a_ramdisk/     # 45 个 .ko + fstab
    ├── vendor_boot_b_ramdisk/
    └── dtbo_a_entries/            # 22 个 .dtb
```

### 12.5 踩过的坑

- `/metadata` 满时 chunk 会被截断，但 stub 的 size 文件仍写"应读字节数"，容易误判为分区很小；
- `adb pull` 失败时本地旧文件仍在，脚本会误把旧文件当新 chunk（已修：pull 前先删本地文件）；
- 分区设备是 0600 root，shell 读不了；sysfs 的 `size` 也 SELinux 拒绝，所以"分区大小"只能靠短 chunk 判断。

## 13. vbmeta（a/b 与 system a/b）：AVB 链用的是 AOSP 测试密钥

四个 vbmeta 分区都拉下来了（各 64 KiB）：

| 分区 | 算法 | rollback_index | 公钥 |
|---|---|---|---|
| `vbmeta_a` | SHA256_RSA4096 | 0 | 4096-bit，位于 offset 3768 |
| `vbmeta_b` | SHA256_RSA4096 | 0 | 与 a 相同 |
| `vbmeta_system_a` | SHA256_RSA2048 | 1701388800（2023-12-01） | 2048-bit |
| `vbmeta_system_b` | SHA256_RSA2048 | 1706745600（2024-02-01） | 与 system_a 相同 |

**关键发现**：`vbmeta_a` / `vbmeta_b` 的 RSA4096 公钥模数与
[`09/testkey_rsa4096.pem`](../../evidence/20261026/keys/testkey_rsa4096.pem) **逐位相同**：

```python
int.from_bytes(vbmeta_a_key_modulus) == int.from_bytes(aosp_testkey_modulus)  # True
```

也就是说，这台零售机的 **AVB 根信任链用的是 AOSP 测试密钥**（至少在 vbmeta 这一层）。

含义：

- **AVB 校验本身不再是障碍**：任何用 testkey 签名的 image 都能通过 vbmeta 校验；
- **真正的障碍仍是 bootloader 锁定**：`fastboot flashing unlock` 返回 `unknown command`（见 09 号专题），
  没有解锁就没有写分区的通道；
- 如果将来出现任意分区写通道（EDL/漏洞），"签名"这关已经天然通过——不需要再折腾 AVB 绕过。

`vbmeta_system` 用的是 2048-bit key、两个槽一致；本仓库没有对应的 PEM，暂不能确认它是否也是
AOSP 的 `testkey_rsa2048.pem`，但"两槽同钥 + 测试构建特征"已经很明显。

## 14. modemst1 / modemst2

两个分区各 3,145,728 字节，整段拉下（短 chunk = 已到分区尾）：

```
modemst1  first16: 10 00 00 00 03 00 00 00 d8 01 00 00 90 45 1b c9
modemst2  first16: 11 00 00 00 03 00 00 00 d8 01 00 00 00 02 d8 9f
```

首部有结构化头（0x10/0x11 + version 3 + ...），前 1 MiB 非零字节约 1.04 M，属于
modem NV/标定数据，对 exploit 路线价值有限，仅作存档。

## 15. 当前产物总表

```
48-init-capability-20261025/partitions/
├── vendor_boot_a.00.bin   8 MiB   (镜像 ~704 KB)
├── vendor_boot_b.00.bin           (vermagic 与运行内核同源)
├── dtbo_a.00.bin          8 MiB   (22 overlays)
├── vbmeta_a.00.bin        64 KiB
├── vbmeta_b.00.bin        64 KiB
├── vbmeta_system_a.00.bin 64 KiB
├── vbmeta_system_b.00.bin 64 KiB
├── modemst1.00.bin        3 MiB
├── modemst2.00.bin        3 MiB
├── vendor_boot_a_ramdisk/        45 个 .ko + fstab
├── vendor_boot_b_ramdisk/
└── dtbo_a_entries/               22 个 .dtb
```

## 16. persist（32 MiB，ext4）

`persist` 正好 32 MiB（chunk 4 读到 0 字节即分区尾），4 个 chunk 全拉下，
离线解析 ext4 后整棵树导出到 `partitions/persist_tree/`（318 个文件、约 948 KB）：

| 目录 | 文件数 | 内容 |
|---|---|---|
| `sensors/` | 278 | 传感器 registry 与标定：`icm4x6xa`（陀螺/加速度）、`tmd2725`（ALS/接近）、`icp101xx`（气压/温度）、`bu52053nvx`（霍尔）等 |
| `data/` | 14 | Keymaster/Keystore 存储（`store_0..4` 各 120 KB + 随机名 blob），TEE 加密，不可直接使用 |
| `coresight/` | 3 | `qdss.agent.sh` / `qdss.config.sh` / `qdss.functions.sh` |
| `misc/`、`time/`、`rfs/` | 20 | 杂项与时间偏移 |
| 根目录 | 2 | `aw_cali.bin`（10 B）、`p780_p`（8 B） |

价值判断：主要是**硬件清单与标定**（确认了具体传感器型号），对 exploit 路线没有直接帮助；
Keymaster 数据在 TEE 之外不可解，也不构成新的攻击面。

## 17. 下一批候选

- `fsg` / `fsc`（modem 文件系统，通常几 MB）；
- `devinfo`（很小，含设备状态位，可能对解锁判断有用）；
- `/vendor/lib/modules` 的 50 个 DLKM 模块（shell 读不了，要 root 载荷逐个搬，成本高）。

## 18. devinfo：4 KiB，全零

`devinfo` 分区只有 4096 字节，整段读回后 **4096 字节全为 0x00**：

```
size=4096  nonzero bytes=0
contains "ANDROID-BOOT!": False
```

解读：

- 没有 Qualcomm 常见的 `ANDROID-BOOT!` 头，也没有 `is_unlocked` / `is_tampered` 等标志位；
- 全零等价于"未解锁、未篡改、无额外状态"，与当前 Bootloader 锁定的现状一致；
- 但它**不能回答"BL 是否支持 unlock"**——这里只是状态存储，能力在 ABL 的命令表里
  （此前 `fastboot flashing unlock` 返回 `unknown command` 才是那个证据）。

记录完毕，没有新攻击面。

## 19. fsg / fsc：modem 文件系统的"黄金副本"与空缓存

| 分区 | 大小 | 内容 |
|---|---|---|
| `fsg` | 3,145,728 B（3 MiB） | 有签名头：`14 00 00 00 03 00 00 00 d8 01 00 00 … IMGEFS- SIGNED_IMAGE`，前 1 MiB 非零约 407 KB |
| `fsc` | 131,072 B（128 KiB） | **全零** |

解读：`fsg` 是 modem EFS 的黄金副本（Qualcomm signed image 格式，`IMGEFS`），
`fsc` 是它在升级时的缓存/回滚区，当前为空——与设备状态健康一致。
两者都是 modem NV 数据，对 exploit 路线没有直接帮助，归档备查。

## 20. frp：512 KiB，只有开头 114 字节非零

```
size=524288  nonzero=114
head: a6 d6 1c 95 19 53 17 93 f7 7d 89 b6 1c 4c 1f 49 … 00 00 00 4d 0a 4b 08 a5 4f 10 20 …
```

- 前 39 字节是随机外观的摘要/密钥材料，之后 `00 00 00` 接一段 protobuf 风格的小消息
  （`4d 0a 4b 08 …`）；
- 全分区没有明文 `FRP` / `LOCK` 字样，也没有可读状态位；
- 说明 FRP 凭据区基本为空（没有绑定 Google 账号的恢复锁数据），对 exploit 无价值。

## 21. 暂缓项：/vendor/lib/modules 的 DLKM 模块

`/vendor/lib/modules` 下有约 50 个 DLKM（`camera.ko`、`gf_fp.ko`、`aw882xx_dlkm.ko`、
`bolero_cdc_dlkm.ko` 等），shell 无读权限、需要 root 载荷逐个搬运，成本高、当前收益不明，
**记录为后续可选任务**（写一个"一次搬一个文件"的通用载荷即可按需取用）。

## 22. 只读榨取总清单（2026-10-25）

| 分区 | 大小 | 结论 |
|---|---|---|
| boot_b → kernel Image | 41,767,424 B | 已提取并恢复 173,205 符号（25/27 号专题） |
| vendor_boot_a / _b | 各 ~704 KB 镜像（8 MiB chunk） | 45 个 first-stage .ko + fstab；B 槽 vermagic 与运行内核同源 |
| dtbo_a | 3,296,351 B（22 entries） | 板型/电池/相机/ADC 配置 |
| vbmeta_a / _b / system_a / _b | 各 64 KiB | **RSA4096 公钥 = AOSP testkey**；system 为 RSA2048、两槽同钥 |
| persist | 32 MiB（ext4） | 278 个传感器标定 + Keymaster store + coresight 脚本 |
| modemst1 / modemst2 | 各 3 MiB | modem NV 数据 |
| fsg / fsc | 3 MiB / 128 KiB | EFS 黄金副本（IMGEFS 签名）/ 空缓存 |
| devinfo | 4 KiB | 全零（未解锁、未篡改） |
| frp | 512 KiB | 仅开头 114 字节非零，无明文状态 |





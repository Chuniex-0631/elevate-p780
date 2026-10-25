# 阶段收尾：GhostLock 判负、域能力边界、只读榨取与解锁线关闭（2026-10-25）

> 本页是 2026-10-25 阶段的收尾说明，汇总四件事：GhostLock（CVE-2026-43499）判负、
> init/installd 域能力边界、9 类分区的只读榨取、OEM Unlock 终结性判定，以及一次全量
> 密钥/信息扫描。所有结论都附本仓库内可复核的证据路径。

## 1. 结论摘要

| 方向 | 结论 | 证据 |
|---|---|---|
| GhostLock / CVE-2026-43499 | **判负**：M1（PI 链建立）、M2（过期 waiter 场景）实机成立；M3（利用窗口内观测/改写）在 6 秒窗口内无可用手段，9 种尝试全部无效 | 本机 `47-ghostlock-20261025/ghostlock-final-report-20261025.md`、`M1.md`/`M2.md`/`M3.md` |
| 内核镜像与符号 | **已恢复**：`boot_b` 提取 arm64 `Image`（41,767,424 B，SHA-256 `6df574af…4f373`），`vmlinux-to-elf` + 独立校验恢复 **173,205** 个符号；修正旧偏移表"整体错位一个符号"的问题 | `25-kernel-dump-20261025/`、`27-symbol-recovery-20261025/` |
| init 域代码执行 | **成立**：`gettid==1` 门控 + `libc++ sentry` trampoline；完整 CapEff、Seccomp=0；可读 `/dev/kmsg`、写 `/metadata`、读块设备 | `48-init-capability-20261025/README.md` §1、`init_status.txt` |
| installd 域代码执行 | **成立且触发可靠**：`uid==0 && cmdline 含 "inst"`，`adb install` 即可触发；CapEff 全开、Seccomp=0 | 同上 §1.1 |
| 运行时 Permissive | **不可行**：写 `/sys/fs/selinux/enforce` 的 `write` 返回 `EACCES`；avc 显示是 `security:setenforce` 被拒；四份策略文件均无任何 `(allow … (security (setenforce)))` | `48-init-capability-20261025/avc-enforce.txt`、README §9–11 |
| 只读榨取 | **完成**：9 类分区/镜像已提取（kernel、vendor_boot×2、dtbo、vbmeta×4、persist、modemst×2、fsg/fsc、devinfo、frp） | 本页 §4、`48-init-capability-20261025/partitions/` |
| OEM Unlock | **关闭**：`oem device-info` 可执行但 `flashing unlock`/`oem unlock`/`get_unlock_ability` 全部 `unknown command`；`ro.oem_unlock_supported=1` 只是 vendor 属性 | `50-oem-unlock-final-20261025/` |
| 密钥/信息扫描 | **1 处需处置**：工作区根目录的 GitHub PAT（`gh-token`，`github_pat_…`）应轮换；`09/testkey_rsa4096.pem` 是 AOSP 测试 AVB 私钥，与 `vbmeta_a` 公钥逐位相同；无其它私钥/keystore | `49-artifact-scan-20261025/README.md`、`scan.json` |

## 2. GhostLock：为什么判负

- **M1（PI 链）**：3 线程跨锁 PI 链建立成功，`/proc/<tid>/stat` 的 prio 字段可读，链几何与预期一致；
- **M2（过期 waiter）**：`FUTEX_CMP_REQUEUE_PI` → `EDEADLK` → `rt_mutex_start_proxy_lock` →
  `remove_waiter(M, waiter_p)`，`current=main`、`waiter->task=p`，bug 形态在实机命中；
- **M3（利用）**：卡在同一个门——`remove_waiter` 只读一次 `waiter->lock`（8 字节），
  之后任何新的 N 等待者都会把 p 的有效优先级重新抬到 120，使 `rt_mutex_waiter_equal` 门通过；
  而移除 q 的等待者会立刻唤醒 p（EAGAIN/ETIMEDOUT），6 秒窗口随之关闭。
  9 种尝试（poke / deboost / r-block / poll spray / hold / keep×3）均未在窗口内制造出
  "stale prio ≠ p 有效优先级" 的组合。

结论：**在本机（SELinux Enforcing、无 RT 权限、`/proc/<tid>/stack` 不可读）上，GhostLock 不具备
可观测、可利用的路径**。论文级原语成立，但不是本机的提权通道。

## 3. 域能力边界

### 3.1 能做的

| 域 | 触发 | 能力 |
|---|---|---|
| init | 孤儿进程回收（竞态，时灵时不灵） | 完整 capability；读 `/dev/kmsg`（唯一通道）；写 `/metadata`；读块设备 |
| installd | `adb install`（可靠） | 完整 capability、Seccomp=0、`u:r:installd:s0`；可读写 `/data`；**不能 exec** `/data/local/tmp`、不能写 selinuxfs |

### 3.2 不能做的

- **运行时切 Permissive**：`security:setenforce` 无任何 allow（avc 已抓，见 `avc-enforce.txt`）；
  因此 `mount tracefs`、kprobe 观测一并关闭；
- **加载自定义 policy**：`security:load_policy` 同样无 allow；
- **pstore**：目录为空/不可访问；installd 也没有 `kmsg_device` 读权限，kmsg 只能走 init。

## 4. 只读榨取清单

| 分区 | 大小 | 结论 |
|---|---|---|
| `boot_b` → kernel `Image` | 41,767,424 B | 173,205 符号已恢复 |
| `vendor_boot_a` / `_b` | 各 ~704 KB 镜像 | 45 个 first-stage `.ko` + `fstab`；**B 槽 vermagic `5.4.233-gea5245e94afe-dirty` 与运行内核同源**，A 槽是另一套构建（`g2570b53dcf94`） |
| `dtbo_a` | 3,296,351 B / 22 entries | 平台 `blair`/`holi`、电池 `ATL436186_020H_3780mAh`、相机 actuator、ADC |
| `vbmeta_a/b`、`vbmeta_system_a/b` | 各 64 KiB | **RSA4096 公钥与 AOSP `testkey_rsa4096.pem` 逐位相同**；system 为 RSA2048、两槽同钥 |
| `persist` | 32 MiB ext4 | 278 个传感器标定（`icm4x6xa`/`tmd2725`/`icp101xx`/`bu52053nvx`）、Keymaster store（TEE 加密）、coresight 脚本 |
| `modemst1/2` | 各 3 MiB | modem NV 数据 |
| `fsg` / `fsc` | 3 MiB / 128 KiB | EFS 黄金副本（`IMGEFS` 签名）/ 空缓存 |
| `devinfo` | 4 KiB | 全零（未解锁、未篡改） |
| `frp` | 512 KiB | 仅开头 114 字节非零，无明文状态 |

两个值得记住的结论：

1. **AVB 根信任是 AOSP 测试密钥**——签名层面不设防；真正的门槛是"没有写分区的通道"；
2. **B 槽 vendor_boot 与运行内核同源**——A 槽是另一套构建，符合"当前从 B 槽启动"的观测。

## 5. OEM Unlock 终结

```
getvar unlocked   -> no
getvar secure     -> yes
oem device-info   -> Device unlocked: false / critical unlocked: false / Verity mode: false
```

`flashing unlock`、`flashing unlock_critical`、`flashing get_unlock_ability`、
`oem unlock`、`oem unlock-go`、`oem enable-unlock`、`oem get_unlock_ability`
**全部 `unknown command`**；而 `oem device-info` 可执行——说明 ABL 命令表里没有解锁命令，
不是权限/状态问题。`ro.oem_unlock_supported=1` 只是 vendor 配置属性，与 ABL 能力不符。

结合 10 号专题的 Journey gate 静态结论，**OEM Unlock 线正式关闭**（常规 fastboot 路径）。

## 6. 密钥与信息扫描

- **需要处置**：工作区根目录 `gh-token` 是真实的 GitHub fine-grained PAT（`github_pat_…`），
  若曾随仓库/备份外传，应立刻轮换；
- **AVB 测试私钥**：`09/testkey_rsa4096.pem`（4096-bit `RSA PRIVATE KEY`），模数与
  `vbmeta_a` 公钥逐位相同——它是 AOSP 公开测试密钥，不算泄露，但说明本机 AVB 根信任是公开私钥；
- **OTA 证书**：`01/otacerts.zip` 内 `releasekey.x509.pem` 为 TINNO 自签（CN=TINNO、2015–2042），
  仓库里只有公钥证书；
- 未发现 AWS key、`ghp_` token、Slack token、SSH 私钥、`.pk8`/`.p12`/`.jks` 私钥库；
- Google API key（`AIza…`）出现在少数 APK/ROM 包中，属客户端公开 key；
- 隐私：设备序列号出现在 3 个文本文件，kmsg/dumpsys 含 MAC 与包列表；公开仓库前应脱敏。

## 7. 边界与教训

1. **不写任何分区**；所有代码执行都在页缓存，重启即还原，SELinux 始终 Enforcing；
2. 19:43 的 init 域 fork 载荷曾导致设备失联约 15 分钟；之后所有载荷改为"无 fork、只读、限时"；
3. `/metadata` 只有 11 MiB，chunk 写满会被静默截断（size 文件仍写应读字节数），必须先清理；
4. `adb pull` 失败时本地旧文件会被误当新 chunk（工具已修）；
5. 带中文的文件一律用 UTF-8 读写（PowerShell 默认编码会写坏）。

## 8. 产物索引（本地工作区）

| 目录 | 内容 |
|---|---|
| `47-ghostlock-20261025/` | GhostLock 全流程（M1/M2/M3、收尾报告、探针源码） |
| `48-init-capability-20261025/` | 能力盘点、SELinux 结论、分区提取与工具（`dump_partition.py`） |
| `49-artifact-scan-20261025/` | 密钥/信息扫描脚本与结果 |
| `50-oem-unlock-final-20261025/` | OEM Unlock 终结判定与 `getvar all` |
| `25/27-*` | 内核镜像提取与符号恢复 |

大体积二进制（分区镜像、`.ko`、`.dtb`、ext4 解包）只在本地保存，仓库仅记录路径与哈希；
`evidence/partitions/manifest-20261025.json` 给出每个产物的字节数与 SHA-256。

## 9. 新的突破点候选（下一阶段）

| 候选 | 为什么值得试 | 主要障碍 |
|---|---|---|
| **OTA / 供应链** | OTA 证书是 TINNO 自签、`otacerts` 只有公钥；若能拿到厂商 OTA 包，可分析 update_engine 的验证与回滚逻辑 | 拿不到签名包/服务器地址 |
| **EDL / Firehose** | Sahara v2 已通，若找到匹配签名的 programmer，可整片读写 | programmer 与签名 |
| **installd 域更深利用** | 完整 capability + 无 seccomp，但受 SELinux 限制；可枚举 `(allow installd …)` 中尚未利用的宽权限（如 `relabelfrom`、`setattr`） | 域策略收得很紧 |
| **内核 5.4.233 其它 CVE** | 已有 Image + 173k 符号，能精确定位任何 5.4 内核漏洞 | 需要可达的触发路径（DirtyFrag 仍是唯一确认的写原语） |
| **ABL 镜像分析** | 若能从 OTA/固件包拿到 `abl_a/b`，可枚举私有 fastboot 命令 | 无镜像来源 |
| **供应商预置服务** | `persist`/`vendor` 里的 TINNO 服务、`QAS_DVC_MSP`、`Journey` 等可能有本地接口 | 需要逐项审计 |

> 不再重复：DSU/GSI 启动、OEM Unlock 的 fastboot 入口、AVB 密钥身份核验、运行时 Permissive。

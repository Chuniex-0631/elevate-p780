# 实机硬件、系统、Bootloader、Fastboot、EDL 档案

## 真实设备快照

来源：2026-06-12 EDL/fastboot 实验记录、2026-10-03 至 10-10 ADB 采集记录、`hand5g_kernel.txt`、`hand5g_fastboot_all.txt` 和已保存 `p780-config.gz`。型号 **Rakuten Hand 5G P780**、制造商 **TINNO**、设备/产品/主板标识 `P780/p780`；`ro.board.platform=holi`；EDL 报告 CPU `mannar`（不同命名层级，不应自行认定是芯片矛盾）。

| 字段 | 实测值 |
|---|---|
| Android | 11 |
| `ro.build.fingerprint` | `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys` |
| 内部固件 | `P780AE_11.0_RMN_JP_162_CFC` |
| 公开/自定义固件 | `P780AE_11.0_RMN_JP_162` |
| Android 版本增量 | `264` |
| Android / Vendor 安全补丁 | `2024-02-01` |
| 系统构建时间 | 2024-02-20 16:26:18 CST |
| 内核编译时间 | 2024-02-20 18:01:03 CST |
| 内核 | `5.4.233-qgki-gea5245e94afe-dirty` |
| 架构 | ARM64 / aarch64 |
| 原厂编译器 | Android Clang 11.0.2 (`r383902b1`), LLD 11.0.2 |
| 本研究旧日志槽位 | `_b`（时间点快照，不代表现在仍为 B 槽） |

## Fastboot / AVB

- 开发者选项中 **OEM unlocking 有入口但灰色不可操作**。
- Android 属性曾显示 `ro.oem_unlock_supported=1`，`sys.oem_unlock_allowed=0`。这不代表实际可解锁。
- Fastboot `unlocked:no`，`Device unlocked: false`，`Device critical unlocked: false`，`Verity mode: true`；早期记录另有 AVB green。
- `fastboot flashing get_unlock_ability` → `FAILED (remote: 'unknown command')`
- `fastboot flashing unlock` → `FAILED (remote: 'unknown command')`
- `fastboot oem unlock` → `FAILED (remote: 'unknown command')`
- `fastboot oem edl` → `FAILED (remote: 'unknown command')`
- **未知命令不是“设备永久不可解锁”的证明**；仅记录当前 Fastboot 接口的响应。

## 分区布局（只读发现）

- `fastboot getvar all` 和 `/dev/block/by-name` 体现 A/B 结构：`boot_a/boot_b`、`vendor_boot_*`、`vbmeta_*`、`abl_*`、`dtbo_*`、`tz_*`、`modem_*`、`xbl_*` 等。
- `userdata` 显示 `f2fs`；`metadata` 为 `ext4`；UFS 设备分区映射见 `archive/device/hand5g_byname.txt`。
- `boot_a` 和 `boot_b` 的 fastboot 报告分区上限约 96 MiB：这是分区容量，**不是已读取的 boot.img 文件大小**。
- 从未用这些分区名直接尝试写入，亦没有成功的官方 `boot.img` 提取记录。

## 2026-06-12 EDL / Sahara

由物理设备识别的 Qualcomm EDL USB VID:PID 为 **05C6:9008**；Sahara v2，设备模式 Sahara，CPU 显示 `mannar`：

- `HWID: 0x0016f0e100000780`
- `MSM_ID: 0x0016f0e1`；`OEM_ID: 0x0000`；`MODEL_ID: 0x0780`
- 记录存在设备独有 EDL serial，本公开式摘要已移除；**原始序列号不放入代码库**。
- `PK_HASH` 为 EDL 针对 OEM 验证公钥哈希的识别值，不是可以拿来签名的私钥；完整匹配信息保留在历史私有原文件库，仓库正文不包含设备独有序列号。
- 工具提示需 `[FHPRG/ENPRG].bin` 匹配 Firehose loader；**未证实 Loader 可用、亦无 Firehose 读写成功**。

## 设备完整性原则

不在缺少可还原官方镜像时进行 EDL GPT / ABL / XBL / VBMeta / RPMB / Keymaster 写入；不把三星 A52s 内核当 P780 的刷机文件。当前目标是保存已证实的数据，尚未获得 root 或解锁。

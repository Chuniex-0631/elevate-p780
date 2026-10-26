# otacerts 页写 App（源码）

用途：在 App 进程里用 Elevate 的 `writeBlock()` 原语，把 `otacerts_ours.zip`
（1135 B）写到 `/system/etc/security/otacerts.zip` 的 page cache，然后由
system_app 触发 update_engine 验证签名。**只写证书页，不写 boot/vbmeta。**

## 依赖

- `libsendfile_probe.so`：从 `release/Elevate-1.0.apk` 的
  `lib/arm64-v8a/` 提取（JNI 符号固定在 `top.dcmqht.p780ipsec.MainActivity`）。
- Android build-tools（aapt2/d8/zipalign/apksigner）与 platform android.jar。
- 本目录的 `MainActivity.java` 与 `AndroidManifest.xml`。

## 构建（ASCII 路径，避免 aapt2 处理中文路径失败）

```powershell
javac -source 8 -target 8 -bootclasspath android.jar -d classes src/MainActivity.java
java -cp d8.jar com.android.tools.r8.D8 --lib android.jar --output dex (all .class)
aapt2 link -o base.apk -I android.jar --manifest AndroidManifest.xml -A assets ^
  --min-sdk-version 30 --target-sdk-version 30
# 把 classes.dex、lib/arm64-v8a/libsendfile_probe.so 加进 base.apk
zipalign -f 4 base.apk aligned.apk
apksigner sign --ks debug.keystore --out signed.apk aligned.apk
```

## 注意

- 包名必须是 `top.dcmqht.p780ipsec`（JNI 符号名固定）；安装前需要先卸载原 Elevate，
  或对 `.so` 做同长度包名替换（会破坏 ELF 符号哈希，不可用）。
- App 读取 `assets/otacerts_ours.zip`，逐 16 字节调用 `runSysWriteProbe`；
  共 71 个块（最后一块 offset 1119 覆盖尾部 15 字节）。
- **page cache 可能被回收**：写完要立刻触发 update_engine；否则会回落到原始证书。
- 写入后重启设备即可恢复原始 `otacerts.zip`（page cache 不会落盘）。

## 实测（2026-10-27）

- App 日志：`after len=1135 match=true`、`done blocks=71`；
- update_engine 日志：`Verified correct signature 1 out of 1 signatures.`、
  `Metadata hash signature matches value in Omaha response.` —— 签名门已绕过；
- 之后 `kPayloadTimestampError`（已通过 manifest `max_timestamp` 修复），
  空分区 manifest 会在 `DeltaPerformer::Write` 触发 SIGSEGV；下一步需要
  带 partition/operation 的合法 payload。

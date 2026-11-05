# 2026-11-05 设备实测工具说明

本目录不包含可执行二进制，只记录本轮使用的构建/注入方法与关键常量。设备是
Rakuten Hand 5G / TINNO P780，ADB 序列号 `b940328a`，实验已停止。

## 1. 通用页写 App

包名保持 `top.dcmqht.p780ipsec`，复用 `release/Elevate-1.0.apk` 里的
`lib/arm64-v8a/libsendfile_probe.so`。最小 `MainActivity` 接受：

```
--es path <文件绝对路径>
--ei offset <十进制或 0x 偏移>
--es hex <要写入的字节>
--ei spawn 1        # 可选：写完调用 native spawnOrphan() 触发 init 域
```

`writeBlock()` 与 Elevate 的 `PatchData` 相同：读 16 B 原块、AES-ECB 反解 IV、
构造 ESP 头/ICV，调用 `runSysWriteProbe`。最后一块不足 16 B 时按文件长度截断读回。

构建方式：`javac -bootclasspath android.jar` + `d8`，替换原 APK 的 `classes.dex`，
用 `uber-apk-signer` 重签；`AndroidManifest` 里的 `ApkProvider` 与 `InstallReceiver`
也必须一起编译，否则启动即 `ClassNotFoundException`。

## 2. init 域 stub 注入

`/system/lib64/libc++.so`：

| 项 | 值 |
|---|---|
| stub 写入偏移 | `0x790b0`（`money_get` 函数头，长 4752 B） |
| sentry 改写偏移 | `0x62fb4`（16 B） |
| sentry 入口字节 | `b0 00 00 f0 10 c2 02 91 00 02 1f d6 1f 20 03 d5` |
| sentry 原 prologue | `fd 7b be a9 f3 0b 00 f9 fd 03 00 91 1f 00 00 39` |

stub 末尾必须重放原 prologue，再跳到 `0x62fc4`。写完后调用 `spawnOrphan()`
触发 init 主线程；stub 通过 `/metadata` 回传 fd/errno。

## 3. OTA 证书页与 payload

- `/system/etc/security/otacerts.zip` 页缓存替换为自建 RSA-2048 证书 zip（1135 B）；
- update_engine 每次 apply 重新读证书，替换后同一 payload 通过
  `Verified correct signature`；
- payload：`CrAU` + 大端 version u64 + 大端 manifest_size u64 +
  大端 metadata_signature_size u32；metadata 与 payload 分别用 PKCS#1 v1.5 SHA-256 签名；
- 本轮 A 槽 payload 为 `boot`（51,408,896 B）、`vendor_boot`（1,359,872 B）、
  `vbmeta`（65,536 B）三个 REPLACE operation，数据区偏移相对 data section 起点。

## 4. A 槽 vbmeta 构造

- 读取原厂 `vbmeta_a` 的 header/descriptors；
- 只替换 `boot`、`vendor_boot` 两个 hash descriptor 的 `image_size/salt/digest`
  （值来自 `vbmeta_b`）；
- `dtbo/system/vendor` hashtree 描述符与 `vbmeta_system` 链描述符保持不变；
- header 的 auth/aux 尺寸、public key、CRC 不变，用 `testkey_rsa4096` 对
  `header + aux` 做 RSA-4096/PKCS#1 v1.5 SHA-256 重签；
- 校验：`avbtool info_image` 显示 boot digest `474ed170…`、vendor_boot `9a0e8906…`。

## 5. 关键偏移

| 对象 | 偏移 |
|---|---|
| GPT header（`/dev/block/sde`，4K 扇区） | 0x1000 |
| GPT entries | 0x2000 |
| `boot_a` entry / attributes | 0x2400 / 0x2430 |
| `boot_b` entry / attributes | 0x2d80 / 0x2db0 |
| header entries CRC / header CRC | 0x1058 / 0x1010 |
| misc `bootloader_control` | 0x0（32 B，CRC 在 0x1c） |

## 6. 风险

- 写 GPT 只能由 `hal_bootctl` 域完成；init 打开 `/dev/block/sde` 返回 EACCES；
- 全局 libc++ `_Znwm` hook 的带栈/syscall 变体均导致整机重启；
- 不要在没有备份 GPT/主备头的情况下写 GPT。

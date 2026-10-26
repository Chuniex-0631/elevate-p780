# 全量系统文件扫描：密钥、凭据与有用信息（2026-10-25）

> 扫描范围：仓库里所有"从设备搞出来"的系统文件与提取产物（排除 SDK/toolchain/大压缩包）。
> 工具：[`scan_secrets.py`](../../tools/artifact-scan/scan_secrets.py)；原始结果：[scan.json](../../evidence/20261026/artifact-scan/scan.json)。
> 共扫 **3,612** 个文件，命中 1,623 个（大多是二进制里的普通字符串），
> 真正需要关注的内容如下。

## 1. 凭据与密钥

| 项 | 位置 | 性质 | 建议 |
|---|---|---|---|
| **GitHub fine-grained PAT** | 仓库根目录 `gh-token`（93 B，`github_pat_…`） | **真实凭据**（脚本用它调 GitHub API） | 轮换，并移出工作区/加 ignore |
| **AVB 测试私钥** | `09/testkey_rsa4096.pem` | `RSA PRIVATE KEY`，4096-bit；模数与 `vbmeta_a` 公钥**逐位相同** | AOSP 公开测试密钥，不算泄露；但它意味着本机 AVB 根信任是"公开私钥" |
| OTA 证书 | `01/otacerts.zip`、`14-supplement-20261024/otacerts.zip` 内 `releasekey.x509.pem` | TINNO 自签（CN=TINNO、TINNO@tinno.com、2015–2042），**只有公钥证书** | 无私钥，风险低 |
| APK 内证书/keystore | GoogleRestore 的 `google.jks`、Thales LPA 的 GSMA 证书 | 公开证书/测试证书 | 无 |
| Google API key（`AIza…`） | `GoogleRestore.apk`、`Turbo.apk`、`ApeCamera2_R_P780.apk`、`P780-ROM-20261025/product.tar*` | 客户端 API key（设计上公开） | 注意配额滥用即可 |

未发现：AWS key、GitHub `ghp_` 类 token、Slack token、SSH 私钥、`.pk8`、`.p12`、`.jks` 私钥库。

补充：全仓库（排除 SDK/toolchain）只有 **1 个** `.pem` 文件，就是那把 AVB 测试私钥。

## 2. 设备与构建信息（比密钥更有用）

从 `03/hand5g_debloat_audit/01_getprop_full.txt` 提取：

| 属性 | 值 |
|---|---|
| `ro.build.fingerprint` | `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys` |
| `ro.build.date` / host / user | `2024-02-20` / `HTSVR18` / `android` |
| `ro.build.version.security_patch` | `2024-02-01` |
| `ro.boot.flash.locked` | **1**（Bootloader 锁定） |
| `ro.boot.verifiedbootstate` | `green`（锁 + 官方 key 链） |
| `ro.boot.secboot.enable` | `yes` |
| `ro.debuggable` / `ro.adb.secure` | `0` / `1` |
| **`ro.oem_unlock_supported`** | **1** |
| `ro.boot.board_id_for_odm` / `pcb_version` | `dvt4` / `v120` |
| `ro.boot.dtb_idx` / `dtbo_idx` | `1` / `5` |
| `ro.boot.baseband` / `dynamic_partitions` | `msm` / `true` |

**最值得注意的一条**：`ro.oem_unlock_supported=1` 表示 Bootloader 自报"支持 OEM 解锁"，
这与早期 `fastboot flashing unlock` 返回 `unknown command` 的结论存在张力——
值得在 OEM Unlock 专题里按"命令/入口是否不同"再核一次（例如 `fastboot oem unlock`、
或先 `setOemUnlockAllowedByUser` 再走 `flashing unlock`）。

## 3. 隐私与发布风险

- 设备序列号 `b940328a` 出现在 3 个文本文件：`03/hand5g_debloat_audit/00_devices.txt`、
  `03/.../01_getprop_full.txt`、`19-repository-sync-20261025/remote-cache/docs/research/p780-ipsec-v0.2-live-loopback-20261024.md`；
- `kmsg` dump、`dumpsys` 与 `getprop` 里含 MAC、包列表、运行态信息；
- IMEI 关键词命中 77 个文件，但绝大多数是 UI 字符串/权限名；15 位数字命中多在二进制里
  （版本号、常量），**未发现真实 IMEI 值**。

若仓库要公开，建议先对以上三类做脱敏。

## 4. 提取产物（48 号）里的秘密检查

| 产物 | 结论 |
|---|---|
| `vendor_boot_{a,b}_ramdisk` 的 45 个 `.ko` | 只有 vermagic/构建信息，无密钥/凭据 |
| `dtbo_a_entries` 的 22 个 `.dtb` | 硬件配置，无敏感信息 |
| `persist_tree` | Keymaster store 是 TEE 加密 blob，不可解；传感器标定无凭据；coresight 是标准 Qualcomm 脚本 |
| `vbmeta_*` / `fsg` / `modemst*` / `frp` / `devinfo` | 无明文密钥；devinfo 全零、frp 仅 114 字节非零 |

## 5. 建议

1. **轮换 `gh-token`**（若曾同步到任何远程/备份），并把这类凭据移出工作区；
2. 公开仓库前脱敏序列号、MAC、包列表与 kmsg；
3. 把"AVB 用 AOSP testkey"记为**设备弱点**（不是仓库泄露）——它意味着只要拿到写通道，
   签名不再是门槛；
4. 重新核对 `ro.oem_unlock_supported=1` 与 `fastboot flashing unlock: unknown command`
   的矛盾，可能还有一条没试过的解锁路径。


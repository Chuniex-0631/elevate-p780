# P780 DSU 第八轮：Google 六个子目录原始 JSON 完整验证（2026-10-18）

> **阶段结论：** 用户 Windows 实际获取的 Google DSU 根索引及六份官方子目录经离线 ZIP CRC、逐字节 SHA-256、JSON 解析独立核验通过，共 **24 个镜像条目**。截图中实际出现的四个候选都在其中。**六个子目录共 24 条记录全部缺少 `vndk` 和 `pubkey` 字段，因此 UI 的出现不是明确的 VNDK30 支持或 GSI AVB 验签通过的证据。**

## 数据出处与边界

- 机主 Windows Python 审计脚本产生的 `p780-dsu-catalog-detail.zip`（本聊天附件），**4073 字节，SHA-256 `ad732d61aa7751aeaa6f2a148e3a1998aeee645beb5fe3f344fff98d9ca74c74`**。
- ZIP 含主索引（508B）、6份 `catalogs/*.json` 子索引、`report.json`，共8项；ZIP CRC 全通过，所有路径和单条大小合理；本地重新核对 `report.json.catalogs[].sha256` 与 ZIP 内各 JSON 实际原始字节，6/6一致，`report.errors=[]`。
- 这些是 **PC 从 Google 下载的公共镜像清单元数据**，并不是 P780 设备本身抓到的 HTTPS 流量或实际镜像 ZIP；**没有下载任何 GSI ZIP、无 DSU 安装、无 Root、无 BL 解锁**。原始 ZIP 由机主与本轮聊天保存，本研究总结只记公开目录及 SHA。
- 主索引 `https://dl.google.com/developers/android/gsi/gsi-src.json` 的 SHA-256 为 `0a1970abfceb6bf3962177881b255e6af9d4f43903aac3ba9aef2c1e5b4a2d09`，其中含6个 `include`。
- 上游规范：[AOSP DSU JSON descriptor](https://source.android.com/docs/core/ota/dynamic-system-updates#dsu-json-descriptor) 与 [Settings `DSULoader.java`](https://android.googlesource.com/platform/packages/apps/Settings/+/286dce6b6ed/src/com/android/settings/development/DSULoader.java)。

## 每个 Google 子目录原始字节 SHA-256

| 分支 | Android | 原始 JSON 字节 | SHA-256 | 镜像数 |
|---|---|---:|---|---:|
| `rvc` | 11 | 1567 | `643538d1e6ce091772d71f5ee7f3dc1b6bf6eecf9eba58b252263e5e4b2b29ac` | 4 |
| `sc` | 12 | 1599 | `d5466d9950d0036170a0b2d0d71934856940cecd399515331de32fd91a2382aa` | 4 |
| `tm` | 13 | 1607 | `e363b642145ff198380e40681e3e521070b70ae3eb10c4b9a338eb6a454feeca` | 4 |
| `udc` | 14 | 1587 | `97439e3a04006da086fd63cc9ccafb7d6f8e6af30e64df1e580a28d22d1d988e` | 4 |
| `vic` | 15 | 1611 | `ae0b61eb52f34659ce5545967f748551046c2a497ec6ce4770145dadf288c3db` | 4 |
| `baklava` | 16 | 1627 | `410cc47372812734694fdfcd10d92030ac95fad4eda3283619a01162cd7d3319` | 4 |

真实目录路径均为 `https://dl.google.com/developers/android/<branch>/images/gsi/gsi-dsc.json`。

## 真机截图四个选项的精确来源

| 镜像名称 | 分支 / OS | 原始 `details` | `spl` |
|---|---|---|---|
| GSI ARM64 | vic / B / Android 15 | `arm64-exp-BP1A.250405.005.C1-13151952-61d23231` | `2025-04-05` |
| GSI+GMS ARM64 | vic / B / Android 15 | `gms_arm64-exp-BP1A.250405.005.C1-13151952-48d6db2a` | `2025-04-05` |
| GSI ARM64 | baklava / C / Android 16 | `arm64-exp-CP11.251209.009.A1-14840729-59a822d9` | `2026-01-05` |
| GSI+GMS ARM64 | baklava / C / Android 16 | `gms_arm64-exp-CP11.251209.009.A1-14840729-89298580` | `2026-01-05` |

这四项都在 JSON 中明确标注 `cpu_abi=arm64-v8a` 和 `uri=https://dl.google.com/.../*.zip`。这些完整 ZIP URI 是**目录中的元数据字符串**，未访问下载链接。

**脚本/旧截图读数的纠错：** 原先助手把 Android16 构建识读为 `CPI1`（字母 I），并把它写入审计脚本的 `TARGETS`，导致 `report.json.matches` **只列出 Android15 的4个记录（2个 ARM64、2个 x86）**；并不是抓取失败。放大原手机截图并与 `baklava` 原始 JSON 校对后，准确字符串是 **`CP11`（数字1、数字1）**，Android16 ARM64 的两条上表记录在 `baklava` 文件中。今后应修改脚本目标，并**从原始 JSON 再算结果**，不可把旧 `report.matches` 当作穷尽匹配清单。

## 关键签名和 VNDK 结论

| 字段 | 24 条 JSON 原始记录实际存在情况 | 正确解读 |
|---|---|---|
| `cpu_abi` | **24/24** 有 | GSI ARM64 候选架构与 P780 `arm64-v8a` 一致 |
| `os_version` | **24/24** 有 | `B`/Android15、`C`/Android16 由各自目录和 GSI 版本标识对应 |
| `spl` | **24/24** 有 | 安卓11 P780 安全补丁 `2024-02-01`，旧目录 R/S/T/U 的补丁日期全早于设备，因此会在 AOSP `DSULoader.isSupported()` 的安全补丁比较中被过滤；剩下 vic/baklava ARM64 各两项，恰与四项截图一致 |
| `uri` | **24/24** 有 | 仅获取到目标 ZIP 的公开 URL 字符串，不能据此证明包实际可下载或为可信镜像 |
| `vndk` | **0/24** 有 | Loader 在没有字段时 **跳过 VNDK30 显式列表校验**，而不是证明镜像内含 VNDK30 |
| `pubkey` | **0/24** 有 | JSON 未携带特定 DSU 公钥 SHA-1 预检标识；不是镜像无 AVB 签名、也不是 P780 的 AVB/GSI信任公钥一定接受该镜像的证据 |

参考 AOSP Android11 `DSULoader.java`: `vndk` 缺失时 `mVndk=null`，`isSupported()` 不会作版本列表匹配；`pubkey` 缺失时 `mPubKey=""` 并继续传给后续 DSU 流程。**Android 15/16 可被 Settings 列出是元数据条件允许，不是证明签名和 runtime 适配。**

AOSP 初筛对 SPL 的约束是候选 `spl >= ro.build.version.security_patch`；此前 P780 的 SPL=2024-02-01。2020/2022/2023 旧 GSI 全部低于此值，2025/2026 两组大于，恰好解释 UI 只见四个 ARM64 项。

## 后续安全研究边界

当前没有验证：对应 `system.img` 与 `vbmeta_system` AVB Footer/HashTree、GSI实际签名公钥是否受 P780 启动 Ramdisk 中 `q/r/s-gsi.avbpubkey` 认可、Android15/16 与 Android11 Vendor Keymaster/Gatekeeper/Weaver 和 HAL 运行、具体 GSI 镜像下载可用性。**本轮不建议直接点击任何 GSI 安装**。高价值的下一步是公开材料的 DSU 签名流程/公钥对应关系离线核验；若将来真要安装，需要机主单独确认风险、设备备份、兼容性与失败退出办法，不能以显示目录为充分理由。

机主自己的原始 ZIP 在本轮会话中可用于二次验证，**未把原件推入 Git 或暴露任何本机唯一硬件标识**。

# EDL programmer 公开渠道搜索结论（2026-10-26）

> 结论：**P780 的签名 Firehose programmer 不在公开渠道。** EDL 可达，但没有匹配
> OEM key 的 loader，读/写/刷机都做不了。这不是“再多搜几个仓库”能解决的问题。

## 1. 设备身份（已确认）

- 机型：Rakuten Hand 5G / TINNO **P780**
- SoC：**Snapdragon 480 / Holi（SM4350）**（XDA 原帖与 HWID 一致；不是 SM6375）
- HWID：`0x0016f0e100000780`（MSM `0x0016f0e1`，model `0x0780`）
- OEM PKHash 前缀：`c19a5029d659b034…`（完整值只在机主 PC）
- EDL：`05c6:9008`，QDL v2.8 可读 Sahara v2；Firehose 未通

## 2. 已排除的公开来源

| 来源 | 结果 |
|---|---|
| `bkerler/Loaders` `qualcomm/factory` | 只有 `mannar`（SM6375），**无 holi**；A/B/C 根 `d9357db8…` |
| `leefshitz2/Qualcomm_Loaders` `480-特殊` | 只有 `OPPO480.elf` + `Sign.bin`/`Digest.bin`，OPPO OEM key，不是 TINNO |
| `Iqinix/Qualcomm-firehoses` | 顶层按 OEM 分（Honor/Huawei/Infinix/…/ZTE），**无 TINNO/Rakuten** |
| GitHub 文件搜索 | 无 `0016F0E100000780` 或 `c19a5029` 命名的 loader |
| XDA 4805241 原帖 | 同一台 P780，确认 EDL 可达、OTA testkey 被拒，**无 loader/固件** |
| Rakuten / TINNO 官方 | 只有更新通知，无固件/服务工具 |
| 五份候选 A–E | 平台/根都不匹配（Mannar/Qualcomm/Hisense/Lenovo；根 `d9357db8…`/`4352b3bf…`/`a51a1c2e…`） |

## 3. 为什么难

- programmer 必须由 **TINNO 的 OEM key**（PKHash `c19a5029`）签名，PBL 才认；
- 同 SoC 的 OPPO/其它 OEM loader 签的是各自 OEM key，不能通用；
- P780 是 TINNO 的 **Holi** 机型，公开仓库里没有对应 holi 签名包；
- 即使拿到 EDL，BL 锁状态还在 **RPMB**，EDL 也未必能直接解锁；但可以用
  **公开 testkey** 刷 `boot`/`vbmeta` 得到持久 root。

## 4. 剩余选项

1. **商业维修工具/服务**：ChimeraTool、UnlockTool、Octoplus、TFT 等，或 TINNO
   授权维修点——它们的服务器里可能有 P780 的签名 loader（付费、外部）；
2. **新内核 CVE/新车辆**：GhostLock 5.4 公开车辆已全部判负（见 56 号），
   需要新的写通道；
3. **等待固件/loader 泄露**：无时间表。

公开材料能做的到此为止。**没有可复现的免费 EDL/root/BL 路径。**

## 5. 来源

- [XDA 4805241](https://xdaforums.com/t/p780-rakuten-hand-5g-looking-for-stock-firmware-firehose-loader-edl-reachable-ota-sideload-not-using-aosp-test-key.4805241/)
- [bkerler/Loaders](https://github.com/bkerler/Loaders)
- [leefshitz2/Qualcomm_Loaders](https://github.com/leefshitz2/Qualcomm_Loaders)
- [Iqinix/Qualcomm-firehoses](https://github.com/Iqinix/Qualcomm-firehoses)
- [ChimeraTool Rakuten](https://chimeratool.com/ja/models/rakuten)
- [Rakuten 更新页](https://network.mobile.rakuten.co.jp/information/software/rakuten-hand-5g/)
- [Volerion CVE-2026-107153](https://volerion.com/vulnerabilities/CVE-2026-107153)

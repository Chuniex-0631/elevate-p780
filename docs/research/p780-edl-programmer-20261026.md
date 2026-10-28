# EDL programmer 公开渠道搜索结论（2026-10-26）

> 2026-10-28 文档复核：只更正解释与证据范围，未新增设备实测；当前状态以 [STATUS](../STATUS.md) 为准，历史候选步骤不作为当前执行计划。

> 2026-10-26 审计更正：本页为旧搜索记录，绝对化结论由[新筛查报告](p780-firehose-screening-20261026.md)更正：未找到≠不存在；摘要混有 SHA-384/SHA-256；Mannar 工具标签不直接否决 MSM_ID；商业 P780 EDL 读取未证实。受限临时 Root 已有后续成功记录。RPMB、可持久写入等未经本轮设备验证。

> 结论：**截至本轮检索未获得可验证匹配的 P780 programmer。** Sahara 可达；完整 EDL 读写与刷写启动链未证实，不能据检索未命中断言公开样本不存在。

## 1. 设备身份（已确认）

- 机型：Rakuten Hand 5G / TINNO **P780**
- SoC：**Snapdragon 480 / Holi（SM4350）**（XDA 原帖与 HWID 一致；不是 SM6375）
- HWID：`0x0016f0e100000780`（MSM `0x0016f0e1`，model `0x0780`）
- OEM PKHash 前缀：`c19a5029d659b034…`（完整值只在机主 PC）
- EDL：`05c6:9008`，QDL v2.8 可读 Sahara v2；Firehose 未通

## 2. 已排除的公开来源

| 来源 | 结果 |
|---|---|
| `bkerler/Loaders` `qualcomm/factory` | 历史按目录名检索未获 holi 样本；Mannar 不直接否决 MSM_ID；根算法详见新筛查 |
| `leefshitz2/Qualcomm_Loaders` `480-特殊` | 只有 `OPPO480.elf` + `Sign.bin`/`Digest.bin`，OPPO OEM key，不是 TINNO |
| `Iqinix/Qualcomm-firehoses` | 顶层按 OEM 分（Honor/Huawei/Infinix/…/ZTE），**无 TINNO/Rakuten** |
| GitHub 文件搜索 | 无 `0016F0E100000780` 或 `c19a5029` 命名的 loader |
| XDA 4805241 原帖 | 同一台 P780，确认 EDL 可达、OTA testkey 被拒，**无 loader/固件** |
| Rakuten / TINNO 官方 | 只有更新通知，无固件/服务工具 |
| 五份候选 A–E | 已扫描根摘要未见目标前缀；Mannar 标签不足以否决平台，完整兼容性未验证（见新筛查报告） |

## 3. 为什么难

- programmer 须按本机信任链验证；完整 PKHash、签名头、根数组与算法尚须核对，不由厂商名推断唯一可接受根；
- 同 SoC 或 OEM 标签不能证明可通用；须按具体文件签名与设备条件核验；
- P780 是 TINNO 的 **Holi** 机型，公开仓库里没有对应 holi 签名包；
- 本机 BL 状态是否存于 RPMB 未经验证；Sahara 或 loader 可用也不代表能解锁。AVB testkey 不提供写入或启动能力，不能据此宣称持久 Root。

## 4. 剩余选项

1. **商业维修工具/服务**：ChimeraTool、UnlockTool、Octoplus、TFT 等，或 TINNO
   授权维修点——它们的服务器里可能有 P780 的签名 loader（付费、外部）；
2. **新内核 CVE/新车辆**：GhostLock 5.4 公开车辆已全部判负（见 56 号），
   需要新的写通道；
3. **等待固件/loader 泄露**：无时间表。

截至该轮，未形成经验证的完整 EDL、永久 Root 或 BL 解锁链；临时受限 UID0 shell 已有成功记录，不能用本页否定。

## 5. 来源

- [XDA 4805241](https://xdaforums.com/t/p780-rakuten-hand-5g-looking-for-stock-firmware-firehose-loader-edl-reachable-ota-sideload-not-using-aosp-test-key.4805241/)
- [bkerler/Loaders](https://github.com/bkerler/Loaders)
- [leefshitz2/Qualcomm_Loaders](https://github.com/leefshitz2/Qualcomm_Loaders)
- [Iqinix/Qualcomm-firehoses](https://github.com/Iqinix/Qualcomm-firehoses)
- [ChimeraTool Rakuten](https://chimeratool.com/ja/models/rakuten)
- [Rakuten 更新页](https://network.mobile.rakuten.co.jp/information/software/rakuten-hand-5g/)
- [Volerion CVE-2026-107153](https://volerion.com/vulnerabilities/CVE-2026-107153)

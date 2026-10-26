# Firehose 候选与商业 EDL 读取核对（2026-10-26）

本轮只处理 PC 文件。工具不含 USB、串口、ADB、EDL 客户端、设备命令或候选自动执行代码。目标是可复核筛查，不产生“可刷写”认证。

## 1. 设备依据与摘要算法

仓库[脱敏 EDL 历史记录](../../archive/device/P780_EDL_2026-06-12_sanitized.txt) 给出 HWID `0016f0e100000780`（MSM `0016f0e1`、OEM `0000`、MODEL `0780`）；CPU 映射打印 `mannar` 与 Android `holi` 不同，不能仅凭工具映射否决同 MSM_ID 文件。[fastboot 原始输出](../../evidence/20261026/oem/fastboot-getvar-all.txt) 的 `variant:SM_ UFS` 和 logical-block-size `0x1000` 为 UFS/4096 提供历史依据；不是本轮 Firehose 的 getstorageinfo 返回值。

仓库此前仅公布 PKHash 前缀 `c19a5029…`，完整本机读数仍需机主私下核对。网上相同机型帖子中的完整值不应自动当作本机原件。此轮公开报告不补写本机完整 PKHash。

[bkerler 上游解析器](https://github.com/bkerler/edl/blob/master/edlclient/Tools/fhloaderparse.py) 会因签名格式/元数据选择 SHA-256 或 SHA-384，并以根证书区域作摘要；loader 文件名只保留前缀。[上游 README](https://github.com/bkerler/edl) 的自动命名和 UFS 命令说明只能解释工具行为，不证明 P780 接受某个文件。本工具独立提取可解析的 X.509 DER，输出 **DER SHA-256、DER SHA-384 与独立的 SPKI SHA-256**，三者不可混淆。多根、元数据版本、根证书数组/填充区域需要继续按签名头解析；本工具不验证 Qualcomm 完整镜像签名。

## 2. 本轮重新下载的五份样本

来源固定到 [bkerler/Loaders `6c416255056a178f54ccd7ee9b67d04a5bdfa8e6`](https://github.com/bkerler/Loaders/tree/6c416255056a178f54ccd7ee9b67d04a5bdfa8e6)。递归树此次未截断。没有把 loader 二进制再提交进本仓库，只提交精确来源、字节数、SHA-256、证书偏移与字符串位置。

| 报告文件别名 | 上游路径 | 第一组自签根 DER 摘要 |
|---|---|---|
| qualcomm.bin | `qualcomm/factory/mannar/0016F0E100000000_d9357db88795b5a8_fhprg.bin` | SHA-384 `d9357db88795b5a8…` |
| prog_firehose_lite.elf | `qualcomm/factory/mannar/prog_firehose_lite.elf` | SHA-384 `d9357db88795b5a8…` |
| hisense.bin | `hisense_agm/0016f0e100000000_d9357db88795b5a8_fhprg.bin` | SHA-384 `d9357db88795b5a8…` |
| hisense_0043.bin | `hisense_agm/0016f0e100430000_4352b3bfeac440ca_fhprg.bin` | SHA-384 `4352b3bfeac440ca…` |
| lenovo.bin | `lenovo_motorola/0016f0e102e80000_a51a1c2e4a5ec0f8_fhprg.bin` | SHA-256 `a51a1c2e4a5ec0f8…` |

每份都还扫描到另一组自签根（XBL Sec Attestation Root CA 4）；**不能把文件最后一个证书直接当 programmer 所用 OEM 根**。前四份 `d935…/4352…` 是 SHA-384，Lenovo 文件名是 SHA-256。旧表把这些短串统一称作同种哈希不够准确。

五份均有 UFS 相关字符串，但不证明能初始化 P780 UFS、识别 LUN 或读取 GPT。本轮扫描到的自签根的 SHA-256/SHA-384 均未出现 `c19a5029` 前缀；这支持“这些已扫描证书未见目标摘要”，不是验证 PBL 的拒绝日志，也不是完整签名兼容性裁决。UFS 和设备接受状态全部保持未验证。

结果：[firehose-screen.json](../../evidence/analysis/boot-edl-20261026/firehose-screen.json)；来源与独立 Git blob 身份核验：[input-manifest.json](../../evidence/analysis/boot-edl-20261026/input-manifest.json)。后者核对下载文件按 `blob <length>\0` 算出的 Git SHA-1，避免把 HTTP 错误页当 loader。

## 3. 离线筛查工具与清单

安装依赖（本机 Python 环境）：`python -m pip install cryptography capstone`。

```text
python tools/abl/firehose_screen.py candidate.elf --output local-screen.json
python tools/abl/firehose_screen.py candidate.elf --pkhash <完整64或96位十六进制摘要> --output private-screen.json
python tools/abl/control_flow_audit.py evidence/20261026/abl/abl_lzma.bin --table 0x4ae98 14
python tools/abl/control_flow_audit.py evidence/20261026/abl/abl_lzma.bin --range 0x310d0 0x1c0
```

`--pkhash` 拒绝短前缀，报告只记录是否提供目标和匹配的证书偏移，不回显参数。源文件不变；输出可覆盖同名本地报告，应选新输出路径。普通退出码 0 仅表示分析完成，不表示兼容。无 DER/无匹配都保持待解析，不自动尝试连接设备。

| 顺序 | 必须核对 | 不能用什么替代 |
|---|---|---|
| 1 | 来源固定提交、文件字节、SHA-256、Git blob | 文件名/网盘描述 |
| 2 | Qualcomm 签名头版本、证书链范围、根数组、摘要算法和完整本机 PKHash | SPKI摘要、文件SHA、8字节前缀 |
| 3 | 镜像签名、HW/SOC_VERS、OEM/MODEL、serial绑定、SW_ID/回滚和认证要求 | 同SoC、同USB ID |
| 4 | UFS初始化代码、存储配置、扇区长度、LUN支持及读取命令权限 | `ufs` 字符串或 `emmc` 文件名 |
| 5 | 单独批准的设备只读会话：授权/握手日志、getstorageinfo、GPT、小分区重复读取哈希 | 9008识别、Get Info、FRP/Format按钮 |

本轮只完成 1 和 2 的 DER 初筛、4 的字符串线索。3 和设备阶段均未完成。即使读取通过也不代表允许写入，更不代表 BL 状态可修改。

## 4. 商业工具公开资料核对

核查日期：2026-10-26（Asia/Shanghai）；未购买许可证、未联系供应商、未运行客户端。

| 工具 | 已核对的第一方来源 | 能支持的结论 |
|---|---|---|
| Chimera | [Rakuten Hand5g P780 专页](https://chimeratool.com/ja/models/rakuten-hand5g-p780) | 精确列出机型，仅 **Get Info**；标为动态使用统计加入。页面未列 EDL 分区读取或 loader；不能据此推荐付费读取 |
| UnlockTool | [官方 models](https://unlocktool.net/models/)；站点限定搜索 Rakuten/P780 | 页面本轮抓取403；没有取得可核验的P780 EDL读取条目，状态未知 |
| Hydra | [官网](https://hydradongle.com/)与[发布记录](https://hydradongle.com/download/software) | 有泛用固件备份功能宣传；没有取得本机型读取证据 |
| Octoplus / TFT | 本轮未取得可核验的精确机型/模式/分区读取第一方记录 | 仍为未核实候选，不宣称支持或不支持 |

检索排除 Lenovo P780（另一机型）、普通 Get Info、FRP reset/format、泛 Qualcomm Flash 功能，以及仅有品牌名的结果。搜索无结果不能证明工具绝不支持。供应商若愿意确认，应给出精确机型/固件、客户端版本、EDL模式、是否需在线授权、实际读取分区/GPT与字节数、两次读取 SHA-256，说明不会自动格式化/写安全分区。只收脱敏记录；不要发送原始用户分区或登录凭据。

## 5. 对旧结论的修正

“公开渠道没有”改为“截至本轮检索未获得可验证匹配样本”；“同 MSM_ID 的 Mannar 文件必然平台不匹配”改为待核实兼容性；“TINNO key/RPMB/只缺签名loader”都需要明确本机签名/存储证据，不能以厂商名或常见设计代替。AVB测试密钥与PBL programmer签名是不同信任链，不能互换。完整 EDL 读写、BL 解锁和永久 root 均未在本轮证实。

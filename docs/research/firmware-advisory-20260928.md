# Rakuten Hand 5G 固件真实性漏洞：JVN#47427200 / CVE-2026-107153

## 结论（更新：2026-10-15）

2026-10-14，Japan Vulnerability Notes 公布 [JVN#47427200](https://jvn.jp/jp/JVN47427200/)，把 Rakuten Mobile 早先只描述为“固件真实性确认机制缺陷”的问题具体归因为：

- Rakuten Hand 5G 的 Android Verified Boot（AVB）使用了已知的 AOSP 测试钥匙；
- **受影响范围为全部版本**，因此覆盖本机 `P780AE_11.0_RMN_JP_162`；
- 登记为 [CVE-2026-107153](https://www.cve.org/CVERecord?id=CVE-2026-107153)、CWE-1391；JVN iPedia 记录号为 [JVNDB-2026-000147](https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000147.html)；
- 物理接触设备后，攻击者可能安装细工的系统镜像。CVSS v4 为 7.0，v3 为 6.6；向量均要求物理访问，低权限、无需用户交互。

这是对固件信任链的**官方协调披露实证**。它仍然**不是**本机已 Root、Bootloader 已解锁或已找到可用刷写通道的证据。

## 时间线与原始来源

| 日期 | 来源 | 新增事实 |
|---|---|---|
| 2026-09-28 | [Rakuten Hand 5G 官方支持页](https://network.mobile.rakuten.co.jp/product/smartphone/rakuten-hand-5g/support/index.html) | 厂商确认修改固件可能被误判为正版；临时操作设备者可能取得权限、运行程序或改设置。页面未公开成因和编号 |
| 2026-10-14 | [JVN#47427200](https://jvn.jp/jp/JVN47427200/) | 明确成因为 AVB 使用 AOSP 测试钥匙，影响 Hand 5G 全版本；给出 CVE/CWE、CVSS 与物理攻击条件 |
| 2026-10-14 | [JVN iPedia](https://jvndb.jvn.jp/ja/contents/2026/JVNDB-2026-000147.html) | 登记 JVNDB-2026-000147；说明由 IPA 接报、JPCERT/CC 与开发者协调，报告者为松原正佳 |
| 2025 | [AVBTestKeyInTheWild 论文](https://www.android-device-security.org/publications/2025-leierzopf-spices/Leierzopf_2025_SPICES_AVBTestKeyInTheWild.pdf) | JVN 引用的通用技术研究；解释测试钥匙如何削弱 AVB，以及修改、重签、重建 vbmeta 和部署的通用链路 |

厂商已结束该产品支持，JVN 给出的对策是停止使用并更换后续产品；公开资料没有修补包。

## 技术含义

论文描述的通用链路包含四个必要阶段：

1. 取得目标设备的原厂固件镜像；
2. 分析并修改受 AVB 保护的镜像，例如 boot；
3. 使用被设备接受的测试钥匙重签分区，并重建相符的 vbmeta 描述；
4. 通过该设备实际允许的通道把镜像写入分区。

测试钥匙解决的是第 3 阶段的**签名信任**问题，不会自动解决第 1 阶段的原厂输入，也不会凭空产生第 4 阶段的分区写入能力。论文也明确指出部署方式因设备而异，锁定 Bootloader 下公开可用的强制写入机制只存在于少数厂商/设备。

论文演示了 Fairphone 3、Cubot A1 和 Tecno Spark 10 Pro 等设备，**没有给出 Rakuten Hand 5G / P780 的实机 PoC、分区图或刷写命令**。JVN 将论文作为相关技术文献引用，不能把论文里的其它机型部署方式直接移植为 P780 成果。

## 本机适配条件与当前缺口

本机固件 `P780AE_11.0_RMN_JP_162` 处于 JVN 所称“Hand 5G 全版本”范围内；但要安全、可复核地验证，还缺：

- 有可追溯来源和哈希的 `_162` 完整 OTA，或至少原厂 `boot.img`、`vendor_boot.img`、`vbmeta*.img`；
- 对上述镜像做离线 AVB 元数据、链式分区描述、回滚索引和公钥指纹核对；
- P780 在 **locked** 状态下可用且经验证的写入通道。当前标准 Fastboot 解锁/写入相关命令没有成功证据；
- 若考虑 EDL，仍需与 `HWID 0x0016f0e100000780` 及设备 PK hash 匹配、且有真实握手记录的 Firehose loader；同 SoC loader 不足以证明兼容；
- 可恢复的原厂分区备份和明确的失败回退方案。

在这些条件满足前，不制作或刷入修改镜像，不运行公开利用链。安全的下一步仅限于获取可信原厂二进制、保存哈希，并对 AVB 元数据做离线审计。

## 与现有研究支线的边界

- **不是 GhostLock**：本问题位于 AVB/固件供应链；GhostLock 是内核 RT mutex 路径，二者没有已证实的因果关系。
- **不是 JourneyConfigService**：明文 HTTP、`RootProcess` 名称和应用策略消费者与 AVB 测试钥匙无关。
- **不是 Bootloader 解锁证明**：锁状态可以保持 locked，而签名验证仍因受信任测试钥匙而失效；“可被错误信任”与“已有途径写入”是不同条件。
- **不是当前 Root 成果**：本机仍未 Root、未解锁；`_162` 原厂二进制和匹配 Firehose 仍缺。

## 2026-10-18：实机 AVB 基线与离线验证路径

机主实机 ADB 输出确认本次启动：`green`、`locked`、`flash.locked=1`、slot `_b`、VBMeta digest `33ee3a6cf5215befd8a4f953382bd746d12efc37f6d4116c0c9b68a7661f95f2`。详细证据边界、AOSP `calculate_vbmeta_digest` 正确比较方式和 Windows 只读采集脚本见 [独立 AVB 取证专题](avb-live-baseline-20261018.md)。这个 digest 不是公钥指纹，也不是原厂二进制；锁定态写入通道依旧未知。

## 2026-10-17：XDA 正文由用户提供

来源：[XDA 4805241](https://xdaforums.com/t/p780-rakuten-hand-5g-looking-for-stock-firmware-firehose-loader-edl-reachable-ota-sideload-not-using-aosp-test-key.4805241/)，[用户粘贴全文](../../evidence/web/2026-10-17/xda-4805241-user-provided.txt)。取得时间为 2026-10-17；不是直接下载的网页 HTML，作者身份、发表日期及独立性未核实。未提供测试 ZIP、签名命令、证书指纹或完整 Recovery 日志，也未给出固件构建号，不能直接归属于本机 `_162`。

- 作者报告正常启动后 `adb reboot edl` 可进入 05c6:9008；这只是第三方报告，不是本机新采集的结果，更不代表 Firehose 握手或分区读写成功。
- 作者报告 Recovery 主菜单无 ADB，sideload 可连接但 shell 返回 closed；菜单出现 fastboot/SD card 选项，不证明 fastboot 写入权限或物理 SD 卡能力。
- 作者报告以 `testkey.x509.pem / testkey.pk8` 和 signapk 签名的最小 ZIP 被拒，显示 `Signature verification failed`。严格结论仅是“该测试包在该次测试中未通过验签”；不能仅凭叙述确定 Recovery 实际信任钥匙。
- AOSP 将 OTA ZIP 的证书验签与 AVB 镜像信任分开；`testkey.x509.pem/testkey.pk8` 不等同于 AVB 的 RSA 测试密钥。原文把两者的测试钥匙概念混用，不能以此推翻 JVN。参阅 [AOSP OTA 签名说明](https://source.android.com/docs/core/ota/sign_builds)。
- signapk 是否使用 OTA 所需 whole-file 签名（如相应版本的 `-w`）、包结构与签名是否有效、Recovery 实际钥匙集合，都缺证据。优先离线核对，暂缓重复实机 sideload 尝试。系统 `/system/etc/security/otacerts.zip` 可作线索，但不能单独替代 Recovery ramdisk `/res/keys`（两者可能不同）。
- “只剩 EDL”是作者判断，不是已经穷尽所有通道的证明；原文请求的 `fastboot boot` 是求助方向，未报告成功。
- `OPG105` 仅是作者提出的检索别名，尚无同板/分区/签名/固件对应证据；不得直接视为 P780 兼容机型。`rawprogram*.xml/patch*.xml` 是 EDL 包可能携带的刷写描述文件，不能要求普通 OTA 必然包含它们。

优先级：继续获取可信原厂镜像与匹配 Loader／可复核锁定态通道；将“用公开 OTA testkey 直接 sideload”的捷径降为暂缓。后续若取得测试 ZIP、完整签名命令、Recovery 日志、构建身份及可信公钥集合，可重新评估该负面结果。当前仍未 Root／未解锁，GhostLock 状态不变。正文获取请求已完成，不重复要求用户提供同一正文；附件与原始实验工件仍未取得。

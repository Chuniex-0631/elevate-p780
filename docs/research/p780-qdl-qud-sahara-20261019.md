# P780 EDL / QDL QUD 通信突破与 Mannar Loader 待测（2026-10-19）

## 证据与范围

2026-10-19，机主在 Windows x64 上用 [linux-msm/qdl v2.8](https://github.com/linux-msm/qdl/releases/tag/v2.8) 官方 Release 的 Windows x64 二进制执行 `qdl list` 和 `qdl chipinfo --backend=qud --serial=COM6 --debug`。程序自报 `v2.8-dirty`；这是构建输出字符串，不单独证明二进制遭篡改。原始终端输出及 `P780-QDL-chipinfo.log` 保留于机主 PC / 当前会话；未提交含设备序列和完整 PKHash 的原件。

### 实际观察

- Windows 设备 `05C6:9008` 经 Qualcomm QDLoader 驱动呈现为 `COM6`；QDL `list` 列出该设备。
- `qud: opened COM6`，`Sahara HELLO version 2 mode 0`，`Sahara protocol version: 2`；至少一次运行完整展示初始 HELLO，另一次成功读取芯片信息。
- 机上 `HW ID: 0x0016f0e100000780`，其中 MSM `0x0016f0e1`、OEM `0x0000`、model `0x0780`，与 2026-06-12 保存的 EDL 记录一致。
- OEM PKHash 前缀 `c19a5029d659b034…` 与早期记录一致；设备序列、完整 OEM PKHash 不写入本页。

### 先前工具的阻断与区分

- [bkerler/edl](https://github.com/bkerler/edl) v3.62 在 Windows `--serial` COM6 模式可识别 `05c6:9008`，但首次读 Sahara HELLO 得到空响应，随即向目标发送 Firehose XML NOP；设备返回 `04 00 00 00 10 00 00 00 0d 00 00 00 01 00 00 00`，对应 Sahara END_TRANSFER / status 0x01，随后误走 Streaming/HDLC 并停住。
- 机主修改本地 `seriallib.py`，取消按照瞬时 `in_waiting` 缩短读取长度；同样的异常依旧。此补丁**未解决问题**，不是原仓代码变更。
- QDL 自 2026-06 v2.7 已有 Windows QUD 后端及对 QUD 丢失初始 Sahara HELLO 的处理；v2.8 源码可复核。此次 QDL 结果证实能稳定到 Sahara command-mode 芯片信息层，不代表以前的 bkerler/edl 整体不可用。

### Loader 匹配与下一步

- [bkerler/Loaders 通用 Mannar 候选 A](https://github.com/bkerler/Loaders/blob/main/qualcomm/factory/mannar/0016F0E100000000_d9357db88795b5a8_fhprg.bin)：文件名的 MSM `0016F0E1` 匹配，model `0000` 不同于 P780 `0780`，签名哈希前缀 `d9357db8…` 不同于机主 `c19a5029…`；极可能被安全启动拒绝。
- **尚未上传此候选、未运行 Firehose、未读取 GPT/UFS、未刷写、未 Root 或解锁。** 之前两次 bkerler 错误不能记作候选 A 被拒。
- 若机主继续授权实验，应在完成手机备份并能正常回 Android 后，用 QDL 的 `<programmer> reset` 路径单独验证 Sahara 镜像传输和 Firehose configure/reset；不带 XML/flash/write/erase。注意该命令会尝试在设备 RAM 中执行第三方 Loader、初始化存储并执行复位，不承诺零风险；不要以 `--dry-run` 代替实机测试（该选项不连接设备）。
- 根据返回的 Sahara NAK / 哈希验证失败 / Firehose configure ACK 分类结果；其后才讨论下一个候选，不反复随机上传。

## 参考

- [QDL v2.8 源码](https://github.com/linux-msm/qdl/tree/v2.8/src)、[v2.8 变更](https://github.com/linux-msm/qdl/blob/v2.8/CHANGELOG.md)；`src/sahara.c` 包含 QUD 缺失 HELLO 的恢复，`src/qdl.c` 的 `qdl_flash` 接受 `<programmer> reset`，生成 `CONFIGURE`/ `RESET` 操作。
- [bkerler/edl 的串口/握手源码](https://github.com/bkerler/edl/tree/master/edlclient/Library)、[Mannar Loader 候选](https://github.com/bkerler/Loaders/tree/main/qualcomm/factory/mannar)。

**证据等级**：机主提供的实际终端输出（未提交原始身份日志） + 官方项目源码交叉解释。签名校验和 Loader 功能均未实机测试。

### 候选 A 实机测试：Sahara READ64 后中断（2026-10-19）

机主使用 QDL v2.8 在 Windows QUD/COM6 执行 `--backend=qud --serial=COM6 --storage=ufs --debug <Mannar candidate A> reset`。
设备先后请求 Sahara image 13 的四个区间：offset/length 为 0x0/0x40、0x40/0x3b8、0x1000/0x1000、0x2000/0xc40。随后程序返回 `failed to read sahara request from device`。
QDL 未打印 `failed to write ... bytes to sahara`，但没有后续 END OF IMAGE、DONE、Firehose 配置或 ACK。签名不匹配是高优先级假说，但无明确设备 NAK/认证错误码；亦不能排除目标中止或 QUD 超时。
本次不证明完整上传、签名通过、Firehose 运行、GPT/UFS 访问或解锁。`reset` Firehose 操作未执行。QDL 上游问题 https://github.com/linux-msm/qdl/issues/184 提示失败后可能需物理重新连接，先确认设备完整恢复 Android，再评估新尝试。

状态：`EARLY_SAHARA_READ64_FAILURE / CAUSE_UNDETERMINED`。日志包含设备身份，仅保存在机主 PC / 会话，不纳入仓库。

### 机主复核：设备正常返回 Android；离线来源搜索（2026-10-19）

上一轮 QDL 传输失败后，机主重新启动设备，Windows ADB 显示设备为 `device` 且 `adb shell getprop sys.boot_completed` 返回 `1`。这是恢复能力的一次实测，并不证明 Firehose Loader 被接受或风险为零。原始 ADB 设备序列号不存仓。

只读调查：GitHub `bkerler/Loaders`（1015 个树条目）、`Iqinix/Qualcomm-firehoses`（1325）、`leefshitz2/Qualcomm_Loaders`（3964）、`essoojay/qualcomm-Loaders`（916）、`RenateUSB/loaders`（70）、`DavidBGE-cmd/Firehose-Finder`（742）、`RoSc22/Qualcomm-_prog_firehose`（682）、`digudc/Programmers`（609）、`Alephgsm/SAMSUNG-EDL-Loaders`（479）的当前递归路径清单；未见文件名含 P780 的签名哈希前缀 `c19a5029` 或准确 HWID `0016f0e100000780` 的 programmer。注意部分仓库是镜像/重复集合，路径搜索的负结果**不证明其二进制内部没有兼容证书**。

2025-06-26 Reddit `r/datarecovery/1ll80dh` 与 `r/androidroot/1ll7jbb` 已有人公开报告相同 P780 HWID 和 PKHash 前缀，仍缺可用 loader；该内容是他人的第三方报告，不能当成本设备测试。

下一步无需再对手机操作：用 [bkerler/edl fhloaderparse](https://github.com/bkerler/edl/blob/master/edlclient/Tools/fhloaderparse.py) 在 PC 上离线提取候选 Programmer 的签名证书链、HWID、PKHash；该脚本依签名格式选用 SHA-256 / SHA-384，不能把主机文件 SHA-256 当作 OEM PKHash。先筛选根证书哈希是否与 P780 设备匹配，再决定是否值得重复上传。

### 候选 A 离线证书元数据复核（2026-10-19）

机主运行 `python -m edlclient.Tools.fhloaderparse candidate-check candidate-parsed`，收到仅一条 `Duplicate: ...` 输出，说明签名解析已经成功，且与原 Loaders 数据库存在签名身份重复记录（不等同于已验证二进制逐字节相同）。原始 `P780-Firehose-offline-parse-v2.log` 为 UTF-16LE PowerShell 输出，保留在当前会话/机主 PC，未入 Git。

| 字段 | 文件 A 内部解析结果 |
|---|---|
|文件长度|698440 字节|
|OEM|Qualcomm|
|MODEL|`0000`|
|HWID|`0000000000000000`（解析器报告；不能仅凭全零推断厂商锁定策略）|
|SWID|`0000000000000003`|
|PK_HASH|`d9357db88795b5a8afaebfd9ab08a569cc8e519f6c689723759f4e6915ca3466e98b5a3282678bdf63673d8517bb0c5b`（96位十六进制，SHA-384 根证书摘要）|
|OEMVER|`crm-ubuntu50`|
|QCVER|`BOOT.XF.4.2-00269-MANNARLAZ-1`|
|VAR|`MannarPkgLAB`|

对照 P780 实机 OEM PKHash `c19a5029d659b034…`（完整值保留机主 PC），**根证书摘要不匹配**。内部签名 HWID 报告全零，与文件名的 `0016F0E100000000` 不同；文件名不是可靠的签名身份依据。根据认证信任根不匹配，**将 A 排除于下一轮优先实机测试名单**。先前四次 Sahara READ64 后断连仍没有设备端错误码，不能把“签名不匹配”与“本次断连原因已实机确证”划等号。

下一步保持手机不操作；对候选 B `prog_firehose_lite.elf` 及其它不同 PKHash 候选进行同类离线证书提取，排除同根重复件，只有取得根摘要匹配并具可信来源的 programmer 才考虑重新制定实机实验。

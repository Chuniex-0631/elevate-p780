# P780 第十四轮：Android 15 GSI AVB 签名公钥 PC 离线提取方案（2026-10-18）

> **进度：操作工具已准备，Python语法与离线模拟流程测试通过，尚未下载官方多GB GSI ZIP、更未读取目标包 AVB 公钥。** BL/Root/DSU实际启动状态不变。切勿将未执行的提取任务登记为“GSI签名不匹配已证实”。

## 输入文件：实证官方目录和 SHA

- 用户 PC 已实际获取、上传并由助手验证 SHA256 的 Google DSU 根索引与 `vic` 子目录 JSON，目标精确匹配P780菜单的 Android15 非GMS ARM64记录：`arm64-exp-BP1A.250405.005.C1-13151952-61d23231`。
- ZIP 官方链接：`https://dl.google.com/developers/android/vic/images/gsi/aosp_arm64-exp-BP1A.250405.005.C1-13151952-61d23231.zip`。
- 官方发布 SHA-256：`61d232315ad773bd4820c76c175efe6a61cd8a9a257508db588032be213e15f7`；此数值由原始 Google JSON 的 ZIP 名末尾缩写、Google [Android15 QPR2 GSI 官方发布页](https://developer.android.com/topic/generic-system-image/releases)完整 SHA 数据交叉核实；**尚未从本次实际下载包重算哈希**。
- Google AOSP 官方 AVB Python 工具来源：`https://android.googlesource.com/platform/external/avb/+/refs/heads/main/avbtool.py?format=TEXT`（原始源文件以base64响应）。AOSP [avbtool.py::info_image](https://android.googlesource.com/platform/external/avb/+/main/avbtool.py) 支持 `--image`、`--output`、`--output_pubkey`，会从system或vbmeta映像携带的AVB结构读取 `Public key (sha1)` 和导出 `.avbpubkey` 二进制。

## 机主 Windows 操作（不触碰手机）

聊天附带两份脚本，建议放到原 `RakutenHand5G` 文件夹，保证对应目标 ZIP 保存到该目录。脚本**没有通过 GitHub 提交分发**，以下列文件 SHA 方便原件追踪：

| 本次工具 | 原始字节长度 | SHA-256 |
|---|---:|---|
| `p780_gsi_avb_run.ps1` | 3150 | `5823dbaa5b09bb165e173ffc342588a547640a7dc77ab44a1a03641ca5adc483` |
| `p780_gsi_avb_extract.py` | 7983 | `64a7ba1a1bbd513845d605ab86a1208114e18f0036ab8d0756e73da7234d0501` |

执行（下载前先确保磁盘**可用≥12 GiB**；此门槛为保守容量安全检查，非手机存储要求）：

```powershell
Set-Location 'C:\Users\ASUS Vivobook\Desktop\RakutenHand5G'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\p780_gsi_avb_run.ps1'
```

PowerShell 工具核对剩余磁盘、通过 `curl.exe --location --continue-at -` 仅下载 Google 官方ZIP（中断可续传）、Windows `Get-FileHash` 完整SHA256校验；再从 AOSP Google源站拉取 `avbtool.py`，由 Python脚本再次SHA校验、仅选择ZIP内 `system.img`、`vbmeta.img`、`vbmeta_system.img` 等必需镜像定向解压；调用 `avbtool info_image --output_pubkey` 获取公钥字节/相关字段、计算SHA1和SHA256并用以前校验的6个 **公开 AOSP** Q/R/S普通及Developer GSI公钥 SHA256做提示性对照。**这些公开参照公钥不是实机P780 ramdisk可信key已验证的原件，脚本明确标记reference-only**。

结果输出在 `p780-gsi15-avb/`，优先只分享小型 `p780-gsi15-avb-report.txt`、`*.avb-info.txt`、`*.avbpubkey`，**不要分享多GB `system.img` 和整个原始ZIP**。若 `system.img` 没有 AVB footer 或 Google 发布包采用不预期的布局，会记录原始 `avbtool` 错误而不自行断言签名拒绝；届时调整提取方式。脚本离线通过了压缩包路径筛选、ZIP SHA保护、定向解压和伪造AVB工具输出的流程测试；**没有在离线容器中下载GB级官方包进行真实签名验证**。

## 如何避免过度解读结果

- 若提取实际 GSI 公钥与六个公开 Q/R/S public SHA 均**不同**，只能说“不匹配这六个公共参照”，不能由此证明 P780 Ramdisk 公钥一定不匹配：设备可能有其他信任公钥。
- 若匹配其中某公开参照，也只能证明 GSI公钥身份，必须后续获得 `_162` 设备实际第一阶段 Ramdisk `avb_keys` 公钥文件来确认受信关系；AOSP 普通 GSI 和 Developer GSI 两类keys不应混用。
- AVB vbmeta的原始公钥匹配只是前置条件之一；还要核对 AVB Footer/rollback 索引、first-stage的活动DSU槽和映像映射；**不等于GSI会实际启动**。
- 目前P780 GSI 安装在系统中，已确认 `installed/disabled`，原厂Android11可正常使用；不要再点Restart/Discard、不要做sticky-mode enable、不要刷写root或unlocked fastboot命令。

## 下一阶段

等待用户上传上述小型输出和 Google ZIP完整哈希校验结果，结合 [Locked BL 与GSI受信密钥专项](p780-dsu-locked-bl-vs-gsi-trust-20261018.md)更新 `STATUS.md`/`EVIDENCE_MANIFEST.md`/`NEXT_STEPS.md`，只把经过镜像实际读取的 SHA 认定为真实签名公钥证据。后续对P780 `_162` 的签名/ramdisk差异应以有来源的精确固件原件为准。
# P780 _162 原厂内核源码与固件工件可得性复核

日期：2026-10-24（Asia/Shanghai）
状态：**未取得可信 _162 原厂 boot/OTA/5.4.233 对应源码；TINNO 请求无回复。**

## 范围和先前证据

目标固件 `P780AE_11.0_RMN_JP_162`、指纹 `Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`、内核 `5.4.233-qgki-gea5245e94afe-dirty`。避免将 Lenovo P780（MediaTek）、Rakuten P710/C330、OPG105 或同 SoC 镜像误认为本机原件。

既有记录：[固件/OTA](firmware-ota.md)、[Google OTA Prober 单次失败](google-ota-prober-p780-20261018.md)、[官方源码申请](../official-source-request-log.md)。不重做已完成的 Google Check-in，不操作手机分区。

## 新一轮公开搜索

| 来源 | 本轮所得 | 限制 |
|---|---|---|
| GitHub 全局 Commit Search `ea5245e94afe` | `commits=[]` | 索引未命中，不等于所有 Git 服务器都不存在 |
| GitHub Code Search 完整 `_162` 构建号与 `ea5245e94afe` | `results=[]` | 非全互联网证据 |
| GitHub Repository Search `Rakuten Hand 5G` | 仅有先前核验过的 [2by2 设备树](https://github.com/2by2-Project-Devices/android_device_rakuten_p780ae) 等非原厂项目 | 该设备树主要移植自 Xiaomi `veux`，不含真实 P780 启动镜像 |
| GitHub Repository Search `P780` | 大量 Lenovo P780 / MediaTek 无关项目 | 相同型号字符串不足以证实兼容 |
| [TinnoOSS/P780](https://github.com/TinnoOSS/P780) | API 仅见 `master`，头提交 `20c26c7658cb5273cc71b10c3704b445b0efbe6b`；公开 `msm-5.4/Makefile` 为 **5.4.61** | 本机是 **5.4.233**，未取得二者对应关系 |
| Web 搜索 `_162` + `boot.img` / OTA / payload | 未找到兼有匹配版本、下载地址与可信出处的可验证工件 | 网络搜索不是全量固件索引 |
| [XDA 的 P780 / OPG105 固件求助标题](https://xdaforums.com/t/request-rakuten-hand-5g-p780-opg105-official-ota-zip-or-full-firmware.4767356/) | 搜索摘要显示为求助，页面直接打开返回 502；正文/附件无法独立核验 | 不得当成已发现镜像或 OPG105 兼容证明 |

没有新的官方 `boot.img`、`vendor_boot.img`、`payload.bin` 或与 `_162` 对应的 GPL 内核源码。上游通用 Linux 5.4.233 和其它厂商 QGKI 5.4.233 都不是 P780 原厂镜像。

## Gmail 实时只读核对（2026-10-24）

- TINNO 请求收件方是官网公开的 **Sales@tinno.com**，这是销售入口，不是已验证的 GPL 专员。
- 邮件头 `Date: Sat, 10 Oct 2026 13:46:01 -0500`，换算到项目 `Asia/Shanghai` 时区是 **2026-10-11 02:46:01**；旧记录中的 10/10 与 10/11 **是同一封信的不同时区日期**。
- Gmail 线程仅有一封 `SENT` 消息，没有 TINNO 回复。只能确认客户端已发，不能证明目标团队收妥。
- 10 月 24 日北京时间凌晨寄出的 Chimera、Hydra、GSMFIX 兼容性询问，目前相关 Gmail 检索也没有发现回复；它们与 GPL 源码获取是分开的线索。

此次**未发送、转发或重发任何邮件**。

## 判断与下一触发条件

**直接观测：** 新一轮 GitHub/网页索引没有命中对应工件；公开 TINNO 内核源码版本不同；TINNO 邮件线程没有回复。

**合理推断：** 真实运行内核与 _162 原厂镜像缺失仍是验证漏洞状态、离线恢复方案的主要障碍。

**不能推出：** 官方从未发布镜像；Git 缩写不存在于别的仓库；已证明有/无 DirtyFrag；拥有可用 Firehose 或锁定态写入能力。

**下一唯一触发：** 获得可核验来源的新源码、原厂镜像、原始 OTA URL 或厂商正式回复。先在 PC 上只读核对机型、构建号、元数据与来源；在恢复材料缺失时不刷写或尝试漏洞利用。是否沿原 TINNO 邮件线程礼貌提醒，等待机主单独决定。

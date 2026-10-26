# 2026-10-26 离线复核产物

输入固定到 `60fe37381d4c2b7bf5152d1d8b36cf5ebbcbc3de`；没有本轮设备会话。`input-manifest.json` 保存输入哈希、五份公开候选的固定提交URL/Git blob核验、依赖版本和 misc 比较结果；未上传候选二进制或本机完整PKHash。

`fastboot-registration.json`：14 项命令/handler指针对；三个反汇编文本：注册循环、FRP读取、注册辅助与分派。地址一律是嵌入PE的RVA。`.text` 包含只读数据，逐字解码的其它输出不自动构成可达代码。

`firehose-screen.json`：所有扫描到的可解析DER证书、DER SHA-256/SHA-384、独立SPKI摘要、自签名校验及存储提示。自签根校验不等于完整链/镜像签名校验。未传完整目标PKHash，因此 signature_screen=not_compared；报告中的前缀差异只作为人工初筛，设备接受与UFS始终未验证。

结论见 [ABL报告](../../../docs/research/p780-boot-edl-audit-20261026.md)与[Firehose报告](../../../docs/research/p780-firehose-screening-20261026.md)。

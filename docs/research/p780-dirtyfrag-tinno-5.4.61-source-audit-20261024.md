# TINNO P780 Linux 5.4.61：DirtyFrag 相关 UDP sendpage / ESP 源码审计

日期：2026-10-24（Asia/Shanghai）  
范围：只读公开源码审计；未执行 PoC、未修改设备、未尝试提权。

## 结论摘要

**TINNO 公开的 5.4.61 候选源码包含一个值得继续核验的旧式 IPv4 路径：**

`sendfile → do_splice_direct → generic_splice_sendpage → pipe_to_sendpage → inet_sendpage → udp_sendpage → ip_append_page → skb_append_pagefrags`

同一候选源码的 `esp_input()` 也存在对未克隆 skb 的 no-COW 快速分支：当 skb 是 nonlinear、没有 frag_list 时，会直接跳过 `skb_cow_data()`；该分支没有检查 `skb_has_shared_frag()`。审计到的 `ip_append_page()/skb_append_pagefrags()` 路径也没有设置旧版 `SKBTX_SHARED_FRAG` 标记。

这构成了与 DirtyFrag 原理**相似且值得进一步核验的静态代码形态**，因此 TINNO 5.4.61 不应被当作完全无关的参考。但这仍然**不是**“5.4.61 已被实机证实可利用”的结论，也不能直接移植成 P780 5.4.233 的漏洞判定。

## 1. 固定源码身份与限制

- 仓库：[`TinnoOSS/P780`](https://github.com/TinnoOSS/P780)
- 固定提交：[`20c26c7658cb5273cc71b10c3704b445b0efbe6b`](https://github.com/TinnoOSS/P780/commit/20c26c7658cb5273cc71b10c3704b445b0efbe6b)，提交说明为 “P780 kernel source”，日期 2021-07-10。
- 源码目录：`msm-5.4/`，项目既有归档标识为 Linux 5.4.61。
- 本机实测版本字符串：`5.4.233-qgki-gea5245e94afe-dirty`。
- 本次没有获得可核验的 P780 `_162` boot/kernel 镜像、`vmlinux`、System.map 或与 5.4.233 构建对应的厂商源码。

因此下文的“存在”仅指固定的 TINNO Git 源码；“与 P780 相似”只能作为候选推断。

## 2. 旧式 IPv4 UDP sendpage 调用链

| 层级 | 固定源码观察 | 解释与边界 |
|---|---|---|
| sendfile syscall | [`fs/read_write.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/fs/read_write.c#L1393-L1470) 的 `do_sendfile()` 调用 `do_splice_direct()` | 证明候选源码的 sendfile 实现走 direct-splice |
| pipe 到 socket | [`fs/splice.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/fs/splice.c#L434-L455) 的 `pipe_to_sendpage()` 调用目标文件的 `sendpage`；`generic_splice_sendpage()` 使用该 actor | 是旧式 page-to-socket 零拷贝接口链 |
| socket / IPv4 协议分发 | [`net/socket.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/socket.c#L125-L153) 将 socket 文件的 splice-write 设为 `generic_splice_sendpage`；[`af_inet.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/ipv4/af_inet.c#L816-L829) 的 `inet_sendpage()` 分发到协议 `sendpage` | 该调用链是候选源码的代码级观察 |
| UDP | [`net/ipv4/udp.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/ipv4/udp.c#L1248-L1297) 的 `udp_sendpage()` 调用 `ip_append_page()`；`udp_prot.sendpage = udp_sendpage`（约 2792 行） | 固定源码具有旧式 IPv4 UDP sendpage |
| IP 分片页 | [`net/ipv4/ip_output.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/ipv4/ip_output.c#L1322-L1450) 的 `ip_append_page()` 调用 `skb_append_pagefrags()`；[`net/core/skbuff.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/core/skbuff.c#L3590-L3608) 只增加 page 引用并填充 frag 描述符 | 审阅到的这条路径没有设置 `SKBTX_SHARED_FRAG` |

### 与 v0.3 实机结果的关系

机主于 2026-10-24 回传的 v0.3 结果显示：P780 API 30、内核字符串 5.4.233；应用私有 1 KiB 文件通过一次 `sendfile()` 发送到 `127.0.0.1` 的 IPv4 UDP socket 成功，接收数据匹配，源文件发送前后内容一致，临时文件已删除。

这与上述旧式 IPv4 调用链相吻合，令该候选路径更值得研究。**但 v0.3 没有内核 trace；它不能单独证明 P780 5.4.233 实际进入了上述每一个函数，也没有将 sendfile 与 ESP 解密组合。**

## 3. 共享页标记与 ESP no-COW 分支

### TINNO 5.4.61 中的标记

- [`include/linux/skbuff.h`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/include/linux/skbuff.h#L3287-L3294) 有 `skb_has_shared_frag()`，其实现检查 nonlinear skb 的 `skb_shinfo(skb)->tx_flags & SKBTX_SHARED_FRAG`。
- `SKBTX_SHARED_FRAG` 在同一文件中定义，用于表示 frag 可能被外部实体（注释举例包括 `vmsplice()/sendfile()`）修改。
- 在审阅的 `udp_sendpage → ip_append_page → skb_append_pagefrags` 路径中，没有找到设置该标记的语句。
- `esp_input()` / `esp6_input()` 中也没有调用 `skb_has_shared_frag()` 的检查。

### IPv4 ESP 输入

[`net/ipv4/esp4.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/ipv4/esp4.c#L696-L775) 的 `esp_input()` 逻辑：

- 如果 skb 未克隆且为线性 skb，则跳过 COW；
- 如果 skb 未克隆、为 nonlinear 且没有 frag_list，也跳过 `skb_cow_data()`；
- 第二个分支没有额外检查 frag 是否由外部文件页支持。

因此，若某个实际到达 ESP 输入的 skb 同时具有“未克隆、nonlinear、无 frag_list、frag 页仍与外部文件页共享”等条件，该代码形态值得关注。**这些条件在本机 ESP 收包路径中是否同时成立，仍未被实机观测。**

### IPv6 ESP 输入的范围限制

[`net/ipv6/esp6.c`](https://github.com/TinnoOSS/P780/blob/20c26c7658cb5273cc71b10c3704b445b0efbe6b/msm-5.4/net/ipv6/esp6.c#L591-L665) 有类似的 ESP no-COW 分支。但本次检查的 TINNO `net/ipv6/udp.c` 未发现 `udp_sendpage` 或 UDP sendpage 注册。故不能把 IPv4 的旧式 UDP sendpage 调用链不加区分地推广到 IPv6。

## 4. 与上游修复的关系

上游修复提交：[f4c50a4034e62ab75f1d5cdd191dd5f9c77fdff4 — “xfrm: esp: avoid in-place decrypt on shared skb frags”](https://github.com/torvalds/linux/commit/f4c50a4034e62ab75f1d5cdd191dd5f9c77fdff4)。

该提交说明了两项防护原则：

1. IPv4/IPv6 数据报通过 `MSG_SPLICE_PAGES` 附加外部页面时设置 `SKBFL_SHARED_FRAG`；
2. ESP 输入在 no-COW 快速分支中增加 `!skb_has_shared_frag(skb)` 条件，避免对外部共享 frag 原地解密。

但 TINNO 5.4.61 的相关代码是旧式 `udp_sendpage/ip_append_page` 路径：审阅的相关文件中没有 `MSG_SPLICE_PAGES` 或 `SKBFL_SHARED_FRAG`，而使用较早的 `SKBTX_SHARED_FRAG` 表示法。**不能把上游提交的差异文本机械套到 5.4.61；应检查是否存在针对旧接口的等价回移植或厂商补丁。**

这也意味着，仅以“没有新 `MSG_SPLICE_PAGES` API”来排除旧内核风险并不充分；反过来，仅发现旧 sendpage 形态也不足以宣告 CVE-2026-43284 在该设备可利用。

## 5. 证据矩阵

| 命题 | 当前证据等级 | 结论 |
|---|---|---|
| TINNO 固定提交存在旧式 IPv4 UDP sendpage → IP page-frag 路径 | 直接源码观察 | 是 |
| 同一提交的 ESP4/ESP6 存在未克隆 skb 的 no-COW 分支 | 直接源码观察 | 是 |
| 所审阅的 IPv4 page-frag 路径设置了 `SKBTX_SHARED_FRAG` | 直接源码检查 | 未发现 |
| TINNO 5.4.61 与上游新修复涉及同类“共享页 + ESP 原地解密”风险 | 静态类比 | 值得核验，尚非漏洞裁决 |
| P780 v0.3 成功完成文件支持 UDP sendfile 回环 | 用户回传的实机输出 | 是 |
| P780 5.4.233 实际运行代码与 TINNO 5.4.61 对应函数一致 | 无匹配镜像/源码 | 未知 |
| P780 5.4.233 已有/没有等价修复回移植 | 无运行代码或对应源码 | 未知 |
| P780 的实际 ESP 输入路径满足所有共享页触发条件 | 无内核 trace / 无安全验证结果 | 未知 |
| DirtyFrag 可利用、可取得 Root | 没有 PoC 或 Root 证据 | 未证实，状态保持 `UNDETERMINED` |

## 6. 审计建议

这次审计说明 TINNO 5.4.61 **值得保留为候选实现模型**，尤其是 IPv4 旧式 sendpage 路径；它比“只因版本号较旧就放弃”更有研究价值。

下一步仍应优先寻找与 P780 `P780AE_11.0_RMN_JP_162` 匹配的 kernel Image、`vmlinux`、对应源码或 OTA/原厂固件，并检查 5.4.233 是否有对旧接口的等价安全修复。当前不运行利用载荷，不修改页面缓存，不加载模块、不刷写分区，也不把候选源码结论直接写成实机漏洞结论。

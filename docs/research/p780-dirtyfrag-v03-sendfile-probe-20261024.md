# P780 DirtyFrag：v0.3.0 文件支持 UDP sendfile 预检

日期：2026-10-24（Asia/Shanghai）  
状态：**CI 构建成功；机主已在 P780 实机运行第 4 项并回传 PASS。**

## 构建证据

- 功能提交：[ed24451](https://github.com/Chuniex-0631/p780-kernel-research/commit/ed24451a1be8927566bbbe77e0960b28747a97bb)；字符转义与诊断文本修正：[601b2ca](https://github.com/Chuniex-0631/p780-kernel-research/commit/601b2ca5a5123ce926895d06cf05bde7edb541e5)、[cfd015b](https://github.com/Chuniex-0631/p780-kernel-research/commit/cfd015b478abdd04f5659ce34ef4a6e667cd8560)、[2803127](https://github.com/Chuniex-0631/p780-kernel-research/commit/28031279664899a8c23a0e1ef5bc15a5d9236fa6)。
- APK 构建：[Actions run 40081265263](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40081265263)，success。
- Artifact：`p780-ipsec-preflight-debug-apk`，ID `12555411610`，ZIP digest `sha256:5cb93cc46acddaa3ed9be17381784b0974da61e044bcd1bf620e8f66ef5c0ea7`。
- 仓库完整性审计：[run 40081461177](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40081461177)，success。

## 设备端原始结果摘要（机主 2026-10-24 回传）

- Android API 30；设备 P780；内核字符串 `5.4.233-qgki-gea5245e94afe-dirty`。
- IPsec manager accessible。只读环境检查阶段没有分配资源、没有流量。
- 文件支持 UDP 回环：创建应用私有临时文件 1024 字节 PASS；一次 `sendfile(file → UDP loopback)` 返回 1024 字节 PASS；收到一个 1024 字节数据报且内容匹配 PASS；源文件发送前后字节完全一致 PASS；临时文件已删除。
- 本项没有启用 IPsec/ESP，没有尝试利用式页面缓存操作。输出明确声明它不建立 DirtyFrag 漏洞或 Root 证据。

## 结果解释

这证明机主回传的 P780 实机运行中，普通应用通过一次文件支持的 `sendfile()` 调用成功把 1024 字节传递到本机 IPv4 UDP socket，并正确收回数据。它比 v0.2 的普通 Java `DatagramPacket` 路径多覆盖了文件描述符数据源。

在 Linux 5.4.61 候选源码中，`sendfile → splice → sendpage → udp_sendpage → ip_append_page → skb_append_pagefrags` 是一条可读的旧式 IPv4 路径；这使该候选模型更值得审计。但设备输出不是内核 trace，不能独自证明 P780 5.4.233 运行时执行了每一个函数，也没有验证 ESP 解密与共享页的组合。

- v0.3 PASS **不等于** DirtyFrag 可利用。
- v0.3 PASS **不等于** 已证明 `udp_sendpage` 回调实际执行。
- v0.3 PASS **不等于** 漏洞已修复或不存在。
- 当前漏洞状态仍为 **DirtyFrag = UNDETERMINED；Root 未取得；Bootloader Locked**。

下一步是对 TINNO 5.4.61 候选源码进行只读静态审计，并继续寻找与 P780 `_162` / 5.4.233 对应的可信内核镜像或源码。不要重复 v0.2/v0.3 普通回环测试，也不运行 DirtyFrag/DFRoot payload。

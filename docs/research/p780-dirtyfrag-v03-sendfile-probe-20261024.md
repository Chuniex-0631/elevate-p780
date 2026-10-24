# P780 DirtyFrag：v0.3.0 文件支持 UDP sendfile 预检

日期：2026-10-24（Asia/Shanghai）  
状态：**源码与 APK 构建成功；尚未安装或在 P780 上运行。需机主单独确认设备执行。**

## 构建证据

- 功能提交：[ed24451](https://github.com/Chuniex-0631/p780-kernel-research/commit/ed24451a1be8927566bbbe77e0960b28747a97bb)；Java 转义修正：[601b2ca](https://github.com/Chuniex-0631/p780-kernel-research/commit/601b2ca5a5123ce926895d06cf05bde7edb541e5)。
- APK 构建：[Actions run 40080355011](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40080355011)，success。
- Artifact：`p780-ipsec-preflight-debug-apk`，ID `12555017495`，ZIP digest `sha256:0bcde8fcedc4a334026126c98f3a983f5f6c5d90d45abf49ec75005603695f6b`。
- 仓库完整性审计：[run 40080355002](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/40080355002)，success。

CI 只编译并上传 APK，没有连接或运行 P780。**v0.3 当前没有设备端结果**；不得把 v0.2 的 PASS 复制成 v0.3 结果。

## 第 4 项做什么

v0.3 增加独立 native 诊断：在应用私有 cache 创建 1 KiB 临时文件；打开只读 FD；创建仅绑定 `127.0.0.1` 的 UDP 收发 socket；**只调用一次** `sendfile(file_fd → UDP socket)`；接收并比对一个数据报；再次读取源文件确认字节不变；关闭资源并删除临时文件。失败时记录 errno，不重试。

此项不启用 IPsec、不创建 ESP Transform、不访问外网、不读取/修改系统文件、不构造畸形数据、不执行 DirtyFrag/DFRoot。

## 对 DirtyFrag 的价值与边界

v0.2 使用 Java `DatagramPacket`，已经实机确认普通 UDP 与 UDP-encapsulated ESP transport 回环成功，但没有用文件 FD 作为 UDP 数据源。v0.3 只检查普通应用是否能完成 file-backed sendfile-to-UDP 数据传递。Linux 5.4 的 sendfile 实现使用 direct-splice 路径，UDP 源码中也存在 `udp_sendpage`；因此该测试比 v0.2 更接近文件页到 UDP socket 的前置路径。

**限制：** 没有内核 trace，不能声称具体回调必然执行；本测试不把 sendfile 与 ESP 解密组合，不会验证共享页 COW/页面缓存写入原语。PASS 不证明 DirtyFrag，FAIL 也不是漏洞已修复的证据。

## 执行边界

- v0.3 APK **尚未安装或运行**。
- CI debug 签名可能与 v0.2 不同；若系统拒绝覆盖安装，需机主确认无待保留数据后再考虑卸载旧调试包。不要未经确认卸载。
- 若机主同意执行，先运行只读检查，再单独点击第 4 项；不需要重复第 2/3 项。
- 结果无论 PASS/FAIL 都只归档 sendfile-to-UDP 路径，不自动升级为 DirtyFrag 结论。

当前状态：**DirtyFrag = UNDETERMINED；Root 未取得；Bootloader Locked。**

# P780 静态修复核对与 Magic3 文章参考（2026-10-25）

范围：对已核验Image做离线修复存在性分析；不生成设备适配载荷、不操作手机。
输入SHA-256：`6df574af40d260c670c32bdee9ceaca023739850d62851d55f77234b89d4f373`。

## 公开修复与本机代码

Linux上游提交 [3bfdc63936dd](https://github.com/torvalds/linux/commit/3bfdc63936dd4773109b7b8c280c0f3b5ae7d349)
将remove_waiter的清理对象从current改为waiter所属任务。
依据为上游GitHub提交API返回的完整提交与差异，以及 [ARM64 v5.4 current.h](https://github.com/torvalds/linux/blob/v5.4/arch/arm64/include/asm/current.h)。
[发现方说明](https://nebusec.ai/research/ionstack-part-2/)用于交叉解释；不把版本范围声明直接转移为本机可利用性结论。

本机remove_waiter反汇编中，早期任务指针取自SP_EL0，随后同一来源用于加锁、队列处理后的清理及解锁，呈现旧式current处理语义；
没有在该清理位置观察到改为waiter所属任务的公开修复语义。
rt_mutex_start_proxy_lock仍存在对该清理函数的直接调用。已直接核对原始Image关键指令字节，未改写输入或应用运行时地址。

结论：**PUBLIC_FIX_SEMANTICS_NOT_OBSERVED_IN_AUDITED_CLEANUP_PATH**。
这是特定清理路径的静态修复核对，不是完整缓解措施审计，不排除未审路径的等价修复或其他约束，也不是GhostLock可在本机成功运行的证明。

证据：[摘要](../../evidence/kernel/20261025-static-patch-review/summary.json)、
[清理函数反汇编](../../evidence/kernel/20261025-static-patch-review/remove-waiter.txt)、
[调用者反汇编](../../evidence/kernel/20261025-static-patch-review/proxy-lock.txt)。
反汇编工具为此前构建环境的GNU AArch64 objdump 2.42，输入为字节保留分析ELF；地址为链接地址，非运行时地址。

## 用户提供的Magic3文章有什么参考价值

原文：[junyu33，Sixty-four](https://blog.junyu33.me/en/2026/09/24/xp3/)。
作者报告的对象是ELZ-AN00 / Android11 / 5.4.86-qgki，与P780同属旧5.4环境，但并非同构建。
文章有一部分技术总结直接引用其AI输出，本轮没有逐项独立复核其仓库或实机日志，因此作为第三方方法参考，不写成本机事实。

最值得吸收的检查要求：

1. 旧CFI机制与新机制不能混同；符号名称解码正确不等于每个跳板标签的目标语义已核验。
   本机恢复表含36,985个带.cfi_jt的名称；只确认名称存在，尚未逐项验证跳板目标，不能声称复现作者的符号问题。
2. 厂商配置会改变结构布局；同为5.4不能共用其他设备的布局或参数。
3. 静态链接位置不等于运行时位置；映射与重定位需分别理解。
4. UID、能力集合、SELinux域和实际操作结果需分别记录；UID0不能替代完整权限验证。
5. 模拟成功不能替代真机证据；文章设备的源码/固件/恢复资源不能直接用作P780材料。

对此前符号恢复结论的限定：全部173,205个名称/静态地址与原始表解码一致仍成立；
这不等于全部符号标签的语义正确，也不等于已恢复C结构体类型或运行时地址。

## 当前可写入状态的结论

- 镜像和符号使修复状态可以开始从二进制核验；本次相关清理路径仍呈现旧语义。
- Magic3文章增加了CFI标签语义、厂商布局、静态/运行时映射和权限分层的复核要求。
- 没有新增设备操作、Root、Bootloader解锁、永久写入或移植成功证据。

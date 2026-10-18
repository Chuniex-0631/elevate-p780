# P780 DSU 第十七轮：真实 Android 15 GSI 使用 AOSP 测试根密钥离线重签并通过 AVB 验证（2026-10-18）

> **历史阶段文档（2026-10-18收束）：DSU已停止。** B组后来已安装并尝试启动、最终回到原厂；本文的“未上机／下一步”限于当时阶段，不是当前指令。最新见[收束报告](p780-dsu-closure-maintenance-route-20261018.md)与[当前状态](../STATUS.md)。

> **结果层级：Windows PC 真正的 1.9GB system.img 经 avbtool 验证成功；尚未安装或启动自签名 DSU 镜像。** 本轮在聊天容器内独立读取并哈希机主上传的三份小文件、逐字段比较原始与新 AVB 元数据；镜像其余区域的逐字节不变来自电脑 v1.1 签名程序的强制分段哈希比较，因未上传1.9GB镜像，助手不能独立重算整镜像SHA。BL仍Locked，Root未取得。

## 直接收到的机主文件与独立 SHA-256

| 文件 | 原始长度 | SHA-256 |
|---|---:|---|
| original-avb-info.txt | 1549B | b7e4890bc061b2228d280bdbdd5a687db51ed9edfba403e10cec62293faa26e1 |
| testroot-avb-info.txt | 1549B | 507e7622f1ec036c338d1c1204ad75e331c004668bd0e606758e790d55714b9a |
| P780-DSU-testroot-audit.txt | 2206B | b8f6b9f836eb8b794650949cf3302bc95269c33b56be13c6ca04a1ff21f5774a |

真实报告中的输入 system.img SHA256：27321f9655530f014c884a690f49a53e6f3beeda71f4f27cbc141b17a8e86954。
测试根重签 system.img SHA256：fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880。
原版签名SHA256/e53f344beb2646b49651ea8dd336dbe75117183e96ef34beed4b367a4a0ae925（Q Developer GSI）；候选签名SHA256/7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6（AOSP RSA4096测试根，与P780本机TEE硬件证明根key hash相同）。

## 同一原始系统镜像：AVB元数据对照

| 项目 | 原版 | 重签版 |
|---|---|---|
| Public key SHA1 | 1ffb1af796b18ebf40d18faed213f686720f73f2 | 2597c218aae470a130f61162feaae70afd97f011 |
| 镜像总长 | 1899589632B | 相同 |
| 原始文件系统长度 | 1869524992B | 相同 |
| VBMeta offset / size | 1899151360 / 2432B | 相同 |
| 签名算法 | SHA256_RSA4096 | 相同 |
| Rollback index / location | 1743811200 / 0 | 相同 |
| AVB Flags | 0 | 0（没有关闭验证） |
| 系统版本/补丁 | Android15 BP1A.250405.005.C1 / 2025-04-05 | 相同 |
| hashtree offset / size | 1869524992 / 14725120 | 相同 |
| dm-verity data/hash block | 4096 / 4096 | 相同 |
| FEC roots / offset / size | 2 / 1884250112 / 14901248 | 相同 |
| system分区名/salt/root digest | system / a7d9494e95b60d6680b9fbb2464a5904245654e6d4130dde4899dda67275748a / 4a4ab356133df76a022da2ae9742f94a5d5e332635ca258bc76ff2dbe514695b | 相同 |

Python解析两份 avbtool info_image 输出中的28个主要数据字段、属性并排序比较，**除了Public key (sha1)，其它数值及属性均一致**。VBMeta 内嵌Prop/Hashtree descriptor的**排列顺序**在重新生成时改变，但各描述符内容相同，且排序变化仍位于独立的2432B VBMeta窗口内。

签名程序实现复核：Python先对源镜像0..1899151360前缀和1899153792..end后缀分别计算SHA256，复制原镜像到隔离 staging，仅替换VBMeta区间，并重新核对候选这两个区间的哈希与原版完全一致；成功后才执行最终 avbtool verify_image 并生成报告。用户电脑报告前缀SHA256=eaa3c42c482026264925118766b0e5d6fee99ed7392908e32a122c9ec94dcb96；后缀SHA256=dd05c1cdf01b89030aa1513c6f0d6ae02486af224621a45c25c36e5afb4bf4a9。**这是用户本地程序强制检测且报告成功的结论，非聊天环境对多GB镜像的再次哈希。**

报告中两次真实 avbtool verify_image 均成功：原版验证footer/签名VBMeta及sha256 hashtree；测试根密钥重签版本使用 testkey_rsa4096.pem 也同样成功。注意 verify_image 是本地密码学和镜像结构一致性自检，**不是**P780运行时信任链验证。

## 实验推论和关键限制

- A对照：原始 Google Android15 GSI system.img 被Q Developer GSI key签名，手机曾经尝试官方Android15 DSU并两次专用重启回原厂。
- B对照：**系统文件系统、verity树、FEC、Footer保持原版**，仅改嵌入式VBMeta签名密钥为AOSP Root Test key；离线verify成功。B**没有**安装进手机、没有启动尝试。
- Bootloader认可 AOSP Root Test key 不代表 standalone DSU fs_mgr/fstab 认可这把key。P780当前只通过文本证实普通 q/r/s-gsi.avbpubkey路径，公开三把普通GSI key均不同于测试根公钥；设备实际ramdisk额外公钥未取。即便B安装成功并单次回原厂，也无法单凭这次结果区分公钥不受信与GetActiveDsu/MapAllImages早退。
- AOSP官方说明 [DSU](https://source.android.com/docs/core/ota/dynamic-system-updates)：第一阶段需要信任与DSU系统镜像签名匹配的ramdisk公钥，Locked下校验不放宽。[DSU Sideloader官方README](https://github.com/VegaBobo/DSU-Sideloader/blob/master/README.md)：ADB/Shizuku模式调用原生安装器，可选img/gz/xz，ZIP仅原生DSU格式；它不是绕过AVB。Android11仅部分支持其某些功能。AOSP官方Android DSU需要受Google/OEM信任的签名。

## 下一步停线

已达成**本轮离线工具验收成功**；保留候选镜像 sha256 fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880，不要再重新下载或重签相同镜像。
优先尝试找到可信P780 _162 boot/ramdisk公钥字节。若用户明确希望继续上机，仅限经备份和Recovery最坏情形确认后的受控安装：先通过官方通知安全清理现有DSU（不能与旧实例叠加），再通过非Root DSU Sideloader选择**单张 system.img**，观察安装流程是否接收，在 Restart前停下截图/日志；**安装成功不意味着允许重启进入GSI，后续独立确认**。不修改Boot/VBMeta原厂分区，不使用Magisk/system或替换GSID模式。

**当前证实：真实Windows离线签名验证完成；当前不证实：Locked P780可安装/启动B、真实AVB公钥受信、Root或BL解锁。**

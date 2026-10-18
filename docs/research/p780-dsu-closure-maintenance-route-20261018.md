# P780 DSU 实机阶段收束与原厂维护接口路线（2026-10-18）

## 最新决策
2026-10-18 20:31（Asia/Shanghai），机主明确停止 DSU 路线，转向其它研究。停止重复安装、Restart、改签名和 DSU 参数试验。不能把“回原厂”写成“已证实厂商禁止 DSU”。

## 已验证与证据边界
- Windows A/B 均通过 avbtool 1.3.0 的 VBMeta/footer、Hashtree 自检；B 指定公开测试根密钥验签通过。Python 3.13.15，OpenSSL 3.5.7。
- A SHA256: 27321f9655530f014c884a690f49a53e6f3beeda71f4f27cbc141b17a8e86954。
- B SHA256: fd98af142b11263e997adba190810c544857c7b750fd905a663e87256a71d880。
- A/B 前1869524992字节系统数据SHA256相同：fe18355c1dc0d83aa9c9e5c0285e5a574c4706d3e7a31c35d12b1d4d619e7ef4。
- 上述整镜像和数据段摘要来自用户PC输出；助手未取得完整镜像独立重算。
- B经DSU Sideloader非Root ADB前端调用原生安装器，日志18:16:29为 READY / INSTALL_COMPLETED。启动前工具显示normal，bugreport为gsid.image_installed=0。
- 18:44:55原生通知触发ACTION_REBOOT_TO_DYN_SYSTEM，18:44:57记录Rebooting, reason: dynsystem。原厂APK只在setEnable返回成功后调用该重启；支持启用调用报告成功，不代表启动信任检查通过。
- 最终回到Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys，Locked=1，green，installed/disabled。启动后bugreport为gsid.image_installed=1、ro.gsid.image_running=0。
- 机主观察黑屏后疑似第二次重启，现有日志不足以独立确定重启次数。
- 没有获得失败启动的pstore/ramoops；/proc/last_kmsg不存在。当前原厂内核日志存在限流。不能区分公钥信任、映射、挂载、兼容性或更早失败。
- 随后机主恢复出厂并报告开发者选项原生DSU Loader仍在两次重启后回原厂；所选目录镜像身份、重置后是否做其它卸载未核实，属于用户观察，不能标成同一A镜像的严格复测。
- 无Root、无解锁、无永久分区写入成果。

## 原厂安装器静态审计
- DynamicSystemInstallationService.apk SHA256: 3015622f3fadb9575cd8521cf303fd3f304a6f1149d42269333e8b9bf3614260。
- framework.jar SHA256: 93944fb3db369e013cd5b744c749567f7e9b691cce226f6e6f1744a04476080c。
- services.jar SHA256: 0d93de73a06fca110c2826a92f243ea4afd7d4bf472f27649e0398995adf7345。
- APK的finishInstallation布尔返回值被忽略；services中该方法调用IGsiService.closeInstall并将非零转为false。不能证明本次返回false；启动后已安装证据减弱了“收尾失败”归因。
- 通知Restart先调用setEnable(true,true)，成功才reboot("dynsystem")；失败路径会移除DSU。
- /system/bin/gsid的adb pull被Permission denied拒绝，未绕过。gsi_tool已取得；不能替代服务端实现。
- 原始bugreport、证书、包含身份信息的日志不直接公开上传；保留在机主PC/会话。仓库保存脱敏结论。

## 收束后的研究去向

机主说明原厂维护/工程APK路线已做过且无线索，随后转为广覆盖静态取样。PC清单、batch1、batch2和SELinux原件分析已经完成阶段核验；不再把“收集原厂包清单/重做工程菜单”列为待办。当前入口是[native交叉矩阵](p780-native-interface-crosscheck-20261018.md)与[行动清单](../NEXT_STEPS.md)。

原厂镜像、匹配签名Loader和运行内核二进制仍缺；DSU失败阶段不明的结论保持不变，不恢复重试。

## 已有公开参考

- https://jvn.jp/en/jp/JVN47427200/ ：测试密钥问题，不提供本机已证实写入入口。
- https://www.android-device-security.org/publications/2025-leierzopf-spices/Leierzopf_2025_SPICES_AVBTestKeyInTheWild.pdf ：固件获取、重签和部署是不同前提，不能把其它机型演示当P780方案。

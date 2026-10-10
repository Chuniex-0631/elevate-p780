# 私人设备研究资料的隐私与安全

本仓库记录用户本人持有的 Rakuten Hand 5G P780。**Private 不等于可以随意提交机主隐私**。

请勿直接上传 IMEI、完整设备序列号、SIM 标识、电话号码、联系人、Wi-Fi/Bluetooth MAC、登录凭据、带 token 的下载地址或敏感 bugreport。对于大型 `hand5g_bugreport.zip` 和 `hand5g_getprop.txt` 应先做脱敏和用途筛选。

`archive/scripts/` 下的 PowerShell 去预装脚本会改变 Android 软件包状态，只作为历史存档，不代表推荐执行。其他机型源码编译所得的内核对象与 P780 出厂镜像不等同。

如果日后改为公开仓库，必须检查**整个提交历史和所有二进制附件**，仅删除主分支当前文件无法清除历史敏感记录。

研究成果主要针对离线源码与实机取证，当前未获得 root 或 bootloader 解锁。
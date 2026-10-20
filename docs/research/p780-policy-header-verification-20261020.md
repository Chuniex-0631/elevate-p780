# GAP-01 header 原件复核（2026-10-20）

结论：两份 PC 原件哈希与 10/19 归档一致；旧专题把 header config 的两端写反，现已纠正。独立 SETools 语义比较仍为 **BLOCKED_TOOLING**，不升级为运行策略完全等价。

## 直接核验

|输入|大小|SHA-256|offset 20 的四字节（小端）|config|
|---|---:|---|---|---|
|running-policy.bin|881104|a4d6851e984a0232dea7cbabbf600f87eeb74b94005a260ecbbca756bcad1409|01 00 00 00|0x1|
|disk precompiled policy|881104|77f077d8c95b38929aed0434c9c56ca6158c24d90c169ee2644d490684111b79|01 00 00 80|0x80000001|

独立脚本直接读取 magic、标识字符串长度和四个 header 字段，没有调用旧记录比较器。两者均 policy v30、8 个符号表、7 个对象表；config 异或为 0x80000000。结果见 [header-verification.json](../../evidence/gaps/20261020/header-verification.json)，工具见 [verify_policy_header.py](../../tools/gaps/verify_policy_header.py)。

原件只读使用，未修改或上传；Git 保存哈希和结果。原件路径沿用既有采集目录，不在结果中公开本地绝对路径。

## 源码对照与推断边界

Linux [v5.4 policydb.h](https://github.com/torvalds/linux/blob/v5.4/security/selinux/ss/policydb.h) 定义 MLS=1、REJECT_UNKNOWN=2、ALLOW_UNKNOWN=4。[policydb_read](https://github.com/torvalds/linux/blob/v5.4/security/selinux/ss/policydb.c) 用上述掩码读取 config；policydb_write 按已解析字段重新构造 config，不原样保留所有输入位。

因此，上游 5.4 的读写方式可以解释“预编译输入有额外高位，而运行导出没有”的现象；这是候选解释，不是本机厂商实现已核验。尚未确定该高位在本机 Android 构建工具链中的产生位置、定义或厂商处理逻辑，不能写成已证实无影响。

旧比较中各限定记录一致仍成立；它不包含独立 SETools 语义复核，也不证明 Binder/HIDL/文件操作实际可用。

## 独立工具检查与停止条件

本轮 Windows 检查：未找到 sediff/seinfo；Python 未安装 setools；wsl --list --quiet 失败并提示 WSL 未安装。没有安装 WSL、改变系统功能或上传策略到第三方主机。故本轮没有执行 sediff，不记录工具版本或虚构比较结果。

下一步仅在可用且获授权的独立 SETools/libsepol 环境就绪后，使用上述哈希对应的未改写原件，保存工具版本、完整命令、解析错误/警告与规则/属性/约束/转换差异；若原始高位导致拒绝，保留失败结果，不先归一化后宣称原件验证通过。若需归一化诊断，必须另存派生副本并单列其结论。

本轮未连接手机、重开 DSU、重复调用点扫描、读取已拒绝路径或尝试 Loader；Root/解锁/永久写入状态不变。

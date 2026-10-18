# P780 SELinux 原件审计：Journey 属性与诊断socket（2026-10-18）

## 输入身份与范围
P780-policy-20261018-222940.zip：SHA256 85f6d86d7d3d33ba940afacca6350527848ce07e29961ab92129ffcdb70a82a1，CRC通过。55份设备静态文件加pull.log，共56文件。五个目录pull退出0，但部分hwservice/mac permissions文件被跳过；不能称完整策略资料。

[逐文件哈希、查询矩阵和范围](../../evidence/static/20261018-222940/policy-audit.json)。

取得odm/precompiled_sepolicy（881104B），可对编译后策略执行SETools规则查询，避免只grep显式CIL而遗漏属性集合继承。原件不修改、不执行。使用SETools 4.4.4查询allow，未发现permissive类型。

重算plat/system_ext/product各自sepolicy.cil与mapping/30.0.cil串联SHA256，分别为：
- plat 414b99ceccbf367b8bef7cd414967a232575bad89c687453b152b80917168ca6
- system_ext 07579c332e2410b267f0aaf3e60f9d10693fd60213ebf1639591c283833bf025
- product 692f32b2d0e9e85b6836c64af246540f8b08ef7e9a46e3d5c83e7d70ffd99bbb

三者与分区配套摘要及ODM预编译策略记录全部一致。这支持磁盘策略配套身份，不是/sys/fs/selinux/policy实机运行策略的独立dump，也不替代OEM来源认证。

## 属性匹配与编译策略结果
按上传property_contexts的exact/最长prefix匹配：
| 属性族/目标 | 类型 | shell设置权限 |
|---|---|---|
| sys.journey.diag.*，含write_misc触发属性 | debug_prop | 编译策略allow |
| sys.journey.*，含restorecon触发属性 | debug_prop | 编译策略allow |
| config.write.*、persist.config.write.* | config_prop | 查询未发现allow |
| persist.vendor.diag.journey.enabled | vendor_default_prop（落在persist.vendor.） | 查询未发现allow |
| odm.journey.diag.*，含factory.reset | odm_journey_diag_prop | 查询未发现allow |

原始有效规则：allow shell debug_prop:property_service set;
platform CIL亦有同一显式规则。system_app、vendor_mmi_sys对debug_prop亦有allow；vendor_mmi可设置odm_journey_diag_prop。

已查询untrusted_app及_25/_27/_29，针对debug_prop/config_prop/default_prop/odm_journey_diag_prop/vendor_default_prop的property_service set均未发现allow。此结果限定指定域和权限；不包含其它应用域或某个高权限代理。

## 与上一批init交叉
system init原件包含sys.journey.diag.write_misc属性触发厂商write_misc动作，参数来自属性展开。sys.journey.restorecon触发restorecon_recursive。结合本批debug_prop映射和shell allow，这构成具体的**静态权限边界候选**，不是仅凭root/DAC的猜测。

仍缺少：
1. 对应init RC是否实际加载及厂商builtin是否注册；
2. write_misc/sync_file实现、参数限制、目标范围、错误处理；
3. 运行属性上下文和实际调用是否通过其它检查；
4. 从这些动作到镜像读取或Root的有效能力链。

不将shell可设置debug_prop扩写为任意文件写、任意分区写或Root。shell已有部分系统管理权限，敏感操作可达也不自动等于新增提权。

### socket方向降级
journey_diag_ext_system服务为root+disabled，init socket DAC模式0666。上传file_contexts没有匹配diag_ext_socket的专用条目，本轮未取得运行socket标签。
编译策略查询shell及untrusted_app/_27/_29到vendor_mmi_sys/vendor_mmi的unix_stream_socket权限均无allow；对socket_device sock_file亦无allow。
因此不能用0666认定可连接；本批不支持shell/普通应用直接连接该root socket。确切结论仍须运行标签，但不发送socket请求、不启动服务。

## 后续
优先离线取得init实现及Journey诊断服务原件，先读ls -lZ确认文件权限/标签。仅对尚未单文件读取过的目标做一次受限pull；拒绝即记录，不反复尝试、不改变权限。工程属性，特别write_misc/factory.reset，不用于试探；不写misc/boot/vbmeta、不触发Recovery、不启动诊断服务。DSU继续停止。

本轮无实机属性写入、提权、解锁或永久写入成果。新的实质进展是编译策略支持shell对Journey debug属性的设置权限，以及排除config.write/ODM reset/默认诊断开关的同等权限推断。

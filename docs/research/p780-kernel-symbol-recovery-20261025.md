# P780 内核符号恢复与独立核验（2026-10-25）

本轮只读处理机主提供的原始 Image，**恢复173,205个符号，全部名称及静态地址通过独立解码核对**；没有操作手机、执行载荷或评估具体漏洞利用能力。

## 输入与身份

输入41,767,424字节，SHA-256 `6df574af40d260c670c32bdee9ceaca023739850d62851d55f77234b89d4f373`。
内核构建字符串匹配既有实机记录；内嵌config.gz共39,170字节，SHA-256为
`0ff9cbb1844e043e1211b527509f5f435862cace25649bab6641d5d62c7bbce0`，与既有实机配置压缩字节一致。
[身份记录](../../evidence/kernel/20261025-symbol-recovery/image-identity.json)。

## 恢复与验证

使用 [marin-m/vmlinux-to-elf](https://github.com/marin-m/vmlinux-to-elf) PyPI 1.4.0定位kallsyms。
独立标准库脚本不导入第三方解析实现，核对原始镜像中的256个token、全部677个marker、
173,205个名称/类型及每项32位偏移；与导出结果逐项一致，地址非递减。
名称流恰好结束于marker表起点。

原始relative_base槽为0，由镜像中的R_AARCH64_RELATIVE重定位记录给出链接基准；
据此独立重算全部静态地址。_head/_text、linux_banner原始字节及内存边界符号提供额外交叉支持。
kallsyms数据表自身名称不在符号名称表中，没有冒称完成这些标签的地址校验。
发现位置来自第三方工具，因此独立的是解码验证而非第二种表发现算法。

- [完整验证](../../evidence/kernel/20261025-symbol-recovery/verification.json)
- [工具来源](../../evidence/kernel/20261025-symbol-recovery/tool-provenance.json)
- [工具定位日志及警告](../../evidence/kernel/20261025-symbol-recovery/recovery-tool.log)
- [验证/ELF工具与复现说明](../../tools/kernel-symbol-recovery/README.md)

## 完整性边界

文件末端恰为恢复的__bss_start；头声明内存长度43,540,480字节恰为_end相对位置。
差额1,773,056字节对应无需存入文件的BSS范围，不能仅据此认定截断。
符号和配置结构自洽，未发现这些方面的截断迹象；这不是所有代码字节未修改的密码学证明，
也不替代原始boot头、提取偏移与分块采集日志。

## 分析ELF

上游默认ELF生成会应用重定位并合成16MiB BSS，故交付另行生成的字节保留版本：
.image段与输入Image逐字节一致，BSS按本镜像边界设置。独立回读ELF中全部173,205个名称/地址对（包括重复名称），与符号文本完全相同；readelf解析通过。

交付`kernel.symbolized.elf` SHA-256：
`03e0cae1069e4581c652ef393f44fae0b04e23eeb7d9cecd27ede91c6d178591`。
[ELF验证](../../evidence/kernel/20261025-symbol-recovery/elf-validation.json) · [产物摘要](../../evidence/kernel/20261025-symbol-recovery/artifact-hashes.json)。

合成ELF只供分析：节划分/权限/类型映射为合成，函数大小置0，原始重定位未应用；
不是厂商debug vmlinux，不恢复DWARF/C结构体信息，不是boot.img，也不用于刷写。
完整符号和ELF随交付ZIP保存，Git只保存验证、工具和摘要。

## 结论与后续

“没有本机Image/符号”这一特定缺口已补上；静态链接地址不是实机KASLR地址。
结构体布局、修复状态与具体移植适用性仍需独立判断，不能从符号存在直接推出可Root。
本轮未生成设备利用profile、未运行GhostLock或修改设备状态。

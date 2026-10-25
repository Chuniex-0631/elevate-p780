# P780 内核符号恢复与独立核验（2026-10-25）

**结果：恢复 173,205 个 kallsyms 符号；全部名称及静态地址通过独立解码核对。**

输入为机主提供的 `kernel.Image`，41,767,424 字节，SHA-256：
`6df574af40d260c670c32bdee9ceaca023739850d62851d55f77234b89d4f373`。
版本和构建字符串匹配既有实机记录；内嵌 config.gz 的压缩字节 SHA-256 为
`0ff9cbb1844e043e1211b527509f5f435862cace25649bab6641d5d62c7bbce0`，也与既有实机配置一致。

## 交付文件

|文件|用途|
|---|---|
|kernel.kallsyms|173,205 行，格式为静态地址、符号类型、名称；保留同名符号和地址别名|
|kernel.symbolized.elf|带符号的分析用 ELF；.image 段逐字节保留输入 Image|
|verification.json|独立解码及范围核对结果|
|elf-validation.json|ELF 符号回读和原始字节一致性结果|
|image-identity.json|输入镜像、ARM64头与配置身份记录|
|recovery-tool.log|vmlinux-to-elf 定位过程及警告；重复的符号标准输出已省略，完整符号另存|
|verify_recovery.py|仅使用 Python 标准库的独立解码验证器|
|build_analysis_elf.py|字节保留的分析 ELF 包装器|
|tool-provenance.json|工具版本、来源与相关实现文件哈希|
|SHA256SUMS.txt|交付文件摘要|

## 方法与交叉核对

先用 [marin-m/vmlinux-to-elf](https://github.com/marin-m/vmlinux-to-elf) PyPI 1.4.0 定位并解码 kallsyms。
然后独立 Python 验证器直接读取原始 Image，不调用该工具的解析函数：

- 解出 256 个 token，并核对整个 token_index；
- 解出全部 173,205 个名称和类型，逐一与输出比对；
- 核对全部 677 个 marker；名称流恰好结束于 markers 起点；
- 从原始 R_AARCH64_RELATIVE 记录核对 relative_base，读取每个32位相对偏移，逐一核对静态地址；
- 地址非递减；所有符号都处于 Image 头声明的内存范围内（含末端符号）；
- 核对 _head、_text、linux_banner 与原始字节；_end 与头部 image_size 相符；
- 最终 ELF 生成后独立回读全部173,205个名称/地址对，包括重复名称；.image SHA与输入完全相同。

发现表位置来自第三方工具，因此这是**独立解码验证，不是独立定位算法**。
kallsyms自身数据表标签没有出现在恢复的名称表中，未冒称通过其标签交叉验证；这些表通过结构核对。

## 地址警告与 ELF 限制

恢复工具报告“相对偏移非负／看起来像绝对地址”的启发式警告，原样保留在日志。
本镜像的原始 relative_base 槽为0，由重定位记录填入静态链接基准。
独立核对确认：base+每项原始相对偏移，与工具输出全部一致；基准也通过镜像内字符串位置和边界符号交叉核对。
这些检查支持该静态映射，**不代表取得实机当前的KASLR地址**。

上游自动生成 ELF 会应用重定位并合成段，且默认附加16MiB BSS。为避免混淆，交付的是另行构造的
`kernel.symbolized.elf`：原始字节完全保留，BSS按本镜像边界计算；不把上游默认BSS当本机事实。
交付 ELF 的 .image/.bss、段权限、符号类型映射均为分析用合成信息，函数大小置0，不是原厂链接器的完整节表。
未应用重定位，文件内指针仍保持原始Image状态；分析时需理解其重定位记录。

它不是厂商原始debug vmlinux，不含恢复出的DWARF、源码行号或C结构体类型，不是boot.img，也不可用于刷写。

## 完整性发现

输入文件大小41,767,424字节，恰好等于恢复的 __bss_start 相对位置。
ARM64头声明的内存大小43,540,480字节，恰好等于恢复的 _end 相对位置。
差额1,773,056字节为该范围内未存入Image的BSS；不能仅凭“文件比头声明大小短”认定截断。
符号、配置和上述边界结构自洽，未发现这些方面的截断迹象。

这不是对来源的密码学认证，亦未证明每个代码字节未经修改。仍缺原始boot头、各块采集偏移及独立块哈希，
无法仅凭本次分析还原或认证提取过程。提取记录中的设备操作及回滚由机主报告，本轮没有操作手机。

## 复现

准备 PyPI `vmlinux-to-elf==1.4.0`（安装minilzo可能需要C编译器）：

```sh
CC=gcc python3 -m pip install --target analysis-deps vmlinux-to-elf==1.4.0
PYTHONPATH=analysis-deps python3 analysis-deps/bin/kallsyms-finder kernel.Image --output kernel.kallsyms > recovery-stdout.log 2> recovery-stderr.log
python3 verify_recovery.py kernel.Image kernel.kallsyms verification.json
python3 build_analysis_elf.py kernel.Image kernel.kallsyms kernel.symbolized.elf
readelf -h kernel.symbolized.elf
readelf -sW kernel.symbolized.elf
```

原始Image另行保管，未重复打包。本轮未进行漏洞修复状态判断、生成设备利用profile、执行载荷或取得Root。

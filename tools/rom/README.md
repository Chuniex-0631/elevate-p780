# P780 ROM Release 离线核验

此目录只有 **PC 本地离线工具**，不连接 ADB、不访问手机、不刷写或解包系统镜像。Python 3.8+ 标准库可用。

## 背景

Release `p780-rom-20261025` 的七个资产已经在 GitHub API 元数据层确认全部上传；要核验**实际二进制**，必须在 PC 上下载这些资产。参见 [ROM 审计](../../docs/rom/AUDIT-20261025.md)。

## 运行

把 `kernel.Image`、`meta1.tar`、`system.tar`、`system_ext.tar`、`vendor.tar`、`product.tar.part1`、`product.tar.part2` 放在同一个目录。

在仓库根目录运行：

```powershell
python tools/rom/verify_release.py "D:\\P780-ROM"
```

默认不写任何文件：校验七个 Release 资产真实 SHA-256 与文件大小；将两个 Product 分卷作为连续字节流计算 `product.tar` 的完整 SHA-256；读取五个 TAR 的条目元数据并逐项比较 `file-manifest.txt`，检测缺失、重复、意外路径及文件大小问题。**不会提取文件内容到磁盘**。

如确实需要生成完整 `product.tar`，使用：

```powershell
python tools/rom/verify_release.py "D:\\P780-ROM" --merge-product
```

输出应新建 `D:\P780-ROM\product.tar`，预期 **3,258,192,896** 字节。若该文件已存在，工具拒绝覆盖并验证它是否与分卷顺序拼接一致。

最终只有在七个 Release 文件、完整 Product 和五个 TAR 条目检查全部通过后才打印 `SUCCESS`。任何缺失文件或不匹配均返回非零退出码。首次完整扫描涉及约 5.7 GB 数据，运行用时取决于磁盘速度。

## 边界

- GitHub 返回的 SHA-256 元数据与本机重新计算的 SHA-256 是不同证据等级；最终需要本地输出日志。
- TAR 头/普通文件元数据一致及整体 SHA-256 一致，可以证明与已记录归档字节相同；不能补出采集时已被拒绝的文件，也不能把 TAR 变成可刷写 IMG。
- 工具从不执行 TAR 成员、不还原符号链接、不提取文件。若要进一步读取内容，必须在隔离目录中单独处理，先考虑私有数据与厂商文件许可。
- 该脚本通过模拟的小型 TAR fixture 检查，但截至本次提交，没有在真实 Release 的全部字节上运行；不要把工具存在当成结果已 PASS。

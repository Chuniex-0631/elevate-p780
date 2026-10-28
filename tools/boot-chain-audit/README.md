# 启动链离线复核

只读取本地保存的普通文件，输出 JSON 到 stdout。没有 ADB、USB、网络、设备节点读取、payload 生成、写盘或切槽功能。不会执行仓库内的 payload 生成器。

```bash
python tools/boot-chain-audit/audit.py
python tools/boot-chain-audit/audit.py --root /path/to/repo --log /path/to/saved-update.log
python -m unittest discover -s tools/boot-chain-audit -p test_audit.py -v
```

第一条命令从仓库提取 RC 双版本声明、VINTF fragment、静态 HAL 客户端/存储权限、历史 fastboot 槽状态、ABL 字符串及测试块生成器的源码行。缺失输入列入 missing，不能当作负证据。

可选 --log 只提取开关、错误码和特定失败事件的行号，不输出原始日志/URL，也不自动判断切槽成功。同一个文件可能含多次更新或不同 boot，必须先人工按会话划分；未见成功日志不判 no-op。输出仍需检查后再公开，不代表通用脱敏器。

哈希针对实际读取的本地字节。如果输入来自连接器转换的 UTF-8 视图，不能把它当成原始设备文件或 Git blob 的字节身份。

结果与下一步见 [启动链复核](../../docs/research/p780-boot-chain-review-20261028.md)。

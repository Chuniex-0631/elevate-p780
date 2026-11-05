# 内核配置与候选结构

归类后的规范入口：`summarize_config.py`、`audit_missing_config.py`、`derive_candidate_layout.py`、`compare_candidate_layouts.py`、`p780-layout-probe.c`。旧根目录路径保留兼容入口。

这些工具分析本地配置、候选源码和离线构建结果，不连接设备。Python 脚本仅依赖标准库；结构测量另需脚本中声明的候选源码、Kbuild 输出及匹配工具链，参见 `.github/workflows/p780-layout-audit.yml`。

```sh
python tools/kernel-config/derive_candidate_layout.py --help
python tools/kernel-config/audit_missing_config.py --help
```

`summarize_config.py` 接受原始、解析后、编译后配置和报告目录四个位置参数。比较与测量只说明候选源码，不认证实机地址或 ABI。

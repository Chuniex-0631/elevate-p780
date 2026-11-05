# Journey 离线分析

规范入口：`compare_journey_config.py`（标准库）、`scan_journey_framework.py` 与 `read_performance_dex.py`（需 androguard、loguru，版本及输入依据历史报告）。旧根目录路径保留兼容转发。

只读取本地导出的 XML、TCS、JAR / DEX，并写入本地衍生报告；不连接手机。DEX 脚本保留历史输入约定，从调用目录查找 `framework-audit/`，缺少原始材料时不能据此重建采集事实。

```sh
python tools/journey/compare_journey_config.py --help
```

相关证据和方法见 [Journey 边界报告](../../docs/STATUS.md)。移入本目录未更改算法或扩大设备端能力。

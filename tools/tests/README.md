# 维护测试

```sh
python -m unittest discover -s tools/tests -v
```

Python 3.11+ 标准库，无第三方依赖、联网或设备操作。涵盖损坏输入、相对链接、优化模式、调用目录独立性、排序稳定性与仓库结构迁移校验。使用临时目录和本地 Git 文件。

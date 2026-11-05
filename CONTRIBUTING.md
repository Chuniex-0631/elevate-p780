# 贡献与维护

## 环境

仓库维护使用 Python 3.11+ 和 Git，支持 Windows、Linux。维护脚本仅处理本地文件，不连接设备。研究工具、Android 应用与历史构建工作流各有额外依赖，不由维护检查自动执行。

## 日常流程

1. 原始证据放入 `evidence/`，保留字节与来源；需要脱敏时另存副本。
2. 在 `docs/research/` 编写报告。结论变化时，依据证据更新 STATUS 和 NEXT_STEPS；重排前保留历史快照。
3. 用 `git add` 将新增文件纳入跟踪。生成器仅索引 Git 跟踪的文件，不收录本地临时产物。
4. 执行以下命令，并将生成的文档一并纳入提交：

```sh
python tools/build_research_index.py
python tools/build_research_index.py --check
python tools/verify_repository.py
python -m unittest discover -s tools/tests -v
python -m unittest discover -s tools/boot-chain-audit -p "test_*.py" -v
```

上述维护工具可从任意工作目录按完整脚本路径运行。`--output` 的报告路径相对于调用目录；建议输出到忽略的 `reports/`。生成器不写入证据目录；`--check` 不写文件。

## 检查范围

- `verify_repository.py`：已跟踪 Python 语法、JSON、Markdown 本地文件链接，以及既有 Journey 压缩包、字节码摘要和历史迁移对象身份校验。失败返回非零退出码，Python `-O` 不会禁用证据检查。
- `build_research_index.py --check`：重新计算全部已跟踪证据的 SHA-256，与生成清单比较；同时检查文档索引是否最新。没有历史摘要的新证据须由报告说明来源，生成清单本身不证明其真实性。
- 维护测试：损坏输入、工作目录独立性、临时文件排除、生成结果确定性。
- CI：Windows / Linux、Python 3.11 / 3.13，自动执行维护检查与启动链离线测试。其他历史工作流保留原有用途。

不检查 Markdown 标题锚点或公网链接，不证明设备端成功、利用效果、权限扩大或跨重启持久性。研究工具不因通过仓库检查而获得实机有效性认证。

## 文件约定

- UTF-8 文本；原始证据使用 `.gitattributes` 禁止换行转换。
- 不移动或重命名原始材料以美化目录，避免破坏引用链。
- 每个工具目录提供 README，说明依赖、输入输出、是否改变设备、恢复方式和已知限制。
- 新增或调整工具时，更新 `tools/README.md`。更改研究结论必须有对应证据，不以代码改动代替验证。

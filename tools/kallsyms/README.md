# kallsyms 提取

从裸 `Image` + `/proc/kallsyms` 还原内核符号表。配套说明见
[`docs/research/p780-kernel-image-extraction-20261025.md`](../../docs/research/p780-kernel-image-extraction-20261025.md)。

```bash
python extract_symbols.py kernel.Image kallsyms_full.txt symbols.txt
```

原理：`/proc/kallsyms` 保留内核符号顺序（地址可能被 `kptr_restrict` 置零），
而 `Image` 里的 `kallsyms_offsets` 是长单调 u32 数组；把第 i 个名字与
`offsets[i]` 配对并校验单调性即可还原偏移（以镜像起点为基准）。

注意：本机 `CONFIG_CFI_CLANG=y`，函数符号带 `$<hash>` 后缀并有 `*.cfi_jt` 跳板，
按裸名查不到时必须用带后缀的名字。

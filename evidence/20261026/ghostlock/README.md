# GhostLock 5.4 反汇编

- `do_futex.txt`、`futex_wait.txt`、`restore_sigframe.txt`、`restore_sigframe_full.txt`。
- 结论：pselect waiter word 15、sigreturn off -0x118；公开车辆判负，见 `docs/research/p780-ghostlock-5.4-20261026.md`。

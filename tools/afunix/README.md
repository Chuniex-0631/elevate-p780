# CVE-2024-26923 触发 harness

- `poc_26923.c` / `poc_26923`：AF_UNIX GC vs connect() 竞态触发，**不是 exploit**。
- 只验证能否触发；成功时可能 panic/reboot；每次重启后只跑一次。
- 实测两轮 30s 未触发，见 `docs/research/p780-afunix-cve-2024-26923-20261026.md`。

# Candidate source layout comparison

Run: https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38060466663

**Offline source measurement, not a certified layout of the running P780.**

| Source | Extraction result |
|---|---|
| tinno-5.4.61 | 31 measurements |
| a52s-5.4.233 | 31 measurements |

| Fact | TINNO 5.4.61 | A52s 5.4.233 | Same? |
|---|---:|---:|---|
| CRED_SECURITY | 120 | 120 | True |
| CRED_SIZE | 168 | 168 | True |
| CRED_UID | 4 | 4 | True |
| CRED_USAGE | 0 | 0 | True |
| FILE_F_COUNT | 56 | 56 | True |
| FILE_F_OP | 40 | 40 | True |
| FILE_SIZE | 272 | 272 | True |
| FOPS_IOCTL | 80 | 80 | True |
| FOPS_SIZE | 288 | 288 | True |
| MM_PGD | 72 | 72 | True |
| MM_SIZE | 912 | 912 | True |
| PAGE_FLAGS | 0 | 0 | True |
| PAGE_SIZEOF | 64 | 64 | True |
| PAGE_SLAB_CACHE | 24 | 24 | True |
| PIPE_BUFFER_OPS | 16 | 16 | True |
| PIPE_BUFFER_PAGE | 0 | 0 | True |
| PIPE_BUFFER_SIZEOF | 40 | 40 | True |
| PIPE_INFO_BUFS | 120 | 120 | True |
| PIPE_INFO_SIZE | 136 | 136 | True |
| REFCOUNT_SIZE | 4 | 4 | True |
| RTMUTEX_SIZE | 32 | 32 | True |
| TASK_COMM | 2120 | 2120 | True |
| TASK_CRED | 2104 | 2104 | True |
| TASK_PID | 1664 | 1664 | True |
| TASK_PI_BLOCKED_ON | 2352 | 2352 | True |
| TASK_PI_LOCK | 2316 | 2316 | True |
| TASK_REAL_CRED | 2096 | 2096 | True |
| WAITER_LOCK | 56 | 56 | True |
| WAITER_SIZE | 80 | 80 | True |
| WAITER_TASK | 48 | 48 | True |
| WAITER_TREE | 0 | 0 | True |

0 of 31 measured facts differ.

Equal numbers do not prove source identity or runtime equivalence. Differences mix version, vendor and configuration changes.

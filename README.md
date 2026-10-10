# P780 Kernel Research (offline, no device flashing)

This private repository holds reproducible, **research-only** analyses for the Rakuten Hand 5G P780. It is **not** a P780 boot image, exploit package, or an assertion of a vulnerable running kernel.

## Verified milestones (2026-10-10)

| Run | What was tested | Verified outcome |
|---|---|---|
| [#38052323798](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38052323798) | Android/Qualcomm 5.4.233 candidate, ARM64 `olddefconfig` + `rtmutex.o`, Ubuntu Clang 14 | Success, compile output is LLVM bitcode |
| [#38053251640](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053251640) | Exact diff based on the above run's original and resolved configuration | 2 compiler-version changes, 24 removed symbols, 327 added, 44 newly enabled |
| [#38053176845](https://github.com/Chuniex-0631/p780-kernel-research/actions/runs/38053176845) | Google Android Clang **11.0.2, r383902b1**; real P780 configuration; ARM64 Kconfig; compile `rtmutex.o` | **All steps succeeded**. 0 changed values, 24 removed symbols, 322 added symbols, no compilation-stage config drift |

Candidate Qualcomm source: `arminask/linux-android-samsung-a52sxq`, `droidian` commit `1f58b196e0dc8de740eb45b51261ea9c5741a30e`, reporting Linux 5.4.233.

Pinned Google Clang prebuilt repo commit: `659f7cadd7ec920e470bffbb799b031d4344c8d9` from branch `android11-qpr2-release`, directory `clang-r383902b1`.

Device configuration: `p780-config.gz`, SHA-256 `0ff9cbb1844e043e1211b527509f5f435862cace25649bab6641d5d62c7bbce0`.

## Why this is NOT a faithful P780 kernel reconstruction

1. The candidate tree is based on **Samsung A52s**, not the P780's exact shipping firmware.
2. The original P780 config had 24 symbols absent in the candidate tree: **15 were active** (`y` or `m`). They include TINNO charge-control drivers, SAR/fingerprint code, and `CONFIG_FORTIFY_SOURCE`/`CONFIG_REFCOUNT_FULL`. These must not be silently dismissed.
3. The candidate introduces hundreds of additional symbols (including Samsung-specific functions).
4. Building `rtmutex.o` under LTO produces an intermediate object, not a linked `vmlinux` and **not a source of trustworthy runtime symbol offsets**.
5. The native Kconfig emitted warnings including conflicting Samsung declarations and `REGMAP` dependencies. Success means the processing and compilation stage returned exit code 0, not that every dependency is harmless.
6. The running P780's vulnerability status is **unverified**. No runtime exploit execution or bootloader unlock is claimed.

## Next research gate

- Identify P780-specific source/config features missing from the candidate and categorize their relevance to any planned **full** research-only kernel build.
- Optionally compile further isolated core locking/futex objects with the matched Clang, without claiming firmware provenance.
- Seek authentic P780 firmware binary and exact OEM kernel revisions for any binary-layout comparison; don't guess or reuse A52s offsets.
- All activity remains read-only w.r.t. the phone; **never flash cross-device images**.

## Reports and source of truth

Open the workflow runs above and download the artifacts at the bottom of each run's page:
- `p780-android-clang11-audit` contains Clang version, original/resolved config, precise config drift JSON and raw build logs.
- `p780-exact-config-delta` contains the explicit 24 missing symbols and 44 newly enabled symbols from the Clang 14 baseline.

No WSL or local Linux setup is required on the user's PC.

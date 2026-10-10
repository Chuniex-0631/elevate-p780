# Candidate layout audit evidence

Final complete run: [38060518994](runs/38060518994/layout-comparison.md). Both source trees produced all 32 requested measurements; all 32 matched. This does not certify the ABI of the running P780 or supply runtime addresses.

- `source-audit/`: actual references for 24 removed config symbols and core header differences.
- `runs/38060518994/`: complete final probe, build logs, configs and comparison.
- `runs/38060466663/`: intermediate 31-fact probe, missing task_struct size due to TASK_SIZE macro collision.
- root `builds/` and root `layout-comparison.*`: initial run 38060293186, TINNO mode failure and partial A52s probe. Preserved as historical evidence, not the final result.
- `LATEST.txt`: last archived run ID; each run remains separate.

See [research report](../../../docs/2026-10-10-config-layout-research.md) for scope and conclusions.

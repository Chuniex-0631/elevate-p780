# Official Rakuten Hand 5G firmware authenticity advisory (2026-09-28)

## Verified statement

Rakuten Mobile publicly states that, **as of September 28, 2026**, it had identified a vulnerability in Rakuten Hand 5G's process for verifying firmware authenticity. The advisory says altered firmware may be incorrectly recognized as genuine. It describes a scenario where someone who can temporarily operate the device might install modified firmware, potentially enabling privilege acquisition, unauthorized programs, or device setting changes.

Original Japanese advisory (primary source):
https://network.mobile.rakuten.co.jp/product/smartphone/rakuten-hand-5g/support/index.html

Rakuten Mobile lists product support as ended **2025-12-31**, and advises against continuing to use the product. This is a security notice, not a research instruction.

## Research implications and strict unknowns

- This may be **more relevant to the boot-chain** than GhostLock's Linux RT mutex path, but the public advisory does **not** identify the affected verification stage.
- It does **not** establish that the Android bootloader can be unlocked or that an arbitrary image can be flashed from Android userspace, recovery, fastboot, or EDL.
- It does **not** identify a CVE, vulnerable firmware build range, patch status, exploit procedure, or signature-verification bypass details in the currently reviewed public text.
- It is distinct from CVE-2026-43499 / GhostLock; no causal connection between those bugs has been established.
- Do not interpret a device-specific firmware-verification advisory as permission to use cross-device images or risk a hard brick.

## Safe next research tasks

1. Search for a vendor/JVN advisory with technical details, affected firmware versions, and public remediation status.
2. Obtain authentic, unmodified firmware images or OTA payloads for the P780, preferably **P780AE_11.0_RMN_JP_162**, only from attributable sources; preserve hashes and provenance.
3. Offline-only: map the device's normal AVB/boot chain configuration from official documentation and authenticated images before drawing conclusions.
4. Never flash or erase partitions based on a different handset's `vmlinux` or the Samsung candidate's symbols.

This is a distinct research track, not a verified rooting method.

# Google OTA Prober × Rakuten Hand 5G (P780) | 2026-10-18

> Status: upstream source audited, comparative Rakuten/Tinno OTA metadata confirmed; no P780 query has been sent, no P780 OTA URL/image obtained. This is not a root/unlock result.

## P780 evidence (user's console, not a separately attached transcript)

- `ro.build.fingerprint=Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`.
- Existing build baseline: `P780AE_11.0_RMN_JP_162`; the fingerprint incremental `264` is NOT the firmware suffix `_162`.
- `/vendor/etc/fstab.default` and `/vendor/etc/fstab.emmc` exist; `/vendor/etc/fstab.qcom` returned file-not-found. Neither existing file was read in this turn.

## Upstream implementation

- [google-ota-prober](https://github.com/tangalbert919/google-ota-prober): read its [README](https://github.com/tangalbert919/google-ota-prober/blob/master/README.md), [probe.py](https://github.com/tangalbert919/google-ota-prober/blob/master/probe.py), and [utils/functions.py](https://github.com/tangalbert919/google-ota-prober/blob/master/utils/functions.py).
- Parses the fingerprint; constructs Google AndroidCheckinRequest protobuf with `fetchSystemUpdates=1`; calls `POST https://android.googleapis.com/checkin`; prints `update_url` if present. This is a Google OTA lookup, NOT a universal vendor/firmware search engine.
- By default, constructs synthetic random serial, IMEI and Wi-Fi MAC; does not require a real phone ID. Still transmits fingerprint, synthetic IDs and request metadata to Google. Do not add real IMEI/serial/account credentials. Creates `test_data.gz` in working directory.
- No ADB, bootloader or flashing operations in CLI `probe.py`. `--download` triggers actual file download; OMIT initially.
- README caveats: requires OEM to distribute through Google's OTA servers; usually returns the next incremental OTA, if any; currently-installed `_162` is last known official P780 version, so no update for current fingerprint cannot prove Google was never used.
- [Issue #5](https://github.com/tangalbert919/google-ota-prober/issues/5) describes even a latest fingerprint retrieving an older OTA. Validate package metadata (`pre-build`, `post-build`, device), do not trust URL/title alone.

## Stronger comparator from public archive

- The [mouseos/ota-archive](https://github.com/mouseos/ota-archive) has [Rakuten C330](https://github.com/mouseos/ota-archive/blob/main/OTA/Google/rakuten/c330/index.json) **real Google OTA metadata**: `530→620` (254,605,505 bytes), `620→830` (208,584,539 bytes), with `preBuild/postBuild`, Android Google OTA package URLs, archive backups, and incremental type. These are archive records; we have not fetched and reverified the packages.
- Rakuten's [Mini manual](https://network.mobile.rakuten.co.jp/assets/pdf/product/Rakuten-Mini-manual.pdf) identifies C330 as Rakuten Mini and Shenzhen Tinno as its maker, giving OEM/brand relevance but NOT proof the later P780 reused the same server.
- The [Tinno P710 index](https://github.com/mouseos/ota-archive/blob/main/OTA/Google/tinno/p710/index.json) includes a Rakuten Hand fingerprint but has `firmware: []` (no archived package).
- A direct listing of the archive's `OTA/Google/rakuten/` and `OTA/Google/tinno/` namespaces shows NO `p780` folder. This is only a coverage gap in that archive, not proof of no P780 Google OTA.
- Official [Rakuten P780 update notice](https://network.mobile.rakuten.co.jp/information/software/rakuten-hand-5g/) lists `_162` from 2024-03-21. A truthful older build fingerprint (`_161`, etc.) would be more informative for the next-update check than the already-current `264`, but it must be obtained from real evidence, never guessed by editing `264`.

## One optional, PC-only query (user has not performed it)

```powershell
git clone https://github.com/tangalbert919/google-ota-prober.git
cd google-ota-prober
python -m pip install -r requirements.txt
python probe.py --fingerprint "Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys" --model P780
```

Do not provide real device identifiers, enable `--download`, run batch fingerprint guesses, upload `test_data.gz`/full debug logs, or install any returned OTA. A URL requires source validation and offline inspection; a negative response is inconclusive. If an incremental package is found, check whether `vbmeta` and `boot` operations independently provide usable complete partition data; a delta can require the exact older base image.

## Correct fstab next step

```powershell
adb shell cat /vendor/etc/fstab.default
adb shell cat /vendor/etc/fstab.emmc
```

Inspect `avb=...`, `logical`, `first_stage_mount`, and `slotselect` to infer declared AVB mount configuration. Merely existing does not prove either file is the active first-stage fstab; `.emmc` in a filename does not establish eMMC storage (historical device evidence indicates UFS).

## Priorities / scope

1. One conservative Google check-in query, or passive discovery of a genuine older P780 fingerprint.
2. Read only the two discovered fstab files; continue independent hardware Key Attestation exploration.
3. If a verified P780 OTA appears, analyze only offline `metadata`/`payload.bin`/`vbmeta`; distinguish full vs incremental and no-write vs installation.
4. Original `_162` images and a verified locked-state write channel remain absent. Root and unlock not achieved.

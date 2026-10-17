# Google OTA Prober × Rakuten Hand 5G (P780) | 2026-10-18

> Status: upstream source audited; user **ran one P780 CLI query** using the exact stock fingerprint and received **no OTA URL**. Rakuten/Tinno comparative metadata is confirmed; still **no P780 OTA URL/image**, root or unlock result.

## P780 evidence (user's console, not a separately attached transcript)

- `ro.build.fingerprint=Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys`.
- Existing build baseline: `P780AE_11.0_RMN_JP_162`; the fingerprint incremental `264` is NOT the firmware suffix `_162`.
- `/vendor/etc/fstab.default` and `/vendor/etc/fstab.emmc` were subsequently both **read successfully** in the user's attached console transcript; `/vendor/etc/fstab.qcom` returned file-not-found. Both real files agree on AVB grouping. See [P780 fstab AVB evidence](p780-fstab-avb-20261018.md).

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

## PC-only P780 query (completed; no URL)

```powershell
git clone https://github.com/tangalbert919/google-ota-prober.git
cd google-ota-prober
python -m pip install -r requirements.txt
python probe.py --fingerprint "Rakuten/P780/P780:11/RKQ1.210715.001/264:user/release-keys" --model P780
```

**Observed 2026-10-18 result (user-provided):** `No OTA URL found for your build. Either Google does not recognize your build fingerprint, or there are no new updates for your device.` The program did not print HTTP status; this proves only that no `update_url` was reported. As `_162` is the most recent official firmware, the result has low discriminatory power regarding historical Google OTA use. **Do not repeat this exact query without new evidence.** Do not provide real device identifiers, enable `--download`, run batch fingerprint guesses, upload `test_data.gz`/full debug logs, or install any returned OTA. A future URL requires source validation and offline inspection; this negative response is inconclusive. If an incremental package is found, check whether `vbmeta` and `boot` operations independently provide usable complete partition data; a delta can require the exact older base image.

## Fstab readings (completed)

Both files were read from P780 by the user. They agree: `system`, `system_ext`, `product` use `avb=vbmeta_system`; `vendor` and `odm` use plain `avb`. System also lists GSI key paths `/avb/q-gsi.avbpubkey`, `/avb/r-gsi.avbpubkey`, `/avb/s-gsi.avbpubkey`, which are **not confirmed production root keys**. See [detailed live fstab analysis](p780-fstab-avb-20261018.md). They differ in `/data` encryption options; the active first-stage fstab selection is not proven.

## Priorities / scope

1. Google check-in with final build is **completed without URL**. Only revisit on discovery of a genuine old P780 fingerprint / new OTA server evidence; no repeated current-build query.
2. Both discovered fstab files are **read and analyzed**; next meaningful untested path is hardware Key Attestation.
3. If a verified P780 OTA appears, analyze only offline `metadata`/`payload.bin`/`vbmeta`; distinguish full vs incremental and no-write vs installation.
4. Original `_162` images and a verified locked-state write channel remain absent. Root and unlock not achieved.

## GUI calling-convention pitfall (source observation)

The current upstream `gui.py` calls `prober.checkin(fingerprint.value, model.value, serial.value, imei.value, timestamp.value)` positionally, but `probe.py` defines `checkin(fingerprint, model=None, debug=False, serial=..., imei=..., timestamp=0)`. Thus GUI fields are shifted: GUI serial enters `debug`, GUI IMEI enters `serial`, GUI timestamp enters `imei`, and `timestamp` stays at the default. This is an **unverified runtime bug inferred from the directly inspected source**, not a test run. Prefer the documented CLI with a quoted fingerprint for the first P780 query, and leave real identifying values out. Do not infer failure from GUI behavior.

## 2026-10-18 外部 AI 提供的旧指纹探测与签名建议核查

**实用部分：** 取得有来源的旧版 P780 Android 完整 build fingerprint 后，可以用 Google OTA Prober 尝试查询该历史源版本的下一更新；目前掌握的 264 是 `_162` 对应设备的 fingerprint incremental，不代表其它厂商 `_161/_151` 可以代入 161/151。

**源码核验：** 上游 probe.py 支持 --fingerprint、--model、--config、--timestamp 等，不支持 --device、--source_fingerprint 或 --target_fingerprint；配置为 config.yml 而非 devices.json。直接将 264 改为未经验证的 151/120 不是使用真实旧版 fingerprint，也没有指定目标 OTA 的功能。

**Google URL 有效期：** 关于通常几小时过期、使用短期 Token 及固件必然永久保留的断言，本轮既没有可靠 HTTP 样本也没有官方适用规则，不能拿它解释本机无 OTA URL。

**增量 payload 限制：** AOSP [update_engine](https://android.googlesource.com/platform/system/update_engine/) 说明 Delta payload 的 SOURCE_COPY/SOURCE_BSDIFF 等操作依赖旧版源分区块；[OTA 构建文档](https://source.android.com/docs/core/ota/tools) 区分 Full 和 Incremental。不能保证所有下载的 payload.bin 都可直接解出完整 boot/vendor/system。对于每个分区应独立检查其操作类型。

**签名机制严重误解：** AOSP [SignApk](https://android.googlesource.com/platform/build/+/79f56d876c721a0404cd50664a7f9da693d1e757/tools/signapk/src/com/android/signapk/SignApk.java) 用于 APK/JAR/OTA ZIP 包签名；启动链中的 vbmeta、hash/hashtree、链式分区与校验签名由 [AVB libavb/avbtool](https://android.googlesource.com/platform/external/avb/+/android11-release/README.md) 负责。对 Magisk 修改的 boot.img 使用 signapk 并不会生成合格的 AVB 签名链，也不解决 locked Bootloader 镜像写入。

**新旧版 OTA 历史实证：** [楽天社区 2024-07-31 P780 161→162 问题帖](https://community.mobile.rakuten.net/questions/x933grdoe6mhntuf) 记录了真正 `_161` 手机当时显示“アップデートを利用できます”，却无法安装 `_162`。这证明当时存在更新提示，不提供完整历史 Android fingerprint、OTA 链接或分发服务器证明，更不能认定就是 Google GOTA。

**决定：** 暂不伪造旧 build fingerprint、不批量扫描、不使用 signapk 作为 AVB 重签刷机流程。优先寻找可追溯的旧版 P780 完整 fingerprint/OTA metadata，或按独立专题研究 Android Keystore Key Attestation。Root 和解锁仍未实现。

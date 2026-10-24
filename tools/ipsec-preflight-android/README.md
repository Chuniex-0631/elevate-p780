# P780 / Android 11 IPsec preflight (non-exploit)

Status: source-level diagnostic only; no device test has been performed.

This is a small standalone Android app aimed at the Rakuten P780 Android 11 release build (API 30). It distinguishes the ability of an ordinary application to obtain public IPsec resources from any inference about a kernel vulnerability.

## What the two buttons do

1. **Read-only environment check:** display Android API, model, kernel version and whether IpSecManager is visible. No resources are allocated.
2. **Temporary resource check:** use the public Android API to reserve one SPI for TEST-NET-2 address 198.51.100.1, open a local UDP encapsulation socket, and try to create an ESP transport-mode transform (AES-CBC + HMAC-SHA256) using fresh random test keys. The transform is **never applied to a socket**. All resources are closed in finally blocks and key arrays are cleared.

The second button temporarily creates kernel-owned XFRM/IPsec state. It is not strictly read-only. It does **not** send any IPsec/ESP or UDP packets, call raw sockets, inject crafted traffic, exploit page-cache behavior, load a kernel module, change bootloader state, or modify user files. It declares INTERNET permission to obtain standard IPsec/UDP socket resources, but contains no code that makes an external connection.

A successful result establishes **only** that the ordinary Android app can allocate the tested IPsec resources. It neither establishes the kernel ESP receive/COW path nor proves or disproves DirtyFrag, root access, or bootloader unlock. A failure can be caused by policy, algorithm availability, resource limits, address validation, or the service implementation; it is not proof that the kernel path is absent.

## Build

GitHub Actions workflow: [P780 IPsec preflight Android APK](../../.github/workflows/p780-ipsec-preflight.yml).

The workflow uses Java 17, Android Gradle Plugin 8.5.2 and compileSdk 35. When green, download the **p780-ipsec-preflight-debug-apk** artifact (app-debug.apk) from that workflow run. Alternatively, on a machine with Android SDK and Gradle 8.7:

    gradle -p tools/ipsec-preflight-android :app:assembleDebug

## Device procedure (ONLY after the owner confirms installation)

Keep the P780 connected to ADB. Download the APK from the successful Actions run. On the Windows PowerShell host:

    adb install -r .\app-debug.apk
    adb shell am start -n top.dcmqht.p780ipsec/.MainActivity

1. Tap the read-only button and copy its output.
2. Only with explicit agreement to temporary IPsec state allocation, tap the second button, and copy its output.
3. Share output back into the project; remove the diagnostic when finished with `adb uninstall top.dcmqht.p780ipsec` if desired.

No ADB root is required; run under ordinary app privileges. No need to change SELinux or bootloader state.

## Related evidence

See [P780 DirtyFrag UDP/ESP source audit](../../docs/research/p780-dirtyfrag-udp-esp-source-audit-20261024.md). This probe is a narrowly scoped follow-up to its *unverified on-device API access* question, not an exploit attempt.

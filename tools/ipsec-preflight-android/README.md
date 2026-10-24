# P780 / Android 11 IPsec diagnostics (non-exploit)

Version: **0.2.0**

This standalone app targets the Rakuten P780 Android 11 release build (API 30). It separates ordinary public-API and loopback checks from any inference about a kernel vulnerability.

## What the three buttons do

1. **Read-only environment check:** display Android API, model, kernel version and whether `IpSecManager` is visible. No resources are allocated.
2. **Temporary resource check:** preserve the 0.1.0 check: reserve one SPI for TEST-NET-2 address `198.51.100.1`, open a UDP encapsulation socket, and create an unassigned ESP transport-mode transform using fresh random test keys. The transform is never applied to a traffic socket and no packet is sent.
3. **Ordinary UDP/ESP loopback diagnostic:** first send exactly one small plain UDP datagram from a socket to itself on `127.0.0.1`. If that baseline passes, create an IPv4 UDP-encapsulated IPsec transport transform for `127.0.0.1`, apply it in both directions to one ordinary `DatagramSocket`, send exactly one small application datagram to that same socket, receive it, and compare its bytes. The framework/kernel produces and consumes the protected packet; the app does not construct ESP.

Every allocated transform, socket and SPI is released. Key arrays are cleared. Button 3 removes transport policies from the diagnostic socket before closing the transform.

## Safety boundary

Button 3 is not read-only: when deliberately tapped, it creates temporary kernel XFRM/IPsec state and sends two local datagrams in total. Both destinations are `127.0.0.1`; there is no external connection.

The app does **not**:

- create a raw socket or manually build an ESP packet;
- send malformed, oversized, fragmented, repeated or attacker-controlled traffic;
- use a DirtyFrag/DFRoot payload or exercise page-cache/COW manipulation;
- load a kernel module, request root, change SELinux or bootloader state, or modify user files;
- claim that a PASS proves or disproves a vulnerability.

A loopback PASS shows only that this ordinary-app/API configuration completed a protected local round trip. A FAIL can result from service policy, algorithm support, vendor implementation, resource limits or timeout and is not proof of a vulnerable or non-vulnerable kernel.

## Android 11 / AOSP basis

The design follows the public [`IpSecManager`](https://developer.android.com/reference/android/net/IpSecManager) contract: apply `DIRECTION_IN` and `DIRECTION_OUT` transport transforms to a `DatagramSocket`, then call `removeTransportModeTransforms` before deactivating the transform.

The Android 11 framework branch exposes the relevant [`IpSecManager`](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android11-mainline-release/core/java/android/net/IpSecManager.java) and [`IpSecTransform`](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android11-mainline-release/core/java/android/net/IpSecTransform.java) classes. AOSP CTS [`IpSecManagerTest`](https://android.googlesource.com/platform/cts/+/408719bc937d75d0def7a484efd2956de9121089/tests/tests/net/src/android/net/cts/IpSecManagerTest.java) uses the same essential ordinary-API pattern: IPv4 loopback, a bound UDP socket, matching inbound/outbound transport transforms, a send/receive byte comparison, and transform removal. This app reduces that pattern to one protected datagram and adds a plain-UDP baseline and explicit cleanup reporting.

## Build

GitHub Actions workflow: [P780 IPsec preflight Android APK](../../.github/workflows/p780-ipsec-preflight.yml).

The workflow uses Java 17, Android Gradle Plugin 8.5.2 and compileSdk 35. When green, download the **p780-ipsec-preflight-debug-apk** artifact (`app-debug.apk`) from that workflow run. Alternatively, on a machine with Android SDK and Gradle 8.7:

    gradle -p tools/ipsec-preflight-android :app:assembleDebug

The Actions build does not install or run the APK on a device.

## Device procedure (only after the owner explicitly confirms execution)

Do not install or launch 0.2.0 merely because it built successfully. After explicit confirmation, install it as an update, run the read-only button first, and separately confirm before tapping Button 3 because it sends loopback traffic and creates temporary IPsec state.

No ADB root, SELinux change or bootloader change is required.

## Related evidence

- [0.1.0 live results and kernel suffix provenance](../../docs/research/p780-ipsec-preflight-live-and-localversion-20261024.md)
- [P780 DirtyFrag UDP/ESP source audit](../../docs/research/p780-dirtyfrag-udp-esp-source-audit-20261024.md)


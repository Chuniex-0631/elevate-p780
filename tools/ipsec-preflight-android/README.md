# P780 / Android 11 IPsec and UDP diagnostics (non-exploit)

Version: **0.3.0**

This standalone app targets the Rakuten P780 Android 11 release build (API 30). It separates ordinary public-API checks from any inference about a kernel vulnerability.

## Four user-initiated checks

1. **Read-only environment check:** display Android API, model, kernel version and whether IpSecManager is visible. No resources are allocated.
2. **Temporary IPsec resource check:** reserve an SPI, open a UDP encapsulation socket and create an unassigned AES-CBC/HMAC-SHA256 transport transform with fresh random keys. It is never applied and sends no packet.
3. **Ordinary UDP/ESP loopback:** send one plain UDP datagram to 127.0.0.1, then create a UDP-encapsulated IPsec transport transform and apply inbound/outbound policies to one ordinary DatagramSocket; send and receive one protected application datagram and compare bytes. Android/framework kernel IPsec handles the protected packet; the app does not construct ESP.
4. **File-backed UDP sendfile loopback:** create a 1 KiB temporary file inside the app-private cache, call sendfile() exactly once from that file descriptor to a connected UDP socket targeting 127.0.0.1, receive and compare the datagram, verify the source file's bytes remain unchanged, close descriptors and unlink the temporary file. **No IPsec transform is active in this test.**

## What the new fourth check can and cannot tell us

A PASS means this app was able to send a file-backed datagram through the normal sendfile(file → UDP socket) interface on this device and that the received bytes matched while the source file remained unchanged. The kernel implementation may use the socket's splice/sendpage path, but the app has no kernel trace and does not claim to prove the exact callback executed.

It does **not** combine file-backed UDP transmission with ESP decapsulation. It does not attempt to write to the source page, does not modify a system file, does not build ESP packets, and does not prove or disprove CVE-2026-43284. A FAIL can reflect Android/Bionic/kernel restrictions and is not a vulnerability verdict.

## Safety boundary

- All network destinations are loopback 127.0.0.1; no external connection is opened.
- The fourth check uses only a short-lived file under the app's private cache directory. It verifies the bytes before/after and unlinks the file.
- No raw sockets, manually constructed ESP, malformed/oversized/fragmented packets, repetition/fuzzing, DirtyFrag/DFRoot payload, exploit-style page-cache manipulation, root request, kernel module, SELinux change, bootloader operation or partition write is performed. The temporary test file uses ordinary app-private file I/O.
- Checks 2 and 3 temporarily create kernel IPsec state; check 4 performs ordinary file-to-UDP sendfile I/O. None is strictly read-only.
- The APK build does not install or run the app on a device. Device execution requires explicit owner confirmation.

## Android 11 / AOSP basis

The IPsec loopback follows the public IpSecManager contract and the corresponding Android 11 framework APIs. The normal protected loopback pattern is based on AOSP CTS IpSecManagerTest.

The sendfile probe is a separate ordinary UDP test. It is deliberately not combined with ESP or file-page mutation because that combination would move from benign path checking into the vulnerable page-cache write primitive.

## Build

GitHub Actions workflow: [P780 IPsec preflight Android APK](../../.github/workflows/p780-ipsec-preflight.yml). It installs Android platform/build-tools, NDK 26.3 and CMake 3.22.1, then builds the arm64-v8a debug APK. The build does not run it on a device.

Artifact name: p780-ipsec-preflight-debug-apk; file: app-debug.apk.

## Device procedure

Do not install or launch v0.3 merely because it built successfully. After the build is reviewed and the owner explicitly confirms device execution, install it as a fresh debug build if Android rejects the prior APK due to a different ephemeral CI debug-signing key. Run check 1 first. Check 4 should be separately confirmed; it performs one file-backed sendfile to loopback and then removes its private temporary file.

## Related evidence

- [v0.2 live loopback result](../../docs/research/p780-ipsec-v0.2-live-loopback-20261024.md)
- [DirtyFrag v0.2 path interpretation and next safety gate](../../docs/research/p780-dirtyfrag-v02-path-interpretation-20261024.md)
- [DirtyFrag UDP/ESP source audit](../../docs/research/p780-dirtyfrag-udp-esp-source-audit-20261024.md)

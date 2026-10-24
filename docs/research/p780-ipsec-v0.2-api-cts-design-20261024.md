# P780 IPsec diagnostics 0.2.0: Android 11 API/CTS basis and safety boundary

Date: 2026-10-24 (Asia/Shanghai)  
Status: implementation prepared for build verification; no device execution authorized or performed.

## Verified API surface

The Android public API documents these API-level-28 operations used by the diagnostic:

- `IpSecManager.allocateSecurityParameterIndex(InetAddress)`;
- `IpSecManager.openUdpEncapsulationSocket()`;
- `IpSecTransform.Builder.setIpv4Encapsulation(...)` and `buildTransportModeTransform(...)`;
- `IpSecManager.applyTransportModeTransform(DatagramSocket, DIRECTION_IN|DIRECTION_OUT, ...)`;
- `IpSecManager.removeTransportModeTransforms(DatagramSocket)`.

The contract states that socket traffic must match the transform's remote address and that transforms must be removed before an applied transform is closed. Version 0.2.0 therefore uses `127.0.0.1` consistently as transform peer and packet destination, and performs cleanup in this order: remove socket policies, close diagnostic socket, close transform, close encapsulation socket, close SPI.

Primary references:

- Android Developers: <https://developer.android.com/reference/android/net/IpSecManager>
- Android 11 framework branch, `IpSecManager.java`: <https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android11-mainline-release/core/java/android/net/IpSecManager.java>
- Android 11 framework branch, `IpSecTransform.java`: <https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android11-mainline-release/core/java/android/net/IpSecTransform.java>

## AOSP CTS pattern used

AOSP CTS `IpSecManagerTest` contains an ordinary UDP transport-mode loopback pattern: allocate a loopback SPI, create a transform, bind a UDP socket, apply matching inbound and outbound transforms, send to the socket's own loopback port, receive and compare bytes, then remove transforms and close resources.

Fixed reference used for the code-pattern audit:

- <https://android.googlesource.com/platform/cts/+/408719bc937d75d0def7a484efd2956de9121089/tests/tests/net/src/android/net/cts/IpSecManagerTest.java>

The P780 diagnostic is intentionally narrower than CTS coverage: one plain baseline datagram and one protected application datagram, IPv4 loopback only, a two-second receive timeout, fresh random keys, and no traffic counters or negative/asymmetric cases.

## Interpretation boundary

A PASS can establish that ordinary UDP loopback works and that the public Android IPsec API can complete one matching transport-mode loopback on this build. It does not establish the identity of the running kernel source, prove the presence or absence of DirtyFrag, test page-cache/COW behavior, or grant root.

A failure remains non-diagnostic for vulnerability status. It may reflect service policy, algorithm availability, a vendor-specific implementation difference, exhausted resources, or timeout.

## Explicit exclusions

No raw sockets, manually constructed ESP, malformed or fragmented traffic, repetitions/fuzzing, DirtyFrag/DFRoot payload, page-cache operation, privilege escalation, persistent system change, or device-side execution is part of this implementation/build step.


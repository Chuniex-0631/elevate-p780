# OEM Lock offline audit

Requires Python and androguard 4.1.4. Based on the repository's read_performance_dex.py table reader. No device or network access during analysis.

Run: `python tools/oemlock/audit.py Settings.apk framework.jar services.jar --output audit-output`

The script decodes the selected controller, OEM Lock classes and JourneyDebugFeature. It records input SHA256, raw method instruction bytes and their SHA256, code offsets and decoded instructions, and checks decoded byte coverage. It does not reconstruct exception tables or prove runtime class loading, permissions or reachability. focused-methods.json is a manually selected 15-method subset of the 114-method run. Original APK/JAR files remain on the owner's PC.

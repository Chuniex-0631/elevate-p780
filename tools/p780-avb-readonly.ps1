# P780 AVB read-only baseline collector (Windows PowerShell 5.1+)
# This script only uses adb get-state, adb shell getprop and adb shell ls -l.
# It does NOT read partition contents, obtain root, reboot, or modify the device.
[CmdletBinding()]
param(
    [string]$OutputPath = (Join-Path (Get-Location).Path ("p780-avb-readonly-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".txt"))
)

$ErrorActionPreference = "Stop"
if (-not (Get-Command adb -ErrorAction SilentlyContinue)) {
    throw "adb was not found in PATH."
}
$state = @(& adb get-state 2>&1) -join "`n"
if ($LASTEXITCODE -ne 0 -or $state.Trim() -ne "device") {
    throw "ADB must be connected and authorized (exactly one device). Current: $state"
}

# Explicit allowlist: no serial, IMEI, MEID, eSIM, accounts or full getprop dump.
$properties = @(
    "ro.product.device",
    "ro.build.fingerprint",
    "ro.custom.build.version",
    "ro.internal.build.version",
    "ro.build.version.release",
    "ro.build.version.security_patch",
    "ro.boot.verifiedbootstate",
    "ro.boot.vbmeta.device_state",
    "ro.boot.flash.locked",
    "ro.boot.slot_suffix",
    "ro.boot.vbmeta.digest",
    "ro.boot.vbmeta.hash_alg",
    "ro.boot.vbmeta.size",
    "ro.boot.vbmeta.public_key_digest",
    "ro.boot.vbmeta.avb_version",
    "ro.boot.avb_version",
    "ro.boot.veritymode"
)
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# P780 AVB read-only collection")
$lines.Add("# Collection time (host-local): " + (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"))
$lines.Add("# Reported values are not a substitute for reading vbmeta images.")
$lines.Add("")

foreach ($property in $properties) {
    $result = @(& adb shell getprop $property 2>&1) -join "`n"
    if ($LASTEXITCODE -ne 0) {
        $lines.Add("$property = <adb error: $result>")
    } else {
        $value = $result.Trim()
        if ($value -eq "") { $value = "<unset or empty>" }
        $lines.Add("$property = $value")
    }
}

$lines.Add("")
$lines.Add("# Partition name / symlink inventory (not contents)")
$inventory = @(& adb shell ls -l /dev/block/by-name 2>&1)
if ($LASTEXITCODE -eq 0) {
    $filtered = @($inventory | Where-Object { $_ -match "(?i)vbmeta|boot|dtbo|super|metadata" })
    if ($filtered.Count -eq 0) {
        $lines.Add("<no matching entries>")
    } else {
        foreach ($line in $filtered) { $lines.Add([string]$line) }
    }
} else {
    $lines.Add("<inventory unavailable: " + ($inventory -join " ") + ">")
}

$lines.Add("")
$lines.Add("# Selected block-device permissions only (no bytes read)")
$blockPerms = @(& adb shell ls -l /dev/block/sde31 /dev/block/sda11 2>&1)
if ($LASTEXITCODE -eq 0) {
    foreach ($line in $blockPerms) { $lines.Add([string]$line) }
} else {
    $lines.Add("<permissions unavailable: " + ($blockPerms -join " ") + ">")
}

$lines.Add("")
$lines.Add("# Logical partition symlinks (not contents)")
$maps = @(& adb shell ls -l /dev/block/mapper 2>&1)
if ($LASTEXITCODE -eq 0) {
    $mapFiltered = @($maps | Where-Object { $_ -match "(?i)system|vendor|product|odm|verity" })
    if ($mapFiltered.Count -eq 0) {
        $lines.Add("<no matching logical partition entries>")
    } else {
        foreach ($line in $mapFiltered) { $lines.Add([string]$line) }
    }
} else {
    $lines.Add("<logical partition inventory unavailable: " + ($maps -join " ") + ">")
}

$lines | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host "Read-only AVB report saved: $OutputPath"
Write-Host "Review the report before sharing; do not share unrelated ADB logs or personal identifiers."

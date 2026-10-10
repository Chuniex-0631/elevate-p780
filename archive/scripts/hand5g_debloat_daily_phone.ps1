# ARCHIVED FOR REFERENCE ONLY. THIS SCRIPT MODIFIES AND UNINSTALLS DEVICE PACKAGES. DO NOT RUN WITHOUT INDEPENDENT REVIEW.
param(
    [switch]$Lean,
    [switch]$RemoveRakutenFinance,
    [switch]$NoReboot,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$baseDir = Get-Location
$log = Join-Path $baseDir "hand5g-daily-phone-debloat-$stamp.log"
$restore = Join-Path $baseDir "hand5g-daily-phone-restore-$stamp.ps1"

Start-Transcript -Path $log -Force | Out-Null

function Stop-WithError([string]$Message) {
    Write-Host "`nERROR: $Message" -ForegroundColor Red
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}

function Wait-AndroidBoot {
    Write-Host "`n=== Waiting for Android ===" -ForegroundColor Cyan
    adb wait-for-device | Out-Null
    for ($i = 0; $i -lt 120; $i++) {
        $boot = (adb shell getprop sys.boot_completed 2>$null | Out-String).Trim()
        if ($boot -eq "1") {
            Start-Sleep -Seconds 8
            Write-Host "Android boot completed." -ForegroundColor Green
            return
        }
        Start-Sleep -Seconds 2
    }
    Stop-WithError "Timed out waiting for Android boot."
}

function Get-User0Packages {
    $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($line in @(adb shell pm list packages --user 0 2>$null)) {
        $s = "$line".Trim()
        if ($s.StartsWith("package:")) {
            [void]$set.Add($s.Substring(8))
        }
    }
    return $set
}

$Removed = New-Object System.Collections.Generic.List[string]
$RemovedDataApps = New-Object System.Collections.Generic.List[string]

function Remove-User0Package([string]$Package, [System.Collections.Generic.HashSet[string]]$Installed) {
    if (-not $Installed.Contains($Package)) {
        Write-Host ("[SKIP] {0}" -f $Package) -ForegroundColor DarkGray
        return
    }

    $path = (adb shell pm path $Package 2>$null | Out-String).Trim()
    $isDataApp = $path -match "package:/data/app/"

    $result = (adb shell pm uninstall --user 0 $Package 2>&1 | Out-String).Trim()
    if ($result -match "^Success") {
        Write-Host ("[ OK ] {0}" -f $Package) -ForegroundColor Green
        [void]$Installed.Remove($Package)
        [void]$Removed.Add($Package)
        if ($isDataApp) {
            [void]$RemovedDataApps.Add($Package)
        }
    } else {
        Write-Host ("[WARN] {0} -> {1}" -f $Package, $result) -ForegroundColor Yellow
    }
}

# ----------------------------------------------------------------------
# Rakuten Hand 5G / P780 - DAILY PHONE profile
#
# Goal:
#   Keep the device usable as a normal Android phone:
#   - calls / SMS / SIM / carrier services
#   - Google Play / GMS / Google account
#   - Chrome / Maps / Photos / Gmail / YouTube
#   - contacts / calendar / clock / calculator / Files
#   - Bluetooth / NFC / FeliCa / Secure Element
#   - camera / gallery / sound recorder
#   - emergency Cell Broadcast
#   - WebView / PackageInstaller / PermissionController
#   - NetworkStack / tethering / MediaProvider
#   - Settings / SystemUI / Launcher / Gboard
#   - location / IMS / RCS / telephony stack
#   - Android backup / restore / managed provisioning
#
# Default mode removes obvious promotional/content bloat and diagnostics.
#
# Optional:
#   -Lean
#       also removes several reinstallable Google apps/features.
#
#   -RemoveRakutenFinance
#       additionally removes Rakuten finance/payment/shopping apps.
#       DO NOT use if you actively use Rakuten Pay/Bank/Card/Edy/etc.
# ----------------------------------------------------------------------

$SafeRemove = @(
    # Rakuten / third-party promotional & content apps
    "jp.co.visselkobe.App",
    "com.viber.voip",
    "com.rakuten.room",
    "jp.co.rakuten.music",
    "jp.co.rakuten.pasha",
    "jp.co.rakuten.slide",
    "jp.co.rakuten.recipe",
    "jp.co.rakuten.research",
    "jp.co.rakuten.magazine",
    "jp.co.rakuten.fashionAndroid",
    "jp.co.rakuten.toolbar.raws",
    "jp.co.rakuten.golf.gora2",
    "jp.co.rakuten.delivery",
    "jp.co.rakuten.rakutenluckykuji",
    "jp.co.rakuten.beauty.android",
    "jp.co.rakuten.carlifeapp",
    "jp.co.rakuten.mobile.browser",
    "jp.co.rakuten.travel.andro",
    "jp.co.rakuten.pointpartner.app",
    "com.ateagles",
    "jp.co.fablic.fril",
    "jp.co.rakuten.video.showtimeplayer",
    "jp.co.rakuten.rebates",

    # Promotional launcher/feed/autoinstall layer
    "com.rakuten.feed",
    "com.rakuten.launcher3",
    "android.autoinstalls.config.tinno",

    # Development / factory / diagnostic components not needed in daily use
    "com.android.dynsystem",
    "com.android.traceur",
    "com.ape.factory",
    "com.qti.diagservices",
    "com.qualcomm.qti.devicestatisticsservice",

    # Low-value Google support/telemetry helpers
    "com.google.android.feedback",
    "com.google.android.printservice.recommendation"
)

$LeanRemove = @(
    # Reinstallable Google apps / optional features.
    # Core Google framework, Play Store, Chrome, Maps, Gmail, Photos,
    # YouTube, Calendar, Files, Assistant/Search and accessibility stay.
    "com.google.android.apps.youtube.music",
    "com.google.android.videos",
    "com.google.android.apps.docs.editors.docs",
    "com.google.android.apps.docs.editors.sheets",
    "com.google.android.apps.docs.editors.slides",
    "com.google.android.apps.tachyon",
    "com.google.android.projection.gearhead",
    "com.google.android.apps.wellbeing"
)

$RakutenFinanceRemove = @(
    # Optional: only when you do NOT use Rakuten ecosystem finance/payment apps.
    "jp.co.rakuten_bank.rakutenbank",
    "jp.co.rakuten.kc.rakutencardapp.android",
    "jp.co.rakuten.android",
    "jp.co.rakuten.pointclub.android",
    "jp.co.rakuten_sec.ispeed",
    "jp.co.rakuten.pay",
    "jp.edy.edyapp"
)

# Packages that this DAILY PHONE profile deliberately protects.
$Protected = @(
    "com.android.phone",
    "com.android.providers.telephony",
    "com.android.carrierconfig",
    "com.android.carrierdefaultapp",
    "com.android.simappdialog",
    "com.android.stk",

    "com.google.android.gms",
    "com.google.android.gsf",
    "com.google.android.gsf.login",
    "com.android.vending",
    "com.google.android.configupdater",
    "com.google.android.setupwizard",
    "com.google.android.onetimeinitializer",
    "com.google.android.partnersetup",
    "com.google.android.apps.restore",

    "com.google.android.dialer",
    "com.google.android.apps.messaging",
    "com.google.android.contacts",
    "com.google.android.syncadapters.contacts",
    "com.google.android.calendar",

    "com.android.nfc",
    "com.android.se",
    "com.felicanetworks.mfw.a.boot",
    "com.felicanetworks.mfc",
    "com.felicanetworks.mfs",
    "com.felicanetworks.mfm.main",

    "com.android.bluetooth",
    "com.android.bluetoothmidiservice",

    "com.google.android.ims",
    "org.codeaurora.ims",
    "jp.co.rakuten.mobile.rcs",

    "com.google.android.cellbroadcastreceiver",
    "com.google.android.cellbroadcastservice",
    "com.android.cellbroadcastreceiver",

    "com.google.android.webview",
    "com.google.android.packageinstaller",
    "com.google.android.permissioncontroller",
    "com.google.android.networkstack",
    "com.google.android.networkstack.tethering",
    "com.google.android.providers.media.module",
    "com.google.android.ext.services",
    "com.google.android.ext.shared",

    "com.android.settings",
    "com.android.systemui",
    "com.android.launcher3",
    "com.google.android.inputmethod.latin",

    "com.android.providers.contacts",
    "com.android.providers.calendar",
    "com.android.providers.blockednumber",
    "com.android.providers.userdictionary",
    "com.android.localtransport",
    "com.android.managedprovisioning",
    "com.android.settings.intelligence",

    "com.qualcomm.location",
    "com.android.location.fused",
    "com.qualcomm.qti.telephonyservice",
    "com.qualcomm.qcrilmsgtunnel"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Rakuten Hand 5G (P780) - DAILY PHONE Debloat" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Keeps normal phone features; removes obvious bloat."
Write-Host "Log     : $log"
Write-Host "Restore : $restore"
Write-Host "Lean mode              : $Lean"
Write-Host "Remove Rakuten finance : $RemoveRakutenFinance"

try {
    Get-Command adb -ErrorAction Stop | Out-Null
} catch {
    Stop-WithError "adb.exe is not available in PATH."
}

adb wait-for-device | Out-Null
$state = (adb get-state 2>$null | Out-String).Trim()
if ($state -ne "device") {
    Stop-WithError "ADB device is not authorized/online."
}

$model   = (adb shell getprop ro.product.model 2>$null | Out-String).Trim()
$product = (adb shell getprop ro.product.name 2>$null | Out-String).Trim()
$device  = (adb shell getprop ro.product.device 2>$null | Out-String).Trim()

Write-Host "`nModel   : $model"
Write-Host "Product : $product"
Write-Host "Device  : $device"

$isP780 = ($model -eq "P780" -or $product -eq "P780" -or $device -eq "P780")
if (-not $isP780 -and -not $Force) {
    Stop-WithError "This script is tailored to Rakuten Hand 5G / P780. Use -Force only if you knowingly accept the risk."
}

$before = Get-User0Packages
Write-Host ("`nInitial user-0 package count: {0}" -f $before.Count)

# Build actual removal list.
$targets = New-Object System.Collections.Generic.List[string]
foreach ($p in $SafeRemove) { [void]$targets.Add($p) }

if ($Lean) {
    foreach ($p in $LeanRemove) { [void]$targets.Add($p) }
}

if ($RemoveRakutenFinance) {
    foreach ($p in $RakutenFinanceRemove) { [void]$targets.Add($p) }
}

# Safety check: protected package must never be in targets.
$badTargets = @($targets | Where-Object { $Protected -contains $_ })
if ($badTargets.Count -gt 0) {
    Stop-WithError ("Protected packages appeared in removal list: " + ($badTargets -join ", "))
}

Write-Host "`n=== Removing selected packages ===" -ForegroundColor Cyan
$installed = Get-User0Packages
foreach ($pkg in ($targets | Sort-Object -Unique)) {
    Remove-User0Package $pkg $installed
}

# Generate a best-effort restore helper for system packages.
$restoreHeader = @'
# Rakuten Hand 5G DAILY PHONE restore helper
# Generated automatically by the debloat script.
#
# System packages removed only for user 0 can usually be restored with:
#   adb shell cmd package install-existing --user 0 <package>
#
# /data/app third-party apps may need to be reinstalled from Google Play,
# F-Droid, APK backup, or by factory reset.
$ErrorActionPreference = "Continue"
'@

Set-Content -Path $restore -Value $restoreHeader -Encoding UTF8

foreach ($pkg in ($Removed | Sort-Object -Unique)) {
    if ($RemovedDataApps.Contains($pkg)) {
        Add-Content -Path $restore -Value ("Write-Host '[DATA APP - reinstall manually] {0}'" -f $pkg)
    } else {
        Add-Content -Path $restore -Value ("adb shell cmd package install-existing --user 0 {0}" -f $pkg)
    }
}

if (-not $NoReboot) {
    Write-Host "`n=== Rebooting ===" -ForegroundColor Cyan
    adb reboot
    Wait-AndroidBoot
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL VALIDATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$final = Get-User0Packages
Write-Host ("Final user-0 package count: {0}" -f $final.Count)
Write-Host ("Removed this run         : {0}" -f (($Removed | Sort-Object -Unique).Count))

Write-Host "`n--- Protected daily-phone components ---" -ForegroundColor Magenta
$missingProtected = @()
foreach ($pkg in $Protected) {
    if ($final.Contains($pkg)) {
        Write-Host "[KEEP] $pkg" -ForegroundColor Green
    } else {
        # Some packages can be absent on a specific firmware from the start,
        # so report rather than automatically declaring corruption.
        $missingProtected += $pkg
        Write-Host "[MISS/NOT PRESENT] $pkg" -ForegroundColor Yellow
    }
}

Write-Host "`n--- Core checks ---" -ForegroundColor Magenta

$home = (adb shell cmd package resolve-activity --brief `
    -a android.intent.action.MAIN `
    -c android.intent.category.HOME 2>$null | Out-String).Trim()
Write-Host "HOME: $home"

$webview = (adb shell dumpsys webviewupdate 2>$null |
    Select-String "Current WebView package" |
    Select-Object -First 1)
if ($webview) { Write-Host $webview }

$wifiLine = (adb shell dumpsys wifi 2>$null |
    Select-String "Wi-Fi is" |
    Select-Object -First 1)
if ($wifiLine) { Write-Host $wifiLine }

Write-Host "`n--- Telephony / Google / NFC / Bluetooth spot check ---" -ForegroundColor Magenta
$spot = @(
    "com.android.phone",
    "com.google.android.gms",
    "com.android.vending",
    "com.google.android.dialer",
    "com.google.android.apps.messaging",
    "com.android.nfc",
    "com.android.bluetooth"
)
foreach ($pkg in $spot) {
    if ($final.Contains($pkg)) {
        Write-Host "[OK] $pkg" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $pkg" -ForegroundColor Yellow
    }
}

Write-Host "`n--- Memory snapshot ---" -ForegroundColor Magenta
adb shell cat /proc/meminfo |
    Select-String "MemFree|MemAvailable|SwapFree"

Write-Host "`nDone." -ForegroundColor Green
Write-Host "Transcript : $log"
Write-Host "Restore helper: $restore"

if ($RemovedDataApps.Count -gt 0) {
    Write-Host "`nNOTE: These removed apps were installed under /data/app and may not be" -ForegroundColor Yellow
    Write-Host "restorable with install-existing. Reinstall them from Play/APK if needed:" -ForegroundColor Yellow
    $RemovedDataApps | Sort-Object -Unique | ForEach-Object { Write-Host "  $_" }
}

Stop-Transcript | Out-Null
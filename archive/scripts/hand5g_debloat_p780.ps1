# ARCHIVED FOR REFERENCE ONLY. THIS SCRIPT MODIFIES AND UNINSTALLS DEVICE PACKAGES. DO NOT RUN WITHOUT INDEPENDENT REVIEW.
param(
    [switch]$Force,
    [switch]$NoReboot
)

$ErrorActionPreference = "Stop"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$log = Join-Path (Get-Location) "hand5g-debloat-$stamp.log"
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
    return ,$set
}

function Remove-User0Package([string]$Package, [System.Collections.Generic.HashSet[string]]$Installed) {
    if (-not $Installed.Contains($Package)) {
        Write-Host ("[SKIP] {0}" -f $Package) -ForegroundColor DarkGray
        return
    }

    $result = (adb shell pm uninstall --user 0 $Package 2>&1 | Out-String).Trim()
    if ($result -match "^Success") {
        Write-Host ("[ OK ] {0}" -f $Package) -ForegroundColor Green
        [void]$Installed.Remove($Package)
    } else {
        Write-Host ("[WARN] {0} -> {1}" -f $Package, $result) -ForegroundColor Yellow
    }
}

function Run-RemovalPass([string]$Label) {
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host $Label -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan

    $installed = Get-User0Packages
    Write-Host ("Packages before pass: {0}" -f $installed.Count)

    foreach ($group in $Groups.GetEnumerator()) {
        Write-Host "`n--- $($group.Key) ---" -ForegroundColor Magenta
        foreach ($pkg in $group.Value) {
            Remove-User0Package $pkg $installed
        }
    }

    $after = Get-User0Packages
    Write-Host ("`nPackages after pass: {0}" -f $after.Count)
}

# ----------------------------------------------------------------------
# Rakuten Hand 5G / P780 - tested user-0 debloat set
#
# IMPORTANT: this intentionally KEEPS Android/Qualcomm core components:
# - com.android.launcher3 / SystemUI / Settings
# - Google WebView / PackageInstaller / PermissionController
# - NetworkStack / Tethering / MediaProvider / ext services
# - Android fused-location framework
# - com.android.phone / QtiTelephonyService / qcrilmsgtunnel
# - Qualcomm CNE/IWLAN/qtidataservices
# - workloadclassifier / PASR / systemhelper / secureui
# - Gboard (useful until the device is fully headless)
# ----------------------------------------------------------------------

$Groups = [ordered]@{
    "Rakuten / preinstalled third-party apps" = @(
        "jp.co.visselkobe.App",
        "com.viber.voip",
        "com.rakuten.room",
        "jp.co.rakuten_bank.rakutenbank",
        "jp.co.rakuten.music",
        "jp.co.rakuten.pasha",
        "jp.co.rakuten.slide",
        "jp.co.rakuten.recipe",
        "jp.co.rakuten.research",
        "jp.co.rakuten.kc.rakutencardapp.android",
        "jp.co.rakuten.magazine",
        "jp.co.rakuten.android",
        "jp.co.rakuten.fashionAndroid",
        "jp.co.rakuten.toolbar.raws",
        "jp.co.rakuten.golf.gora2",
        "jp.co.rakuten.delivery",
        "jp.co.rakuten.rakutenluckykuji",
        "jp.co.rakuten.pointclub.android",
        "jp.co.rakuten.beauty.android",
        "jp.co.rakuten.carlifeapp",
        "jp.co.rakuten.mobile.browser",
        "jp.co.rakuten.travel.andro",
        "jp.co.rakuten.pointpartner.app",
        "com.ateagles",
        "jp.co.fablic.fril",
        "jp.co.rakuten.video.showtimeplayer",
        "jp.co.rakuten.rebates",
        "jp.co.rakuten_sec.ispeed",
        "jp.co.rakuten.pay",
        "ht.spotlig.rakutenchk",
        "jp.edy.edyapp"
    )

    "Google / consumer apps / setup" = @(
        "com.android.vending",
        "com.google.android.googlequicksearchbox",
        "com.google.android.apps.googleassistant",
        "com.google.android.youtube",
        "com.google.android.apps.youtube.music",
        "com.google.android.gm",
        "com.google.android.apps.maps",
        "com.google.android.apps.photos",
        "com.google.android.videos",
        "com.google.android.apps.docs",
        "com.google.android.apps.docs.editors.docs",
        "com.google.android.apps.docs.editors.sheets",
        "com.google.android.apps.docs.editors.slides",
        "com.google.android.calendar",
        "com.google.android.apps.tachyon",
        "com.google.android.calculator",
        "com.google.android.deskclock",
        "com.google.android.apps.nbu.files",
        "com.android.chrome",
        "com.google.android.projection.gearhead",
        "com.google.android.apps.wellbeing",
        "com.google.android.gms.location.history",
        "com.google.android.feedback",
        "com.google.android.printservice.recommendation",
        "com.google.android.marvin.talkback",
        "com.google.android.dialer",
        "com.google.android.apps.messaging",
        "com.google.android.contacts",
        "com.google.android.syncadapters.contacts",
        "com.google.android.onetimeinitializer",
        "com.google.android.partnersetup",
        "com.google.android.apps.restore",
        "com.google.android.setupwizard",
        "com.google.android.apps.turbo",
        "com.android.hotwordenrollment.okgoogle",
        "com.android.hotwordenrollment.xgoogle",
        "com.google.android.tts",
        "com.android.printspooler",
        "com.android.bips",
        "com.android.bluetoothmidiservice",
        "com.google.android.gms",
        "com.google.android.gsf",
        "com.google.android.configupdater",
        "com.google.android.gsf.login"
    )

    "Rakuten launcher / feed / setup extras" = @(
        "com.rakuten.feed",
        "jp.co.rakuten.mobile.ecare",
        "com.rakuten.launcher3",
        "android.autoinstalls.config.tinno",
        "com.ape.setupwizard",
        "jp.co.rakuten.mobile.rcs"
    )

    "SIM / carrier / IMS / telephony extras" = @(
        "com.google.android.ims",
        "com.qualcomm.qti.simcontacts",
        "com.qualcomm.qti.callfeaturessetting",
        "com.qti.confuridialer",
        "com.qualcomm.qti.confdialer",
        "com.qualcomm.qti.simsettings",
        "com.qualcomm.qti.remoteSimlockAuth",
        "com.qualcomm.qti.ims",
        "com.android.carrierdefaultapp",
        "com.android.simappdialog",
        "com.qualcomm.embms",
        "com.qti.ltebc",
        "com.android.stk",
        "com.google.android.cellbroadcastreceiver",
        "com.google.android.cellbroadcastservice",
        "com.android.cellbroadcastreceiver",
        "com.qualcomm.uimremoteclient",
        "com.qualcomm.uimremoteserver",
        "com.qualcomm.qti.uim",
        "com.qualcomm.qti.uimGbaApp",
        "com.qualcomm.qti.lpa",
        "com.qualcomm.qti.uceShimService",
        "com.android.cellbroadcast.overlay",
        "com.android.cellbroadcastservice.overlay",
        "com.android.cellbroadcastreceiver.overlay.common",
        "com.gemalto.odc.lpa.consumer.app",
        "com.qualcomm.atfwd",
        "org.codeaurora.ims",
        "com.android.smspush",
        "com.android.carrierconfig",
        "com.android.carrierconfig.overlay.common"
    )

    "NFC / FeliCa / Secure Element UI" = @(
        "com.android.nfc",
        "com.felicanetworks.mfw.a.boot",
        "com.felicanetworks.mfc",
        "com.felicanetworks.mfs",
        "com.felicanetworks.mfm.main",
        "com.android.se"
    )

    "OEM diagnostics / factory / unused services" = @(
        "com.ape.faceunlock",
        "com.qualcomm.qti.devicestatisticsservice",
        "com.qti.diagservices",
        "com.quicinc.voice.activation",
        "com.ape.soundrecorder",
        "com.ape.factory",
        "com.android.dynsystem",
        "com.android.managedprovisioning",
        "com.android.traceur",
        "com.android.localtransport",
        "com.android.settings.intelligence"
    )

    "Providers not needed on headless server" = @(
        "com.android.providers.calendar",
        "com.android.providers.contacts",
        "com.android.providers.blockednumber",
        "com.android.providers.userdictionary"
    )

    "Qualcomm location / QCC extras" = @(
        "com.qualcomm.location",
        "com.qualcomm.location.XT",
        "com.qualcomm.location.XT.setup",
        "com.qualcomm.qti.performancemode",
        "com.qualcomm.qti.qdma",
        "com.qualcomm.qti.qccauthmgr"
    )

    "Wallpaper / dreams" = @(
        "com.android.wallpapercropper",
        "com.android.wallpaper.livepicker",
        "com.android.wallpaperpicker",
        "com.android.wallpaperbackup",
        "com.android.dreams.basic"
    )

    "Bluetooth (final tested cut)" = @(
        "com.android.bluetooth"
    )
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Rakuten Hand 5G (P780) one-shot debloat" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Log: $log"

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
    Stop-WithError "This script is tailored to Rakuten Hand 5G / P780. Re-run with -Force only if you intentionally accept the risk."
}

$before = Get-User0Packages
Write-Host ("`nInitial user-0 package count: {0}" -f $before.Count)

Write-Host "`n=== Network mode ===" -ForegroundColor Cyan
adb shell cmd connectivity airplane-mode enable 2>$null | Out-Null
adb shell svc wifi enable 2>$null | Out-Null
Start-Sleep -Seconds 2
Write-Host ("Airplane mode: " + ((adb shell settings get global airplane_mode_on) | Out-String).Trim())
Write-Host "Wi-Fi requested enabled."

Run-RemovalPass "PASS 1 - remove tested packages"

if (-not $NoReboot) {
    Write-Host "`n=== Rebooting for persistence check ===" -ForegroundColor Cyan
    adb reboot
    Wait-AndroidBoot

    adb shell cmd connectivity airplane-mode enable 2>$null | Out-Null
    adb shell svc wifi enable 2>$null | Out-Null
    Start-Sleep -Seconds 3

    Run-RemovalPass "PASS 2 - catch packages re-registered after reboot"
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL VALIDATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$final = Get-User0Packages
Write-Host ("Final user-0 package count: {0}" -f $final.Count)
Write-Host ("Removed from user 0      : {0}" -f ($before.Count - $final.Count))

$mustKeep = @(
    "com.android.launcher3",
    "com.android.systemui",
    "com.android.settings",
    "com.google.android.webview",
    "com.google.android.packageinstaller",
    "com.google.android.permissioncontroller",
    "com.google.android.networkstack",
    "com.google.android.networkstack.tethering",
    "com.google.android.providers.media.module",
    "com.google.android.ext.services",
    "com.google.android.ext.shared",
    "com.google.android.inputmethod.latin"
)

Write-Host "`n--- Critical packages that must remain ---" -ForegroundColor Magenta
$criticalFailure = $false
foreach ($pkg in $mustKeep) {
    if ($final.Contains($pkg)) {
        Write-Host "[KEEP] $pkg" -ForegroundColor Green
    } else {
        Write-Host "[MISS] $pkg" -ForegroundColor Red
        $criticalFailure = $true
    }
}

Write-Host "`n--- Core runtime checks ---" -ForegroundColor Magenta
Write-Host ("Airplane mode: " + ((adb shell settings get global airplane_mode_on) | Out-String).Trim())

$wifiLine = (adb shell dumpsys wifi 2>$null | Select-String "Wi-Fi is" | Select-Object -First 1)
if ($wifiLine) { Write-Host $wifiLine }

$home = (adb shell cmd package resolve-activity --brief `
    -a android.intent.action.MAIN `
    -c android.intent.category.HOME 2>$null | Out-String).Trim()
Write-Host "HOME: $home"

$webview = (adb shell dumpsys webviewupdate 2>$null |
    Select-String "Current WebView package" |
    Select-Object -First 1)
if ($webview) { Write-Host $webview }

Write-Host "`n--- Remaining target packages (ideally empty) ---" -ForegroundColor Magenta
$remainingTargets = @()
foreach ($group in $Groups.GetEnumerator()) {
    foreach ($pkg in $group.Value) {
        if ($final.Contains($pkg)) { $remainingTargets += $pkg }
    }
}
if ($remainingTargets.Count -eq 0) {
    Write-Host "None." -ForegroundColor Green
} else {
    $remainingTargets | Sort-Object -Unique | ForEach-Object {
        Write-Host "[LEFT] $_" -ForegroundColor Yellow
    }
}

Write-Host "`n--- Memory snapshot ---" -ForegroundColor Magenta
adb shell cat /proc/meminfo |
    Select-String "MemFree|MemAvailable|SwapFree"

if ($criticalFailure) {
    Write-Host "`nWARNING: One or more critical keep-packages are missing." -ForegroundColor Red
    Write-Host "Do NOT proceed to Termux setup until you inspect the log." -ForegroundColor Red
} else {
    Write-Host "`nDebloat completed. Core keep-packages are present." -ForegroundColor Green
}

Write-Host "Transcript saved to: $log"

Stop-Transcript | Out-Null
# Rebuild exploit_p780 with the local Android NDK (r26d, extracted at
# <workspace>\.ndk\android-ndk-r26d).  Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File .\build_p780_ndk.ps1
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$root = Split-Path -Parent $here
$ndk = Join-Path $root '.ndk\android-ndk-r26d'
$clang = Join-Path $ndk 'toolchains\llvm\prebuilt\windows-x86_64\bin\aarch64-linux-android21-clang.cmd'
if (!(Test-Path $clang)) {
    Write-Error "NDK clang not found: $clang`nRe-extract android-ndk-r26d-windows.zip to $root\.ndk"
    exit 1
}
Push-Location (Join-Path $here 'pipa')
try {
    & $clang -fPIE -pie -O2 -pthread -w -I. exploit_p780.c -o exploit_p780_new
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Get-Item exploit_p780_new | Select-Object Name, Length
} finally {
    Pop-Location
}

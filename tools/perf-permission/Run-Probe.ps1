param([string]$AdbPath = '')
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$log = Join-Path $root ('P780-perf-permission-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$remote = '/data/local/tmp/p780-perf-permission-v0.1.0'
$pushed = $false
function Log([string]$Text) {
    Write-Host $Text
    [IO.File]::AppendAllText($log, $Text + [Environment]::NewLine, $utf8)
}
function Invoke-Adb([string[]]$AdbArgs) {
    $quoted = foreach ($item in $AdbArgs) {
        if ($item.Contains('"')) { throw 'Unexpected double quote in argument.' }
        '"' + $item + '"'
    }
    $info = New-Object Diagnostics.ProcessStartInfo
    $info.FileName = $script:adbExecutable
    $info.Arguments = $quoted -join ' '
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $proc = New-Object Diagnostics.Process
    $proc.StartInfo = $info
    try {
        if (-not $proc.Start()) { throw 'Could not start adb.' }
        $outTask = $proc.StandardOutput.ReadToEndAsync()
        $errTask = $proc.StandardError.ReadToEndAsync()
        if (-not $proc.WaitForExit(20000)) {
            $proc.Kill()
            $proc.WaitForExit()
            throw 'Local adb command timed out. Stop here; do not repeat the probe.'
        }
        $stdout = $outTask.GetAwaiter().GetResult()
        $stderr = $errTask.GetAwaiter().GetResult()
        if ($stdout.Trim()) { Log $stdout.TrimEnd() }
        if ($stderr.Trim()) { Log $stderr.TrimEnd() }
        Log ('adb_exit=' + $proc.ExitCode)
        return [int]$proc.ExitCode
    } finally { $proc.Dispose() }
}
try {
    Log 'P780 perf permission probe runner 0.1.0'
    Log ('started_local=' + (Get-Date -Format o))
    Log 'One authorized ADB device required. No root, sampling, reboot or settings changes.'
    if ($AdbPath) {
        $script:adbExecutable = (Resolve-Path -LiteralPath $AdbPath).Path
    } elseif (Test-Path -LiteralPath (Join-Path $root 'adb.exe')) {
        $script:adbExecutable = Join-Path $root 'adb.exe'
    } else {
        $script:adbExecutable = (Get-Command adb.exe -ErrorAction Stop).Source
    }
    $binary = Join-Path $root 'p780-perf-permission-arm64'
    if (-not (Test-Path -LiteralPath $binary -PathType Leaf)) { throw 'ARM64 probe binary missing.' }
    Log 'STEP 1: Check authorized device (no device-list or serial collection).'
    $rc = Invoke-Adb -AdbArgs @('get-state')
    if ($rc -ne 0) { throw 'ADB unavailable, unauthorized, or multiple devices. Stop; connect exactly one device.' }
    Log 'STEP 2: Push this probe only.'
    $rc = Invoke-Adb -AdbArgs @('push', $binary, $remote)
    if ($rc -ne 0) { throw 'Push failed; probe not run.' }
    $pushed = $true
    $rc = Invoke-Adb -AdbArgs @('shell', 'chmod', '700', $remote)
    if ($rc -ne 0) { throw 'chmod failed; probe not run.' }
    Log 'STEP 3: Run once in ordinary ADB shell.'
    $rc = Invoke-Adb -AdbArgs @('shell', $remote)
    Log ('probe_adb_exit=' + $rc)
    Log 'Return the complete log. Nonzero exit is diagnostic evidence; do not rerun or change permissions.'
} catch {
    Log ('RUNNER_ERROR=' + $_.Exception.Message)
} finally {
    if ($pushed) {
        try {
            Log 'STEP 4: Remove only the fixed probe path.'
            $cleanup = Invoke-Adb -AdbArgs @('shell', 'rm', '-f', $remote)
            if ($cleanup -ne 0) { Log ('CLEANUP_PENDING=' + $remote) }
        } catch { Log ('CLEANUP_PENDING=' + $remote) }
    }
    Log ('finished_local=' + (Get-Date -Format o))
    Write-Host ('Log saved: ' + $log)
}

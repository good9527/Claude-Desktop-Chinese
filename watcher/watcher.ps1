param(
    [Parameter(Mandatory=$false)][switch]$RegisterTask,
    [Parameter(Mandatory=$false)][switch]$UnregisterTask,
    [Parameter(Mandatory=$false)][ValidateSet("enable", "disable", "status", "")][string]$Daemon = "",
    [Parameter(Mandatory=$false)][switch]$DaemonOn,
    [Parameter(Mandatory=$false)][switch]$DaemonOff,
    [Parameter(Mandatory=$false)][switch]$Status,
    [Parameter(Mandatory=$false)][switch]$RunOnce,
    [Parameter(Mandatory=$false)][switch]$Check,
    [Parameter(Mandatory=$false)][string]$Path,
    [Parameter(Mandatory=$false)][switch]$Quiet
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "SilentlyContinue"

$cacheDir = Join-Path $env:LOCALAPPDATA "Claude-Chinese-Patch"
$cachedDict = Join-Path $cacheDir "zh-CN.json"
$logFile = Join-Path $cacheDir "watcher.log"
$taskName = "ClaudeDesktopChineseWatcher"
$regRunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$regRunName = "ClaudeDesktopChineseAutoHeal"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
    $logLine = "[$timestamp] [$Level] $Message"
    if (-not $Quiet) {
        switch ($Level) {
            "ERROR" { Write-Host $logLine -ForegroundColor Red }
            "WARN"  { Write-Host $logLine -ForegroundColor Yellow }
            "SUCCESS" { Write-Host $logLine -ForegroundColor Green }
            default { Write-Host $logLine -ForegroundColor Gray }
        }
    }
    try {
        if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null }
        Add-Content -Path $logFile -Value $logLine -Encoding UTF8 -ErrorAction SilentlyContinue
    } catch {}
}

function Find-ClaudeI18nFile {
    if ($Path -and (Test-Path $Path)) {
        if ($Path -like "*en-US.json") { return $Path }
        $candidate = Join-Path $Path "app\resources\ion-dist\i18n\en-US.json"
        if (Test-Path $candidate) { return $candidate }
    }

    $appx = Get-AppxPackage -Name "*Claude*" -ErrorAction SilentlyContinue | Sort-Object Version -Descending | Select-Object -First 1
    if ($appx -and $appx.InstallLocation) {
        $candidate = Join-Path $appx.InstallLocation "app\resources\ion-dist\i18n\en-US.json"
        if (Test-Path $candidate) { return $candidate }
        
        $found = Get-ChildItem -LiteralPath $appx.InstallLocation -Filter "en-US.json" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) { return $found.FullName }
    }

    $exeCandidates = @(
        "$env:LOCALAPPDATA\AnthropicClaude",
        "$env:LOCALAPPDATA\Programs\Claude",
        "$env:ProgramFiles\Claude",
        "${env:ProgramFiles(x86)}\Claude"
    )
    foreach ($dir in $exeCandidates) {
        if (Test-Path $dir) {
            $found = Get-ChildItem -LiteralPath $dir -Filter "en-US.json" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) { return $found.FullName }
        }
    }
    return $null
}

function Apply-ClaudePatch {
    param([string]$targetFile, [string]$dictFile)

    if (-not $targetFile -or -not (Test-Path -LiteralPath $targetFile)) {
        Write-Log "Target i18n file not found." "ERROR"
        return $false
    }
    if (-not $dictFile -or -not (Test-Path -LiteralPath $dictFile)) {
        Write-Log "Translation dictionary file not found: $dictFile" "ERROR"
        return $false
    }

    try {
        $enJsonStr = [System.IO.File]::ReadAllText($targetFile, [System.Text.Encoding]::UTF8)
        $enObj = $enJsonStr | ConvertFrom-Json
        $zhJsonStr = [System.IO.File]::ReadAllText($dictFile, [System.Text.Encoding]::UTF8)
        $zhObj = $zhJsonStr | ConvertFrom-Json

        $merged = [ordered]@{}
        $total = 0
        $translated = 0

        foreach ($prop in $enObj.PSObject.Properties) {
            $total++
            $k = $prop.Name
            $enVal = $prop.Value
            if ($zhObj.PSObject.Properties[$k] -and $zhObj.$k) {
                $merged[$k] = $zhObj.$k
                $translated++
            } else {
                $merged[$k] = $enVal
            }
        }

        $mergedJson = $merged | ConvertTo-Json -Depth 50 -Compress
        $tempFile = Join-Path $cacheDir ("en-US-patched-" + [Guid]::NewGuid().ToString("N") + ".json")
        [System.IO.File]::WriteAllText($tempFile, $mergedJson, [System.Text.Encoding]::UTF8)

        $success = $false
        for ($i = 1; $i -le 5; $i++) {
            try {
                [System.IO.File]::Copy($tempFile, $targetFile, $true)
                $success = $true
                break
            } catch {
                Start-Sleep -Milliseconds (300 * $i)
            }
        }
        Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

        if ($success) {
            Write-Log "Successfully patched Claude en-US.json ($translated / $total keys translated)!" "SUCCESS"
            return $true
        } else {
            Write-Log "Failed to overwrite en-US.json (file locked or permission denied)." "WARN"
            return $false
        }
    } catch {
        Write-Log "Patch execution error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Set-DaemonState {
    param([string]$Action)

    $scriptPath = if ($PSCommandPath) { $PSCommandPath } else { Join-Path $cacheDir "watcher.ps1" }

    if ($Action -eq "enable") {
        if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null }
        if ($PSCommandPath -and (Test-Path $PSCommandPath) -and ($PSCommandPath -ne (Join-Path $cacheDir "watcher.ps1"))) {
            Copy-Item $PSCommandPath (Join-Path $cacheDir "watcher.ps1") -Force
        }

        $cmd = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`" -RunOnce -Quiet"
        Set-ItemProperty -Path $regRunKey -Name $regRunName -Value $cmd -Force -ErrorAction SilentlyContinue

        try {
            $actionObj = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`" -RunOnce -Quiet"
            $triggerObj = New-ScheduledTaskTrigger -AtLogOn
            Register-ScheduledTask -TaskName $taskName -Action $actionObj -Trigger $triggerObj -Force -ErrorAction SilentlyContinue | Out-Null
        } catch {}

        Write-Log "Auto-healing daemon enabled successfully." "SUCCESS"
        return $true
    } elseif ($Action -eq "disable") {
        Remove-ItemProperty -Path $regRunKey -Name $regRunName -ErrorAction SilentlyContinue
        try { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}
        Write-Log "Auto-healing daemon disabled." "WARN"
        return $true
    } elseif ($Action -eq "status") {
        $regExists = (Get-ItemProperty -Path $regRunKey -Name $regRunName -ErrorAction SilentlyContinue) -ne $null
        $taskExists = (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) -ne $null
        return ($regExists -or $taskExists)
    }
}

if ($DaemonOn -or ($Daemon -eq "enable")) { Set-DaemonState "enable"; exit 0 }
if ($DaemonOff -or ($Daemon -eq "disable")) { Set-DaemonState "disable"; exit 0 }
if ($Daemon -eq "status" -or $Status) {
    $st = Set-DaemonState "status"
    Write-Host ("Auto-Healing Daemon Status: " + ($st ? "ENABLED" : "DISABLED"))
    exit ($st ? 0 : 1)
}

$i18nFile = Find-ClaudeI18nFile
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path $scriptPath -Parent }
$dictSource = if (Test-Path $cachedDict) { $cachedDict } else { Join-Path $scriptDir "dist\zh-CN.json" }

if ($Check) {
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "     Claude Desktop Chinese Patch Diagnostics             " -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  i18n File Location  :" ($i18nFile ? $i18nFile : "NOT FOUND")
    Write-Host "  Dictionary Location :" ($dictSource ? $dictSource : "NOT FOUND")
    Write-Host "  Auto-Healing Daemon :" ((Set-DaemonState "status") ? "ENABLED [OK]" : "DISABLED")
    Write-Host "==========================================================" -ForegroundColor Cyan
    exit ($i18nFile ? 0 : 1)
}

if ($RunOnce -or -not $RegisterTask) {
    if ($i18nFile -and $dictSource) {
        Apply-ClaudePatch -targetFile $i18nFile -dictFile $dictSource
    }
}

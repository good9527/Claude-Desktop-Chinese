param(
    [Parameter(Mandatory=$false)][Alias("i")][switch]$Install,
    [Parameter(Mandatory=$false)][Alias("u")][switch]$Uninstall,
    [Parameter(Mandatory=$false)][Alias("c")][switch]$Check,
    [Parameter(Mandatory=$false)][Alias("r")][switch]$Restore,
    [Parameter(Mandatory=$false)][ValidateSet("enable", "disable", "status", "")][string]$Daemon = "",
    [Parameter(Mandatory=$false)][switch]$DaemonOn,
    [Parameter(Mandatory=$false)][switch]$DaemonOff,
    [Parameter(Mandatory=$false)][Alias("q")][switch]$Quiet,
    [Parameter(Mandatory=$false)][switch]$Silent,
    [Parameter(Mandatory=$false)][Alias("p")][string]$Path,
    [Parameter(Mandatory=$false)][switch]$Json
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

if ($Silent) { $Quiet = $true }

$repoOwner = "good9527"
$repoName = "Claude-Desktop-Chinese"
$cacheDir = Join-Path $env:LOCALAPPDATA "Claude-Chinese-Patch"
$cachedDict = Join-Path $cacheDir "zh-CN.json"
$backupFile = Join-Path $cacheDir "en-US-original.json"
$regRunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$regRunName = "ClaudeDesktopChineseAutoHeal"
$taskName = "ClaudeDesktopChineseWatcher"

function Write-Msg {
    param([string]$Message, [string]$Color = "Gray")
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]$identity
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Start-ElevatedSelf {
    if (Test-IsAdmin) { return }
    Write-Msg "Requesting administrator permission..." "Yellow"
    $script = if ($PSCommandPath) { $PSCommandPath } else {
        $temp = Join-Path $env:TEMP "claude_install_elevated.ps1"
        $wc = New-Object System.Net.WebClient
        $wc.Encoding = [System.Text.Encoding]::UTF8
        $wc.DownloadFile("https://fastly.jsdelivr.net/gh/$repoOwner/$repoName@main/install.ps1", $temp)
        $temp
    }
    $args = "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
    $p = Start-Process powershell.exe -ArgumentList $args -Verb RunAs -PassThru
    $p.WaitForExit()
    exit $p.ExitCode
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

function Get-CdnFile {
    param([string]$relPath, [string]$dest)
    $mirrors = @(
        "https://fastly.jsdelivr.net/gh/$repoOwner/$repoName@main/$relPath",
        "https://cdn.jsdelivr.net/gh/$repoOwner/$repoName@main/$relPath",
        "https://ghfast.top/https://raw.githubusercontent.com/$repoOwner/$repoName/main/$relPath",
        "https://raw.githubusercontent.com/$repoOwner/$repoName/main/$relPath"
    )
    foreach ($url in $mirrors) {
        try {
            $wc = New-Object System.Net.WebClient
            $wc.Encoding = [System.Text.Encoding]::UTF8
            $wc.DownloadFile($url, $dest)
            if ((Test-Path $dest) -and (Get-Item $dest).Length -gt 100) {
                return $true
            }
        } catch {}
    }
    return $false
}

function Ensure-WritableFile {
    param([string]$FilePath)
    if (-not (Test-Path -LiteralPath $FilePath)) { return $false }
    try {
        $stream = [System.IO.File]::Open($FilePath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite)
        $stream.Close()
        return $true
    } catch {
        try {
            takeown.exe /F "$FilePath" /A | Out-Null
            icacls.exe "$FilePath" /grant "*S-1-5-32-544:F" | Out-Null
            icacls.exe "$FilePath" /grant "${env:USERNAME}:(F)" | Out-Null
            return $true
        } catch {
            return $false
        }
    }
}

function Set-DaemonState {
    param([string]$Action)
    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { $cacheDir }
    $watcherSrc = Join-Path $scriptDir "watcher\watcher.ps1"
    $watcherDst = Join-Path $cacheDir "watcher.ps1"

    if ($Action -eq "enable") {
        if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null }
        if (Test-Path $watcherSrc) { Copy-Item $watcherSrc $watcherDst -Force }
        $cmd = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$watcherDst`" -RunOnce -Quiet"
        Set-ItemProperty -Path $regRunKey -Name $regRunName -Value $cmd -Force -ErrorAction SilentlyContinue

        try {
            $actionObj = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$watcherDst`""
            $triggerObj = New-ScheduledTaskTrigger -AtLogOn
            $settingsObj = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0 -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
            $principalObj = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
            Register-ScheduledTask -TaskName $taskName -Action $actionObj -Trigger $triggerObj -Settings $settingsObj -Principal $principalObj -Force -ErrorAction SilentlyContinue | Out-Null
        } catch {}

        try {
            $runningWatcher = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { 
                ($_.CommandLine -like "*Claude*watcher.ps1*") -and $_.ProcessId -ne $PID 
            }
            if (-not $runningWatcher) {
                Start-Process -FilePath "powershell.exe" -ArgumentList "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$watcherDst`"" -WindowStyle Hidden
                Write-Msg "Background auto-healing watcher process spawned successfully (<10ms)!" "Green"
            }
        } catch {}

        return $true
    } elseif ($Action -eq "disable") {
        Remove-ItemProperty -Path $regRunKey -Name $regRunName -ErrorAction SilentlyContinue
        try { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}
        return $true
    } elseif ($Action -eq "status") {
        $regExists = (Get-ItemProperty -Path $regRunKey -Name $regRunName -ErrorAction SilentlyContinue) -ne $null
        $taskExists = (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) -ne $null
        return ($regExists -or $taskExists)
    }
}

function Invoke-InstallPatch {
    Start-ElevatedSelf

    Write-Msg "==========================================================" "Cyan"
    Write-Msg "     Claude Desktop Chinese Patch Universal Installer      " "Cyan"
    Write-Msg "     (Zero-Dependency Hot Patch + Auto-Healing Daemon)    " "Cyan"
    Write-Msg "==========================================================" "Cyan"

    $i18nFile = Find-ClaudeI18nFile
    if (-not $i18nFile) {
        throw "Could not locate Claude Desktop installation. Please ensure Claude is installed."
    }
    Write-Msg "Target language file: $i18nFile" "Green"

    if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null }

    # Backup original en-US.json
    if (-not (Test-Path $backupFile)) {
        Write-Msg "Creating original backup to $backupFile..." "Green"
        Copy-Item $i18nFile $backupFile -Force
    }

    # Resolve dictionary
    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { $null }
    $localDict = if ($scriptDir) { Join-Path $scriptDir "dist\zh-CN.json" } else { $null }

    if ($localDict -and (Test-Path $localDict)) {
        Write-Msg "Loading dictionary from local package..." "Green"
        Copy-Item $localDict $cachedDict -Force
    } elseif (Test-Path $cachedDict) {
        Write-Msg "Loading dictionary from offline cache..." "Green"
    } else {
        Write-Msg "Downloading dictionary via multi-mirror CDN..." "Green"
        $ok = Get-CdnFile "dist/zh-CN.json" $cachedDict
        if (-not $ok) { throw "Failed to download translation dictionary. Please check your network." }
    }

    # Merge & Patch
    Write-Msg "Applying in-place translation merge..." "Green"
    $enJsonStr = [System.IO.File]::ReadAllText($i18nFile, [System.Text.Encoding]::UTF8)
    $enObj = $enJsonStr | ConvertFrom-Json
    $zhJsonStr = [System.IO.File]::ReadAllText($cachedDict, [System.Text.Encoding]::UTF8)
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

    # Replace with retry
    Ensure-WritableFile $i18nFile | Out-Null
    $success = $false
    for ($i = 1; $i -le 5; $i++) {
        try {
            [System.IO.File]::WriteAllText($i18nFile, $mergedJson, [System.Text.Encoding]::UTF8)
            $success = $true
            break
        } catch {
            try {
                [System.IO.File]::Copy($tempFile, $i18nFile, $true)
                $success = $true
                break
            } catch {
                Start-Sleep -Milliseconds (300 * $i)
            }
        }
    }
    Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

    if (-not $success) {
        throw "Failed to update language file. Ensure you have administrator permissions."
    }

    # Setup Daemon
    Set-DaemonState "enable"

    Write-Msg ""
    Write-Msg "==========================================================" "Cyan"
    Write-Msg ("     [+] "+([char]0x6c49)+([char]0x5316)+([char]0x8865)+([char]0x4e01)+([char]0x5b89)+([char]0x88c5)+([char]0x6210)+([char]0x529f)+([char]0xff01)+"(Patch Successfully Installed) ") "Green"
    Write-Msg "==========================================================" "Cyan"
    Write-Msg ("  [*] "+([char]0x5df2)+([char]0x6c49)+([char]0x5316)+" $translated / $total "+([char]0x4e2a)+([char]0x8bed)+([char]0x8a00)+([char]0x8bcd)+([char]0x6761)+([char]0xff0c)+([char]0x5df2)+([char]0x5f00)+([char]0x542f)+([char]0x81ea)+([char]0x52a8)+([char]0x8ddf)+([char]0x968f)+([char]0x5b88)+([char]0x62a4)+([char]0xff01)) "Yellow"
    Write-Msg ("  [*] "+([char]0x91cd)+([char]0x542f)+" Claude Desktop "+([char]0x5373)+([char]0x53ef)+([char]0x67e5)+([char]0x770b)+([char]0x5b8c)+([char]0x6574)+([char]0x4e2d)+([char]0x6587)+([char]0x754c)+([char]0x9762)+([char]0x3002)) "Green"
    Write-Msg "==========================================================" "Cyan"
}

function Invoke-RestoreBackup {
    Start-ElevatedSelf
    $i18nFile = Find-ClaudeI18nFile
    if (-not $i18nFile -or -not (Test-Path $backupFile)) {
        throw "Backup file not found at $backupFile."
    }
    Copy-Item $backupFile $i18nFile -Force
    Write-Msg "Successfully restored official English language file!" "Green"
}

function Invoke-CheckDiagnostics {
    $i18nFile = Find-ClaudeI18nFile
    $hasBackup = Test-Path $backupFile
    $daemonActive = Set-DaemonState "status"

    if ($Json) {
        $data = @{
            i18nFile = $i18nFile
            hasBackup = $hasBackup
            daemonActive = $daemonActive
            healthy = ($i18nFile -ne $null)
        }
        return ($data | ConvertTo-Json)
    }

    Write-Msg "==========================================================" "Cyan"
    Write-Msg "     Claude Desktop Chinese Patch Diagnostics             " "Cyan"
    Write-Msg "==========================================================" "Cyan"
    Write-Msg "  Language File Location : $(if ($i18nFile) { $i18nFile } else { 'NOT FOUND' })"
    Write-Msg "  Original Backup File   : $(if ($hasBackup) { 'PRESENT [OK]' } else { 'MISSING' })"
    Write-Msg "  Auto-Healing Daemon    : $(if ($daemonActive) { 'ENABLED [OK]' } else { 'DISABLED' })"
    Write-Msg "==========================================================" "Cyan"
}

# Parameter Dispatcher
if ($Check) { Invoke-CheckDiagnostics; exit 0 }
if ($Restore -or $Uninstall) { Invoke-RestoreBackup; Set-DaemonState "disable"; exit 0 }
if ($DaemonOn -or ($Daemon -eq "enable")) { Set-DaemonState "enable"; exit 0 }
if ($DaemonOff -or ($Daemon -eq "disable")) { Set-DaemonState "disable"; exit 0 }

# Default
Invoke-InstallPatch

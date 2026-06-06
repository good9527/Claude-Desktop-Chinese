# ============================================================
#  Claude Desktop Chinese Language Patch Uninstaller
#  Restores the original English en-US.json backup
# ============================================================

$ErrorActionPreference = "Stop"

$RepositoryRawBase = "https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main"
$PatchDir = Join-Path $env:LOCALAPPDATA "Claude-Chinese-Patch"
$BackupFile = Join-Path $PatchDir "en-US-original.json"

function Write-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Color = "Yellow"
    )
    Write-Host ""
    Write-Host $Message -ForegroundColor $Color
}

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]$identity
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Add-Utf8Bom {
    param([Parameter(Mandatory = $true)][string]$Path)

    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 3 -or $bytes[0] -ne 0xEF -or $bytes[1] -ne 0xBB -or $bytes[2] -ne 0xBF) {
        [IO.File]::WriteAllBytes($Path, [byte[]]@(0xEF, 0xBB, 0xBF) + $bytes)
    }
}

function Start-ElevatedSelf {
    if (Test-IsAdmin) {
        return
    }

    Write-Host "  Requesting administrator permission..." -ForegroundColor Yellow
    Write-Host "  A new administrator PowerShell window will open." -ForegroundColor Gray

    if ($PSCommandPath) {
        $argumentList = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        $proc = Start-Process -FilePath "powershell.exe" -ArgumentList $argumentList -Verb RunAs -PassThru
        $proc.WaitForExit()
        exit $proc.ExitCode
    }

    $tempScript = Join-Path $env:TEMP "claude_zh_uninstall.ps1"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri "$RepositoryRawBase/uninstall.ps1" -OutFile $tempScript -UseBasicParsing
        Add-Utf8Bom -Path $tempScript
        $argumentList = "-NoProfile -ExecutionPolicy Bypass -File `"$tempScript`""
        $proc = Start-Process -FilePath "powershell.exe" -ArgumentList $argumentList -Verb RunAs -PassThru
        $proc.WaitForExit()
        exit $proc.ExitCode
    } catch {
        Write-Host "  ERROR: Failed to start elevated uninstaller: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Please open Windows Terminal as administrator and run the uninstall command again." -ForegroundColor Yellow
        exit 1
    } finally {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}

function Wait-ForExit {
    param([Parameter(Mandatory = $true)][string]$ProcessName)

    Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    for ($i = 1; $i -le 10; $i++) {
        Start-Sleep -Milliseconds 500
        if (-not (Get-Process -Name $ProcessName -ErrorAction SilentlyContinue)) {
            return
        }
    }
    throw "$ProcessName is still running. Please close it and run this script again."
}

function Get-ClaudePackage {
    $packages = @(Get-AppxPackage -Name "Claude" -ErrorAction SilentlyContinue)
    if ($packages.Count -eq 0) {
        $packages = @(Get-AppxPackage -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -eq "Claude" -or $_.Name -like "*Claude*"
        })
    }
    if ($packages.Count -eq 0) {
        throw "Claude Desktop was not found. Please install Claude from the Microsoft Store first."
    }
    return $packages | Sort-Object Version -Descending | Select-Object -First 1
}

function Get-I18nFile {
    param([Parameter(Mandatory = $true)]$Package)

    $candidate = Join-Path $Package.InstallLocation "app\resources\ion-dist\i18n\en-US.json"
    if (Test-Path -LiteralPath $candidate) {
        return $candidate
    }

    $found = Get-ChildItem -LiteralPath $Package.InstallLocation -Filter "en-US.json" -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\i18n\\en-US\.json$" } |
        Select-Object -First 1

    if (-not $found) {
        throw "Could not find Claude's en-US.json under: $($Package.InstallLocation)"
    }
    return $found.FullName
}

function Read-JsonObject {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "File not found: $Path"
    }

    $json = [IO.File]::ReadAllText($Path, [Text.Encoding]::UTF8)
    return $json | ConvertFrom-Json
}

function Copy-WithRetry {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    for ($i = 1; $i -le 5; $i++) {
        try {
            [IO.File]::Copy($Source, $Destination, $true)
            return
        } catch {
            if ($i -eq 5) {
                throw
            }
            Start-Sleep -Seconds 2
        }
    }
}

function Replace-ProtectedFile {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    try {
        Copy-WithRetry -Source $Source -Destination $Destination
        return
    } catch {
        Write-Host "  Direct restore failed, trying replace strategy..." -ForegroundColor DarkGray
    }

    $destinationDir = Split-Path $Destination -Parent
    $stagedFile = Join-Path $destinationDir ("en-US-restore-{0}.json" -f ([Guid]::NewGuid().ToString("N")))
    $moved = $false

    try {
        Copy-WithRetry -Source $Source -Destination $stagedFile
        Remove-Item -LiteralPath $Destination -Force -ErrorAction Stop
        if (Test-Path -LiteralPath $Destination) {
            throw "Could not delete patched file."
        }

        try {
            Move-Item -LiteralPath $stagedFile -Destination $Destination -Force -ErrorAction Stop
            $moved = $true
        } catch {
            throw "Could not move staged file into place. Staged file kept at: $stagedFile. $($_.Exception.Message)"
        }
    } finally {
        if ($moved -and (Test-Path -LiteralPath $stagedFile)) {
            Remove-Item -LiteralPath $stagedFile -Force -ErrorAction SilentlyContinue
        }
    }
}

Start-ElevatedSelf

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Claude Chinese Patch - Uninstall" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

try {
    if (-not (Test-Path -LiteralPath $BackupFile)) {
        throw "Backup file was not found: $BackupFile. Run the installer once to create a backup, or reinstall Claude from the Microsoft Store."
    }

    Write-Step "[1/4] Detecting Claude installation..."
    $claude = Get-ClaudePackage
    $enUsFile = Get-I18nFile -Package $claude
    Write-Host "  Found: Claude v$($claude.Version)" -ForegroundColor Green
    Write-Host "  Target: $enUsFile" -ForegroundColor Gray

    Write-Step "[2/4] Closing Claude..."
    Wait-ForExit -ProcessName "Claude"
    Write-Host "  Done." -ForegroundColor Green

    Write-Step "[3/4] Restoring original English..."
    $backupData = Read-JsonObject -Path $BackupFile
    $backupKeyCount = @($backupData.PSObject.Properties).Count

    Replace-ProtectedFile -Source $BackupFile -Destination $enUsFile

    $verifyData = Read-JsonObject -Path $enUsFile
    $verifyKeyCount = @($verifyData.PSObject.Properties).Count
    if ($verifyKeyCount -ne $backupKeyCount) {
        throw "Verification failed: expected $backupKeyCount keys, found $verifyKeyCount."
    }
    Write-Host "  Restored and verified." -ForegroundColor Green

    Write-Step "[4/4] Starting Claude..."
    $claudeExe = Join-Path $claude.InstallLocation "app\Claude.exe"
    if (Test-Path -LiteralPath $claudeExe) {
        Start-Process -FilePath $claudeExe -ErrorAction SilentlyContinue
        Write-Host "  Claude started." -ForegroundColor Green
    } else {
        Write-Host "  Claude.exe was not found; please start Claude manually." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  Done! Claude restored to English." -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit"

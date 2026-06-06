# ============================================================
#  Claude Desktop Chinese Language Patch Installer
#  One-click Chinese localization for Claude Desktop (Windows)
# ============================================================

$ErrorActionPreference = "Stop"

$RepositoryRawBase = "https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main"
$PatchDir = Join-Path $env:LOCALAPPDATA "Claude-Chinese-Patch"
$BackupFile = Join-Path $PatchDir "en-US-original.json"
$MetadataFile = Join-Path $PatchDir "metadata.json"
$DictionaryUrl = "$RepositoryRawBase/dist/zh-CN.json"

function Write-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Color = "Yellow"
    )
    Write-Host ""
    Write-Host $Message -ForegroundColor $Color
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

    $tempScript = Join-Path $env:TEMP "claude_zh_install.ps1"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri "$RepositoryRawBase/install.ps1" -OutFile $tempScript -UseBasicParsing
        Add-Utf8Bom -Path $tempScript
        $argumentList = "-NoProfile -ExecutionPolicy Bypass -File `"$tempScript`""
        $proc = Start-Process -FilePath "powershell.exe" -ArgumentList $argumentList -Verb RunAs -PassThru
        $proc.WaitForExit()
        exit $proc.ExitCode
    } catch {
        Write-Host "  ERROR: Failed to start elevated installer: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Please open Windows Terminal as administrator and run the install command again." -ForegroundColor Yellow
        exit 1
    } finally {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
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

    $candidates = @(
        (Join-Path $Package.InstallLocation "app\resources\ion-dist\i18n\en-US.json")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $found = Get-ChildItem -LiteralPath $Package.InstallLocation -Filter "en-US.json" -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\i18n\\en-US\.json$" } |
        Select-Object -First 1

    if (-not $found) {
        throw "Could not find Claude's en-US.json under: $($Package.InstallLocation)"
    }
    return $found.FullName
}

function Get-DictionaryFile {
    if ($PSScriptRoot) {
        $localCandidates = @(
            (Join-Path $PSScriptRoot "dist\zh-CN.json"),
            (Join-Path $PSScriptRoot "zh-CN-ion.json")
        )
        foreach ($candidate in $localCandidates) {
            if (Test-Path -LiteralPath $candidate) {
                Write-Host "  Using local dictionary: $candidate" -ForegroundColor Gray
                return $candidate
            }
        }
    }

    $downloadPath = Join-Path $env:TEMP "claude-zh-dict.json"
    Write-Host "  Downloading dictionary from GitHub..." -ForegroundColor Gray
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $DictionaryUrl -OutFile $downloadPath -UseBasicParsing
    return $downloadPath
}

function Read-JsonObject {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "File not found: $Path"
    }

    $json = [IO.File]::ReadAllText($Path, [Text.Encoding]::UTF8)
    return $json | ConvertFrom-Json
}

function ConvertTo-OrderedHashtable {
    param([Parameter(Mandatory = $true)]$Object)

    $ordered = [ordered]@{}
    foreach ($prop in $Object.PSObject.Properties) {
        $ordered[$prop.Name] = $prop.Value
    }
    return $ordered
}

function Write-JsonUtf8 {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $json = $Object | ConvertTo-Json -Depth 50 -Compress
    [IO.File]::WriteAllText($Path, $json, [Text.Encoding]::UTF8)
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
        Write-Host "  Direct write failed, trying replace strategy..." -ForegroundColor DarkGray
    }

    $destinationDir = Split-Path $Destination -Parent
    $stagedFile = Join-Path $destinationDir ("zh-CN-patched-{0}.json" -f ([Guid]::NewGuid().ToString("N")))
    $moved = $false

    try {
        Copy-WithRetry -Source $Source -Destination $stagedFile
        Remove-Item -LiteralPath $Destination -Force -ErrorAction Stop
        if (Test-Path -LiteralPath $Destination) {
            throw "Could not delete original file."
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

function Save-Metadata {
    param(
        [Parameter(Mandatory = $true)]$Package,
        [Parameter(Mandatory = $true)][string]$TargetFile,
        [Parameter(Mandatory = $true)][int]$SourceKeyCount,
        [Parameter(Mandatory = $true)][int]$TranslatedKeyCount,
        [Parameter(Mandatory = $true)][int]$ReplacedCount
    )

    $metadata = [ordered]@{
        installedAt = (Get-Date).ToString("o")
        claudePackageName = $Package.Name
        claudeVersion = $Package.Version.ToString()
        installLocation = $Package.InstallLocation
        targetFile = $TargetFile
        backupFile = $BackupFile
        sourceKeyCount = $SourceKeyCount
        translatedKeyCount = $TranslatedKeyCount
        replacedCount = $ReplacedCount
    }
    Write-JsonUtf8 -Object $metadata -Path $MetadataFile
}

Start-ElevatedSelf

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Claude Desktop Chinese Language Patch" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

try {
    Write-Step "[1/5] Detecting Claude installation..."
    $claude = Get-ClaudePackage
    $enUsFile = Get-I18nFile -Package $claude
    Write-Host "  Found: Claude v$($claude.Version)" -ForegroundColor Green
    Write-Host "  Target: $enUsFile" -ForegroundColor Gray

    Write-Step "[2/5] Closing Claude..."
    Wait-ForExit -ProcessName "Claude"
    Write-Host "  Done." -ForegroundColor Green

    Write-Step "[3/5] Backing up original en-US.json..."
    New-Item -ItemType Directory -Path $PatchDir -Force | Out-Null
    if (-not (Test-Path -LiteralPath $BackupFile)) {
        Copy-WithRetry -Source $enUsFile -Destination $BackupFile
        Write-Host "  Backup saved to: $BackupFile" -ForegroundColor Green
    } else {
        Write-Host "  Backup already exists, keeping it." -ForegroundColor Gray
    }

    Write-Step "[4/5] Applying Chinese translations..."
    $dictFile = Get-DictionaryFile
    $enData = Read-JsonObject -Path $enUsFile
    $zhData = Read-JsonObject -Path $dictFile

    $zhMap = ConvertTo-OrderedHashtable -Object $zhData
    $merged = [ordered]@{}
    $replacedCount = 0

    foreach ($prop in $enData.PSObject.Properties) {
        if ($zhMap.Contains($prop.Name)) {
            $merged[$prop.Name] = $zhMap[$prop.Name]
            $replacedCount++
        } else {
            $merged[$prop.Name] = $prop.Value
        }
    }

    $sourceKeyCount = @($enData.PSObject.Properties).Count
    $translatedKeyCount = @($zhData.PSObject.Properties).Count
    Write-Host "  Replaced $replacedCount / $sourceKeyCount strings" -ForegroundColor Green

    $tempFile = Join-Path $env:TEMP ("claude-zh-patch-{0}.json" -f ([Guid]::NewGuid().ToString("N")))
    Write-JsonUtf8 -Object $merged -Path $tempFile

    try {
        Replace-ProtectedFile -Source $tempFile -Destination $enUsFile
    } finally {
        Remove-Item -LiteralPath $tempFile -Force -ErrorAction SilentlyContinue
    }

    $verifyData = Read-JsonObject -Path $enUsFile
    $verifyCount = @($verifyData.PSObject.Properties).Count
    if ($verifyCount -ne $sourceKeyCount) {
        throw "Verification failed: expected $sourceKeyCount keys, found $verifyCount."
    }

    Save-Metadata -Package $claude -TargetFile $enUsFile -SourceKeyCount $sourceKeyCount -TranslatedKeyCount $translatedKeyCount -ReplacedCount $replacedCount
    Write-Host "  Patch applied and verified." -ForegroundColor Green

    Write-Step "[5/5] Starting Claude..."
    $claudeExe = Join-Path $claude.InstallLocation "app\Claude.exe"
    if (Test-Path -LiteralPath $claudeExe) {
        Start-Process -FilePath $claudeExe -ErrorAction SilentlyContinue
        Write-Host "  Claude started." -ForegroundColor Green
    } else {
        Write-Host "  Claude.exe was not found; please start Claude manually." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  Done! Claude is now in Chinese." -ForegroundColor Cyan
    Write-Host "  To restore English, run uninstall.ps1" -ForegroundColor Gray
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Backup location: $BackupFile" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit"

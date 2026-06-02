# ============================================================
#  Claude Desktop Chinese Language Patch Installer
#  Supports: online (iwr | iex) and local (double-click .bat)
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Claude Desktop Chinese Language Patch" -ForegroundColor Cyan
Write-Host "  Claude 桌面版中文汉化补丁" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Detect Claude ---
Write-Host "[1/5] Detecting Claude..." -ForegroundColor Yellow
$claude = Get-AppxPackage -Name 'Claude' -ErrorAction SilentlyContinue
if (-not $claude) {
    Write-Host "  ERROR: Claude Desktop not found!" -ForegroundColor Red
    Write-Host "  Please install Claude from Microsoft Store first." -ForegroundColor Red
    Write-Host "  请先从 Microsoft Store 安装 Claude Desktop。" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
$installDir = $claude.InstallLocation
$enUsFile = Join-Path $installDir "app\resources\ion-dist\i18n\en-US.json"
Write-Host "  Found Claude v$($claude.Version)" -ForegroundColor Green

if (-not (Test-Path $enUsFile)) {
    Write-Host "  ERROR: en-US.json not found at: $enUsFile" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# --- Step 2: Load translation dictionary ---
Write-Host ""
Write-Host "[2/5] Loading translations..." -ForegroundColor Yellow

# Try local path first, then download from GitHub
$dictFile = $null
if ($PSScriptRoot) {
    $localDict = Join-Path $PSScriptRoot "dist\zh-CN.json"
    if (Test-Path $localDict) {
        $dictFile = $localDict
    }
}
if (-not $dictFile) {
    # Online mode: download from GitHub
    Write-Host "  Downloading zh-CN.json from GitHub..." -ForegroundColor Gray
    $dictUrl = "https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/dist/zh-CN.json"
    $dictFile = Join-Path $env:TEMP "claude-zh-dict.json"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $dictUrl -OutFile $dictFile -UseBasicParsing
        Write-Host "  Downloaded." -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Failed to download - $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

$zhData = [IO.File]::ReadAllText($dictFile) | ConvertFrom-Json
Write-Host "  Loaded $($zhData.PSObject.Properties.Count) translations." -ForegroundColor Green

# --- Step 3: Close Claude ---
Write-Host ""
Write-Host "[3/5] Closing Claude..." -ForegroundColor Yellow
Get-Process -Name 'Claude' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "  Done." -ForegroundColor Green

# --- Step 4: Backup & merge ---
Write-Host ""
Write-Host "[4/5] Applying Chinese..." -ForegroundColor Yellow

# Backup
$backupDir = Join-Path $env:USERPROFILE "AppData\Local\Claude-Chinese-Patch"
$backupFile = Join-Path $backupDir "en-US-original.json"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}
if (-not (Test-Path $backupFile)) {
    [IO.File]::Copy($enUsFile, $backupFile, $true)
    Write-Host "  Backup saved." -ForegroundColor Gray
}

# Merge
$enData = [IO.File]::ReadAllText($enUsFile) | ConvertFrom-Json
$merged = @{}
$count = 0
foreach ($prop in $enData.PSObject.Properties) {
    if ($zhData.PSObject.Properties[$prop.Name]) {
        $merged[$prop.Name] = $zhData.PSObject.Properties[$prop.Name].Value
        $count++
    } else {
        $merged[$prop.Name] = $prop.Value
    }
}
Write-Host "  Replaced $count / $($enData.PSObject.Properties.Count) strings" -ForegroundColor Green

# Write to temp then copy (bypass WindowsApps protection)
$tempFile = Join-Path $env:TEMP "claude-zh-patch.json"
$merged | ConvertTo-Json -Depth 10 -Compress | Set-Content $tempFile -Encoding UTF8

# Try multiple times with retry
$success = $false
for ($i = 1; $i -le 5; $i++) {
    try {
        [IO.File]::Copy($tempFile, $enUsFile, $true)
        $success = $true
        break
    } catch {
        Start-Sleep -Seconds 2
    }
}
Remove-Item $tempFile -ErrorAction SilentlyContinue

if (-not $success) {
    Write-Host "  ERROR: Failed to write. File may be locked." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "  Patch applied!" -ForegroundColor Green

# --- Step 5: Start Claude (detached) ---
Write-Host ""
Write-Host "[5/5] Starting Claude..." -ForegroundColor Yellow
$claudeExe = Join-Path $installDir "app\Claude.exe"
if (Test-Path $claudeExe) {
    Start-Process "cmd.exe" -ArgumentList "/c start `"`" `"$claudeExe`"" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Write-Host "  Claude started." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Done! Claude is now in Chinese." -ForegroundColor Cyan
Write-Host "  完成！Claude 已切换为中文界面。" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

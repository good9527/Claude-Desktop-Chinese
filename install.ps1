# ============================================================
#  Claude Desktop Chinese Language Patch Installer
#  One-click Chinese localization for Claude Desktop (Windows)
# ============================================================

$ErrorActionPreference = "Stop"

# --- Auto-elevate to admin if needed (required for WindowsApps write) ---
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "  需要管理员权限，正在请求提权..." -ForegroundColor Yellow
    Write-Host "  请在弹出的 UAC 窗口点击'是'" -ForegroundColor Cyan
    Write-Host ""
    $tempScript = Join-Path $env:TEMP "claude_zh_install.ps1"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/good9527/Claude-Desktop-Chinese/main/install.ps1" -OutFile $tempScript -UseBasicParsing
    try {
        Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$tempScript`"" -Verb RunAs -Wait
    } catch {
        Write-Host "  [ERROR] 提权失败，请手动右键管理员运行。" -ForegroundColor Red
    }
    Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    exit 0
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Claude Desktop Chinese Language Patch" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# --- Config ---
$patchDir = Join-Path $env:LOCALAPPDATA "Claude-Chinese-Patch"
$backupFile = Join-Path $patchDir "en-US-original.json"

# --- Step 1: Detect Claude installation ---
Write-Host "[1/5] Detecting Claude installation..." -ForegroundColor Yellow
$claude = Get-AppxPackage -Name 'Claude' -ErrorAction SilentlyContinue
if (-not $claude) {
    Write-Host "  ERROR: Claude Desktop not found!" -ForegroundColor Red
    Write-Host "  Please install Claude from the Microsoft Store first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
$installDir = $claude.InstallLocation
$i18nDir = Join-Path $installDir "app\resources\ion-dist\i18n"
$enUsFile = Join-Path $i18nDir "en-US.json"
Write-Host "  Found: Claude v$($claude.Version)" -ForegroundColor Green

# --- Step 2: Close Claude ---
Write-Host ""
Write-Host "[2/5] Closing Claude..." -ForegroundColor Yellow
Get-Process -Name 'Claude' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "  Done." -ForegroundColor Green

# --- Step 3: Backup original en-US.json ---
Write-Host ""
Write-Host "[3/5] Backing up original en-US.json..." -ForegroundColor Yellow
if (-not (Test-Path $patchDir)) {
    New-Item -ItemType Directory -Path $patchDir -Force | Out-Null
}
if (-not (Test-Path $backupFile)) {
    # First install: save original English file
    [IO.File]::Copy($enUsFile, $backupFile, $true)
    Write-Host "  Backup saved to: $backupFile" -ForegroundColor Green
} else {
    Write-Host "  Backup already exists, keeping it." -ForegroundColor Gray
}

# --- Step 4: Merge translations ---
Write-Host ""
Write-Host "[4/5] Applying Chinese translations..." -ForegroundColor Yellow

$dictFile = $null
if ($PSScriptRoot) {
    $localDict = Join-Path $PSScriptRoot "dist\zh-CN.json"
    if (Test-Path $localDict) {
        $dictFile = $localDict
    }
}
if (-not $dictFile) {
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
if (-not (Test-Path $dictFile)) {
    Write-Host "  ERROR: zh-CN.json not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Read source files
$enData = [IO.File]::ReadAllText($enUsFile) | ConvertFrom-Json
$zhData = [IO.File]::ReadAllText($dictFile) | ConvertFrom-Json

# Merge: replace English values with Chinese
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

# Write to temp file first
$tempFile = Join-Path $env:TEMP "claude-zh-patch.json"
$merged | ConvertTo-Json -Depth 10 -Compress | Set-Content $tempFile -Encoding UTF8

# Copy to target (bypass WindowsApps protection)
[IO.File]::Copy($tempFile, $enUsFile, $true)
Remove-Item $tempFile -ErrorAction SilentlyContinue
Write-Host "  Patch applied!" -ForegroundColor Green

# --- Step 5: Start Claude (detached) ---
Write-Host ""
Write-Host "[5/5] Starting Claude..." -ForegroundColor Yellow
$claudeExe = Join-Path $installDir "app\Claude.exe"
if (Test-Path $claudeExe) {
    # Use cmd start to fully detach from this console session
    Start-Process "cmd.exe" -ArgumentList "/c start `"`" `"$claudeExe`"" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Write-Host "  Claude started (detached)." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Done! Claude is now in Chinese." -ForegroundColor Cyan
Write-Host "  To restore English, run uninstall.ps1" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  窗口将在5秒后自动关闭..." -ForegroundColor Gray
Start-Sleep -Seconds 5

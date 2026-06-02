# ============================================================
#  Claude Desktop Chinese Language Patch - Uninstaller
#  Restores Claude Desktop to original English
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Claude Chinese Patch - Uninstall" -ForegroundColor Cyan
Write-Host "  Claude 中文补丁 - 卸载还原" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Detect Claude ---
Write-Host "[1/3] Detecting Claude..." -ForegroundColor Yellow
$claude = Get-AppxPackage -Name 'Claude' -ErrorAction SilentlyContinue
if (-not $claude) {
    Write-Host "  ERROR: Claude Desktop not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
$installDir = $claude.InstallLocation
$enUsFile = Join-Path $installDir "app\resources\ion-dist\i18n\en-US.json"
Write-Host "  Found Claude v$($claude.Version)" -ForegroundColor Green

# --- Step 2: Close Claude ---
Write-Host ""
Write-Host "[2/3] Closing Claude..." -ForegroundColor Yellow
Get-Process -Name 'Claude' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
Write-Host "  Done." -ForegroundColor Green

# --- Step 3: Restore backup ---
Write-Host ""
Write-Host "[3/3] Restoring English..." -ForegroundColor Yellow

$backupFile = Join-Path $env:USERPROFILE "AppData\Local\Claude-Chinese-Patch\en-US-original.json"
if (-not (Test-Path $backupFile)) {
    Write-Host "  ERROR: Backup not found." -ForegroundColor Red
    Write-Host "  You may need to reinstall Claude." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Retry logic
$success = $false
for ($i = 1; $i -le 5; $i++) {
    try {
        [IO.File]::Copy($backupFile, $enUsFile, $true)
        $success = $true
        break
    } catch {
        Write-Host "  Attempt $i failed, retrying..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
}

if (-not $success) {
    Write-Host "  ERROR: All attempts failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "  Restored successfully!" -ForegroundColor Green

# --- Start Claude (detached) ---
$claudeExe = Join-Path $installDir "app\Claude.exe"
if (Test-Path $claudeExe) {
    Start-Process "cmd.exe" -ArgumentList "/c start `"`" `"$claudeExe`"" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Write-Host "  Claude started." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Done! Claude restored to English." -ForegroundColor Cyan
Write-Host "  完成！Claude 已恢复英文界面。" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

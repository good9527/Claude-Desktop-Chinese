# ============================================================
#  Claude Desktop Chinese Language Patch - Uninstaller
# ============================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Claude Chinese Patch - Uninstall" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# --- Config ---
$patchDir = "$env:USERPROFILE\AppData\Local\Claude-Chinese-Patch"
$backupFile = Join-Path $patchDir "en-US-original.json"

Write-Host "[DEBUG] USERPROFILE: $env:USERPROFILE" -ForegroundColor Gray
Write-Host "[DEBUG] patchDir: $patchDir" -ForegroundColor Gray
Write-Host "[DEBUG] Backup path: $backupFile" -ForegroundColor Gray
Write-Host "[DEBUG] Dir exists: $(Test-Path $patchDir)" -ForegroundColor Gray
Write-Host "[DEBUG] File exists: $(Test-Path -LiteralPath $backupFile)" -ForegroundColor Gray
# List files in the directory
if (Test-Path $patchDir) {
    Get-ChildItem $patchDir | ForEach-Object { Write-Host "[DEBUG] Found: $($_.Name) ($($_.Length) bytes)" -ForegroundColor Gray }
}

# --- Step 1: Detect Claude ---
Write-Host ""
Write-Host "[1/3] Detecting Claude..." -ForegroundColor Yellow
$claude = Get-AppxPackage -Name 'Claude' -ErrorAction SilentlyContinue
if (-not $claude) {
    Write-Host "  ERROR: Claude not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
$installDir = $claude.InstallLocation
$enUsFile = Join-Path $installDir "app\resources\ion-dist\i18n\en-US.json"
Write-Host "  Found: Claude v$($claude.Version)" -ForegroundColor Green
Write-Host "[DEBUG] Target: $enUsFile" -ForegroundColor Gray

# --- Step 2: Close Claude ---
Write-Host ""
Write-Host "[2/3] Closing Claude..." -ForegroundColor Yellow
Get-Process -Name 'Claude' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 4
$stillRunning = Get-Process -Name 'Claude' -ErrorAction SilentlyContinue
if ($stillRunning) {
    Write-Host "  WARNING: Claude still running! Trying harder..." -ForegroundColor Red
    $stillRunning | Stop-Process -Force
    Start-Sleep -Seconds 3
}
Write-Host "  Done." -ForegroundColor Green

# --- Step 3: Restore backup ---
Write-Host ""
Write-Host "[3/3] Restoring original English..." -ForegroundColor Yellow
if (-not (Test-Path $backupFile)) {
    Write-Host "  ERROR: Backup file not found at:" -ForegroundColor Red
    Write-Host "  $backupFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Tip: Run install.bat first to create the backup." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    # Try multiple times with delay (file may still be locked)
    $success = $false
    for ($i = 1; $i -le 5; $i++) {
        try {
            [IO.File]::Copy($backupFile, $enUsFile, $true)
            $success = $true
            break
        } catch {
            Write-Host "  Attempt $i failed, retrying in 3s..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        }
    }
    if (-not $success) {
        Write-Host "  ERROR: All attempts failed. File may be locked." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "  Restored successfully!" -ForegroundColor Green

    # Verify
    $verify = Get-Content $enUsFile -TotalCount 5
    Write-Host ""
    Write-Host "  First 5 lines of restored file:" -ForegroundColor Gray
    $verify | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} catch {
    Write-Host "  ERROR: Failed to copy - $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# --- Start Claude (detached) ---
Write-Host ""
Write-Host "Starting Claude..." -ForegroundColor Yellow
$claudeExe = Join-Path $installDir "app\Claude.exe"
if (Test-Path $claudeExe) {
    Start-Process "cmd.exe" -ArgumentList "/c start `"`" `"$claudeExe`"" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Write-Host "  Claude started (detached)." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Done! Claude restored to English." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"

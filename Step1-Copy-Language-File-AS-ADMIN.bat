@echo off
echo ==========================================
echo  Step 1: Copy zh-CN.json (Run as Admin)
echo ==========================================
echo.
echo This will close Claude, copy the file, then restart it.
echo Please save your work first!
echo.
pause

:: Auto-detect Claude install path
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Get-AppxPackage | Where-Object { $_.Name -eq 'Claude' } | Select-Object -ExpandProperty InstallLocation"`) do set "CLAUDE_DIR=%%I"

if "%CLAUDE_DIR%"=="" (
    echo [ERROR] Claude installation not found.
    pause
    exit /b 1
)
echo Found Claude at: %CLAUDE_DIR%

set "RES_DIR=%CLAUDE_DIR%\app\resources"
set "CLAUDE_EXE=%CLAUDE_DIR%\app\Claude.exe"

echo.
echo Closing Claude...
taskkill /IM claude.exe /F >nul 2>&1
ping 127.0.0.1 -n 4 >nul

echo Copying zh-CN.json...
powershell -NoProfile -Command ^
    "Copy-Item -Path '%~dp0zh-CN.json' -Destination '%RES_DIR%\zh-CN.json' -Force; if(Test-Path '%RES_DIR%\zh-CN.json'){Write-Host '  SUCCESS!'} else {Write-Host '  FAILED - file could not be copied'}"

echo.
echo Starting Claude...
start "" "%CLAUDE_EXE%"

echo.
echo Done! Now run Step 2 (no admin needed).
echo.
pause

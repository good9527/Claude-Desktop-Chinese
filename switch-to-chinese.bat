@echo off
echo ==========================================
echo   Claude Chinese Language Switcher
echo ==========================================
echo.

:: Auto-detect Claude install path
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Get-AppxPackage | Where-Object { $_.Name -eq 'Claude' } | Select-Object -ExpandProperty InstallLocation"`) do set "CLAUDE_DIR=%%I"

if "%CLAUDE_DIR%"=="" (
    echo [ERROR] Claude installation not found.
    pause
    exit /b 1
)

set "CLAUDE_EXE=%CLAUDE_DIR%\app\Claude.exe"

echo [1/3] Closing Claude...
taskkill /IM claude.exe /F >nul 2>&1
ping 127.0.0.1 -n 3 >nul
echo       Done.

echo.
echo [2/3] Setting locale to zh-CN...
powershell -NoProfile -Command "$f='C:\Users\19901\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\config.json'; if(Test-Path $f){ $c=[IO.File]::ReadAllText($f); $c=$c -replace '\"locale\":\s*\"[^\"]*\"','\"locale\": \"zh-CN\"'; [IO.File]::WriteAllText($f,$c); Write-Host '       Done! locale set to zh-CN' } else { Write-Host '       [ERROR] config.json not found' }"

echo.
echo [3/3] Starting Claude...
start "" "%CLAUDE_EXE%"

echo.
echo ==========================================
echo   Done! Claude should be in Chinese now.
echo ==========================================
echo.
pause

@echo off
echo ==========================================
echo   Deploy Claude Chinese Translation
echo ==========================================
echo.
echo This will close Claude and install Chinese.
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

set "I18N=%CLAUDE_DIR%\app\resources\ion-dist\i18n"
set "RES=%CLAUDE_DIR%\app\resources"
set "CLAUDE_EXE=%CLAUDE_DIR%\app\Claude.exe"

echo.
echo [1/4] Closing Claude...
taskkill /IM claude.exe /F >nul 2>&1
ping 127.0.0.1 -n 4 >nul
echo       Done.

echo.
echo [2/4] Copying zh-CN.json to ion-dist/i18n/...
powershell -NoProfile -Command "Copy-Item -Path '%~dp0zh-CN-ion.json' -Destination '%I18N%\zh-CN.json' -Force; if(Test-Path '%I18N%\zh-CN.json'){Write-Host '       zh-CN.json -> ion-dist OK'}else{Write-Host '       [FAIL]'}"

echo.
echo [3/4] Copying zh-CN.json to resources/...
powershell -NoProfile -Command "Copy-Item -Path '%~dp0zh-CN-ion.json' -Destination '%RES%\zh-CN.json' -Force; if(Test-Path '%RES%\zh-CN.json'){Write-Host '       zh-CN.json -> resources OK'}else{Write-Host '       [FAIL]'}"

echo.
echo [4/4] Setting locale in config...
set "CONFIG=C:\Users\19901\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\config.json"
powershell -NoProfile -Command "$f='%CONFIG%'; if(Test-Path $f){ $c=[IO.File]::ReadAllText($f); $c=$c -replace '\"locale\":\s*\"[^\"]*\"','\"locale\": \"zh-CN\"'; [IO.File]::WriteAllText($f,$c); Write-Host '       locale -> zh-CN' } else { Write-Host '       [WARN] config not found' }"

echo.
echo Starting Claude...
start "" "%CLAUDE_EXE%"

echo.
echo ==========================================
echo   Done! Claude should now be in Chinese!
echo   15170 strings translated (99.6%% coverage)
echo ==========================================
echo.
pause

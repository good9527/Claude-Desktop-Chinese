@echo off
chcp 65001 >nul
echo ==========================================
echo    Claude 桌面版中文汉化工具
echo ==========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请右键此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

:: 自动检测 Claude 安装路径
echo [0/4] 正在检测 Claude 安装路径...
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Get-AppxPackage | Where-Object { $_.Name -eq 'Claude' } | Select-Object -ExpandProperty InstallLocation"`) do set "CLAUDE_DIR=%%I"

if "%CLAUDE_DIR%"=="" (
    echo       [错误] 未找到 Claude 安装，请确认已安装 Claude 桌面版。
    pause
    exit /b 1
)
echo       找到: %CLAUDE_DIR%

set "RES_DIR=%CLAUDE_DIR%\app\resources"
set "CLAUDE_EXE=%CLAUDE_DIR%\app\Claude.exe"

echo.
echo [1/4] 正在关闭 Claude...
taskkill /IM claude.exe /F >nul 2>&1
timeout /t 3 /nobreak >nul
echo       已关闭。

echo.
echo [2/4] 正在复制中文语言文件...
set "SOURCE=%~dp0zh-CN.json"
set "DEST=%RES_DIR%\zh-CN.json"

:: 先获取目录权限
takeown /f "%RES_DIR%" /a >nul 2>&1
icacls "%RES_DIR%" /grant Administrators:F >nul 2>&1

copy /Y "%SOURCE%" "%DEST%" >nul 2>&1
if exist "%DEST%" (
    echo       成功！zh-CN.json 已写入。
) else (
    echo       自动写入失败，尝试便携版方案...
    echo.
    echo [备选] 启动便携版 Claude...
    start "" "%~dp0..\AppData\Local\Claude-Portable\Claude.exe"
    echo       便携版已启动！
    echo.
    echo ==========================================
    echo       汉化完成（便携版模式）
    echo ==========================================
    pause
    exit /b 0
)

echo.
echo [3/4] 正在重启 Claude...
start "" "%CLAUDE_EXE%"

echo.
echo [4/4] 切换语言...
echo       请在 Claude 中进入: 设置(Settings) > 语言(Language)
echo       选择"中文(简体)" / "zh-CN"
echo.
echo ==========================================
echo       汉化完成！请手动切换语言为中文
echo ==========================================
echo.
pause

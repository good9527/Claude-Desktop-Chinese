@echo off
echo.
echo ==========================================
echo   Claude Desktop Chinese Language Patch
echo ==========================================
echo.
echo This will patch Claude Desktop to show Chinese.
echo.
choice /C YN /M "Continue?"
if errorlevel 2 exit

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"

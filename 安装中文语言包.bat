@echo off
chcp 65001 >nul
echo 此旧入口现在会使用维护中的安装器。
echo.
call "%~dp0install.bat"

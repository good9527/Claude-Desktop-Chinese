@echo off
chcp 65001 >nul
title Claude Desktop 中文汉化管理工具
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0patch_claude.ps1"
pause

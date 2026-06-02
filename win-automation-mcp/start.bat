@echo off
REM Windows Automation MCP Server Launcher
REM 启动 Windows 自动化 MCP 服务器

cd /d "%~dp0"
python server.py %*

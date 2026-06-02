@echo off
mkdir "%USERPROFILE%\AppData\Local\Claude-Chinese-Patch" 2>nul
copy "%USERPROFILE%\Desktop\claude-en-backup.json" "%USERPROFILE%\AppData\Local\Claude-Chinese-Patch\en-US-original.json" /Y
dir "%USERPROFILE%\AppData\Local\Claude-Chinese-Patch\"
pause

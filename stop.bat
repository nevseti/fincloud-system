@echo off
chcp 65001 >nul
echo Stopping FinCloud...
powershell -ExecutionPolicy Bypass -File "scripts\swarm-stop.ps1"
pause

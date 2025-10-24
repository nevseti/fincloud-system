@echo off
echo ⏹️ Остановка FinCloud...
powershell -ExecutionPolicy Bypass -File "scripts\swarm-stop.ps1"
pause

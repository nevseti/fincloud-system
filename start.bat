@echo off
chcp 65001 >nul
echo Starting FinCloud...
powershell -ExecutionPolicy Bypass -File "scripts\swarm-deploy.ps1"
pause

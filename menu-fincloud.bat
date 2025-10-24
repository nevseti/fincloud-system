@echo off
chcp 65001 >nul
echo ========================================
echo    FinCloud System - Quick Actions
echo ========================================
echo.

echo Choose an action:
echo.
echo [1] Start FinCloud
echo [2] Stop FinCloud
echo [3] Check Status
echo [4] View Logs
echo [5] Open Application
echo [6] Open API Documentation
echo [7] Restart Services
echo [8] Clean System
echo [0] Exit
echo.

set /p choice="Enter number (0-8): "

if "%choice%"=="1" (
    call start-fincloud.bat
) else if "%choice%"=="2" (
    call stop-fincloud.bat
) else if "%choice%"=="3" (
    call status-fincloud.bat
) else if "%choice%"=="4" (
    call logs-fincloud.bat
) else if "%choice%"=="5" (
    echo Opening application...
    start http://localhost:8080
    echo Application opened in browser
    pause
) else if "%choice%"=="6" (
    echo Opening API documentation...
    start http://localhost:8000/docs
    echo API documentation opened in browser
    pause
) else if "%choice%"=="7" (
    echo Restarting services...
    call stop-fincloud.bat
    timeout /t 3 /nobreak >nul
    call start-fincloud.bat
) else if "%choice%"=="8" (
    echo Cleaning system...
    docker system prune -a -f
    docker volume prune -f
    echo System cleaned
    pause
) else if "%choice%"=="0" (
    exit /b 0
) else (
    echo Invalid choice!
    pause
)

echo.
echo For quick access to menu use: menu-fincloud.bat
echo.
pause

@echo off
echo ========================================
echo    FinCloud System - Quick Actions
echo ========================================
echo.

echo Выберите действие:
echo.
echo [1] 🚀 Запустить FinCloud
echo [2] ⏹️  Остановить FinCloud
echo [3] 📊 Проверить статус
echo [4] 📋 Посмотреть логи
echo [5] 🌐 Открыть приложение
echo [6] 📚 Открыть API документацию
echo [7] 🔄 Перезапустить сервисы
echo [8] 🧹 Очистить систему
echo [0] Выход
echo.

set /p choice="Введите номер (0-8): "

if "%choice%"=="1" (
    call start-fincloud.bat
) else if "%choice%"=="2" (
    call stop-fincloud.bat
) else if "%choice%"=="3" (
    call status-fincloud.bat
) else if "%choice%"=="4" (
    call logs-fincloud.bat
) else if "%choice%"=="5" (
    echo 🌐 Открываю приложение...
    start http://localhost:8080
    echo ✅ Приложение открыто в браузере
    pause
) else if "%choice%"=="6" (
    echo 📚 Открываю API документацию...
    start http://localhost:8000/docs
    echo ✅ API документация открыта в браузере
    pause
) else if "%choice%"=="7" (
    echo 🔄 Перезапускаю сервисы...
    call stop-fincloud.bat
    timeout /t 3 /nobreak >nul
    call start-fincloud.bat
) else if "%choice%"=="8" (
    echo 🧹 Очищаю систему...
    docker system prune -a -f
    docker volume prune -f
    echo ✅ Система очищена
    pause
) else if "%choice%"=="0" (
    exit /b 0
) else (
    echo ❌ Неверный выбор!
    pause
)

echo.
echo 💡 Для быстрого доступа к меню используйте: menu-fincloud.bat
echo.
pause

# Скрипт для запуска тестов локально (PowerShell)

Write-Host "🧪 Запуск тестов FinCloud..." -ForegroundColor Green

# Устанавливаем переменные окружения для тестов
$env:AUTH_DATABASE_URL = "sqlite:///./test_auth.db"
$env:FINANCE_DATABASE_URL = "sqlite:///./test_finance.db"

# Устанавливаем pytest если не установлен
Write-Host "📦 Устанавливаем зависимости для тестов..." -ForegroundColor Yellow
pip install pytest pytest-asyncio httpx

# Запускаем функциональные тесты
Write-Host "🔍 Запуск функциональных тестов Auth Service..." -ForegroundColor Cyan
Set-Location auth-service
python -m pytest tests/test_auth_functional.py -v
Set-Location ..

Write-Host "🔍 Запуск функциональных тестов Finance Service..." -ForegroundColor Cyan
Set-Location finance-service  
python -m pytest tests/test_finance_functional.py -v
Set-Location ..

# Запускаем тесты базы данных
Write-Host "🗄️ Запуск тестов базы данных..." -ForegroundColor Cyan
python -m pytest tests/test_database.py -v

Write-Host "✅ Все тесты завершены!" -ForegroundColor Green

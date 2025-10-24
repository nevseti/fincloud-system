#!/bin/bash
# Скрипт для запуска тестов локально

echo "🧪 Запуск тестов FinCloud..."

# Устанавливаем переменные окружения для тестов
export AUTH_DATABASE_URL="sqlite:///./test_auth.db"
export FINANCE_DATABASE_URL="sqlite:///./test_finance.db"

# Устанавливаем pytest если не установлен
echo "📦 Устанавливаем зависимости для тестов..."
pip install pytest pytest-asyncio httpx

# Запускаем функциональные тесты
echo "🔍 Запуск функциональных тестов Auth Service..."
cd auth-service
python -m pytest tests/test_auth_functional.py -v
cd ..

echo "🔍 Запуск функциональных тестов Finance Service..."
cd finance-service  
python -m pytest tests/test_finance_functional.py -v
cd ..

# Запускаем тесты базы данных
echo "🗄️ Запуск тестов базы данных..."
python -m pytest tests/test_database.py -v

echo "✅ Все тесты завершены!"

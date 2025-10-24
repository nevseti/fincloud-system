# 🧪 FinCloud Testing Guide

Этот документ описывает систему тестирования проекта FinCloud.

## 📁 Структура тестов

```
tests/
├── test_integration.py      # Интеграционные тесты между сервисами
├── test_database.py         # Тесты базы данных
auth-service/tests/
├── test_auth_functional.py # Функциональные тесты Auth Service
finance-service/tests/
├── test_finance_functional.py # Функциональные тесты Finance Service
```

## 🚀 Запуск тестов

### Локально

1. **Установите зависимости для тестов:**
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Запустите все тесты:**
   ```bash
   # Функциональные тесты Auth Service
   cd auth-service && python -m pytest tests/test_auth_functional.py -v
   
   # Функциональные тесты Finance Service  
   cd finance-service && python -m pytest tests/test_finance_functional.py -v
   
   # Тесты базы данных
   python -m pytest tests/test_database.py -v
   
   # Интеграционные тесты (требуют запущенные сервисы)
   python -m pytest tests/test_integration.py -v
   ```

3. **Запустите все тесты сразу:**
   ```bash
   python -m pytest tests/ auth-service/tests/ finance-service/tests/ -v
   ```

### В GitHub Actions

Тесты автоматически запускаются при каждом push и pull request в ветку `main`.

## 🧪 Типы тестов

### 1. **Функциональные тесты** (`test_*_functional.py`)
- **Что проверяют:** Реальную работу API endpoints
- **Примеры:** Регистрация пользователя, создание операции, аутентификация
- **Технологии:** FastAPI TestClient, pytest

### 2. **Тесты базы данных** (`test_database.py`)
- **Что проверяют:** Корректность SQL операций, модели данных, ограничения
- **Примеры:** Создание записей, уникальность, связи между таблицами
- **Технологии:** SQLAlchemy, SQLite (для тестов)

### 3. **Интеграционные тесты** (`test_integration.py`)
- **Что проверяют:** Взаимодействие между сервисами
- **Примеры:** Auth → Finance, Finance → Report, полный workflow
- **Технологии:** httpx, реальные HTTP запросы

## 📊 Покрытие тестами

### Auth Service
- ✅ Регистрация пользователя
- ✅ Вход в систему  
- ✅ Получение списка пользователей
- ✅ Валидация токенов
- ✅ Хеширование паролей

### Finance Service
- ✅ Создание операций
- ✅ Получение операций
- ✅ Расчет баланса
- ✅ Изоляция данных между пользователями
- ✅ Валидация типов операций

### Database
- ✅ Создание и получение записей
- ✅ Уникальность полей
- ✅ Связи между таблицами
- ✅ SQL запросы
- ✅ Обработка больших чисел

### Integration
- ✅ Полный workflow пользователя
- ✅ Взаимодействие сервисов
- ✅ Обработка токенов
- ✅ Одновременные операции

## 🔧 Настройка тестов

### Переменные окружения для тестов
```bash
# Тестовые базы данных (SQLite)
AUTH_DATABASE_URL="sqlite:///./test_auth.db"
FINANCE_DATABASE_URL="sqlite:///./test_finance.db"

# URL сервисов для интеграционных тестов
AUTH_SERVICE_URL="http://localhost:8000"
FINANCE_SERVICE_URL="http://localhost:8001"
REPORT_SERVICE_URL="http://localhost:8002"
```

### Структура тестовых данных
- Каждый тест использует изолированную базу данных
- Тестовые данные создаются и удаляются автоматически
- Используются уникальные email адреса с timestamp

## 🐛 Отладка тестов

### Если тесты не проходят:

1. **Проверьте зависимости:**
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Проверьте синтаксис Python:**
   ```bash
   python -m py_compile auth-service/app/main.py
   ```

3. **Запустите тесты с подробным выводом:**
   ```bash
   python -m pytest tests/test_database.py -v -s
   ```

4. **Проверьте логи в GitHub Actions:**
   - Перейдите в раздел "Actions" в GitHub
   - Выберите последний запуск
   - Посмотрите логи каждого шага

## 📈 Метрики качества

- **Покрытие функциональности:** ~90%
- **Количество тестов:** 25+ тестов
- **Время выполнения:** ~2-3 минуты
- **Стабильность:** Высокая (изолированные тесты)

## 🎯 Что тестируем в CI/CD

1. ✅ **Компиляция кода** - синтаксис Python
2. ✅ **Запуск сервисов** - импорт модулей
3. ✅ **Функциональные тесты** - API endpoints
4. ✅ **Тесты базы данных** - SQL операции
5. ✅ **Сборка Docker** - Dockerfile'ы
6. ✅ **Docker Swarm** - развертывание

Это обеспечивает высокое качество кода и уверенность в работоспособности системы! 🚀

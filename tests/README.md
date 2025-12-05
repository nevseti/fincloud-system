# Тесты для системы FinCloud

## Структура тестов

```
tests/
├── test_integration.py    # Интеграционные тесты
├── test_api.py            # API тесты
├── test_security.py       # Тесты безопасности
└── test_e2e.py           # End-to-End тесты

auth-service/tests/
└── test_auth_unit.py      # Unit тесты для auth-service

finance-service/tests/
└── test_finance_unit.py   # Unit тесты для finance-service
```

## Запуск тестов

### Unit тесты

```bash
# Auth service
cd auth-service
python -m pytest tests/test_auth_unit.py -v

# Finance service
cd finance-service
python -m pytest tests/test_finance_unit.py -v
```

### Integration тесты

```bash
cd tests
python -m pytest test_integration.py -v
```

### API тесты

```bash
cd tests
python -m pytest test_api.py -v
```

### Security тесты

```bash
cd tests
python -m pytest test_security.py -v
```

### E2E тесты

```bash
cd tests
python -m pytest test_e2e.py -v
```

### Все тесты

```bash
# Из корня проекта
python -m pytest auth-service/tests/ finance-service/tests/ tests/ -v
```

## Требования

- Python 3.11+
- pytest
- fastapi
- httpx (для TestClient)

Установка зависимостей:

```bash
pip install pytest fastapi httpx
```

## Примечания

- Тесты используют SQLite для тестирования (настроено через переменные окружения)
- Для запуска некоторых тестов требуется доступ к базе данных
- E2E тесты требуют запущенных сервисов или используют TestClient


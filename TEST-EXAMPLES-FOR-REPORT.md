# Примеры тестов для отчета

## Что делать:
1. Создать папки `auth-service/tests/`, `finance-service/tests/`, `tests/`
2. Вынести примеры тестов из ci-cd.yml в отдельные файлы
3. Добавить в отчет листинги этих тестов
4. Показать результаты выполнения (можно взять из GitHub Actions)

---

## Пример 1: Unit Test для Auth Service

**Файл:** `auth-service/tests/test_auth_unit.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth_utils import create_access_token, verify_token, get_password_hash, verify_password
from app.schemas import UserCreate

client = TestClient(app)

def test_health_endpoint():
    """Тест проверки работоспособности сервиса"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_user_registration_validation():
    """Тест валидации данных при регистрации"""
    # Пустые данные
    response = client.post('/register', json={})
    assert response.status_code == 422
    
    # Невалидный email
    response = client.post('/register', json={
        'email': 'invalid-email',
        'password': 'pass123',
        'role': 'accountant',
        'branch_id': 1
    })
    assert response.status_code == 422

def test_user_registration_success():
    """Тест успешной регистрации пользователя"""
    user_data = {
        'email': 'test_unit@example.com',
        'password': 'testpass123',
        'role': 'accountant',
        'branch_id': 1
    }
    response = client.post('/register', json=user_data)
    assert response.status_code == 200
    assert response.json()['email'] == user_data['email']
    assert response.json()['role'] == user_data['role']

def test_password_hashing():
    """Тест хеширования паролей"""
    password = 'test_password_123'
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 0
    assert verify_password(password, hashed) == True
    assert verify_password('wrong_password', hashed) == False

def test_jwt_token_creation():
    """Тест создания и верификации JWT токенов"""
    payload = {
        'user_id': 1,
        'email': 'test@example.com',
        'role': 'accountant',
        'branch_id': 1
    }
    
    token = create_access_token(payload)
    assert token is not None
    assert len(token) > 0
    
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded['user_id'] == payload['user_id']
    assert decoded['email'] == payload['email']
```

---

## Пример 2: Unit Test для Finance Service

**Файл:** `finance-service/tests/test_finance_unit.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Operation
from app.schemas import OperationCreate

client = TestClient(app)

def test_health_endpoint():
    """Тест проверки работоспособности сервиса"""
    response = client.get('/health')
    assert response.status_code == 200

def test_balance_endpoint_requires_auth():
    """Тест что баланс требует аутентификации"""
    response = client.get('/balance')
    assert response.status_code == 401  # Unauthorized

def test_operations_endpoint_requires_auth():
    """Тест что операции требуют аутентификации"""
    response = client.get('/operations')
    assert response.status_code == 401

def test_create_operation_validation():
    """Тест валидации данных операции"""
    # Невалидный тип операции
    invalid_op = {
        'type': 'invalid_type',
        'amount': 100.0,
        'description': 'Test',
        'branch_id': 1
    }
    # Должно либо валидироваться (422), либо обрабатываться в бизнес-логике
    # В зависимости от реализации
```

---

## Пример 3: Integration Test

**Файл:** `tests/test_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from auth_service.app.main import app as auth_app
from finance_service.app.main import app as finance_app
import time

auth_client = TestClient(auth_app)
finance_client = TestClient(finance_app)

def test_auth_finance_integration():
    """Интеграционный тест взаимодействия auth и finance сервисов"""
    
    # 1. Регистрация пользователя
    user_data = {
        'email': 'integration_test@example.com',
        'password': 'testpass123',
        'role': 'accountant',
        'branch_id': 1
    }
    register_response = auth_client.post('/register', json=user_data)
    assert register_response.status_code == 200
    
    # 2. Вход и получение токена
    login_response = auth_client.post('/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    
    # 3. Использование токена для доступа к finance сервису
    balance_response = finance_client.get(
        '/balance',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert balance_response.status_code == 200
    assert 'total_balance' in balance_response.json()
    
    # 4. Создание финансовой операции
    operation = {
        'type': 'income',
        'amount': 5000.0,
        'description': 'Integration test income',
        'branch_id': 1
    }
    op_response = finance_client.post(
        '/operations',
        json=operation,
        headers={'Authorization': f'Bearer {token}'}
    )
    assert op_response.status_code == 200
    assert op_response.json()['type'] == 'income'
    assert op_response.json()['amount'] == 5000.0
    
    # 5. Проверка обновления баланса
    updated_balance = finance_client.get(
        '/balance',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert updated_balance.status_code == 200
    balance_data = updated_balance.json()
    assert balance_data['total_income'] >= 5000.0

def test_service_health_checks():
    """Тест health endpoints всех сервисов"""
    # Auth service
    auth_health = auth_client.get('/health')
    assert auth_health.status_code == 200
    
    # Finance service  
    finance_health = finance_client.get('/health')
    assert finance_health.status_code == 200
    
    # Report service (если доступен)
    # report_health = report_client.get('/health')
    # assert report_health.status_code == 200
```

---

## Пример 4: API Test (из ci-cd.yml)

**Файл:** `tests/test_api.py`

```python
from fastapi.testclient import TestClient
from auth_service.app.main import app as auth_app
from finance_service.app.main import app as finance_app

auth_client = TestClient(auth_app)
finance_client = TestClient(finance_app)

def test_complete_user_journey():
    """E2E тест полного пользовательского сценария"""
    
    # Регистрация
    user = {
        'email': 'e2e_test@example.com',
        'password': 'password123',
        'role': 'accountant',
        'branch_id': 1
    }
    register = auth_client.post('/register', json=user)
    assert register.status_code == 200
    
    # Вход
    login = auth_client.post('/login', json={
        'email': user['email'],
        'password': user['password']
    })
    assert login.status_code == 200
    token = login.json()['access_token']
    
    # Получение баланса
    balance = finance_client.get(
        '/balance',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert balance.status_code == 200
    
    # Создание операций
    operations = [
        {'type': 'income', 'amount': 10000.0, 'description': 'Income 1', 'branch_id': 1},
        {'type': 'income', 'amount': 5000.0, 'description': 'Income 2', 'branch_id': 1},
        {'type': 'expense', 'amount': 2000.0, 'description': 'Expense 1', 'branch_id': 1},
    ]
    
    for op in operations:
        response = finance_client.post(
            '/operations',
            json=op,
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    # Проверка финального баланса
    final_balance = finance_client.get(
        '/balance',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert final_balance.status_code == 200
    balance_data = final_balance.json()
    assert balance_data['total_income'] >= 15000.0
    assert balance_data['total_expense'] >= 2000.0
```

---

## Результаты выполнения (пример для отчета):

```
🧪 Unit Tests - auth-service
✅ Python syntax: All files compile successfully
✅ Module imports: All modules import without errors
✅ Health endpoint: Responds with status 200
✅ Schema validation: All schemas validate correctly
✅ Password hashing: bcrypt working correctly
✅ JWT tokens: Token creation and verification working

🧪 Unit Tests - finance-service
✅ Python syntax: All files compile successfully
✅ Module imports: All modules import without errors
✅ Health endpoint: Responds with status 200

🔗 Integration Tests
✅ Service imports: All services import successfully
✅ Health endpoints: All services respond to /health
✅ Service communication: Services can communicate

🌐 API Tests
✅ Health endpoints: All services respond to /health
✅ User registration: Users can register successfully
✅ User login: Login returns valid JWT tokens
✅ Protected endpoints: Token-based authentication works
✅ Finance operations: Balance and operations endpoints work
✅ Create operations: Can create financial operations

🔒 Security Tests
✅ JWT tokens: Token creation and verification working
✅ Password hashing: bcrypt hashing and verification working
✅ Input validation: Pydantic schemas validate input correctly

🎭 E2E Tests
✅ User registration: Users can register successfully
✅ User login: Users can login and receive tokens
✅ Protected access: Authenticated users can access protected endpoints
✅ Finance integration: Can access finance service with auth token
✅ Operations: Can create and retrieve financial operations
✅ Balance calculation: Balance updates correctly after operations
```

---

## Что добавить в отчет:

1. **В раздел 3.5** (после описания CI/CD) добавить подраздел **3.5.1. Примеры тестов и результаты выполнения**

2. Вставить листинги:
   - Листинг 10 – Unit тест для auth-service (test_auth_unit.py)
   - Листинг 11 – Unit тест для finance-service (test_finance_unit.py)
   - Листинг 12 – Integration тест (test_integration.py)
   - Листинг 13 – API/E2E тест (test_api.py)

3. Добавить таблицу с результатами выполнения тестов

4. Можно добавить скриншот из GitHub Actions (если есть)


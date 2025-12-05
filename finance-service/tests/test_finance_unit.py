"""
Unit tests for finance-service
Тестирование отдельных компонентов сервиса финансовых операций
"""
import pytest
import sys
import os

# Добавляем путь к модулю app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.schemas import OperationCreate

client = TestClient(app)


def test_health_endpoint():
    """Тест проверки работоспособности сервиса"""
    response = client.get('/health')
    assert response.status_code == 200
    print('Health endpoint: OK')


def test_python_syntax():
    """Тест синтаксиса Python файлов"""
    import app.main
    import app.models
    import app.schemas
    import app.database
    # Если импорт прошел успешно, синтаксис корректен
    assert True


def test_module_imports():
    """Тест импорта модулей"""
    from app.main import app
    from app.models import Operation
    from app.schemas import OperationCreate, OperationResponse
    print("All modules imported successfully")


def test_balance_endpoint_requires_auth():
    """Тест что баланс требует аутентификации"""
    response = client.get('/balance')
    assert response.status_code == 401  # Unauthorized
    print('Balance endpoint requires auth: OK')


def test_operations_endpoint_requires_auth():
    """Тест что операции требуют аутентификации"""
    response = client.get('/operations')
    assert response.status_code == 401
    print('Operations endpoint requires auth: OK')


def test_create_operation_requires_auth():
    """Тест что создание операции требует аутентификации"""
    operation = {
        'type': 'income',
        'amount': 100.0,
        'description': 'Test',
        'branch_id': 1
    }
    response = client.post('/operations', json=operation)
    assert response.status_code == 401
    print('Create operation requires auth: OK')


def test_database_models():
    """Тест моделей базы данных"""
    try:
        from app.models import Operation
        assert hasattr(Operation, '__table__'), 'Operation model should have table definition'
        print('Operation model has table definition')
    except ImportError:
        print('Models module not available (skipping)')


def test_operation_schema_validation():
    """Тест валидации схемы операции"""
    try:
        from app.schemas import OperationCreate
        
        # Валидная операция
        valid_op = OperationCreate(
            type='income',
            amount=1000.0,
            description='Test operation',
            branch_id=1
        )
        assert valid_op.type == 'income'
        assert valid_op.amount == 1000.0
        print('Operation schema validation: OK')
    except ImportError:
        print('Schemas module not available (skipping)')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


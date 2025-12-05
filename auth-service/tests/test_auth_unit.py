"""
Unit tests for auth-service
Тестирование отдельных компонентов сервиса аутентификации
"""
import pytest
import sys
import os

# Добавляем путь к модулю app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.auth_utils import create_access_token, verify_token, get_password_hash, verify_password
from app.schemas import UserCreate, UserResponse
from app.models import User

client = TestClient(app)


def test_health_endpoint():
    """Тест проверки работоспособности сервиса"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_python_syntax():
    """Тест синтаксиса Python файлов"""
    import app.main
    import app.auth_utils
    import app.schemas
    import app.database
    # Если импорт прошел успешно, синтаксис корректен
    assert True


def test_module_imports():
    """Тест импорта модулей"""
    from app.main import app
    from app.auth_utils import create_access_token, verify_token
    from app.schemas import UserCreate, UserResponse
    print("All modules imported successfully")


def test_user_registration_validation_empty():
    """Тест валидации пустых данных при регистрации"""
    response = client.post('/register', json={})
    assert response.status_code == 422


def test_user_registration_validation_invalid_email():
    """Тест валидации невалидного email"""
    response = client.post('/register', json={
        'email': 'invalid-email',
        'password': 'pass123',
        'role': 'accountant',
        'branch_id': 1
    })
    assert response.status_code == 422


def test_schema_validation():
    """Тест валидации схем Pydantic"""
    test_users = [
        {'email': 'test1@example.com', 'password': 'pass123', 'role': 'accountant', 'branch_id': 1},
        {'email': 'test2@example.com', 'password': 'pass456', 'role': 'manager', 'branch_id': 0},
        {'email': 'test3@example.com', 'password': 'pass789', 'role': 'system_admin', 'branch_id': 0},
    ]
    
    for user_data in test_users:
        user = UserCreate(**user_data)
        assert user.email == user_data['email']
        assert user.role == user_data['role']
        print(f'Schema validation ({user_data["role"]}): OK')


def test_user_registration_success():
    """Тест успешной регистрации пользователя"""
    user_data = {
        'email': 'test_unit@example.com',
        'password': 'testpass123',
        'role': 'accountant',
        'branch_id': 1
    }
    response = client.post('/register', json=user_data)
    # Может быть 200 (успех) или 400 (пользователь уже существует)
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        assert response.json()['email'] == user_data['email']
        assert response.json()['role'] == user_data['role']


def test_password_hashing():
    """Тест хеширования паролей с помощью bcrypt"""
    test_passwords = [
        'simple123',
        'Complex@Pass123!',
        'very_long_password_that_exceeds_normal_length_but_should_still_work_123456789',
        'short',
    ]
    
    for password in test_passwords:
        hashed = get_password_hash(password)
        assert hashed != password, 'Password should be hashed, not stored in plain text'
        assert len(hashed) > 0
        
        # Проверка правильного пароля
        is_valid = verify_password(password, hashed)
        assert is_valid, f'Password verification failed for: {password[:10]}...'
        
        # Проверка неправильного пароля
        is_invalid = verify_password('wrong_password', hashed)
        assert not is_invalid, 'Wrong password should not be accepted'
        print(f'Password hashing verified for password length {len(password)}')


def test_jwt_token_creation():
    """Тест создания и верификации JWT токенов"""
    test_payloads = [
        {'user_id': 1, 'email': 'test1@example.com', 'role': 'accountant', 'branch_id': 1},
        {'user_id': 2, 'email': 'test2@example.com', 'role': 'manager', 'branch_id': 0},
        {'user_id': 3, 'email': 'test3@example.com', 'role': 'system_admin', 'branch_id': 0},
    ]
    
    for payload in test_payloads:
        token = create_access_token(payload)
        assert token is not None
        assert len(token) > 0
        
        decoded = verify_token(token)
        assert decoded is not None
        assert decoded.get('user_id') == payload['user_id']
        assert decoded.get('email') == payload['email']
        print(f'JWT token created and verified for {payload["email"]}')


def test_jwt_invalid_token():
    """Тест обработки невалидного токена"""
    invalid_token = 'invalid.token.here'
    decoded = verify_token(invalid_token)
    assert decoded is None, 'Invalid token should return None'
    print('Invalid token correctly rejected')


def test_database_models():
    """Тест моделей базы данных"""
    try:
        from app.models import User
        assert hasattr(User, '__table__'), 'User model should have table definition'
        print('User model has table definition')
    except ImportError:
        print('Models module not available (skipping)')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


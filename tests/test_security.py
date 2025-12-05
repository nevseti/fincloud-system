"""
Security tests for FinCloud system
Тестирование безопасности: JWT, пароли, валидация
"""
import pytest
import sys
import os

# Добавляем путь к auth-service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'auth-service'))

from app.auth_utils import create_access_token, verify_token, get_password_hash, verify_password
from app.schemas import UserCreate
from pydantic import ValidationError


def test_jwt_token_creation_and_verification():
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
        assert hashed is not None
        assert len(hashed) > 0
        assert hashed != password, 'Password should be hashed, not stored in plain text'
        
        # Проверка правильного пароля
        is_valid = verify_password(password, hashed)
        assert is_valid, f'Password verification failed for: {password[:10]}...'
        
        # Проверка неправильного пароля
        is_invalid = verify_password('wrong_password', hashed)
        assert not is_invalid, 'Wrong password should not be accepted'
        print(f'Password hashing verified for password length {len(password)}')


def test_input_validation():
    """Тест валидации входных данных"""
    # Валидный пользователь
    try:
        user = UserCreate(
            email='test@example.com',
            password='password123',
            role='accountant',
            branch_id=1
        )
        assert user.email == 'test@example.com'
        print('Valid user creation: OK')
    except Exception as e:
        print(f'Valid user creation failed: {e}')
        raise
    
    # Невалидный email
    try:
        user = UserCreate(
            email='invalid-email',
            password='pass123',
            role='accountant',
            branch_id=1
        )
        print('Invalid email should have been rejected')
        assert False, 'Invalid email should raise ValidationError'
    except ValidationError:
        print('Invalid email correctly rejected')
    
    # Отсутствующие обязательные поля
    try:
        user = UserCreate(email='test@example.com', password='pass123')
        print('Missing fields should have been rejected')
        assert False, 'Missing fields should raise ValidationError'
    except ValidationError:
        print('Missing required fields correctly rejected')
    
    # Разные роли
    valid_roles = ['accountant', 'manager', 'system_admin']
    for role in valid_roles:
        user = UserCreate(
            email=f'test_{role}@example.com',
            password='pass123',
            role=role,
            branch_id=1
        )
        assert user.role == role
        print(f'Role validation ({role}): OK')
    
    print('Input validation working correctly')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


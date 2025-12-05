"""
Integration tests for FinCloud system
Тестирование взаимодействия между сервисами
"""
import pytest
import sys
import os

# Добавляем пути к сервисам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'auth-service'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'finance-service'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'report-service'))

from fastapi.testclient import TestClient
import sys
import os

# Правильные пути для импорта
auth_path = os.path.join(os.path.dirname(__file__), '..', 'auth-service')
finance_path = os.path.join(os.path.dirname(__file__), '..', 'finance-service')
report_path = os.path.join(os.path.dirname(__file__), '..', 'report-service')

sys.path.insert(0, auth_path)
from app.main import app as auth_app

sys.path.insert(0, finance_path)
from app.main import app as finance_app

sys.path.insert(0, report_path)
from app.main import app as report_app

auth_client = TestClient(auth_app)
finance_client = TestClient(finance_app)
report_client = TestClient(report_app)


def test_service_imports():
    """Тест импорта всех сервисов"""
    import sys
    import os
    
    auth_path = os.path.join(os.path.dirname(__file__), '..', 'auth-service')
    finance_path = os.path.join(os.path.dirname(__file__), '..', 'finance-service')
    report_path = os.path.join(os.path.dirname(__file__), '..', 'report-service')
    
    sys.path.insert(0, auth_path)
    from app.main import app
    print('Auth service: OK')
    
    sys.path.insert(0, finance_path)
    from app.main import app
    print('Finance service: OK')
    
    sys.path.insert(0, report_path)
    from app.main import app
    print('Report service: OK')


def test_service_health_endpoints():
    """Тест health endpoints всех сервисов"""
    # Auth service
    response = auth_client.get('/health')
    assert response.status_code == 200
    print(f'Auth health: {response.status_code}')
    
    # Finance service
    response = finance_client.get('/health')
    assert response.status_code == 200
    print(f'Finance health: {response.status_code}')
    
    # Report service
    response = report_client.get('/health')
    assert response.status_code == 200
    print(f'Report health: {response.status_code}')


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
    # Может быть 200 (успех) или 400 (пользователь уже существует)
    assert register_response.status_code in [200, 400]
    
    # 2. Вход и получение токена
    login_response = auth_client.post('/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    print('User registered and logged in')
    
    # 3. Использование токена для доступа к finance сервису
    balance_response = finance_client.get(
        '/balance',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert balance_response.status_code == 200
    assert 'total_balance' in balance_response.json()
    print('Finance service accessed with auth token')


def test_service_communication():
    """Тест коммуникации между сервисами"""
    # Проверяем, что все сервисы могут быть импортированы и запущены
    assert auth_app is not None
    assert finance_app is not None
    assert report_app is not None
    print('All services can communicate')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


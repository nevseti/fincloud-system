"""
API tests for FinCloud system
Тестирование API endpoints всех сервисов
"""
import pytest
import sys
import os
import time

# Добавляем пути к сервисам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'auth-service'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'finance-service'))

from fastapi.testclient import TestClient
import sys
import os

# Правильные пути для импорта
auth_path = os.path.join(os.path.dirname(__file__), '..', 'auth-service')
finance_path = os.path.join(os.path.dirname(__file__), '..', 'finance-service')

sys.path.insert(0, auth_path)
from app.main import app as auth_app

sys.path.insert(0, finance_path)
from app.main import app as finance_app

auth_client = TestClient(auth_app)
finance_client = TestClient(finance_app)


def test_auth_service_api():
    """Тест API endpoints auth-service"""
    
    # Health endpoint
    response = auth_client.get('/health')
    assert response.status_code == 200
    print('Health endpoint: OK')
    time.sleep(0.1)
    
    # Register validation (empty data)
    response = auth_client.post('/register', json={})
    assert response.status_code == 422
    print('Register validation (empty): OK')
    
    # Register validation (invalid email)
    response = auth_client.post('/register', json={
        'email': 'invalid',
        'password': 'pass',
        'role': 'user',
        'branch_id': 1
    })
    assert response.status_code == 422
    print('Register validation (invalid email): OK')
    time.sleep(0.1)
    
    # Successful registration
    test_users = [
        {'email': 'api_test_accountant@example.com', 'password': 'testpass123', 'role': 'accountant', 'branch_id': 1},
        {'email': 'api_test_manager@example.com', 'password': 'testpass123', 'role': 'manager', 'branch_id': 0},
    ]
    
    tokens = {}
    for user in test_users:
        response = auth_client.post('/register', json=user)
        # Может быть 200 (успех) или 400 (пользователь уже существует)
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            user_data = response.json()
            assert user_data['email'] == user['email']
            assert user_data['role'] == user['role']
            print(f'User registration ({user["role"]}): OK')
            time.sleep(0.1)
            
            # Login
            login_response = auth_client.post('/login', json={
                'email': user['email'],
                'password': user['password']
            })
            assert login_response.status_code == 200
            tokens[user['role']] = login_response.json()['access_token']
            print(f'User login ({user["role"]}): OK')
            time.sleep(0.1)
    
    # Protected endpoint
    if tokens:
        for role, token in tokens.items():
            response = auth_client.get('/users/me', headers={'Authorization': f'Bearer {token}'})
            assert response.status_code == 200
            user_info = response.json()
            assert user_info['role'] == role
            print(f'Protected endpoint access ({role}): OK')
            time.sleep(0.1)
    
    print('Auth service API tests: PASSED')


def test_finance_service_api():
    """Тест API endpoints finance-service"""
    
    # Сначала получаем токен от auth-service
    user_data = {
        'email': 'finance_api_test@example.com',
        'password': 'testpass123',
        'role': 'accountant',
        'branch_id': 1
    }
    auth_client.post('/register', json=user_data)
    login_response = auth_client.post('/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        
        # Health endpoint
        response = finance_client.get('/health')
        assert response.status_code == 200
        print('Health endpoint: OK')
        time.sleep(0.1)
        
        # Balance endpoint
        response = finance_client.get('/balance', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        balance = response.json()
        assert 'total_balance' in balance
        assert 'total_income' in balance
        assert 'total_expense' in balance
        print(f'Balance endpoint: OK (balance: {balance["total_balance"]})')
        time.sleep(0.1)
        
        # Operations endpoint
        response = finance_client.get('/operations', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        operations = response.json()
        assert isinstance(operations, list)
        print(f'Operations endpoint: OK ({len(operations)} operations)')
        time.sleep(0.1)
        
        # Create operation
        operation = {
            'type': 'income',
            'amount': 5000.0,
            'description': 'API test income',
            'branch_id': 1
        }
        response = finance_client.post('/operations', json=operation, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        op_data = response.json()
        assert op_data['type'] == 'income'
        assert op_data['amount'] == 5000.0
        print('Create operation: OK')
        time.sleep(0.1)
        
        print('Finance service API tests: PASSED')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


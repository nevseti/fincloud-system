"""
End-to-End tests for FinCloud system
Тестирование полного пользовательского сценария
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


def test_complete_user_journey():
    """E2E тест полного пользовательского сценария"""
    
    # 1. Регистрация пользователя
    user_data = {
        'email': 'e2e_test@example.com',
        'password': 'password123',
        'role': 'accountant',
        'branch_id': 1
    }
    register_response = auth_client.post('/register', json=user_data)
    # Может быть 200 (успех) или 400 (пользователь уже существует)
    assert register_response.status_code in [200, 400]
    if register_response.status_code == 200:
        print('Step 1: User registered')
    
    # 2. Вход
    login_response = auth_client.post('/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    print('Step 2: User logged in')
    
    # 3. Получение баланса
    balance_response = finance_client.get(
        '/balance',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert balance_response.status_code == 200
    initial_balance = balance_response.json()
    assert 'total_balance' in initial_balance
    initial_total = initial_balance['total_balance']
    print(f'Step 3: Initial balance retrieved: {initial_total}')
    time.sleep(0.1)
    
    # 4. Создание доходных операций
    income_ops = [
        {'type': 'income', 'amount': 10000.0, 'description': 'E2E income 1', 'branch_id': 1},
        {'type': 'income', 'amount': 5000.0, 'description': 'E2E income 2', 'branch_id': 1},
        {'type': 'income', 'amount': 3000.0, 'description': 'E2E income 3', 'branch_id': 1},
    ]
    
    created_ops = []
    for i, op in enumerate(income_ops, 1):
        response = finance_client.post(
            '/operations',
            json=op,
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        op_data = response.json()
        assert op_data['type'] == 'income'
        created_ops.append(op_data)
        print(f'Step 4.{i}: Income operation created ({op["amount"]})')
        time.sleep(0.1)
    
    # 5. Создание расходных операций
    expense_ops = [
        {'type': 'expense', 'amount': 2000.0, 'description': 'E2E expense 1', 'branch_id': 1},
        {'type': 'expense', 'amount': 1500.0, 'description': 'E2E expense 2', 'branch_id': 1},
    ]
    
    for i, op in enumerate(expense_ops, 1):
        response = finance_client.post(
            '/operations',
            json=op,
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        op_data = response.json()
        assert op_data['type'] == 'expense'
        created_ops.append(op_data)
        print(f'Step 5.{i}: Expense operation created ({op["amount"]})')
        time.sleep(0.1)
    
    # 6. Получение списка операций
    operations_response = finance_client.get(
        '/operations',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert operations_response.status_code == 200
    operations = operations_response.json()
    assert len(operations) >= len(created_ops)
    print(f'Step 6: Retrieved {len(operations)} operations')
    time.sleep(0.1)
    
    # 7. Проверка обновленного баланса
    updated_balance_response = finance_client.get(
        '/balance',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert updated_balance_response.status_code == 200
    updated_balance = updated_balance_response.json()
    
    # Расчет ожидаемого изменения
    total_income = sum(op['amount'] for op in income_ops)
    total_expense = sum(op['amount'] for op in expense_ops)
    expected_change = total_income - total_expense
    
    # Баланс должен увеличиться
    assert updated_balance['total_balance'] >= initial_total + expected_change - 0.01, \
        f'Balance not updated correctly: {updated_balance["total_balance"]} vs expected {initial_total + expected_change}'
    
    print(f'Step 7: Balance updated correctly')
    print(f'   Initial: {initial_total}')
    print(f'   Income: {updated_balance["total_income"]}')
    print(f'   Expense: {updated_balance["total_expense"]}')
    print(f'   Final: {updated_balance["total_balance"]}')
    time.sleep(0.1)
    
    # 8. Баланс с фильтром по branch_id
    branch_balance_response = finance_client.get(
        '/balance?branch_id=1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert branch_balance_response.status_code == 200
    branch_balance = branch_balance_response.json()
    assert 'total_balance' in branch_balance
    print('Step 8: Branch-specific balance retrieved')
    
    print('E2E test completed successfully!')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


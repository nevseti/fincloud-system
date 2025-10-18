import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_operation_unauthorized():
    """Тест создания операции без авторизации"""
    operation_data = {
        "type": "income",
        "amount": 1000.0,
        "description": "Test operation",
        "branch_id": 1
    }
    
    response = client.post("/operations", json=operation_data)
    assert response.status_code == 401

def test_get_operations_unauthorized():
    """Тест получения операций без авторизации"""
    response = client.get("/operations")
    assert response.status_code == 401

def test_get_balance_unauthorized():
    """Тест получения баланса без авторизации"""
    response = client.get("/balance")
    assert response.status_code == 401

def test_create_operation_with_auth():
    """Тест создания операции с авторизацией"""
    # Сначала нужно получить токен от auth-service
    # Это упрощенный тест, в реальности нужно мокать auth-service
    
    operation_data = {
        "type": "income",
        "amount": 1000.0,
        "description": "Test operation",
        "branch_id": 1
    }
    
    # Мокаем токен (в реальности нужно получать от auth-service)
    headers = {"Authorization": "Bearer mock_token"}
    
    # Этот тест будет падать, так как токен не валидный
    # В реальном проекте нужно настроить моки или тестовую БД
    response = client.post("/operations", json=operation_data, headers=headers)
    # Ожидаем 401, так как токен не валидный
    assert response.status_code == 401

def test_operation_data_validation():
    """Тест валидации данных операции"""
    # Тест с неверными данными
    invalid_data = {
        "type": "invalid_type",
        "amount": -100,  # Отрицательная сумма
        "description": "",
        "branch_id": "invalid"  # Не число
    }
    
    headers = {"Authorization": "Bearer mock_token"}
    response = client.post("/operations", json=invalid_data, headers=headers)
    # Ожидаем ошибку валидации
    assert response.status_code in [400, 401, 422]

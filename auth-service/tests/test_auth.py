import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user():
    """Тест регистрации пользователя"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "accountant",
        "branch_id": 1
    }
    
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert data["branch_id"] == user_data["branch_id"]

def test_register_duplicate_user():
    """Тест регистрации дублирующегося пользователя"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123",
        "role": "accountant",
        "branch_id": 1
    }
    
    # Первая регистрация
    response1 = client.post("/register", json=user_data)
    assert response1.status_code == 200
    
    # Попытка зарегистрировать того же пользователя
    response2 = client.post("/register", json=user_data)
    assert response2.status_code == 400

def test_login_success():
    """Тест успешного входа"""
    # Сначала регистрируем пользователя
    user_data = {
        "email": "login@example.com",
        "password": "testpassword123",
        "role": "accountant",
        "branch_id": 1
    }
    client.post("/register", json=user_data)
    
    # Теперь пытаемся войти
    login_data = {
        "email": "login@example.com",
        "password": "testpassword123"
    }
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Тест входа с неверными данными"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/login", json=login_data)
    assert response.status_code == 401

def test_get_current_user():
    """Тест получения информации о текущем пользователе"""
    # Регистрируем пользователя
    user_data = {
        "email": "current@example.com",
        "password": "testpassword123",
        "role": "accountant",
        "branch_id": 1
    }
    client.post("/register", json=user_data)
    
    # Входим в систему
    login_data = {
        "email": "current@example.com",
        "password": "testpassword123"
    }
    login_response = client.post("/login", json=login_data)
    token = login_response.json()["access_token"]
    
    # Получаем информацию о пользователе
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"

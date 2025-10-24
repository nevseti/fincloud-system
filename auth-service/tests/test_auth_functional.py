"""
Функциональные тесты для Auth Service
Проверяем реальную работу API endpoints
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

# Импортируем наше приложение
from app.main import app
from app.database import get_db, Base
from app.models import User
from app.auth_utils import get_password_hash

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Переопределяем зависимость базы данных для тестов"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestAuthService:
    """Тесты для Auth Service"""
    
    def setup_method(self):
        """Очищаем базу перед каждым тестом"""
        # Удаляем все пользователей
        db = TestingSessionLocal()
        db.query(User).delete()
        db.commit()
        db.close()
    
    def test_register_user_success(self):
        """Тест успешной регистрации пользователя"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "branch_id": 1
        }
        
        response = client.post("/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["branch_id"] == 1
        assert "id" in data
        assert "password" not in data  # Пароль не должен возвращаться
    
    def test_register_user_duplicate_email(self):
        """Тест регистрации с существующим email"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "branch_id": 1
        }
        
        # Создаем первого пользователя
        client.post("/register", json=user_data)
        
        # Пытаемся создать второго с тем же email
        response = client.post("/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self):
        """Тест успешного входа"""
        # Сначала регистрируем пользователя
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "branch_id": 1
        }
        client.post("/register", json=user_data)
        
        # Теперь логинимся
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self):
        """Тест входа с неправильным паролем"""
        # Регистрируем пользователя
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "branch_id": 1
        }
        client.post("/register", json=user_data)
        
        # Пытаемся войти с неправильным паролем
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Тест входа несуществующего пользователя"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "somepassword"
        }
        
        response = client.post("/login", data=login_data)
        
        assert response.status_code == 401
        assert "User not found" in response.json()["detail"]
    
    def test_get_users_without_token(self):
        """Тест получения списка пользователей без токена"""
        response = client.get("/users")
        
        assert response.status_code == 401
    
    def test_get_users_with_valid_token(self):
        """Тест получения списка пользователей с валидным токеном"""
        # Регистрируем пользователя
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "branch_id": 1
        }
        client.post("/register", json=user_data)
        
        # Получаем токен
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        login_response = client.post("/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Получаем список пользователей
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "test@example.com"
    
    def test_password_hashing(self):
        """Тест хеширования паролей"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Хеш должен быть другим, чем оригинальный пароль
        assert hashed != password
        # Хеш должен быть строкой
        assert isinstance(hashed, str)
        # Хеш должен быть достаточно длинным
        assert len(hashed) > 20

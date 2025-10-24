"""
Функциональные тесты для Finance Service
Проверяем работу с финансовыми операциями
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Импортируем наше приложение
from app.main import app
from app.database import get_db, Base
from app.models import Operation
from app.auth_utils import create_access_token

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_finance.db"
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

class TestFinanceService:
    """Тесты для Finance Service"""
    
    def setup_method(self):
        """Очищаем базу перед каждым тестом"""
        db = TestingSessionLocal()
        db.query(Operation).delete()
        db.commit()
        db.close()
    
    def get_auth_headers(self, user_id: int = 1):
        """Получаем заголовки авторизации для тестов"""
        token = create_access_token(data={"sub": str(user_id)})
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_operation_success(self):
        """Тест успешного создания операции"""
        operation_data = {
            "amount": 1000.50,
            "description": "Тестовая операция",
            "operation_type": "income"
        }
        
        headers = self.get_auth_headers()
        response = client.post("/operations", json=operation_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 1000.50
        assert data["description"] == "Тестовая операция"
        assert data["operation_type"] == "income"
        assert data["user_id"] == 1
        assert "id" in data
        assert "created_at" in data
    
    def test_create_operation_negative_amount(self):
        """Тест создания операции с отрицательной суммой"""
        operation_data = {
            "amount": -100.0,
            "description": "Отрицательная операция",
            "operation_type": "expense"
        }
        
        headers = self.get_auth_headers()
        response = client.post("/operations", json=operation_data, headers=headers)
        
        assert response.status_code == 201  # Отрицательные суммы разрешены для расходов
        data = response.json()
        assert data["amount"] == -100.0
    
    def test_create_operation_without_auth(self):
        """Тест создания операции без авторизации"""
        operation_data = {
            "amount": 1000.0,
            "description": "Операция без авторизации",
            "operation_type": "income"
        }
        
        response = client.post("/operations", json=operation_data)
        
        assert response.status_code == 401
    
    def test_get_operations_success(self):
        """Тест получения списка операций"""
        # Создаем несколько операций
        operations = [
            {"amount": 1000.0, "description": "Операция 1", "operation_type": "income"},
            {"amount": -500.0, "description": "Операция 2", "operation_type": "expense"},
        ]
        
        headers = self.get_auth_headers()
        for op in operations:
            client.post("/operations", json=op, headers=headers)
        
        # Получаем список операций
        response = client.get("/operations", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["amount"] == 1000.0
        assert data[1]["amount"] == -500.0
    
    def test_get_operations_different_users(self):
        """Тест изоляции операций между пользователями"""
        # Создаем операцию для пользователя 1
        headers_user1 = self.get_auth_headers(user_id=1)
        operation_data = {
            "amount": 1000.0,
            "description": "Операция пользователя 1",
            "operation_type": "income"
        }
        client.post("/operations", json=operation_data, headers=headers_user1)
        
        # Создаем операцию для пользователя 2
        headers_user2 = self.get_auth_headers(user_id=2)
        operation_data = {
            "amount": 2000.0,
            "description": "Операция пользователя 2",
            "operation_type": "income"
        }
        client.post("/operations", json=operation_data, headers=headers_user2)
        
        # Пользователь 1 должен видеть только свои операции
        response = client.get("/operations", headers=headers_user1)
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == 1000.0
        
        # Пользователь 2 должен видеть только свои операции
        response = client.get("/operations", headers=headers_user2)
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == 2000.0
    
    def test_get_balance_calculation(self):
        """Тест расчета баланса"""
        # Создаем операции с разными суммами
        operations = [
            {"amount": 1000.0, "description": "Доход", "operation_type": "income"},
            {"amount": -300.0, "description": "Расход", "operation_type": "expense"},
            {"amount": 500.0, "description": "Доход", "operation_type": "income"},
        ]
        
        headers = self.get_auth_headers()
        for op in operations:
            client.post("/operations", json=op, headers=headers)
        
        # Получаем баланс
        response = client.get("/balance", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        expected_balance = 1000.0 - 300.0 + 500.0  # 1200.0
        assert data["balance"] == expected_balance
    
    def test_invalid_operation_type(self):
        """Тест с неверным типом операции"""
        operation_data = {
            "amount": 1000.0,
            "description": "Неверный тип",
            "operation_type": "invalid_type"
        }
        
        headers = self.get_auth_headers()
        response = client.post("/operations", json=operation_data, headers=headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_large_amount(self):
        """Тест с большой суммой"""
        operation_data = {
            "amount": 999999999999.99,
            "description": "Большая сумма",
            "operation_type": "income"
        }
        
        headers = self.get_auth_headers()
        response = client.post("/operations", json=operation_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 999999999999.99

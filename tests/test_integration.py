"""
Интеграционные тесты для FinCloud системы
Проверяем взаимодействие между сервисами
"""
import pytest
import httpx
import asyncio
import time
from typing import Dict, Any

class TestFinCloudIntegration:
    """Интеграционные тесты для всей системы"""
    
    def __init__(self):
        self.auth_base_url = "http://localhost:8000"
        self.finance_base_url = "http://localhost:8001"
        self.report_base_url = "http://localhost:8002"
        self.frontend_url = "http://localhost:8080"
        self.auth_token = None
        self.user_id = None
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.auth_token = None
        self.user_id = None
    
    def register_and_login_user(self) -> Dict[str, Any]:
        """Регистрируем и логиним пользователя, возвращаем токен"""
        # Регистрация
        user_data = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpassword123",
            "branch_id": 1
        }
        
        with httpx.Client() as client:
            # Регистрируем пользователя
            response = client.post(f"{self.auth_base_url}/register", json=user_data)
            assert response.status_code == 201
            user_info = response.json()
            self.user_id = user_info["id"]
            
            # Логинимся
            login_data = {
                "username": user_data["email"],
                "password": user_data["password"]
            }
            response = client.post(f"{self.auth_base_url}/login", data=login_data)
            assert response.status_code == 200
            token_info = response.json()
            self.auth_token = token_info["access_token"]
            
            return {
                "user_id": self.user_id,
                "token": self.auth_token,
                "email": user_data["email"]
            }
    
    def test_auth_to_finance_integration(self):
        """Тест интеграции между Auth и Finance сервисами"""
        # Регистрируем и логинимся
        user_info = self.register_and_login_user()
        
        # Создаем операцию в Finance сервисе используя токен из Auth
        operation_data = {
            "amount": 1500.0,
            "description": "Интеграционный тест",
            "operation_type": "income"
        }
        
        headers = {"Authorization": f"Bearer {user_info['token']}"}
        
        with httpx.Client() as client:
            # Создаем операцию
            response = client.post(
                f"{self.finance_base_url}/operations", 
                json=operation_data, 
                headers=headers
            )
            assert response.status_code == 201
            operation = response.json()
            assert operation["user_id"] == user_info["user_id"]
            assert operation["amount"] == 1500.0
            
            # Получаем список операций
            response = client.get(
                f"{self.finance_base_url}/operations", 
                headers=headers
            )
            assert response.status_code == 200
            operations = response.json()
            assert len(operations) == 1
            assert operations[0]["amount"] == 1500.0
    
    def test_finance_to_report_integration(self):
        """Тест интеграции между Finance и Report сервисами"""
        # Регистрируем пользователя и создаем операции
        user_info = self.register_and_login_user()
        
        headers = {"Authorization": f"Bearer {user_info['token']}"}
        
        with httpx.Client() as client:
            # Создаем несколько операций
            operations = [
                {"amount": 2000.0, "description": "Доход 1", "operation_type": "income"},
                {"amount": -500.0, "description": "Расход 1", "operation_type": "expense"},
                {"amount": 1000.0, "description": "Доход 2", "operation_type": "income"},
            ]
            
            for op in operations:
                response = client.post(
                    f"{self.finance_base_url}/operations", 
                    json=op, 
                    headers=headers
                )
                assert response.status_code == 201
            
            # Получаем отчет через Report сервис
            response = client.get(
                f"{self.report_base_url}/report", 
                headers=headers
            )
            assert response.status_code == 200
            
            # Проверяем что отчет содержит данные
            report_data = response.json()
            assert "total_income" in report_data
            assert "total_expense" in report_data
            assert "balance" in report_data
            assert report_data["total_income"] == 3000.0  # 2000 + 1000
            assert report_data["total_expense"] == 500.0
            assert report_data["balance"] == 2500.0  # 3000 - 500
    
    def test_full_user_workflow(self):
        """Тест полного рабочего процесса пользователя"""
        # 1. Регистрация и вход
        user_info = self.register_and_login_user()
        headers = {"Authorization": f"Bearer {user_info['token']}"}
        
        with httpx.Client() as client:
            # 2. Создаем несколько операций
            operations = [
                {"amount": 5000.0, "description": "Зарплата", "operation_type": "income"},
                {"amount": -1200.0, "description": "Аренда", "operation_type": "expense"},
                {"amount": -300.0, "description": "Продукты", "operation_type": "expense"},
                {"amount": 2000.0, "description": "Премия", "operation_type": "income"},
            ]
            
            created_operations = []
            for op in operations:
                response = client.post(
                    f"{self.finance_base_url}/operations", 
                    json=op, 
                    headers=headers
                )
                assert response.status_code == 201
                created_operations.append(response.json())
            
            # 3. Проверяем баланс
            response = client.get(f"{self.finance_base_url}/balance", headers=headers)
            assert response.status_code == 200
            balance = response.json()
            expected_balance = 5000 - 1200 - 300 + 2000  # 5500
            assert balance["balance"] == expected_balance
            
            # 4. Получаем отчет
            response = client.get(f"{self.report_base_url}/report", headers=headers)
            assert response.status_code == 200
            report = response.json()
            assert report["total_income"] == 7000.0  # 5000 + 2000
            assert report["total_expense"] == 1500.0  # 1200 + 300
            assert report["balance"] == 5500.0
            
            # 5. Проверяем список операций
            response = client.get(f"{self.finance_base_url}/operations", headers=headers)
            assert response.status_code == 200
            operations_list = response.json()
            assert len(operations_list) == 4
    
    def test_token_expiration_handling(self):
        """Тест обработки истечения токена"""
        # Регистрируем пользователя
        user_info = self.register_and_login_user()
        
        # Создаем операцию с валидным токеном
        headers = {"Authorization": f"Bearer {user_info['token']}"}
        operation_data = {
            "amount": 1000.0,
            "description": "Тест токена",
            "operation_type": "income"
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{self.finance_base_url}/operations", 
                json=operation_data, 
                headers=headers
            )
            assert response.status_code == 201
            
            # Пытаемся использовать невалидный токен
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            response = client.post(
                f"{self.finance_base_url}/operations", 
                json=operation_data, 
                headers=invalid_headers
            )
            assert response.status_code == 401
    
    def test_concurrent_operations(self):
        """Тест одновременных операций от разных пользователей"""
        # Регистрируем двух пользователей
        user1_info = self.register_and_login_user()
        
        # Небольшая задержка для уникальности email
        time.sleep(1)
        user2_info = self.register_and_login_user()
        
        headers1 = {"Authorization": f"Bearer {user1_info['token']}"}
        headers2 = {"Authorization": f"Bearer {user2_info['token']}"}
        
        with httpx.Client() as client:
            # Создаем операции от обоих пользователей
            operation1 = {
                "amount": 1000.0,
                "description": "Операция пользователя 1",
                "operation_type": "income"
            }
            operation2 = {
                "amount": 2000.0,
                "description": "Операция пользователя 2",
                "operation_type": "income"
            }
            
            # Создаем операции параллельно
            response1 = client.post(
                f"{self.finance_base_url}/operations", 
                json=operation1, 
                headers=headers1
            )
            response2 = client.post(
                f"{self.finance_base_url}/operations", 
                json=operation2, 
                headers=headers2
            )
            
            assert response1.status_code == 201
            assert response2.status_code == 201
            
            # Проверяем что операции принадлежат разным пользователям
            op1 = response1.json()
            op2 = response2.json()
            assert op1["user_id"] != op2["user_id"]
            assert op1["user_id"] == user1_info["user_id"]
            assert op2["user_id"] == user2_info["user_id"]

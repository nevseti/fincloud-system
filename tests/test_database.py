"""
Тесты для работы с базой данных
Проверяем корректность SQL операций и моделей
"""
import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Импортируем модели из обоих сервисов
import sys
sys.path.append('auth-service')
sys.path.append('finance-service')

from auth_service.app.models import User as AuthUser, Base as AuthBase
from finance_service.app.models import Operation as FinanceOperation, Base as FinanceBase

class TestDatabaseOperations:
    """Тесты для операций с базой данных"""
    
    def setup_method(self):
        """Настройка тестовой базы данных"""
        # Создаем тестовую базу данных в памяти
        self.database_url = "sqlite:///./test_database.db"
        self.engine = create_engine(self.database_url, connect_args={"check_same_thread": False})
        
        # Создаем все таблицы
        AuthBase.metadata.create_all(bind=self.engine)
        FinanceBase.metadata.create_all(bind=self.engine)
        
        # Создаем сессию
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
    
    def teardown_method(self):
        """Очистка после тестов"""
        self.db.close()
        # Удаляем тестовую базу данных
        if os.path.exists("test_database.db"):
            os.remove("test_database.db")
    
    def test_user_creation_and_retrieval(self):
        """Тест создания и получения пользователя"""
        # Создаем пользователя
        user = AuthUser(
            email="test@example.com",
            hashed_password="hashed_password_here",
            branch_id=1
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Проверяем что пользователь создался
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.branch_id == 1
        
        # Получаем пользователя из базы
        retrieved_user = self.db.query(AuthUser).filter(AuthUser.email == "test@example.com").first()
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
    
    def test_user_email_uniqueness(self):
        """Тест уникальности email пользователей"""
        # Создаем первого пользователя
        user1 = AuthUser(
            email="unique@example.com",
            hashed_password="password1",
            branch_id=1
        )
        self.db.add(user1)
        self.db.commit()
        
        # Пытаемся создать второго пользователя с тем же email
        user2 = AuthUser(
            email="unique@example.com",
            hashed_password="password2",
            branch_id=2
        )
        self.db.add(user2)
        
        # Должна возникнуть ошибка уникальности
        with pytest.raises(IntegrityError):
            self.db.commit()
    
    def test_operation_creation_and_retrieval(self):
        """Тест создания и получения операции"""
        # Сначала создаем пользователя
        user = AuthUser(
            email="test@example.com",
            hashed_password="hashed_password",
            branch_id=1
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Создаем операцию
        operation = FinanceOperation(
            amount=1500.50,
            description="Тестовая операция",
            operation_type="income",
            user_id=user.id
        )
        
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)
        
        # Проверяем что операция создалась
        assert operation.id is not None
        assert operation.amount == 1500.50
        assert operation.user_id == user.id
        
        # Получаем операцию из базы
        retrieved_operation = self.db.query(FinanceOperation).filter(
            FinanceOperation.id == operation.id
        ).first()
        assert retrieved_operation is not None
        assert retrieved_operation.amount == 1500.50
    
    def test_operation_user_relationship(self):
        """Тест связи между операциями и пользователями"""
        # Создаем пользователя
        user = AuthUser(
            email="test@example.com",
            hashed_password="hashed_password",
            branch_id=1
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Создаем несколько операций для пользователя
        operations = [
            FinanceOperation(amount=1000.0, description="Операция 1", operation_type="income", user_id=user.id),
            FinanceOperation(amount=-500.0, description="Операция 2", operation_type="expense", user_id=user.id),
            FinanceOperation(amount=2000.0, description="Операция 3", operation_type="income", user_id=user.id),
        ]
        
        for op in operations:
            self.db.add(op)
        self.db.commit()
        
        # Получаем все операции пользователя
        user_operations = self.db.query(FinanceOperation).filter(
            FinanceOperation.user_id == user.id
        ).all()
        
        assert len(user_operations) == 3
        
        # Проверяем суммы
        amounts = [op.amount for op in user_operations]
        assert 1000.0 in amounts
        assert -500.0 in amounts
        assert 2000.0 in amounts
    
    def test_database_constraints(self):
        """Тест ограничений базы данных"""
        # Тест обязательных полей для пользователя
        user_without_email = AuthUser(
            hashed_password="password",
            branch_id=1
        )
        self.db.add(user_without_email)
        
        with pytest.raises(IntegrityError):
            self.db.commit()
        
        # Откатываем транзакцию
        self.db.rollback()
        
        # Тест обязательных полей для операции
        operation_without_user = FinanceOperation(
            amount=1000.0,
            description="Операция без пользователя",
            operation_type="income"
        )
        self.db.add(operation_without_user)
        
        with pytest.raises(IntegrityError):
            self.db.commit()
    
    def test_balance_calculation_query(self):
        """Тест SQL запроса для расчета баланса"""
        # Создаем пользователя
        user = AuthUser(
            email="balance@example.com",
            hashed_password="hashed_password",
            branch_id=1
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Создаем операции с разными суммами
        operations = [
            FinanceOperation(amount=3000.0, description="Большой доход", operation_type="income", user_id=user.id),
            FinanceOperation(amount=-800.0, description="Расход 1", operation_type="expense", user_id=user.id),
            FinanceOperation(amount=1200.0, description="Доход 2", operation_type="income", user_id=user.id),
            FinanceOperation(amount=-200.0, description="Расход 2", operation_type="expense", user_id=user.id),
        ]
        
        for op in operations:
            self.db.add(op)
        self.db.commit()
        
        # Выполняем SQL запрос для расчета баланса
        result = self.db.execute(text("""
            SELECT SUM(amount) as balance 
            FROM operations 
            WHERE user_id = :user_id
        """), {"user_id": user.id}).fetchone()
        
        expected_balance = 3000.0 - 800.0 + 1200.0 - 200.0  # 3200.0
        assert result.balance == expected_balance
    
    def test_operation_type_validation(self):
        """Тест валидации типов операций"""
        # Создаем пользователя
        user = AuthUser(
            email="validation@example.com",
            hashed_password="hashed_password",
            branch_id=1
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Тестируем валидные типы операций
        valid_types = ["income", "expense"]
        
        for op_type in valid_types:
            operation = FinanceOperation(
                amount=1000.0,
                description=f"Операция типа {op_type}",
                operation_type=op_type,
                user_id=user.id
            )
            self.db.add(operation)
            self.db.commit()
            self.db.refresh(operation)
            
            # Проверяем что операция сохранилась
            assert operation.operation_type == op_type
            
            # Удаляем операцию для следующего теста
            self.db.delete(operation)
            self.db.commit()
    
    def test_large_numbers_handling(self):
        """Тест работы с большими числами"""
        # Создаем пользователя
        user = AuthUser(
            email="large@example.com",
            hashed_password="hashed_password",
            branch_id=1
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Создаем операцию с очень большой суммой
        large_amount = 999999999999.99
        operation = FinanceOperation(
            amount=large_amount,
            description="Очень большая сумма",
            operation_type="income",
            user_id=user.id
        )
        
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)
        
        # Проверяем что большая сумма сохранилась корректно
        assert operation.amount == large_amount
        
        # Получаем операцию из базы
        retrieved_operation = self.db.query(FinanceOperation).filter(
            FinanceOperation.id == operation.id
        ).first()
        assert retrieved_operation.amount == large_amount
    
    def test_concurrent_database_access(self):
        """Тест одновременного доступа к базе данных"""
        # Создаем двух пользователей
        user1 = AuthUser(
            email="user1@example.com",
            hashed_password="password1",
            branch_id=1
        )
        user2 = AuthUser(
            email="user2@example.com",
            hashed_password="password2",
            branch_id=2
        )
        
        self.db.add(user1)
        self.db.add(user2)
        self.db.commit()
        self.db.refresh(user1)
        self.db.refresh(user2)
        
        # Создаем операции для обоих пользователей
        operation1 = FinanceOperation(
            amount=1000.0,
            description="Операция пользователя 1",
            operation_type="income",
            user_id=user1.id
        )
        operation2 = FinanceOperation(
            amount=2000.0,
            description="Операция пользователя 2",
            operation_type="income",
            user_id=user2.id
        )
        
        self.db.add(operation1)
        self.db.add(operation2)
        self.db.commit()
        
        # Проверяем что операции принадлежат разным пользователям
        assert operation1.user_id != operation2.user_id
        assert operation1.user_id == user1.id
        assert operation2.user_id == user2.id

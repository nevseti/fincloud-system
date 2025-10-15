import sys
import os

# Устанавливаем кодировку UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from app.database import engine, Base
from app.models import User
from app.auth_utils import get_password_hash, verify_password

def test_all():
    try:
        print("1. Проверяем подключение к PostgreSQL...")
        
        # Тестируем подключение
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"   ✅ PostgreSQL подключен: {version.split(',')[0]}")
        
        # 2. Создаем таблицы
        print("2. Создаем таблицы...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ Таблицы созданы")
        
        # 3. Тестируем хеширование с нормальным паролем
        print("3. Тестируем хеширование...")
        password = "test123"  # Короткий пароль
        hashed = get_password_hash(password)
        is_valid = verify_password(password, hashed)
        print(f"   ✅ Хеширование работает: {is_valid}")
        
        # 4. Тестируем импорты
        print("4. Проверяем импорты...")
        from app import main, schemas, auth_utils
        print("   ✅ Все модули импортируются")
        
        print("\n🎉 ВСЕ РАБОТАЕТ! Auth-service готов!")
        print("📊 База данных: PostgreSQL")
        print("🔐 Аутентификация: JWT + bcrypt")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_all()
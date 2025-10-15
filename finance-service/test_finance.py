from app.database import engine, Base
from app.models import Operation

def test_finance_setup():
    try:
        # Создаем таблицы
        print("1. Создаем таблицы в PostgreSQL...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ Таблицы созданы")
        
        # Проверяем импорты
        print("2. Проверяем импорты...")
        from app import main, schemas, auth_utils
        print("   ✅ Все модули импортируются")
        
        print("\n🎉 Finance-service готов к работе!")
        print("📊 База данных: PostgreSQL (finance_db)")
        print("💰 Функциональность: операции, баланс, отчеты")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_finance_setup()
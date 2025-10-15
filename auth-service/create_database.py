import psycopg2

def create_database():
    try:
        # Подключаемся к основной базе postgres
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="postgres",
            user="postgres",
            password="u1s9e7i1n"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Создаем базу auth_db если не существует
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'auth_db'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE auth_db;")
            print("✅ База данных auth_db создана")
        else:
            print("✅ База данных auth_db уже существует")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при создании базы: {e}")

if __name__ == "__main__":
    create_database()
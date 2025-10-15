import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Запуск Finance Service...")
    print("📡 Сервер будет доступен по: http://localhost:8001")
    print("📚 Документация API: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)
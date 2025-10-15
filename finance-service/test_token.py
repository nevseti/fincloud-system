from jose import jwt

# Токен из браузера
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFjY291bnRhbnRAZmludG9yZy5ydSIsImV4cCI6MTc2MDQ2NDQxNX0.BBSNAsT6dZqpDt141NnvocADSz9RV3-1zkDOfUf_o68"

# Секретный ключ из finance-service
SECRET_KEY = "your-secret-key-for-development-change-in-production"

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print("✅ Токен валиден в finance-service!")
    print("Payload:", payload)
except Exception as e:
    print("❌ Токен невалиден в finance-service:", e)
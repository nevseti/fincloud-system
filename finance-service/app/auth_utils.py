from jose import JWTError, jwt
from fastapi import HTTPException, status
from typing import Optional

# ДОЛЖЕН БЫТЬ ТОТ ЖЕ СЕКРЕТНЫЙ КЛЮЧ ЧТО И В AUTH-SERVICE!
SECRET_KEY = "your-secret-key-for-development-change-in-production"
ALGORITHM = "HS256"

def verify_token(token: str) -> Optional[dict]:
    """Проверяет JWT токен и возвращает payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token: str):
    """Получает пользователя из токена"""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload
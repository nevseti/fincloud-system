from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from . import models, schemas, auth_utils
from .database import get_db, engine
from .models import Base

# Создаем таблицы при старте
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service",
    description="Сервис аутентификации и управления пользователями",
    version="1.0.0"
)

# CORS middleware - используем встроенный CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = auth_utils.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user_id = payload.get("user_id")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != 'system_admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin rights required")
    return current_user

@app.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = auth_utils.get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        branch_id=user_data.branch_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user or not auth_utils.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = auth_utils.create_access_token(
        data={"user_id": user.id, "email": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user

# Admin-only user management endpoints
@app.get("/users", response_model=List[schemas.UserResponse])
def list_users(_admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post("/users", response_model=schemas.UserResponse)
def create_user(user_data: schemas.UserCreate, _admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    hashed_password = auth_utils.get_password_hash(user_data.password)
    user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        branch_id=user_data.branch_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, update: schemas.UserUpdate, _admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if update.email is not None:
        if db.query(models.User).filter(models.User.email == update.email, models.User.id != user_id).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        user.email = update.email
    if update.password is not None:
        user.hashed_password = auth_utils.get_password_hash(update.password)
    if update.role is not None:
        user.role = update.role
    if update.branch_id is not None:
        user.branch_id = update.branch_id
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, _admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "auth-service", "database": "PostgreSQL"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
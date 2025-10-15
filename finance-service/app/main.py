from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import os

from . import models, schemas, auth_utils
from .database import get_db, engine
from .models import Base

# Создаем таблицы при старте
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Service",
    description="Сервис управления финансовыми операциями",
    version="1.0.0"
)

# CORS middleware - ИСПРАВЛЕННАЯ ВЕРСИЯ
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={"message": "CORS preflight"})
    else:
        response = await call_next(request)
    
    # Добавляем CORS заголовки ко ВСЕМ ответам
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Явные OPTIONS handlers для всех путей
@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(
        content={"message": "CORS preflight"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@app.options("/")
async def options_root():
    return JSONResponse(
        content={"message": "CORS preflight"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With", 
            "Access-Control-Allow-Credentials": "true"
        }
    )

security = HTTPBearer()

def get_current_user_data(credentials = Depends(security)):
    token = credentials.credentials
    user_data = auth_utils.get_current_user(token)
    return user_data

# Эндпоинты с проверкой прав
@app.post("/operations", response_model=schemas.OperationResponse)
def create_operation(
    operation_data: schemas.OperationCreate,
    user_data: dict = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    """Создание новой финансовой операции с проверкой прав"""
    role = user_data.get('role')
    user_branch_id = user_data.get('branch_id')
    
    # Руководители не могут создавать операции
    if role == 'manager':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Руководители не могут создавать операции"
        )
    
    # Бухгалтеры могут создавать операции только для своего филиала
    if role == 'accountant':
        if operation_data.branch_id != user_branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Можно создавать операции только для своего филиала"
            )
    
    # Создаем операцию
    db_operation = models.Operation(
        type=operation_data.type,
        amount=operation_data.amount,
        description=operation_data.description,
        user_id=user_data["user_id"],
        branch_id=operation_data.branch_id
    )
    
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    
    return db_operation

@app.get("/operations", response_model=List[schemas.OperationResponse])
def get_operations(
    user_data: dict = Depends(get_current_user_data),
    db: Session = Depends(get_db),
    branch_id: int = None
):
    """Получение списка операций с учетом прав доступа"""
    role = user_data.get('role')
    user_branch_id = user_data.get('branch_id')
    
    # Бухгалтер - только операции своего филиала
    if role == 'accountant':
        query = db.query(models.Operation).filter(models.Operation.branch_id == user_branch_id)
    else:
        # Админ и руководитель - все операции
        query = db.query(models.Operation)
        if branch_id:
            query = query.filter(models.Operation.branch_id == branch_id)
    
    operations = query.order_by(models.Operation.created_at.desc()).all()
    return operations

@app.get("/balance", response_model=schemas.BalanceResponse)
def get_balance(
    user_data: dict = Depends(get_current_user_data),
    db: Session = Depends(get_db),
    branch_id: int = None
):
    """Получение баланса с учетом прав доступа"""
    role = user_data.get('role')
    user_branch_id = user_data.get('branch_id')
    
    # Бухгалтер - только баланс своего филиала
    if role == 'accountant':
        if branch_id and branch_id != user_branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен к этому филиалу"
            )
        # Если branch_id не указан, используем филиал бухгалтера
        actual_branch_id = branch_id or user_branch_id
        query = db.query(models.Operation).filter(models.Operation.branch_id == actual_branch_id)
    else:
        # Админ и руководитель - любой баланс
        query = db.query(models.Operation)
        if branch_id:
            query = query.filter(models.Operation.branch_id == branch_id)
    
    # Считаем доходы и расходы
    income_result = query.filter(models.Operation.type == "income").with_entities(func.sum(models.Operation.amount)).scalar()
    total_income = income_result if income_result else 0.0
    
    expense_result = query.filter(models.Operation.type == "expense").with_entities(func.sum(models.Operation.amount)).scalar()
    total_expense = expense_result if expense_result else 0.0
    
    total_balance = total_income - total_expense
    
    return {
        "total_balance": total_balance,
        "total_income": total_income,
        "total_expense": total_expense,
        "branch_id": branch_id or 0
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "finance-service"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск Finance Service с исправленным CORS...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
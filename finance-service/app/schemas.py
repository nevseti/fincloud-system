from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OperationCreate(BaseModel):
    type: str  # 'income' или 'expense'
    amount: float
    description: str
    branch_id: int

class OperationResponse(BaseModel):
    id: int
    type: str
    amount: float
    description: str
    user_id: int
    branch_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class BalanceResponse(BaseModel):
    total_balance: float
    total_income: float
    total_expense: float
    branch_id: int
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from .database import Base
from datetime import datetime

class Operation(Base):
    __tablename__ = "operations"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), nullable=False)  # 'income' или 'expense'
    amount = Column(Float, nullable=False)
    description = Column(Text)
    user_id = Column(Integer, nullable=False)
    branch_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Operation(id={self.id}, type={self.type}, amount={self.amount})>"
from sqlalchemy import Column, Integer, String, Float, Date
from database import Base
from pydantic import BaseModel
from datetime import date
from typing import Optional

# --- SQLAlchemy Models (DB Schema) ---

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=True)

class Income(Base):
    __tablename__ = "incomes"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=True)

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(Date, nullable=True)

class BudgetLimit(Base):
    __tablename__ = "budget_limits"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)


# --- Pydantic Models (Validation / API Schema) ---

class ExpenseBase(BaseModel):
    amount: float
    category: Optional[str] = None
    date: date
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase): pass
class ExpenseResponse(ExpenseBase):
    id: int
    class Config: from_attributes = True

class IncomeBase(BaseModel):
    amount: float
    date: date
    description: Optional[str] = None

class IncomeCreate(IncomeBase): pass
class IncomeResponse(IncomeBase):
    id: int
    class Config: from_attributes = True

class GoalBase(BaseModel):
    name: str
    target_amount: float
    deadline: Optional[date] = None

class GoalCreate(GoalBase): pass
class GoalUpdateFunds(BaseModel):
    amount_to_add: float

class GoalResponse(GoalBase):
    id: int
    current_amount: float
    class Config: from_attributes = True

class BudgetLimitBase(BaseModel):
    category: str
    amount: float

class BudgetLimitCreate(BudgetLimitBase): pass
class BudgetLimitResponse(BudgetLimitBase):
    id: int
    spent_amount: float = 0.0
    class Config: from_attributes = True

class ChatRequest(BaseModel):
    message: str

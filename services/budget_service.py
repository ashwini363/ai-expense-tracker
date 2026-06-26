from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import date
import models

def get_budget_limits(db: Session):
    budgets = db.query(models.BudgetLimit).all()
    current_month = date.today().replace(day=1)
    
    result = []
    for b in budgets:
        spent = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.category == b.category,
            models.Expense.date >= current_month
        ).scalar() or 0.0
        
        result.append({
            "id": b.id,
            "category": b.category,
            "amount": b.amount,
            "spent_amount": spent
        })
    return result

def set_budget_limit(db: Session, budget: models.BudgetLimitCreate):
    # Check if exists, update if it does
    existing = db.query(models.BudgetLimit).filter(models.BudgetLimit.category == budget.category).first()
    if existing:
        existing.amount = budget.amount
        db.commit()
        db.refresh(existing)
        db_budget = existing
    else:
        db_budget = models.BudgetLimit(**budget.model_dump())
        db.add(db_budget)
        db.commit()
        db.refresh(db_budget)
        
    current_month = date.today().replace(day=1)
    spent = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.category == db_budget.category,
        models.Expense.date >= current_month
    ).scalar() or 0.0
    
    return {
        "id": db_budget.id,
        "category": db_budget.category,
        "amount": db_budget.amount,
        "spent_amount": spent
    }

def delete_budget_limit(db: Session, budget_id: int):
    b = db.query(models.BudgetLimit).filter(models.BudgetLimit.id == budget_id).first()
    if b:
        db.delete(b)
        db.commit()
    return b

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
from database import get_db
from services import expense_service, ai_agent, email_service
import os
from sqlalchemy import func
from datetime import date

router = APIRouter(
    prefix="/api/expenses",
    tags=["expenses"]
)

@router.get("/", response_model=List[models.ExpenseResponse])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expenses = expense_service.get_expenses(db, skip=skip, limit=limit)
    return expenses

@router.post("/", response_model=models.ExpenseResponse)
def create_expense(expense: models.ExpenseCreate, db: Session = Depends(get_db)):
    if not expense.category or expense.category.lower() == "auto":
        expense.category = ai_agent.categorize_expense_with_ai(expense.description)
        
    created = expense_service.create_expense(db=db, expense=expense)
    
    # Check Budget Limit for this category
    current_month = date.today().replace(day=1)
    limit = db.query(models.BudgetLimit).filter(models.BudgetLimit.category == created.category).first()
    
    if limit:
        # Calculate total spent this month for this category
        spent = db.query(func.sum(models.Expense.amount))\
                  .filter(models.Expense.category == created.category)\
                  .filter(models.Expense.date >= current_month)\
                  .scalar() or 0.0
                  
        if spent > limit.amount:
            user_email = os.getenv("USER_EMAIL") # Add this to .env
            email_service.send_overbudget_email_async(created.category, limit.amount, spent, user_email)
            
    return created

@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    deleted = expense_service.delete_expense(db=db, expense_id=expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return expense_service.get_expense_summary(db)

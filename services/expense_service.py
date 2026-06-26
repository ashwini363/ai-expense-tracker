from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from datetime import date, datetime

def get_expenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Expense).order_by(models.Expense.date.desc()).offset(skip).limit(limit).all()

def create_expense(db: Session, expense: models.ExpenseCreate):
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if expense:
        db.delete(expense)
        db.commit()
    return expense

def get_expense_summary(db: Session):
    total = db.query(func.sum(models.Expense.amount)).scalar() or 0.0
    
    categories = db.query(models.Expense.category, func.sum(models.Expense.amount))\
        .group_by(models.Expense.category).all()
        
    total_income = db.query(func.sum(models.Income.amount)).scalar() or 0.0
    bank_balance = total_income - total
    
    return {
        "total": total,
        "total_income": total_income,
        "bank_balance": bank_balance,
        "by_category": [{"category": c[0], "amount": c[1]} for c in categories]
    }

def get_expense_summary_by_month(db: Session, year: int, month: int):
    import calendar
    from datetime import date
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    
    expenses_query = db.query(models.Expense).filter(
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    )
    
    total = expenses_query.with_entities(func.sum(models.Expense.amount)).scalar() or 0.0
    
    categories = expenses_query.with_entities(models.Expense.category, func.sum(models.Expense.amount))\
        .group_by(models.Expense.category).all()
        
    return {
        "year": year,
        "month": month,
        "total": total,
        "by_category": [{"category": c[0], "amount": c[1]} for c in categories]
    }

def get_yearly_expense_summary(db: Session, year: int):
    from datetime import date
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    expenses = db.query(models.Expense).filter(
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).all()
    
    monthly_data = {}
    for i in range(1, 13):
        monthly_data[i] = {"total": 0.0, "categories": {}}
        
    for e in expenses:
        month = e.date.month
        monthly_data[month]["total"] += e.amount
        cat = e.category
        if cat not in monthly_data[month]["categories"]:
            monthly_data[month]["categories"][cat] = 0.0
        monthly_data[month]["categories"][cat] += e.amount
        
    return {
        "year": year,
        "monthly_breakdown": monthly_data
    }



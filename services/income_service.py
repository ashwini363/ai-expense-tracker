from sqlalchemy.orm import Session
import models

def get_incomes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Income).order_by(models.Income.date.desc()).offset(skip).limit(limit).all()

def create_income(db: Session, income: models.IncomeCreate):
    db_income = models.Income(**income.model_dump())
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income

def delete_income(db: Session, income_id: int):
    income = db.query(models.Income).filter(models.Income.id == income_id).first()
    if income:
        db.delete(income)
        db.commit()
    return income

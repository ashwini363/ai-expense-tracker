from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
from database import get_db
from services import budget_service

router = APIRouter(
    prefix="/api/budgets",
    tags=["budgets"]
)

@router.get("/", response_model=List[models.BudgetLimitResponse])
def read_budgets(db: Session = Depends(get_db)):
    return budget_service.get_budget_limits(db)

@router.post("/", response_model=models.BudgetLimitResponse)
def set_budget(budget: models.BudgetLimitCreate, db: Session = Depends(get_db)):
    return budget_service.set_budget_limit(db=db, budget=budget)

@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    deleted = budget_service.delete_budget_limit(db=db, budget_id=budget_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Budget limit not found")
    return {"message": "Budget limit deleted"}

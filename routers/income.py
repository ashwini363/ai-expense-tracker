from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
from database import get_db
from services import income_service

router = APIRouter(
    prefix="/api/income",
    tags=["income"]
)

@router.get("/", response_model=List[models.IncomeResponse])
def read_incomes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return income_service.get_incomes(db, skip=skip, limit=limit)

@router.post("/", response_model=models.IncomeResponse)
def create_income(income: models.IncomeCreate, db: Session = Depends(get_db)):
    return income_service.create_income(db=db, income=income)

@router.delete("/{income_id}")
def delete_income(income_id: int, db: Session = Depends(get_db)):
    deleted = income_service.delete_income(db=db, income_id=income_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"message": "Income deleted successfully"}

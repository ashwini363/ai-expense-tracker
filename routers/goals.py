from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
from database import get_db
from services import goal_service

router = APIRouter(
    prefix="/api/goals",
    tags=["goals"]
)

@router.get("/", response_model=List[models.GoalResponse])
def read_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return goal_service.get_goals(db, skip=skip, limit=limit)

@router.post("/", response_model=models.GoalResponse)
def create_goal(goal: models.GoalCreate, db: Session = Depends(get_db)):
    return goal_service.create_goal(db=db, goal=goal)

@router.post("/{goal_id}/add_funds", response_model=models.GoalResponse)
def add_funds(goal_id: int, funds: models.GoalUpdateFunds, db: Session = Depends(get_db)):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.current_amount += funds.amount_to_add
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    deleted = goal_service.delete_goal(db=db, goal_id=goal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted successfully"}

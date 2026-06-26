from sqlalchemy.orm import Session
import models

def get_goals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Goal).offset(skip).limit(limit).all()

def create_goal(db: Session, goal: models.GoalCreate):
    db_goal = models.Goal(**goal.model_dump())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, goal_id: int):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if goal:
        db.delete(goal)
        db.commit()
    return goal

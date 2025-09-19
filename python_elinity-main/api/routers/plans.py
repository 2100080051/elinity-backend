from fastapi import APIRouter,Depends
from database.session import Session,get_db
from models.credits import Plan
from typing import List
from schemas.credits import PlanSchema

router = APIRouter()


@router.get("/", response_model=List[PlanSchema])
def get_plans(db:Session = Depends(get_db)):
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    return plans

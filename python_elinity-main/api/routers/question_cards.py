from fastapi import APIRouter,Depends
from elinity_ai.question_card import OptimizedCardGenerator,QuestionCard
from schemas.question_cards import QuestionCardQuery
from typing import List
from utils.token import get_current_user
from models.user import Tenant
from database.session import get_db,Session
from sqlalchemy.orm import selectinload
from schemas.user import User
router = APIRouter()


@router.get("/cards/",tags=["Question Cards"],response_model=List[QuestionCard])
def generate_cards(query: QuestionCardQuery = Depends(),current_user: Tenant = Depends(get_current_user),db: Session = Depends(get_db)):
    generator = OptimizedCardGenerator()
    user = (
        db.query(Tenant)
        .options(
            selectinload(Tenant.profile_pictures),
            selectinload(Tenant.personal_info),
            selectinload(Tenant.big_five_traits),
            selectinload(Tenant.mbti_traits),
            selectinload(Tenant.psychology),
            selectinload(Tenant.interests_and_hobbies),
            selectinload(Tenant.values_beliefs_and_goals),
            selectinload(Tenant.favorites),
            selectinload(Tenant.relationship_preferences),
            selectinload(Tenant.friendship_preferences),
            selectinload(Tenant.collaboration_preferences),
            selectinload(Tenant.personal_free_form),
            selectinload(Tenant.intentions),
            selectinload(Tenant.aspiration_and_reflections),
            selectinload(Tenant.ideal_characteristics),
        )
        .filter(Tenant.id == current_user.id)
        .first()
    )
    
    cards = generator.generate_cards(User.model_validate(user),query.count)
    return cards
    
    


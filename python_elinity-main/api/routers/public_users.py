from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.orm import Session, selectinload
from database.session import get_db
from models.user import Tenant
from schemas.user import User as UserSchema

router = APIRouter(prefix="/public/users", tags=["Public Users"])

@router.get("/", response_model=List[UserSchema], status_code=status.HTTP_200_OK)
async def list_users(db: Session = Depends(get_db)):
    """Retrieve all users with full profile"""
    users = (
        db.query(Tenant)
        .options(
            selectinload(Tenant.profile_pictures),
            selectinload(Tenant.personal_info),
            selectinload(Tenant.big_five_traits),
            selectinload(Tenant.psychology),
            selectinload(Tenant.interests_and_hobbies),
            selectinload(Tenant.values_beliefs_and_goals),
            selectinload(Tenant.favorites),
            selectinload(Tenant.relationship_preferences),
            selectinload(Tenant.friendship_preferences),
            selectinload(Tenant.collaboration_preferences),
            selectinload(Tenant.personal_free_form),
            selectinload(Tenant.intentions),
        )
        .all()
    )
    return users

@router.get("/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Retrieve a single user by ID with full profile"""
    user = (
        db.query(Tenant)
        .options(
            selectinload(Tenant.profile_pictures),
            selectinload(Tenant.personal_info),
            selectinload(Tenant.big_five_traits),
            selectinload(Tenant.psychology),
            selectinload(Tenant.interests_and_hobbies),
            selectinload(Tenant.values_beliefs_and_goals),
            selectinload(Tenant.favorites),
            selectinload(Tenant.relationship_preferences),
            selectinload(Tenant.friendship_preferences),
            selectinload(Tenant.collaboration_preferences),
            selectinload(Tenant.personal_free_form),
            selectinload(Tenant.intentions),
        )
        .filter(Tenant.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

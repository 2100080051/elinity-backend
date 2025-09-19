from fastapi import APIRouter, Depends
from models.notifications import Notification,FBToken
from schemas.notification import TokenCreate, NotificationSchema, TokenSchema  # Keep Pydantic models
from database.session import get_db, Session
from models.user import Tenant
from typing import List
from utils.token import get_current_user

router = APIRouter(tags=['Notifications'])

@router.get('/', response_model=List[NotificationSchema])
def get_notification(
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifications = db.query(Notification).filter(
        Notification.tenant == current_user.id
    ).all()
    return notifications

@router.post('/token/', response_model=TokenSchema)
def create_token(
    request: TokenCreate,
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    token = FBToken(
        tenant=current_user.id,
        token=request.token,
        type=request.type
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token
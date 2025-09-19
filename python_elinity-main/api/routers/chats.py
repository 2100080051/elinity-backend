from fastapi import APIRouter, Depends, HTTPException, status
from models.chat import Chat
from database.session import get_db, Session
from utils.token import get_current_user
from models.user import Tenant
from schemas.chat import ChatSchema

router = APIRouter()

@router.get("/", tags=["Chats"])
async def get_chats(current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Chat).filter(Chat.sender == current_user.id).all()

@router.post("/", tags=["Chats"], response_model=ChatSchema)
async def create_chat(chat: ChatSchema, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    chat_obj = Chat(sender=current_user.id, **chat.model_dump())
    db.add(chat_obj)
    db.commit(); db.refresh(chat_obj)
    return chat_obj

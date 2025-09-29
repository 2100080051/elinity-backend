from fastapi import APIRouter, Depends, HTTPException, status
from models.chat import Chat
from database.session import get_db, Session
from utils.token import get_current_user
from models.user import Tenant
from schemas.chat import ChatSchema, ChatCreateSchema

router = APIRouter()

# ---------------------------
# Get all chats for user
# ---------------------------
@router.get("/", tags=["Chats"])
async def get_chats(
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Chat).filter(Chat.sender == current_user.id).all()


# ---------------------------
# Create new chat
# ---------------------------
@router.post("/", tags=["Chats"], response_model=ChatSchema)
async def create_chat(
    chat: ChatCreateSchema,   # ✅ use create schema
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # sender is always current_user
    chat_obj = Chat(sender=current_user.id, **chat.model_dump())
    db.add(chat_obj)
    db.commit()
    db.refresh(chat_obj)
    return chat_obj


# ---------------------------
# Get single chat by ID
# ---------------------------
@router.get("/{chat_id}", tags=["Chats"], response_model=ChatSchema)
async def get_chat(
    chat_id: str,  # UUID
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat_obj = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat_obj

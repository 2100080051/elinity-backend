from fastapi import APIRouter, Depends, WebSocket
from fastapi.encoders import jsonable_encoder
import logging 
from schemas.chat import ChatSchema, GroupSchema
from utils.websockets import manager
from utils.token import get_current_user
from fastapi import HTTPException
from fastapi import status
from database.session import get_db, Session
from models.chat import Chat,Group
from elinity_ai.elinity_bot import ElinityChatbot
from typing import List 

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("group_chat")

router = APIRouter()

@router.post('/send-ai-message/{room_id}/', tags=["Group Chat"], response_model=ChatSchema)
async def send_ai_message(room_id: str, conversation: List[ChatSchema], db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == room_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room ID.")
    try: 
        elinity_chatbot = ElinityChatbot(history=conversation)
        chat = Chat(group=room_id, message=elinity_chatbot.get_message())
        db.add(chat)
        db.commit(); db.refresh(chat)
    
        await manager.broadcast(room_id, jsonable_encoder(chat))
        return chat
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.websocket('/ws/{room_id}')
async def group_chat(websocket: WebSocket, room_id: str, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == room_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room ID.")
    await manager.connect(websocket, room_id)
    try:
        token = websocket.headers.get("authorization").split(" ")[1]
        current_user = await get_current_user(token, db)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")
        while True:
            data = await websocket.receive_json()
            data["sender"] = current_user.id
            data["group"] = room_id
            chat = Chat(**data)
            db.add(chat)
            db.commit(); db.refresh(chat)

            chat_data = ChatSchema.model_validate(chat).model_dump(by_alias=True, serialize_as_any=True)
            await manager.broadcast(room_id, jsonable_encoder(chat_data)) 
    except:
        await manager.disconnect(websocket, room_id)



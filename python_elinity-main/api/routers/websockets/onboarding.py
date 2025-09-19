from fastapi import APIRouter, HTTPException,status
import logging 
import uuid
from datetime import datetime
from models.chat import Group,Chat
from sqlalchemy import exists
from fastapi import Depends
from utils.token import get_current_user
from models.user import Tenant
from database.session import get_db, Session
from fastapi import WebSocket
from utils.websockets import onboarding_manager as manager
from elinity_ai.multimodal import ElinityMultimodal
from elinity_ai.onboarding_conversation import ElinityOnboardingConversation,ConversationChat,ContinueConversation
from pydantic import BaseModel
from typing import List

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("onboarding_chat")

router = APIRouter(prefix="", tags=["Onboarding"])

mul_model = ElinityMultimodal()

@router.get('/history')
async def get_history(current_user: Tenant = Depends(get_current_user),db: Session = Depends(get_db)):
    group_name = f"onboarding_{current_user.id}"
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please start a chat before continuing.")
    
    chats = db.query(Chat).filter(Chat.group == group.id).all()
    conversation_history = [ConversationChat(role="user" if chat.sender == current_user.id else "assistant",content=chat.message) for chat in chats]
    return conversation_history

@router.post('/start')
async def start_conversation(current_user: Tenant = Depends(get_current_user),db: Session = Depends(get_db)):
    model = ElinityOnboardingConversation()

    group_name = f"onboarding_{current_user.id}"

    group = db.query(Group).filter(Group.name == group_name).first()

    # 1. Create a group
    if not group:
        group = Group(name=group_name,tenant=current_user.id,description=f"Onboarding Group for {current_user.id}",type='user_ai')
        db.add(group)
        db.commit(); db.refresh(group)
    
    chat_exists = db.query(exists().where(Chat.group == group.id)).scalar()
    if  chat_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have chat started. Please continue the chat.")
    
    chat = Chat(group=group.id, message=model.welcome_message,receiver=current_user.id)
    db.add(chat)
    db.commit(); db.refresh(chat)
    
    model.start_conversation()
    return chat


@router.put('/continue')
async def continue_conversation(body: ContinueConversation,current_user: Tenant = Depends(get_current_user),db: Session = Depends(get_db)):
    group_name = f"onboarding_{current_user.id}"

    '''
    1. Check if group exists
    2. Check if chat exists
    3. Get conversation history
    '''
    # 1. Check if group exists
    group_exists = db.query(exists().where(Group.name == group_name)).scalar()
    
    if not group_exists: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please start a chat before continuing.")

    group = db.query(Group).filter(Group.name == group_name).first()
    
    # 2. Check if chat exists
    chat_exists = db.query(exists().where(Chat.group == group.id)).scalar()
    
    if not chat_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please start a chat before continuing.")
    
    # 3. Get conversation history
    chats = db.query(Chat).filter(Chat.group == group.id).all()
    conversation_history = [ConversationChat(role="user" if chat.sender == current_user.id else "assistant",content=chat.message) for chat in chats]

    model = ElinityOnboardingConversation(conversation_history=conversation_history)
   
    if body.asset_url:
        prompt = mul_model.process(body.asset_url)
    else:
        prompt = body.user_message
    
    # Get next prompt
    next_prompt = model.get_next_prompt(prompt)
    
    # Store the chat and user message
    chat_objs = [
        Chat(group=group.id,sender=current_user.id, message=body.user_message), # user message
        Chat(group=group.id, message=next_prompt,receiver=current_user.id) # assistant message
    ]
    db.add_all(chat_objs)
    db.commit()
    
    return {
        "tenant_id": current_user.id,
        "message": next_prompt
    }

class OnboardingConversation(BaseModel):
    tenant_id: str
    user: str
    chat_history: List[str] = []


@router.websocket('/ws/{tenant_id}')   
async def websocket_endpoint(websocket: WebSocket, tenant_id: str): 
    # try:
        '''
        1. Initialize the websocket connection
        2. Initialize the onboarding conversation
        3. Send the welcome message
        4. Wait for user input
        5. Get the next prompt from Gemini
        6. Store the Chat History
        7. Send the next prompt
        8. Send the response
        '''

        logger.debug(f"Managing websocket connection for tenant {tenant_id}")
        await manager.connect(websocket, tenant_id)
        while True:
            
            # data = await websocket.receive_json()
            
            await manager.broadcast(tenant_id,model.welcome_message())
    # except:
    #     logger.debug(f"Disconnecting websocket connection for tenant {tenant_id}")
    #     await manager.disconnect(websocket,tenant_id)

 
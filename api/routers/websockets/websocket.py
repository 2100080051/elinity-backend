from fastapi import APIRouter
import logging 
import uuid
from datetime import datetime
from fastapi import WebSocket
from utils.websockets import  manager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("group_chat")

router = APIRouter()

@router.post('/room/')
async def create_room():
    room_id = str(uuid.uuid4())
    return {"room_id": room_id,"created_at": datetime.now().isoformat()}

@router.websocket('/ws/{room_id}')
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        logger.debug(f"Managing websocket connection for room {room_id}")
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room_id, data) 
    except:
        logger.debug(f"Disconnecting websocket connection for room {room_id}")
        await manager.disconnect(websocket, room_id)

 
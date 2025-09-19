from elinity_ai.lumi import AICoachingSystem
from fastapi import APIRouter

router = APIRouter()


@router.post("/chat/")
async def lumi_endpoint(query: str):
    lumi = AICoachingSystem()
    response = lumi.process_message(query)
    return {"LumiAI": response}

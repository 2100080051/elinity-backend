from pydantic import BaseModel


class MultimodalSchema(BaseModel):
    url: str

class MultimodalResponse(BaseModel):
    url: str 
    text: str
    insights: str
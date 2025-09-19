from pydantic import BaseModel
from datetime import datetime

 
class TokenSchema(BaseModel):
    id: str
    tenant: str
    token: str
    type: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenCreate(BaseModel):
    token: str
    type: str

    class Config:
        from_attributes = True


class NotificationSchema(BaseModel):
    id: str
    tenant: str
    title: str
    message: str
    type: str
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    

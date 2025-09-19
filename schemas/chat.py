from pydantic import BaseModel,ConfigDict
from typing import Optional 
from datetime import datetime 
 

class GroupSchema(BaseModel):
    id: str
    asset_url: Optional[str]
    name: str
    tenant: str
    description: str
    created_at: datetime
    type: str
    status: str
    updated_at: Optional[datetime]


class GroupCreateSchema(BaseModel):
    name: str
    description: str
    asset_url: Optional[str] = None
    type: str

    class Config:
        from_attributes = True


class GroupMemberSchema(BaseModel):
    id: str
    group: str
    tenant: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] 

class AssetSchema(BaseModel):
    id: str
    tenant: str
    url: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class ChatSchema(BaseModel): 
    id: str
    sender: Optional[str]
    group: Optional[str]
    asset_url: Optional[str]
    message: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
    
    
    
    
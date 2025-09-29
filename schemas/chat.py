from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ----------------------------
# Group
# ----------------------------
class GroupSchema(BaseModel):   # For responses
    id: str
    asset_url: Optional[str]
    name: str
    tenant: str
    description: str
    created_at: datetime
    type: str
    status: str
    updated_at: Optional[datetime]


class GroupCreateSchema(BaseModel):   # For creating
    name: str
    description: str
    asset_url: Optional[str] = None
    type: str

    class Config:
        from_attributes = True


# ----------------------------
# Group Members
# ----------------------------
class GroupMemberSchema(BaseModel):   # For responses
    id: str
    group: str
    tenant: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime]


class GroupMemberCreateSchema(BaseModel):   # For creating
    group: str
    role: str = "member"

    class Config:
        from_attributes = True


# ----------------------------
# Assets
# ----------------------------
class AssetSchema(BaseModel):
    id: str
    tenant: str
    url: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Chats
# ----------------------------
class ChatSchema(BaseModel):   # For responses
    id: str
    sender: Optional[str]
    receiver: Optional[str]
    group: Optional[str]
    asset_url: Optional[str]
    message: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ChatCreateSchema(BaseModel):   # For creating
    receiver: Optional[str] = None
    group: Optional[str] = None
    asset_url: Optional[str] = None
    message: str   # required

    class Config:
        from_attributes = True

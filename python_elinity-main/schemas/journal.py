from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JournalCreate(BaseModel):
    """Schema for creating a new journal entry"""
    title: str
    content: str
    media: Optional[str] = None

    class Config:
        from_attributes = True


class JournalResponse(BaseModel):
    """Schema for journal response with all fields"""
    id: str
    tenant: str
    title: str
    content: str
    media: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

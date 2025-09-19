from pydantic import BaseModel
from datetime import datetime


class BlogSchema(BaseModel):
    id: str
    title: str
    content: str
    images: list
    videos: list
    tags: list
    links: list
    created_at: datetime
    updated_at: datetime
from database.session import Base
from sqlalchemy import Column, String, DateTime, JSON, Boolean
from datetime import datetime, timezone
import uuid


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(String, primary_key=True,default=uuid.uuid4)
    title = Column(String)
    content = Column(String)
    images = Column(JSON, default=list, nullable=False)
    videos = Column(JSON, default=list, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    links = Column(JSON, default=list, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
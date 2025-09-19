from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
import uuid
from datetime import datetime, timezone
from database.session import Base


def gen_uuid():
    return str(uuid.uuid4())

FB_TOKEN_TYPES = ['web', 'android', 'ios','other']
NOTIFICATION_TYPES = ['general', 'group', 'personal','system','social','event']

class FBToken(Base):
    __tablename__ = "fb_tokens"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    token = Column(String, nullable=False)
    type = Column(String, nullable=False,default='web')
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    __table_args__ = (
        CheckConstraint("type IN ('web', 'android', 'ios','other')", name="check_fb_token_type"),
    )
    class Config:
        from_attributes = True

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False,default='general')
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    __table_args__ = (
        CheckConstraint("type IN ('general', 'group','personal','system','social','event')", name="check_notification_type"),
    )
    class Config:
        from_attributes = True
    
    

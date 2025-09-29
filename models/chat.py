from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
import uuid
from database.session import Base


def gen_uuid():
    return str(uuid.uuid4())


# ----------------------------
# Constants
# ----------------------------
MEMBER_TYPES = ['member', 'admin', 'owner']
GROUP_TYPES = ['user_ai', 'users_ai', 'group']
GROUP_STATUS = ['active', 'inactive']


# ----------------------------
# Group
# ----------------------------
class Group(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    asset_url = Column(String, ForeignKey("assets.id"), nullable=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False, default='group')
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String, nullable=False, default='active')
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("type IN ('user_ai', 'users_ai', 'group')", name="check_group_type"),
        CheckConstraint("status IN ('active', 'inactive')", name="check_group_status"),
    )

    class Config:
        from_attributes = True


# ----------------------------
# GroupMember
# ----------------------------
class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(String, primary_key=True, default=gen_uuid)
    group = Column(String, ForeignKey("groups.id"), nullable=False)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    role = Column(String, nullable=False, default='member')
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("role IN ('member', 'admin', 'owner')", name="check_member_role"),
    )

    class Config:
        from_attributes = True


# ----------------------------
# Asset
# ----------------------------
class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=True)

    class Config:
        from_attributes = True


# ----------------------------
# Chat
# ----------------------------
class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True, default=gen_uuid)
    sender = Column(String, ForeignKey("tenants.id"), nullable=True)   # auto-fill from current_user
    receiver = Column(String, ForeignKey("tenants.id"), nullable=True) # one-on-one chats
    group = Column(String, ForeignKey("groups.id"), nullable=True)     # for group chats
    asset_url = Column(String, ForeignKey("assets.id"), nullable=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    class Config:
        from_attributes = True

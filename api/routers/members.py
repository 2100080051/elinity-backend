from fastapi import APIRouter, Depends, HTTPException, status
from models.chat import GroupMember
from database.session import get_db, Session
from utils.token import get_current_user
from models.user import Tenant
from schemas.chat import GroupMemberSchema, GroupMemberCreateSchema
from pydantic import BaseModel

router = APIRouter()

# ---------------------------
# Extra schema for updates
# ---------------------------
class GroupMemberUpdateSchema(BaseModel):
    role: str

    class Config:
        from_attributes = True


# ---------------------------
# Routes
# ---------------------------
@router.get("/", tags=["Members"])
async def get_members(
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(GroupMember).filter(
        GroupMember.tenant == current_user.id
    ).all()


@router.post("/", tags=["Members"], response_model=GroupMemberSchema)
async def create_member(
    member: GroupMemberCreateSchema,   # ✅ minimal schema
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member_obj = GroupMember(tenant=current_user.id, **member.model_dump())
    db.add(member_obj)
    db.commit()
    db.refresh(member_obj)
    return member_obj


@router.get("/{member_id}", tags=["Members"], response_model=GroupMemberSchema)
async def get_member(
    member_id: str,   # ✅ UUID, not int
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member_obj = db.query(GroupMember).filter(
        GroupMember.id == member_id,
        GroupMember.tenant == current_user.id   # ✅ restrict to tenant
    ).first()

    if not member_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    return member_obj


@router.put("/{member_id}", tags=["Members"], response_model=GroupMemberSchema)
async def update_member(
    member_id: str,
    member: GroupMemberUpdateSchema,   # ✅ only updatable fields
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member_obj = db.query(GroupMember).filter(
        GroupMember.id == member_id,
        GroupMember.tenant == current_user.id   # ✅ restrict to tenant
    ).first()

    if not member_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    for k, v in member.model_dump().items():
        setattr(member_obj, k, v)

    db.commit()
    db.refresh(member_obj)
    return member_obj


@router.delete("/{member_id}", tags=["Members"])
async def delete_member(
    member_id: str,
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member_obj = db.query(GroupMember).filter(
        GroupMember.id == member_id,
        GroupMember.tenant == current_user.id   # ✅ restrict to tenant
    ).first()

    if not member_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    db.delete(member_obj)
    db.commit()
    return {"message": "Member deleted"}

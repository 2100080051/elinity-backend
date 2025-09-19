from fastapi import APIRouter, Depends
from models.chat import Group
from database.session import get_db, Session
from utils.token import get_current_user
from models.user import Tenant
from schemas.chat import GroupSchema,GroupCreateSchema
from fastapi import HTTPException

router = APIRouter()

@router.get("/", tags=["Groups"])
async def get_groups(current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Group).filter(Group.tenant == current_user.id,Group.status == 'active').all()

@router.post("/", tags=["Groups"], response_model=GroupSchema)
async def create_group(group: GroupCreateSchema, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    group_obj = Group(tenant=current_user.id, **group.model_dump())
    db.add(group_obj)
    db.commit(); db.refresh(group_obj)
    return group_obj

@router.get("/{group_id}", tags=["Groups"], response_model=GroupSchema)
async def get_group(group_id: int, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Group).filter(Group.id == group_id,Group.status == 'active').first()

@router.put("/{group_id}", tags=["Groups"], response_model=GroupSchema)
async def update_group(group_id: int, group: GroupSchema, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    group_obj = db.query(Group).filter(Group.id == group_id,Group.status == 'active').first()
    if not group_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    for k, v in group.model_dump().items(): setattr(group_obj, k, v)
    db.commit(); db.refresh(group_obj)
    return group_obj

@router.delete("/{group_id}", tags=["Groups"])
async def delete_group(group_id: int, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    group_obj = db.query(Group).filter(Group.id == group_id,Group.status == 'active').first()
    if not group_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    group_obj.status = 'inactive'
    db.commit()
    return {"message": "Group deleted"}


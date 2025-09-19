from models.user import Tenant
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from database.session import Session
from typing import List
from fastapi import HTTPException

class UserService:
    def __init__(self):
        self.limit = 10
        self.offset = 0
    
    def get_tenants(self, limit: int = 10, offset: int = 0) -> List[Tenant]:
        with Session() as db:
            users = (
                db.query(Tenant)
                .options(
                    selectinload(Tenant.profile_pictures),
                    selectinload(Tenant.personal_info),
                    selectinload(Tenant.big_five_traits),
                    selectinload(Tenant.mbti_traits),
                    selectinload(Tenant.psychology),
                    selectinload(Tenant.interests_and_hobbies),
                    selectinload(Tenant.values_beliefs_and_goals),
                    selectinload(Tenant.favorites),
                    selectinload(Tenant.relationship_preferences),
                    selectinload(Tenant.friendship_preferences),
                    selectinload(Tenant.collaboration_preferences),
                    selectinload(Tenant.personal_free_form),
                    selectinload(Tenant.intentions),
                    selectinload(Tenant.aspiration_and_reflections),
                    selectinload(Tenant.ideal_characteristics),
                ) 
                .filter(Tenant.embedding_id.is_(None))
                .limit(limit)
                .offset(offset)
               
            )
            return users

    def get_last_index(self):
        with Session() as db:
            # Get the maximum embedding_id value or 0 if no embeddings exist
            max_id = db.query(func.max(Tenant.embedding_id)).scalar() or 0
            return max_id
    
    def update_embedding_id(self, tenant_id: str, embedding_id: int) -> Tenant:
        print(f"Updating embedding_id for tenant {tenant_id} with embedding_id {embedding_id}")
        with Session() as db:
            user = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user.embedding_id = embedding_id
            db.add(user)
            db.commit(); db.refresh(user)
            print(f"✅ Successfully updated embedding_id for tenant {tenant_id}")
            return user
        
     
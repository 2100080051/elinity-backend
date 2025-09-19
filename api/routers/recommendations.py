import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from elinity_ai.milvus_db import MilvusUserSimilarityPipeline
from models.user import Tenant
from schemas.user import RecommendedUserSchema, TenantSchema
from database.session import get_db
from utils.token import get_current_user
from elinity_ai.milvus_db import milvus_db
from elinity_ai.insights import ElinityInsights

router = APIRouter()

insights = ElinityInsights()

async def process_tenant_insight(tenant: Tenant, query: str, score: float) -> RecommendedUserSchema:
    """Helper function to process one tenant and get AI insight."""
    try:
        user_id = tenant.id
        name_parts = [
            tenant.personal_info.first_name,
            tenant.personal_info.middle_name,
            tenant.personal_info.last_name
        ]
        user_name = " ".join(part for part in name_parts if part)
        
        user_interests = ','.join(tenant.interests_and_hobbies.interests or [])

        # Use asyncio.to_thread to run the SYNC function in a thread
        ai_insight_text = await asyncio.to_thread(
            insights.generate_insight,
            query=query,
            user_id=user_id,
            user_name=user_name,
            score=score,
            user_interests=user_interests
        )

        return RecommendedUserSchema(
            tenant=TenantSchema.model_validate(tenant),
            score=score,
            ai_insight=ai_insight_text
        )
    except Exception as e:
        print(f"Error processing insight for user {tenant.id}: {e}")
        return RecommendedUserSchema(
            tenant=TenantSchema.model_validate(tenant),
            score=score,
            ai_insight=f"Could not generate insight for {user_name}."
        )


@router.get("/search", tags=["Recommendations"], response_model=List[RecommendedUserSchema])
async def get_recommendations_optimized(
    query: str, 
    current_user: Tenant = Depends(get_current_user), 
    db: Session = Depends(get_db)
): 
    try:
        # 1. Query Milvus (Assuming this part is reasonably fast or sync)
        res = milvus_db.query(query)
        if not res or not res[0]:
            return [] # No results found

        milvus_items = res[0]
        
        # 2. Create Score Map for reliable lookup (ID -> Score)
        # IMPORTANT: Assuming 'item.id' from Milvus IS the 'embedding_id' in Tenant
        score_map = {item.id: item.score for item in milvus_items}
        ids_to_fetch = list(score_map.keys())

        if not ids_to_fetch:
            return []

        # 3. Query Database (Optimized with joinedload)
        tenants = await asyncio.to_thread(
            db.query(Tenant)
              .options(
                  joinedload(Tenant.personal_info), 
                  joinedload(Tenant.interests_and_hobbies)
              )
              .filter(
                  Tenant.embedding_id.in_(ids_to_fetch), 
                  Tenant.id != current_user.id
              )
              .all
        )

        tasks = []
        for tenant in tenants:
            score = score_map.get(tenant.embedding_id)
            if score is not None:
                tasks.append(process_tenant_insight(tenant, query, score))

        users_with_insights = await asyncio.gather(*tasks)

        users_with_insights.sort(key=lambda x: x.score, reverse=True)

        return users_with_insights

    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", tags=["Recommendations"])
async def get_recommendations(current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get recommendations for the current user"""

    # 4. Query database for similar users
    # 5. Return list of recommended users
    # embedding_id = current_user.embedding_id
    # Initialize the pipeline using environment variables
    pipeline = MilvusUserSimilarityPipeline()
    
    # Find similar users for a specific user ID
    '''
    # 1. Query tenants for embedding id
    # 2. Query milvus for current user embedding id
    # 3. Query milvus for similar users
    '''
    similar_users = pipeline.find_similar_users_by_id(current_user.embedding_id, top_k=5)
    # Close connection
    pipeline.close()

    score_map = {user['id']: user['score'] for user in similar_users}
    ids_to_fetch = [user['id'] for user in similar_users]

    if not ids_to_fetch:
        return []

    # 3. Query Database (Optimized with joinedload)
    tenants = await asyncio.to_thread(
        db.query(Tenant)
            .options(
                joinedload(Tenant.personal_info), 
                joinedload(Tenant.interests_and_hobbies)
            )
            .filter(
                Tenant.embedding_id.in_(ids_to_fetch), 
                Tenant.id != current_user.id
            )
            .all
    )

    tasks = []
    for tenant in tenants:
        score = score_map.get(tenant.embedding_id)
        if score is not None:
            tasks.append(process_tenant_insight(tenant, "", score))

    users_with_insights = await asyncio.gather(*tasks)

    users_with_insights.sort(key=lambda x: x.score, reverse=True)

    return users_with_insights 
 
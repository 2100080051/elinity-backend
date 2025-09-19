from schemas.user import User
from ._celery import celery_app
from datetime import datetime,timezone 
import traceback
from core.logging import logger
from services.user_service import UserService
from services.model_converter import tenant_to_dict
from elinity_ai.embeddings import ElinityEmbedding
from elinity_ai.embeddings import milvus_client


user_service = UserService()

def prepare_tenant_metadata(tenants,start_index=1):
    """
    Prepare metadata for all tenants, filtering out failed embeddings.
    Returns a list of successfully processed metadata objects.
    """
    elinity_embedding = ElinityEmbedding()
    metadata_list = []
    failed_tenants = []
    
    for i, user_profile in enumerate(tenants,start=start_index):
        try:
            # Create a single embedding instance for all tenants
            text, embedding = elinity_embedding.create_embedding(user_profile)
            
            if not text or embedding is None:
                logger.error(f"Failed to generate embedding for tenant {user_profile.get('id', i+1)}")
                failed_tenants.append(user_profile.get('id', i+1))
                continue
                
            metadata = {
                "created_at": datetime.now(timezone.utc).isoformat(),  
                "source": "profile_embedding", 
                "tenant": user_profile,
                "id": i,  
                "vector": embedding,
                "bio": text
            }
            metadata_list.append(metadata)
            
        except Exception as e:
            tenant_id = user_profile.get('id', i+1)
            logger.error(f"Error processing tenant {tenant_id}: {str(e)}")
            logger.debug(traceback.format_exc())
            failed_tenants.append(tenant_id)
            continue
    
    logger.info(f"✅ Successfully prepared {len(metadata_list)} tenant embeddings")
    if failed_tenants:
        logger.warning(f"❌ Failed to process {len(failed_tenants)} tenants: {failed_tenants}")
    
    return metadata_list

@celery_app.task(name="core.celery._tasks.create_profile_embeddings", bind=True)
def create_profile_embeddings(self):

    try: 
        limit = 10
        offset = 0
        tenants = []
        tenants = user_service.get_tenants(limit, offset)

        if not tenants: 
            logger.info("No tenants found")
            return 
        
        logger.info(f"Found {tenants.count()} tenants") 
        tenants = [tenant_to_dict(tenant) for tenant in tenants]
        last_index = user_service.get_last_index()
        metadata_list = prepare_tenant_metadata(tenants,start_index=last_index+1)
        
        update_user = [user_service.update_embedding_id(data["tenant"]["id"],data["id"]) for data in metadata_list]
        result = milvus_client.upsert(metadata_list)
        logger.info(f"✅ Task completed at {datetime.now(timezone.utc).isoformat()}")
        logger.info(f"✅ Task result: {result}")
        
    except Exception as e:
        error_msg = f"Task failed: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise  RuntimeError(error_msg)
    
 
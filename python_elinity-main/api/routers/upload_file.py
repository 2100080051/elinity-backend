from fastapi import APIRouter, UploadFile, Depends
from utils.storage import AWSStorage
from utils.token import get_current_user
from models.user import Tenant 

router = APIRouter()


aws_client = AWSStorage()

@router.post("/", tags=["Upload Assets"])
async def upload_file(file: UploadFile, current_user: Tenant = Depends(get_current_user)) -> dict:
    print(file)
    # read file bytes before uploading
    data = await file.read()
    
    # upload bytes to AWS
    blob_url = aws_client.upload_bytes_to_aws(data, file.filename, current_user.id)
    
    return {"url": blob_url}

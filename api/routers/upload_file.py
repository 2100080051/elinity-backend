from fastapi import APIRouter, UploadFile, Depends
from utils.storage import FirebaseStorageClient
from utils.token import get_current_user
from models.user import Tenant

router = APIRouter()
firebase_client = FirebaseStorageClient()


@router.post("/", tags=["Upload Assets"])
async def upload_file(file: UploadFile, current_user: Tenant = Depends(get_current_user)) -> dict:
    """
    Upload a file to Firebase Storage under the current user's folder.
    """
    print(file)

    # Read file bytes
    data = await file.read()

    # Upload to Firebase (automatically handles bytes)
    blob_url = firebase_client.upload_file(data, file.filename, current_user.id)

    return {"url": blob_url}

from fastapi import APIRouter, Depends,UploadFile, File, Form
from models.chat import Asset
from database.session import get_db, Session
from utils.storage import AWSStorage
from utils.token import get_current_user
from models.user import Tenant
from schemas.chat import AssetSchema
router = APIRouter()

aws_client = AWSStorage()

@router.get("/", tags=["Assets"])
async def get(db: Session = Depends(get_db)):
    return db.query(Asset).all()

@router.post("/", tags=["Assets"], response_model=AssetSchema)
async def create(
    file: UploadFile = File(...), 
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
    ) -> AssetSchema: 

    # Read file bytes before uploading
    data = await file.read()

    # Upload file to AWS under tenant_id path
    blob_url = aws_client.upload_bytes_to_aws(data, file.filename, current_user.id)

    print(current_user.id)
    # # Create and persist asset
    asset = Asset(tenant=current_user.id, url=blob_url)
    db.add(asset)
    db.commit(); db.refresh(asset)
    
    return AssetSchema.model_validate(asset)   
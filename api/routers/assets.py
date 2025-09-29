from fastapi import APIRouter, Depends, UploadFile, File
from models.chat import Asset
from database.session import get_db, Session
from utils.storage import FirebaseStorageClient
from utils.token import get_current_user
from models.user import Tenant
from schemas.chat import AssetSchema

router = APIRouter()
firebase_client = FirebaseStorageClient()

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

    # Upload file to Firebase under tenant_id path
    blob_url = firebase_client.upload_file(data, f"{current_user.id}/{file.filename}", "default")


    print(f"Uploaded by tenant: {current_user.id}")

    # Create and persist asset
    asset = Asset(tenant=current_user.id, url=blob_url)
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return AssetSchema.model_validate(asset)

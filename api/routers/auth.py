from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.auth import RegisterRequest, RefreshRequest, LoginRequest, Token
from datetime import datetime, timezone  

from models.user import (
    Tenant,
    PersonalInfo,
    BigFiveTraits,
    MBTITraits,
    Psychology,
    InterestsAndHobbies,
    ValuesBeliefsAndGoals,
    Favorites,
    RelationshipPreferences,
    FriendshipPreferences,
    AspirationAndReflections,
    IdealCharacteristics,
    CollaborationPreferences,
    PersonalFreeForm,
    Intentions,
) 
from models.user import Tenant
from utils.token import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_access_from_refresh
)
from fastapi.security import OAuth2PasswordRequestForm

# {
#   "email": "johndoe@elinity.com",
#   "phone": "9102472789",
#   "password": "E4DOJ309#ESF"
# }

router = APIRouter(tags=['Authentication'])


@router.post("/register", response_model=Token )
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not req.email and not req.phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone is required")
    key_filter = []
    if req.email:
        key_filter.append(Tenant.email == req.email)
    if req.phone:
        key_filter.append(Tenant.phone == req.phone)
    exists = db.query(Tenant).filter(*key_filter).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
    hashed = get_password_hash(req.password)
    tenant_obj = Tenant(
        email=req.email,
        phone=req.phone,
        password=hashed,
        last_login=None
    )
    db.add(tenant_obj)
    db.commit(); db.refresh(tenant_obj)
    # Initialize related profile records
    db.add_all([
        PersonalInfo(tenant=tenant_obj.id),
        BigFiveTraits(tenant=tenant_obj.id),
        MBTITraits(tenant=tenant_obj.id),
        Psychology(tenant=tenant_obj.id),
        InterestsAndHobbies(tenant=tenant_obj.id),
        ValuesBeliefsAndGoals(tenant=tenant_obj.id),
        Favorites(tenant=tenant_obj.id),
        RelationshipPreferences(tenant=tenant_obj.id),
        FriendshipPreferences(tenant=tenant_obj.id),
        CollaborationPreferences(tenant=tenant_obj.id),
        PersonalFreeForm(tenant=tenant_obj.id),
        Intentions(tenant=tenant_obj.id),
        AspirationAndReflections(tenant=tenant_obj.id),
        IdealCharacteristics(tenant=tenant_obj.id),
    ])
    db.commit()
    access_token = create_access_token({"sub": tenant_obj.id})
    refresh_token = create_refresh_token({"sub": tenant_obj.id})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/login", response_model=Token )
async def login(req: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate via JSON email/phone & password"""
    if req.email:
        user = db.query(Tenant).filter(Tenant.email == req.email).first()
    elif req.phone:
        user = db.query(Tenant).filter(Tenant.phone == req.phone).first()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone required")
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    user.last_login = datetime.now(timezone.utc)
    db.commit(); db.refresh(user)
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    """Authenticate via form-data (for Swagger OAuth2)"""
    username = form_data.username
    password = form_data.password
    if "@" in username:
        user = db.query(Tenant).filter(Tenant.email == username).first()
    else:
        user = db.query(Tenant).filter(Tenant.phone == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    user.last_login = datetime.now(timezone.utc)
    db.commit(); db.refresh(user)
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post('/refresh', response_model=Token)
async def refresh_token_endpoint(refresh_req: RefreshRequest, db: Session = Depends(get_db)):
    token = refresh_req.refresh_token
    # Treat missing or literal "null" as invalid
    if not token or token.strip().lower() == "null":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is required")
    try:
        access_token = create_access_from_refresh(token)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return Token(access_token=access_token, refresh_token=token, token_type='bearer')
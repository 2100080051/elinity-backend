from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from jose import jwt, JWTError
from typing import Optional
from fastapi import Depends, HTTPException, status
from models.user import Tenant
from database.session import get_db,Session
from utils.settings import (
    SECRET_KEY,
    JWT_HASH_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    HASH_ALGORITHM
)
 
# Security utils
pwd_context = CryptContext(schemes=[HASH_ALGORITHM], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",  
    scopes={"me": "Read current user's profile"}  
)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Generate an access token with specified expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)

def verify_access_token(token: str, db: Session) -> Optional[Tenant]:
    """Verify the access token and return the user if valid"""
    
    if not token:
        
        return None
        
    try:
        # Decode the token
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_HASH_ALGORITHM])
        
        user_id = payload.get("sub") 
        
        if not user_id:
            
            return None
            
        # Get user from database
        
        user = db.query(Tenant).filter(Tenant.id == user_id).first()
        
        
        if not user:
            
            return None
            
        
        return user
        
    except jwt.JWTError as e: 
        return None
    except Exception as e: 
        return None

def create_access_from_refresh(refresh_token: str) -> str:
    """Generate an access token from a refresh token."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=JWT_HASH_ALGORITHM)
        return create_access_token({"sub": payload["sub"]})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

def create_refresh_token(data: dict) -> str:
    """Generate a refresh token with longer expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)

async def get_current_user(
    request: Request = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Decode JWT, fetch Tenant, and enforce authentication""" 
    
    # Try to get token from Authorization header first
    if not token and request:
        
        # Fall back to cookie if no Authorization header
        token = request.cookies.get("access_token")
        
        if token and token.startswith("Bearer "):
            token = token[7:]  # Remove 'Bearer ' prefix
            
    
    if not token:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        
        user = verify_access_token(token, db)
        if not user:
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except JWTError as e:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication",
        )

async def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> Tenant:
    """Get current user from access_token cookie"""
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = token[7:]  # Remove 'Bearer ' prefix
    user = verify_access_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user
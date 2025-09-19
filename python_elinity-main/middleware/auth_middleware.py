from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.routing import APIRoute
from typing import Callable, Optional, Dict, Any
from jose import JWTError, jwt
from database.session import get_db
from models.user import Tenant
from sqlalchemy.orm import Session
import logging
from utils.token import verify_access_token
from contextlib import contextmanager   

# Configure logging
logging.basicConfig(level=logging.INFO)

 

@contextmanager
def get_db_session():
    """Get a database session with proper cleanup"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

async def get_current_user_from_token(token: str, db: Session) -> Optional[Tenant]:
    """Get the current user from the token in the cookie"""
    if not token or not token.startswith("Bearer "):
        
        return None
        
    token = token[7:]  # Remove 'Bearer ' prefix
    
    return verify_access_token(token, db) 

class AdminAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        request = Request(scope, receive=receive)
        
        # Only check for admin paths
        if request.url.path.startswith('/admin/'):
            # Skip auth for login, auth, and static files
            if (request.url.path in ['/admin/login', '/admin/static', '/auth/login'] or 
                request.url.path.startswith('/admin/static/') or
                request.url.path.startswith('/auth/')):
                return await self.app(scope, receive, send)
            
            try:
                with get_db_session() as db:
                    token = request.cookies.get("access_token")
                    user = await get_current_user_from_token(token, db) if token else None
                    
                    # Check if user is authenticated and is admin
                    if not user or not hasattr(user, 'role') or user.role.lower() != 'admin':
                        
                        # If it's an API request, return 401
                        if 'application/json' in request.headers.get('accept', ''):
                            response = JSONResponse(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"detail": "Not authenticated or insufficient permissions"}
                            )
                        else:
                            # For web requests, redirect to login
                            # Don't redirect to login if we're already on the login page
                            if request.url.path == '/admin/auth/login':
                                return await self.app(scope, receive, send)
                                
                            response = RedirectResponse(
                                url=f"/admin/auth/login?next={request.url.path}",
                                status_code=status.HTTP_303_SEE_OTHER
                            )
                            response.delete_cookie("access_token", path="/")
                        
                        await response(scope, receive, send)
                        return
                    
                    # User is authenticated and is admin, continue with the request
                    
                    return await self.app(scope, receive, send)
                    
            except Exception as e:
                
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Internal server error"}
                )
                await response(scope, receive, send)
                return
                
        # For non-admin paths, continue without auth check
        return await self.app(scope, receive, send)

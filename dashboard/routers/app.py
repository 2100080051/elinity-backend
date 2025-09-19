from fastapi import APIRouter, Depends,status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from database.session import get_db, Session
from models.user import Tenant
from utils.token import verify_access_token

# Import sub-routers
from .dashboard import router as dashboard_router
from .blog import router as blog_router
from .users import router as users_router
from .login import router as auth_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
# Include blog router with admin prefix
router.include_router(blog_router, prefix="", tags=["blog"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Get base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Setup templates
templates = Jinja2Templates(directory=str(BASE_DIR / "dashboard" / "templates"))

# Admin dependency
async def get_admin_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Dependency to check if the current user is an admin"""
    # Get the token from the cookie
    token = request.cookies.get("access_token")
    
    if not token:
        # No token found, redirect to login
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url=f"/auth/login?next={request.url.path}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    try:
        current_user = verify_access_token(token, db)
        if not current_user or not hasattr(current_user, 'role') or current_user.role != 'admin':
            raise ValueError("Invalid user or not an admin")
        return current_user
    except Exception as e:
        # Token verification failed or user is not admin
        response = RedirectResponse(
            url=f"/auth/login?next={request.url.path}",
            status_code=status.HTTP_303_SEE_OTHER
        )
        # Clear invalid token
        response.delete_cookie("access_token")
        return response

# Admin routes
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db) 
):
    """Admin dashboard page"""
    try:
        # Get the token from the cookie
        token = request.cookies.get("access_token")
        
        # If no token, redirect to login
        if not token:
            return RedirectResponse(
                url=f"/auth/login?next={request.url.path}",
                status_code=status.HTTP_303_SEE_OTHER
            )
        
        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        # Verify the token and get the user
        current_user = verify_access_token(token, db)
        
        # If token is invalid or user is not admin, redirect to login
        if not current_user or not hasattr(current_user, 'role') or current_user.role != 'admin':
            response = RedirectResponse(
                url=f"/auth/login?next={request.url.path}",
                status_code=status.HTTP_303_SEE_OTHER
            )
            response.delete_cookie("access_token")
            return response
        
        # If we get here, we have a valid admin user
        # Get some admin stats
        total_users = db.query(Tenant).count()
        total_admins = db.query(Tenant).filter(Tenant.role == 'admin').count()
        
        context = {
            "request": request,
            "current_user": current_user,
            "total_users": total_users,
            "total_admins": total_admins,
            "page_title": "Admin Dashboard"
        }
        return templates.TemplateResponse("admin/dashboard.html", context)
        
    except Exception as e:
        # If any error occurs, redirect to login
        response = RedirectResponse(
            url=f"/auth/login?next={request.url.path}",
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.delete_cookie("access_token")
        return response

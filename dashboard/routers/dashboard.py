import os
from fastapi import APIRouter, Request, Depends, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.session import get_db, Session
from utils.token import get_current_user_from_cookie as get_current_user
from models.user import Tenant
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent  # Go up to project root

router = APIRouter(tags=["dashboard"])

# Mount static files under /admin/static
router.mount("/static", StaticFiles(directory=str(BASE_DIR / "dashboard" / "static")), name="dashboard_static")

# Setup templates
templates = Jinja2Templates(directory=str(BASE_DIR / "dashboard" / "templates"))

 
# Routes
@router.get("", response_class=HTMLResponse)
async def dashboard_page(
    request: Request, 
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render the admin dashboard"""
    
    
    # At this point, we know the user is authenticated and is an admin (handled by middleware)
    try:
        # Get dashboard statistics
        total_users = db.query(Tenant).count()
        
        context = {
            "request": request,
            "current_user": {
                "email": current_user.email,
                "role": current_user.role,
                "id": current_user.id
            },
            "total_users": total_users,
            "active_users": 0,  # Add your logic here
            "new_users_this_week": 0,  # Add your logic here
            "page_title": "Admin Dashboard"
        }
        return templates.TemplateResponse("admin/dashboard.html", context)
        
    except HTTPException as e:
        
        return RedirectResponse(
            f"/admin/auth/login?next={request.url.path}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as e:
        
        return RedirectResponse(
            "/admin/auth/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, current_user: Tenant = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    users = db.query(Tenant).all()
    context = {
        "request": request,
        "current_user": current_user,
        "users": users,
        "title": "Users"
    }
    return templates.TemplateResponse("users/list.html", context)

@router.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request, current_user: Tenant = Depends(get_current_user)):
    context = {
        "request": request,
        "current_user": current_user,
        "title": "Analytics"
    }
    return templates.TemplateResponse("analytics.html", context)

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, current_user: Tenant = Depends(get_current_user)):
    context = {
        "request": request,
        "current_user": current_user,
        "title": "Settings"
    }
    return templates.TemplateResponse("admin/settings.html", context)

# API endpoints for dashboard data
@router.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: Tenant = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    total_users = db.query(Tenant).count()
    
    # Add your actual stats calculation here
    return {
        "total_users": total_users,
        "active_users": 0,  # Add your logic
        "new_users_this_week": 0,  # Add your logic
        "engagement_rate": 0  # Add your logic
    }
 
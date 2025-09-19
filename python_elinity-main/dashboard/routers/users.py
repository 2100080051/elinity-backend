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

 
@router.get("/", response_class=HTMLResponse)
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
 
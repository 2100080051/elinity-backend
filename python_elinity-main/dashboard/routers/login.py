from datetime import timedelta
from pathlib import Path
from typing import Optional
from fastapi import Form
from fastapi import APIRouter, Request, Depends, status, HTTPException, Response, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.session import get_db
from models.user import Tenant
from utils.token import verify_password, create_access_token


# Setup router
router = APIRouter(tags=["auth"])

# Get base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Setup templates
templates = Jinja2Templates(directory=str(BASE_DIR / "dashboard" / "templates"))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """Render the login page"""
    # Get the next URL from query parameters, default to /admin/dashboard
    next_url = request.query_params.get("next", "/admin/dashboard")
    
    
    
    
    # Get CSRF token from cookies or generate a new one
    csrf_token = request.cookies.get("csrftoken")
    
    response = templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request, 
            "error": error,
            "next": next_url,
            "csrf_token": csrf_token
        }
    )
    
    # Set CSRF token in cookie if not present
    if not csrf_token:
        csrf_token = "dummy-csrf-token"
        response.set_cookie(
            "csrftoken",
            value=csrf_token,
            httponly=True,
            samesite="lax",
            max_age=3600  # 1 hour
        )
    
    return response
 


@router.post("/login")
async def login(
    request: Request, 
    db: Session = Depends(get_db),
    email: str = Form(None),
    password: str = Form(None),
    next: str = Form("/admin")
):
    
    
    
    # Get form data from form submission
    form_data = await request.form()
    email = email or form_data.get("email")
    password = password or form_data.get("password")
    redirect_url = next or "/admin/"
    
    
    
    
    
    
    # Basic validation
    if not email or not password:
        error_msg = "Email and password are required"
        
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request, 
                "error": error_msg, 
                "email": email, 
                "next": redirect_url
            },
            status_code=status.HTTP_200_OK
        )
    
    try:
        # Find user by email
        
        user = db.query(Tenant).filter(Tenant.email == email).first()
        
        if not user or not verify_password(password, user.password):
            error = "Invalid email or password"
            
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": error, "email": email, "next": next}
            )
        
        # Check if user is admin
        if user.role != "admin":
            error = "Access denied. Admin privileges required."
            
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": error, "email": email, "next": next}
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Ensure next URL is safe and defaults to /admin
        safe_next = next if (next and next.startswith("/") and not next.startswith("/admin/auth")) else "/admin"
        
        
        # Create response
        response = RedirectResponse(
            url=safe_next,
            status_code=status.HTTP_303_SEE_OTHER
        )
        
        # Set secure cookie with token
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=60 * 60 * 24 * 7,  # 7 days
            samesite="lax",
            secure=False  # Set to True in production with HTTPS
        )
        
        # Regenerate CSRF token after successful login
        response.set_cookie(
            key="csrftoken",
            value="new-csrf-token-after-login",
            httponly=True,
            samesite="lax",
            max_age=3600  # 1 hour
        )
        
        
        return response
        
    except Exception as e:
        error = f"An error occurred: {str(e)}"
        
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": error, "email": email, "next": next}
        )


@router.get("/logout")
async def logout():
    """Handle user logout"""
    response = RedirectResponse("/admin/auth/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

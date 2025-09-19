import os
import datetime
import uuid
from fastapi import APIRouter, Depends, Request, Form, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional, Dict, Any, List
import secrets
import json
import uuid
import os
from datetime import datetime,timezone

# Import storage utility
from utils.storage import AWSStorage

from database.session import get_db
from models.user import Tenant
from models.blogs import Blog
from utils.token import get_current_user_from_cookie as get_current_user

# Configure upload directory
UPLOAD_DIR = Path("static/uploads/blogs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

BASE_DIR = Path(__file__).parent.parent.parent

# Create the router with prefix
router = APIRouter(
    prefix="/blogs",
    tags=["blog_management"],
    responses={404: {"description": "Not found"}},
)

# Mount static files
router.mount("/static", StaticFiles(directory=str(BASE_DIR / "dashboard" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "dashboard" / "templates"))

 
# Blog Management Routes
@router.get("/", response_class=HTMLResponse)
async def list_blogs(request: Request, 
                   current_user: Tenant = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    blogs = db.query(Blog).all()
    
    context = {
        "request": request,
        "current_user": {
            "email": current_user.email,
            "role": current_user.role,
            "id": current_user.id
        },
        "blogs": blogs,
        "page_title": "Blog Management"
    }
    return templates.TemplateResponse("blogs/list.html", context)

# Generate a CSRF token
def generate_csrf_token():
    return secrets.token_urlsafe(32)


# Add blog form
@router.get("/add/", response_class=HTMLResponse)  
async def add_blog(
    request: Request, 
    current_user: Tenant = Depends(get_current_user)
):
    # Generate a new CSRF token for this session
    csrf_token = generate_csrf_token()
    
    # Store the token in the session
    request.session['csrf_token'] = csrf_token
    
    context: Dict[str, Any] = {
        "request": request,
        "current_user": {
            "email": current_user.email,
            "role": current_user.role,
            "id": current_user.id
        },
        "title": "Add Blog",
        "csrf_token": csrf_token,
        "max_file_size": 50 * 1024 * 1024,  # 50MB
        "allowed_file_types": ["image/jpeg", "image/png", "image/gif", "video/mp4", "video/webm"],
        "max_files": 10
    }
    return templates.TemplateResponse("blogs/add.html", context)

 
# Handle file upload
@router.post("/upload/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: Tenant = Depends(get_current_user)
):
    try:
        # Initialize storage
        storage = AWSStorage()
        
        # Read file content
        content = await file.read()
        
        # Generate a unique filename
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        
        # Upload to S3
        file_url = storage.upload_bytes_to_aws(
            data=content,
            filename=filename,
            tenant_id=str(current_user.id)
        )
        
        return JSONResponse({
            "url": file_url,
            "filename": filename
        })
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

# Create new blog post
@router.post("/", response_class=HTMLResponse) 
async def create_blog(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    slug: Optional[str] = Form(None),
    status: str = Form("draft"),
    tags: str = Form(""),
    links: str = Form(""),
    images: str = Form("[]"),
    videos: str = Form("[]"),
    csrf_token: str = Form(...),
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify CSRF token
    if 'csrf_token' not in request.session or request.session.get('csrf_token') != csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
    
    # Clear the CSRF token after use
    request.session.pop('csrf_token', None)
    
    try:
        # Parse the JSON strings for images and videos
        try:
            image_urls = json.loads(images) if images else []
            video_urls = json.loads(videos) if videos else []
        except json.JSONDecodeError:
            image_urls = []
            video_urls = []
        
        # Parse tags and links
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        link_list = [link.strip() for link in links.split("\n") if link.strip()]
        
        # Create blog post
        # Create blog post
        blog = Blog(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            slug=slug or None,  # Will be auto-generated if None
            images=image_urls,
            videos=video_urls,
            tags=tag_list,
            links=link_list,
            status=status,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(blog)
        db.commit()
        db.refresh(blog)
        
        # Redirect to the list of blogs
        return RedirectResponse(
            url=request.url_for("list_blogs"),
            status_code=status.HTTP_303_SEE_OTHER
        )
        
    except Exception as e:
        db.rollback()
        print(f"Error creating blog post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating blog post: {str(e)}"
        )


# View single blog post - This must come after all other specific routes
@router.get("/{blog_id}", response_class=HTMLResponse)
async def view_blog(
    blog_id: int,
    request: Request, 
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # First check if the path is actually a string that should be handled by another route
    if not str(blog_id).isdigit():
        raise HTTPException(status_code=404, detail="Page not found")
        
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    context = {
        "request": request,
        "current_user": {
            "email": current_user.email,
            "role": current_user.role,
            "id": current_user.id
        },
        "blog": {
            "id": blog.id,
            "title": blog.title,
            "content": blog.content,
            "slug": blog.slug,
            "status": blog.status,
            "images": blog.images,
            "videos": blog.videos,
            "tags": blog.tags,
            "links": blog.links,
            "created_at": blog.created_at,
            "updated_at": blog.updated_at
        },
        "page_title": blog.title
    }
    return templates.TemplateResponse("blogs/view.html", context)


# Edit blog post
@router.get("/update/{blog_id}", response_class=HTMLResponse)
async def edit_blog(
    blog_id: int,
    request: Request, 
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    context = {
        "request": request,
        "current_user": {
            "email": current_user.email,
            "role": current_user.role,
            "id": current_user.id
        },
        "blog": blog,
        "title": f"Edit: {blog.title}"
    }
    return templates.TemplateResponse("blogs/update.html", context)

# Delete blog post
@router.post("/delete/{blog_id}", response_class=HTMLResponse)
async def settings(blog_id:int,request: Request, current_user: Tenant = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    db.delete(blog)
    db.commit()
    db.refresh(blog) 
    return RedirectResponse(url="/admin/blogs", status_code=status.HTTP_302_FOUND)
    
    

 
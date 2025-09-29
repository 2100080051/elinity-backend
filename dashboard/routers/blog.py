import os
import uuid
import secrets
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import (
    APIRouter, Depends, Request, Form, File, UploadFile,
    HTTPException, status
)
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Import storage utility
from utils.storage import FirebaseStorageClient
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
router.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "dashboard" / "static")),
    name="static"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "dashboard" / "templates"))


# -------------------- Blog Management Routes --------------------

@router.get("/", response_class=HTMLResponse)
async def list_blogs(
    request: Request,
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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


# -------------------- CSRF Token --------------------
def generate_csrf_token():
    return secrets.token_urlsafe(32)


# -------------------- Add Blog Form --------------------
@router.get("/add/", response_class=HTMLResponse)
async def add_blog(
    request: Request,
    current_user: Tenant = Depends(get_current_user)
):
    csrf_token = generate_csrf_token()
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
        "allowed_file_types": [
            "image/jpeg", "image/png", "image/gif", "video/mp4", "video/webm"
        ],
        "max_files": 10
    }
    return templates.TemplateResponse("blogs/add.html", context)


# -------------------- Handle File Upload --------------------
@router.post("/upload/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: Tenant = Depends(get_current_user)
):
    try:
        firebase_client = FirebaseStorageClient()

        content = await file.read()
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"

        # ✅ Upload to Firebase (not AWS)
        file_url = firebase_client.upload_file(
            data=content,
            remote_path=f"{current_user.id}/{filename}"
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


# -------------------- Create New Blog Post --------------------
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
    if 'csrf_token' not in request.session or request.session.get('csrf_token') != csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
    request.session.pop('csrf_token', None)

    try:
        try:
            image_urls = json.loads(images) if images else []
            video_urls = json.loads(videos) if videos else []
        except json.JSONDecodeError:
            image_urls, video_urls = [], []

        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        link_list = [link.strip() for link in links.split("\n") if link.strip()]

        blog = Blog(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            slug=slug or None,
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


# -------------------- View Single Blog --------------------
@router.get("/{blog_id}", response_class=HTMLResponse)
async def view_blog(
    blog_id: int,
    request: Request,
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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


# -------------------- Edit Blog --------------------
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


# -------------------- Delete Blog --------------------
@router.post("/delete/{blog_id}", response_class=HTMLResponse)
async def delete_blog(
    blog_id: int,
    request: Request,
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    db.delete(blog)
    db.commit()

    return RedirectResponse(url="/admin/blogs", status_code=status.HTTP_302_FOUND)

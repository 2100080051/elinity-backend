# app.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from middleware.auth_middleware import AdminAuthMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from api.routers import auth,users,upload_file,assets,chats,groups,members,journal,multimodal,notifications,plans,blogs,recommendations,lumi,question_cards 
from dashboard.routers import app as dashboard_app,login
from api.routers.websockets import websocket,onboarding,group_chat 
from fastapi.responses import HTMLResponse
from database.session import engine, Base
from core.limiter import RateLimiter

limiter = RateLimiter(requests=5,window=60)

import os 
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app:FastAPI):
    # Create database tables on startup
    Base.metadata.create_all(bind=engine) 

    # Seed database with fake data if empty
    # subprocess.run(["python", "scripts/seed_db.py"], check=True) 
    yield
    # Optional: drop tables on shutdown
    # Base.metadata.drop_all(bind=engine) 
     
# Initialize the application with lifespan
app = FastAPI(lifespan=lifespan)

# Add middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("CSRF_SECRET_KEY"),
    session_cookie="session"
)
app.add_middleware(AdminAuthMiddleware)

# Mount static files
static_dir = Path(__file__).parent / "dashboard" / "static"
app.mount(
    "/static",
    StaticFiles(directory=str(static_dir)),
    name="static"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers 
app.include_router(prefix='/auth', router=auth.router)
app.include_router(prefix='/users', router=users.router)
app.include_router(prefix='/upload-file',router=upload_file.router)
app.include_router(prefix='/assets',router=assets.router)
app.include_router(prefix='/chats',router=chats.router)
app.include_router(prefix='/groups',router=groups.router)
app.include_router(prefix='/members',router=members.router)
app.include_router(prefix='/journal',router=journal.router)
app.include_router(prefix='/websocket',router=websocket.router)
app.include_router(prefix='/onboarding',router=onboarding.router)
app.include_router(prefix='/multimodal',router=multimodal.router)
app.include_router(prefix='/room',router=group_chat.router)
app.include_router(prefix='/notifications',router=notifications.router)
app.include_router(prefix='/plans',router=plans.router)
app.include_router(prefix='/blogs',router=blogs.router)
app.include_router(prefix='/recommendations',router=recommendations.router)
app.include_router(prefix='/lumi',router=lumi.router)
app.include_router(prefix='/questions',router=question_cards.router)

# Include dashboard router with /admin prefix
app.include_router(
    dashboard_app.router,
    prefix="/admin",
    tags=["dashboard"]
)

# Include login routes with /admin/auth prefix
app.include_router(
    login.router,
    prefix="/admin/auth",
    tags=["auth"]
)


@app.get("/", response_class=HTMLResponse)
async def root(rate_limited:bool=Depends(limiter)):
    with open("templates/index.html") as f:
        return f.read()


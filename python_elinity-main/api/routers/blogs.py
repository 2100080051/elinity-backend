from fastapi import APIRouter,Depends
from models.blogs import Blog  
from database.session import get_db,Session
from schemas.blogs import BlogSchema

router = APIRouter(tags=["blogs"])

@router.get("/", response_model=list[BlogSchema])
def get_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.active == True).all()
    return blogs
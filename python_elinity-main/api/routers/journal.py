from fastapi import APIRouter, Depends, HTTPException, status
from utils.token import get_current_user
from models.user import Tenant
from database.session import get_db, Session
from models.journal import Journal
from typing import List
from schemas.journal import JournalCreate, JournalResponse


router = APIRouter(prefix="", tags=["Journal"])


@router.get("/", response_model=List[JournalResponse])
def get_journals(current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all journal entries for the current user"""
    journals = db.query(Journal).filter(Journal.tenant == current_user.id).all()
    return journals


@router.get("/{id}", response_model=JournalResponse)
def get_journal_by_id(id: str, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific journal entry by ID for the current user"""
    journal = db.query(Journal).filter(Journal.id == id, Journal.tenant == current_user.id).first()
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    return journal


@router.post("/", response_model=JournalResponse)
def create_journal(journal: JournalCreate, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new journal entry for the current user"""
    # Create journal with tenant ID from the authenticated user and data from request
    new_journal = Journal(tenant=current_user.id, **journal.model_dump())
    
    # Add to database and commit
    db.add(new_journal)
    db.commit()
    db.refresh(new_journal)
    return new_journal


@router.put("/{id}", response_model=JournalResponse)
def update_journal(id: str, journal: JournalCreate, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    journal = db.query(Journal).filter(Journal.id == id,Journal.tenant == current_user.id).first()
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    for k, v in journal.model_dump().items(): setattr(journal, k, v)
    db.commit(); db.refresh(journal)
    return journal


@router.delete("/{id}")
def delete_journal(id: str, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    journal = db.query(Journal).filter(Journal.id == id,Journal.tenant == current_user.id).first()
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    db.delete(journal)
    db.commit()
    return {"message": "Journal deleted successfully"}

from sqlalchemy.orm import Session
from models.shared_checklist import SharedChecklist
from schemas.shared_checklist import SharedChecklistCreate
from crud.checklist import get_checklist

def create_shared_link(db: Session, checklist_id: int, user_id: int):
    """Create a shareable link for a checklist if the user owns it"""
    # First check if the user owns the checklist
    checklist = get_checklist(db, checklist_id, user_id)
    if not checklist:
        return None
    
    # Check if a share token already exists
    existing = db.query(SharedChecklist).filter(SharedChecklist.checklist_id == checklist_id).first()
    if existing:
        return existing
    
    # Create a new shared checklist record
    db_shared_checklist = SharedChecklist(
        checklist_id=checklist_id,
        share_token=SharedChecklist.generate_token()
    )
    db.add(db_shared_checklist)
    db.commit()
    db.refresh(db_shared_checklist)
    return db_shared_checklist

def get_checklist_by_token(db: Session, token: str):
    """Get a checklist using a share token"""
    shared_checklist = db.query(SharedChecklist).filter(SharedChecklist.share_token == token).first()
    if not shared_checklist:
        return None
    return shared_checklist.checklist

def revoke_shared_link(db: Session, checklist_id: int, user_id: int):
    """Revoke a shared link for a checklist"""
    # First check if the user owns the checklist
    checklist = get_checklist(db, checklist_id, user_id)
    if not checklist:
        return False
    
    # Find and delete the shared link
    shared = db.query(SharedChecklist).filter(SharedChecklist.checklist_id == checklist_id).first()
    if not shared:
        return False
    
    db.delete(shared)
    db.commit()
    return True

def get_shared_link(db: Session, checklist_id: int, user_id: int):
    """Get the shared link for a checklist if the user owns it"""
    # First check if the user owns the checklist
    checklist = get_checklist(db, checklist_id, user_id)
    if not checklist:
        return None
    
    return db.query(SharedChecklist).filter(SharedChecklist.checklist_id == checklist_id).first()
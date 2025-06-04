from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core.security import get_current_user, require_admin
from models.user import User
from core.config import settings  

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/users")
def list_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)  
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return users
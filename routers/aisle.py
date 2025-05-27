from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.aisle import Aisle, AisleCreate
from crud import aisle as aisle_crud
from core.security import get_current_user, verify_pi_api_key
from models.user import User

router = APIRouter(
    prefix="/aisles",
    tags=["aisles"]
)

@router.post("/", response_model=Aisle, status_code=status.HTTP_201_CREATED)
def create_aisle(
    aisle_data: AisleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new aisle (admin only)"""
    return aisle_crud.create_aisle(db, aisle_data)

@router.get("/", response_model=List[Aisle])
def read_aisles(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all aisles"""
    return aisle_crud.get_aisles(db, skip, limit)

@router.get("/{aisle_id}", response_model=Aisle)
def read_aisle(
    aisle_id: int, 
    db: Session = Depends(get_db)
):
    """Get a specific aisle by ID"""
    db_aisle = aisle_crud.get_aisle(db, aisle_id)
    if db_aisle is None:
        raise HTTPException(status_code=404, detail="Aisle not found")
    return db_aisle
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.checklist import (
    Checklist, ChecklistWithItems, ChecklistCreate, ChecklistUpdate,
    ChecklistItem, ChecklistItemCreate, ChecklistItemUpdate
)
from crud import checklist as checklist_crud
from core.security import get_current_user
from models.user import User

router = APIRouter(
    prefix="/checklists",
    tags=["checklists"]
)

@router.post("/", response_model=ChecklistWithItems)
def create_checklist(
    checklist: ChecklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new checklist for the current user"""
    return checklist_crud.create_checklist(db, checklist, current_user.id)

@router.get("/", response_model=List[ChecklistWithItems])
def get_user_checklists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all checklists for the current user"""
    return checklist_crud.get_user_checklists(db, current_user.id, skip, limit)

@router.get("/{checklist_id}", response_model=ChecklistWithItems)
def get_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific checklist by ID"""
    checklist = checklist_crud.get_checklist(db, checklist_id, current_user.id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return checklist

@router.put("/{checklist_id}", response_model=Checklist)
def update_checklist_name(
    checklist_id: int,
    checklist_update: ChecklistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a checklist's name"""
    updated = checklist_crud.update_checklist_name(db, checklist_id, current_user.id, checklist_update.name)
    if not updated:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return updated

@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a checklist"""
    deleted = checklist_crud.delete_checklist(db, checklist_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return {"status": "success"}

# Checklist Items endpoints
@router.post("/{checklist_id}/items", response_model=ChecklistItem)
def add_item_to_checklist(
    checklist_id: int,
    item: ChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an item to a checklist"""
    item = checklist_crud.add_checklist_item(db, checklist_id, current_user.id, item)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return item

@router.put("/{checklist_id}/items/{item_id}", response_model=ChecklistItem)
def update_checklist_item(
    checklist_id: int,
    item_id: int,
    item_update: ChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a checklist item"""
    updated = checklist_crud.update_checklist_item(db, item_id, checklist_id, current_user.id, item_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found or not accessible")
    return updated

@router.delete("/{checklist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checklist_item(
    checklist_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a checklist item"""
    deleted = checklist_crud.delete_checklist_item(db, item_id, checklist_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found or not accessible")
    return {"status": "success"}
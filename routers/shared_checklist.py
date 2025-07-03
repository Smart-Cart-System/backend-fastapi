from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict

from database import get_db
from models.user import User
from schemas.checklist import ChecklistWithItems, ChecklistItemCreate
from schemas.shared_checklist import SharedChecklistResponse
from crud import shared_checklist as shared_crud
from crud import checklist as checklist_crud
from core.security import get_current_user

router = APIRouter(
    prefix="/shared",
    tags=["shared-checklists"]
)

@router.post("/checklist/{checklist_id}", response_model=Dict)
def create_share_link(
    checklist_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a shareable link for a checklist"""
    shared = shared_crud.create_shared_link(db, checklist_id, current_user.id)
    if not shared:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    # Get base URL for the frontend - this should be configurable
    base_url = str(request.base_url).rstrip("/")
    shareable_url = f"{base_url}/shared/{shared.share_token}"
    
    return {
        "id": shared.id,
        "checklist_id": shared.checklist_id,
        "share_token": shared.share_token,
        "shareable_url": shareable_url,
        "created_at": shared.created_at,
        "created_by": {
            "id": current_user.id,  # Assuming current_user has an id attribute     
            "username": current_user.username  # Assuming current_user has a username attribute
            }
    }

@router.get("/checklist/{checklist_id}", response_model=Dict)
def get_share_link(
    checklist_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the shareable link for a checklist if it exists"""
    shared = shared_crud.get_shared_link(db, checklist_id, current_user.id)
    if not shared:
        raise HTTPException(status_code=404, detail="Shared link not found")
    
    # Get base URL for the frontend
    base_url = str(request.base_url).rstrip("/")
    shareable_url = f"{base_url}/shared/{shared.share_token}"
    
    return {
        "id": shared.id,
        "checklist_id": shared.checklist_id,
        "share_token": shared.share_token,
        "shareable_url": shareable_url,
        "created_at": shared.created_at
    }

@router.delete("/checklist/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_share_link(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke a shareable link for a checklist"""
    success = shared_crud.revoke_shared_link(db, checklist_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Shared link not found or already revoked")
    return {"status": "success"}

@router.get("/{token}", response_model=ChecklistWithItems)
def view_shared_checklist(
    token: str,
    db: Session = Depends(get_db)
):
    """View a shared checklist using a token (no authentication required)"""
    checklist = shared_crud.get_checklist_by_token(db, token)
    if not checklist:
        raise HTTPException(status_code=404, detail="Shared checklist not found or link revoked")
    return checklist

@router.post("/{token}/items", response_model=ChecklistWithItems)
def add_item_to_shared_checklist(
    token: str,
    item: ChecklistItemCreate,
    db: Session = Depends(get_db)
):
    """Add an item to a shared checklist (no authentication required)"""
    checklist = shared_crud.get_checklist_by_token(db, token)
    if not checklist:
        raise HTTPException(status_code=404, detail="Shared checklist not found or link revoked")
    
    # Add the item to the checklist
    checklist_crud.add_checklist_item(db, checklist.id, checklist.user_id, item)
    
    # Get the updated checklist
    return checklist
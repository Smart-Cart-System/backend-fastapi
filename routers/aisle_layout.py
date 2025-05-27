from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from database import get_db
from schemas.aisle_layout import (
    AislePositionCreate, AislePosition, AisleConnectionCreate, 
    AisleMap, NavigationRequest, NavigationResponse
)
from crud import aisle_layout
from core.security import get_current_user
from models.user import User
from services.navigation_service import find_path_to_promotion

router = APIRouter(
    prefix="/layout",
    tags=["store-layout"]
)

@router.post("/position", response_model=AislePosition)
def create_aisle_position(
    position: AislePositionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update an aisle position in the store map"""
    return aisle_layout.create_aisle_position(db, position)

@router.post("/connection", status_code=status.HTTP_201_CREATED)
def create_aisle_connection(
    connection: AisleConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a connection between two aisles (bidirectional)"""
    success = aisle_layout.create_aisle_connection(
        db, connection.aisle_id, connection.connected_aisle_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="One or both aisles not found")
    
    return {"status": "success"}

@router.get("/map", response_model=AisleMap)
def get_store_map(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the entire store map with aisle positions and connections"""
    positions = aisle_layout.get_all_aisle_positions(db)
    connections = aisle_layout.get_all_aisle_connections(db)
    
    return AisleMap(
        positions=positions,
        connections=connections
    )

@router.post("/navigate", response_model=NavigationResponse)
def navigate_to_promotion(
    request: NavigationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get optimal navigation path to a promotion from current location"""
    path = find_path_to_promotion(db, request.session_id, request.target_promotion_id)
    
    if not path:
        raise HTTPException(
            status_code=404, 
            detail="Could not create navigation path. Check that session has a location and promotion exists."
        )
    
    return path
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from schemas.session_location import SessionLocation, SessionLocationCreate, SessionLocationUpdate
from crud import session_location as location_crud
from core.security import get_current_user, verify_pi_api_key
from models.user import User
from services.websocket_service import notify_clients  # Import the websocket service

router = APIRouter(
    prefix="/session-location",
    tags=["session_location"]
)

@router.post("/", response_model=SessionLocation, status_code=status.HTTP_201_CREATED)
def create_session_location(
    location: SessionLocationCreate,
    db: Session = Depends(get_db),
    pi_authenticated: bool = Depends(verify_pi_api_key)
):
    """Create a new session location entry (called by raspberry pi)"""
    db_location = location_crud.create_session_location(db, location)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Session not found or not active")
    return db_location

@router.put("/{session_id}", response_model=SessionLocation)
def update_session_location(
    session_id: int,
    location_update: SessionLocationUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    pi_authenticated: bool = Depends(verify_pi_api_key)
):
    """Update session location (called by raspberry pi)"""
    # Get previous location to check if aisle changed
    previous_location = location_crud.get_latest_session_location(db, session_id)
    previous_aisle_id = previous_location.aisle_id if previous_location else None
    
    # Update location
    db_location = location_crud.update_session_location(db, session_id, location_update)
    
    # If aisle changed, notify via websocket that promotions need updating
    if previous_aisle_id != location_update.aisle_id:
        background_tasks.add_task(
            notify_clients,
            session_id,
            "promotions-updated",
            location_update.aisle_id  # Using the aisle_id as the data (uses barcode parameter)
        )
    
    return db_location

@router.get("/{session_id}", response_model=SessionLocation)
def get_latest_location(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get latest location for a session"""
    location = location_crud.get_latest_session_location(db, session_id)
    if location is None:
        raise HTTPException(status_code=404, detail="No location found for this session")
    return location
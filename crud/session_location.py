from sqlalchemy.orm import Session
from models.session_location import SessionLocation
from models.customer_session import CustomerSession
from schemas.session_location import SessionLocationCreate, SessionLocationUpdate
from datetime import datetime

def create_session_location(db: Session, location: SessionLocationCreate):
    # Check if session is active
    session = db.query(CustomerSession).filter(
        CustomerSession.session_id == location.session_id,
        CustomerSession.is_active == True
    ).first()
    
    if not session:
        return None
    
    # Create new location entry
    db_location = SessionLocation(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def update_session_location(db: Session, session_id: int, location_update: SessionLocationUpdate):
    # Find the latest location for this session
    latest_location = db.query(SessionLocation).filter(
        SessionLocation.session_id == session_id
    ).order_by(SessionLocation.created_at.desc()).first()
    
    if latest_location:
        # If it's the same aisle, just update timestamp
        if latest_location.aisle_id == location_update.aisle_id:
            latest_location.updated_at = datetime.now()
            db.commit()
            return latest_location
    
    # Create new location entry
    db_location = SessionLocation(
        session_id=session_id,
        aisle_id=location_update.aisle_id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_latest_session_location(db: Session, session_id: int):
    return db.query(SessionLocation).filter(
        SessionLocation.session_id == session_id
    ).order_by(SessionLocation.created_at.desc()).first()
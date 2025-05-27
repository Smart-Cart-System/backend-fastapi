from sqlalchemy.orm import Session
from models.aisle_layout import AislePosition
from models.aisle import Aisle
from models.promotion import PromotionData
from models.session_location import SessionLocation
from schemas.aisle_layout import AislePositionCreate
import datetime

def create_aisle_position(db: Session, position: AislePositionCreate):
    """Create or update an aisle position"""
    # Check if position already exists for this aisle
    existing = db.query(AislePosition).filter(
        AislePosition.aisle_id == position.aisle_id
    ).first()
    
    if existing:
        # Update existing position
        existing.x = position.x
        existing.y = position.y
        existing.is_walkable = position.is_walkable
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new position
    db_position = AislePosition(**position.dict())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

def create_aisle_connection(db: Session, aisle_id: int, connected_aisle_id: int):
    """Create a bidirectional connection between aisles"""
    # Get the aisles
    aisle = db.query(Aisle).filter(Aisle.id == aisle_id).first()
    connected_aisle = db.query(Aisle).filter(Aisle.id == connected_aisle_id).first()
    
    if not aisle or not connected_aisle:
        return False
    
    # Create bidirectional connection
    if connected_aisle not in aisle.connected_to:
        aisle.connected_to.append(connected_aisle)
    
    if aisle not in connected_aisle.connected_to:
        connected_aisle.connected_to.append(aisle)
    
    db.commit()
    return True

def get_aisle_position(db: Session, aisle_id: int):
    """Get position for an aisle"""
    return db.query(AislePosition).filter(AislePosition.aisle_id == aisle_id).first()

def get_all_aisle_positions(db: Session):
    """Get all aisle positions"""
    return db.query(AislePosition).all()

def get_all_aisle_connections(db: Session):
    """Get all aisle connections as pairs of IDs"""
    # This is a more complex query working with the association table
    connections = []
    aisles = db.query(Aisle).all()
    
    for aisle in aisles:
        for connected in aisle.connected_to:
            connections.append([aisle.id, connected.id])
    
    return connections

def get_aisle_promotions_count(db: Session, aisle_id: int):
    """Count active promotions for an aisle"""
    today = datetime.date.today()
    
    count = db.query(PromotionData).filter(
        PromotionData.aisle_id == aisle_id,
        PromotionData.promotion_starting_date <= today,
        PromotionData.promotion_ending_date >= today
    ).count()
    
    return count

def get_last_session_location(db: Session, session_id: int):
    """Get the last aisle ID visited by a session"""
    location = db.query(SessionLocation).filter(
        SessionLocation.session_id == session_id
    ).order_by(SessionLocation.created_at.desc()).first()
    
    return location.aisle_id if location else None
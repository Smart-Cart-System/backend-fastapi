from sqlalchemy.orm import Session
from models.aisle import Aisle
from schemas.aisle import AisleCreate

def create_aisle(db: Session, aisle: AisleCreate):
    db_aisle = Aisle(**aisle.dict())
    db.add(db_aisle)
    db.commit()
    db.refresh(db_aisle)
    return db_aisle

def get_aisle(db: Session, aisle_id: int):
    return db.query(Aisle).filter(Aisle.id == aisle_id).first()

def get_aisles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Aisle).offset(skip).limit(limit).all()
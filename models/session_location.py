from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class SessionLocation(Base):
    __tablename__ = "session_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("customer_session.session_id"))
    aisle_id = Column(Integer, ForeignKey("aisles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("CustomerSession", back_populates="locations")
    aisle = relationship("Aisle", back_populates="session_locations")
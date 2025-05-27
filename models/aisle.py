from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Aisle(Base):
    __tablename__ = "aisles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    
    # Relationships
    promotions = relationship("PromotionData", back_populates="aisle")
    session_locations = relationship("SessionLocation", back_populates="aisle")
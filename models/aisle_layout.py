from sqlalchemy import Column, Integer, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from database import Base

# Association table for aisle connections
aisle_connections = Table(
    'aisle_connections',
    Base.metadata,
    Column('aisle_id', Integer, ForeignKey('aisles.id'), primary_key=True),
    Column('connected_aisle_id', Integer, ForeignKey('aisles.id'), primary_key=True)
)

class AislePosition(Base):
    __tablename__ = "aisle_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    aisle_id = Column(Integer, ForeignKey("aisles.id", ondelete="CASCADE"), unique=True)
    x = Column(Integer, nullable=False) 
    y = Column(Integer, nullable=False)
    is_walkable = Column(Boolean, default=True)
    
    # Relationships
    aisle = relationship("Aisle", back_populates="position")

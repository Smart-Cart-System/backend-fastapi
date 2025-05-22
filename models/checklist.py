from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Checklist(Base):
    __tablename__ = "checklists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User")
    items = relationship("ChecklistItem", back_populates="checklist", cascade="all, delete-orphan")

class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    checked = Column(Boolean, default=False)
    checklist_id = Column(Integer, ForeignKey("checklists.id"))
    
    # Relationships
    checklist = relationship("Checklist", back_populates="items")
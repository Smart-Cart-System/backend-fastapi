from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import secrets

class SharedChecklist(Base):
    __tablename__ = "shared_checklists"
    
    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("checklists.id", ondelete="CASCADE"))
    share_token = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    checklist = relationship("Checklist")
    
    @classmethod
    def generate_token(cls):
        """Generate a secure random token for sharing"""
        return secrets.token_urlsafe(32)
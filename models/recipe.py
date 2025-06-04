from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("customer_session.session_id"), nullable=False)
    title = Column(String(255), nullable=False)
    title_ar = Column(String(255), nullable=True)  # Arabic title
    ingredients = Column(Text, nullable=False)  # JSON string of ingredients
    ingredients_ar = Column(Text, nullable=True)  # JSON string of Arabic ingredients
    instructions = Column(Text, nullable=False)
    instructions_ar = Column(Text, nullable=True)  # Arabic instructions
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)  # Arabic description
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship with session
    session = relationship("CustomerSession", back_populates="recipes")
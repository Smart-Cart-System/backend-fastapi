from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class SatisfactionLevel(str, enum.Enum):
    SAD = "sad"
    NEUTRAL = "neutral"
    HAPPY = "happy"

# Association table for feedback items
feedback_items = Table(
    'feedback_items',
    Base.metadata,
    Column('feedback_id', Integer, ForeignKey('feedback.id'), primary_key=True),
    Column('feedback_item_id', Integer, ForeignKey('feedback_item.id'), primary_key=True)
)

class FeedbackItem(Base):
    __tablename__ = "feedback_item"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    
    
    feedbacks = relationship(
        "Feedback", 
        secondary=feedback_items,
        back_populates="selected_items"
    )

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("customer_session.session_id"), nullable=False)
    satisfaction = Column(Enum(SatisfactionLevel), nullable=False)
    additional_comments = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    session = relationship("CustomerSession", back_populates="feedback")
    selected_items = relationship(
        "FeedbackItem",
        secondary=feedback_items,
        back_populates="feedbacks"
    )
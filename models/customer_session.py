from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class CustomerSession(Base):
    __tablename__ = "customer_session"
    
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cart_id = Column(Integer, ForeignKey("carts.cart_id"))
    created_at = Column(String(255), default=func.now())
    is_active = Column(Boolean, default=True)
    
    user = relationship("User")
    cart = relationship("Cart")
    
    # Fix: Properly configure relationship for composite primary key
    items = relationship(
    "CartItem", 
    back_populates="session", 
    lazy="select",  # Change from "joined" to "select"
    primaryjoin="CustomerSession.session_id == CartItem.session_id",
    foreign_keys="CartItem.session_id",
    viewonly=True  # Add this parameter
)

    # Add to existing model
    locations = relationship("SessionLocation", back_populates="session")
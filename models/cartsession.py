from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class CartSession(Base):
    __tablename__ = "cartsession"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, index=True)  # Changed from String to Integer
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer)  # Changed from String to Integer
    quantity = Column(Integer, default=1)
    created_at = Column(String(255), default=func.now())
    
    user = relationship("User")
    product = relationship("ProductionData", foreign_keys=[item_id], 
                          primaryjoin="CartSession.item_id == ProductionData.item_no_")
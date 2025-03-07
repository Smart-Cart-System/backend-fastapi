from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class CartItem(Base):
    __tablename__ = "cart_items"
    
    session_id = Column(Integer, ForeignKey("customer_session.session_id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("products_data.item_no_"), primary_key=True)
    quantity = Column(Integer, default=1)
    saved_weight = Column(Float, nullable=True)
    
    session = relationship("CustomerSession", back_populates="items")
    product = relationship("ProductionData")
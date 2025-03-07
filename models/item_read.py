from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class ItemRead(Base):
    __tablename__ = "item_read"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("customer_session.session_id"))
    item_no_ = Column(Integer, ForeignKey("products_data.item_no_"))
    read_at = Column(DateTime, default=func.now())
    
    session = relationship("CustomerSession")
    product = relationship("ProductionData")
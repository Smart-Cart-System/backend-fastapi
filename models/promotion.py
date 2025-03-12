from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PromotionData(Base):
    __tablename__ = "promotions_data"
    
    index = Column(Integer, primary_key=True)
    item_no_ = Column(Integer, ForeignKey("products_data.item_no_"))
    description_ar = Column(String(255))
    item_category_code = Column(String(255))
    promotion_description = Column(String(255))
    discount_amount = Column(Float)
    promotion_starting_date = Column(Date)
    promotion_ending_date = Column(Date)
    
    # Relationship to product
    product = relationship("ProductionData")
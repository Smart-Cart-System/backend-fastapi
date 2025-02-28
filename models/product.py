from sqlalchemy import Column, Integer, String, Float
from database import Base

class ProductionData(Base):
    __tablename__ = "production_data"
    
    index = Column(String(255), primary_key=True)
    location_code = Column(String(255))
    item_no_ = Column(String(255))
    description = Column(String(255))
    description_2 = Column(String(255))
    product_size = Column(String(255))
    barcode = Column(String(255), index=True)
    unit_price = Column(String(255))
    stock = Column(String(255))
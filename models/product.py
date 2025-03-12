from sqlalchemy import Column, Integer, String, Float, BigInteger
from database import Base

class ProductionData(Base):
    __tablename__ = "products_data"
    
    item_no_ = Column(Integer, primary_key=True)
    location_code = Column(String(255))
    description = Column(String(255))
    description_ar = Column(String(255))
    product_size = Column(String(255))
    barcode = Column(BigInteger, index=True)
    unit_price = Column(Float)
    stock = Column(Integer)
    image_url = Column(String(255), nullable=True)
from sqlalchemy import Column, Integer, String, Enum
from database import Base
from sqlalchemy.orm import relationship


class Cart(Base):
    __tablename__ = "carts"
    
    cart_id = Column(Integer, primary_key=True)
    status = Column(Enum('available', 'in use', 'maintenance', 'battery low', 
                       name='cart_status_enum'), default='available')
    qrcode_token = Column(String(255), unique=True, index=True)
    battery_level = Column(Integer, default=100)
    

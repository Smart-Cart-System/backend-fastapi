from pydantic import BaseModel
from typing import Optional

class CartBase(BaseModel):
    status: str
    qrcode_token: str
    battery_level: int = 100

class CartCreate(CartBase):
    pass

class Cart(CartBase):
    cart_id: int
    
    class Config:
        from_attributes = True
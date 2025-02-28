from pydantic import BaseModel
from typing import Optional

class CartItemBase(BaseModel):
    cart_id: str
    user_id: int
    item_id: str
    quantity: Optional[int] = 1

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    
    class Config:
        from_attributes = True

class BarcodeRequest(BaseModel):
    barcode: str
    cart_id: str
    user_id: int
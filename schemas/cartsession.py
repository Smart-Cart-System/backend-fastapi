from pydantic import BaseModel
from typing import Optional

class CartItemBase(BaseModel):
    cart_id: int  # Changed from str to int
    user_id: int
    item_id: int  # Changed from str to int
    quantity: Optional[int] = 1

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    
    class Config:
        from_attributes = True

class BarcodeRequest(BaseModel):
    barcode: int  
    cart_id: int  
    user_id: int
from pydantic import BaseModel
from typing import Optional, Union, Dict, Any, List

class CartItemBase(BaseModel):
    session_id: int
    item_id: int
    quantity: int = 1
    saved_weight: Optional[float] = None

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    class Config:
        from_attributes = True

class CartItemRequest(BaseModel):
    sessionID: int
    barcode: int
    weight: Optional[float] = None  # Add weight for item weighing

class CartItemResponse(BaseModel):
    session_id: int
    item_id: int
    quantity: int
    saved_weight: Optional[float] = None
    product: Optional[Dict[str, Any]] = None  # Optional product details
    
    class Config:
        from_attributes = True

class CartItemListResponse(BaseModel):
    items: List[CartItemResponse]
    total_price: float
    item_count: int

class RemoveResponse(BaseModel):
    success: bool
    message: str
    item: Optional[CartItemResponse] = None
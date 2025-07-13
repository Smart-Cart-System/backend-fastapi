from pydantic import BaseModel
from typing import Optional  # Add this import

class ItemReadRequest(BaseModel):
    sessionID: int
    barcode: int
    
class ItemReadResponse(BaseModel):
    item_no_: int
    description: str
    description_ar: str
    unit_price: float
    product_size: str
    barcode: int 
    image_url: Optional[str] = None  # Change this line to use Optional
    
    class Config:
        from_attributes = True
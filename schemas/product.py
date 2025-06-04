from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    item_no_: int
    description: str
    description_ar: Optional[str] = None
    unit_price: float
    barcode: int
    image_url: Optional[str] = None
    product_size: Optional[str] = None
    
    class Config:
        from_attributes = True

class SuggestedProductsResponse(BaseModel):
    products: List[ProductBase]
    count: int
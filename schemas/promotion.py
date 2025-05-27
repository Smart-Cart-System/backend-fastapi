from pydantic import BaseModel
from typing import Optional
from datetime import date

class PromotionResponse(BaseModel):
    # Promotion data
    index: int
    item_no_: int
    promotion_description: str
    discount_amount: float
    promotion_starting_date: date
    promotion_ending_date: date
    
    # Product data
    product_description: str
    product_description_ar: str
    unit_price: float
    discounted_price: float
    discount_percentage: float
    image_url: Optional[str] = None
    
    # Aisle data
    aisle_id: Optional[int] = None
    aisle_name: Optional[str] = None
    
    class Config:
        from_attributes = True
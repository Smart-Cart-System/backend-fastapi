from pydantic import BaseModel

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
    image_url: str = None 
    
    class Config:
        from_attributes = True
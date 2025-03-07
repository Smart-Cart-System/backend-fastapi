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
    
    class Config:
        from_attributes = True
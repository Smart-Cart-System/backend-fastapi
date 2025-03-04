from pydantic import BaseModel

class ProductBase(BaseModel):
    barcode: int  

class Product(ProductBase):
    location_code: str
    item_no_: int
    description: str
    description_ar: str  
    product_size: str
    unit_price: float   
    stock: int           
    
    class Config:
        from_attributes = True
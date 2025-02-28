from pydantic import BaseModel

class ProductBase(BaseModel):
    barcode: str

class Product(ProductBase):
    index: str
    location_code: str
    item_no_: str
    description: str
    description_2: str
    product_size: str
    unit_price: str
    stock: str
    
    class Config:
        from_attributes = True
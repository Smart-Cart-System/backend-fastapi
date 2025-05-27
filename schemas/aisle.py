from pydantic import BaseModel
from typing import Optional

class AisleBase(BaseModel):
    name: str
    category: Optional[str] = None

class AisleCreate(AisleBase):
    pass

class Aisle(AisleBase):
    id: int
    
    class Config:
        from_attributes = True
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionLocationBase(BaseModel):
    session_id: int
    aisle_id: int

class SessionLocationCreate(SessionLocationBase):
    pass

class SessionLocation(SessionLocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SessionLocationUpdate(BaseModel):
    aisle_id: int
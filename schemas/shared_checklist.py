from pydantic import BaseModel
from datetime import datetime

class SharedChecklistBase(BaseModel):
    checklist_id: int

class SharedChecklistCreate(SharedChecklistBase):
    pass

class SharedChecklistResponse(SharedChecklistBase):
    id: int
    share_token: str
    created_at: datetime
    
    class Config:
        from_attributes = True
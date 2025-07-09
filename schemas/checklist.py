from pydantic import BaseModel
from typing import List, Optional

# ChecklistItem schemas
class ChecklistItemBase(BaseModel):
    text: str
    checked: bool = False

class ChecklistItemCreate(ChecklistItemBase):
    pass

class ChecklistItemUpdate(BaseModel):
    text: Optional[str] = None
    checked: Optional[bool] = None

class ChecklistItem(ChecklistItemBase):
    id: int
    checklist_id: int
    
    class Config:
        from_attributes = True

# Checklist schemas
class ChecklistBase(BaseModel):
    name: str
    is_pinned: Optional[bool] = False  

class ChecklistCreate(ChecklistBase):
    items: List[ChecklistItemCreate] = []

class ChecklistUpdate(BaseModel):
    name: Optional[str] = None
    is_pinned: Optional[bool] = None

class ChecklistWithItems(ChecklistBase):
    id: int
    user_id: int
    items: List[ChecklistItem] = []
    
    class Config:
        from_attributes = True

class Checklist(ChecklistBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True
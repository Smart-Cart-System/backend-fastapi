from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schemas.cart_item import CartItemListResponse

class SessionBase(BaseModel):
    user_id: int
    cart_id: int

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    session_id: int
    created_at: str
    is_active: bool = True
    
    class Config:
        from_attributes = True

# Request model for scanning QR code
class QRScanRequest(BaseModel):
    token: str

# Schema for finishing a session
class SessionUpdate(BaseModel):
    is_active: bool

class SessionDetailsResponse(CartItemListResponse):
    created_at: datetime

class RecentSessionsResponse(BaseModel):
    sessions: List[SessionDetailsResponse]
    class Config:
        from_attributes = True
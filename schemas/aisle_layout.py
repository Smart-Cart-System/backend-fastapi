from pydantic import BaseModel
from typing import List, Optional

class AislePositionBase(BaseModel):
    x: int
    y: int
    is_walkable: bool = True

class AislePositionCreate(AislePositionBase):
    aisle_id: int

class AislePosition(AislePositionBase):
    id: int
    aisle_id: int
    
    class Config:
        from_attributes = True

class AisleConnectionCreate(BaseModel):
    aisle_id: int
    connected_aisle_id: int

class AisleMap(BaseModel):
    positions: List[AislePosition]
    connections: List[List[int]]  # List of [aisle_id, connected_aisle_id] pairs

class NavigationRequest(BaseModel):
    session_id: int
    target_promotion_id: int

class NavigationStep(BaseModel):
    aisle_id: int
    name: str
    x: int
    y: int
    promotions_count: int
    
class NavigationResponse(BaseModel):
    path: List[NavigationStep]
    total_distance: int
    total_promotions: int
    target_promotion_id: int
    target_aisle_id: int
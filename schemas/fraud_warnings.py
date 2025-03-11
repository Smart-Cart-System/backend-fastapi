from pydantic import BaseModel
from enum import Enum

class WarningTypeEnum(str, Enum):
    WEIGHT_INCREASED = "weight increased"
    WEIGHT_DECREASED = "weight decreased"

class FraudWarningCreate(BaseModel):
    session_id: int
    type_of_warning: WarningTypeEnum

class FraudWarning(FraudWarningCreate):
    id: int
    
    class Config:
        from_attributes = True

class CartUpdateNotificationRequest(BaseModel):
    session_id: int
    barcode: int = 0  # Optional barcode parameter, default 0
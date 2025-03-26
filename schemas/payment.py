from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from enum import Enum

class Amount(BaseModel):
    amount: float
    currency: str

class Tag(BaseModel):
    id: int
    name: str

class PaymentRequest(BaseModel):
    name: str
    customer_name: str
    customer_email: EmailStr
    allow_recurring_payments: bool
    customer_mobile: str
    cc_email: EmailStr
    amount: Amount
    community_id: str
    payment_methods: List[str]
    vat_percentage: float
    expiry_date: str
    send_by_email: bool
    send_by_sms: bool
    redirect_url: str
    callback_url: str

class PaymentResponse(BaseModel):
    success: bool
    merchant_id: str
    payment_id: str
    payment_url: str
    message: str
    total_amount: Optional[float] = None
    transaction_id: Optional[str] = None
    transaction_status: Optional[str] = None
    total_amount_piasters: Optional[float] = None

    class Config:
        from_attributes = True

class PaymentCallbackResponse(BaseModel):
    message: str
    member_id: Optional[str] = None
    payment_id: str
    merchant_id: Optional[str] = None
    total_amount: float
    transaction_id: str
    transaction_status: str
    total_amount_piasters: float
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentAPIResponseStatus(BaseModel):
    code: int
    message: str
    errors: List[Any]

class PaymentAPIResponseData(BaseModel):
    success: bool
    merchant_id: str
    payment_id: str
    payment_url: str
    message: str

class PaymentAPIResponse(BaseModel):
    status: PaymentAPIResponseStatus
    data: PaymentAPIResponseData
    count: Optional[int] = None
    next: Optional[str] = None
    previous: Optional[str] = None

    class Config:
        from_attributes = True



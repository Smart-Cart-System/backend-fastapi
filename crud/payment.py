import httpx
from fastapi import HTTPException
from schemas.payment import PaymentRequest, PaymentAPIResponse
import os
from sqlalchemy.orm import Session
from models.payment import Payment, PaymentStatusEnum
import logging

logger = logging.getLogger(__name__)

async def create_online_payment(payment_data: PaymentRequest) -> PaymentAPIResponse:
    api_url = "https://staging.xpay.app/api/orders/create-direct-order/"
    headers = {
        "x-api-key": os.getenv("XPAY_API_KEY"),
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, headers=headers, json=payment_data.model_dump())
        if response.status_code not in {200, 201}:
            logger.error(f"Failed to create online payment: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
        response_data = response.json()
        logger.info(f"Payment API response: {response_data}")
        return PaymentAPIResponse(**response_data)

def create_payment_record(db: Session, payment_data: PaymentRequest, online_payment_response: PaymentAPIResponse, session_id: int, total_price: float):
    # Check if a payment record already exists for this session
    existing_payment = db.query(Payment).filter(Payment.session_id == session_id).first()
    if existing_payment:
        return existing_payment
    # Create a new payment record
    try:
        new_payment = Payment(
            payment_id=online_payment_response.data.payment_id,
            payment_url=online_payment_response.data.payment_url,
            total_amount=total_price,
            transaction_status=PaymentStatusEnum.pending,
            session_id=session_id,
        )
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        return new_payment
    except Exception as e:
        logger.error(f"Error creating payment record: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create payment record")

def get_payment_by_session_id(db: Session, session_id: int) -> Payment:
    return db.query(Payment).filter(Payment.session_id == session_id).first()
def get_payment_by_payment_id(db: Session, payment_id: str) -> Payment:
    return db.query(Payment).filter(Payment.payment_id == payment_id).first()
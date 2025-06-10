from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from schemas.payment import PaymentRequest, Amount, PaymentAPIResponse, PaymentCallbackResponse
from crud.payment import create_online_payment, create_payment_record, get_payment_by_session_id, get_payment_by_payment_id
from crud.customer_session import get_session, finish_session
from crud.cart_item import get_cart_items_by_session
from crud.user import get_user_by_id
from database import get_db
from models.payment import PaymentStatusEnum
from dotenv import load_dotenv
from services.websocket_service import notify_clients, notify_hardware_clients
import os
import json
from services.logging_service import LoggingService, get_logging_service, SessionEventType


# Load environment variables from .env file
load_dotenv()

router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)


@router.post("/create-payment/{session_id}")
async def create_payment(session_id: int, 
                         db: Session = Depends(get_db),
                         logging_service: LoggingService = Depends(get_logging_service)):
    # Fetch session details
    session = get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Fetch cart items and calculate total amount
    cart_items, total_price = get_cart_items_by_session(db, session_id)
    if not cart_items:
        raise HTTPException(status_code=404, detail="No items found in the cart")
    user = get_user_by_id(db, session.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fill in the necessary payment data
    payment_data = PaymentRequest(
        name=f"Payment for session {session_id}",
        customer_name=user.username + " " + user.username,
        customer_email=user.email,
        allow_recurring_payments=False,
        customer_mobile=user.mobile_number,
        cc_email=user.email,
        amount=Amount(amount=total_price, currency="EGP"),
        community_id="vBMeRBW",
        payment_methods=[
            "CARD",
            "FAWRY"
        ],
        vat_percentage=5.0,
        expiry_date="2025-5-31",
        send_by_email=False,
        send_by_sms=False,
        redirect_url="https://api.duckuycart.me",
        callback_url="https://api.duckycart.me/payment/webhook"
    )

    # Call the function to create an online payment and await its response
    try:
        online_payment_response = await create_online_payment(payment_data)
    except Exception as e:
        logging_service.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            severity="HIGH",
            endpoint="/payment/create-payment",
            additional_data={"session_id": session_id}
        )
        raise HTTPException(status_code=500, detail="Failed to create online payment")
    
    # Create a payment record in the database
    try:
        payment_id = create_payment_record(db, payment_data, online_payment_response, session_id, total_price)
    except Exception as e:
        logging_service.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            severity="HIGH",
            endpoint="/payment/create-payment",
            additional_data={"session_id": session_id}
        )
        raise HTTPException(status_code=500, detail="Failed to create payment record")

    # Log the successful creation of the payment
    logging_service.log_session_activity(
        event_type=SessionEventType.PAYMENT_CREATED,
        user_id=user.id,
        session_id=session_id,
        additional_data={
            "payment_id": payment_id,
            "total_amount": total_price,
            "payment_url": online_payment_response.data.payment_url
        }
    )
    await notify_hardware_clients(
        cart_id=session.cart_id,
        command="payment_created",
        session_id=session_id
    )
    # Notify clients about the new payment
    a = await notify_clients(session_id, "Payment created", 0)
    print(f"Notification sent: {a}")
    # Return a success response

    return HTTPException(status_code=201, detail="Payment created successfully")


@router.get("/get-payment/{session_id}")
def get_payment(session_id: int, db: Session = Depends(get_db)):
    payment = get_payment_by_session_id(db, session_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"payment_url": payment.payment_url}


@router.post("/webhook", response_model=PaymentCallbackResponse)
async def payment_webhook(payload: PaymentCallbackResponse,
                           db: Session = Depends(get_db),
                           logging_service: LoggingService = Depends(get_logging_service)):
    # Check if the transaction ID exists in the payments table
    payment = get_payment_by_payment_id(db, payload.payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction ID not found")

    # Log the received webhook payload
    # Process payment based on response
    try:
        status = payload.transaction_status.lower()
        payment.callback_data = json.dumps(payload.model_dump())

        if status == "successful":
            payment.transaction_status = PaymentStatusEnum.successful
            payment.transaction_id = payload.transaction_id
            await notify_clients(payment.session_id, "Payment successful", 0)
            finish_session(db, payment.session_id)
        elif status == "failed":
            if payment.retry_attempts < 3:
                payment.transaction_status = PaymentStatusEnum.failed
                payment.retry_attempts += 1
                await notify_clients(payment.session_id, "Payment failed, retrying", 0)
            else:
                payment.transaction_status = PaymentStatusEnum.failed
                await notify_clients(payment.session_id, "Payment failed", 0)
        else:
            logging_service.log_warning(
                message=f"Unknown transaction status: {status}",
                user_id=None,
                session_id=payment.session_id
            )
        payment.updated_at = payload.updated_at or payment.updated_at
        db.commit()
        db.refresh(payment)

    except Exception as e:
        logging_service.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            severity="HIGH",
            endpoint="/payment/webhook",
            additional_data={"payment_id": payment.payment_id}
        )
        raise HTTPException(status_code=500, detail="Internal server error")

    # Convert the Payment object to a PaymentCallbackResponse model
    payment_response = PaymentCallbackResponse(
        message=payment.callback_data,
        member_id=None,
        payment_id=payment.payment_id,
        merchant_id=payload.merchant_id,
        total_amount=payment.total_amount,
        transaction_id=payment.transaction_id,
        transaction_status=payment.transaction_status,
        total_amount_piasters=payment.total_amount * 100,  # Assuming 1 EGP = 100 piasters
        updated_at=payment.updated_at
    )

    return payment_response
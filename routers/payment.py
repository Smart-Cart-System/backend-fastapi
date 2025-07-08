from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from schemas.payment import PaymentRequest, Amount, PaymentAPIResponse, PaymentCallbackResponse
from crud.payment import create_online_payment, create_payment_record, get_payment_by_session_id, get_payment_by_payment_id
from crud.customer_session import get_session, finish_session
from crud.cart_item import get_cart_items_by_session, validate_session, get_total_price_by_session
from crud.user import get_user_by_id
from database import get_db
from models.payment import PaymentStatusEnum
from models.session_location import SessionLocation
from dotenv import load_dotenv
from services.websocket_service import notify_clients, notify_hardware_clients
import os
from crud.session_location import get_latest_session_location
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
                         db: Session = Depends(get_db)):
    # Fetch session details
    logging_service = get_logging_service(db)
    session = validate_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    # last_location = get_latest_session_location(db, session_id)
    # if last_location.aisle_id is not 16:
    #     raise HTTPException(status_code=404, detail="You didnt finish your shopping yet, please go to the checkout aisle to pay")
    # Fetch cart items and calculate total amount
    total_price = get_total_price_by_session(db, session_id)
    total_price = float(total_price) if total_price else 0.0
    if total_price == 0:
        raise HTTPException(status_code=404, detail="No items found in the cart")
    user = get_user_by_id(db, session.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    first_name, last_name = user.full_name.split(" ", 1) if user.full_name else (user.full_name, user.full_name)
    # Fill in the payment data
    payment_data = PaymentRequest(
        name=f"Payment for session {session_id}",
        customer_name=first_name + " " + last_name,
        customer_email=user.email,
        allow_recurring_payments=False,
        customer_mobile=user.mobile_number,
        cc_email="duckycart@gmail.com",
        amount=Amount(amount=total_price, currency="EGP"),
        community_id="vBMeRBW",
        payment_methods=[
            "CARD",
            "FAWRY"
        ],
        vat_percentage=5.0,
        expiry_date="2025-7-31",
        send_by_email=False,
        send_by_sms=False,
        redirect_url="https://api.duckuycart.me/payment/payment-success",
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
        raise HTTPException(status_code=500, detail="Failed to create online payment api problem")
    
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
        raise HTTPException(status_code=500, detail="Failed to create payment record database problem")

    # Log the successful creation of the payment
    logging_service.log_session_activity(
        event_type=SessionEventType.PAYMENT_CREATED,
        user_id=user.id,
        session_id=session_id,
        cart_id=session.cart_id,
        additional_data={
            "payment_id": payment_id.payment_id,
            "total_amount": total_price
        }
    )
    await notify_hardware_clients(
        cart_id=session.cart_id,
        command="payment_created",
        session_id=session_id
    )
    # Notify clients about the new payment
    await notify_clients(session_id, "Payment created", 0)
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
            await finish_session(db, payment.session_id)
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

@router.get("/payment-success")
def payment_success():
    #return simple html page with success message with true icon
    return """
    <html>
        <head>
            <title>Payment Success</title>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    background-color: #222222;
                }
                .success-icon {
                    width: 100px;
                    height: 100px;
                    background-color: #4CAF50;  /* Green background */
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 50px;
                    color: white;  /* White checkmark */
                }
                .message {
                    margin-top: 20px;
                    font-size: 24px;
                    color: white;  /* Also updated text color to be visible on dark background */
                }
            </style>
        </head>
        <body>
            <div class="success-icon">✔️</div>
            <div class="message">Payment Successful!</div>
        </body>
    </html>
    """

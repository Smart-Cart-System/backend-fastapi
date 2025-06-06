from fastapi import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.security import verify_pi_api_key
from database import get_db
from schemas.fraud_warnings import CartUpdateNotificationRequest, FraudWarningCreate, FraudWarning
from models.customer_session import CustomerSession
from crud import fraud_warnings
from typing import List
from services.websocket_service import notify_clients

router = APIRouter(
    prefix="/fraud-warnings",
    tags=["fraud warnings"]
)

@router.post("/", response_model=FraudWarning)
async def report_warning(warning: FraudWarningCreate, db: Session = Depends(get_db),pi_authenticated: bool = Depends(verify_pi_api_key) ):
    """Report a fraud warning from the Raspberry Pi"""
    # First validate that the session exists
    session = db.query(CustomerSession).filter(CustomerSession.session_id == warning.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session with ID {warning.session_id} not found")
    
    # If session exists, proceed with creating warning
    db_warning = fraud_warnings.create_warning(db, warning)
    
    await notify_clients(
        warning.session_id, 
        warning.type_of_warning,
        0
    )
    
    return db_warning

@router.get("/session/{session_id}", response_model=List[FraudWarning])
def get_session_warnings(session_id: int, db: Session = Depends(get_db)):
    """Get all warnings for a session"""
    return fraud_warnings.get_warnings_by_session(db, session_id)

@router.post("/notify-cart-update", status_code=status.HTTP_200_OK)
async def notify_cart_update(request: CartUpdateNotificationRequest,pi_authenticated: bool = Depends(verify_pi_api_key)):
    """
    Send a cart-update notification to the WebSocket client without changing the database
    """
    await notify_clients(
        request.session_id,
        "cart-updated",
        request.barcode
    )
    
    return {"message": "Notification sent successfully"}
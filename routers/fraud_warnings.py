from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.fraud_warnings import FraudWarningCreate, FraudWarning
from models.customer_session import CustomerSession
from crud import fraud_warnings
from typing import List
from routers.websocket import notify_clients

router = APIRouter(
    prefix="/fraud-warnings",
    tags=["fraud warnings"]
)

@router.post("/", response_model=FraudWarning)
async def report_warning(warning: FraudWarningCreate, db: Session = Depends(get_db)):
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
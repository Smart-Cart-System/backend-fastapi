from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.customer_session import CustomerSession
from schemas.customer_session import SessionCreate, Session, QRScanRequest
from crud import cart, customer_session
from core.security import get_current_user, verify_pi_api_key
from models.user import User
from fastapi.responses import StreamingResponse


router = APIRouter(
    prefix="/customer-session",
    tags=["customer_session"]
)



@router.get("/qr/{cart_id}")
def get_qr(cart_id: int, db: Session = Depends(get_db)):
    db_cart = cart.get_cart_by_id(db, cart_id)
    if not db_cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return StreamingResponse(customer_session.generate_qr(cart_id), media_type="image/png")

@router.post("/scan-qr", response_model=Session)
def scan_qr_code(scan_data: QRScanRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Process QR code scan and create a customer session"""
    try:
        cartid = customer_session.validate_qr_token(scan_data.token)
        if not cartid:
            raise HTTPException(status_code=401, detail="Invalid or expired QR code.")
        
        # Find the cart by ID (not by QR code anymore)
        db_cart = cart.get_cart_by_id(db, cart_id=cartid)
        if not db_cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Check if cart is available
        if db_cart.status != 'available':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Cart is not available (current status: {db_cart.status})"
            )
        
        # Create a session
        session = SessionCreate(user_id=scan_data.userID, cart_id=cartid)
        new_session = customer_session.create_session(db, session)
        
        return new_session
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid cart ID format"
        )

@router.get("/cart/{cart_id}", response_model=Session)
def get_session_by_cart(cart_id: int, db: Session = Depends(get_db), pi_authenticated: bool = Depends(verify_pi_api_key)):
    """Get the latest session for a specific cart"""
    # Use a simpler query that doesn't join with cart_items
    db_session = db.query(CustomerSession).filter(
        CustomerSession.cart_id == cart_id,
        CustomerSession.is_active == True
    ).order_by(CustomerSession.created_at.desc()).first()
    
    if db_session is None:
        raise HTTPException(status_code=404, detail="No active session found for this cart")
    return db_session

@router.get("/active/{user_id}", response_model=Session)
def get_active_session_for_user(user_id: int, db: Session = Depends(get_db)):
    """Get the active session for a specific user"""
    db_session = customer_session.get_active_session_by_user(db, user_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="No active session found for this user")
    return db_session

@router.post("/{session_id}/checkout", response_model=Session)
def checkout_session(session_id: int, db: Session = Depends(get_db)):
    """End a shopping session (checkout) and make the cart available again"""
    db_session = customer_session.finish_session(db, session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.get("/cart-status/{cart_id}")
def check_cart_status(cart_id: int, db: Session = Depends(get_db)):
    """Check if a cart has an active session"""
    try:
        # Check if cart exists first
        cart_status = cart.get_cart_by_id(db, cart_id)
        if not cart_status:
            raise HTTPException(status_code=404, detail=f"Cart with ID {cart_id} not found")
            
        # Then check for active session
        db_session = customer_session.get_active_session_by_cart(db, cart_id)
        
        return {
            "cart_id": cart_id,
            "status": cart_status.status,
            "has_active_session": db_session is not None,
            "session_id": db_session.session_id if db_session else None,
            "user_id": db_session.user_id if db_session else None
        }
    except Exception as e:
        # Log the error
        print(f"Error checking cart status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking cart status: {str(e)}")
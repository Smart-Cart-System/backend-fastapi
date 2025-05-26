import datetime
from sqlalchemy.orm import Session
from models.customer_session import CustomerSession
from models.cart import Cart
from schemas.customer_session import SessionCreate, SessionUpdate
from io import BytesIO
import qrcode
import jwt
from crud.cart import get_cart_by_id

def create_session(db: Session, session: SessionCreate):
    # First update cart status to 'in use'
    cart = db.query(Cart).filter(Cart.cart_id == session.cart_id).first()
    if cart:
        cart.status = 'in use'
    
    # Create new session
    db_session = CustomerSession(
        user_id=session.user_id,
        cart_id=session.cart_id,
        is_active=True
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: int):
    return db.query(CustomerSession).filter(CustomerSession.session_id == session_id).first()

def get_active_session_by_user(db: Session, user_id: int):
    return db.query(CustomerSession).filter(CustomerSession.user_id == user_id, 
                                           CustomerSession.is_active == True).first()

def get_active_session_by_cart(db: Session, cart_id: int):
    return db.query(CustomerSession).filter(CustomerSession.cart_id == cart_id, 
                                           CustomerSession.is_active == True).first()

def finish_session(db: Session, session_id: int):
    db_session = get_session(db, session_id)
    if db_session:
        # Update session status
        db_session.is_active = False
        
        # Update cart status back to available
        cart = db.query(Cart).filter(Cart.cart_id == db_session.cart_id).first()
        if cart:
            cart.status = 'available'
        
        db.commit()
        db.refresh(db_session)
    return db_session


SECRET_KEY = "DuckyCart_2025_V1"
EXPIRATION_MINUTES = 1

def generate_qr(data: str) -> BytesIO:
    """Generates a QR code Token and returns it"""
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=EXPIRATION_MINUTES)
    payload = {
        "cartid": data,
        "exp": expires_at
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def validate_qr_token(token: str):
    """Validate the QR token and extract cart ID."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["cartid"]  # Returns cart ID if valid
    except jwt.ExpiredSignatureError:
        return None  # QR Code expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

async def create_session_from_qr(db: Session, cart_id: int, user_id: int, token: str):
    """Create a session from QR code with validation"""
    # Get cart and validate availability (returns tuple with result and error)
    db_cart = get_cart_by_id(db, cart_id=cart_id)
    if not db_cart:
        return None, "Cart not found"
    
    if db_cart.status != 'available':
        return None, f"Cart is not available (current status: {db_cart.status})"
    
    # Create session
    session = SessionCreate(user_id=user_id, cart_id=cart_id)
    new_session = create_session(db, session)
    
    # Return session (controller handles notifications)
    return new_session, None
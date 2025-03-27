import datetime
from sqlalchemy.orm import Session
from models.customer_session import CustomerSession
from models.cart import Cart
from schemas.customer_session import SessionCreate, SessionUpdate
from io import BytesIO
import qrcode
import jwt

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
    """Generates a QR code and returns it as an in-memory binary stream."""
    qr = qrcode.QRCode(
        version=None,  # Automatically adjusts size
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=4,
    )
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=EXPIRATION_MINUTES)
    payload = {
        "cartid": data,
        "exp": expires_at
    }
    qr.add_data(jwt.encode(payload, SECRET_KEY, algorithm="HS256"))
    qr.make(fit=True)
    img_bytes = BytesIO()
    qr.make_image(fill_color="#007058", back_color="#FFFFFF").save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

def validate_qr_token(token: str):
    """Validate the QR token and extract cart ID."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["cartid"]  # Returns cart ID if valid
    except jwt.ExpiredSignatureError:
        return None  # QR Code expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
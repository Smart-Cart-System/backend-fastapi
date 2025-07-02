import datetime
from sqlalchemy.orm import Session
from models.customer_session import CustomerSession
from models.cart import Cart
from schemas.customer_session import SessionCreate, SessionUpdate
from io import BytesIO
import qrcode
import jwt
from schemas.cart_item import CartItemResponse, CartItemListResponse
from crud.cart import get_cart_by_id
from crud.cart_item import get_cart_items_by_session
from services.logging_service import LoggingService, SessionEventType
from datetime import datetime, timezone, timedelta
from services.websocket_service import notify_hardware_clients
from services.logging_service import SecurityEventType, LoggingService, get_logging_service 
from core.config import settings
from models.session_location import SessionLocation
from services.email_service import send_cart_receipt_email
from models.user import User

def create_session(db: Session, session: SessionCreate):
    logging_service = get_logging_service(db)
    
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
    
    # Create default location entry for aisle 1
    default_location = SessionLocation(
        session_id=db_session.session_id,
        aisle_id=1  # Set default aisle to 1
    )
    
    # Add the default location
    db.add(default_location)
    db.commit()
    
    # Log session start
    logging_service.log_session_activity(
        event_type=SessionEventType.SESSION_START,
        session_id=db_session.session_id,
        user_id=session.user_id,
        cart_id=session.cart_id,
        additional_data={
            "cart_status": "in_use",
            "session_created": True
        }
    )
    
    return db_session

def get_session(db: Session, session_id: int):
    return db.query(CustomerSession).filter(CustomerSession.session_id == session_id).first()

def get_active_session_by_user(db: Session, user_id: int):
    return db.query(CustomerSession).filter(CustomerSession.user_id == user_id, 
                                           CustomerSession.is_active == True).first()

def get_active_session_by_cart(db: Session, cart_id: int):
    return db.query(CustomerSession).filter(CustomerSession.cart_id == cart_id, 
                                           CustomerSession.is_active == True).first()

async def finish_session(db: Session, session_id: int):
    logging_service = get_logging_service(db)
    session_start_time = datetime.now()
    
    # Get session details before finishing
    session = db.query(CustomerSession).filter(CustomerSession.session_id == session_id).first()
    if not session:
        return False
    
    # Calculate session duration if created_at is available
    duration_seconds = None
    if hasattr(session, 'created_at') and session.created_at:
        try:
            # Parse created_at string to datetime if it's a string
            if isinstance(session.created_at, str):
                created_at = datetime.fromisoformat(session.created_at)
            else:
                created_at = session.created_at
            duration_seconds = int((session_start_time - created_at).total_seconds())
        except:
            duration_seconds = None
    
    # Get final cart totals
    items, total_price = get_cart_items_by_session(db, session_id)
    item_count = len(items)
    
    # Update session status
    session.is_active = False
    
    # Update cart status back to 'available'
    if session.cart_id:
        cart = db.query(Cart).filter(Cart.cart_id == session.cart_id).first()
        if cart:
            cart.status = 'available'
    
    db.commit()
    
    # Log session end
    logging_service.log_session_activity(
        event_type=SessionEventType.SESSION_END,
        session_id=session_id,
        user_id=session.user_id,
        cart_id=session.cart_id,
        total_price=total_price,
        duration_seconds=duration_seconds,
        additional_data={
            "item_count": item_count,
            "cart_status": "available",
            "session_finished": True
        }
    )
    await notify_hardware_clients(
        cart_id=session.cart_id,
        command="end_session",
        session_id=session_id
    )

    item_responses = []
    for item in items:
        product_info = item.product
        item_responses.append(CartItemResponse(
            session_id=item.session_id,
            item_id=item.item_id,
            quantity=item.quantity,
            saved_weight=item.saved_weight,
            product={
                "item_no_": product_info.item_no_,
                "description": product_info.description,
                "description_ar": product_info.description_ar,
                "unit_price": product_info.unit_price,
                "product_size": product_info.product_size,
                "barcode": product_info.barcode,
                "image_url": product_info.image_url
            } if product_info else None
        ))
    print(item_responses)
    cart_data = CartItemListResponse(
        items=item_responses,
        total_price=total_price,
        item_count=len(items)
    )
    user = db.query(User).filter(User.id == session.user_id).first()
    # Send email
    if user.email:
        send_cart_receipt_email(
            recipient_email=user.email,
            cart_data=cart_data,
            user_name=user.full_name if user else "Valued Customer"
        )
    return True



def generate_qr(data: str) -> BytesIO:
    """Generates a QR code Token and returns it"""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.QR_EXPIRATION_MINUTES)
    payload = {
        "cartid": data,
        "exp": expires_at
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def validate_qr_token(token: str, db: Session):
    """Validate the QR token and extract cart ID."""
    logging_service = get_logging_service(db)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        logging_service.log_security_event(
            event_type=SecurityEventType.QR_SCAN_OK,
            user_id=None,
            additional_data={"token": token},
            success=True,
            failure_reason=None,
            ip_address="unknown"  # Replace with actual IP if available
        )
        return payload["cartid"]  # Returns cart ID if valid
    except jwt.ExpiredSignatureError:
        logging_service.log_security_event(
            event_type=SecurityEventType.TOKEN_REFRESH,
            user_id=None,
            additional_data={"token": token},
            success=False,
            failure_reason="QR Code expired",
            ip_address="unknown"
        )
        return None  # QR Code expired
    except jwt.InvalidTokenError:
        logging_service.log_security_event(
            event_type=SecurityEventType.TOKEN_REFRESH,
            user_id=None,
            additional_data={"token": token},
            success=False,
            failure_reason="Invalid QR Code",
            ip_address="unknown"
        )
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
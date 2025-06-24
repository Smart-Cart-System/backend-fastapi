from sqlalchemy.orm import Session
from models.user import User  # Import the class, not the module
from models.customer_session import CustomerSession
from schemas.user import UserCreate
from schemas.customer_session import SessionDetailsResponse
from core.security import get_password_hash
from crud.cart_item import get_cart_items_by_session, get_sessions_summary
from schemas.cart_item import CartItemResponse, CartItemListResponse
from services.logging_service import LoggingService, SecurityEventType, get_logging_service
from fastapi import HTTPException, status
from core.config import settings


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()  # Use the User class

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()  # Use the User class

def create_user(db: Session, user: UserCreate, admin_secret: str = None):
    logging_service = get_logging_service(db)
    
    # Check if attempting to create an admin user
    is_admin = user.is_admin
    
    # If trying to create admin user, verify admin_secret
    if is_admin:
        if admin_secret != settings.ADMIN_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin secret key"
            )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        mobile_number=user.mobile_number,  
        age=user.age,
        full_name=user.full_name,
        address=user.address,
        is_admin=is_admin 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Add logging for user creation
    logging_service.log_security_event(
        event_type=SecurityEventType.LOGIN_SUCCESS,  # You might want to add USER_CREATED event type
        user_id=db_user.id,
        username=user.username,
        ip_address="system",
        success=True,
        additional_data={"action": "user_created", "email": user.email, "full_name": user.full_name}
    )
    
    return db_user

def get_user_sessions_with_cart_details(db: Session, user_id: int):
    """Fetch all sessions for a user and include cart details"""
    sessions = db.query(CustomerSession).filter(
        CustomerSession.user_id == user_id,
        CustomerSession.is_active == False
    ).order_by(CustomerSession.created_at.desc()).all()
    
    if not sessions:
        return []

    session_responses = []
    for session in sessions:
        sessionId = session.session_id
        items, total_amount = get_sessions_summary(db, sessionId)
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

        cartItems = SessionDetailsResponse(
            items=item_responses,
            total_price=total_amount,
            item_count=len(items),
            session_id=sessionId,
            created_at=session.created_at,
        )
        session_responses.append(cartItems)

    return session_responses

def update_user(db: Session, user_id: int, user_data: UserCreate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    db_user.username = user_data.username
    db_user.email = user_data.email
    db_user.mobile_number = user_data.mobile_number
    db_user.age = user_data.age
    db_user.full_name = user_data.full_name
    db_user.address = user_data.address
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user_password(db: Session, user_id: int, new_password: str):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.hashed_password = get_password_hash(new_password)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user
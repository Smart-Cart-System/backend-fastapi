from sqlalchemy.orm import Session
from models.customer_session import CustomerSession
from models.cart import Cart
from schemas.customer_session import SessionCreate, SessionUpdate

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
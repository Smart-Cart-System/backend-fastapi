from sqlalchemy.orm import Session
from models.cart import Cart
from schemas.cart import CartCreate
from models.customer_session import CustomerSession

def get_carts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Cart).offset(skip).limit(limit).all()

def get_cart_by_id(db: Session, cart_id: int):
    return db.query(Cart).filter(Cart.cart_id == cart_id).first()

def get_cart_by_qrcode(db: Session, qrcode_token: str):
    return db.query(Cart).filter(Cart.qrcode_token == qrcode_token).first()

def get_cart_by_session(db: Session, session_id: int):
    db_session = (
        db.query(CustomerSession)
          .filter(CustomerSession.session_id == session_id)
          .first()
    )
    return db_session.cart_id if db_session else None

def create_cart(db: Session, cart: CartCreate):
    db_cart = Cart(**cart.dict())
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def update_cart_status(db: Session, cart_id: int, status: str):
    db_cart = get_cart_by_id(db, cart_id)
    if db_cart:
        db_cart.status = status
        db.commit()
        db.refresh(db_cart)
    return db_cart
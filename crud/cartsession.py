from sqlalchemy.orm import Session
from models.cartsession import CartSession
from schemas.cartsession import CartItemCreate

def create_cart_item(db: Session, cart_item: CartItemCreate):
    db_cart_item = CartSession(
        cart_id=cart_item.cart_id,
        user_id=cart_item.user_id,
        item_id=cart_item.item_id,
        quantity=cart_item.quantity
    )
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item

def get_cart_items(db: Session, cart_id: str):
    return db.query(CartSession).filter(CartSession.cart_id == cart_id).all()
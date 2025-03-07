from sqlalchemy.orm import Session
from models.item_read import ItemRead
from models.cart_item import CartItem
from models.customer_session import CustomerSession
from models.product import ProductionData

def validate_session(db: Session, session_id: int):
    """Check if session exists and is active"""
    return db.query(CustomerSession).filter(
        CustomerSession.session_id == session_id,
        CustomerSession.is_active == True
    ).first()

def read_item(db: Session, session_id: int, barcode: int):
    """Record an item read event"""
    # Validate session
    session = validate_session(db, session_id)
    if not session:
        return None, "Invalid or inactive session"
    
    # Find product
    product = db.query(ProductionData).filter(ProductionData.barcode == barcode).first()
    if not product:
        return None, "Product not found"
    
    # Record read event
    item_read = ItemRead(
        session_id=session_id,
        item_no_=product.item_no_
    )
    db.add(item_read)
    db.commit()
    db.refresh(item_read)
    
    return product, None  # Return product and no error

def add_cart_item(db: Session, session_id: int, barcode: int):
    """Add item to cart or increment quantity"""
    # Validate session
    session = validate_session(db, session_id)
    if not session:
        return None, "Invalid or inactive session"
    
    # Find product
    product = db.query(ProductionData).filter(ProductionData.barcode == barcode).first()
    if not product:
        return None, "Product not found"
    
    # Check if item already exists in cart
    cart_item = db.query(CartItem).filter(
        CartItem.session_id == session_id, 
        CartItem.item_id == product.item_no_
    ).first()
    
    if cart_item:
        # Increment quantity
        cart_item.quantity += 1
        db.commit()
        db.refresh(cart_item)
    else:
        # Add new item
        cart_item = CartItem(
            session_id=session_id,
            item_id=product.item_no_,
            quantity=1
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
    
    return cart_item, None

def remove_cart_item(db: Session, session_id: int, barcode: int):
    """Remove item from cart or decrement quantity"""
    # Validate session
    session = validate_session(db, session_id)
    if not session:
        return None, "Invalid or inactive session"
    
    # Find product
    product = db.query(ProductionData).filter(ProductionData.barcode == barcode).first()
    if not product:
        return None, "Product not found"
    
    # Find cart item
    cart_item = db.query(CartItem).filter(
        CartItem.session_id == session_id, 
        CartItem.item_id == product.item_no_
    ).first()
    
    if not cart_item:
        return None, "Item not in cart"
    
    if cart_item.quantity > 1:
        # Decrement quantity
        cart_item.quantity -= 1
        db.commit()
        db.refresh(cart_item)
        return cart_item, None
    else:
        # Remove item
        db.delete(cart_item)
        db.commit()
        return {"removed": True}, None